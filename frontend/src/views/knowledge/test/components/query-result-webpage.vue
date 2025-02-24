<template>
  <a-typography-text v-if="knowledgeStore.queryResultRecord?.webpage">
    <a-link
      :href="void 0"
      @click="openWebpage(knowledgeStore.queryResultRecord?.webpage.url)"
      >{{ knowledgeStore.queryResultRecord?.webpage.url }}</a-link
    >
    <a-typography-paragraph
      :copyable="true"
      :ellipsis="{
        rows: 6,
      }"
    >
      {{ knowledgeStore.queryResultRecord?.webpage.title }}
    </a-typography-paragraph>
    <a-typography-paragraph
      :copyable="true"
      :ellipsis="{
        rows: 6,
      }"
    >
      {{ knowledgeStore.queryResultRecord?.webpage.content }}
    </a-typography-paragraph>
  </a-typography-text>
</template>

<script lang="ts" setup>
  import { useKnowledgeStore } from '@/store';
  import { openWindow } from '@/utils';

  const knowledgeStore = useKnowledgeStore();

  const openWebpage = (url: string) => {
    openWindow(url, { target: '_blank' });
  };
</script>
