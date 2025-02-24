import { createPinia } from 'pinia';
import useAppStore from './modules/app';
import useUserStore from './modules/user';
import useTabBarStore from './modules/tab-bar';
import useKnowledgeStore from './modules/knowledge';

const pinia = createPinia();

export { useAppStore, useUserStore, useTabBarStore, useKnowledgeStore };
export default pinia;
