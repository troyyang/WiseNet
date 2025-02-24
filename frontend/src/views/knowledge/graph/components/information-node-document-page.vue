<template>
  <a-list
    class="list-doc-page-action-layout"
    :bordered="false"
    :data="pages"
    :pagination-props="
      reactive({
        defaultPageSize: 1,
        total: pages.length,
        size: 'mini' as 'mini',
        simple: true,
      })
    "
  >
    <template #item="{ item }">
      <a-list-item class="list-doc-page-item" action-layout="vertical">
        <a-typography-paragraph
          :copyable="true"
          :ellipsis="{
            rows: 10,
          }"
        >
          {{ item.content }}
        </a-typography-paragraph>
        <InformationVectorPiece :vector="item.contentVector" />
      </a-list-item>
    </template>
  </a-list>
</template>

<script lang="ts" setup>
  import { reactive, PropType, defineAsyncComponent } from 'vue';
  import { DocumentPageRecord } from '@/api/graph';

  const InformationVectorPiece = defineAsyncComponent(
    () => import('./information-vector-piece.vue')
  );

  defineProps({
    pages: {
      type: Array as PropType<DocumentPageRecord[]>,
      default() {
        return [];
      },
    },
  });
</script>

<style scoped lang="less">
  :deep(.arco-descriptions-item-label) {
    padding-right: 6px;
  }

  .vector-basic {
    padding: 10px;
    width: 200px;
    background-color: var(--color-bg-popup);
    border-radius: 4px;
    box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.15);
  }

  .list-doc-page-action-layout {
    height: 100%;
    padding: 0 0;
  }
  .list-doc-page-action-layout .list-doc-page-item {
    padding: 0 0;
    border-bottom: 1px solid var(--color-fill-3);
  }

  .list-doc-page-action-layout .arco-list-item-action .arco-icon {
    margin: 0 0;
  }
</style>
