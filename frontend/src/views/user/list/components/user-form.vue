<template>
  <div class="container">
    <a-card class="general-card" :title="t('user.form')">
      <div class="user-form-error-msg">{{ errorMessage }}</div>
      <a-form :model="formModel" @submit="handleSubmit">
        <a-form-item
          field="username"
          :rules="[
            { required: true, message: t('user.form.username.placeholder') },
          ]"
          :validate-trigger="['change', 'blur']"
          hide-label
        >
          <a-input
            v-model="formModel.username"
            :placeholder="t('user.form.username.placeholder')"
          >
            <template #prefix>
              <icon-user />
            </template>
          </a-input>
        </a-form-item>
        <a-form-item
          field="email"
          :rules="[
            { required: true, message: t('user.form.email.placeholder') },
          ]"
          :validate-trigger="['change', 'blur']"
          hide-label
        >
          <a-input
            v-model="formModel.email"
            :placeholder="t('user.form.email.placeholder')"
          >
            <template #prefix>
              <icon-at />
            </template>
          </a-input>
        </a-form-item>
        <a-form-item
          field="mobile"
          :rules="[
            { required: false, message: t('user.form.mobile.placeholder') },
          ]"
          :validate-trigger="['change', 'blur']"
          hide-label
        >
          <a-input
            v-model="formModel.mobile"
            :placeholder="t('user.form.mobile.placeholder')"
          >
            <template #prefix>
              <icon-mobile />
            </template>
          </a-input>
        </a-form-item>
        <a-form-item
          v-if="userStore.selectedUser"
          field="password"
          :rules="[
            { required: false, message: t('user.form.password.placeholder') },
          ]"
          :validate-trigger="['change', 'blur']"
          hide-label
        >
          <a-input-password
            v-model="formModel.password"
            :placeholder="t('user.form.password.placeholder')"
            min-length="6"
            allow-clear
          >
            <template #prefix>
              <icon-lock />
            </template>
          </a-input-password>
        </a-form-item>
        <a-space :size="16" align="center">
          <a-button type="primary" html-type="submit" :loading="loading">
            {{ t('user.form.submit') }}
          </a-button>
          <a-button type="text" @click="handleCancel">
            {{ t('user.form.cancel') }}
          </a-button>
        </a-space>
      </a-form>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
  import { ref, watch, PropType, onMounted } from 'vue';
  import EventBus from '@/utils/event-bus';
  import { useI18n } from 'vue-i18n';
  import useLoading from '@/hooks/loading';
  import { useUserStore } from '@/store';
  import { UserRecord, saveUser } from '@/api/user';
  import { ValidatedError } from '@arco-design/web-vue/es/form/interface';
  import { Message } from '@arco-design/web-vue';
  import validateEmail from '@/utils/email';

  const userStore = useUserStore();

  const userFormModel = () => {
    return {
      id: '',
      username: '',
      email: '',
      mobile: '',
      password: '',
      confirmPassword: '',
    };
  };
  const { loading, setLoading } = useLoading(false);
  const { t } = useI18n();
  const errorMessage = ref('');
  const formModel = ref(userFormModel());

  const props = defineProps({
    selectedUser: {
      type: Object as PropType<UserRecord>,
      default: null,
    },
  });

  watch(
    () => props.selectedUser,
    () => {
      formModel.value.id = props.selectedUser?.id
        ? String(props.selectedUser.id)
        : '';
      formModel.value.username = props.selectedUser?.username;
      formModel.value.email = props.selectedUser?.email;
      formModel.value.mobile = props.selectedUser?.mobile;
    }
  );

  const handleSubmit = async ({
    errors,
    values,
  }: {
    errors: Record<string, ValidatedError> | undefined;
    values: Record<string, any>;
  }) => {
    if (loading.value) return;
    if (!errors) {
      if (
        userStore.selectedUser &&
        !formModel.value.id &&
        !formModel.value.password
      ) {
        errorMessage.value = t('user.form.password.empty.errMsg');
        return;
      }

      if (formModel.value.email && !validateEmail(formModel.value.email)) {
        errorMessage.value = t('user.form.email.invalid.errMsg');
        return;
      }

      errorMessage.value = '';
      setLoading(true);
      const userToSave: UserRecord = {
        id: formModel.value.id ? Number(formModel.value.id) : null,
        username: formModel.value.username,
        email: formModel.value.email,
        mobile: formModel.value.mobile,
        password: formModel.value.password,
        createTime: new Date().toISOString(),
        updateTime: new Date().toISOString(),
        role: '',
      };
      saveUser(userToSave)
        .then((response) => {
          const { data } = response;
          if (data) {
            EventBus.emit('saved_user');
          }
          userStore.selectedUser = undefined;
          formModel.value = userFormModel();
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

  const handleCancel = () => {
    userStore.selectedUser = undefined;
    formModel.value = userFormModel();
  };

  onMounted(() => {
    if (props.selectedUser) {
      formModel.value.id = props.selectedUser?.id
        ? String(props.selectedUser.id)
        : '';
      formModel.value.username = props.selectedUser?.username;
      formModel.value.email = props.selectedUser?.email;
      formModel.value.mobile = props.selectedUser?.mobile;
    }
  });
</script>

<script lang="ts">
  export default {
    name: 'UserForm',
  };
</script>

<style lang="less" scoped>
  .user-form {
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
