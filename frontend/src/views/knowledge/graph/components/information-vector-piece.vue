<template>
  <a-space v-if="vector && vector.length > 0">
    <a-trigger trigger="click" :unmount-on-close="false">
      <a-button type="text" size="mini">
        {{ t('knowledge.information.vector') }}
      </a-button>
      <template #content>
        <div class="vector-basic">
          <a-typography-text
            :copyable="true"
            :ellipsis="{
              rows: 5,
            }"
          >
            {{ vector }}
          </a-typography-text>
        </div>
      </template>
    </a-trigger>
  </a-space>
</template>

<script lang="ts" setup>
  import { useI18n } from 'vue-i18n';
  import { PropType } from 'vue';

  let t: (key: string) => string;
  try {
    const { t: _t } = useI18n();
    t = _t;
  } catch (error) {
    t = (key: string) => {
      return key;
    };
  }

  defineProps({
    vector: {
      type: Array as PropType<number[]>,
      default: () => [],
    },
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
