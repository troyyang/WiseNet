import localeMessageBox from '@/components/message-box/locale/en-US';
import localeLogin from '@/views/login/locale/en-US';
import localeRegister from '@/views/register/locale/en-US';
import localeKnowledge from '@/views/knowledge/locale/en-US';

import localeSuccess from '@/views/result/success/locale/en-US';
import localeError from '@/views/result/error/locale/en-US';

import localeUserList from '@/views/user/list/locale/en-US';
import localeUserSetting from '@/views/user/setting/locale/en-US';

import localeSettings from './en-US/settings';

export default {
  'app.name': 'WiseNet',
  'menu.knowledge': 'Knowledge',
  'menu.api': 'API',
  'menu.api.swagger': 'Swagger',
  'menu.api.redoc': 'Redoc',
  'menu.list': 'List',
  'menu.result': 'Result',
  'menu.exception': 'Exception',
  'menu.form': 'Form',
  'menu.profile': 'Profile',
  'menu.user': 'User Center',
  'menu.contact': 'Contact',
  'menu.doc': 'Docs',
  'menu.doc.md': 'Markdown',
  'menu.github': 'Github',

  'navbar.docs': 'Docs',
  'navbar.action.locale': 'Switch to English',
  'Default': 'Default',
  ...localeSettings,
  ...localeMessageBox,
  ...localeLogin,
  ...localeRegister,
  ...localeKnowledge,
  ...localeSuccess,
  ...localeError,
  ...localeUserList,
  ...localeUserSetting,
};
