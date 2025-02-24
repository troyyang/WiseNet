import { DEFAULT_LAYOUT } from '../base';
import { AppRouteRecordRaw } from '../types';

const KNNOWLEDGE: AppRouteRecordRaw = {
  path: '/knowledge',
  name: 'knowledge',
  component: DEFAULT_LAYOUT,
  meta: {
    locale: 'menu.knowledge',
    requiresAuth: true,
    icon: 'icon-relation',
    order: 1,
  },
  children: [
    {
      path: 'knowledge-graph',
      name: 'KnowledgeGraph',
      component: () => import('@/views/knowledge/graph/index.vue'),
      meta: {
        locale: 'menu.knowledge.graph',
        requiresAuth: true,
        roles: ['*'],
      },
    },
    {
      path: 'knowledge-test',
      name: 'KnowledgeTest',
      component: () => import('@/views/knowledge/test/index.vue'),
      meta: {
        locale: 'menu.knowledge.test',
        requiresAuth: true,
        roles: ['*'],
      },
    },
  ],
};

export default KNNOWLEDGE;
