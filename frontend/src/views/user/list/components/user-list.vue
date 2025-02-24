<template>
  <div class="container">
    <a-card class="general-card" :title="t('menu.user.list')">
      <a-row>
        <a-col :flex="1">
          <a-form
            :model="formModel"
            :label-col-props="{ span: 5 }"
            :wrapper-col-props="{ span: 18 }"
            label-align="right"
          >
            <a-row :gutter="16">
              <a-col :span="10">
                <a-form-item field="keyword" :label="t('user.form.keyword')">
                  <a-input
                    v-model="formModel.keyword"
                    :placeholder="t('user.form.keyword.placeholder')"
                  />
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
        </a-col>
        <a-divider direction="vertical" />
        <a-col :flex="'200px'" style="text-align: right">
          <a-space direction="horizontal" :size="18">
            <a-button type="primary" @click="search">
              <template #icon>
                <icon-search />
              </template>
              {{ t('user.form.search') }}
            </a-button>
            <a-button @click="reset">
              <template #icon>
                <icon-refresh />
              </template>
              {{ t('user.form.reset') }}
            </a-button>
          </a-space>
        </a-col>
      </a-row>
      <a-divider style="margin-top: 0" />
      <a-row style="margin-bottom: 16px">
        <a-col :span="12">
          <a-space>
            <a-button type="primary" @click="handleCreate">
              <template #icon>
                <icon-plus />
              </template>
              {{ t('user.operation.create') }}
            </a-button>
          </a-space>
        </a-col>
      </a-row>
      <a-table
        row-key="id"
        :loading="loading"
        :pagination="pagination"
        :columns="(cloneColumns as TableColumnData[])"
        :data="renderData"
        :bordered="false"
        :size="size"
        @page-change="onPageChange"
      >
        <template #operations="{ rowIndex }">
          <a-button
            v-permission="['ADMIN']"
            type="secondary"
            :title="t('user.operation.edit')"
            @click="editItem(rowIndex)"
          >
            <template #icon>
              <icon-edit />
            </template>
          </a-button>
          <a-popconfirm
            v-permission="['ADMIN']"
            :content="t('user.operation.delete.confirm')"
            @ok="deleteItem(rowIndex)"
          >
            <a-button
              v-permission="['ADMIN']"
              type="secondary"
              style="margin-left: 2px"
              :title="t('user.operation.delete')"
            >
              <template #icon>
                <icon-delete />
              </template>
            </a-button>
          </a-popconfirm>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
  import { computed, ref, reactive, watch, onMounted } from 'vue';
  import EventBus from '@/utils/event-bus';
  import { useI18n } from 'vue-i18n';
  import { useUserStore } from '@/store';
  import useLoading from '@/hooks/loading';
  import {
    queryUserList,
    UserRecord,
    UserParams,
    deleteUser,
  } from '@/api/user';
  import { Pagination } from '@/types/global';
  import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
  import cloneDeep from 'lodash/cloneDeep';
  import { Message } from '@arco-design/web-vue';

  type SizeProps = 'mini' | 'small' | 'medium' | 'large';
  type Column = TableColumnData & { checked?: true };

  const userFormModel = () => {
    return {
      keyword: '',
      role: '',
      startTime: '',
      endTime: '',
    };
  };
  const { loading, setLoading } = useLoading(true);
  const { t } = useI18n();
  const userStore = useUserStore();
  const renderData = ref<UserRecord[]>([]);
  const formModel = ref(userFormModel());
  const cloneColumns = ref<Column[]>([]);
  const showColumns = ref<Column[]>([]);

  const size = ref<SizeProps>('medium');

  const basePagination: Pagination = {
    current: 1,
    pageSize: 20,
  };
  const pagination = reactive({
    ...basePagination,
  });

  const columns = computed<TableColumnData[]>(() => [
    {
      title: t('user.form.username'),
      dataIndex: 'username',
    },
    {
      title: t('user.form.email'),
      dataIndex: 'email',
    },
    {
      title: t('user.form.mobile'),
      dataIndex: 'mobile',
    },
    {
      title: t('user.form.role'),
      dataIndex: 'role',
    },
    {
      title: t('user.form.createTime'),
      dataIndex: 'createTime',
    },
    {
      title: t('user.operation'),
      dataIndex: 'operations',
      slotName: 'operations',
    },
  ]);

  const fetchData = async (
    params: UserParams = { current: 1, pageSize: 20 } as UserParams
  ) => {
    setLoading(true);
    try {
      const response = await queryUserList(params);
      const { data } = response;
      renderData.value = data.list as UserRecord[];
      pagination.current = params.current as number;
      pagination.total = data.total as number;
    } catch (err) {
      // you can report use errorHandler or other
    } finally {
      setLoading(false);
    }
  };

  const search = () => {
    fetchData({
      ...basePagination,
      ...formModel.value,
    } as unknown as UserParams);
  };
  const onPageChange = (current: number) => {
    fetchData({ ...basePagination, current } as unknown as UserParams);
  };

  fetchData();
  const reset = () => {
    formModel.value = userFormModel();
  };

  const editItem = (rowIndex: number) => {
    userStore.setSelectedUser(renderData.value[rowIndex]);
  };

  const deleteItem = (rowIndex: number) => {
    const id = renderData?.value[rowIndex]?.id;
    if (id) {
      deleteUser(id).then(() => {
        Message.success(t('user.operation.delete.success'));
        fetchData();
      });
    }
  };

  watch(
    () => columns.value,
    (val) => {
      cloneColumns.value = cloneDeep(val);
      cloneColumns.value.forEach((item, index) => {
        item.checked = true;
      });
      showColumns.value = cloneDeep(cloneColumns.value);
    },
    { deep: true, immediate: true }
  );

  const handleCreate = () => {
    userStore.selectedUser = undefined;
    userStore.setSelectedUser({} as UserRecord);
  };

  onMounted(() => {
    EventBus.off('saved_user');
    EventBus.on('saved_user', () => {
      fetchData();
    });
  });
</script>

<script lang="ts">
  export default {
    name: 'UserList',
  };
</script>

<style scoped lang="less">
  .container {
    padding: 0 20px 20px 20px;
  }
  :deep(.arco-table-th) {
    &:last-child {
      .arco-table-th-item-title {
        margin-left: 16px;
      }
    }
  }
  .action-icon {
    margin-left: 12px;
    cursor: pointer;
  }
  .active {
    color: #0960bd;
    background-color: #e3f4fc;
  }
  .setting {
    display: flex;
    align-items: center;
    width: 200px;
    .title {list
      margin-left: 12px;
      cursor: pointer;
    }
  }
</style>
