import axios from 'axios';
import type { AxiosRequestConfig, AxiosResponse } from 'axios';
import { Message, Modal } from '@arco-design/web-vue';
import { useUserStore } from '@/store';
import { getToken } from '@/utils/auth';
import i18n from '@/locale'; // ✅ Import global i18n instance

const TOKEN_ERROR_CODES = [50008, 50012, 50014];

export interface HttpResponse<T = unknown> {
  status: number;
  msg: string;
  code: number;
  data: T;
}

if (import.meta.env.VITE_API_BASE_URL) {
  axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL;
}

axios.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    if (!config.headers) {
      config.headers = {};
    }

    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    const currentLocale = i18n.global.locale.value; // ✅ Use global locale
    config.headers['accept-language'] = currentLocale || 'en-US';
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

axios.interceptors.response.use(
  (response: AxiosResponse<HttpResponse>) => {

    const res = response.data;
    if (typeof res === 'string') {
      return res;
    }

    if (typeof res !== 'string' && res.code !== 0) {
      Message.error({
        content: res.msg || i18n.global.t('requestError'), // ✅ Use global translation
        duration: 5 * 1000,
      });

      if (
        TOKEN_ERROR_CODES.includes(res.code) &&
        response.config.url !== '/api/auth/info'
      ) {
        Modal.error({
          title: i18n.global.t('confirmLogoutTitle'), // ✅ Use global translation
          content: i18n.global.t('confirmLogoutContent'),
          okText: i18n.global.t('reLogin'),
          async onOk() {
            const userStore = useUserStore();
            await userStore.logout();
            window.location.reload();
          },
        });
      }
      return Promise.reject(new Error(res.msg || i18n.global.t('requestError')));
    }
    return res;
  },
  (error) => {
    Message.error({
      content:
        error.response?.data?.detail ||
        error.response?.data?.msg ||
        error.message ||
        i18n.global.t('requestError'), // ✅ Use global translation
      duration: 5 * 1000,
    });
    return Promise.reject(error);
  }
);

// Export the configured axios instance
export default axios;
