<template>
  <a-typography
    v-if="
      knowledgeStore.queryResultRecord?.tags &&
      knowledgeStore.queryResultRecord?.tags.length > 0
    "
    :copyable="true"
  >
    <a-typography-title :heading="6">
      {{ t('knowledge.information.tags') }}
    </a-typography-title>
    <a-typography-text>
      <ol>
        <li
          v-for="tag in knowledgeStore.queryResultRecord?.tags"
          :key="tag.elementId"
        >
          {{ tag.content }}
        </li>
      </ol>
    </a-typography-text>
  </a-typography>
</template>

<script lang="ts" setup>
  import { useI18n } from 'vue-i18n';
  import { useKnowledgeStore } from '@/store';

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();
</script>
