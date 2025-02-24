<template>
  <div class="container">
    <Breadcrumb :items="['menu.knowledge', 'menu.knowledge.graph']" />
    <div class="layout">
      <div class="layout-left-side">
        <KnowledgeLibPanel />
      </div>
      <div class="layout-content">
        <a-space :size="16" direction="vertical" fill>
          <Config />
          <Graph />
          <Subject />
        </a-space>
      </div>
      <div class="layout-right-side">
        <a-space :size="16" direction="vertical" fill>
          <Information />
        </a-space>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import KnowledgeLibPanel from './components/knowledge-lib-panel.vue';
  import Config from './components/config.vue';
  import Graph from './components/graph.vue';
  import Subject from './components/subject.vue';
  import Information from './components/information.vue';
</script>

<script lang="ts">
  export default {
    name: 'Graph',
  };
</script>

<style scoped lang="less">
  .container {
    padding: 0 20px 20px 20px;
  }

  .layout {
    display: flex;

    &-left-side {
      flex: 1;
    }

    &-content {
      flex: 4 0 0;
      padding: 0 16px;
    }

    &-right-side {
      flex: 1;
      min-width: 280px;
    }
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
        flex-basis: 100%;
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
