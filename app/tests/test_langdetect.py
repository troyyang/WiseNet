import unittest
from ai.nlp import detect_language

class TestLangDetect(unittest.TestCase):
    def test_detect_en(self):
        text = "Barack Obama visited San Francisco last Thursday to attend a conference on artificial intelligence at Stanford University."
        language = detect_language(text)
        assert language == 'en'

    def test_detect_zh_simplified(self):
        text = "巴拉克·奥巴马上周四访问了旧金山，参加在斯坦福大学举行的人工智能会议。"
        language = detect_language(text)
        assert language == 'zh'

    def test_detect_zh_traditional(self):
        text = "巴拉克·歐巴馬週四訪問了舊金山，參加了在史丹佛大學舉行的人工智慧會議。"
        language = detect_language(text)
        assert language == 'zh'

if __name__ == '__main__':
    unittest.main()

