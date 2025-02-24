import axios from 'axios';
import type { RouteRecordNormalized } from 'vue-router';

export interface UserRecord {
  id: number | null;
  username: string;
  email: string;
  mobile: string;
  password: string;
  createTime: string | null;
  updateTime: string | null;
  role: string | null;
}

export interface UserParams {
  keyword: string;
  role: string;
  startTime: string;
  endTime: string;
  current: number | null;
  pageSize: number | null;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  password: string;
  email: string;
}

export interface LoginRes {
  token: string;
}

export interface UpdateUserPasswordRes {
  orgPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export function login(data: LoginData) {
  return axios.post<LoginRes>('/api/auth/login', data);
}

export function register(data: RegisterData) {
  return axios.post<LoginRes>('/api/auth/register', data);
}

export function logout() {
  return axios.post<LoginRes>('/api/auth/logout');
}

export function getUserInfo() {
  return axios.post<UserRecord>('/api/auth/info');
}

export function updateUserInfo(data: UserRecord) {
  return axios.put<UserRecord>('/api/auth/update', data);
}

export function updateUserPassword(data: UpdateUserPasswordRes) {
  return axios.put<UserRecord>('/api/auth/update/password', data);
}

export function getMenuList() {
  return axios.post<RouteRecordNormalized[]>('/api/auth/menu');
}

// for admin user
export function queryUserList(userParams: UserParams) {
  return axios.post('/api/user/list', userParams);
}

export function saveUser(data: UserRecord) {
  return axios.put('/api/user', data);
}

export function deleteUser(id: number) {
  return axios.delete(`/api/user/${id}`);
}
