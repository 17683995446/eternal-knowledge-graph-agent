
"""
终身学习机制 - 阶段48
支持持续学习、知识遗忘与巩固、学习曲线跟踪
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class KnowledgeRetention(Enum):
    """知识保持度"""
    MASTERED = "mastered"
    PROFICIENT = "proficient"
    FAMILIAR = "familiar"
    FORGETTING = "forgetting"
    FORGOTTEN = "forgotten"


@dataclass
class LearningRecord:
    """学习记录"""
    knowledge_id: str
    learn_time: str
    review_count: int = 0
    last_review: Optional[str] = None
    retention_score: float = 0.0
    difficulty_rating: int = 3  # 1-5


class LifelongLearning:
    """终身学习系统"""
    
    def __init__(self, domain_manager):
        self.domain_manager = domain_manager
        self.learning_records: Dict[str, LearningRecord] = {}
        
        # 艾宾浩斯遗忘曲线参数
        self.forget_curve_intervals = [1, 2, 4, 7, 15, 30, 90]  # 天数
    
    def record_learning(self, knowledge_id: str, difficulty: int = 3):
        """记录学习"""
        now = datetime.now().isoformat()
        
        if knowledge_id not in self.learning_records:
            self.learning_records[knowledge_id] = LearningRecord(
                knowledge_id=knowledge_id,
                learn_time=now,
                difficulty_rating=difficulty
            )
        else:
            record = self.learning_records[knowledge_id]
            record.review_count += 1
            record.last_review = now
            # 更新保持度
            record.retention_score = min(1.0, record.retention_score + 0.2)
    
    def get_retention_status(self, knowledge_id: str) -> Dict[str, Any]:
        """获取知识保持状态"""
        if knowledge_id not in self.learning_records:
            return {"status": "not_learned", "retention": 0.0}
        
        record = self.learning_records[knowledge_id]
        
        # 计算时间衰减
        if record.last_review:
            last_time = datetime.fromisoformat(record.last_review)
        else:
            last_time = datetime.fromisoformat(record.learn_time)
        
        days_passed = (datetime.now() - last_time).days
        
        # 基于艾宾浩斯曲线计算保持度
        base_retention = record.retention_score
        decay = self._calculate_decay(days_passed, record.review_count)
        current_retention = max(0.0, base_retention - decay)
        
        # 确定状态
        if current_retention > 0.8:
            status = KnowledgeRetention.MASTERED.value
        elif current_retention > 0.6:
            status = KnowledgeRetention.PROFICIENT.value
        elif current_retention > 0.4:
            status = KnowledgeRetention.FAMILIAR.value
        elif current_retention > 0.2:
            status = KnowledgeRetention.FORGETTING.value
        else:
            status = KnowledgeRetention.FORGOTTEN.value
        
        # 计算下次复习时间
        next_review = self._calculate_next_review(record, days_passed)
        
        return {
            "status": status,
            "retention": round(current_retention, 2),
            "days_since_review": days_passed,
            "review_count": record.review_count,
            "next_review": next_review,
            "difficulty": record.difficulty_rating
        }
    
    def _calculate_decay(self, days: int, review_count: int) -> float:
        """计算遗忘衰减"""
        # 复习次数越多，衰减越慢
        base_decay = 0.1 * days
        retention_factor = 1.0 / (1.0 + review_count * 0.5)
        return base_decay * retention_factor
    
    def _calculate_next_review(self, record: LearningRecord, days_passed: int) -> str:
        """计算下次复习时间"""
        idx = min(record.review_count, len(self.forget_curve_intervals) - 1)
        interval = self.forget_curve_intervals[idx]
        
        next_date = datetime.now() + timedelta(days=interval)
        return next_date.isoformat()
    
    def get_review_recommendations(self) -> List[Dict[str, Any]]:
        """获取复习推荐"""
        recommendations = []
        
        for knowledge_id, record in self.learning_records.items():
            status = self.get_retention_status(knowledge_id)
            
            if status["status"] in ["forgetting", "forgotten"]:
                knowledge = self.domain_manager.get_domain_knowledge(knowledge_id)
                if knowledge:
                    recommendations.append({
                        "knowledge_id": knowledge_id,
                        "name": knowledge.name,
                        "retention": status["retention"],
                        "priority": "high" if status["status"] == "forgotten" else "medium"
                    })
        
        return sorted(recommendations, key=lambda x: x["retention"])
    
    def get_learning_curve(self, knowledge_id: str) -> List[Dict[str, Any]]:
        """获取学习曲线"""
        # 简化实现
        return [
            {"time": "initial", "retention": 1.0},
            {"time": "after_1day", "retention": 0.7},
            {"time": "after_1week", "retention": 0.5},
            {"time": "after_1month", "retention": 0.3}
        ]

