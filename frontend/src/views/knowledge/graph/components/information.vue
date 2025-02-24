<template>
  <a-card class="general-card" :title="dynamicTitle">
    <InformationOverview />
    <InformationLink />
    <InformationNode />
  </a-card>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { useKnowledgeStore } from '@/store';
  import InformationOverview from './information-overview.vue';
  import InformationNode from './information-node.vue';
  import InformationLink from './information-link.vue';

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();
  const dynamicTitle = computed(() => {
    let title = t('knowledge.title.node.overview');
    if (knowledgeStore.selectedNode) {
      title = t('knowledge.title.node.localNode'); // Title for localNode
    } else if (knowledgeStore.selectedRelationship) {
      title = t('knowledge.title.node.localLink'); // Title for localLink
    }
    return title;
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

  .doc-content {
    height: 300px;
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
