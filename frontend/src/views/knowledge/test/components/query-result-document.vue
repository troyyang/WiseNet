<template>
  <a-typography-text v-if="knowledgeStore.queryResultRecord?.document">
    <a-link
      :href="void 0"
      @click="openDocument(knowledgeStore.queryResultRecord?.document.savedAt)"
      >{{ knowledgeStore.queryResultRecord?.document.name }}</a-link
    >
    <a-typography-paragraph
      :copyable="true"
      :ellipsis="{
        rows: 2,
      }"
      bold
    >
      {{ knowledgeStore.queryResultRecord?.document.title }}
    </a-typography-paragraph>
    <a-typography-paragraph
      :copyable="true"
      :ellipsis="{
        rows: 6,
      }"
    >
      {{ knowledgeStore.queryResultRecord?.document.content }}
    </a-typography-paragraph>
  </a-typography-text>
</template>

<script lang="ts" setup>
  import { getDownloadUrl } from '@/api/graph';
  import { useKnowledgeStore } from '@/store';

  const knowledgeStore = useKnowledgeStore();

  const openDocument = (savedAt: string) => {
    window.open(getDownloadUrl(savedAt), '_blank');
  };
</script>
