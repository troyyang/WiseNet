import { DEFAULT_LAYOUT } from '../base';
import { AppRouteRecordRaw } from '../types';

const API: AppRouteRecordRaw = {
  path: '/api',
  name: 'api',
  component: DEFAULT_LAYOUT,
  meta: {
    locale: 'menu.api',
    requiresAuth: true,
    icon: 'icon-code',
    order: 3,
  },
  children: [
    {
      path: 'api-swagger',
      name: 'Swagger',
      component: () => import('@/views/api/swagger/index.vue'),
      meta: {
        locale: 'menu.api.swagger',
        requiresAuth: true,
        roles: ['*'],
      },
    },
    {
      path: 'api-redoc',
      name: 'Redoc',
      component: () => import('@/views/api/redoc/index.vue'),
      meta: {
        locale: 'menu.api.redoc',
        requiresAuth: true,
        roles: ['*'],
      },
    },
  ],
};

export default API;
