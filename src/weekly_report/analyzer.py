"""风险分析器"""
import re
from typing import List
from datetime import datetime
from .models import RiskItem, RiskLevel, RiskCategory


class RiskAnalyzer:
    """风险分析器"""
    
    # 高风险模式
    CRITICAL_PATTERNS = [
        (r'password|passwd|pwd', RiskCategory.SECURITY, "发现硬编码密码"),
        (r'api[_-]?key|apikey|secret|token', RiskCategory.SECURITY, "发现硬编码 API Key/Token"),
        (r'eval\(|exec\(|os\.system', RiskCategory.SECURITY, "发现危险函数调用"),
        (r'sql\s*\+|execute\(|cursor\.execute', RiskCategory.SECURITY, "可能存在 SQL 注入风险"),
    ]
    
    # 中风险模式
    HIGH_PATTERNS = [
        (r'import\s+(os|sys|subprocess)', RiskCategory.CODE_QUALITY, "导入系统级模块"),
        (r'TODO|FIXME|XXX|HACK', RiskCategory.CODE_QUALITY, "存在未完成代码标记"),
        (r'print\(|logging\.info', RiskCategory.CODE_QUALITY, "可能存在调试代码"),
        (r'raise\s+NotImplementedError', RiskCategory.CODE_QUALITY, "存在未实现功能"),
    ]
    
    # 低风险模式
    MEDIUM_PATTERNS = [
        (r'#.*deprecated', RiskCategory.CODE_QUALITY, "使用已废弃 API"),
        (r'assert\s+', RiskCategory.CODE_QUALITY, "生产代码中使用 assert"),
        (r'time\.sleep\(', RiskCategory.PERFORMANCE, "存在同步延迟"),
    ]
    
    # 破坏性变更关键词
    BREAKING_KEYWORDS = [
        'breaking', 'breaking change', '破坏性', '不兼容',
        'remove', 'delete', 'deprecate',
        'rename', 'refactor api'
    ]

    def __init__(self):
        pass
    
    def analyze_file(self, filename: str, content: str) -> List[RiskItem]:
        """分析单个文件的风险"""
        risks = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查高风险
            for pattern, category, desc in self.CRITICAL_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    risks.append(RiskItem(
                        id=f"risk-{filename}-{i}",
                        level=RiskLevel.CRITICAL,
                        category=category,
                        title=desc,
                        description=f"在 {filename}:{i} 发现: {line.strip()[:80]}",
                        file=filename,
                        line=i,
                        suggestion=self._get_suggestion(category),
                        evidence=line.strip()
                    ))
            
            # 检查中风险
            for pattern, category, desc in self.HIGH_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    risks.append(RiskItem(
                        id=f"risk-{filename}-{i}",
                        level=RiskLevel.HIGH,
                        category=category,
                        title=desc,
                        description=f"在 {filename}:{i}",
                        file=filename,
                        line=i,
                        suggestion=self._get_suggestion(category),
                        evidence=line.strip()[:80]
                    ))
        
        return risks
    
    def analyze_commit_message(self, message: str) -> List[RiskItem]:
        """分析提交信息"""
        risks = []
        msg_lower = message.lower()
        
        # 检查破坏性变更
        for keyword in self.BREAKING_KEYWORDS:
            if keyword in msg_lower:
                risks.append(RiskItem(
                    id=f"risk-commit-{hash(message)}",
                    level=RiskLevel.MEDIUM,
                    category=RiskCategory.BREAKING_CHANGE,
                    title="破坏性变更",
                    description=f"提交包含破坏性变更关键词: {keyword}",
                    suggestion="检查变更是否需要版本升级说明",
                    evidence=message[:100]
                ))
                break
        
        return risks
    
    def _get_suggestion(self, category: RiskCategory) -> str:
        """获取风险建议"""
        suggestions = {
            RiskCategory.SECURITY: "使用环境变量或密钥管理服务，避免硬编码",
            RiskCategory.DEPENDENCY: "检查依赖版本，考虑升级或替换",
            RiskCategory.CODE_QUALITY: "重构代码，移除调试代码，添加文档",
            RiskCategory.PERFORMANCE: "考虑异步处理或缓存优化",
            RiskCategory.DOCUMENTATION: "补充或更新相关文档",
            RiskCategory.BREAKING_CHANGE: "在 CHANGELOG 中记录变更",
        }
        return suggestions.get(category, "建议人工审查")
    
    def prioritize_risks(self, risks: List[RiskItem]) -> List[RiskItem]:
        """按风险等级排序"""
        return sorted(risks, key=lambda r: (
            0 if r.level == RiskLevel.CRITICAL else
            1 if r.level == RiskLevel.HIGH else
            2 if r.level == RiskLevel.MEDIUM else 3
        ))
