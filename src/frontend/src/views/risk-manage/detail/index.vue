<!--
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
-->
<template>
  <bk-loading :loading="loading || strategyLoading || statusLoading">
    <div class="risk-manage-detail-wrap mb12">
      <base-info
        :data="riskData"
        :risk-status-common="riskStatusCommon"
        :strategy-list="strategyList" />
    </div>
    <bk-tab
      v-model:active="active"
      type="card-grid"
      @change="onTabChange">
      <bk-tab-panel
        v-for="(item) in panels"
        :key="item.name"
        :label="item.label"
        :name="item.name" />
      <component
        :is="comMap[active as keyof typeof comMap]"
        v-if="!loading && riskData"
        :data="riskData"
        :risk-id="riskData.risk_id"
        :strategy-list="strategyList"
        @update="handleUpdate" />

      <!-- 跳转到页面最后的锚点 -->
      <span id="risk-manage-detail-end-anchor" />
    </bk-tab>
  </bk-loading>
</template>

<script setup lang='ts'>
  import {
    onUnmounted,
    ref,
  } from 'vue';
  import { useI18n } from 'vue-i18n';
  import {
    useRoute,
    useRouter,
  } from 'vue-router';

  import RiskManageService from '@service/risk-manage';
  import StrategyManageService from '@service/strategy-manage';

  import RiskManageModel from '@model/risk/risk';

  import useRequest from '@hooks/use-request';
  import useRouterBack from '@hooks/use-router-back';
  import useRouterLink from '@hooks/use-router-link';
  import useUrlSearch from '@hooks/use-url-search';

  import {
    execCopy,
  } from '@utils/assist';

  import BaseInfo from './components/base-info.vue';
  import LinkEvent from './components/link-event.vue';
  import RiskHandle from './components/risk-handle/index.vue';

  const router = useRouter();
  const route = useRoute();
  const { t } = useI18n();
  let timeout: undefined | number = undefined;
  const panels = [
    { name: 'linkEvent', label: '关联事件' },
    { name: 'handleRisk', label: '风险处理' },
  ];
  const comMap = {
    linkEvent: LinkEvent,
    handleRisk: RiskHandle,
  };
  const active = ref('linkEvent');
  const { getSearchParams, replaceSearchParams } = useUrlSearch();
  const { tab } = getSearchParams();
  if (tab) {
    active.value = tab;
  }

  const {
    loading: strategyLoading,
    data: strategyList,
  } = useRequest(StrategyManageService.fetchAllStrategyList, {
    manual: true,
    defaultValue: [],
  });

  const {
    data: riskStatusCommon,
    loading: statusLoading,
  } = useRequest(RiskManageService.fetchRiskStatusCommon, {
    manual: true,
    defaultValue: [],
  });
  // 查询详情
  const {
    loading,
    data: riskData,
    run: fetchRiskList,
  } = useRequest(RiskManageService.fetchRiskById, {
    defaultValue: new RiskManageModel(),
    defaultParams: {
      id: route.params.riskId,
    },
    manual: true,
    onSuccess(data) {
      if (['for_approve', 'auto_process'].includes(data.status)) {
        startPolling();
      } else {
        clearTimeout(timeout);
      }
    },
  });


  const handleUpdate = () => {
    fetchRiskList({
      id: route.params.riskId,
    });
  };
  const onTabChange = (tab: string) => {
    replaceSearchParams({
      tab,
    });
  };
  // 轮训查询详情
  const startPolling = () => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      handleUpdate();
    }, 60 * 1000);
  };
  onUnmounted(() => {
    clearTimeout(timeout);
  });


  useRouterLink(() => {
    const route = window.location.href;
    execCopy(route, t('复制成功'));
  });
  useRouterBack(() => {
    router.push({
      name: route.name === 'riskManageDetail'
        ? 'riskManageList'
        : 'handleManageList',
    });
  });
</script>
<style scoped lang="postcss">
.risk-manage-detail-wrap{
  .flex{
    display: flex;
    align-items: center;


  }
}
</style>
