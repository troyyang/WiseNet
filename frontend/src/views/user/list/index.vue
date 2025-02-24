<template>
  <div class="container">
    <Breadcrumb :items="['menu.user', 'menu.user.list']" />
    <div class="layout">
      <div class="layout-content">
        <UserList />
      </div>
      <div v-if="userStore.selectedUser" class="layout-right-side">
        <a-space :size="16" direction="vertical" fill>
          <UserForm :selected-user="userStore.selectedUser" />
        </a-space>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { useUserStore } from '@/store';
  import UserList from './components/user-list.vue';
  import UserForm from './components/user-form.vue';

  const userStore = useUserStore();
</script>

<style scoped lang="less">
  .container {
    padding: 0 20px 20px 20px;
  }

  .layout {
    display: flex;

    &-content {
      flex: 4 0 0;
      padding: 0 16px;
    }

    &-right-side {
      flex: 1;
      min-width: 280px;
    }
  }
</style>

<style lang="less" scoped>
  // responsive
  @media (max-width: @screen-lg) {
    .layout {
      flex-wrap: wrap;
      &-left-side {
        flex: 1;
        flex-basis: 100%;
        margin-bottom: 16px;
      }

      &-content {
        flex: none;
        flex-basis: 100%;
        padding: 0;
        order: -1;
        margin-bottom: 16px;
      }

      &-right-side {
        flex-basis: 100%;
      }
    }
  }
</style>
