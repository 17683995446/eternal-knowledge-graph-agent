"""
阶段22: 高级自驱学习与进化框架
基于第一性原理，实现自适应学习、知识质量评估和进化策略选择
"""
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class EvolutionStrategy(Enum):
    """进化策略枚举"""
    CONSERVATIVE = "conservative"  # 保守策略：小步迭代，低风险
    BALANCED = "balanced"         # 平衡策略：中等调整
    AGGRESSIVE = "aggressive"    # 激进策略：大胆尝试，高风险高回报


@dataclass
class TaskRecord:
    """任务执行记录"""
    task_id: str
    task_type: str
    task_content: str
    start_time: float
    end_time: Optional[float] = None
    success: bool = False
    result: Optional[str] = None
    error: Optional[str] = None
    knowledge_used: List[str] = field(default_factory=list)  # 使用的知识节点
    knowledge_produced: List[str] = field(default_factory=list)  # 产生的知识
    execution_time: float = 0.0


@dataclass
class KnowledgeQuality:
    """知识质量评估"""
    node_id: str
    node_name: str
    usage_count: int = 0
    success_rate: float = 0.0  # 使用此知识时任务成功率
    freshness: float = 1.0  # 新鲜度（时间衰减）
    completeness: float = 1.0  # 完整性（属性丰富度）
    connectivity: float = 0.0  # 连接度（关联边数量）
    quality_score: float = 0.0  # 综合质量分数
    last_used: float = 0.0
    created_at: float = 0.0


class LearningTracker:
    """
    学习追踪器 - 记录任务执行、知识使用和效果
    遵循记忆公理：所有学习经验必须结构化存储
    """

    def __init__(self):
        self.task_history: List[TaskRecord] = []
        self.knowledge_usage: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                'usage_count': 0,
                'success_count': 0,
                'last_used': 0,
                'total_execution_time': 0.0,
                'success_rates': []  # 每次使用的成功率
            }
        )
        self.current_task: Optional[TaskRecord] = None

    def start_task(self, task_id: str, task_type: str, task_content: str) -> None:
        """开始追踪任务执行"""
        self.current_task = TaskRecord(
            task_id=task_id,
            task_type=task_type,
            task_content=task_content,
            start_time=time.time()
        )

    def end_task(self, success: bool, result: Optional[str] = None,
                 error: Optional[str] = None, knowledge_used: List[str] = None) -> None:
        """结束任务追踪"""
        if not self.current_task:
            return

        self.current_task.end_time = time.time()
        self.current_task.success = success
        self.current_task.result = result
        self.current_task.error = error
        self.current_task.knowledge_used = knowledge_used or []
        self.current_task.execution_time = (
            self.current_task.end_time - self.current_task.start_time
        )

        self.task_history.append(self.current_task)

        # 更新知识使用统计
        for node_id in self.current_task.knowledge_used:
            usage = self.knowledge_usage[node_id]
            usage['usage_count'] += 1
            usage['last_used'] = time.time()
            usage['total_execution_time'] += self.current_task.execution_time
            if success:
                usage['success_count'] += 1
            usage['success_rates'].append(
                usage['success_count'] / usage['usage_count']
            )

        self.current_task = None

    def record_knowledge_produced(self, node_id: str) -> None:
        """记录产生的知识"""
        if self.current_task:
            self.current_task.knowledge_produced.append(node_id)

    def get_task_success_rate(self, task_type: Optional[str] = None) -> float:
        """获取任务成功率"""
        tasks = self.task_history
        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]

        if not tasks:
            return 0.0

        successful = sum(1 for t in tasks if t.success)
        return successful / len(tasks)

    def get_knowledge_effectiveness(self, node_id: str) -> Dict[str, float]:
        """获取知识有效性指标"""
        usage = self.knowledge_usage.get(node_id, {
            'usage_count': 0,
            'success_count': 0,
            'last_used': 0,
            'total_execution_time': 0.0,
            'success_rates': []
        })

        if usage['usage_count'] == 0:
            return {
                'usage_count': 0,
                'success_rate': 0.0,
                'avg_execution_time': 0.0,
                'effectiveness': 0.0,
                'last_used': 0
            }

        success_rate = usage['success_count'] / usage['usage_count']
        avg_time = usage['total_execution_time'] / usage['usage_count']

        # 有效性 = 成功率 / (1 + 归一化执行时间)
        effectiveness = success_rate / (1 + min(avg_time, 10) / 10)

        return {
            'usage_count': usage['usage_count'],
            'success_rate': success_rate,
            'avg_execution_time': avg_time,
            'effectiveness': effectiveness,
            'last_used': usage['last_used']
        }

    def get_recent_performance(self, window_size: int = 20) -> Dict[str, Any]:
        """获取最近性能指标"""
        recent_tasks = self.task_history[-window_size:]

        if not recent_tasks:
            return {
                'task_count': 0,
                'success_rate': 0.0,
                'avg_execution_time': 0.0,
                'knowledge_produced': 0
            }

        successful = sum(1 for t in recent_tasks if t.success)
        total_time = sum(t.execution_time for t in recent_tasks)
        total_knowledge = sum(len(t.knowledge_produced) for t in recent_tasks)

        return {
            'task_count': len(recent_tasks),
            'success_rate': successful / len(recent_tasks),
            'avg_execution_time': total_time / len(recent_tasks),
            'knowledge_produced': total_knowledge
        }


class KnowledgeQualityAssessor:
    """
    知识质量评估器 - 评估和优化知识图谱中的知识质量
    遵循自驱公理：知识必须持续优化，避免老化臃肿
    """

    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph
        self.quality_cache: Dict[str, KnowledgeQuality] = {}
        self.last_assessment_time: float = 0
        self.assessment_interval: float = 60.0  # 每60秒评估一次

    def _parse_timestamp(self, timestamp) -> float:
        """解析时间戳，处理字符串格式"""
        if isinstance(timestamp, (int, float)):
            return float(timestamp)
        elif isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp).timestamp()
            except (ValueError, TypeError):
                return time.time()
        else:
            return time.time()

    def assess_knowledge_quality(self, node_id: str,
                                 tracker: LearningTracker) -> Optional[KnowledgeQuality]:
        """评估单个知识节点的质量"""
        node = self.kg.nodes.get(node_id)
        if not node:
            return None

        # 获取使用统计
        effectiveness = tracker.get_knowledge_effectiveness(node_id)
        usage_count = effectiveness['usage_count']
        success_rate = effectiveness['success_rate']
        last_used = effectiveness['last_used']

        # 计算新鲜度（基于时间衰减）
        current_time = time.time()
        created_time = self._parse_timestamp(node.created_at)
        time_since_creation = current_time - created_time
        freshness = max(0.1, 1.0 - (time_since_creation / (7 * 24 * 3600)))  # 7天完全衰减

        # 计算完整性（基于属性丰富度）
        attr_count = len(node.attr) if node.attr else 0
        completeness = min(1.0, attr_count / 5)  # 5个属性为满分

        # 计算连接度（基于边数量）
        neighbors = self.kg.get_neighbors(node.name)
        connectivity = min(1.0, len(neighbors) / 10)  # 10个邻居为满分

        # 综合质量分数
        # 权重：使用频率(0.3) + 成功率(0.3) + 新鲜度(0.2) + 完整性(0.1) + 连接度(0.1)
        quality_score = (
            min(1.0, usage_count / 20) * 0.3 +
            success_rate * 0.3 +
            freshness * 0.2 +
            completeness * 0.1 +
            connectivity * 0.1
        )

        quality = KnowledgeQuality(
            node_id=node_id,
            node_name=node.name,
            usage_count=usage_count,
            success_rate=success_rate,
            freshness=freshness,
            completeness=completeness,
            connectivity=connectivity,
            quality_score=quality_score,
            last_used=last_used,
            created_at=created_time
        )

        self.quality_cache[node_id] = quality
        return quality

    def assess_all_knowledge(self, tracker: LearningTracker) -> List[KnowledgeQuality]:
        """评估所有知识节点"""
        qualities = []

        for node_id in self.kg.nodes.keys():
            quality = self.assess_knowledge_quality(node_id, tracker)
            if quality:
                qualities.append(quality)

        # 按质量排序
        qualities.sort(key=lambda q: q.quality_score, reverse=True)

        self.last_assessment_time = time.time()
        return qualities

    def get_low_quality_knowledge(self, tracker: LearningTracker,
                                   threshold: float = 0.3) -> List[str]:
        """获取低质量知识节点ID列表"""
        qualities = self.assess_all_knowledge(tracker)
        return [q.node_id for q in qualities if q.quality_score < threshold]

    def get_stale_knowledge(self, tracker: LearningTracker,
                            days_threshold: int = 30) -> List[str]:
        """获取长期未使用的知识"""
        stale_nodes = []
        current_time = time.time()
        threshold_seconds = days_threshold * 24 * 3600

        for node_id, usage in tracker.knowledge_usage.items():
            if current_time - usage['last_used'] > threshold_seconds:
                stale_nodes.append(node_id)

        return stale_nodes


class AdaptiveEvolutionEngine:
    """
    自适应进化引擎 - 根据系统状态自动选择最优进化策略
    遵循存续公理：进化不能威胁系统稳定
    """

    def __init__(self, knowledge_graph, tracker: LearningTracker,
                 assessor: KnowledgeQualityAssessor):
        self.kg = knowledge_graph
        self.tracker = tracker
        self.assessor = assessor
        self.current_strategy = EvolutionStrategy.BALANCED
        self.strategy_history: List[Tuple[float, EvolutionStrategy]] = []

        # 策略参数
        self.strategy_params = {
            EvolutionStrategy.CONSERVATIVE: {
                'trim_threshold': 0.2,      # 淘汰阈值
                'evolution_intensity': 0.1,  # 进化强度
                'exploration_rate': 0.05,   # 探索率
                'consolidation_ratio': 0.8  # 巩固比例
            },
            EvolutionStrategy.BALANCED: {
                'trim_threshold': 0.3,
                'evolution_intensity': 0.3,
                'exploration_rate': 0.15,
                'consolidation_ratio': 0.6
            },
            EvolutionStrategy.AGGRESSIVE: {
                'trim_threshold': 0.4,
                'evolution_intensity': 0.6,
                'exploration_rate': 0.3,
                'consolidation_ratio': 0.4
            }
        }

    def analyze_system_state(self) -> Dict[str, Any]:
        """分析当前系统状态"""
        recent = self.tracker.get_recent_performance(window_size=20)
        knowledge_count = len(self.kg.nodes)
        edge_count = len(self.kg.edges)

        # 计算知识密度
        density = edge_count / max(1, knowledge_count)

        # 评估知识质量分布
        qualities = self.assessor.assess_all_knowledge(self.tracker)
        if qualities:
            avg_quality = sum(q.quality_score for q in qualities) / len(qualities)
            quality_variance = sum(
                (q.quality_score - avg_quality) ** 2 for q in qualities
            ) / len(qualities)
        else:
            avg_quality = 0
            quality_variance = 0

        return {
            'success_rate': recent['success_rate'],
            'task_count': recent['task_count'],
            'knowledge_count': knowledge_count,
            'edge_count': edge_count,
            'knowledge_density': density,
            'avg_quality': avg_quality,
            'quality_variance': quality_variance,
            'system_load': knowledge_count / 1000  # 假设1000为高负载
        }

    def select_strategy(self) -> EvolutionStrategy:
        """基于系统状态选择进化策略"""
        state = self.analyze_system_state()

        # 决策逻辑
        if state['success_rate'] < 0.5:
            # 成功率低，切换到保守策略
            new_strategy = EvolutionStrategy.CONSERVATIVE
        elif state['success_rate'] > 0.8 and state['avg_quality'] > 0.6:
            # 表现良好，可以激进一些
            if state['system_load'] > 0.7:
                # 高负载，平衡策略
                new_strategy = EvolutionStrategy.BALANCED
            else:
                new_strategy = EvolutionStrategy.AGGRESSIVE
        elif state['quality_variance'] > 0.1:
            # 质量差异大，需要平衡
            new_strategy = EvolutionStrategy.BALANCED
        else:
            # 默认平衡策略
            new_strategy = EvolutionStrategy.BALANCED

        if new_strategy != self.current_strategy:
            self.current_strategy = new_strategy
            self.strategy_history.append((time.time(), new_strategy))
            print(f"[策略选择] 切换到 {new_strategy.value} 策略")

        return new_strategy

    def get_current_params(self) -> Dict[str, float]:
        """获取当前策略参数"""
        return self.strategy_params[self.current_strategy].copy()

    def execute_adaptive_evolution(self) -> Dict[str, Any]:
        """执行自适应进化"""
        strategy = self.select_strategy()
        params = self.get_current_params()

        print(f"[自适应进化] 使用 {strategy.value} 策略")
        print(f"  参数: {params}")

        # 1. 清理低质量知识
        low_quality_nodes = self.assessor.get_low_quality_knowledge(
            self.tracker, params['trim_threshold']
        )
        trimmed_count = 0
        for node_id in low_quality_nodes[:int(len(low_quality_nodes) * params['consolidation_ratio'])]:
            node = self.kg.nodes.get(node_id)
            if node and self.kg.delete_node(node.name):
                trimmed_count += 1

        # 2. 强化高质量知识 - 通过增加权重的方式
        qualities = self.assessor.assess_all_knowledge(self.tracker)
        strengthened_count = 0
        for quality in qualities[:10]:  # 强化前10
            if quality.quality_score > 0.7:
                node = self.kg.nodes.get(quality.node_id)
                if node:
                    neighbors = self.kg.get_neighbors(node.name)
                    for neighbor in neighbors[:3]:  # 最多强化3个邻居
                        self.kg.reinforce_edge(node.name, neighbor, "质量强化", boost=0.05)
                    strengthened_count += 1

        # 3. 执行知识推理扩展
        inference_count = int(10 * params['evolution_intensity'])
        for _ in range(inference_count):
            self.kg.infer_new_relations("")

        return {
            'strategy': strategy.value,
            'params': params,
            'trimmed_nodes': trimmed_count,
            'strengthened_nodes': strengthened_count,
            'new_inferences': inference_count
        }

    def get_evolution_report(self) -> Dict[str, Any]:
        """获取进化报告"""
        state = self.analyze_system_state()
        qualities = self.assessor.assess_all_knowledge(self.tracker)

        return {
            'current_strategy': self.current_strategy.value,
            'system_state': state,
            'knowledge_quality_distribution': {
                'high': len([q for q in qualities if q.quality_score > 0.7]),
                'medium': len([q for q in qualities if 0.4 <= q.quality_score <= 0.7]),
                'low': len([q for q in qualities if q.quality_score < 0.4])
            },
            'strategy_history_count': len(self.strategy_history),
            'recommendations': self._generate_recommendations(state)
        }

    def _generate_recommendations(self, state: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []

        if state['success_rate'] < 0.5:
            recommendations.append("任务成功率较低，建议增加知识巩固，减少探索")

        if state['avg_quality'] < 0.4:
            recommendations.append("平均知识质量较低，建议强化优质知识，淘汰低质知识")

        if state['knowledge_density'] < 0.5:
            recommendations.append("知识密度较低，建议增加知识关联")

        if state['system_load'] > 0.8:
            recommendations.append("系统负载较高，建议精简知识库")

        if not recommendations:
            recommendations.append("系统运行良好，继续保持当前策略")

        return recommendations
