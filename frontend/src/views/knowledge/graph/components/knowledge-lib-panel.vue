<template>
  <a-card
    class="general-card knowledge-lib-panel"
    :title="t('knowledge.title.knowledgeLibPanel')"
    :bordered="false"
    :header-style="{ paddingBottom: '0' }"
    :body-style="{
      height: '100%',
      paddingTop: '16px',
      display: 'flex',
      flexFlow: 'column',
    }"
  >
    <a-space :size="8">
      <a-input-search
        v-model="keyword"
        :placeholder="t('knowledge.lib.placeholder.search')"
        @press-enter="fetchData"
        @search="fetchData"
      />
      <a-button @click="createLib">
        <template #icon>
          <icon-plus-circle-fill />
        </template>
        {{ t('knowledge.operation.create') }}
      </a-button>
    </a-space>
    <div class="knowledge-lib-panel-content">
      <a-spin :loading="loading" style="width: 100%">
        <KnowledgeLibList :render-list="knowledgeLibData" />
      </a-spin>
    </div>
  </a-card>
</template>

<script lang="ts" setup>
  import { onMounted, ref } from 'vue';
  import { useI18n } from 'vue-i18n';
  import EventBus from '@/utils/event-bus';
  import {
    queryKnowledgeLibList,
    KnowledgeLibRecord,
    createKnowledgeLib,
    updateKnowledgeLib,
    deleteKnowledgeLib,
    publishKnowledgeLib,
  } from '@/api/knowledge';
  import useLoading from '@/hooks/loading';
  import KnowledgeLibList from './knowledge-lib-list.vue';

  const { t } = useI18n();
  const { loading, setLoading } = useLoading(true);
  const knowledgeLibData = ref<KnowledgeLibRecord[]>([]);
  const keyword = ref('');

  interface ItemData {
    rowIndex: number;
    title?: string;
  }

  const saveLib = async (itemData: ItemData) => {
    setLoading(true);
    const lib = knowledgeLibData.value[itemData.rowIndex];
    if (!lib) return;
    lib.title = itemData.title ?? '';
    if (!lib.id) {
      const response = await createKnowledgeLib(lib);
      if (!response) return;
      const { data } = response;
      if (data) {
        knowledgeLibData.value[itemData.rowIndex] = data;
        EventBus.emit('knowledgeLibSelected', { rowIndex: 0, ...knowledgeLibData.value[0] });
      }
    } else {
      const response = await updateKnowledgeLib(lib);
      if (!response) return;
      const { data } = response;
      if (data) {
        knowledgeLibData.value.splice(itemData.rowIndex, 1);
        knowledgeLibData.value.push(data);
      }
    }
    setLoading(false);
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      const condition = {
        keyword: keyword.value,
      };
      const response = await queryKnowledgeLibList(condition);
      const { data } = response;
      knowledgeLibData.value = data;
      if (data.length > 0) {
        EventBus.emit('knowledgeLibSelected', { rowIndex: 0, ...data[0] });
      }
      setLoading(false);
    } catch (err) {
      // you can report use errorHandler or other
    } finally {
      setLoading(false);
    }
  };

  const createLib = () => {
    if (knowledgeLibData.value.length === 0 || knowledgeLibData.value[0].id) {
      knowledgeLibData.value.unshift({
        title: '',
        editable: true,
      } as KnowledgeLibRecord);
    }
  };

  const deleteLib = async (itemData: ItemData) => {
    setLoading(true);
    const lib = knowledgeLibData.value[itemData.rowIndex];
    if (!lib.id) {
      knowledgeLibData.value.splice(itemData.rowIndex, 1);
      setLoading(false);
      return;
    }

    const response = await deleteKnowledgeLib(lib.id);
    if (!response) return;
    const { data } = response;
    if (data && data.success) {
      knowledgeLibData.value.splice(itemData.rowIndex, 1);
      EventBus.emit('knowledgeLibSelected', {});
    }
    setLoading(false);
  };

  const publishLib = async (itemData: ItemData) => {
    setLoading(true);
    const lib = knowledgeLibData.value[itemData.rowIndex];
    if (!lib?.id) {
      setLoading(false);
      return;
    }

    const response = await publishKnowledgeLib(lib.id);
    if (!response) {
      setLoading(false);
      return;
    }
    const { data } = response;
    if (data) {
      knowledgeLibData.value[itemData.rowIndex] = data;
    }
    setLoading(false);
  };

  onMounted(() => {
    fetchData();

    EventBus.off('save_lib');
    EventBus.on('save_lib', async (event: unknown) => {
      const itemData = event as ItemData;
      saveLib(itemData);
    });

    EventBus.off('delete_lib');
    EventBus.on('delete_lib', async (event: unknown) => {
      const itemData = event as ItemData;
      deleteLib(itemData);
    });

    EventBus.off('publish_lib');
    EventBus.on('publish_lib', async (event: unknown) => {
      const itemData = event as ItemData;
      publishLib(itemData);
    });

    EventBus.on('knowledgeLibSelected', (event: unknown) => {
      const itemData = event as ItemData;
      knowledgeLibData.value.forEach((item, index) => {
        if (index !== itemData.rowIndex) {
          item.selected = false;
        } else {
          item.selected = true;
        }
      });
    });
  });
</script>

<style scoped lang="less">
  .knowledge-lib-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    // padding: 20px;
    background-color: var(--color-bg-2);

    &-content {
      flex: 1;
      margin: 20px 0;
    }
  }
</style>
