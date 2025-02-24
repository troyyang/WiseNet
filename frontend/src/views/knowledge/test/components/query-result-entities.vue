<template>
  <a-typography
    v-if="
      knowledgeStore.queryResultRecord?.entities &&
      knowledgeStore.queryResultRecord?.entities.length > 0
    "
    :copyable="true"
  >
    <a-typography-title :heading="6">
      {{ t('knowledge.information.entities') }}
    </a-typography-title>
    <a-typography-text>
      <ol>
        <li
          v-for="entity in knowledgeStore.queryResultRecord?.entities"
          :key="entity.elementId"
        >
          {{ entity.content }}
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
