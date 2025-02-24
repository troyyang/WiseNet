<template>
  <a-typography-text v-if="knowledgeStore.queryResultRecord?.mainNode?.title">
    <a-typography-title :heading="6">
      {{ $t('knowledge.information.title') }}
    </a-typography-title>
    <a-typography-text :copyable="true">{{
      knowledgeStore.queryResultRecord?.mainNode?.title
    }}</a-typography-text>
  </a-typography-text>
  <a-typography-text>
    <a-typography-title :heading="6">
      {{ $t('knowledge.information.content') }}:
    </a-typography-title>
    <a-typography-text
      :ellipsis="{
        rows: 5,
        expandable: true,
      }"
      :copyable="true"
    >
      {{ knowledgeStore.queryResultRecord?.mainNode?.content }}
    </a-typography-text>
  </a-typography-text>
</template>

<script lang="ts" setup>
  import { useKnowledgeStore } from '@/store';

  const knowledgeStore = useKnowledgeStore();
</script>
