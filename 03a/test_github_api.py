import unittest
from unittest.mock import patch, Mock

import github_api as g


def fake_response(status=200, data=None):
    """Build a fake requests response so no real network call is made."""
    resp = Mock()
    resp.status_code = status
    resp.json.return_value = data if data is not None else []
    return resp


class TestGitHubApiMocked(unittest.TestCase):

    @patch("github_api.requests.get")
    def test_repo_names(self, mock_get):
        mock_get.return_value = fake_response(
            200, [{"name": "Triangle567"}, {"name": "Square567"}])
        self.assertEqual(g.get_repo_names("john567"),
                         ["Triangle567", "Square567"])
        mock_get.assert_called_once_with(
            "https://api.github.com/users/john567/repos?per_page=100",
            timeout=10)

    @patch("github_api.requests.get")
    def test_no_repos(self, mock_get):
        mock_get.return_value = fake_response(200, [])
        self.assertEqual(g.get_user_repo_commits("john567"), [])

    @patch("github_api.requests.get")
    def test_commit_count_single_page(self, mock_get):
        mock_get.return_value = fake_response(200, [{}] * 10)
        self.assertEqual(g.get_commit_count("john567", "Triangle567"), 10)

    @patch("github_api.requests.get")
    def test_commit_count_pagination(self, mock_get):
        mock_get.side_effect = [fake_response(200, [{}] * 100),
                                fake_response(200, [{}] * 5)]
        self.assertEqual(g.get_commit_count("john567", "Triangle567"), 105)
        self.assertEqual(mock_get.call_count, 2)

    @patch("github_api.requests.get")
    def test_full_flow(self, mock_get):
        mock_get.side_effect = [
            fake_response(200, [{"name": "Triangle567"}, {"name": "Square567"}]),
            fake_response(200, [{}] * 10),
            fake_response(200, [{}] * 27),
        ]
        results = g.get_user_repo_commits("john567")
        self.assertEqual(results, [("Triangle567", 10), ("Square567", 27)])
        self.assertEqual(g.format_output(results),
                         ["Repo: Triangle567 Number of commits: 10",
                          "Repo: Square567 Number of commits: 27"])

    @patch("github_api.requests.get")
    def test_user_not_found(self, mock_get):
        mock_get.return_value = fake_response(404)
        with self.assertRaises(ValueError):
            g.get_repo_names("nosuchuser")

    @patch("github_api.requests.get")
    def test_server_error(self, mock_get):
        mock_get.return_value = fake_response(500)
        with self.assertRaises(RuntimeError):
            g.get_repo_names("john567")

    @patch("github_api.requests.get")
    def test_rate_limit(self, mock_get):
        mock_get.return_value = fake_response(403)
        with self.assertRaises(RuntimeError):
            g.get_repo_names("john567")

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            g.get_user_repo_commits("")

    def test_format_output(self):
        self.assertEqual(g.format_output([("A", 3)]),
                         ["Repo: A Number of commits: 3"])


if __name__ == "__main__":
    unittest.main()
    