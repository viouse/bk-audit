# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云 - 审计中心 (BlueKing - Audit Center) available.
Copyright (C) 2023 THL A29 Limited,
a Tencent company. All rights reserved.
Licensed under the MIT License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the
specific language governing permissions and limitations under the License.
We undertake not to change the open source license (MIT license) applicable
to the current version of the project delivered to anyone in the future.
"""

import datetime
import time
import traceback

from bk_resource import resource
from bk_resource.exceptions import APIRequestError
from blueapps.utils.logger import logger
from celery.schedules import crontab
from celery.task import periodic_task, task
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext

from apps.meta.constants import ConfigLevelChoices
from apps.meta.models import GlobalMetaConfig, System
from apps.notice.handlers import ErrorMsgHandler
from core.utils.tools import single_task_decorator
from services.web.databus.collector.check.handlers import ReportCheckHandler
from services.web.databus.collector.etl.base import EtlStorage
from services.web.databus.collector.handlers import TailLogHandler
from services.web.databus.collector.join.base import AssetHandler, JoinDataHandler
from services.web.databus.collector_plugin.handlers import PluginEtlHandler
from services.web.databus.constants import (
    API_PUSH_ETL_RETRY_TIMES,
    API_PUSH_ETL_RETRY_WAIT_TIME,
    COLLECTOR_PLUGIN_ID,
    EtlConfigEnum,
    PluginSceneChoices,
    SnapshotRunningStatus,
    SnapShotStorageChoices,
)
from services.web.databus.models import CollectorConfig, CollectorPlugin, Snapshot


@periodic_task(run_every=crontab(minute="*/1"))
@single_task_decorator
def start_snapshot():
    # 获取所有的启动中快照并逐个运行 (Redis)
    snapshots = Snapshot.objects.filter(
        status__in=(SnapshotRunningStatus.PREPARING.value, SnapshotRunningStatus.FAILED.value),
        storage_type__in=(SnapShotStorageChoices.REDIS.value,),
    )
    for snapshot in snapshots:
        logger.info(
            "[start_snapshot] SystemID => %s; ResourceTypeID => %s", snapshot.system_id, snapshot.resource_type_id
        )
        JoinDataHandler(snapshot.system_id, snapshot.resource_type_id).start()
    # 创建HDFS快照
    snapshots = Snapshot.objects.filter(
        hdfs_status__in=(SnapshotRunningStatus.PREPARING.value, SnapshotRunningStatus.FAILED.value),
        storage_type__in=(SnapShotStorageChoices.HDFS.value,),
    )
    for snapshot in snapshots:
        logger.info("[start_asset] SystemID => %s; ResourceTypeID => %s", snapshot.system_id, snapshot.resource_type_id)
        AssetHandler(snapshot.system_id, snapshot.resource_type_id).start()


@periodic_task(run_every=crontab(minute="*/10"))
@single_task_decorator
def sync_tail_log_time():
    collectors = CollectorConfig.objects.all()
    for collector in collectors:
        TailLogHandler.get_instance(collector).sync()


@periodic_task(run_every=crontab(minute="*/1"))
@single_task_decorator
def change_storage_cluster():
    def change_plugin_storage():
        collector_plugins = CollectorPlugin.objects.filter(storage_changed=True)
        for collector_plugin in collector_plugins:
            try:
                default_plugin_id = GlobalMetaConfig.get(
                    COLLECTOR_PLUGIN_ID,
                    config_level=ConfigLevelChoices.NAMESPACE.value,
                    instance_key=collector_plugin.namespace,
                )
                resource.databus.collector_plugin.update_plugin(
                    namespace=collector_plugin.namespace,
                    etl_config=collector_plugin.etl_config,
                    etl_params=collector_plugin.etl_params,
                    is_default=str(default_plugin_id) == str(collector_plugin.collector_plugin_id),
                    collector_plugin_id=collector_plugin.collector_plugin_id,
                )
                collector_plugin.refresh_from_db()
                collector_plugin.storage_changed = False
                collector_plugin.save()
            except Exception as err:  # NOCC:broad-except(需要处理所有错误)
                title = gettext("ChangePluginStorageFailed")
                content = gettext("Error: %s") % str(err)
                ErrorMsgHandler(title, content).send()
                logger.exception(
                    "[Change Plugin Storage Failed] CollectorPluginID => %s; Err => %s",
                    collector_plugin.collector_plugin_id,
                    err,
                )

    def change_config_storage():
        collectors = CollectorConfig.objects.filter(storage_changed=True, is_deleted=False)
        for collector in collectors:
            try:
                system = System.objects.get(system_id=collector.system_id)
                etl_storage: EtlStorage = EtlStorage.get_instance(collector.etl_config)
                etl_storage.update_or_create(
                    collector.collector_config_id,
                    collector.etl_params,
                    collector.fields,
                    system.namespace,
                )
                collector.refresh_from_db()
                collector.storage_changed = False
                collector.save()
            except Exception as err:  # NOCC:broad-except(需要处理所有错误)
                title = gettext("ChangeCollectorStorageFailed")
                content = gettext("Error: %s") % str(err)
                ErrorMsgHandler(title, content).send()
                logger.exception("[Change Collector Storage Failed] CollectorID => %s; Err => %s", collector.id, err)

    change_plugin_storage()
    change_config_storage()


@periodic_task(run_every=crontab(minute="0", hour="0"))
@single_task_decorator
def refresh_snapshot():
    # 获取所有的运行中快照
    snapshots = Snapshot.objects.filter(status=SnapshotRunningStatus.RUNNING.value).order_by("updated_at")
    snapshots_count = snapshots.count()
    logger.info(f"[Refresh Snapshot] Snapshots Count => {snapshots_count}")
    if not snapshots_count:
        return
    # 计算需要更新的数量
    ex_days = int(settings.HTTP_PULL_REDIS_TIMEOUT.replace("d", ""))
    past_days = (timezone.now() - snapshots.first().updated_at).days
    updated_count = int(snapshots_count * (past_days / ex_days))
    logger.info(f"[Refresh Snapshot] ex_days => {ex_days}; past_days => {past_days}; updated_count => {updated_count}")
    if not updated_count:
        return
    # 更新状态
    snapshot_ids = [snapshot.id for snapshot in snapshots[:updated_count]]
    Snapshot.objects.filter(id__in=snapshot_ids).update(status=SnapshotRunningStatus.PREPARING.value)


@task()
def create_api_push_etl(collector_config_id: int):
    """
    创建 API PUSH 对应的数据清洗入库链路
    """

    logger.info("[create_api_push_etl] Start %s", datetime.datetime.now())

    collector = CollectorConfig.objects.get(collector_config_id=collector_config_id)
    namespace = CollectorPlugin.objects.get(collector_plugin_id=collector.collector_plugin_id).namespace

    # 创建清洗策略
    fields = [
        {
            **_field,
            "option": {
                "key": f"attributes/{_field['field_name']}",
                "path": f"attributes/{_field['field_name']}",
                "val": None,
            },
        }
        for _field in resource.meta.get_standard_fields()
    ]
    etl_params = {
        "namespace": namespace,
        "collector_config_id": collector.collector_config_id,
        "etl_config": EtlConfigEnum.BK_LOG_JSON.value,
        "etl_params": {"retain_original_text": True},
        "fields": fields,
        "ignore_check": True,
    }

    # Delay 任务不会及时到 BkBase，需要增加 Retry
    retry = 1
    time.sleep(API_PUSH_ETL_RETRY_WAIT_TIME)
    while retry <= API_PUSH_ETL_RETRY_TIMES:
        retry += 1
        try:
            resource.databus.collector.collector_etl(**etl_params)
            retry = API_PUSH_ETL_RETRY_TIMES + 1
            logger.info("[CreateApiPushEtlSuccess] Retry => %s; Collector => %s", retry, collector.collector_config_id)
        except Exception as err:  # NOCC:broad-except(需要处理所有错误)
            logger.exception(
                "[CreateApiPushEtlError] Retry => %s; Error => %s; Detail %s;", retry, str(err), traceback.format_exc()
            )
            if isinstance(err, APIRequestError):
                time.sleep(API_PUSH_ETL_RETRY_WAIT_TIME)
            else:
                break

    logger.info("[create_api_push_etl] End %s", datetime.datetime.now())


@periodic_task(run_every=crontab(minute="*/1"))
@single_task_decorator
def check_report_continues(end_time: datetime.datetime = None, time_period: int = None, time_range: int = None):
    """检查上报数据是否连续"""

    namespaces = CollectorPlugin.objects.all().order_by().values_list("namespace", flat=True).distinct()

    for namespace in namespaces:
        try:
            ReportCheckHandler(
                namespace=namespace, end_time=end_time, time_period=time_period, time_range=time_range
            ).check()
        except Exception as err:  # NOCC:broad-except(需要处理所有错误)
            logger.error(
                "[ReportCheckRunFailed] "
                "Namespace => %s; "
                "end_time => %s; "
                "time_period => %s; "
                "time_range => %s; "
                "Err => %s",
                namespace,
                end_time,
                time_period,
                time_range,
                err,
            )


@periodic_task(run_every=crontab(minute="*/1"))
@single_task_decorator
def create_or_update_plugin_etl(collector_plugin_id: int = None):
    """创建或更新采集插件清洗入库"""

    if collector_plugin_id:
        plugins = CollectorPlugin.objects.filter(collector_plugin_id=collector_plugin_id)
    else:
        # 仅为采集项类型的采集插件创建入库
        plugins = CollectorPlugin.objects.filter(
            plugin_scene=PluginSceneChoices.COLLECTOR.value, bkbase_table_id__isnull=True
        )
    # 创建或更新
    for plugin in plugins:
        PluginEtlHandler(collector_plugin_id=plugin.collector_plugin_id).create_or_update()
