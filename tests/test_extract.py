import unittest
from extract_github import extract_repo

class TestExtractGithub(unittest.TestCase):
    def test_valid_repo(self):
        result = extract_repo("https://github.com/user/sample-repo.git")
        self.assertTrue("Extraction complete" in result)

if __name__ == "__main__":
    unittest.main()