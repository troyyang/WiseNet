<template>
  <div class="container">
    <a-card class="general-card" :title="t('userSetting.tab.securitySettings')">
      <div class="user-form-error-msg">{{ errorMessage }}</div>
      <a-form :model="formModel" @submit="handleSubmit">
        <a-form-item
          field="orgPassword"
          :label="t('userSetting.securitySettings.orgPassword.label')"
          :rules="[
            {
              required: true,
              message: t(
                'userSetting.securitySettings.orgPassword.placeholder'
              ),
            },
          ]"
          :validate-trigger="['change', 'blur']"
        >
          <a-input-password
            v-model="formModel.orgPassword"
            :placeholder="
              t('userSetting.securitySettings.orgPassword.placeholder')
            "
            allow-clear
          >
            <template #prefix>
              <icon-lock />
            </template>
          </a-input-password>
        </a-form-item>
        <a-form-item
          field="newPassword"
          :label="t('userSetting.securitySettings.newPassword.label')"
          :rules="[
            {
              required: true,
              message: t(
                'userSetting.securitySettings.newPassword.placeholder'
              ),
            },
          ]"
          :validate-trigger="['change', 'blur']"
        >
          <a-input-password
            v-model="formModel.newPassword"
            :placeholder="
              t('userSetting.securitySettings.newPassword.placeholder')
            "
            min-length="6"
            allow-clear
          >
            <template #prefix>
              <icon-lock />
            </template>
          </a-input-password>
        </a-form-item>
        <a-form-item
          field="confirmPassword"
          :label="t('userSetting.securitySettings.confirmPassword.label')"
          :rules="[
            {
              required: true,
              message: t(
                'userSetting.securitySettings.confirmPassword.placeholder'
              ),
            },
          ]"
          :validate-trigger="['change', 'blur']"
        >
          <a-input-password
            v-model="formModel.confirmPassword"
            :placeholder="
              t('userSetting.securitySettings.confirmPassword.placeholder')
            "
            min-length="6"
            allow-clear
          >
            <template #prefix>
              <icon-safe />
            </template>
          </a-input-password>
        </a-form-item>
        <a-form-item>
          <a-space :size="16" align="center">
            <a-button type="primary" html-type="submit" :loading="loading">
              {{ t('userSetting.securitySettings.submit') }}
            </a-button>
            <a-button type="text" @click="handleReset">
              {{ t('userSetting.securitySettings.reset') }}
            </a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { useI18n } from 'vue-i18n';
  import useLoading from '@/hooks/loading';
  import { updateUserPassword } from '@/api/user';
  import { ValidatedError } from '@arco-design/web-vue/es/form/interface';
  import { Message } from '@arco-design/web-vue';

  const userFormModel = () => {
    return {
      newPassword: '',
      confirmPassword: '',
      orgPassword: '',
    };
  };
  const { loading, setLoading } = useLoading(false);
  const { t } = useI18n();
  const errorMessage = ref('');
  const formModel = ref(userFormModel());

  const handleSubmit = async ({
    errors,
    values,
  }: {
    errors: Record<string, ValidatedError> | undefined;
    values: Record<string, any>;
  }) => {
    if (loading.value) return;
    if (!errors) {
      if (formModel.value.orgPassword === formModel.value.newPassword) {
        errorMessage.value = t(
          'userSetting.securitySettings.newPassword.duplicate.errMsg'
        );
        return;
      }
      if (formModel.value.newPassword !== formModel.value.confirmPassword) {
        errorMessage.value = t(
          'userSetting.securitySettings.confirmPassword.duplicate.errMsg'
        );
        return;
      }

      errorMessage.value = '';
      setLoading(true);
      updateUserPassword(formModel.value)
        .then(() => {
          formModel.value = userFormModel();
          Message.success(t('userSetting.securitySettings.update.success'));
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
    formModel.value = userFormModel();
  };
</script>

<script lang="ts">
  export default {
    name: 'SecuritySettings',
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
