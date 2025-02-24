<template>
  <a-typography
    v-if="
      knowledgeStore.queryResultRecord?.keywords &&
      knowledgeStore.queryResultRecord?.keywords.length > 0
    "
    :copyable="true"
  >
    <a-typography-title :heading="6">
      {{ t('knowledge.information.keywords') }}
    </a-typography-title>
    <a-typography-text>
      <ol>
        <li
          v-for="keyword in knowledgeStore.queryResultRecord?.keywords"
          :key="keyword.elementId"
        >
          {{ keyword.content }}
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
