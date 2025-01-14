/*
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
*/
import Aegis from 'aegis-web-sdk';
import BkuiVue from 'bkui-vue';
import { bkTooltips } from 'bkui-vue/lib/directives';
import { createApp } from 'vue';

import RootManageService from '@service/root-manage';

import ApplyPermissionCatch from '@components/apply-permission/catch.vue';
import AuditForm from '@components/audit-form/index.vue';
import AuditIcon from '@components/audit-icon';
import AuditPopconfirm from '@components/audit-popconfirm/index.vue';
import AuditRouterView from '@components/audit-router-view/index.vue';
import AuditSideslider from '@components/audit-sideslider/index.vue';
import AuditUserSelector from '@components/audit-user-selector/index.vue';
import AuthButton from '@components/auth/button.vue';
import AuthComponent from '@components/auth/component';
import AuthOption from '@components/auth/option.vue';
import AuthRouterLink from '@components/auth/router-link.vue';
import AuthSwitch from '@components/auth/switch.vue';
import RenderList from '@components/render-list/index.vue';
import RenderSensitivityLevel from '@components/render-sensitivity-level/index.vue';
import ScrollFaker from '@components/scroll-faker/index.vue';
import SkeletonLoading from '@components/skeleton-loading/index.vue';
import SmartAction from '@components/smart-action/index.vue';

import cursor from '@directives/cursor';

import createRouter from '@router/index';

import i18n from '@language/index.js';

import App from './app.vue';

import('tippy.js/dist/tippy.css');
import('tippy.js/themes/light.css');
import('bkui-vue/dist/style.css');
import('@lib/bk-icon/style.css');
import('@lib/bk-icon/iconcool.js');
import('@/css/reset.css');
import('@/css/common.css');

window.changeConfirm = false;

RootManageService.config()
  .then((config) => {
    document.title = config.title;
    const BKApp = createApp(App);

    BKApp.use(BkuiVue);
    BKApp.use(i18n);
    BKApp.use(createRouter(config));

    BKApp.component('ApplyPermissionCatch', ApplyPermissionCatch);
    BKApp.component('AuditForm', AuditForm);
    BKApp.component('AuditIcon', AuditIcon);
    BKApp.component('AuditPopconfirm', AuditPopconfirm);
    BKApp.component('AuditRouterView', AuditRouterView);
    BKApp.component('AuditSideslider', AuditSideslider);
    BKApp.component('AuditUserSelector', AuditUserSelector);
    BKApp.component('AuthButton', AuthButton);
    BKApp.component('AuthComponent', AuthComponent);
    BKApp.component('AuthOption', AuthOption);
    BKApp.component('AuthSwitch', AuthSwitch);
    BKApp.component('AuthRouterLink', AuthRouterLink);
    BKApp.component('RenderList', RenderList);
    BKApp.component('RenderSensitivityLevel', RenderSensitivityLevel);
    BKApp.component('ScrollFaker', ScrollFaker);
    BKApp.component('SkeletonLoading', SkeletonLoading);
    BKApp.component('SmartAction', SmartAction);

    BKApp.directive('bk-tooltips', bkTooltips);
    BKApp.directive('cursor', cursor);

    BKApp.mount('#app');

    // TAM前端监控
    setTimeout(() => {
      if (config.aegis_id) {
        new Aegis({
          id: config.aegis_id, // 项目ID，即上报id
          uin: '', // 用户唯一 ID（可选）
          reportApiSpeed: true, // 接口测速
          reportAssetSpeed: true, // 静态资源测速
        });
      }
    });
  });

