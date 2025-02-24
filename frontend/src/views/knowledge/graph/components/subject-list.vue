<template>
  <a-spin :loading="loading" style="width: 100%">
    <div>
      <a-table
        ref="subjectTableRef"
        :columns="columns"
        :data="knowledgeSubjectList"
        row-key="id"
        :row-selection="{
          type: 'checkbox',
          showCheckedAll: true,
        }"
        :border="false"
        :pagination="false"
        :bordered="{ cell: true }"
        column-resizable
        @selection-change="handleSelectionChange"
      >
        <template #name="{ rowIndex }">
          <a-input
            v-if="knowledgeSubjectList[rowIndex].editable"
            v-model="knowledgeSubjectList[rowIndex].name"
            :placeholder="
              knowledgeSubjectList[rowIndex].editError ||
              t('knowledge.subject.name')
            "
            :max-length="200"
            :error="!!knowledgeSubjectList[rowIndex].editError"
            @press-enter="submitEdit(rowIndex)"
          >
            <template #append>
              <a-button
                type="secondary"
                :title="t('knowledge.operation.submit')"
                @click="submitEdit(rowIndex)"
              >
                <template #icon>
                  <icon-save />
                </template>
              </a-button>
              <a-button
                type="secondary"
                :title="t('knowledge.operation.cancel')"
                style="margin-left: 2px"
                @click="cancelEdit(rowIndex)"
              >
                <template #icon>
                  <icon-close />
                </template>
              </a-button>
            </template>
          </a-input>
          <span v-else>{{ knowledgeSubjectList[rowIndex].name }}</span>
        </template>
        <template #operation="{ rowIndex }">
          <a-button
            type="secondary"
            :title="t('knowledge.operation.edit')"
            @click="edit(rowIndex)"
          >
            <template #icon>
              <icon-edit />
            </template>
          </a-button>
          <a-button
            type="secondary"
            style="margin-left: 2px"
            :title="t('knowledge.operation.delete')"
            @click="deleteItem(rowIndex)"
          >
            <template #icon>
              <icon-delete />
            </template>
          </a-button>
        </template>
      </a-table>
    </div>
  </a-spin>
</template>

<script lang="ts" setup>
  import { computed, h, compile, onMounted, watch, ref } from 'vue';
  import EventBus from '@/utils/event-bus';
  import { useI18n } from 'vue-i18n';
  import { Message, Table } from '@arco-design/web-vue';
  import type {
    TableColumnData,
    TableData,
  } from '@arco-design/web-vue/es/table/interface.d';
  import {
    KnowledgeLibRecord,
    KnowledgeSubjectRecord,
    queryKnowledgeSubjectList,
    deleteSubject,
    createSubject,
    updateSubject,
  } from '@/api/knowledge';
  import {
    generateGraph,
    analyzeGraph,
    cancelGenerateGraph,
  } from '@/api/graph';
  import useLoading from '@/hooks/loading';
  import { useKnowledgeStore } from '@/store';

  const { loading, setLoading } = useLoading(true);
  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();

  const knowledgeSubjectList = ref<KnowledgeSubjectRecord[]>([]);
  const knowledgeLibID = ref<number | null>(null);
  const selectedSubjectIDs = ref<number[] | null>(null);
  const subjectTableRef = ref<InstanceType<typeof Table> | null>(null);

  watch(selectedSubjectIDs, () => {
    EventBus.emit('knowledgeSubjectSelecteChange', {
      libId: knowledgeLibID.value,
      subjectIDs: selectedSubjectIDs.value,
    });
  });
  const edit = (rowIndex: number) => {
    knowledgeSubjectList.value[rowIndex].editable = true;
  };

  const cancelEdit = (rowIndex: number) => {
    knowledgeSubjectList.value[rowIndex].editable = false;
    if (!knowledgeSubjectList.value[rowIndex].id) {
      knowledgeSubjectList.value.splice(rowIndex, 1);
    }
  };

  const submitEdit = async (rowIndex: number) => {
    if (knowledgeSubjectList.value[rowIndex].name === '') {
      knowledgeSubjectList.value[rowIndex].editError = t(
        'knowledge.subject.name.error'
      );
      return;
    }

    knowledgeSubjectList.value[rowIndex].editable = false;
    knowledgeSubjectList.value[rowIndex].editError = '';

    if (!knowledgeSubjectList.value[rowIndex].id) {
      const response = await createSubject({
        name: knowledgeSubjectList.value[rowIndex].name,
        knowledgeLibId: knowledgeLibID.value,
      } as KnowledgeSubjectRecord);
      if (!response) return;
      const { data } = response;

      if (data && data.id) {
        knowledgeSubjectList.value[rowIndex] = data;
      }
    } else {
      const response = await updateSubject(
        knowledgeSubjectList.value[rowIndex]
      );
      if (!response) return;
      const { data } = response;
      if (data) {
        knowledgeSubjectList.value[rowIndex] = data;
      }
    }
  };

  const deleteItem = async (rowIndex: number) => {
    if (!knowledgeSubjectList.value[rowIndex].id) {
      knowledgeSubjectList.value.splice(rowIndex, 1);
      return;
    }

    const response = await deleteSubject(
      knowledgeSubjectList.value[rowIndex].id
    );
    if (!response) return;
    const { data } = response;
    if (data && data.success) {
      if (selectedSubjectIDs.value && selectedSubjectIDs.value.length > 0) {
        selectedSubjectIDs.value = selectedSubjectIDs.value.filter(
          (item) => item !== knowledgeSubjectList.value[rowIndex].id
        );
      }
      knowledgeSubjectList.value.splice(rowIndex, 1);
    }
  };

  // Using the Render function is more flexible than using templates.
  // But, cannot bind context and local scopes are also lost

  const columns = computed(() => {
    return [
      {
        title: t('knowledge.list.title.order'),
        width: 80,
        render({
          rowIndex,
        }: {
          record: TableData;
          column: TableColumnData;
          rowIndex: number;
        }) {
          const tmp = `<span>${rowIndex + 1}</span>`;
          return h(compile(tmp));
        },
      },
      {
        title: t('knowledge.subject.name'),
        dataIndex: 'name',
        slotName: 'name',
      },
      {
        title: t('knowledge.operation'),
        slotName: 'operation',
        width: 100,
      },
    ];
  });

  const handleSelectionChange = (keys: (string | number)[]) => {
    const validIds = keys
      .map((key) => Number(key))
      .filter((id) => knowledgeSubjectList.value.some((subject) => subject.id === id));
    selectedSubjectIDs.value = validIds;
  };

  const fetchData = async () => {
    try {
      if (!knowledgeLibID.value) {
        knowledgeSubjectList.value = [];
        return;
      }

      setLoading(true);
      const response = await queryKnowledgeSubjectList(knowledgeLibID.value);
      if (!response) return;
      const { data } = response;
      knowledgeSubjectList.value = data;
      selectedSubjectIDs.value = null;
      if (knowledgeSubjectList.value.length > 0 && !selectedSubjectIDs.value) {
        if (subjectTableRef.value) {
          subjectTableRef.value.selectAll(false);
          if (knowledgeSubjectList.value[0].id) {
            subjectTableRef.value.select(
              knowledgeSubjectList.value[0].id,
              true
            );
          }
        }
      }

      setLoading(false);
    } catch (err) {
      // you can report use errorHandler or other
    } finally {
      setLoading(false);
    }
  };

  const startRefreshGraph = () => {
    EventBus.emit('refresh_graph');
  };

  onMounted(() => {
    EventBus.on('knowledgeLibSelected', async (itemData) => {
      knowledgeLibID.value = (itemData as KnowledgeLibRecord).id;
      fetchData();
    });

    EventBus.off('generate_graph');
    EventBus.on('generate_graph', async (payload: unknown) => {
      if (!selectedSubjectIDs.value || selectedSubjectIDs.value.length === 0) {
        Message.warning({
          content: t('knowledge.graph.generate.error.empty'),
          duration: 5 * 1000,
        });
        EventBus.emit('blockGenratingGraph');
      } else if (selectedSubjectIDs.value.length > 1) {
        Message.warning({
          content: t('knowledge.graph.generate.error.onlyone'),
          duration: 5 * 1000,
        });
        EventBus.emit('blockGenratingGraph');
      } else {
        await generateGraph({
          libId: knowledgeLibID.value,
          subjectId: selectedSubjectIDs.value[0],
          maxDepth: (payload as { maxGraphDeep: number }).maxGraphDeep,
          llmName: knowledgeStore.currentLlm,
          embeddingModel: knowledgeStore.currentEmbedding,
          maxTokensEachChunk: knowledgeStore.maxTokensEachChunk,
        }).then(async (response) => {
          const { data } = response;
          if (data && data.success) {
            Message.success({
              content: t('knowledge.graph.generate.info.waiting'),
              duration: 5 * 1000,
            });

            // start polling
            setTimeout(startRefreshGraph, 10000);
          }
        });
      }
    });

    EventBus.off('analyze_graph');
    EventBus.on('analyze_graph', async () => {
      if (knowledgeStore.isAnalyzingGraph) {
        Message.warning({
          content: t('knowledge.graph.analyze.info.waiting'),
          duration: 3 * 1000,
        });
        return;
      }
      knowledgeStore.isAnalyzingGraph = true;
      if (!selectedSubjectIDs.value || selectedSubjectIDs.value.length === 0) {
        Message.warning({
          content: t('knowledge.graph.analyze.error.empty'),
          duration: 5 * 1000,
        });
      } else {
        setLoading(true);
        await analyzeGraph({
          libId: knowledgeLibID.value,
          subjectIds: selectedSubjectIDs.value,
          llmName: knowledgeStore.currentLlm,
          embeddingModel: knowledgeStore.currentEmbedding,
          maxTokensEachChunk: knowledgeStore.maxTokensEachChunk,
        })
          .then(async (response) => {
            const { data } = response;
            if (data && data.success) {
              Message.warning({
                content: t('knowledge.operation.analyze.success'),
                duration: 5 * 1000,
              });
            }
          })
          .finally(() => {
            setLoading(false);
            knowledgeStore.isAnalyzingGraph = false;
          });
      }
    });

    EventBus.off('cancel_generate_graph');
    EventBus.on('cancel_generate_graph', async () => {
      if (!knowledgeLibID.value) return;
      const response = await cancelGenerateGraph(knowledgeLibID.value);
      if (!response) return;
      const { data } = response;
      if (data && data.success) {
        Message.success({
          content: t('knowledge.graph.cancel.success'),
          duration: 5 * 1000,
        });
      }
    });

    EventBus.off('new_subject');
    EventBus.on('new_subject', async () => {
      knowledgeSubjectList.value.push({
        id: 0,
        name: '',
        knowledgeLibId: knowledgeLibID.value,
        editable: true,
      } as KnowledgeSubjectRecord);
    });
  });
</script>

<style lang="less">
  // Warning: Here is the global style
  .subject {
    &-list {
      &-cover {
        &-wrapper {
          position: relative;
          height: 68px;
        }

        &-tag {
          position: absolute;
          top: 6px;
          left: 6px;
        }
      }

      &-tip {
        display: block;
        margin-top: 16px;
        text-align: center;
      }
    }
  }
</style>
