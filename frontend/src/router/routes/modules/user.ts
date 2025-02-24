import { DEFAULT_LAYOUT } from '../base';
import { AppRouteRecordRaw } from '../types';

const USER: AppRouteRecordRaw = {
  path: '/user',
  name: 'user',
  component: DEFAULT_LAYOUT,
  meta: {
    locale: 'menu.user',
    icon: 'icon-user',
    requiresAuth: true,
    order: 2,
  },
  children: [
    {
      path: 'user-list',
      name: 'UserList',
      component: () => import('@/views/user/list/index.vue'),
      meta: {
        locale: 'menu.user.list',
        requiresAuth: true,
        roles: ['ADMIN'],
      },
    },
    {
      path: 'setting',
      name: 'Setting',
      component: () => import('@/views/user/setting/index.vue'),
      meta: {
        locale: 'menu.user.setting',
        requiresAuth: true,
        roles: ['*'],
      },
    },
  ],
};

export default USER;
