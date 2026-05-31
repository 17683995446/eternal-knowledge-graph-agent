
"""
领域知识质量评估与优化系统 - 阶段36
支持知识质量评分、完整性检查、冗余检测和优化建议
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
from collections import Counter

from core.domain_knowledge_manager import DomainKnowledge, DomainType, KnowledgeTemplate


class QualityLevel(Enum):
    """质量等级"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class QualityReport:
    """质量报告"""
    knowledge_id: str
    overall_score: float
    quality_level: QualityLevel
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    freshness_score: float
    issues: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    evaluated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class QualityMetrics:
    """质量指标"""
    total_knowledges: int
    avg_quality_score: float
    quality_distribution: Dict[str, int]
    completeness_avg: float
    accuracy_avg: float
    consistency_avg: float
    freshness_avg: float
    top_issues: List[Dict[str, Any]]


class DomainKnowledgeQuality:
    """领域知识质量管理器"""
    
    def __init__(self, domain_manager):
        self.domain_manager = domain_manager
        self.quality_reports: Dict[str, QualityReport] = {}
        
        self.data_dir = Path("data/quality")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self._load_reports()
    
    def _load_reports(self):
        """加载质量报告"""
        reports_file = self.data_dir / "quality_reports.json"
        if reports_file.exists():
            try:
                with open(reports_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for r_data in data.get("reports", []):
                    report = QualityReport(
                        knowledge_id=r_data["knowledge_id"],
                        overall_score=r_data["overall_score"],
                        quality_level=QualityLevel(r_data["quality_level"]),
                        completeness_score=r_data["completeness_score"],
                        accuracy_score=r_data["accuracy_score"],
                        consistency_score=r_data["consistency_score"],
                        freshness_score=r_data["freshness_score"],
                        issues=r_data.get("issues", []),
                        suggestions=r_data.get("suggestions", []),
                        evaluated_at=r_data.get("evaluated_at")
                    )
                    self.quality_reports[report.knowledge_id] = report
            except Exception as e:
                print(f"加载质量报告失败: {e}")
    
    def _save_reports(self):
        """保存质量报告"""
        reports_file = self.data_dir / "quality_reports.json"
        data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "reports": []
        }
        for report in self.quality_reports.values():
            data["reports"].append({
                "knowledge_id": report.knowledge_id,
                "overall_score": report.overall_score,
                "quality_level": report.quality_level.value,
                "completeness_score": report.completeness_score,
                "accuracy_score": report.accuracy_score,
                "consistency_score": report.consistency_score,
                "freshness_score": report.freshness_score,
                "issues": report.issues,
                "suggestions": report.suggestions,
                "evaluated_at": report.evaluated_at
            })
        try:
            with open(reports_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存质量报告失败: {e}")
    
    def evaluate_knowledge(self, knowledge_id: str) -> Optional[QualityReport]:
        """
        评估知识质量
        
        Args:
            knowledge_id: 知识ID
        
        Returns:
            质量报告
        """
        knowledge = self.domain_manager.get_domain_knowledge(knowledge_id)
        if not knowledge:
            print(f"知识 {knowledge_id} 不存在")
            return None
        
        issues = []
        suggestions = []
        
        # 1. 完整性评估
        completeness_score = self._evaluate_completeness(knowledge, issues, suggestions)
        
        # 2. 准确性评估
        accuracy_score = self._evaluate_accuracy(knowledge, issues, suggestions)
        
        # 3. 一致性评估
        consistency_score = self._evaluate_consistency(knowledge, issues, suggestions)
        
        # 4. 新鲜度评估
        freshness_score = self._evaluate_freshness(knowledge, issues, suggestions)
        
        # 计算总分
        overall_score = (
            completeness_score * 0.3 +
            accuracy_score * 0.25 +
            consistency_score * 0.25 +
            freshness_score * 0.2
        )
        
        # 确定质量等级
        quality_level = self._get_quality_level(overall_score)
        
        report = QualityReport(
            knowledge_id=knowledge_id,
            overall_score=round(overall_score, 2),
            quality_level=quality_level,
            completeness_score=round(completeness_score, 2),
            accuracy_score=round(accuracy_score, 2),
            consistency_score=round(consistency_score, 2),
            freshness_score=round(freshness_score, 2),
            issues=issues,
            suggestions=suggestions
        )
        
        self.quality_reports[knowledge_id] = report
        self._save_reports()
        
        return report
    
    def _evaluate_completeness(self, knowledge: DomainKnowledge, 
                               issues: List[Dict], suggestions: List[str]) -> float:
        """评估完整性"""
        score = 1.0
        
        # 检查必填字段
        template = self.domain_manager.get_template(
            knowledge.knowledge_id.split('_')[0]
        )
        if template:
            missing_fields = []
            for field in template.required_fields:
                if field not in knowledge.content or not knowledge.content[field]:
                    missing_fields.append(field)
            
            if missing_fields:
                score -= len(missing_fields) * 0.2
                issues.append({
                    "type": "completeness",
                    "severity": "high",
                    "message": f"缺少必填字段: {', '.join(missing_fields)}"
                })
                suggestions.append(f"补充以下字段: {', '.join(missing_fields)}")
        
        # 检查标签
        if not knowledge.tags:
            score -= 0.15
            issues.append({
                "type": "completeness",
                "severity": "medium",
                "message": "缺少标签"
            })
            suggestions.append("添加相关标签以便分类和搜索")
        
        # 检查来源
        if not knowledge.sources:
            score -= 0.1
            issues.append({
                "type": "completeness",
                "severity": "low",
                "message": "缺少来源信息"
            })
            suggestions.append("添加知识来源以提高可信度")
        
        return max(score, 0.0)
    
    def _evaluate_accuracy(self, knowledge: DomainKnowledge,
                          issues: List[Dict], suggestions: List[str]) -> float:
        """评估准确性"""
        score = knowledge.confidence
        
        # 检查内容长度
        content_str = json.dumps(knowledge.content, ensure_ascii=False)
        if len(content_str) < 50:
            score -= 0.1
            issues.append({
                "type": "accuracy",
                "severity": "medium",
                "message": "内容过于简短，可能不够详细"
            })
            suggestions.append("补充更多详细信息")
        
        # 检查名称有效性
        if len(knowledge.name) < 3:
            score -= 0.1
            issues.append({
                "type": "accuracy",
                "severity": "medium",
                "message": "知识名称过短"
            })
            suggestions.append("使用更具描述性的名称")
        
        return max(score, 0.0)
    
    def _evaluate_consistency(self, knowledge: DomainKnowledge,
                             issues: List[Dict], suggestions: List[str]) -> float:
        """评估一致性"""
        score = 1.0
        
        # 检查标签与领域类型一致性
        domain_type = knowledge.domain_type.value
        tag_domain_map = {
            "technology": ["技术", "编程", "软件", "硬件", "网络"],
            "healthcare": ["医疗", "健康", "疾病", "药物", "治疗"],
            "education": ["教育", "学习", "课程", "学校", "教学"],
            "finance": ["金融", "经济", "投资", "银行", "货币"],
            "legal": ["法律", "法规", "合同", "诉讼", "权利"],
            "science": ["科学", "研究", "实验", "理论", "发现"],
            "language": ["语言", "词汇", "语法", "翻译", "文学"]
        }
        
        expected_tags = tag_domain_map.get(domain_type, [])
        if expected_tags:
            has_domain_tag = any(tag in expected_tags for tag in knowledge.tags)
            if not has_domain_tag:
                score -= 0.15
                issues.append({
                    "type": "consistency",
                    "severity": "low",
                    "message": f"标签与领域类型 '{domain_type}' 不一致"
                })
                suggestions.append(f"添加与 '{domain_type}' 领域相关的标签")
        
        # 检查内容格式一致性
        content = knowledge.content
        for key, value in content.items():
            if isinstance(value, list) and len(value) == 0:
                score -= 0.05
                issues.append({
                    "type": "consistency",
                    "severity": "low",
                    "message": f"字段 '{key}' 为空列表"
                })
        
        return max(score, 0.0)
    
    def _evaluate_freshness(self, knowledge: DomainKnowledge,
                           issues: List[Dict], suggestions: List[str]) -> float:
        """评估新鲜度"""
        score = 1.0
        
        try:
            updated = datetime.fromisoformat(knowledge.updated_at)
            days_since_update = (datetime.now() - updated).days
            
            if days_since_update > 365:
                score -= 0.3
                issues.append({
                    "type": "freshness",
                    "severity": "high",
                    "message": f"知识已 {days_since_update} 天未更新"
                })
                suggestions.append("更新知识内容以保持时效性")
            elif days_since_update > 180:
                score -= 0.15
                issues.append({
                    "type": "freshness",
                    "severity": "medium",
                    "message": f"知识已 {days_since_update} 天未更新"
                })
                suggestions.append("建议定期审查和更新")
            elif days_since_update > 90:
                score -= 0.05
        except:
            score -= 0.1
            issues.append({
                "type": "freshness",
                "severity": "low",
                "message": "无法解析更新时间"
            })
        
        return max(score, 0.0)
    
    def _get_quality_level(self, score: float) -> QualityLevel:
        """根据分数获取质量等级"""
        if score >= 0.9:
            return QualityLevel.EXCELLENT
        elif score >= 0.7:
            return QualityLevel.GOOD
        elif score >= 0.5:
            return QualityLevel.FAIR
        elif score >= 0.3:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    def batch_evaluate(self) -> QualityMetrics:
        """批量评估所有知识"""
        reports = []
        
        for knowledge_id in self.domain_manager.domain_knowledges:
            report = self.evaluate_knowledge(knowledge_id)
            if report:
                reports.append(report)
        
        if not reports:
            return QualityMetrics(
                total_knowledges=0,
                avg_quality_score=0.0,
                quality_distribution={},
                completeness_avg=0.0,
                accuracy_avg=0.0,
                consistency_avg=0.0,
                freshness_avg=0.0,
                top_issues=[]
            )
        
        # 计算统计
        quality_distribution = Counter(r.quality_level.value for r in reports)
        
        all_issues = []
        for r in reports:
            all_issues.extend(r.issues)
        
        top_issues = Counter(i["message"] for i in all_issues).most_common(5)
        
        return QualityMetrics(
            total_knowledges=len(reports),
            avg_quality_score=round(sum(r.overall_score for r in reports) / len(reports), 2),
            quality_distribution=dict(quality_distribution),
            completeness_avg=round(sum(r.completeness_score for r in reports) / len(reports), 2),
            accuracy_avg=round(sum(r.accuracy_score for r in reports) / len(reports), 2),
            consistency_avg=round(sum(r.consistency_score for r in reports) / len(reports), 2),
            freshness_avg=round(sum(r.freshness_score for r in reports) / len(reports), 2),
            top_issues=[{"issue": issue, "count": count} for issue, count in top_issues]
        )
    
    def get_low_quality_knowledges(self, threshold: float = 0.5) -> List[QualityReport]:
        """获取低质量知识"""
        low_quality = []
        for report in self.quality_reports.values():
            if report.overall_score < threshold:
                low_quality.append(report)
        return sorted(low_quality, key=lambda x: x.overall_score)
    
    def get_quality_report(self, knowledge_id: str) -> Optional[QualityReport]:
        """获取质量报告"""
        return self.quality_reports.get(knowledge_id)
    
    def generate_optimization_plan(self) -> Dict[str, Any]:
        """生成优化计划"""
        low_quality = self.get_low_quality_knowledges()
        
        plan = {
            "generated_at": datetime.now().isoformat(),
            "total_issues": len(low_quality),
            "priority_actions": [],
            "suggestions": []
        }
        
        for report in low_quality[:10]:
            knowledge = self.domain_manager.get_domain_knowledge(report.knowledge_id)
            plan["priority_actions"].append({
                "knowledge_id": report.knowledge_id,
                "name": knowledge.name if knowledge else "Unknown",
                "score": report.overall_score,
                "level": report.quality_level.value,
                "main_issues": [i["message"] for i in report.issues[:3]]
            })
        
        # 汇总建议
        all_suggestions = []
        for report in low_quality:
            all_suggestions.extend(report.suggestions)
        
        top_suggestions = Counter(all_suggestions).most_common(5)
        plan["suggestions"] = [{"action": s, "count": c} for s, c in top_suggestions]
        
        return plan

