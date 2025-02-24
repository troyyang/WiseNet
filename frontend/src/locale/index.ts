import { createI18n } from 'vue-i18n';
import en from './en-US';
import cn from './zh-CN';

export const LOCALE_OPTIONS = [
  { label: 'English', value: 'en-US' },
  { label: '中文', value: 'zh-CN' },
];
const defaultLocale = localStorage.getItem('arco-locale') || 'zh-CN';

const i18n = createI18n({
  locale: defaultLocale,
  fallbackLocale: 'en-US',
  legacy: false,
  allowComposition: true,
  messages: {
    'en-US': en,
    'zh-CN': cn,
  },
});

export default i18n;
