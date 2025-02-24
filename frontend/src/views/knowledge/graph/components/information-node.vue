<template>
  <a-spin :loading="loading" style="width: 100%; min-height: 1600px">
    <a-space>
      <a-button
        v-if="
          knowledgeStore.selectedNode &&
          !knowledgeStore.selectedNode.editable &&
          knowledgeStore.selectedNode.content
        "
        :title="$t('knowledge.graph.analysis')"
        type="secondary"
        @click="analysis"
      >
        <template #icon>
          <icon-command />
        </template>
      </a-button>
      <a-button
        v-if="
          knowledgeStore.selectedNode &&
          !knowledgeStore.selectedNode.editable &&
          knowledgeStore.selectedNode.content &&
          (knowledgeStore.selectedNode.type === 'HUMAN' ||
            knowledgeStore.selectedNode.type === 'INFO')
        "
        :title="$t('knowledge.operation.generete.question')"
        type="secondary"
        @click="generateQuestion"
      >
        <template #icon>
          <icon-question-circle />
        </template>
      </a-button>
      <a-button
        v-if="
          knowledgeStore.selectedNode &&
          !knowledgeStore.selectedNode.editable &&
          knowledgeStore.selectedNode.content &&
          (knowledgeStore.selectedNode.type === 'HUMAN' ||
            knowledgeStore.selectedNode.type === 'QUESTION')
        "
        :title="$t('knowledge.operation.generete.answer')"
        type="secondary"
        @click="generateAnswer"
      >
        <template #icon>
          <icon-translate />
        </template>
      </a-button>
      <a-button
        v-if="
          file &&
          file.status === 'uploading' &&
          knowledgeStore.selectedNode &&
          (knowledgeStore.selectedNode.type === 'HUMAN' ||
            knowledgeStore.selectedNode.type === 'INFO')
        "
        :title="$t('knowledge.graph.import.file')"
        type="secondary"
      >
        <template #icon>
          <icon-loading />
        </template>
      </a-button>
      <a-upload
        v-if="
          knowledgeStore.selectedNode &&
          !knowledgeStore.selectedNode.editable &&
          knowledgeStore.selectedNode.content &&
          (knowledgeStore.selectedNode.type === 'HUMAN' ||
            knowledgeStore.selectedNode.type === 'INFO')
        "
        :title="$t('knowledge.graph.import.file')"
        :action="getUploadUrl()"
        :file-list="file ? [file] : []"
        :show-file-list="false"
        :limit="1"
        :headers="{
          'Authorization': 'Bearer ' + token,
          'accept-language': locale,
        }"
        :data="{
          lib_id: knowledgeStore.selectedNode.libId,
          subject_id: knowledgeStore.selectedNode.subjectId,
          element_id: knowledgeStore.selectedNode.elementId,
        } as any"
        accept=".pdf,.doc,.docx,ppt,.pptx,.xml,.json,.xls,.xlsx,.csv,.json,.xml,.html,.txt,.md"
        @change="onFileChange"
        @error="onFileError"
      >
        <template #upload-button>
          <a-space>
            <a-button>
              <template #icon>
                <icon-upload />
              </template>
            </a-button>
          </a-space>
        </template>
      </a-upload>
      <a-button
        v-if="
          knowledgeStore.selectedNode &&
          !knowledgeStore.selectedNode.editable &&
          knowledgeStore.selectedNode.content &&
          (knowledgeStore.selectedNode.type === 'HUMAN' ||
            knowledgeStore.selectedNode.type === 'INFO')
        "
        :title="$t('knowledge.graph.add.webpage')"
        type="secondary"
        @click="addWebPage"
      >
        <template #icon>
          <icon-link />
        </template>
      </a-button>
    </a-space>
    <a-space
      v-if="isShowInputUrlPane"
      orientation="vertical"
      :style="{ marginTop: '8px' }"
    >
      <a-input
        v-model="webUrl"
        width="100%"
        :max-length="2048"
        placeholder="https://"
        :error="!!editWebPageError"
        @press-enter="submitAddWebPage"
      >
        <template #suffix>
          <a-button type="secondary" size="mini" @click="submitAddWebPage">
            <icon-save style="cursor: pointer" />
          </a-button>
          <a-button type="secondary" size="mini" @click="cancelAddWebPage">
            <icon-close style="cursor: pointer; margin-left: 2px" />
          </a-button>
        </template>
      </a-input>
      <a-typography-text v-if="editWebPageError" type="danger">
        {{ editWebPageError }}
      </a-typography-text>
    </a-space>
    <a-space
      v-if="
        knowledgeStore.selectedNode && !knowledgeStore.selectedNode.editable
      "
      direction="vertical"
      :size="4"
    >
      <a-typography-title :heading="5" :copyable="true">
        {{ knowledgeStore.selectedNode.type }}
      </a-typography-title>
      <a-collapse
        expand-icon-position="right"
        :default-active-key="['1', '2', '3', '4', '5']"
        :bordered="false"
      >
        <template #expand-icon="{ active }">
          <icon-double-down v-if="active" />
          <icon-double-right v-else />
        </template>
        <a-collapse-item
          key="1"
          style="width: 320px"
          :header="t('knowledge.graph.basicInfo')"
        >
          <InformationNodeGraphInfo />
        </a-collapse-item>
        <a-collapse-item
          v-if="
            knowledgeStore.selectedNode &&
            ((knowledgeStore.selectedNode.entities &&
              knowledgeStore.selectedNode.entities.length > 0) ||
              (knowledgeStore.selectedNode.keywords &&
                knowledgeStore.selectedNode.keywords.length > 0) ||
              (knowledgeStore.selectedNode.tags &&
                knowledgeStore.selectedNode.tags.length > 0))
          "
          key="2"
          style="width: 320px"
          :header="t('knowledge.graph.extendedInfo')"
        >
          <InformationNodeEntities />
          <InformationNodeKeywords />
          <InformationNodeTags />
        </a-collapse-item>
        <a-collapse-item
          v-if="
            knowledgeStore.selectedNode &&
            knowledgeStore.selectedNode.documents &&
            knowledgeStore.selectedNode.documents.length > 0
          "
          key="3"
          style="width: 320px"
          :header="t('knowledge.information.documents')"
        >
          <InformationNodeDocuments />
        </a-collapse-item>
        <a-collapse-item
          v-if="
            knowledgeStore.selectedNode &&
            knowledgeStore.selectedNode.webpages &&
            knowledgeStore.selectedNode.webpages.length > 0
          "
          key="4"
          style="width: 320px"
          :header="t('knowledge.information.webpages')"
        >
          <InformationNodeWebpages />
        </a-collapse-item>
        <a-collapse-item
          key="5"
          style="width: 320px"
          :header="t('knowledge.graph.content')"
        >
          <InformationNodeContent />
        </a-collapse-item>
      </a-collapse>
    </a-space>
    <a-space
      v-if="knowledgeStore.selectedNode && knowledgeStore.selectedNode.editable"
      direction="vertical"
      :size="8"
      style="width: 100%"
    >
      <div style="display: flex; flex-direction: column; width: 100%">
        <a-textarea
          v-model="knowledgeStore.selectedNode.content"
          :placeholder="
            t('knowledge.graph.information.node.content.placeholder')
          "
          :max-length="500"
          allow-clear
          :auto-size="{ minRows: 16, maxRows: 30 }"
          style="flex-grow: 1"
          show-word-limit
        />
      </div>
      <a-space
        direction="horizontal"
        :size="8"
        style="justify-content: flex-end"
      >
        <a-button type="secondary" style="width: 100px" @click="cancelEdit">{{
          t('knowledge.operation.cancel')
        }}</a-button>
        <a-button type="primary" style="width: 100px" @click="saveMessage">{{
          t('knowledge.operation.submit')
        }}</a-button>
      </a-space>
    </a-space>
  </a-spin>
</template>

<script lang="ts" setup>
  import { onMounted, ref, defineAsyncComponent } from 'vue';
  import { useI18n } from 'vue-i18n';
  import EventBus from '@/utils/event-bus';
  import { formatTimestamp } from '@/utils/datetime';
  import { getToken } from '@/utils/auth';
  import {
    queryNodeDetail,
    generateGraphAnswer,
    generateGraphQuestions,
    analyzeGraphNode,
    getUploadUrl,
    addGraphNodeWebpage,
  } from '@/api/graph';
  import { useKnowledgeStore } from '@/store';
  import { Message } from '@arco-design/web-vue';
  import useLoading from '@/hooks/loading';
  import { regexUrl } from '@/utils';

  const InformationNodeGraphInfo = defineAsyncComponent(
    () => import('./information-node-graph-info.vue')
  );
  const InformationNodeEntities = defineAsyncComponent(
    () => import('./information-node-entities.vue')
  );
  const InformationNodeKeywords = defineAsyncComponent(
    () => import('./information-node-keywords.vue')
  );
  const InformationNodeTags = defineAsyncComponent(
    () => import('./information-node-tags.vue')
  );
  const InformationNodeDocuments = defineAsyncComponent(
    () => import('./information-node-documents.vue')
  );
  const InformationNodeWebpages = defineAsyncComponent(
    () => import('./information-node-webpages.vue')
  );
  const InformationNodeContent = defineAsyncComponent(
    () => import('./information-node-content.vue')
  );

  const { t, locale } = useI18n();
  const { loading, setLoading } = useLoading(false);
  const knowledgeStore = useKnowledgeStore();
  const token = getToken();

  const file = ref();
  const isShowInputUrlPane = ref(false);

  const onFileChange = (info: any, currentFile: any) => {
    file.value = {
      ...currentFile,
    };
    if (currentFile.status === 'done') {
      if (
        currentFile.response.code === 0 &&
        currentFile.response.data &&
        knowledgeStore.selectedNode &&
        knowledgeStore.selectedNode.documents
      ) {
        knowledgeStore.selectedNode.documents.push(currentFile.response.data);
      } else if (currentFile.response.code === -1) {
        Message.error(currentFile.response.msg);
      }

      file.value = null;
    } else if (currentFile.status === 'error') {
      Message.error(t('knowledge.operation.upload.failed'));
      file.value = null;
    }
  };

  const onFileError = () => {
    file.value = null;
  };

  const webUrl = ref('');
  const editWebPageError = ref('');
  const addWebPage = () => {
    webUrl.value = '';
    editWebPageError.value = '';
    isShowInputUrlPane.value = true;
  };

  const cancelAddWebPage = () => {
    webUrl.value = '';
    editWebPageError.value = '';
    isShowInputUrlPane.value = false;
  };

  const submitAddWebPage = () => {
    if (!regexUrl.test(webUrl.value)) {
      editWebPageError.value = t('knowledge.information.webpage.url.invalid');
      return;
    }
    editWebPageError.value = '';

    if (knowledgeStore.selectedNode) {
      addGraphNodeWebpage(
        knowledgeStore.selectedNode.libId,
        knowledgeStore.selectedNode.subjectId,
        knowledgeStore.selectedNode.elementId,
        webUrl.value
      )
        .then((response) => {
          const { data } = response;
          if (data && knowledgeStore.selectedNode) {
            knowledgeStore.selectedNode.webpages.push(data);
          }
        })
        .catch((error) => {
          Message.error(error);
        })
        .finally(() => {
          isShowInputUrlPane.value = false;
        });
    } else {
      isShowInputUrlPane.value = false;
    }
  };

  const cancelEdit = () => {
    if (knowledgeStore.selectedNode) {
      knowledgeStore.selectedNode.editable = false;
    }
  };

  const saveMessage = () => {
    if (knowledgeStore.selectedNode) {
      knowledgeStore.selectedNode.editable = false;
      EventBus.emit('update_node', knowledgeStore.selectedNode);
    }
  };

  const analysis = () => {
    if (!knowledgeStore.selectedNode) {
      return;
    }

    setLoading(true);

    analyzeGraphNode(
      knowledgeStore.selectedNode.elementId,
      knowledgeStore.currentLlm ? knowledgeStore.currentLlm : '',
      knowledgeStore.currentEmbedding ? knowledgeStore.currentEmbedding : '',
      knowledgeStore.maxTokensEachChunk
    )
      .then((response) => {
        const { data } = response;
        if (data && knowledgeStore.selectedNode) {
          knowledgeStore.selectedNode.title = data.title;
          knowledgeStore.selectedNode.titleVector = data.titleVector;
          knowledgeStore.selectedNode.content = data.content;
          knowledgeStore.selectedNode.contentVector = data.contentVector;
          knowledgeStore.selectedNode.entities = data.entities;
          knowledgeStore.selectedNode.keywords = data.keywords;
          knowledgeStore.selectedNode.tags = data.tags;
          knowledgeStore.selectedNode.documents = data.documents;
          knowledgeStore.selectedNode.webpages = data.webpages;
          knowledgeStore.selectedNode.createdAt = formatTimestamp(
            data.createdAt
          );
          knowledgeStore.selectedNode.updatedAt = formatTimestamp(
            data.updatedAt
          );
        }
      })
      .catch((error) => {
        Message.error(error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const generateQuestion = () => {
    if (!knowledgeStore.selectedNode) {
      return;
    }

    setLoading(true);

    generateGraphQuestions(
      knowledgeStore.selectedNode.libId,
      knowledgeStore.selectedNode.subjectId,
      knowledgeStore.selectedNode.elementId,
      knowledgeStore.currentLlm ? knowledgeStore.currentLlm : ''
    )
      .then((response) => {
        EventBus.emit('ganerate_graph_questions', response.data);
      })
      .catch((error) => {
        Message.error(error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const generateAnswer = () => {
    if (!knowledgeStore.selectedNode) {
      return;
    }

    setLoading(true);

    generateGraphAnswer(
      knowledgeStore.selectedNode.libId,
      knowledgeStore.selectedNode.subjectId,
      knowledgeStore.selectedNode.elementId,
      knowledgeStore.currentLlm ? knowledgeStore.currentLlm : ''
    )
      .then((data) => {
        EventBus.emit('ganerate_graph_answer', data);
      })
      .catch((error) => {
        Message.error(error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const fetchNodeDetail = async (elementId: string) => {
    setLoading(true);
    queryNodeDetail(elementId)
      .then((response) => {
        const { data } = response;
        if (knowledgeStore.selectedNode && data) {
          knowledgeStore.selectedNode.title = data.title;
          knowledgeStore.selectedNode.titleVector = data.titleVector;
          knowledgeStore.selectedNode.content = data.content;
          knowledgeStore.selectedNode.contentVector = data.contentVector;
          knowledgeStore.selectedNode.entities = data.entities;
          knowledgeStore.selectedNode.keywords = data.keywords;
          knowledgeStore.selectedNode.tags = data.tags;
          knowledgeStore.selectedNode.documents = data.documents;
          knowledgeStore.selectedNode.webpages = data.webpages;
          knowledgeStore.selectedNode.createdAt = formatTimestamp(
            data.createdAt
          );
          knowledgeStore.selectedNode.updatedAt = formatTimestamp(
            data.updatedAt
          );
        }
      })
      .finally(() => {
        setLoading(false);
      });
  };

  onMounted(() => {
    EventBus.on('graphSelected', () => {
      if (
        knowledgeStore.selectedNode &&
        knowledgeStore.selectedNode.elementId
      ) {
        fetchNodeDetail(knowledgeStore.selectedNode.elementId);
      }
    });
  });
</script>

<style scoped lang="less">
  :deep(.arco-descriptions-item-label) {
    padding-right: 6px;
  }
</style>
