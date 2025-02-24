<template>
  <a-typography-text
    v-if="
      knowledgeStore.selectedNode?.keywords &&
      knowledgeStore.selectedNode?.keywords.length > 0
    "
    :copyable="true"
  >
    <a-typography-title :heading="6">
      {{ t('knowledge.information.keywords') }}
    </a-typography-title>
    <a-typography-text>
      <ol>
        <li
          v-for="keyword in knowledgeStore.selectedNode?.keywords"
          :key="keyword?.elementId"
        >
          {{ keyword?.content }}
          <a-space>
            <InformationVectorPiece :vector="keyword?.contentVector" />
            <a-button
              type="secondary"
              size="mini"
              @click="
                deleteKeyword(
                  keyword?.elementId,
                  knowledgeStore.selectedNode?.elementId
                )
              "
            >
              <template #icon>
                <icon-delete />
              </template>
            </a-button>
          </a-space>
        </li>
      </ol>
    </a-typography-text>
  </a-typography-text>
</template>

<script lang="ts" setup>
  import { useI18n } from 'vue-i18n';
  import { defineAsyncComponent } from 'vue';
  import { deleteGraphNodeKeyword } from '@/api/graph';
  import { useKnowledgeStore } from '@/store';

  const InformationVectorPiece = defineAsyncComponent(
    () => import('./information-vector-piece.vue')
  );

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();

  const deleteKeyword = (elementId: string, nodeElementId: string) => {
    deleteGraphNodeKeyword(elementId, nodeElementId).then((response) => {
      const { data } = response;
      if (
        data &&
        data.success &&
        knowledgeStore.selectedNode &&
        knowledgeStore.selectedNode.keywords
      ) {
        knowledgeStore.selectedNode.keywords =
          knowledgeStore.selectedNode.keywords.filter(
            (keyword) => keyword.elementId !== elementId
          );
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
</style>
