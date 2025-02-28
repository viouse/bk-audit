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
  <div class="reopen-mis-report-wrap">
    <div class="mis-title">
      <span style="color:#313238">{{ data.operator }}</span>
      <span
        class="ml8"
        style="color: #979BA5">{{ data.time }}</span>
    </div>
    <div class="mis-content">
      <render-info-item :label="t('处理方法')">
        <span v-if="data.custom_action === 'CloseRisk'">{{ t('人工关单') }}</span>
        <span v-else-if="data.custom_action === 'TransOperator'">
          {{ t('转单给') }}{{ data.new_operators?.join(',') }}
        </span>
        <span v-else>{{ t('处理套餐') }} </span>
      </render-info-item>
      <template v-if="data.custom_action === 'AutoProcess'">
        <render-info-item
          class="mt8"
          :label="t('选择套餐')">
          {{ processApplicationList
            .find(item=>item.id === data.pa_id)?.name || data.pa_id || '--' }}
        </render-info-item>
        <template v-if="data.pa_params">
          <render-info-item
            v-for="(key,index) in Object.keys(data.pa_params)"
            :key="index"
            class="mt8"
            :label="processPackageDetail[key]?.name || key">
            {{ riskFieldMap[data.pa_params[key].field] || data.pa_params[key].field ||'--' }}
          </render-info-item>
        </template>
        <render-info-item
          class="mt8"
          :label="t('套餐执行成功后自动关单')">
          {{ data.auto_close_risk ? t('是') : t('否') }}
        </render-info-item>
      </template>
      <render-info-item
        v-else
        class="mt8"
        :label="t('处理说明')">
        {{ data.description || '--' }}
      </render-info-item>
    </div>
  </div>
</template>

<script setup lang='ts'>
  import {
    computed,
  } from 'vue';
  import {
    useI18n,
  } from 'vue-i18n';

  import type RiskManageModel from '@model/risk/risk';

  import RenderInfoItem from '@views/risk-manage/detail/components/render-info-item.vue';


  interface Props{
    data: RiskManageModel['ticket_history'][0],
    processApplicationList: Array<{
      id: string,
      name: string,
      sops_template_id: number,
    }>,
    riskFieldMap: Record<string, string>,
    // 处理套餐详情
    processDetail: Record<string, any>
  }
  const props = defineProps<Props>();
  const { t } = useI18n();
  const processPackageDetail = computed(() => {
    if (props.data && props.processDetail) {
      const ret = props.processDetail[props.data.pa_id] || {};
      return ret;
    }
    return {};
  });
</script>
<style scoped lang="postcss">
.reopen-mis-report-wrap{
  padding: 10px 16px;
  background: #FFF;
  border: 1px solid #EAEBF0;
  border-radius: 6px;
  box-shadow: 0 2px 6px 0 #0000000a;

  .mis-title{
    font-size: 12px;
  }

  >.mis-content{
    padding: 12px 16px;
    margin-top: 8px;
    background: #F5F7FA;
    border-radius: 4px;
  }
}
</style>
