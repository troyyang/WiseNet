<template>
  <div
    :class="[
      'knowledge-lib-item',
      { 'knowledge-lib-item-highlight': itemData.selected },
    ]"
  >
    <a-input
      v-if="localItemData.editable"
      v-model="localItemData.title"
      :placeholder="
        localItemData.editError || t('knowledge.lib.placeholder.title')
      "
      :error="!!localItemData.editError"
      @press-enter="submitEdit"
    >
      <template #suffix>
        <icon-save style="cursor: pointer" @click="submitEdit" />
        <icon-close
          style="cursor: pointer; margin-left: 2px"
          @click="cancelEdit"
        />
      </template>
    </a-input>
    <a-space v-else :size="4" direction="vertical" fill @click="selectItem">
      <a-typography-text class="knowledge-lib-item-title" :copyable="true">
        {{ localItemData.title }}
      </a-typography-text>

      <a-typography-text
        :copyable="true"
        :ellipsis="{
          rows: 2,
          expandable: true,
        }"
      >
        {{ localItemData.content }}
      </a-typography-text>
      <div class="knowledge-lib-item-footer">
        <div class="knowledge-lib-item-time">
          <a-typography-text type="secondary">
            {{ itemData.updateTime }}
          </a-typography-text>
        </div>
        <div class="knowledge-lib-item-actions">
          <div
            class="knowledge-lib-item-actions-item"
            :title="t('knowledge.operation.edit')"
            @click="editTitle"
          >
            <icon-edit />
          </div>
          <div
            class="knowledge-lib-item-actions-item"
            :title="t('knowledge.operation.delete')"
            @click="deleteItem"
          >
            <icon-delete />
          </div>
          <div
            class="knowledge-lib-item-actions-item"
            :title="
              itemData.status === 'PENDING'
                ? t('knowledge.operation.publish')
                : t('knowledge.operation.unpublish')
            "
            @click="publishItem"
          >
            <icon-arrow-rise v-if="itemData.status === 'PENDING'" />
            <icon-arrow-fall v-else />
          </div>
        </div>
      </div>
    </a-space>
  </div>
</template>

<script lang="ts" setup>
  import { ref, PropType } from 'vue';
  import EventBus from '@/utils/event-bus';
  import { useI18n } from 'vue-i18n';
  import { KnowledgeLibRecord } from '@/api/knowledge';

  const { t } = useI18n();

  const props = defineProps({
    itemData: {
      type: Object as PropType<KnowledgeLibRecord>,
      default() {
        return {};
      },
    },
    rowIndex: {
      type: Number,
      default: 0,
    },
  });

  interface LocalItemData {
    title: string;
    content: string;
    rowIndex: number;
    editable: boolean;
    editError: string;
  }

  const localItemData = ref<LocalItemData>({
    title: props.itemData.title || '',
    content: props.itemData.content || '',
    rowIndex: props.rowIndex,
    editable: props.itemData.editable,
    editError: '',
  });

  const editTitle = (event: Event) => {
    localItemData.value.editable = true;
    event.preventDefault();
    event.stopPropagation();
  };

  const submitEdit = async (event: Event) => {
    if (localItemData.value.title === '') {
      localItemData.value.editError = t('knowledge.edit.error.title');
      return;
    }

    EventBus.emit('save_lib', {
      rowIndex: props.rowIndex,
      title: localItemData.value.title,
    });

    localItemData.value.editable = false;
    event.preventDefault();
    event.stopPropagation();
  };

  const cancelEdit = (event: Event) => {
    localItemData.value.editable = false;
    localItemData.value.title = '';
    localItemData.value.editError = '';

    if (props.itemData.title === '' && localItemData.value.title === '') {
      EventBus.emit('delete_lib', {
        rowIndex: props.rowIndex,
      });
    }
    event.preventDefault();
    event.stopPropagation();
  };

  const deleteItem = (event: Event) => {
    EventBus.emit('delete_lib', {
      rowIndex: props.rowIndex,
    });
    event.preventDefault();
    event.stopPropagation();
  };

  const publishItem = (event: Event) => {
    EventBus.emit('publish_lib', {
      rowIndex: props.rowIndex,
    });
    event.preventDefault();
    event.stopPropagation();
  };

  const selectItem = () => {
    EventBus.emit('knowledgeLibSelected', {
      rowIndex: props.rowIndex,
      ...props.itemData,
    });
  };
</script>

<style scoped lang="less">
  .knowledge-lib-item {
    padding: 8px;
    font-size: 12px;
    line-height: 20px;
    border-radius: 2px;

    &-title {
      font-size: 14px;
      font-weight: bold;
    }
    &-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    &-actions {
      display: flex;
      opacity: 0;

      &-item {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        margin-right: 4px;
        color: var(--color-text-3);
        font-size: 14px;
        border-radius: 50%;
        cursor: pointer;

        &:hover {
          background-color: rgb(var(--gray-3));
        }

        &:last-child {
          margin-right: 0;
        }
      }
    }

    &-collected {
      .knowledge-lib-item-actions-collect {
        color: rgb(var(--gold-6));
      }
    }

    &:hover {
      background-color: rgb(var(--gray-2));

      .knowledge-lib-item-actions {
        opacity: 1;
      }
    }

    &-highlight {
      background-color: rgb(var(--gray-1));
    }
  }
</style>
