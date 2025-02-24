<template>
  <div class="container">
    <Breadcrumb :items="['menu.doc', 'menu.doc.md']" />
    <div v-html="htmlContent"></div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import MarkdownIt from 'markdown-it'; 

  import i18n from '@/locale';
  import { Message } from '@arco-design/web-vue';

  const { t } = i18n.global;
  const htmlContent = ref('');
  const md = new MarkdownIt(); 

  onMounted(() => {
    if (htmlContent.value === '') {
      const currentLocale = i18n.global.locale.value;
      const filePath =
        currentLocale === 'zh-CN'
          ? '/src/assets/docs/README_zh.md'
          : '/src/assets/docs/README.md';
      fetch(filePath)
        .then((response) => response.text())
        .then((text) => {
          const result = md.render(text);
          htmlContent.value = result;
        })
        .catch((error) => Message.error(t('Markdown load failed'), error));
    }
  });
</script>

<script lang="ts">
  export default {
    name: 'DocDefault',
  };
</script>

<style scoped lang="less">
  .container {
    padding: 0 20px 20px 20px;
    height: calc(100% - 40px);
    :deep(.content) {
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      text-align: center;
      background-color: var(--color-bg-1);
      border-radius: 4px;
    }
  }
</style>
