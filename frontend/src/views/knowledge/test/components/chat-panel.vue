<template>
  <a-card class="general-card" :title="t('chat.list.title')">
    <template #extra>
      <a-button
        type="secondary"
        :title="t('chat.list.new')"
        @click="newConversation"
      >
        <icon-plus />
      </a-button>
    </template>
    <div class="chat-wrapper">
      <div class="chat-list">
        <div
          v-for="message in messages"
          :key="message.id"
          :item-data="message"
          :class="message.type === 'ai' ? 'chat-item-left' : 'chat-item-right'"
        >
          <a-space
            :size="12"
            :class="
              message.type === 'ai'
                ? 'left-item-container'
                : 'right-item-container'
            "
            @click="changeInformationNode(message)"
          >
            <a-avatar
              :size="24"
              :class="message.type === 'ai' ? 'left-avatar' : 'right-avatar'"
            >
              <img
                :src="
                  message.type === 'ai'
                    ? logoImg
                    : userHeaderImg
                "
              />
            </a-avatar>
            <a-typography-text>
              <a-typography-text :copyable="true">
                {{ message.content }}
                <a-typography-text
                  v-if="message.queryResult?.document"
                  type="secondary"
                  style="font-size: 12px"
                  >{{ t('chat.list.source')
                  }}<a-link
                    :href="void 0"
                    @click="
                      openDocument(message.queryResult?.document?.savedAt)
                    "
                    >{{ message.queryResult?.document?.name }}</a-link
                  ></a-typography-text
                >
                <a-typography-text
                  v-if="message.queryResult?.webpage"
                  type="secondary"
                  style="font-size: 12px"
                  >{{ t('chat.list.source')
                  }}<a-link
                    :href="void 0"
                    @click="openWebpage(message.queryResult?.webpage?.url)"
                    >{{ message.queryResult?.webpage?.url }}</a-link
                  ></a-typography-text
                >
              </a-typography-text>
              <a-typography
                v-if="
                  message.queryResult?.prompts &&
                  message.queryResult?.prompts.length > 0
                "
                class="prompts-content"
                :copyable="true"
              >
                <ol>
                  <li
                    v-for="prompt in message.queryResult?.prompts"
                    :key="prompt.elementId"
                  >
                    <a-link @click="searchByPrompt(prompt)">
                      {{ prompt.content }}
                    </a-link>
                  </li>
                </ol>
              </a-typography>
              <a-typography
                v-if="
                  message.queryResult?.relatedNodes &&
                  message.queryResult?.relatedNodes.length > 0
                "
                class="prompts-content"
                :copyable="true"
              >
                <ol>
                  <a-typography-title :heading="6">
                    {{ t('knowledge.information.related') }}
                  </a-typography-title>
                  <li
                    v-for="relatedNode in message.queryResult?.relatedNodes"
                    :key="relatedNode.elementId"
                  >
                    <a-link @click="searchByRelatedNode(relatedNode)">
                      {{ relatedNode.title }}
                    </a-link>
                  </li>
                </ol>
              </a-typography>
            </a-typography-text>
          </a-space>
        </div>
      </div>
      <div class="chat-bar">
        <div
          v-if="knowledgeStore.testMessageProcessing"
          id="thinking"
          class="lds-ellipsis"
          ><div></div><div></div><div></div><div></div
        ></div>
      </div>
    </div>
  </a-card>
</template>

<script lang="ts" setup>
  import { ref, onMounted, nextTick } from 'vue';
  import { useI18n } from 'vue-i18n';
  import EventBus from '@/utils/event-bus';
  import { useKnowledgeStore } from '@/store';
  import {
    sendMessage,
    sendMessageStream,
    MessageRecord,
    getDownloadUrl,
    QueryResultRecord,
    NodeRecord,
  } from '@/api/graph';
  import { Message } from '@arco-design/web-vue';
  import { openWindow } from '@/utils';
  import logoImg from '@/assets/logo.png';
  import userHeaderImg from '@/assets/images/user-header.png';

  const { t } = useI18n();
  const knowledgeStore = useKnowledgeStore();
  const promptElementId = ref<string>('');
  const relatedNodeElementId = ref<string>('');
  const streamQueryResult = ref<QueryResultRecord | undefined>(undefined);

  const messages = ref<MessageRecord[]>([]);

  const gotoTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  const gotoBottom = () => {
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior: 'smooth',
    });
  };

  const newConversation = () => {
    messages.value = [
      {
        id: 1,
        type: 'ai',
        content: t('test.greet'),
        time: new Date(),
        queryResult: null,
      },
    ];
    knowledgeStore.testMessageProcessing = false;
    streamQueryResult.value = undefined;
    knowledgeStore.queryResultRecord = undefined;

    nextTick(() => {
      gotoTop();
    });
  };

  const openWebpage = (url: string) => {
    openWindow(url, { target: '_blank' });
  };

  const openDocument = (savedAt: string) => {
    openWindow(getDownloadUrl(savedAt), { target: '_blank' });
  };

  const changeInformationNode = (message: MessageRecord) => {
    if (!message.queryResult) {
      return;
    }
    knowledgeStore.queryResultRecord = message.queryResult;
  };

  const isTyping = ref(false);
  const typewriterEffect = (text: string, index = 0) => {
    if (index < text.length) {
      isTyping.value = true;
      messages.value[messages.value.length - 1].content += text.charAt(index);
      setTimeout(() => {
        typewriterEffect(text, index + 1);
        nextTick(() => {
          gotoBottom();
        });
      }, 10);
    } else {
      isTyping.value = false;
    }
  };

  const handleStreamingEnd = () => {
    if (isTyping.value) {
      setTimeout(() => {
        handleStreamingEnd();
      }, 300);
    } else {
      knowledgeStore.testMessageProcessing = false;
      if (streamQueryResult.value) {
        messages.value[messages.value.length - 1].queryResult =
          streamQueryResult.value;
        knowledgeStore.queryResultRecord = streamQueryResult.value;
        nextTick(() => {
          gotoBottom();
        });
      }
    }
  };

  const searchKnowledge = (messageContents: string[]) => {
    knowledgeStore.testMessageProcessing = true;
    streamQueryResult.value = undefined;
    nextTick(() => {
      gotoBottom();
    });
    const condition = {
      messages: messageContents,
      libId: knowledgeStore.testLibId,
      subjectId: knowledgeStore.testSubjectId
        ? knowledgeStore.testSubjectId
        : undefined,
      llmName: knowledgeStore.currentLlm,
      returnMethod: knowledgeStore.testReturnMethod,
      chainType: knowledgeStore.currentMessageSummaryType,
      embeddingModel: knowledgeStore.currentEmbedding,
      maxTokensEachChunk: knowledgeStore.maxTokensEachChunk,
      searchScope: knowledgeStore.selectedSearchScopes,
      searchType: knowledgeStore.selectedSearchType,
      onlyTitle: knowledgeStore.onlyTitle,
      promptElementId: promptElementId.value || undefined,
      relatedNodeElementId: relatedNodeElementId.value || undefined,
    };

    if (condition.returnMethod === 'stream') {
      sendMessageStream(
        condition,
        (data) => {
          if (!streamQueryResult.value) {
            streamQueryResult.value = {
              text: '',
              mainNode: null,
              entities: [],
              keywords: [],
              tags: [],
              webpage: null,
              document: null,
              prompts: [],
              relatedNodes: [],
            };
            messages.value.push({
              id: messages.value.length + 1,
              type: 'ai',
              content: '',
              time: new Date(),
              queryResult: {
                text: '',
                mainNode: null,
                entities: [],
                keywords: [],
                tags: [],
                webpage: null,
                document: null,
                prompts: [],
                relatedNodes: [],
              },
            });
          }
          if (streamQueryResult.value && data.text) {
            streamQueryResult.value.text += data.text;
            // messages.value[messages.value.length - 1].content += data.text;
            typewriterEffect(data.text);
          }
          if (streamQueryResult.value && data.mainNode) {
            streamQueryResult.value.mainNode = data.mainNode;
          }
          if (
            streamQueryResult.value &&
            data.entities &&
            data.entities.length > 0
          ) {
            streamQueryResult.value.entities = data.entities;
          }
          if (
            streamQueryResult.value &&
            data.keywords &&
            data.keywords.length > 0
          ) {
            streamQueryResult.value.keywords = data.keywords;
          }
          if (streamQueryResult.value && data.tags && data.tags.length > 0) {
            streamQueryResult.value.tags = data.tags;
          }
          if (streamQueryResult.value && data.webpage) {
            streamQueryResult.value.webpage = data.webpage;
          }
          if (streamQueryResult.value && data.document) {
            streamQueryResult.value.document = data.document;
          }
          if (
            streamQueryResult.value &&
            data.prompts &&
            data.prompts.length > 0
          ) {
            streamQueryResult.value.prompts = data.prompts;
          }
          if (
            streamQueryResult.value &&
            data.relatedNodes &&
            data.relatedNodes.length > 0
          ) {
            streamQueryResult.value.relatedNodes = data.relatedNodes;
          }

          // scroll to bottom after data update
          nextTick(() => {
            gotoBottom();
          });
        },
        () => {
          handleStreamingEnd();
        },
        (err) => {
          Message.error(err);
          messages.value.push({
            id: messages.value.length + 1,
            type: 'ai',
            content: err.message,
            time: new Date(),
            queryResult: null,
          });

          knowledgeStore.queryResultRecord = undefined;

          nextTick(() => {
            gotoBottom();
          });
          knowledgeStore.testMessageProcessing = false;
        }
      );
    } else {
      sendMessage(condition)
        .then((res) => {
          const { data } = res;
          knowledgeStore.testMessageProcessing = false;
          messages.value.push({
            id: messages.value.length + 1,
            type: 'ai',
            content: data.text,
            time: new Date(),
            queryResult: data,
          });
          knowledgeStore.queryResultRecord = data;
          // scroll to bottom after data update
          nextTick(() => {
            gotoBottom();
          });
        })
        .catch((err) => {
          Message.error(err);
          messages.value.push({
            id: messages.value.length + 1,
            type: 'ai',
            content: err.message,
            time: new Date(),
            queryResult: null,
          });
          knowledgeStore.queryResultRecord = undefined;

          nextTick(() => {
            gotoBottom();
          });
        })
        .finally(() => {
          knowledgeStore.testMessageProcessing = false;
        });
    }
  };

  const searchByPrompt = (prompt: NodeRecord) => {
    promptElementId.value = prompt.elementId;
    messages.value.push({
      id: messages.value.length + 1,
      type: 'user',
      content: prompt.content,
      time: new Date(),
      queryResult: null,
    });
    searchKnowledge([]);
  };

  const searchByRelatedNode = (relatedNode: NodeRecord) => {
    relatedNodeElementId.value = relatedNode.elementId;
    messages.value.push({
      id: messages.value.length + 1,
      type: 'user',
      content: relatedNode.title,
      time: new Date(),
      queryResult: null,
    } as MessageRecord);
    searchKnowledge([]);
  };

  onMounted(() => {
    newConversation();

    EventBus.off('onSendMessage');
    EventBus.on('onSendMessage', (msg) => {
      if (!msg) {
        Message.warning(t('knowledge.search.placeholder'));
        knowledgeStore.testMessageProcessing = false;
        return;
      }
      if (!knowledgeStore.testLibId) {
        Message.warning(t('knowledge.test.lib.empty'));
        knowledgeStore.testMessageProcessing = false;
        return;
      }

      messages.value.push({
        id: messages.value.length + 1,
        type: 'user',
        content: msg || '',
        time: new Date(),
        queryResult: null,
      } as MessageRecord);

      const lastMessages = messages.value.slice(-1);
      const messageContents: string[] = [];
      lastMessages.forEach((message) => {
        messageContents.push(message.content);
      });

      searchKnowledge(messageContents);
    });
  });
</script>

<style scoped lang="less">
  .chat {
    &-wrapper {
      display: block;
      margin: 0 auto;
      width: 100%;
    }

    &-list {
      display: flex;
      flex-direction: column;
    }

    &-item-left {
      align-self: flex-start;
      margin-bottom: 10px;
      padding: 10px;
      border-radius: 10px;
      background-color: #ffffff;
      border: 1px solid #ccc;
      max-width: 100%;
      font-size: 14px;
      line-height: 1.5;
    }

    &-item-right {
      align-self: flex-end;
      margin-bottom: 10px;
      padding: 10px;
      border-radius: 10px;
      background-color: #f8f8f8;
      border: 1px solid #ccc;
      max-width: 80%;
      font-size: 14px;
      line-height: 1.5;
    }

    &-bar {
      width: 100%;
      display: flex;
      flex-direction: column;
      justify-content: center;
      margin-top: 16px;
      font-size: 12px;
      align-items: center;
      justify-content: center;
    }
  }
  .left-item-container {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
  }
  .right-item-container {
    display: flex;
    flex-direction: row-reverse;
    align-items: flex-start;
  }
  .left-avatar {
    margin-right: 0px;
  }
  .right-avatar {
    margin-left: 10px;
    margin-right: -12px;
  }
</style>

<style scoped lang="less">
  @import './ids-ellipsis.less';
</style>
