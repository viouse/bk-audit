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

import abc

from bk_resource import BkApiResource
from django.utils.translation import gettext_lazy

from api.domains import BK_ITSM_API_URL


class BKITSM(BkApiResource, abc.ABC):
    module_name = "bk_itsm"
    base_url = BK_ITSM_API_URL
    platform_authorization = True


class GetServices(BKITSM):
    name = gettext_lazy("服务列表查询")
    method = "GET"
    action = "/v2/itsm/get_services/"


class GetServiceDetail(BKITSM):
    name = gettext_lazy("获取服务详情")
    method = "GET"
    action = "/v2/itsm/get_service_detail/"


class CreateTicket(BKITSM):
    name = gettext_lazy("创建单据")
    method = "POST"
    action = "/v2/itsm/create_ticket/"


class GetTicketStatus(BKITSM):
    name = gettext_lazy("单据状态查询")
    method = "GET"
    action = "/v2/itsm/get_ticket_status/"


class TicketApproveResult(BKITSM):
    name = gettext_lazy("查询审批结果")
    method = "POST"
    action = "/v2/itsm/ticket_approval_result/"


class OperateTicket(BKITSM):
    name = gettext_lazy("操作单据")
    method = "POST"
    action = "/v2/itsm/operate_ticket/"
