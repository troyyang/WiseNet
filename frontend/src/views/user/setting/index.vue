<template>
  <div class="container">
    <Breadcrumb :items="['menu.user', 'menu.user.setting']" />

    <div class="wrapper">
      <a-col :span="24">
        <a-tabs default-active-key="1" type="rounded">
          <a-tab-pane key="1" :title="$t('userSetting.tab.basicInformation')">
            <UserBaseInfo
              v-if="userStore.currentUser"
              :selected-user="userStore.currentUser"
            />
          </a-tab-pane>
          <a-tab-pane key="2" :title="$t('userSetting.tab.securitySettings')">
            <SecuritySettings />
          </a-tab-pane>
        </a-tabs>
      </a-col>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { useUserStore } from '@/store';
  import UserBaseInfo from './components/user-base-info.vue';
  import SecuritySettings from './components/security-settings.vue';

  const userStore = useUserStore();
</script>

<script lang="ts">
  export default {
    name: 'Setting',
  };
</script>

<style scoped lang="less">
  .container {
    padding: 0 20px 20px 20px;
  }

  .wrapper {
    padding: 20px 0 0 20px;
    background-color: var(--color-bg-2);
    border-radius: 4px;
    max-width: 800px;
    margin: 0 auto;
    height: 100%;
  }

  :deep(.section-title) {
    margin-top: 0;
    margin-bottom: 16px;
    font-size: 14px;
  }
</style>
