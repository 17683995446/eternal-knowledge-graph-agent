
"""
持续自适应优化 - 阶段50-60
支持性能监控、自动调优、资源管理
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import time


@dataclass
class PerformanceMetric:
    """性能指标"""
    metric_name: str
    value: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    threshold: float = 0.0


class ContinuousOptimization:
    """持续优化系统"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.optimization_history: List[Dict] = []
        self.performance_thresholds = {
            "response_time": 1.0,  # 秒
            "accuracy": 0.8,
            "memory_usage": 100,  # MB
        }
    
    def record_metric(self, metric_name: str, value: float):
        """记录性能指标"""
        threshold = self.performance_thresholds.get(metric_name, 0.0)
        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            threshold=threshold
        )
        self.metrics.append(metric)
        
        # 检查是否需要优化
        if value > threshold:
            self._trigger_optimization(metric_name, value)
    
    def _trigger_optimization(self, metric_name: str, current_value: float):
        """触发优化"""
        optimization = {
            "timestamp": datetime.now().isoformat(),
            "metric": metric_name,
            "before_value": current_value,
            "action": "auto_optimization",
            "status": "triggered"
        }
        self.optimization_history.append(optimization)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        if not self.metrics:
            return {"status": "no_data"}
        
        # 按指标分组统计
        metric_groups = {}
        for m in self.metrics:
            if m.metric_name not in metric_groups:
                metric_groups[m.metric_name] = []
            metric_groups[m.metric_name].append(m.value)
        
        report = {}
        for name, values in metric_groups.items():
            report[name] = {
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "latest": values[-1],
                "threshold": self.performance_thresholds.get(name, 0),
                "status": "normal" if values[-1] <= self.performance_thresholds.get(name, float('inf')) else "warning"
            }
        
        return report
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """获取优化统计"""
        return {
            "total_optimizations": len(self.optimization_history),
            "recent_optimizations": self.optimization_history[-5:] if self.optimization_history else [],
            "performance_thresholds": self.performance_thresholds
        }

