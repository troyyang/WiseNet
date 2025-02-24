<template>
  <a-space
    v-if="knowledgeStore.overview"
    direction="vertical"
    :size="4"
    :copyable="true"
  >
    <a-typography-title :heading="5">
      {{ t('knowledge.information.node') }}
    </a-typography-title>
    <a-typography-text
      v-for="node in knowledgeStore.overview.nodes"
      :key="node.type"
      :copyable="true"
    >
      <a-typography-text bold> {{ node.type }}: </a-typography-text>
      <a-typography-text>{{ node.count }}</a-typography-text>
    </a-typography-text>
    <a-typography-title :heading="5">
      {{ t('knowledge.information.link') }}
    </a-typography-title>
    <a-typography-text
      v-for="link in knowledgeStore.overview.links"
      :key="link.type"
      :copyable="true"
    >
      <a-typography-text bold> {{ link.type }}: </a-typography-text>
      <a-typography-text>{{ link.count }}</a-typography-text>
    </a-typography-text>
  </a-space>
</template>

<script lang="ts" setup>
  import { useI18n } from 'vue-i18n';
  import { useKnowledgeStore } from '@/store';

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();
</script>
