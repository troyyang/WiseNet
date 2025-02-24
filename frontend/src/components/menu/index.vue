<script lang="tsx">
  import { defineComponent, ref, h, compile, computed, VNode } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { useRoute, useRouter, RouteRecordRaw } from 'vue-router';
  import type { RouteMeta } from 'vue-router';
  import { useAppStore } from '@/store';
  import { listenerRouteChange } from '@/utils/route-listener';
  import { openWindow, regexUrl } from '@/utils';
  import { Menu, SubMenu, MenuItem } from '@arco-design/web-vue';
  import useMenuTree from './use-menu-tree';

  export default defineComponent({
    emit: ['collapse'],
    setup() {
      const { t } = useI18n();
      const appStore = useAppStore();
      const router = useRouter();
      const route = useRoute();
      const { menuTree } = useMenuTree();
      const collapsed = computed({
        get() {
          if (appStore.device === 'desktop') return appStore.menuCollapse;
          return false;
        },
        set(value: boolean) {
          appStore.updateSettings({ menuCollapse: value });
        },
      });

      const topMenu = computed(() => appStore.topMenu);
      const openKeys = ref<string[]>([]);
      const selectedKey = ref<string[]>([]);

      const goto = (item: RouteRecordRaw) => {
        // Open external link
        if (regexUrl.test(item.path)) {
          openWindow(item.path);
          selectedKey.value = [item.name as string];
          return;
        }
        // Eliminate external link side effects
        const { hideInMenu, activeMenu } = item.meta as RouteMeta;
        if (route.name === item.name && !hideInMenu && !activeMenu) {
          selectedKey.value = [item.name as string];
          return;
        }
        // Trigger router change
        router.push({
          name: item.name,
        });
      };
      const findMenuOpenKeys = (target: string) => {
        const result: string[] = [];
        let isFind = false;
        const backtrack = (item: RouteRecordRaw, keys: string[]) => {
          if (item.name === target) {
            isFind = true;
            result.push(...keys);
            return;
          }
          if (item.children?.length) {
            item.children.forEach((el) => {
              backtrack(el, [...keys, el.name as string]);
            });
          }
        };
        menuTree.value.forEach((el: RouteRecordRaw) => {
          if (isFind) return; // Performance optimization
          backtrack(el, [el.name as string]);
        });
        return result;
      };
      listenerRouteChange((newRoute) => {
        const { requiresAuth, activeMenu, hideInMenu } = newRoute.meta;
        if (requiresAuth && (!hideInMenu || activeMenu)) {
          const menuOpenKeys = findMenuOpenKeys(
            (activeMenu || newRoute.name) as string
          );

          const keySet = new Set([...menuOpenKeys, ...openKeys.value]);
          openKeys.value = [...keySet];

          selectedKey.value = [
            activeMenu || menuOpenKeys[menuOpenKeys.length - 1],
          ];
        }
      }, true);
      const setCollapse = (val: boolean) => {
        if (appStore.device === 'desktop')
          appStore.updateSettings({ menuCollapse: val });
      };

      const renderSubMenu = () => {
        function travel(_route: RouteRecordRaw[], nodes: VNode[] = []) {
          if (_route) {
            _route.forEach((element) => {
              const iconComponent = element?.meta?.icon
                ? h(compile(`<${element?.meta?.icon}/>`))
                : null;
              const node =
                element?.children && element?.children.length !== 0
                  ? h(
                      SubMenu,
                      {
                        key: String(element?.name),
                        title: t(element?.meta?.locale || ''),
                      },
                      {
                        icon: () => iconComponent,
                        default: () => travel(element.children || []),
                      }
                    )
                  : h(
                      MenuItem,
                      {
                        key: String(element?.name),
                        onClick: () => goto(element),
                      },
                      {
                        icon: () => iconComponent,
                        default: () => t(element?.meta?.locale || ''),
                      }
                    );
              nodes.push(node);
            });
          }
          return nodes;
        }
        return travel(menuTree.value);
      };

      return () =>
        h(
          Menu,
          {
            mode: topMenu.value ? 'horizontal' : 'vertical',
            'v-model:collapsed': collapsed.value,
            'v-model:open-keys': openKeys.value,
            'v-model:selected-keys': selectedKey.value,
            showCollapseButton: appStore.device !== 'mobile',
            autoOpen: false,
            autoOpenSelected: true,
            selectedKeys: selectedKey.value,
            levelIndent: 34,
            style: 'height: 100%; width:100%;',
            onCollapse: setCollapse
          },
          {
            default: () => renderSubMenu(),
          }
        );
    },
  });
</script>

<style lang="less" scoped>
  :deep(.arco-menu-inner) {
    .arco-menu-inline-header {
      display: flex;
      align-items: center;
    }
    .arco-icon {
      &:not(.arco-icon-down) {
        font-size: 18px;
      }
    }
  }
</style>
