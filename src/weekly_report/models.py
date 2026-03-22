"""数据模型"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """风险等级"""
    CRITICAL = "CRITICAL"   # 严重
    HIGH = "HIGH"          # 高
    MEDIUM = "MEDIUM"      # 中
    LOW = "LOW"            # 低


class RiskCategory(str, Enum):
    """风险类别"""
    SECURITY = "SECURITY"          # 安全
    DEPENDENCY = "DEPENDENCY"     # 依赖
    CODE_QUALITY = "CODE_QUALITY"  # 代码质量
    PERFORMANCE = "PERFORMANCE"   # 性能
    DOCUMENTATION = "DOCUMENTATION" # 文档
    BREAKING_CHANGE = "BREAKING"   # 破坏性变更


class RiskItem(BaseModel):
    """风险项"""
    id: str
    level: RiskLevel
    category: RiskCategory
    title: str
    description: str
    file: Optional[str] = None
    line: Optional[int] = None
    suggestion: str
    evidence: str = ""


class Commit(BaseModel):
    """提交"""
    sha: str
    message: str
    author: str
    date: str
    additions: int = 0
    deletions: int = 0


class Change(BaseModel):
    """变更"""
    file: str
    additions: int
    deletions: int
    status: str  # added, modified, deleted


class RepositoryStats(BaseModel):
    """仓库统计"""
    name: str
    commits: int = 0
    additions: int = 0
    deletions: int = 0
    files_changed: int = 0
    contributors: List[str] = Field(default_factory=list)
    active_branches: List[str] = Field(default_factory=list)


class WeeklyReport(BaseModel):
    """周报"""
    report_id: str
    generated_at: str
    period_start: str
    period_end: str
    repositories: List[RepositoryStats] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    total_commits: int = 0
    total_changes: int = 0

    def to_markdown(self) -> str:
        """生成 Markdown 报告"""
        date = datetime.now().strftime("%Y-%m-%d")
        
        md = f"""# 📊 GitHub 每周报告

**生成时间**: {date}  
**统计周期**: {self.period_start} ~ {self.period_end}

---

## 📈 代码改动统计

| 指标 | 数值 |
|------|------|
| 📝 总提交数 | {self.total_commits} |
| 📝 文件变更 | {self.total_changes} |
| ➕ 代码增加 | {sum(r.additions for r in self.repositories):,} 行 |
| ➖ 代码删除 | {sum(r.deletions for r in self.repositories):,} 行 |

### 仓库详情

| 仓库 | 提交 | 文件变更 | 增加 | 删除 |
|------|------|----------|------|------|
"""
        for repo in self.repositories:
            md += f"| {repo.name} | {repo.commits} | {repo.files_changed} | +{repo.additions:,} | -{repo.deletions:,} |\n"

        # 风险清单
        md += f"""

---

## 🚨 风险清单

"""
        
        # 按等级分组
        critical = [r for r in self.risks if r.level == RiskLevel.CRITICAL]
        high = [r for r in self.risks if r.level == RiskLevel.HIGH]
        medium = [r for r in self.risks if r.level == RiskLevel.MEDIUM]
        
        if critical:
            md += "### 🔴 严重风险 ({})\n\n".format(len(critical))
            for r in critical:
                md += f"- **{r.title}**\n  - {r.description}\n  - 📁 {r.file or 'N/A'}\n  - 💡 {r.suggestion}\n\n"
        
        if high:
            md += "### 🟠 高风险 ({})\n\n".format(len(high))
            for r in high:
                md += f"- **{r.title}**\n  - {r.description}\n  - 💡 {r.suggestion}\n\n"
        
        if medium:
            md += "### 🟡 中风险 ({})\n\n".format(len(medium))
            for r in medium[:5]:  # 只显示前5个
                md += f"- {r.title}: {r.description[:60]}...\n"
        
        if not self.risks:
            md += "*暂无风险识别*\n"

        # 审查重点
        md += """

---

## 🔍 审查重点建议

### 1. 需要优先审查的变更
"""
        # 找出变更最多的仓库
        if self.repositories:
            top_repo = max(self.repositories, key=lambda r: r.commits)
            md += f"- **{top_repo.name}** - 本周提交最多 ({top_repo.commits} 次)\n"
        
        # 找出删除较多的文件
        deleted = []
        for repo in self.repositories:
            # 简化处理
            pass
        
        md += """
### 2. 建议关注点
- 检查新增的依赖是否安全
- 验证破坏性变更的影响范围
- 确保关键功能有测试覆盖

---

*由 AI Weekly Reporter 自动生成*
"""
        return md
