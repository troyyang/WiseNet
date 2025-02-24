<template>
  <a-card class="general-card" :title="t('query.result.title')">
    <a-collapse
      expand-icon-position="right"
      :default-active-key="['1', '2', '3', '4', '5']"
      :bordered="false"
    >
      <template #expand-icon="{ active }">
        <icon-double-down v-if="active" />
        <icon-double-right v-else />
      </template>
      <a-collapse-item
        v-if="knowledgeStore.queryResultRecord?.mainNode"
        key="1"
        style="width: 320px"
        :header="t('knowledge.information.node')"
      >
        <MainNode />
      </a-collapse-item>
      <a-collapse-item
        v-if="
          (knowledgeStore.queryResultRecord?.entities &&
            knowledgeStore.queryResultRecord?.entities.length > 0) ||
          (knowledgeStore.queryResultRecord?.keywords &&
            knowledgeStore.queryResultRecord?.keywords.length > 0) ||
          (knowledgeStore.queryResultRecord?.tags &&
            knowledgeStore.queryResultRecord?.tags.length > 0)
        "
        key="2"
        style="width: 320px"
        :header="t('knowledge.graph.extendedInfo')"
      >
        <Entities />
        <Keywords />
        <Tags />
      </a-collapse-item>
      <a-collapse-item
        v-if="knowledgeStore.queryResultRecord?.document"
        key="3"
        style="width: 320px"
        :header="t('knowledge.information.documents')"
      >
        <Document />
      </a-collapse-item>
      <a-collapse-item
        v-if="knowledgeStore.queryResultRecord?.webpage"
        key="4"
        style="width: 320px"
        :header="t('knowledge.information.webpages')"
      >
        <Webpage />
      </a-collapse-item>
    </a-collapse>
  </a-card>
</template>

<script lang="ts" setup>
  import { defineAsyncComponent } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { useKnowledgeStore } from '@/store';

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();

  const MainNode = defineAsyncComponent(
    () => import('./query-result-main-node.vue')
  );
  const Entities = defineAsyncComponent(
    () => import('./query-result-entities.vue')
  );
  const Keywords = defineAsyncComponent(
    () => import('./query-result-keywords.vue')
  );
  const Tags = defineAsyncComponent(() => import('./query-result-tags.vue'));
  const Document = defineAsyncComponent(
    () => import('./query-result-document.vue')
  );
  const Webpage = defineAsyncComponent(
    () => import('./query-result-webpage.vue')
  );
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
</style>
