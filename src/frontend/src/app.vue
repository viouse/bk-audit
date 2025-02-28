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
  <bk-loading
    :loading="watermarkLoading"
    mode="spin"
    style="height: 100vh;"
    theme="primary">
    <bk-config-provider
      :locale="bkuiLocal">
      <layout
        v-if="isWatermarkSuccess"
        class="layout-box">
        <template #header>
          <router-back />
          <span>{{ t(pageTitle) }}</span>
          <use-router-link />
          <div
            id="teleport-nav-step"
            style="flex: 1;" />
        </template>
        <template #headerRight>
          <bk-dropdown class="site-top-dropdown-menu">
            <div class="site-help-btn">
              <audit-icon
                style="font-size: 19px;"
                :type="locale === 'zh-CN' ? 'lang-zh' : 'lang-en'" />
            </div>
            <template #content>
              <bk-dropdown-menu>
                <bk-dropdown-item
                  class="language-option-item"
                  :class="{
                    'active': locale === 'zh-CN'
                  }"
                  @click="handleSwitchLang('zh-CN')">
                  <audit-icon type="lang-zh" />
                  <span>简体中文</span>
                </bk-dropdown-item>
                <bk-dropdown-item
                  class="language-option-item"
                  :class="{
                    'active': locale === 'en-US'
                  }"
                  @click="handleSwitchLang('en')">
                  <audit-icon type="lang-en" />
                  <span>English</span>
                </bk-dropdown-item>
              </bk-dropdown-menu>
            </template>
          </bk-dropdown>
          <bk-dropdown class="site-top-dropdown-menu">
            <div class="site-help-btn">
              <audit-icon
                class="version-log-icon"
                type="help-document-fill" />
            </div>
            <template #content>
              <bk-dropdown-menu>
                <bk-dropdown-item @click="handleVersionLog">
                  {{ t('版本日志') }}
                </bk-dropdown-item>
              </bk-dropdown-menu>
            </template>
          </bk-dropdown>
          <bk-dropdown class="site-top-dropdown-menu">
            <div class="account-info-btn">
              <span>{{ userInfo.username }}</span>
              <audit-icon
                class="logout-btn"
                type="angle-fill-down" />
            </div>
            <template #content>
              <bk-dropdown-menu>
                <bk-dropdown-item @click="handleLogout">
                  {{ t('退出登录') }}
                </bk-dropdown-item>
              </bk-dropdown-menu>
            </template>
          </bk-dropdown>
        </template>
        <router-view />
        <version-log v-model:is-show="isShowVersionLog" />
      </layout>
      <bk-exception
        v-else-if="!watermarkLoading"
        class="exception-wrap-item exception-part exception-gray"
        :description="t('基础数据加载失败，请刷新重试')"
        scene="part"
        style="padding-top: 17%;"
        type="500" />
    </bk-config-provider>
  </bk-loading>
</template>
<script setup lang="ts">
  import bkuiLocalEN from 'bkui-vue/dist/locale/en.esm.js';
  import bkuiLocalZHCN from 'bkui-vue/dist/locale/zh-cn.esm.js';
  import Cookie from 'js-cookie';
  import {
    computed,
    ref,
    watch,
  } from 'vue';
  import { useI18n } from 'vue-i18n';
  import {
    useRoute,
  } from 'vue-router';

  import AccountManageService from '@service/account-manage';
  import EntryManageService from '@service/entry-manage';

  import AccountModel from '@model/account/account';

  import useRequest from '@hooks/use-request';

  import RouterBack from '@components/router-back/index.vue';
  import UseRouterLink from '@components/router-link/index.vue';
  import VersionLog from '@components/version-log/index.vue';

  import WaterMark from '@utils/assist/water-mark';

  import Layout from './layout.vue';

  const { locale, t } = useI18n();
  const route = useRoute();
  const isShowVersionLog = ref(false);
  const isWatermarkSuccess = ref(false);

  const bkuiLocal = locale.value === 'en-US' ? bkuiLocalEN : bkuiLocalZHCN;
  const steps = ref<Array<{ title: string }>>([]);
  const {
    data: userInfo,
  } = useRequest(AccountManageService.fetchUserInfo, {
    defaultValue: new AccountModel(),
    manual: true,
  });

  const pageTitle = computed(() => (route.meta.title || '') as string);

  const handleVersionLog = () => {
    isShowVersionLog.value = true;
  };

  const {
    run: fetchLogout,
  } = useRequest(EntryManageService.fetchLogout);

  const  {
    loading: watermarkLoading,
  } = useRequest(EntryManageService.watermark, {
    defaultValue: null,
    manual: true,
    onSuccess(data) {
      if (data) {
        const src = data.watermark.items[0].data;
        WaterMark(src);
        isWatermarkSuccess.value = true;
      }
    },
  });

  const handleLogout = async () => {
    await fetchLogout();
    window.location.reload();
  };

  const handleSwitchLang = (lang: string) => {
    Cookie.remove('blueking_language', { path: '' });
    Cookie.set('blueking_language', lang, {
      expires: 3600,
      domain: window.location.hostname.replace(/^.*(\.[^.]+\.[^.]+)$/, '$1'),
    });
    window.location.reload();
  };

  watch(() => route, () => {
    if (route.meta.hasStep) {
      const titles = route.meta.stepTitles as string[];
      steps.value = titles.map(item => ({
        title: t(item),
      }));
    }
  }, {
    immediate: true,
    deep: true,
  });
</script>
<style lang="postcss">
.account-info-btn {
  height: 32px;
  font-size: 14px;
  line-height: 32px;
  color: #979ba5;
  cursor: pointer;

  &:hover {
    color: #3a84ff;
  }
}

.logout-btn {
  margin-left: 3px;
  font-size: 12px;
}

.site-help-btn {
  display: flex;
  width: 32px;
  height: 32px;
  margin-right: 15px;
  color: #979ba5;
  align-items: center;
  justify-content: center;

  &:hover {
    color: #3a84ff;
    cursor: pointer;
    background: #f0f1f5;
    border-radius: 100%;
  }
}

.site-top-dropdown-menu {
  .bk-dropdown-menu {
    margin-top: 5px;
  }
}

.language-option-item {
  &:hover {
    background: #e1ecff !important;
  }

  &.active {
    color: #3a84ff !important;
    background: #e1ecff;
  }

  i {
    margin-right: 4px;
    font-size: 14px;
  }
}
</style>
