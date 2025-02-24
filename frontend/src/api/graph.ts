import axios from 'axios';
import { getToken } from '@/utils/auth';

export interface EntityRecord {
  elementId: string;
  content: string;
  contentVector: number[];
}

export interface KeywordRecord {
  elementId: string;
  content: string;
  contentVector: number[];
}

export interface TagRecord {
  elementId: string;
  content: string;
  contentVector: number[];
}

export interface DocumentPageRecord {
  elementId: string;
  source: string;
  title: string;
  subtitle: string;
  row: number;
  page: number;
  content: string;
  contentVector: number[];
}

export interface DocumentRecord {
  elementId: string;
  name: string;
  title: string;
  content: string;
  titleVector: number[];
  contentVector: number[];
  savedAt: string;
  pages: DocumentPageRecord[];
  analyzing: boolean;
  loaded: boolean;
}

export interface WebPageRecord {
  elementId: string;
  url: string;
  title: string;
  titleVector: number[];
  content: string;
  contentVector: number[];
  pages: DocumentPageRecord[];
  analyzing: boolean;
  loaded: boolean;
}

export interface NodeRecord {
  elementId: string;
  id: number;
  labels: string[];
  libId: number;
  subjectId: number;
  content: string;
  contentVector: number[];
  title: string;
  titleVector: number[];
  entities: EntityRecord[];
  keywords: KeywordRecord[];
  tags: TagRecord[];
  documents: DocumentRecord[];
  webpages: WebPageRecord[];
  createdAt: string;
  updatedAt: string;
  type: string;
  editable: boolean;
  editError: string;
  index: number;
  x: number;
  y: number;
}

export interface RelationshipRecord {
  elementId: string;
  id: number;
  source: NodeRecord;
  target: NodeRecord;
  sourceElementId: string;
  targetElementId: string;
  type: string;
  libId: number;
  subjectId: number;
  content: string;
  contentVector: number[];
  createdAt: string;
  updatedAt: string;
  editable: boolean;
  selected: boolean;
  editError: string;
}

export interface OverviewRecord {
  type: string;
  count: number;
}

export interface GraphRecord {
  nodes: NodeRecord[];
  links: RelationshipRecord[];
  overview: {
    nodes: OverviewRecord[];
    links: OverviewRecord[];
  };
}

export interface QueryResultRecord {
  text: string;
  mainNode: NodeRecord | null;
  entities: EntityRecord[];
  keywords: KeywordRecord[];
  tags: TagRecord[];
  prompts: NodeRecord[];
  webpage: WebPageRecord | null;
  document: DocumentRecord | null;
  relatedNodes: NodeRecord[];
}

export interface MessageRecord {
  id: number;
  type: string;
  content: string;
  time: Date;
  queryResult: QueryResultRecord | null;
}

export const getUploadUrl = () => {
  return `${axios.defaults.baseURL}/api/graph/node/upload/file`;
};

export const getDownloadUrl = (fileName: string) => {
  return `${axios.defaults.baseURL}/api/graph/node/download/file/${fileName}`;
};

export function queryGraph(libId: number, condition: any) {
  const url = `/api/graph/query/${libId}`;
  return axios.post<any>(url, condition);
}

export function queryGraphOverview(libId: number, condition: any) {
  const url = `/api/graph/overview/${libId}`;
  return axios.post<{
    nodes: OverviewRecord[];
    links: OverviewRecord[];
  }>(url, condition);
}

export function cancelGenerateGraph(libId: number | null) {
  if (!libId) return null;
  const url = `/api/graph/cancel/${libId}`;
  return axios.post<any>(url);
}

export function generateGraph(data: any) {
  const url = `/api/graph/generate`;
  return axios.post<any>(url, data);
}

export function analyzeGraph(data: any) {
  const url = `/api/graph/analyze`;
  return axios.post<any>(url, data);
}

export function deleteGraphNode(elementId: string) {
  const url = `/api/graph/node/${elementId}`;
  return axios.delete<any>(url);
}

export function deleteGraphRelationship(elementId: string) {
  const url = `/api/graph/relationship/${elementId}`;
  return axios.delete<any>(url);
}

export function addGraphNode(node: any) {
  const url = `/api/graph/node`;
  return axios.post<{ node: NodeRecord; relationship: RelationshipRecord }>(
    url,
    node
  );
}

export function addGraphRelationship(relationship: any) {
  const url = `/api/graph/relationship`;
  return axios.post<RelationshipRecord>(url, relationship);
}

export function updateNodeInfo(
  node: NodeRecord,
  embeddingModel: string | null,
  maxTokensEachChunk: number
) {
  const url = `/api/graph/node`;
  const data = {
    libId: node.libId,
    subjectId: node.subjectId,
    elementId: node.elementId,
    content: node.content,
    embeddingModel,
    maxTokensEachChunk,
  };
  return axios.put<NodeRecord>(url, data);
}

export function updateRelationshipInfo(
  link: RelationshipRecord,
  embeddingModel: string | null,
  maxTokensEachChunk: number
) {
  const url = `/api/graph/relationship/info`;
  const data = {
    elementId: link.elementId,
    content: link.content,
    embeddingModel,
    maxTokensEachChunk,
  };
  return axios.put<RelationshipRecord>(url, data);
}

export function queryNodeDetail(elementId: string) {
  const url = `/api/graph/node/${elementId}`;
  return axios.get<NodeRecord>(url);
}

export function queryRelationshipDetail(elementId: string) {
  const url = `/api/graph/relationship/${elementId}`;
  return axios.get<RelationshipRecord>(url);
}

export function generateGraphAnswer(
  libId: number,
  subjectId: number,
  elementId: string,
  llmName: string | null
) {
  const url = `/api/graph/generate/answer`;
  const data = { libId, subjectId, elementId, llmName };
  return axios.post<any>(url, data);
}

export function generateGraphQuestions(
  libId: number,
  subjectId: number,
  elementId: string,
  llmName: string
) {
  const url = `/api/graph/generate/questions`;
  const data = { libId, subjectId, elementId, llmName };
  return axios.post<any>(url, data);
}

export function generateGraphPrompts(
  libId: number,
  subjectId: number,
  elementId: string,
  llmName: string
) {
  const url = `/api/graph/generate/prompts`;
  const data = { libId, subjectId, elementId, llmName };
  return axios.post<any>(url, data);
}

export function analyzeGraphNode(
  elementId: string,
  llmName: string | null,
  embeddingModel: string | null,
  maxTokensEachChunk: number
) {
  const url = `/api/graph/node/analyze`;
  const data = {
    elementId,
    llmName,
    embeddingModel,
    maxTokensEachChunk,
  };
  return axios.post<any>(url, data);
}

export function deleteGraphNodeEntity(
  entityElementId: string,
  nodeElementId: string
) {
  const url = `/api/graph/node/entity/${entityElementId}/${nodeElementId}`;
  return axios.delete<any>(url);
}

export function deleteGraphNodeKeyword(
  keywordElementId: string,
  nodeElementId: string
) {
  const url = `/api/graph/node/keyword/${keywordElementId}/${nodeElementId}`;
  return axios.delete<any>(url);
}

export function deleteGraphNodeTag(
  tagElementId: string,
  nodeElementId: string
) {
  const url = `/api/graph/node/tag/${tagElementId}/${nodeElementId}`;
  return axios.delete<any>(url);
}

export function deleteGraphNodeDocument(documentElementId: string) {
  const url = `/api/graph/node/document/${documentElementId}`;
  return axios.delete<any>(url);
}

export function analyzeGraphNodeDocument(
  elementId: string,
  llmName: string | null,
  embeddingModel: string | null,
  maxTokensEachChunk: number
) {
  const url = `/api/graph/node/document/analyze`;
  const data = {
    elementId, // document element id
    llmName,
    embeddingModel,
    maxTokensEachChunk,
  };
  return axios.post<any>(url, data);
}

export function getGraphNodeDocument(documentElementId: string) {
  const url = `/api/graph/node/document/detail/${documentElementId}`;
  return axios.get<any>(url);
}

export function addGraphNodeWebpage(
  libId: number,
  subjectId: number,
  elementId: string,
  webUrl: string
) {
  const url = `/api/graph/node/webpage`;
  const data = {
    elementId,
    url: webUrl,
    libId,
    subjectId,
  };
  return axios.post<any>(url, data);
}

export function analyzeGraphNodeWebpage(
  elementId: string,
  llmName: string | null,
  embeddingModel: string | null,
  maxTokensEachChunk: number
) {
  const url = `/api/graph/node/webpage/analyze`;
  const data = {
    elementId,
    llmName,
    embeddingModel,
    maxTokensEachChunk,
  };
  return axios.post<any>(url, data);
}

export function getGraphNodeWebpageDetail(elementId: string) {
  const url = `/api/graph/node/webpage/${elementId}`;
  return axios.get<any>(url);
}

export function deleteGraphNodeWebpageDetail(elementId: string) {
  const url = `/api/graph/node/webpage/detail/${elementId}`;
  return axios.delete<any>(url);
}

export function getGraphNodeDocumentDetail(documentElementId: string) {
  const url = `/api/graph/node/document/detail/${documentElementId}`;
  return axios.get<any>(url);
}

export function deleteGraphNodeWebpage(webpageElementId: string) {
  const url = `/api/graph/node/webpage/${webpageElementId}`;
  return axios.delete<any>(url);
}

export function sendMessage(data: any) {
  const url = `/api/graph/search`;
  return axios.post<QueryResultRecord>(url, data);
}

// Helper function to process ReadableStream without async generators
function streamProcessor(
  stream: ReadableStream<Uint8Array>,
  onData: (data: any) => void,
  onEnd?: () => void,
  onError?: (error: any) => void
) {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let partialData = '';

  function processChunk() {
    reader
      .read()
      .then(({ value, done }) => {
        if (done) {
          if (onEnd) onEnd();
          return;
        }

        partialData += decoder.decode(value, { stream: true });

        // Process each JSON object when a new line is encountered
        const lines = partialData.split('\n');
        partialData = lines.pop() || ''; // Save incomplete JSON for next iteration

        lines.forEach((line) => {
          if (line.trim()) {
            try {
              const parsedData = JSON.parse(line);
              if (parsedData.end) {
                console.log('Stream ended.');
                return;
              }
              onData(parsedData);
            } catch (error) {
              console.error('Error parsing JSON:', error);
            }
          }
        });

        // Recursively process next chunk
        processChunk();
      })
      .catch((error) => {
        console.error('Streaming error:', error);
        if (onError) onError(error);
      });
  }

  processChunk();
}

export function sendMessageStream(
  queryCondition: any,
  onData: (data: any) => void,
  onEnd?: () => void,
  onError?: (error: any) => void
) {
  const url = `${axios.defaults.baseURL}/api/graph/search`;
  const token = getToken();

  fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'Accept': 'application/x-ndjson', // Accept NDJSON format
      'X-Streaming-Response': 'true', // Custom header to bypass interceptor
    },
    body: JSON.stringify(queryCondition),
  })
    .then((response) => {
      if (!response.ok || !response.body) {
        console.log('Response error:', response);
        throw new Error('Failed to fetch data');
      }
      return response.body;
    })
    .then((stream) => {
      streamProcessor(stream, onData, onEnd, onError);
    })
    .catch((error) => {
      console.error('Fetch error:', error);
      if (onError) onError(error);
    });
}

// export function sendMessageStream(
//   queryCondition: any,
//   onData: (data: any) => void,
//   onEnd: () => void,
//   onError: (error: any) => void
// ) {
//   const url = '/api/graph/search';

//   // Make a POST request with streaming enabled
//   fetch(url, {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//       'Accept': 'application/x-ndjson', // Accept NDJSON format
//       'X-Streaming-Response': 'true', // Custom header to bypass interceptor
//     },
//     body: JSON.stringify(queryCondition),
//   })
//     .then((response) => {
//       if (!response.ok) {
//         throw new Error(`HTTP error! Status: ${response.status}`);
//       }

//       // Get the readable stream from the response body
//       const reader = response.body?.getReader();
//       if (!reader) {
//         throw new Error('ReadableStream not supported in this browser');
//       }

//       // Buffer to accumulate chunks of data
//       let buffer = '';

//       // Function to process each chunk
//       const processChunk = ({ done, value }: ReadableStreamReadResult<Uint8Array>) => {
//         if (done) {
//           // Handle end of stream
//           if (buffer.trim()) {
//             try {
//               const data = JSON.parse(buffer);
//               if (data.end) {
//                 onEnd();
//               } else if (data.error) {
//                 onError(data.error);
//               } else {
//                 onData(data);
//               }
//             } catch (e) {
//               onError(e);
//             }
//           }
//           onEnd(); // Ensure onEnd is called
//           return;
//         }

//         // Convert the chunk to a string and append to the buffer
//         buffer += new TextDecoder().decode(value);

//         // Split the buffer by newlines to handle multiple JSON objects
//         const lines = buffer.split('\n');
//         buffer = lines.pop() || ''; // Keep the last incomplete line in the buffer
//         console.log('lines', lines);

//         // Process each complete line as a JSON object
//         lines.forEach((line) => {
//           if (line.trim()) {
//             try {
//               const data = JSON.parse(line);
//               if (data.end) {
//                 onEnd();
//               } else if (data.error) {
//                 onError(data.error);
//               } else {
//                 onData(data);
//               }
//             } catch (e) {
//               onError(e);
//             }
//           }
//         });

//         // Read the next chunk
//         return reader.read().then(processChunk);
//       };

//       // Start reading the stream
//       return reader.read().then(processChunk);
//     })
//     .catch((error) => {
//       // Handle fetch errors (e.g., network errors, server errors)
//       onError(error);
//     });
// }

// export function sendMessageStream(
//   queryCondition: any,
//   onData: (data: any) => void,
//   onEnd: () => void,
//   onError: (error: any) => void
// ) {
//   const url = '/api/graph/search';

//   // Make a POST request with streaming enabled
//   axios
//     .post(url, queryCondition, {
//       responseType: 'stream', // Ensure the response is treated as a stream
//       headers: {
//         Accept: 'application/x-ndjson', // Accept NDJSON format
//         'X-Streaming-Response': 'true', // Custom header to bypass interceptor
//       },
//     })
//     .then((response: AxiosResponse) => {
//       const stream = response.data;

//       // Buffer to accumulate chunks of data
//       let buffer = '';

//       // Handle data events
//       stream.on('data', (chunk: Buffer) => {
//         buffer += chunk.toString();

//         // Split the buffer by newlines to handle multiple JSON objects
//         const lines = buffer.split('\n');
//         buffer = lines.pop() || ''; // Keep the last incomplete line in the buffer

//         // Process each complete line as a JSON object
//         lines.forEach((line) => {
//           if (line.trim()) {
//             try {
//               const data = JSON.parse(line);
//               if (data.end) {
//                 onEnd(); // Handle end of stream
//               } else if (data.error) {
//                 onError(data.error); // Handle errors
//               } else {
//                 onData(data); // Handle the data
//               }
//             } catch (e) {
//               onError(e); // Handle JSON parsing errors
//             }
//           }
//         });
//       });

//       // Handle end of stream
//       stream.on('end', () => {
//         if (buffer.trim()) {
//           try {
//             const data = JSON.parse(buffer);
//             if (data.end) {
//               onEnd();
//             } else if (data.error) {
//               onError(data.error);
//             } else {
//               onData(data);
//             }
//           } catch (e) {
//             onError(e);
//           }
//         }
//         onEnd(); // Ensure onEnd is called even if no data is left
//       });

//       // Handle stream errors
//       stream.on('error', (error: any) => {
//         onError(error);
//       });
//     })
//     .catch((error: any) => {
//       // Handle axios errors (e.g., network errors, server errors)
//       onError(error);
//     });
// }
