<template>
  <a-card class="general-card" :title="$t('config.title')">
    <a-space direction="vertical" size="small" fill>
      <a-space direction="horizontal" size="small" fill>
        <label>{{ t('menu.knowledge') }}</label>
        <a-select
          v-model="knowledgeStore.testLibId"
          :style="{ width: '320px' }"
          :placeholder="t('menu.knowledge')"
          :title="t('menu.knowledge')"
          allow-search
          @change="knowlegeChange"
        >
          <a-option
            v-for="knowledgeLib in knowledgeLibData"
            :key="knowledgeLib.id ? knowledgeLib.id : undefined"
            :value="knowledgeLib.id ? knowledgeLib.id : undefined"
            :title="knowledgeLib.title"
          >
            {{ knowledgeLib.title }}
          </a-option>
        </a-select>
        <a-select
          v-model="knowledgeStore.testSubjectId"
          :style="{ width: '320px' }"
          :placeholder="t('menu.knowledge.subject')"
          :title="t('menu.knowledge.subject')"
          allow-search
        >
          <a-option value="">
            {{ t('knowledge.operation.noselected') }}
          </a-option>
          <a-option
            v-for="subject in subjectData"
            :key="subject.id ? subject.id : undefined"
            :value="subject.id ? subject.id : undefined"
            :title="subject.name"
          >
            {{ subject.name }}
          </a-option>
        </a-select>
      </a-space>
      <a-space direction="horizontal" size="small" fill>
        <label>{{ t('knowledge.graph.llm') }}</label>
        <a-select
          v-model="knowledgeStore.currentLlm"
          :style="{ width: '160px' }"
          :placeholder="t('knowledge.graph.llm')"
          :title="t('knowledge.graph.llm')"
        >
          <a-option value="">
            {{ t('knowledge.operation.noselected') }}
          </a-option>
          <a-option v-for="llm in knowledgeStore.llms" :key="llm" :value="llm">
            {{ llm }}
          </a-option>
        </a-select>
        <a-tooltip :content="t('test.config.message.return.method')">
          <a-select
            v-model="knowledgeStore.testReturnMethod"
            :style="{ width: '95px' }"
            :title="t('menu.knowledge.subject')"
          >
            <a-option
              v-for="returnMethod in knowledgeStore.testReturnMethods"
              :key="returnMethod"
              :value="returnMethod"
              :title="returnMethod"
            >
              {{ returnMethod }}
            </a-option>
          </a-select>
        </a-tooltip>
        <a-tooltip :content="t('knowledge.graph.embedding')">
          <a-select
            v-model="knowledgeStore.currentEmbedding"
            :style="{ width: '80px' }"
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
      <a-space direction="horizontal" size="small" fill>
        <label>{{ t('test.config.message') }}</label>
        <a-tooltip :content="t('test.config.messages.count')">
          <a-input-number
            v-model="knowledgeStore.messageCount"
            :style="{ width: '70px' }"
            :min="1"
            :max="20"
          />
        </a-tooltip>
        <a-tooltip :content="t('test.config.message.summary.type')">
          <a-select
            v-model="knowledgeStore.currentMessageSummaryType"
            :style="{ width: '110px' }"
            :title="t('test.config.message.summary.type')"
          >
            <a-option
              v-for="messageSummaryType in knowledgeStore.messageSummaryTypes"
              :key="messageSummaryType"
              :value="messageSummaryType"
              :title="messageSummaryType"
            >
              {{ messageSummaryType }}
            </a-option>
          </a-select>
          <a-tooltip :content="t('test.config.summary.detail')">
            <a-checkbox v-model="knowledgeStore.isSummary">{{
              t('test.config.summary')
            }}</a-checkbox>
          </a-tooltip>
        </a-tooltip>
      </a-space>
      <a-space direction="horizontal" size="small" fill>
        <label>{{ t('test.config.search.scope') }}</label>
        <a-checkbox-group v-model="knowledgeStore.selectedSearchScopes">
          <a-checkbox
            v-for="scope in knowledgeStore.searchScopes"
            :key="scope"
            :value="scope"
            >{{ scope }}</a-checkbox
          >
        </a-checkbox-group>
        <a-checkbox v-model="knowledgeStore.onlyTitle">{{
          t('test.config.only.title')
        }}</a-checkbox>
        <a-tooltip :content="t('test.config.search.type')">
          <a-select
            v-model="knowledgeStore.selectedSearchType"
            :style="{ width: '100px' }"
            :placeholder="t('test.config.search.type')"
            :title="t('test.config.search.type')"
          >
            <a-option
              v-for="searchType in knowledgeStore.searchTypes"
              :key="searchType"
              :value="searchType"
            >
              {{ searchType }}
            </a-option>
          </a-select>
        </a-tooltip>
      </a-space>
    </a-space>
  </a-card>
</template>

<script lang="ts" setup>
  import { onMounted, ref } from 'vue';
  import { useI18n } from 'vue-i18n';
  import {
    KnowledgeLibRecord,
    KnowledgeSubjectRecord,
    searchKnowledgeLibList,
    queryKnowledgeSubjectList,
  } from '@/api/knowledge';
  import { useKnowledgeStore } from '@/store';
  import useLoading from '@/hooks/loading';

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();
  const knowledgeLibData = ref<KnowledgeLibRecord[]>([]);
  const subjectData = ref<KnowledgeSubjectRecord[]>([]);

  const { setLoading } = useLoading();

  const fetchSubjects = async () => {
    if (!knowledgeStore.testLibId) return;

    try {
      setLoading(true);
      knowledgeStore.testSubjectId = undefined;
      subjectData.value = [];
      const response = await queryKnowledgeSubjectList(
        knowledgeStore.testLibId
      );
      if (!response) return;
      const { data } = response;
      if (data && data.length > 0) {
        subjectData.value = data;
      } else {
        subjectData.value = [];
      }
      setLoading(false);
    } catch (err) {
      // you can report use errorHandler or other
      subjectData.value = [];
    } finally {
      setLoading(false);
    }
  };

  const fetchKnowledgeLib = async () => {
    try {
      setLoading(true);
      const response = await searchKnowledgeLibList({});
      const { data } = response;
      if (data && data.length > 0) {
        knowledgeLibData.value = data;
        knowledgeStore.testLibId = data[0].id ? data[0].id : undefined;
        fetchSubjects();
      } else {
        knowledgeLibData.value = [];
        subjectData.value = [];
        knowledgeStore.testLibId = undefined;
      }
      setLoading(false);
    } catch (err) {
      // you can report use errorHandler or other
      knowledgeLibData.value = [];
      subjectData.value = [];
      knowledgeStore.testLibId = undefined;
    } finally {
      setLoading(false);
    }
  };

  const knowlegeChange = () => {
    fetchSubjects();
  };

  onMounted(() => {
    knowledgeStore.queryAll();
    fetchKnowledgeLib();
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
