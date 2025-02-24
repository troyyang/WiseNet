<template>
  <a-typography-text :copyable="true">
    <a-typography-title :heading="6">
      {{ t('knowledge.information.element.id') }}
    </a-typography-title>
    <a-typography-text>{{
      knowledgeStore.selectedNode?.elementId
    }}</a-typography-text>
  </a-typography-text>
  <a-typography-text :copyable="true">
    <a-typography-title :heading="6"> ID </a-typography-title>
    <a-typography-text>{{ knowledgeStore.selectedNode?.id }}</a-typography-text>
  </a-typography-text>
  <a-typography-text :copyable="true">
    <a-typography-title :heading="6">
      {{ t('knowledge.information.lib.id') }}
    </a-typography-title>
    <a-typography-text>{{
      knowledgeStore.selectedNode?.libId
    }}</a-typography-text>
  </a-typography-text>
  <a-typography-text :copyable="true">
    <a-typography-title :heading="6">
      {{ t('knowledge.information.subject.id') }}
    </a-typography-title>
    <a-typography-text>{{
      knowledgeStore.selectedNode?.subjectId
    }}</a-typography-text>
  </a-typography-text>
  <a-typography-text :copyable="true">
    <a-typography-title :heading="6">
      {{ t('knowledge.information.index') }}
    </a-typography-title>
    <a-typography-text>{{
      knowledgeStore.selectedNode?.index
    }}</a-typography-text>
  </a-typography-text>
  <a-typography-text :copyable="true">
    <a-typography-title :heading="6">
      {{ t('knowledge.information.position') }}
    </a-typography-title>
    <a-typography-text
      >({{ knowledgeStore.selectedNode?.x }},
      {{ knowledgeStore.selectedNode?.y }})</a-typography-text
    >
  </a-typography-text>
</template>

<script lang="ts" setup>
  import { useI18n } from 'vue-i18n';
  import { useKnowledgeStore } from '@/store';

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();
</script>
