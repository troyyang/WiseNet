<template>
  <a-card class="general-card" :title="t('menu.knowledge.subject')">
    <div class="subject-content">
      <div class="subject-list-wrapper">
        <div class="subject-list-header">
          <a-space>
            <a-button type="primary" @click="generate">
              <template v-if="isGenratingGraph" #icon>
                <icon-loading />
              </template>
              <template #default>
                {{ t('knowledge.operation.generate') }}
              </template>
            </a-button>
            <div>
              <a-select
                v-model="knowledgeStore.maxGraphDeep"
                style="width: 60px"
                :placeholder="t('knowledge.graph.max.deep')"
                @change="knowledgeStore.setMaxGraphDeep"
              >
                <a-option
                  v-for="deep in knowledgeStore.graphDeeps"
                  :key="deep"
                  :value="deep"
                  >{{ deep }}</a-option
                >
              </a-select>
              <a-popover :title="t('knowledge.graph.max.deep')">
                <icon-question-circle :title="t('knowledge.graph.max.deep')" />
                <template #content>
                  <p>{{ t('knowledge.graph.max.deep.detail') }}</p>
                </template>
              </a-popover>
            </div>
            <a-button
              type="primary"
              :title="t('knowledge.operation.analyze.graph')"
              @click="analyze"
            >
              <template v-if="knowledgeStore.isAnalyzingGraph" #icon>
                <icon-loading />
              </template>
              <template v-else #icon>
                <icon-command />
              </template>
            </a-button>
            <a-button
              type="secondary"
              :title="t('knowledge.operation.cancel')"
              @click="cancelGenerateGraph"
            >
              <template #icon>
                <icon-stop />
              </template>
            </a-button>
          </a-space>
          <a-button type="outline" @click="newSubject">{{
            t('knowledge.operation.new.subject')
          }}</a-button>
        </div>
        <div class="subject-list-content">
          <SubjectList />
        </div>
      </div>
    </div>
  </a-card>
</template>

<script lang="ts" setup>
  import { onMounted, ref } from 'vue';
  import { useI18n } from 'vue-i18n';
  import EventBus from '@/utils/event-bus';
  import { useKnowledgeStore } from '@/store';
  import { Message } from '@arco-design/web-vue';
  import SubjectList from './subject-list.vue';

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();

  const isGenratingGraph = ref<boolean>(false);

  const generate = () => {
    if (isGenratingGraph.value) {
      Message.warning({
        content: t('knowledge.graph.generate.info.waiting'),
        duration: 3 * 1000,
      });
      return;
    }
    isGenratingGraph.value = true;
    EventBus.emit('generate_graph', {
      maxGraphDeep: knowledgeStore.maxGraphDeep,
    });
  };

  const analyze = () => {
    EventBus.emit('analyze_graph');
  };

  const cancelGenerateGraph = () => {
    EventBus.emit('cancel_generate_graph');
  };

  const newSubject = () => {
    EventBus.emit('new_subject');
  };

  onMounted(() => {
    knowledgeStore.queryAll();
    EventBus.off('finishGenratingGraph');
    EventBus.on('finishGenratingGraph', () => {
      if (isGenratingGraph.value) {
        Message.success({
          content: t('knowledge.operation.generate.success'),
          duration: 5 * 1000,
        });
      }
      isGenratingGraph.value = false;
    });
    EventBus.off('blockGenratingGraph');
    EventBus.on('blockGenratingGraph', () => {
      isGenratingGraph.value = false;
    })
  });
</script>

<style scoped lang="less">
  .subject {
    &-content {
      padding: 0px 0;
    }

    &-list {
      &-header {
        display: flex;
        justify-content: space-between;
      }

      &-content {
        margin-top: 6px;
      }
    }
  }
</style>
