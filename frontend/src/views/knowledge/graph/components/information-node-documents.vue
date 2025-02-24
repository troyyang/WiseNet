<template>
  <a-typography-text
    v-if="
      knowledgeStore.selectedNode &&
      knowledgeStore.selectedNode.documents &&
      knowledgeStore.selectedNode.documents.length > 0
    "
  >
    <a-typography-text>
      <a-collapse
        v-for="document in knowledgeStore.selectedNode.documents"
        :key="document.elementId"
        :bordered="false"
        @change="getDocumentDetail(document.elementId)"
      >
        <a-collapse-item
          :key="document.elementId"
          :header="
            document.name.length > 20
              ? document.name.substring(0, 20) + '...'
              : document.name
          "
          :title="document.name"
        >
          <template #extra>
            <a-button
              type="secondary"
              size="mini"
              :title="t('knowledge.graph.analysis')"
              @click.stop="analyzeDocument(document.elementId)"
            >
              <template #icon>
                <icon-computer v-if="!document.analyzing" />
                <icon-loading v-else />
              </template>
            </a-button>
            <a-button
              type="secondary"
              size="mini"
              :title="t('knowledge.operation.download')"
              @click.stop="openDocument(document.savedAt)"
            >
              <template #icon>
                <icon-download />
              </template>
            </a-button>
            <a-button
              type="secondary"
              size="mini"
              :title="t('knowledge.operation.delete')"
              @click.stop="deleteDocument(document.elementId)"
            >
              <template #icon>
                <icon-delete />
              </template>
            </a-button>
          </template>
          <InformationNodeDocumentTabs
            :title="document.title"
            :content="document.content"
            :title-vector="document.titleVector"
            :content-vector="document.contentVector"
            :pages="document.pages"
          />
        </a-collapse-item>
      </a-collapse>
    </a-typography-text>
  </a-typography-text>
</template>

<script lang="ts" setup>
  import { useI18n } from 'vue-i18n';
  import { defineAsyncComponent } from 'vue';
  import {
    deleteGraphNodeDocument,
    getDownloadUrl,
    analyzeGraphNodeDocument,
    getGraphNodeDocument,
  } from '@/api/graph';
  import { useKnowledgeStore } from '@/store';

  const InformationNodeDocumentTabs = defineAsyncComponent(
    () => import('./information-node-document-tabs.vue')
  );

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();

  const openDocument = (savedAt: string) => {
    window.open(getDownloadUrl(savedAt), '_blank');
  };

  const analyzeDocument = (docmentElementId: string) => {
    let isAnalyzing = false;
    if (knowledgeStore.selectedNode && knowledgeStore.selectedNode.documents) {
      isAnalyzing = knowledgeStore.selectedNode.documents.some(
        (document) =>
          document.elementId === docmentElementId && document.analyzing
      );
    }
    if (isAnalyzing) {
      return;
    }
    if (knowledgeStore.selectedNode && knowledgeStore.selectedNode.documents) {
      knowledgeStore.selectedNode.documents.forEach((document) => {
        if (document.elementId === docmentElementId) {
          document.analyzing = true;
        }
      });
      analyzeGraphNodeDocument(
        docmentElementId,
        knowledgeStore.currentLlm ? knowledgeStore.currentLlm : null,
        knowledgeStore.currentEmbedding
          ? knowledgeStore.currentEmbedding
          : null,
        knowledgeStore.maxTokensEachChunk
      )
        .then((response) => {
          const { data } = response;
          if (
            data &&
            knowledgeStore.selectedNode &&
            knowledgeStore.selectedNode.documents
          ) {
            knowledgeStore.selectedNode.documents.forEach((document) => {
              if (document.elementId === docmentElementId) {
                document.title = data.title;
                document.titleVector = data.titleVector;
                document.content = data.content;
                document.contentVector = data.contentVector;
                document.pages = data.pages;
                document.analyzing = false;
                document.loaded = true;
              }
            });
          }
        })
        .finally(() => {
          if (
            knowledgeStore.selectedNode &&
            knowledgeStore.selectedNode.documents
          ) {
            knowledgeStore.selectedNode.documents.forEach((document) => {
              if (document.elementId === docmentElementId) {
                document.analyzing = false;
              }
            });
          }
        });
    }
  };

  const getDocumentDetail = (docmentElementId: string) => {
    let documentLoaded = false;
    if (knowledgeStore.selectedNode && knowledgeStore.selectedNode.documents) {
      documentLoaded = knowledgeStore.selectedNode.documents.some(
        (document) => document.elementId === docmentElementId && document.loaded
      );
    }
    if (documentLoaded) {
      return;
    }
    getGraphNodeDocument(docmentElementId).then((response) => {
      const { data } = response;
      if (
        data &&
        knowledgeStore.selectedNode &&
        knowledgeStore.selectedNode.documents
      ) {
        knowledgeStore.selectedNode.documents.forEach((document) => {
          if (document.elementId === docmentElementId) {
            document.title = data.title;
            document.titleVector = data.titleVector;
            document.content = data.content;
            document.contentVector = data.contentVector;
            document.pages = data.pages;
            document.analyzing = false;
            document.loaded = true;
          }
        });
      }
    });
  };

  const deleteDocument = (elementId: string) => {
    deleteGraphNodeDocument(elementId).then((response) => {
      const { data } = response;
      if (
        data &&
        data.success &&
        knowledgeStore.selectedNode &&
        knowledgeStore.selectedNode.documents
      ) {
        if (knowledgeStore.selectedNode) {
          knowledgeStore.selectedNode.documents =
            knowledgeStore.selectedNode.documents.filter(
              (document) => document.elementId !== elementId
            );
        }
      }
    });
  };
</script>

<style scoped lang="less">
  :deep(.arco-descriptions-item-label) {
    padding-right: 6px;
  }

  .vector-basic {
    padding: 10px;
    width: 200px;
    background-color: var(--color-bg-popup);
    border-radius: 4px;
    box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.15);
  }

  .doc-content {
    height: 300px;
  }
</style>
