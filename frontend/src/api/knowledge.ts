import axios from 'axios';

export interface KnowledgeLibRecord {
  id: number | null;
  title: string | null;
  content: string;
  createTime: string;
  updateTime: string;
  editable: boolean;
  selected: boolean;
  status: string | null;
}

export interface KnowledgeSubjectRecord {
  id: number | null;
  name: string;
  knowledgeLibId: number | null;
  createTime: string;
  updateTime: string;
  editable: boolean;
  selected: boolean;
  editError: string;
}

export function queryKnowledgeLibList(condition: any) {
  return axios.post<KnowledgeLibRecord[]>('/api/knowledge/lib/find', condition);
}

export function searchKnowledgeLibList(condition: any) {
  return axios.post<KnowledgeLibRecord[]>(
    '/api/knowledge/lib/search',
    condition
  );
}

export function queryKnowledgeSubjectList(libId: number | null) {
  if (!libId) return null;
  const url = `/api/knowledge/subject/find/${libId}`;
  return axios.get<KnowledgeSubjectRecord[]>(url);
}

export function createSubject(data: KnowledgeSubjectRecord | null) {
  if (!data) return null;
  const url = `/api/knowledge/subject`;
  return axios.post<KnowledgeSubjectRecord>(url, data);
}

export function updateSubject(data: KnowledgeSubjectRecord | null) {
  if (!data) return null;
  const url = `/api/knowledge/subject`;
  return axios.put<KnowledgeSubjectRecord>(url, data);
}

export function deleteSubject(subjectId: number | null) {
  if (!subjectId) return null;
  const url = `/api/knowledge/subject/${subjectId}`;
  return axios.delete<any>(url);
}

export function createKnowledgeLib(data: KnowledgeLibRecord | null) {
  if (!data) return null;
  const url = `/api/knowledge/lib`;
  return axios.post<KnowledgeLibRecord>(url, data);
}

export function updateKnowledgeLib(data: KnowledgeLibRecord | null) {
  if (!data) return null;
  const url = `/api/knowledge/lib`;
  return axios.put<KnowledgeLibRecord>(url, data);
}

export function deleteKnowledgeLib(libId: number | null) {
  if (!libId) return null;
  const url = `/api/knowledge/lib/${libId}`;
  return axios.delete<any>(url);
}

export function publishKnowledgeLib(libId: number | null) {
  if (!libId) return null;
  const url = `/api/knowledge/lib/publish/${libId}`;
  return axios.get<KnowledgeLibRecord>(url);
}
