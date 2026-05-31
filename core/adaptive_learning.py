
"""
自适应学习框架 - 阶段41
支持在线学习、用户反馈集成、知识更新策略和A/B测试
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import random
from pathlib import Path
from collections import defaultdict


class FeedbackType(Enum):
    """反馈类型"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CORRECTION = "correction"


class LearningStrategy(Enum):
    """学习策略"""
    INCREMENTAL = "incremental"
    BATCH = "batch"
    ACTIVE = "active"
    REINFORCEMENT = "reinforcement"


@dataclass
class UserFeedback:
    """用户反馈"""
    feedback_id: str
    knowledge_id: str
    user_id: str
    feedback_type: FeedbackType
    rating: Optional[int] = None  # 1-5
    comment: str = ""
    correction: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class LearningEvent:
    """学习事件"""
    event_id: str
    event_type: str
    knowledge_id: str
    before_state: Dict[str, Any] = field(default_factory=dict)
    after_state: Dict[str, Any] = field(default_factory=dict)
    confidence_delta: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ABTestVariant:
    """A/B测试变体"""
    variant_id: str
    name: str
    config: Dict[str, Any] = field(default_factory=dict)
    traffic_percentage: float = 0.5
    metrics: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))


@dataclass
class ABTest:
    """A/B测试"""
    test_id: str
    test_name: str
    variants: List[ABTestVariant] = field(default_factory=list)
    status: str = "running"  # running, paused, completed
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None


class AdaptiveLearningFramework:
    """自适应学习框架"""
    
    def __init__(self, domain_manager, domain_searcher):
        self.domain_manager = domain_manager
        self.domain_searcher = domain_searcher
        
        self.feedbacks: Dict[str, UserFeedback] = {}
        self.learning_events: List[LearningEvent] = []
        self.ab_tests: Dict[str, ABTest] = {}
        self.learning_strategies: Dict[str, LearningStrategy] = {}
        
        # 学习参数
        self.learning_rate = 0.1
        self.confidence_decay = 0.95
        self.feedback_threshold = 0.6
        
        self.data_dir = Path("data/learning")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self._load_data()
    
    def _load_data(self):
        """加载学习数据"""
        feedback_file = self.data_dir / "feedbacks.json"
        if feedback_file.exists():
            try:
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for f_data in data.get("feedbacks", []):
                    feedback = UserFeedback(
                        feedback_id=f_data["feedback_id"],
                        knowledge_id=f_data["knowledge_id"],
                        user_id=f_data["user_id"],
                        feedback_type=FeedbackType(f_data["feedback_type"]),
                        rating=f_data.get("rating"),
                        comment=f_data.get("comment", ""),
                        correction=f_data.get("correction", {}),
                        timestamp=f_data.get("timestamp")
                    )
                    self.feedbacks[feedback.feedback_id] = feedback
            except Exception as e:
                print(f"加载反馈数据失败: {e}")
    
    def _save_data(self):
        """保存学习数据"""
        feedback_file = self.data_dir / "feedbacks.json"
        data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "feedbacks": []
        }
        for feedback in self.feedbacks.values():
            data["feedbacks"].append({
                "feedback_id": feedback.feedback_id,
                "knowledge_id": feedback.knowledge_id,
                "user_id": feedback.user_id,
                "feedback_type": feedback.feedback_type.value,
                "rating": feedback.rating,
                "comment": feedback.comment,
                "correction": feedback.correction,
                "timestamp": feedback.timestamp
            })
        try:
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存反馈数据失败: {e}")
    
    def add_feedback(self, 
                    knowledge_id: str,
                    user_id: str,
                    feedback_type: str,
                    rating: Optional[int] = None,
                    comment: str = "",
                    correction: Optional[Dict[str, Any]] = None) -> Optional[UserFeedback]:
        """
        添加用户反馈
        
        Args:
            knowledge_id: 知识ID
            user_id: 用户ID
            feedback_type: 反馈类型
            rating: 评分 1-5
            comment: 评论
            correction: 修正内容
        
        Returns:
            反馈对象
        """
        knowledge = self.domain_manager.get_domain_knowledge(knowledge_id)
        if not knowledge:
            print(f"知识 {knowledge_id} 不存在")
            return None
        
        feedback_id = f"fb_{knowledge_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        feedback = UserFeedback(
            feedback_id=feedback_id,
            knowledge_id=knowledge_id,
            user_id=user_id,
            feedback_type=FeedbackType(feedback_type),
            rating=rating,
            comment=comment,
            correction=correction or {}
        )
        
        self.feedbacks[feedback_id] = feedback
        self._save_data()
        
        # 触发学习更新
        self._process_feedback(feedback)
        
        print(f"添加反馈: {feedback_id} ({feedback_type})")
        return feedback
    
    def _process_feedback(self, feedback: UserFeedback):
        """处理反馈并更新知识"""
        knowledge = self.domain_manager.get_domain_knowledge(feedback.knowledge_id)
        if not knowledge:
            return
        
        # 记录学习前状态
        before_state = {
            "confidence": knowledge.confidence,
            "content": dict(knowledge.content)
        }
        
        # 根据反馈类型调整
        if feedback.feedback_type == FeedbackType.POSITIVE:
            # 正面反馈增加置信度
            knowledge.confidence = min(1.0, knowledge.confidence + self.learning_rate)
        elif feedback.feedback_type == FeedbackType.NEGATIVE:
            # 负面反馈降低置信度
            knowledge.confidence = max(0.0, knowledge.confidence - self.learning_rate)
        elif feedback.feedback_type == FeedbackType.CORRECTION:
            # 修正反馈更新内容
            if feedback.correction:
                knowledge.content.update(feedback.correction)
                knowledge.confidence = min(1.0, knowledge.confidence + self.learning_rate * 0.5)
        
        # 根据评分调整
        if feedback.rating:
            rating_adjustment = (feedback.rating - 3) / 10.0  # -0.2 to 0.2
            knowledge.confidence = max(0.0, min(1.0, knowledge.confidence + rating_adjustment))
        
        # 记录学习事件
        event = LearningEvent(
            event_id=f"learn_{feedback.feedback_id}",
            event_type="feedback_update",
            knowledge_id=feedback.knowledge_id,
            before_state=before_state,
            after_state={
                "confidence": knowledge.confidence,
                "content": dict(knowledge.content)
            },
            confidence_delta=knowledge.confidence - before_state["confidence"]
        )
        self.learning_events.append(event)
        
        # 保存更新
        self.domain_manager._save_knowledge()
    
    def get_knowledge_feedback_stats(self, knowledge_id: str) -> Dict[str, Any]:
        """获取知识的反馈统计"""
        knowledge_feedbacks = [
            f for f in self.feedbacks.values() if f.knowledge_id == knowledge_id
        ]
        
        if not knowledge_feedbacks:
            return {"total": 0, "avg_rating": 0, "sentiment": "neutral"}
        
        ratings = [f.rating for f in knowledge_feedbacks if f.rating is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        type_counts = {}
        for f in knowledge_feedbacks:
            t = f.feedback_type.value
            type_counts[t] = type_counts.get(t, 0) + 1
        
        # 计算情感倾向
        positive = type_counts.get("positive", 0) + type_counts.get("correction", 0) * 0.5
        negative = type_counts.get("negative", 0)
        total = len(knowledge_feedbacks)
        
        if positive / total > 0.6:
            sentiment = "positive"
        elif negative / total > 0.4:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "total": len(knowledge_feedbacks),
            "avg_rating": round(avg_rating, 2),
            "sentiment": sentiment,
            "type_distribution": type_counts,
            "recent_feedback": [
                {
                    "type": f.feedback_type.value,
                    "rating": f.rating,
                    "comment": f.comment,
                    "timestamp": f.timestamp
                }
                for f in sorted(knowledge_feedbacks, key=lambda x: x.timestamp, reverse=True)[:5]
            ]
        }
    
    def create_ab_test(self, 
                      test_name: str,
                      variants: List[Dict[str, Any]]) -> ABTest:
        """
        创建A/B测试
        
        Args:
            test_name: 测试名称
            variants: 变体配置列表
        
        Returns:
            A/B测试对象
        """
        test_id = f"abtest_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        ab_variants = []
        for i, v_config in enumerate(variants):
            variant = ABTestVariant(
                variant_id=f"{test_id}_v{i}",
                name=v_config.get("name", f"Variant {i}"),
                config=v_config.get("config", {}),
                traffic_percentage=v_config.get("traffic_percentage", 1.0 / len(variants))
            )
            ab_variants.append(variant)
        
        test = ABTest(
            test_id=test_id,
            test_name=test_name,
            variants=ab_variants
        )
        
        self.ab_tests[test_id] = test
        
        print(f"创建A/B测试: {test_name} ({test_id})")
        return test
    
    def get_ab_test_variant(self, test_id: str, user_id: str) -> Optional[ABTestVariant]:
        """为用户分配A/B测试变体"""
        if test_id not in self.ab_tests:
            return None
        
        test = self.ab_tests[test_id]
        if test.status != "running":
            return None
        
        # 使用用户ID的哈希值确定变体
        hash_val = hash(f"{test_id}_{user_id}") % 100
        cumulative = 0
        
        for variant in test.variants:
            cumulative += variant.traffic_percentage * 100
            if hash_val < cumulative:
                return variant
        
        return test.variants[-1]
    
    def record_ab_test_metric(self, 
                             test_id: str,
                             variant_id: str,
                             metric_name: str,
                             value: float):
        """记录A/B测试指标"""
        if test_id not in self.ab_tests:
            return
        
        for variant in self.ab_tests[test_id].variants:
            if variant.variant_id == variant_id:
                variant.metrics[metric_name].append(value)
                break
    
    def get_ab_test_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """获取A/B测试结果"""
        if test_id not in self.ab_tests:
            return None
        
        test = self.ab_tests[test_id]
        results = {
            "test_id": test_id,
            "test_name": test.test_name,
            "status": test.status,
            "variants": []
        }
        
        for variant in test.variants:
            variant_results = {
                "variant_id": variant.variant_id,
                "name": variant.name,
                "traffic_percentage": variant.traffic_percentage,
                "metrics": {}
            }
            
            for metric_name, values in variant.metrics.items():
                if values:
                    variant_results["metrics"][metric_name] = {
                        "count": len(values),
                        "mean": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values)
                    }
            
            results["variants"].append(variant_results)
        
        return results
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """获取学习统计"""
        return {
            "total_feedbacks": len(self.feedbacks),
            "total_learning_events": len(self.learning_events),
            "total_ab_tests": len(self.ab_tests),
            "active_ab_tests": sum(1 for t in self.ab_tests.values() if t.status == "running"),
            "feedback_by_type": self._count_feedbacks_by_type(),
            "avg_confidence_change": self._avg_confidence_change()
        }
    
    def _count_feedbacks_by_type(self) -> Dict[str, int]:
        """按类型统计反馈"""
        counts = {}
        for f in self.feedbacks.values():
            t = f.feedback_type.value
            counts[t] = counts.get(t, 0) + 1
        return counts
    
    def _avg_confidence_change(self) -> float:
        """平均置信度变化"""
        if not self.learning_events:
            return 0.0
        return sum(e.confidence_delta for e in self.learning_events) / len(self.learning_events)
    
    def apply_learning_strategy(self, 
                               knowledge_id: str,
                               strategy: LearningStrategy) -> bool:
        """应用学习策略"""
        knowledge = self.domain_manager.get_domain_knowledge(knowledge_id)
        if not knowledge:
            return False
        
        self.learning_strategies[knowledge_id] = strategy
        
        if strategy == LearningStrategy.INCREMENTAL:
            # 增量学习：小步调整
            pass
        elif strategy == LearningStrategy.BATCH:
            # 批量学习：收集多个反馈后更新
            pass
        elif strategy == LearningStrategy.ACTIVE:
            # 主动学习：选择最有价值的数据
            pass
        elif strategy == LearningStrategy.REINFORCEMENT:
            # 强化学习：基于奖励调整
            pass
        
        print(f"应用学习策略 {strategy.value} 到 {knowledge_id}")
        return True

