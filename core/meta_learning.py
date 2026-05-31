
"""
元学习能力 - 阶段46
支持学习策略优化、超参数自适应、模型选择
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path


class MetaStrategy(Enum):
    """元策略"""
    FAST_LEARN = "fast_learn"
    DEEP_LEARN = "deep_learn"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"


@dataclass
class LearningProfile:
    """学习画像"""
    profile_id: str
    domain_type: str
    success_rate: float = 0.0
    avg_learning_time: float = 0.0
    preferred_strategy: str = "balanced"
    difficulty_level: str = "medium"


class MetaLearning:
    """元学习系统"""
    
    def __init__(self):
        self.profiles: Dict[str, LearningProfile] = {}
        self.strategy_performance: Dict[str, List[float]] = {}
        self.data_dir = Path("data/meta_learning")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_learning_pattern(self, 
                                knowledge_id: str,
                                learning_history: List[Dict]) -> Dict[str, Any]:
        """分析学习模式"""
        if not learning_history:
            return {"pattern": "unknown", "confidence": 0.0}
        
        # 计算成功率
        successes = sum(1 for h in learning_history if h.get("success", False))
        success_rate = successes / len(learning_history)
        
        # 计算平均学习时间
        times = [h.get("time", 0) for h in learning_history if h.get("time")]
        avg_time = sum(times) / len(times) if times else 0
        
        # 确定模式
        if success_rate > 0.8 and avg_time < 10:
            pattern = "fast_learner"
        elif success_rate > 0.8:
            pattern = "thorough_learner"
        elif success_rate > 0.5:
            pattern = "average_learner"
        else:
            pattern = "struggling_learner"
        
        return {
            "pattern": pattern,
            "success_rate": success_rate,
            "avg_time": avg_time,
            "total_attempts": len(learning_history),
            "confidence": min(success_rate + 0.2, 1.0)
        }
    
    def recommend_strategy(self, 
                          domain_type: str,
                          user_pattern: str) -> str:
        """推荐学习策略"""
        strategy_map = {
            "fast_learner": MetaStrategy.FAST_LEARN.value,
            "thorough_learner": MetaStrategy.DEEP_LEARN.value,
            "average_learner": MetaStrategy.BALANCED.value,
            "struggling_learner": MetaStrategy.CONSERVATIVE.value
        }
        
        return strategy_map.get(user_pattern, MetaStrategy.BALANCED.value)
    
    def get_meta_stats(self) -> Dict[str, Any]:
        """获取元学习统计"""
        return {
            "total_profiles": len(self.profiles),
            "strategy_performance": {
                k: {"avg": sum(v)/len(v) if v else 0, "count": len(v)}
                for k, v in self.strategy_performance.items()
            }
        }

