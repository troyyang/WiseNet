import { defineStore } from 'pinia';
import {
  login as userLogin,
  logout as userLogout,
  getUserInfo,
  LoginData,
  register as userRegister,
  RegisterData,
  UserRecord,
} from '@/api/user';
import { setToken, clearToken } from '@/utils/auth';
import { removeRouteListener } from '@/utils/route-listener';
import { UserState } from './types';
import useAppStore from '../app';

const useUserStore = defineStore('user', {
  state: (): UserState => ({
    currentUser: {} as UserRecord,
    selectedUser: undefined,
  }),

  getters: {
    userInfo(state: UserState): UserState {
      return { ...state };
    },
  },

  actions: {
    switchRoles() {
      return new Promise((resolve) => {
        this.currentUser.role =
          this.currentUser.role === 'user' ? 'admin' : 'user';
        resolve(this.currentUser.role);
      });
    },
    // Set user's information
    setUserState(partial: Partial<UserState>) {
      this.$patch(partial);
    },

    // Reset user's information
    resetInfo() {
      this.$reset();
    },

    // Get user's information
    async info() {
      getUserInfo()
        .then((response) => {
          const { data } = response;
          this.setUserState({ currentUser: data as UserRecord });
        })
        .catch((error) => {
          console.log(error);
        });
    },

    setSelectedUser(user: UserRecord) {
      this.setUserState({ selectedUser: user });
    },

    // Login
    async login(loginForm: LoginData) {
      try {
        const response = await userLogin(loginForm);
        const { data } = response;
        setToken(data.token);
      } catch (err) {
        clearToken();
        throw err;
      }
    },
    // Register
    async register(registerForm: RegisterData) {
      try {
        const response = await userRegister(registerForm);
        setToken(response.data.token);
      } catch (err) {
        clearToken();
        throw err;
      }
    },
    logoutCallBack() {
      const appStore = useAppStore();
      this.resetInfo();
      clearToken();
      removeRouteListener();
      appStore.clearServerMenu();
    },
    // Logout
    async logout() {
      try {
        await userLogout();
      } finally {
        this.logoutCallBack();
      }
    },
  },
});

export default useUserStore;
