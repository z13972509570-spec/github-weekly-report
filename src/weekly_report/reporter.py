"""报告生成器"""
import uuid
from datetime import datetime, timedelta
from typing import List
from .models import WeeklyReport, RepositoryStats, RiskItem
from .fetcher import GitHubFetcher
from .analyzer import RiskAnalyzer


class WeeklyReporter:
    def __init__(self, token: str, owner: str):
        self.fetcher = GitHubFetcher(token, owner)
        self.analyzer = RiskAnalyzer()

    def generate(self, days: int = 7) -> WeeklyReport:
        """生成周报"""
        repos = self.fetcher.get_repos()
        repo_stats = []
        all_risks = []

        for repo in repos:
            stats = self.fetcher.get_commit_stats(repo, days)
            repo_stats.append(RepositoryStats(
                name=repo,
                commits=stats["commits"],
                contributors=stats["authors"]
            ))

        return WeeklyReport(
            report_id=f"report-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}",
            generated_at=datetime.now().isoformat(),
            period_start=(datetime.now() - timedelta(days=days)).isoformat(),
            period_end=datetime.now().isoformat(),
            repositories=repo_stats,
            risks=all_risks,
            total_commits=sum(r.commits for r in repo_stats),
            total_changes=len(repo_stats)
        )
