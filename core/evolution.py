"""
基于第一性原理，轻量化永动知识图谱智能体 - 自驱进化层
自驱公理核心实现：整合任务生成器和知识推演引擎
"""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.knowledge_graph import KnowledgeGraph
    from core.task_queue import TaskQueue

from core.task_generator import TaskGenerator
from core.reasoning import KnowledgeReasoner


class EvolutionLayer:
    """自驱进化层：知识驱动任务生成与系统进化"""

    def __init__(self, kg: "KnowledgeGraph", task_queue: "TaskQueue"):
        self.kg = kg
        self.task_queue = task_queue
        self.task_generator = TaskGenerator(kg)
        self.reasoner = KnowledgeReasoner(kg)
        self.evolution_count = 0
        self.last_evolution_time = 0

    def evolve(self) -> dict:
        """执行一次进化迭代"""
        self.evolution_count += 1

        stats = {
            "evolution_count": self.evolution_count,
            "tasks_generated": 0,
            "knowledge_created": 0
        }

        # 1. 从知识图谱推演新任务
        derived_tasks = self.reasoner.derive_from_all_nodes(limit=5)
        added = self.task_queue.add_batch_unique(derived_tasks)
        stats["tasks_generated"] += added

        # 2. 使用任务生成器生成新任务
        new_tasks = self.task_generator.generate_new_tasks(count=5)
        added = self.task_queue.add_batch_unique(new_tasks)
        stats["tasks_generated"] += added

        # 3. 生成知识巩固任务
        consolidation_tasks = self._generate_consolidation_tasks()
        added = self.task_queue.add_batch_unique(consolidation_tasks)
        stats["tasks_generated"] += added

        # 4. 记录进化事件
        self._record_evolution_event(stats)

        print(f"[进化迭代 {self.evolution_count}] 生成 {stats['tasks_generated']} 个新任务")

        return stats

    def _generate_consolidation_tasks(self) -> list[str]:
        """生成知识巩固任务"""
        tasks = []

        low_weight_edges = [e for e in self.kg.edges if 0.1 < e.weight < 0.3]

        if low_weight_edges:
            sample_size = min(3, len(low_weight_edges))
            sample = random.sample(low_weight_edges, sample_size)
            for edge in sample:
                task = f"巩固关联_{edge.source}_{edge.relation}_{edge.target}"
                tasks.append(task)

        return tasks

    def _record_evolution_event(self, stats: dict):
        """记录进化事件到知识图谱"""
        self.kg.add_node(
            f"进化迭代_{self.evolution_count}",
            {
                "type": "evolution_event",
                "tasks_generated": stats["tasks_generated"],
                "timestamp": self._get_timestamp()
            }
        )

        if self.evolution_count > 1:
            self.kg.add_edge(
                f"进化迭代_{self.evolution_count - 1}",
                f"进化迭代_{self.evolution_count}",
                "进化链",
                0.9
            )

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()

    def get_evolution_status(self) -> dict:
        """获取进化状态"""
        return {
            "evolution_count": self.evolution_count,
            "task_generator_strategies": len(self.task_generator.generation_strategies),
            "knowledge_nodes": len(self.kg.nodes),
            "knowledge_edges": len(self.kg.edges),
            "pending_tasks": self.task_queue.size()
        }

    def idle_evolve(self, iterations: int = 3) -> dict:
        """空闲时进化：系统无任务时执行自我进化"""
        total_stats = {
            "iterations": iterations,
            "total_tasks_generated": 0
        }

        for i in range(iterations):
            stats = self.evolve()
            total_stats["total_tasks_generated"] += stats["tasks_generated"]

        print(f"[空闲进化] 完成 {iterations} 次迭代，生成 {total_stats['total_tasks_generated']} 个任务")

        return total_stats

    def adaptive_evolve(self, system_state: dict) -> dict:
        """自适应进化：根据系统状态调整进化策略"""
        queue_size = system_state.get("task_queue_size", 0)
        memory_percent = system_state.get("memory_percent", 0)

        stats = self.evolve()

        # 队列空或接近空，需要大量生成
        if queue_size < 3:
            stats["strategy"] = "aggressive"
        # 内存压力大，少量生成
        elif memory_percent > 80:
            stats["strategy"] = "conservative"
            stats["tasks_generated"] = min(stats["tasks_generated"], 2)
        # 正常情况
        else:
            stats["strategy"] = "balanced"

        return stats
