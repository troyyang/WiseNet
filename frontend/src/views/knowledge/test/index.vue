<template>
  <div class="container">
    <Breadcrumb :items="['menu.knowledge', 'menu.knowledge.test']" />
    <div class="layout">
      <div class="layout-content">
        <a-space :size="16" class="content-panel" direction="vertical" fill>
          <a-affix>
            <Config />
          </a-affix>
          <ChatPanel />
          <a-affix :offset-bottom="30">
            <a-space :size="16" direction="vertical" fill>
              <InputPanel />
            </a-space>
          </a-affix>
        </a-space>
      </div>
      <div v-if="knowledgeStore.queryResultRecord" class="layout-right-side">
        <a-space :size="16" direction="vertical" fill>
          <QueryResult />
        </a-space>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { useKnowledgeStore } from '@/store';

  import Config from './components/config.vue';
  import ChatPanel from './components/chat-panel.vue';
  import InputPanel from './components/input-panel.vue';
  import QueryResult from './components/query-result.vue';

  const knowledgeStore = useKnowledgeStore();
</script>

<script lang="ts">
  export default {
    name: 'Test',
  };
</script>

<style scoped lang="less">
  .container {
    padding: 0 20px 20px 20px;
  }

  .layout {
    display: flex;

    &-left-side {
      flex-basis: 300px;
    }

    &-content {
      flex: 1;
      padding: 0 16px;
      display: flex;
      justify-content: center;
    }

    &-right-side {
      flex-basis: 360px;
    }
  }
  .content-panel {
    width: 800px;
  }
</style>

<style lang="less" scoped>
  // responsive
  @media (max-width: @screen-lg) {
    .layout {
      flex-wrap: wrap;
      &-left-side {
        flex: 1;
        flex-basis: 100%;
        margin-bottom: 16px;
      }

      &-content {
        flex: none;
        flex-basis: 80%;
        padding: 0;
        order: -1;
        margin-bottom: 16px;
      }

      &-right-side {
        flex-basis: 100%;
      }
    }
  }
</style>
