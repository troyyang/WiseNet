<template>
  <a-card class="general-card" :title="$t('config.title')">
    <a-space direction="horizontal" size="small">
      <label>{{ t('knowledge.graph.llm') }}</label>
      <a-tooltip :content="t('knowledge.graph.llm')">
        <a-select
          v-model="knowledgeStore.currentLlm"
          :style="{ width: '160px' }"
          :placeholder="t('knowledge.graph.llm')"
          :title="t('knowledge.graph.llm')"
        >
          <a-option v-for="llm in knowledgeStore.llms" :key="llm" :value="llm">
            {{ llm }}
          </a-option>
        </a-select>
      </a-tooltip>
      <a-tooltip :content="t('knowledge.graph.embedding')">
        <a-select
          v-model="knowledgeStore.currentEmbedding"
          :style="{ width: '100px' }"
          :placeholder="t('knowledge.graph.embedding')"
          :title="t('knowledge.graph.embedding')"
        >
          <a-option
            v-for="embedding in knowledgeStore.embeddings"
            :key="embedding"
            :value="embedding"
          >
            {{ embedding }}
          </a-option>
        </a-select>
      </a-tooltip>
      <a-tooltip :content="t('knowledge.graph.max.tokens')">
        <a-input-number
          v-model="knowledgeStore.maxTokensEachChunk"
          :style="{ width: '70px' }"
          :min="10"
          :max="128"
        />
      </a-tooltip>
    </a-space>
  </a-card>
</template>

<script lang="ts" setup>
  import { onMounted } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { useKnowledgeStore } from '@/store';

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();

  onMounted(() => {
    knowledgeStore.queryAll();
  });
</script>

<style scoped lang="less">
  .config {
    display: flex;
    background-color: var(--color-bg-2);
    padding: 10px 10px;
    border-radius: 3px;
  }
</style>
