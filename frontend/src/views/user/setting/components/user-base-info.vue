<template>
  <div class="container">
    <a-card class="general-card" :title="t('userSetting.tab.basicInformation')">
      <div class="user-base-info-error-msg">{{ errorMessage }}</div>
      <a-form :model="formModel" @submit="handleSubmit">
        <a-form-item
          field="username"
          :label="t('userSetting.basicInfo.form.label.username')"
          :rules="[
            {
              required: true,
              message: t('userSetting.basicInfo.form.error.username.required'),
            },
          ]"
          :validate-trigger="['change', 'blur']"
        >
          <a-input
            v-model="formModel.username"
            :placeholder="t('userSetting.basicInfo.placeholder.username')"
          >
            <template #prefix>
              <icon-user />
            </template>
          </a-input>
        </a-form-item>
        <a-form-item
          field="email"
          :label="t('userSetting.basicInfo.form.label.email')"
          :rules="[
            {
              required: true,
              message: t('userSetting.basicInfo.form.error.email.required'),
            },
          ]"
          :validate-trigger="['change', 'blur']"
        >
          <a-input
            v-model="formModel.email"
            :placeholder="t('userSetting.basicInfo.placeholder.email')"
          >
            <template #prefix>
              <icon-at />
            </template>
          </a-input>
        </a-form-item>
        <a-form-item
          field="mobile"
          :label="t('userSetting.basicInfo.form.label.mobile')"
          :validate-trigger="['change', 'blur']"
        >
          <a-input
            v-model="formModel.mobile"
            :placeholder="t('userSetting.basicInfo.placeholder.mobile')"
          >
            <template #prefix>
              <icon-mobile />
            </template>
          </a-input>
        </a-form-item>
        <a-form-item>
          <a-space :size="16" align="center">
            <a-button type="primary" html-type="submit" :loading="loading">
              {{ t('userSetting.form.submit') }}
            </a-button>
            <a-button type="text" @click="handleReset">
              {{ t('userSetting.form.reset') }}
            </a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
  import { ref, PropType, onMounted } from 'vue';
  import { useI18n } from 'vue-i18n';
  import useLoading from '@/hooks/loading';
  import { UserRecord, updateUserInfo } from '@/api/user';
  import { useUserStore } from '@/store';
  import { ValidatedError } from '@arco-design/web-vue/es/form/interface';
  import { Message } from '@arco-design/web-vue';
  import validateEmail from '@/utils/email';

  const { loading, setLoading } = useLoading(false);
  const { t } = useI18n();
  const errorMessage = ref('');
  const formModel = ref({
    id: null,
    username: '',
    email: '',
    mobile: '',
  } as UserRecord);

  const userStore = useUserStore();

  const props = defineProps({
    selectedUser: {
      type: Object as PropType<UserRecord>,
      default: null,
    },
  });

  const handleSubmit = async ({
    errors,
    values,
  }: {
    errors: Record<string, ValidatedError> | undefined;
    values: Record<string, any>;
  }) => {
    if (loading.value) return;
    if (!errors) {
      if (formModel.value.email && !validateEmail(formModel.value.email)) {
        errorMessage.value = t('user.form.email.invalid.errMsg');
        return;
      }

      errorMessage.value = '';
      setLoading(true);
      updateUserInfo(formModel.value)
        .then(() => {
          userStore.info();
          Message.success(t('user.form.save.success'));
        })
        .catch((error) => {
          errorMessage.value = error.message;
        })
        .finally(() => {
          setLoading(false);
        });
    }
  };

  const handleReset = () => {
    formModel.value = props.selectedUser;
  };

  onMounted(() => {
    if (props.selectedUser) {
      formModel.value.id = props.selectedUser.id;
      formModel.value.username = props.selectedUser.username;
      formModel.value.email = props.selectedUser.email;
      formModel.value.mobile = props.selectedUser.mobile;
    }
  });
</script>

<script lang="ts">
  export default {
    name: 'UserBaseInfo',
  };
</script>

<style lang="less" scoped>
  .user-base-info {
    &-wrapper {
      width: 320px;
    }

    &-title {
      color: var(--color-text-1);
      font-weight: 500;
      font-size: 24px;
      line-height: 32px;
    }

    &-sub-title {
      color: var(--color-text-3);
      font-size: 16px;
      line-height: 24px;
    }

    &-error-msg {
      height: 32px;
      color: rgb(var(--red-6));
      line-height: 32px;
    }

    &-password-actions {
      display: flex;
      justify-content: space-between;
    }
  }
</style>
