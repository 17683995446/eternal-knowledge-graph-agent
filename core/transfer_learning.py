
"""
知识迁移学习 - 阶段47
支持跨领域知识迁移、相似度计算、迁移效果评估
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


class TransferLearning:
    """迁移学习系统"""
    
    def __init__(self, domain_manager):
        self.domain_manager = domain_manager
    
    def calculate_similarity(self, 
                            source_knowledge_id: str,
                            target_knowledge_id: str) -> float:
        """计算知识相似度"""
        source = self.domain_manager.get_domain_knowledge(source_knowledge_id)
        target = self.domain_manager.get_domain_knowledge(target_knowledge_id)
        
        if not source or not target:
            return 0.0
        
        # 标签相似度
        source_tags = set(source.tags)
        target_tags = set(target.tags)
        tag_sim = len(source_tags & target_tags) / max(len(source_tags | target_tags), 1)
        
        # 领域相似度
        domain_sim = 1.0 if source.domain_type == target.domain_type else 0.3
        
        # 内容相似度（简单实现）
        source_content = str(source.content)
        target_content = str(target.content)
        content_sim = self._text_similarity(source_content, target_content)
        
        return tag_sim * 0.4 + domain_sim * 0.3 + content_sim * 0.3
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """文本相似度"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def transfer_knowledge(self, 
                          source_knowledge_id: str,
                          target_domain: str,
                          adaptation_rules: Optional[Dict] = None) -> Optional[Any]:
        """迁移知识到新领域"""
        source = self.domain_manager.get_domain_knowledge(source_knowledge_id)
        if not source:
            return None
        
        # 创建迁移后的知识
        from core.domain_knowledge_manager import DomainKnowledge, DomainType
        
        new_knowledge = DomainKnowledge(
            knowledge_id=f"transferred_{source_knowledge_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            domain_type=DomainType(target_domain),
            name=f"[迁移] {source.name}",
            content=dict(source.content),
            confidence=source.confidence * 0.8,  # 迁移后置信度降低
            tags=source.tags + ["transferred", target_domain],
            sources=source.sources + ["transfer_learning"]
        )
        
        # 应用适配规则
        if adaptation_rules:
            for key, value in adaptation_rules.items():
                if key in new_knowledge.content:
                    new_knowledge.content[key] = value
        
        return new_knowledge
    
    def find_transfer_candidates(self, 
                                source_domain: str,
                                target_domain: str,
                                min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        """查找迁移候选"""
        candidates = []
        
        for knowledge in self.domain_manager.domain_knowledges.values():
            if knowledge.domain_type.value == source_domain:
                # 计算与目标领域的相似度
                similarity = self._estimate_domain_similarity(
                    knowledge, target_domain
                )
                
                if similarity >= min_similarity:
                    candidates.append({
                        "knowledge_id": knowledge.knowledge_id,
                        "name": knowledge.name,
                        "similarity": similarity
                    })
        
        return sorted(candidates, key=lambda x: x["similarity"], reverse=True)
    
    def _estimate_domain_similarity(self, knowledge, target_domain: str) -> float:
        """估计领域相似度"""
        # 基于标签和领域类型
        domain_tag_map = {
            "technology": ["技术", "编程", "软件", "硬件"],
            "healthcare": ["医疗", "健康", "疾病", "药物"],
            "education": ["教育", "学习", "课程", "学校"],
            "finance": ["金融", "经济", "投资", "银行"],
        }
        
        target_tags = set(domain_tag_map.get(target_domain, []))
        knowledge_tags = set(knowledge.tags)
        
        if not target_tags:
            return 0.5
        
        overlap = knowledge_tags & target_tags
        return len(overlap) / len(target_tags)

