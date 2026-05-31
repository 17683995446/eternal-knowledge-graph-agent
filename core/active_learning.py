
"""
主动学习策略 - 阶段49
支持不确定性采样、信息增益计算、主动查询
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import random


class ActiveLearning:
    """主动学习系统"""
    
    def __init__(self, domain_manager):
        self.domain_manager = domain_manager
        self.uncertainty_threshold = 0.5
    
    def calculate_uncertainty(self, knowledge_id: str) -> float:
        """计算知识不确定性"""
        knowledge = self.domain_manager.get_domain_knowledge(knowledge_id)
        if not knowledge:
            return 1.0
        
        # 基于置信度计算不确定性
        uncertainty = 1.0 - knowledge.confidence
        
        # 内容完整性影响
        content_completeness = len(knowledge.content) / 5.0  # 假设5个字段为完整
        uncertainty += max(0, 1.0 - content_completeness) * 0.3
        
        # 标签数量影响
        if not knowledge.tags:
            uncertainty += 0.2
        
        return min(uncertainty, 1.0)
    
    def select_samples_for_labeling(self, 
                                   sample_size: int = 5) -> List[Dict[str, Any]]:
        """选择需要标注的样本"""
        uncertainties = []
        
        for knowledge_id in self.domain_manager.domain_knowledges:
            uncertainty = self.calculate_uncertainty(knowledge_id)
            knowledge = self.domain_manager.get_domain_knowledge(knowledge_id)
            
            if uncertainty > self.uncertainty_threshold:
                uncertainties.append({
                    "knowledge_id": knowledge_id,
                    "name": knowledge.name if knowledge else "Unknown",
                    "uncertainty": uncertainty,
                    "confidence": knowledge.confidence if knowledge else 0.0
                })
        
        # 按不确定性排序
        uncertainties.sort(key=lambda x: x["uncertainty"], reverse=True)
        
        return uncertainties[:sample_size]
    
    def suggest_queries(self, 
                       domain_type: Optional[str] = None,
                       limit: int = 3) -> List[str]:
        """建议查询"""
        suggestions = []
        
        # 基于领域类型生成建议
        domain_queries = {
            "technology": [
                "最新的编程技术有哪些？",
                "如何学习人工智能？",
                "前端开发框架对比"
            ],
            "healthcare": [
                "常见疾病的预防措施",
                "健康饮食建议",
                "运动健身指南"
            ],
            "education": [
                "高效学习方法",
                "学科知识体系",
                "考试备考策略"
            ]
        }
        
        if domain_type and domain_type in domain_queries:
            suggestions = domain_queries[domain_type][:limit]
        else:
            # 随机选择
            all_queries = [q for queries in domain_queries.values() for q in queries]
            suggestions = random.sample(all_queries, min(limit, len(all_queries)))
        
        return suggestions
    
    def get_active_learning_stats(self) -> Dict[str, Any]:
        """获取主动学习统计"""
        total = len(self.domain_manager.domain_knowledges)
        
        high_uncertainty = sum(
            1 for kid in self.domain_manager.domain_knowledges
            if self.calculate_uncertainty(kid) > self.uncertainty_threshold
        )
        
        return {
            "total_knowledges": total,
            "high_uncertainty_count": high_uncertainty,
            "uncertainty_threshold": self.uncertainty_threshold,
            "labeling_priority": high_uncertainty / total if total > 0 else 0
        }

