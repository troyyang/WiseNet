import unittest
from core.i18n import _, set_locale

class TestI18n(unittest.TestCase):
    def test_en(self):
        text = _("Invalid token")
        assert text == "Invalid Token"

    def test_zh(self):
        set_locale("zh_CN")
        text = _("Invalid token")
        assert text == "无效令牌"

    def test_multi_line_text_en(self):
        text = _("Content prompt template")
        assert text == "{input}\nPlease generate a description based on the above information. The word count is limited to 300 words."

    def test_multi_line_text_zh(self):
        set_locale("zh_CN")
        text = _("Content prompt template")
        assert text == "{input}\n请根据以上信息，生成一段描述信息，字数限制在300个以内，输出语言限定为[中文]。"

if __name__ == '__main__':
    unittest.main()
