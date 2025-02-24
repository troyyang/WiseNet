<template>
  <a-typography-text v-if="knowledgeStore.selectedNode?.title">
    <a-typography-title :heading="6">
      {{ t('knowledge.information.title') }}
    </a-typography-title>
    <a-typography-text :copyable="true">{{
      knowledgeStore.selectedNode?.title
    }}</a-typography-text>
    <InformationVectorPiece
      :vector="knowledgeStore.selectedNode?.titleVector"
    />
  </a-typography-text>
  <a-typography-text>
    <a-typography-title :heading="6">
      {{ t('knowledge.information.content') }}:
    </a-typography-title>
    <a-typography-text
      :ellipsis="{
        rows: 5,
        expandable: true,
      }"
      :copyable="true"
    >
      {{ knowledgeStore.selectedNode?.content }}
    </a-typography-text>
    <InformationVectorPiece
      :vector="knowledgeStore.selectedNode?.contentVector"
    />
  </a-typography-text>
  <a-typography-text :copyable="true">
    <a-typography-title :heading="6">
      {{ t('knowledge.information.createtime') }}
    </a-typography-title>
    <a-typography-text>{{
      knowledgeStore.selectedNode?.createdAt
    }}</a-typography-text>
  </a-typography-text>
  <a-typography-text :copyable="true">
    <a-typography-title :heading="6">
      {{ t('knowledge.information.updatetime') }}
    </a-typography-title>
    <a-typography-text>{{
      knowledgeStore.selectedNode?.updatedAt
    }}</a-typography-text>
  </a-typography-text>
</template>

<script lang="ts" setup>
  import { defineAsyncComponent } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { useKnowledgeStore } from '@/store';

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();

  const InformationVectorPiece = defineAsyncComponent(
    () => import('./information-vector-piece.vue')
  );
</script>
