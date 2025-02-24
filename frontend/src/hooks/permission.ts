import { RouteLocationNormalized, RouteRecordRaw } from 'vue-router';
import { useUserStore } from '@/store';

export default function usePermission() {
  const userStore = useUserStore();
  return {
    accessRouter(route: RouteLocationNormalized | RouteRecordRaw) {
      const requiresAuth = route.meta?.requiresAuth;
      const roles = route.meta?.roles;
      const currentRole = userStore.currentUser.role ? userStore.currentUser.role : '';
      const hasAccess = !requiresAuth || !roles || roles.includes('*') || roles.includes(currentRole);
      return hasAccess;
    },
    findFirstPermissionRoute(_routers: any, role = 'ADMIN') {
      const cloneRouters = [..._routers];
      while (cloneRouters.length) {
        const firstElement = cloneRouters.shift();
        const roles = firstElement?.meta?.roles;
        if (roles && (roles.includes('*') || roles.includes(role))) {
          return { name: firstElement.name };
        }
        if (firstElement?.children) {
          cloneRouters.push(...firstElement.children);
        }
      }
      return null;
    },
    // You can add any rules you want
  };
}