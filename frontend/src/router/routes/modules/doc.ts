import { DEFAULT_LAYOUT } from '../base';
import { AppRouteRecordRaw } from '../types';

const Doc: AppRouteRecordRaw = {
  path: '/doc',
  name: 'doc',
  component: DEFAULT_LAYOUT,
  meta: {
    locale: 'menu.doc',
    requiresAuth: true,
    icon: 'icon-book',
    order: 4,
  },
  children: [
    {
      path: 'doc-md',
      name: 'DocMd',
      component: () => import('@/views/doc/md/index.vue'),
      meta: {
        locale: 'menu.doc.md',
        requiresAuth: true,
        roles: ['*'],
      },
    },
  ],
};

export default Doc;
