import localeMessageBox from '@/components/message-box/locale/zh-CN';
import localeLogin from '@/views/login/locale/zh-CN';
import localeRegister from '@/views/register/locale/zh-CN';
import localeKnowledge from '@/views/knowledge/locale/zh-CN';
import localeSuccess from '@/views/result/success/locale/zh-CN';
import localeError from '@/views/result/error/locale/zh-CN';
import localeUserSetting from '@/views/user/setting/locale/zh-CN';
import localeUserList from '@/views/user/list/locale/zh-CN';
import localeSettings from './zh-CN/settings';

export default {
  'app.name': 'WiseNet',
  'menu.knowledge': '知识库',
  'menu.api': 'API',
  'menu.api.swagger': 'Swagger',
  'menu.api.redoc': 'Redoc',
  'menu.list': '列表页',
  'menu.result': '结果页',
  'menu.exception': '异常页',
  'menu.form': '表单页',
  'menu.profile': '详情页',
  'menu.user': '个人中心',
  'menu.contact': '联系我们',
  'menu.doc': '文档中心',
  'menu.doc.md': 'Markdown',
  'menu.github': 'Github',
  'navbar.docs': '文档中心',
  'navbar.action.locale': '切换为中文',
  'Default': '默认',
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
