export type RoleType = '' | '*' | 'ADMIN' | 'USER';
import { UserRecord } from '@/api/user';
export interface UserState {
  currentUser: UserRecord;
  selectedUser?: UserRecord;
}
