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
  <skeleton-loading
    fullscreen
    :loading="isLoading"
    name="analysisList">
    <div class="analysis-manage-page">
      <search-box
        ref="searchBoxRef"
        @change="handleSearchChange" />
      <div class="search-result-action">
        <!-- <BkButton>导出</BkButton> -->
        <render-type-tab
          v-if="false"
          v-model="renderType" />
      </div>
      <component
        :is="searchResultCom"
        ref="resultRef"
        :filter="searchModel"
        @clear-search="handleClearSearch" />
      <search-page-footer />
    </div>
  </skeleton-loading>
</template>
<script setup lang="ts">
  import {
    computed,
    ref,
  } from 'vue';

  import RenderTypeTab from './components/render-type-tab.vue';
  import SearchBox from './components/search-box/index.vue';
  import SearchPageFooter from './components/search-page-footer.vue';
  import SearchResultChart from './components/search-result-chart/index.vue';
  import SearchResultTable from './components/search-result-table/index.vue';

  const comMap = {
    table: SearchResultTable,
    chart: SearchResultChart,
  };
  const renderType = ref<'chart'|'table'>('table');
  const searchBoxRef = ref();
  const resultRef = ref();

  const searchModel = ref<Record<string, any>>({});

  const searchResultCom = computed(() => comMap[renderType.value]);
  const isLoading = computed(() => (resultRef.value ? resultRef.value.loading : true));

  // 搜索
  const handleSearchChange = (value: Record<string, any>) => {
    searchModel.value = value;
  };
  // 清空搜索
  const handleClearSearch = () => {
    searchBoxRef.value.clearValue();
  };
</script>
<style lang="postcss">
  .analysis-manage-page {
    padding-bottom: 44px;

    /* 解决表格悬停超出 */
    .bk-table-fixed .column_fixed{
      bottom:80px !important;
    }

    .search-result-action {
      display: flex;
      margin-top: 16px;
    }
  }
</style>
