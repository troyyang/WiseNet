<template>
  <a-card :bordered="false" :body-style="{ padding: '20px' }">
    <div class="textarea-container">
      <a-textarea
        v-model="message"
        :placeholder="t('knowledge.search.placeholder')"
        :auto-size="{
          minRows: 3,
          maxRows: 30,
        }"
        :max-length="500"
        :disabled="knowledgeStore.testMessageProcessing"
        allow-clear
        show-word-limit
      />
      <a-space class="toolbar">
        <a-button
          :disabled="knowledgeStore.testMessageProcessing"
          @click="onSend"
        >
          <template #icon>
            <icon-send />
          </template>
          <!-- Use the default slot to avoid extra spaces -->
          <template #default>{{ t('knowledge.operation.send') }}</template>
        </a-button>
      </a-space>
    </div>
  </a-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { useI18n } from 'vue-i18n';
  import EventBus from '@/utils/event-bus';
  import { useKnowledgeStore } from '@/store';
  import { Message } from '@arco-design/web-vue';

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();

  const message = ref<string>();

  const onSend = () => {
    if (!message.value) {
      Message.error(t('knowledge.search.placeholder'));
      return;
    }

    EventBus.emit('onSendMessage', message.value);
    message.value = '';
  };
</script>

<style scoped lang="less">
  .textarea-container {
    position: relative;
    display: flex;
    align-items: flex-start;
    flex-direction: column;
  }
  .toolbar {
    width: 100%;
    display: flex;
    justify-content: flex-end;
    margin-top: 5px;
  }
</style>
