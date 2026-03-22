"""GitHub API 数据抓取"""
import httpx
from typing import List, Optional
from datetime import datetime, timedelta
from .models import Commit, Change, RepositoryStats


class GitHubFetcher:
    def __init__(self, token: str, owner: str):
        self.token = token
        self.owner = owner
        self.client = httpx.Client(headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json"
        })

    def get_repos(self) -> List[str]:
        """获取所有仓库"""
        repos = []
        page = 1
        while True:
            resp = self.client.get(
                f"https://api.github.com/users/{self.owner}/repos",
                params={"per_page": 100, "page": page, "type": "all"}
            )
            data = resp.json()
            if not data:
                break
            repos.extend([r["name"] for r in data])
            page += 1
        return repos

    def get_commit_stats(self, repo: str, days: int = 7) -> dict:
        """获取提交统计"""
        since = (datetime.now() - timedelta(days=days)).isoformat()
        resp = self.client.get(
            f"https://api.github.com/repos/{self.owner}/{repo}/commits",
            params={"since": since, "per_page": 100}
        )
        commits = resp.json() or []
        return {
            "commits": len(commits),
            "authors": list(set(c["commit"]["author"]["name"] for c in commits if c["commit"].get("author")))
        }
