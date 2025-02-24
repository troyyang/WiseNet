<template>
  <a-tabs size="mini">
    <a-tab-pane
      key="1"
      :title="t('knowledge.information.summary')"
      class="doc-content"
    >
      <a-typography-paragraph
        :copyable="true"
        :ellipsis="{
          rows: 2,
        }"
        bold
      >
        {{ title }}
      </a-typography-paragraph>
      <InformationVectorPiece :vector="titleVector" />
      <a-divider dashed />
      <a-typography-paragraph
        :copyable="true"
        :ellipsis="{
          rows: 6,
        }"
      >
        {{ content }}
      </a-typography-paragraph>
      <InformationVectorPiece :vector="contentVector" />
    </a-tab-pane>
    <a-tab-pane :title="t('knowledge.information.chunks')">
      <InformationNodeDocumentPage :pages="pages" />
    </a-tab-pane>
  </a-tabs>
</template>

<script lang="ts" setup>
  import { PropType, defineAsyncComponent } from 'vue';
  import { DocumentPageRecord } from '@/api/graph';
  import { useI18n } from 'vue-i18n';

  const InformationNodeDocumentPage = defineAsyncComponent(
    () => import('./information-node-document-page.vue')
  );
  const InformationVectorPiece = defineAsyncComponent(
    () => import('./information-vector-piece.vue')
  );

  const { t } = useI18n();

  defineProps({
    title: {
      type: String,
      default: '',
    },
    content: {
      type: String,
      default: '',
    },
    titleVector: {
      type: Array as PropType<number[]>,
      default: () => [],
    },
    contentVector: {
      type: Array as PropType<number[]>,
      default: () => [],
    },
    pages: {
      type: Array as PropType<DocumentPageRecord[]>,
      default() {
        return [];
      },
    },
  });
</script>
