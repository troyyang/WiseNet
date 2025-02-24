import logging
import unittest
from core.security import hash_password_md5

logging.basicConfig(level=logging.INFO)


class TestSecurity(unittest.TestCase):
    def test_hash_password_md5(self):
        password = "123456"
        expected_hash = "e10adc3949ba59abbe56e057f20f883e"  # MD5 hash for '123456'
        self.assertEqual(hash_password_md5(password), expected_hash)

    def test_hash_password_md5_admin(self):
        password = "admin"
        expected_hash = "21232f297a57a5a743894a0e4a801fc3"  # MD5 hash for 'admin'
        self.assertEqual(hash_password_md5(password), expected_hash)


    def test_hash_password_md5_empty_string(self):
        password = ""
        expected_hash = "d41d8cd98f00b204e9800998ecf8427e"  # MD5 hash for empty string
        self.assertEqual(hash_password_md5(password), expected_hash)


if __name__ == '__main__':
    unittest.main()