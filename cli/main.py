#!/usr/bin/env python3
"""CLI 入口"""
import click
import os
from weekly_report import WeeklyReporter


@click.command()
@click.option("--days", default=7, help="统计天数")
@click.option("--output", default="weekly-report.md", help="输出文件")
def generate(days, output):
    """生成周报"""
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER", "z13972509570-spec")
    reporter = WeeklyReporter(token, owner)
    report = reporter.generate(days)
    with open(output, "w") as f:
        f.write(report.to_markdown())
    click.echo(f"✅ 周报已生成: {output}")


if __name__ == "__main__":
    generate()
