import { defineStore } from 'pinia';
import { queryAllLlm } from '@/api/llm';
import { KnowledgeState } from './types';

const useKnowledgeStore = defineStore('knowledge', {
  state: (): KnowledgeState => ({
    llms: [] as string[],
    embeddings: [] as string[],
    graphDeeps: [2, 4, 6, 8, 10, 12],
    currentLlm: 'wizardlm2',
    currentEmbedding: 'sbert',
    maxGraphDeep: 4,
    maxTokensEachChunk: 128,
    selectedNode: undefined,
    selectedRelationship: undefined,
    overview: undefined,
    messageCount: 3,
    isSummary: true,
    currentMessageSummaryType: 'stuff',
    messageSummaryTypes: ['stuff', 'refine', 'map_reduce'],
    testLibId: undefined,
    testSubjectId: undefined,
    testMessageProcessing: false,
    testReturnMethods: ['sync', 'stream'],
    testReturnMethod: 'sync',
    queryResultRecord: undefined,
    searchScopes: ['question', 'page', 'document', 'webpage', 'node'],
    searchTypes: ['fulltext', 'vector', 'hybrid'],
    selectedSearchScopes: ['question', 'page', 'document', 'webpage', 'node'],
    selectedSearchType: 'vector',
    onlyTitle: false,
    isAnalyzingGraph: false,
  }),

  getters: {
    knowledgeInfo(state: KnowledgeState): KnowledgeState {
      return { ...state };
    },
  },

  actions: {
    setKnowledge(partial: Partial<KnowledgeState>) {
      this.$patch(partial);
    },

    // Get all available llms
    async queryAll() {
      const response = await queryAllLlm();
      if (!response.data) return;
      const { data } = response;
      this.setKnowledge({ llms: data.llms, embeddings: data.embeddings });
    },

    setCurrentLlm(llm: string) {
      this.setKnowledge({ currentLlm: llm });
    },

    setCurrentEmbedding(embedding: string) {
      this.setKnowledge({ currentEmbedding: embedding });
    },

    setMaxGraphDeep(deep: number) {
      this.setKnowledge({ maxGraphDeep: deep });
    },
  },
});

export default useKnowledgeStore;
