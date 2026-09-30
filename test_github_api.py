import unittest
from unittest.mock import patch
import github_api as g


class TestGitHubApi(unittest.TestCase):
    @patch("github_api._fetch_json")
    def test_repo_names(self, m):
        m.return_value = [{"name": "A"}, {"name": "B"}]
        self.assertEqual(g.get_repo_names("bob"), ["A", "B"])

    @patch("github_api._fetch_json")
    def test_no_repos(self, m):
        m.return_value = []
        self.assertEqual(g.get_user_repo_commits("bob"), [])

    @patch("github_api._fetch_json")
    def test_commit_count_pagination(self, m):
        m.side_effect = [[{}] * 100, [{}] * 5]
        self.assertEqual(g.get_commit_count("bob", "A"), 105)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            g.get_user_repo_commits("")

    def test_format_output(self):
        self.assertEqual(g.format_output([("A", 3)]),
                         ["Repo: A Number of commits: 3"])


if __name__ == "__main__":
    unittest.main()
