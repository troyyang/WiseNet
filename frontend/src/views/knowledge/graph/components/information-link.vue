<template>
  <a-spin :loading="loading" style="width: 100%">
    <a-space
      v-if="
        knowledgeStore.selectedRelationship &&
        !knowledgeStore.selectedRelationship.editable
      "
      direction="vertical"
      :size="4"
    >
      <a-typography-title :heading="5">
        {{ knowledgeStore.selectedRelationship.type }}
      </a-typography-title>
      <a-typography-text :copyable="true">
        <a-typography-text bold>
          {{ t('knowledge.information.element.id') }}:
        </a-typography-text>
        <a-typography-text>{{
          knowledgeStore.selectedRelationship.elementId
        }}</a-typography-text>
      </a-typography-text>
      <a-typography-text :copyable="true">
        <a-typography-text bold> ID: </a-typography-text>
        <a-typography-text>{{
          knowledgeStore.selectedRelationship.id
        }}</a-typography-text>
      </a-typography-text>
      <a-typography-text :copyable="true">
        <a-typography-text bold>
          {{ t('knowledge.information.source.id') }}:
        </a-typography-text>
        <a-typography-text>{{
          knowledgeStore.selectedRelationship.source.id
        }}</a-typography-text>
      </a-typography-text>
      <a-typography-text :copyable="true">
        <a-typography-text bold>
          {{ t('knowledge.information.target.id') }}:
        </a-typography-text>
        <a-typography-text>{{
          knowledgeStore.selectedRelationship.target.id
        }}</a-typography-text>
      </a-typography-text>
      <a-typography-text :copyable="true">
        <a-typography-text bold>
          {{ t('knowledge.information.source.element.id') }}:
        </a-typography-text>
        <a-typography-text>{{
          knowledgeStore.selectedRelationship.source.elementId
        }}</a-typography-text>
      </a-typography-text>
      <a-typography-text :copyable="true">
        <a-typography-text bold>
          {{ t('knowledge.information.target.element.id') }}:
        </a-typography-text>
        <a-typography-text>{{
          knowledgeStore.selectedRelationship.target.elementId
        }}</a-typography-text>
      </a-typography-text>
      <a-typography-text :copyable="true">
        <a-typography-text bold>
          {{ t('knowledge.information.lib.id') }}:
        </a-typography-text>
        <a-typography-text>{{
          knowledgeStore.selectedRelationship.libId
        }}</a-typography-text>
      </a-typography-text>
      <a-typography-text :copyable="true">
        <a-typography-text bold>
          {{ t('knowledge.information.subject.id') }}:
        </a-typography-text>
        <a-typography-text>{{
          knowledgeStore.selectedRelationship.subjectId
        }}</a-typography-text>
      </a-typography-text>
      <a-typography-text :copyable="true">
        <a-typography-text bold>
          {{ t('knowledge.information.content') }}:
        </a-typography-text>
        <a-typography-text
          :ellipsis="{
            rows: 3,
            expandable: true,
            showTooltip: true,
          }"
        >
          {{ knowledgeStore.selectedRelationship.content }}
        </a-typography-text>
        <InformationVectorPiece
          :vector="knowledgeStore.selectedRelationship.contentVector"
        />
      </a-typography-text>
    </a-space>
    <a-space
      v-if="
        knowledgeStore.selectedRelationship &&
        knowledgeStore.selectedRelationship.editable
      "
      direction="vertical"
      :size="8"
      style="width: 100%"
    >
      <div style="display: flex; flex-direction: column; width: 100%">
        <a-textarea
          v-model="knowledgeStore.selectedRelationship.content"
          :placeholder="
            t('knowledge.graph.information.link.content.placeholder')
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
        <a-button type="primary" style="width: 100px" @click="saveLink">{{
          t('knowledge.operation.submit')
        }}</a-button>
      </a-space>
    </a-space>
  </a-spin>
</template>

<script lang="ts" setup>
  import { onMounted, defineAsyncComponent } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { queryRelationshipDetail } from '@/api/graph';
  import EventBus from '@/utils/event-bus';
  import { useKnowledgeStore } from '@/store';
  import useLoading from '@/hooks/loading';

  const InformationVectorPiece = defineAsyncComponent(
    () => import('./information-vector-piece.vue')
  );

  const { t } = useI18n();
  const { loading, setLoading } = useLoading(false);

  const knowledgeStore = useKnowledgeStore();

  const cancelEdit = () => {
    if (knowledgeStore.selectedRelationship) {
      knowledgeStore.selectedRelationship.editable = false;
    }
  };

  const saveLink = () => {
    if (!knowledgeStore.selectedRelationship) {
      return;
    }

    knowledgeStore.selectedRelationship.editable = false;
    EventBus.emit('update_link', knowledgeStore.selectedRelationship);
  };

  const fetchRelationshipDetail = async (elementId: string) => {
    const response = await queryRelationshipDetail(elementId);
    return response.data;
  };

  onMounted(() => {
    EventBus.on('graphSelected', () => {
      if (
        knowledgeStore.selectedRelationship &&
        knowledgeStore.selectedRelationship.elementId
      ) {
        fetchRelationshipDetail(knowledgeStore.selectedRelationship.elementId)
          .then((data) => {
            if (
              knowledgeStore.selectedRelationship &&
              data &&
              knowledgeStore.selectedRelationship.elementId === data.elementId
            ) {
              knowledgeStore.selectedRelationship.content = data.content;
              knowledgeStore.selectedRelationship.contentVector =
                data.contentVector;
            }
          })
          .finally(() => {
            setLoading(false);
          });
      }
    });
  });
</script>

<style scoped lang="less">
  .vector-basic {
    padding: 10px;
    width: 200px;
    background-color: var(--color-bg-popup);
    border-radius: 4px;
    box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.15);
  }
</style>
