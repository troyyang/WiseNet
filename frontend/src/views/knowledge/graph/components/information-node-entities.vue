<template>
  <a-typography
    v-if="
      knowledgeStore.selectedNode?.entities &&
      knowledgeStore.selectedNode?.entities.length > 0
    "
    :copyable="true"
  >
    <a-typography-title :heading="6">
      {{ t('knowledge.information.entities') }}
    </a-typography-title>
    <a-typography-text>
      <ol>
        <li
          v-for="entity in knowledgeStore.selectedNode?.entities"
          :key="entity.elementId"
        >
          {{ entity.content }}
          <a-space>
            <InformationVectorPiece :vector="entity.contentVector" />
            <a-button
              type="secondary"
              size="mini"
              @click="
                deleteEntity(
                  entity.elementId,
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
  </a-typography>
</template>

<script lang="ts" setup>
  import { useI18n } from 'vue-i18n';
  import { defineAsyncComponent } from 'vue';
  import { deleteGraphNodeEntity } from '@/api/graph';
  import { useKnowledgeStore } from '@/store';

  const InformationVectorPiece = defineAsyncComponent(
    () => import('./information-vector-piece.vue')
  );

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();

  const deleteEntity = (elementId: string, nodeElementId: string) => {
    deleteGraphNodeEntity(elementId, nodeElementId).then((response) => {
      const { data } = response;
      if (
        data &&
        data.success &&
        knowledgeStore.selectedNode &&
        knowledgeStore.selectedNode.entities
      ) {
        knowledgeStore.selectedNode.entities =
          knowledgeStore.selectedNode.entities.filter(
            (entity) => entity.elementId !== elementId
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
