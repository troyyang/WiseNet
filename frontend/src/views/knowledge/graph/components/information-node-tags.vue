<template>
  <a-typography-text
    v-if="
      knowledgeStore.selectedNode?.tags &&
      knowledgeStore.selectedNode?.tags.length > 0
    "
    :copyable="true"
  >
    <a-typography-title :heading="6">
      {{ t('knowledge.information.tags') }}
    </a-typography-title>
    <a-typography-text>
      <ol>
        <li
          v-for="tag in knowledgeStore.selectedNode?.tags"
          :key="tag.elementId"
        >
          {{ tag.content }}
          <InformationVectorPiece :vector="tag.contentVector" />
          <a-space>
            <a-button
              type="secondary"
              size="mini"
              @click="
                deleteTag(tag.elementId, knowledgeStore.selectedNode?.elementId)
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
  import { deleteGraphNodeTag } from '@/api/graph';
  import { useKnowledgeStore } from '@/store';

  const InformationVectorPiece = defineAsyncComponent(
    () => import('./information-vector-piece.vue')
  );

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();

  const deleteTag = (elementId: string, nodeElementId: string) => {
    deleteGraphNodeTag(elementId, nodeElementId).then((response) => {
      const { data } = response;
      if (
        data &&
        data.success &&
        knowledgeStore.selectedNode &&
        knowledgeStore.selectedNode.tags
      ) {
        knowledgeStore.selectedNode.tags =
          knowledgeStore.selectedNode.tags.filter(
            (tag) => tag.elementId !== elementId
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
