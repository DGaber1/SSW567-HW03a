import requests

BASE = "https://api.github.com"


def _fetch_json(url):
    resp = requests.get(url, timeout=10)
    if resp.status_code == 404:
        raise ValueError("Not found")
    if resp.status_code != 200:
        raise RuntimeError(f"GitHub API error: {resp.status_code}")
    return resp.json()


def get_repo_names(user_id):
    data = _fetch_json(f"{BASE}/users/{user_id}/repos?per_page=100")
    return [repo["name"] for repo in data]


def get_commit_count(user_id, repo):
    total, page = 0, 1
    while True:
        data = _fetch_json(f"{BASE}/repos/{user_id}/{repo}/commits?per_page=100&page={page}")
        total += len(data)
        if len(data) < 100:
            return total
        page += 1


def get_user_repo_commits(user_id):
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("user_id must be a non-empty string")
    return [(r, get_commit_count(user_id, r)) for r in get_repo_names(user_id)]


def format_output(results):
    return [f"Repo: {r} Number of commits: {c}" for r, c in results]


if __name__ == "__main__":
    uid = input("GitHub user ID: ")
    for line in format_output(get_user_repo_commits(uid)):
        print(line)
