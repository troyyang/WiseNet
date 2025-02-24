<template>
  <div class="container">
    <Breadcrumb :items="['menu.api', 'menu.api.swagger']" />
    <iframe :src="getSwaggerUrl()" frameborder="0"></iframe>
  </div>
</template>

<script lang="ts" setup>
  import { getSwaggerUrl } from '@/api/api-doc';
</script>

<script lang="ts">
  export default {
    name: 'Swagger',
  };
</script>

<style scoped lang="less">
  .container {
    padding: 0 20px 20px 20px;
    height: calc(100% - 40px);
    :deep(.content) {
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      text-align: center;
      background-color: var(--color-bg-1);
      border-radius: 4px;
    }
  }
  iframe {
    width: 100%;
    height: 100%;
    border: none;
  }
</style>
