<template>
  <a-typography-text
    v-if="
      knowledgeStore.selectedNode?.webpages &&
      knowledgeStore.selectedNode?.webpages.length > 0
    "
  >
    <a-typography-text>
      <a-collapse
        v-for="webpage in knowledgeStore.selectedNode?.webpages"
        :key="webpage.elementId"
        :bordered="false"
        @change="getWebpageDetail(webpage.elementId)"
      >
        <a-collapse-item
          :key="webpage.url"
          :header="
            webpage.url.length > 20
              ? webpage.url.substring(0, 20) + '...'
              : webpage.url
          "
          :title="webpage.url"
        >
          <template #extra>
            <a-button
              type="secondary"
              size="mini"
              :title="t('knowledge.graph.analysis')"
              @click.stop="analyzeWebpage(webpage.elementId)"
            >
              <template #icon>
                <icon-computer v-if="!webpage.analyzing" />
                <icon-loading v-else />
              </template>
            </a-button>
            <a-button
              type="secondary"
              size="mini"
              :title="t('knowledge.operation.open')"
              @click.stop="openWebpage(webpage.url)"
            >
              <template #icon>
                <icon-desktop />
              </template>
            </a-button>
            <a-button
              type="secondary"
              size="mini"
              :title="t('knowledge.operation.delete')"
              @click.stop="deleteWebpage(webpage.elementId)"
            >
              <template #icon>
                <icon-delete />
              </template>
            </a-button>
          </template>
          <InformationNodeDocumentTabs
            :title="webpage.title"
            :content="webpage.content"
            :title-vector="webpage.titleVector"
            :content-vector="webpage.contentVector"
            :pages="webpage.pages"
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
    deleteGraphNodeWebpage,
    analyzeGraphNodeWebpage,
    getGraphNodeWebpageDetail,
  } from '@/api/graph';
  import { useKnowledgeStore } from '@/store';
  import { openWindow } from '@/utils';

  const InformationNodeDocumentTabs = defineAsyncComponent(
    () => import('./information-node-document-tabs.vue')
  );

  const { t } = useI18n();

  const knowledgeStore = useKnowledgeStore();

  const openWebpage = (url: string) => {
    openWindow(url, { target: '_blank' });
  };

  const analyzeWebpage = (webpageElementId: string) => {
    let isAnalyzing = false;
    if (knowledgeStore.selectedNode && knowledgeStore.selectedNode.webpages) {
      isAnalyzing = knowledgeStore.selectedNode.webpages.some(
        (webpage) => webpage.elementId === webpageElementId && webpage.analyzing
      );
    }
    if (isAnalyzing) {
      return;
    }
    if (knowledgeStore.selectedNode && knowledgeStore.selectedNode.webpages) {
      knowledgeStore.selectedNode.webpages.forEach((webpage) => {
        if (webpage.elementId === webpageElementId) {
          webpage.analyzing = true;
        }
      });
      analyzeGraphNodeWebpage(
        webpageElementId,
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
            knowledgeStore.selectedNode.webpages
          ) {
            knowledgeStore.selectedNode.webpages.forEach((webpage) => {
              if (webpage.elementId === webpageElementId) {
                webpage.title = data.title;
                webpage.titleVector = data.titleVector;
                webpage.content = data.content;
                webpage.contentVector = data.contentVector;
                webpage.pages = data.pages;
                webpage.analyzing = false;
              }
            });
          }
        })
        .catch(() => {
          if (
            knowledgeStore.selectedNode &&
            knowledgeStore.selectedNode.webpages
          ) {
            knowledgeStore.selectedNode.webpages.forEach((webpage) => {
              if (webpage.elementId === webpageElementId) {
                webpage.analyzing = false;
              }
            });
          }
        });
    }
  };

  const getWebpageDetail = (webpageElementId: string) => {
    let webpageLoaded = false;
    if (knowledgeStore.selectedNode && knowledgeStore.selectedNode.webpages) {
      webpageLoaded = knowledgeStore.selectedNode.webpages.some(
        (webpage) => webpage.elementId === webpageElementId && webpage.loaded
      );
    }
    if (webpageLoaded) {
      return;
    }
    getGraphNodeWebpageDetail(webpageElementId).then((response) => {
      const { data } = response;
      if (
        data &&
        knowledgeStore.selectedNode &&
        knowledgeStore.selectedNode.webpages
      ) {
        knowledgeStore.selectedNode.webpages.forEach((webpage) => {
          if (webpage.elementId === webpageElementId) {
            webpage.title = data.title;
            webpage.titleVector = data.titleVector;
            webpage.content = data.content;
            webpage.contentVector = data.contentVector;
            webpage.pages = data.pages;
            webpage.analyzing = false;
            webpage.loaded = true;
          }
        });
      }
    });
  };

  const deleteWebpage = (elementId: string) => {
    deleteGraphNodeWebpage(elementId).then((response) => {
      const { data } = response;
      if (
        data &&
        data.success &&
        knowledgeStore.selectedNode &&
        knowledgeStore.selectedNode.webpages
      ) {
        knowledgeStore.selectedNode.webpages =
          knowledgeStore.selectedNode.webpages.filter(
            (webpage) => webpage.elementId !== elementId
          );
      }
    });
  };
</script>
