import unittest
from utils import validate_url

class TestUtils(unittest.TestCase):
    def test_validate_url(self):
        self.assertTrue(validate_url("https://github.com/user/repo.git"))
        self.assertFalse(validate_url("https://example.com/repo.git"))

if __name__ == "__main__":
    unittest.main()