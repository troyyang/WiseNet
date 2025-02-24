import axios from 'axios';

export interface LlmQueryResponse {
  llms: string[];
  embeddings: string[];
}

export function queryAllLlm() {
  return axios.get<LlmQueryResponse>('/api/llm/all');
}

export default queryAllLlm;
