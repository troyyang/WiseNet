import {
  NodeRecord,
  RelationshipRecord,
  OverviewRecord,
  QueryResultRecord,
} from '@/api/graph';

export interface KnowledgeState {
  maxGraphDeep?: number;
  llms?: string[];
  embeddings?: string[];
  graphDeeps?: number[];
  currentLlm?: string;
  currentEmbedding?: string;
  maxTokensEachChunk: number;
  selectedNode?: NodeRecord;
  selectedRelationship?: RelationshipRecord;
  overview?: {
    nodes: OverviewRecord[];
    links: OverviewRecord[];
  };
  messageCount: number;
  isSummary: boolean;
  currentMessageSummaryType: string;
  messageSummaryTypes: string[];
  testLibId?: number;
  testSubjectId?: number;
  testMessageProcessing?: boolean;
  testReturnMethods?: string[];
  testReturnMethod: string;
  queryResultRecord?: QueryResultRecord;
  searchScopes?: string[];
  searchTypes?: string[];
  selectedSearchScopes?: string[];
  selectedSearchType?: string;
  onlyTitle?: boolean;
  isAnalyzingGraph?: boolean;
}
