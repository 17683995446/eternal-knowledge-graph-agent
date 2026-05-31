"""
基于第一性原理，轻量化永动知识图谱智能体 - 任务生成器
自驱公理核心实现：知识驱动自动生成任务
"""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.knowledge_graph import KnowledgeGraph

from core.reasoning import KnowledgeReasoner


class TaskGenerator:
    """任务衍生器：知识驱动自动生成任务"""

    def __init__(self, kg: "KnowledgeGraph"):
        self.kg = kg
        self.reasoner = KnowledgeReasoner(kg)
        self.generation_strategies = [
            self._generate_from_high_weight_edges,
            self._generate_from_chain_reasoning,
            self._generate_from_patterns,
            self._generate_from_subgraph_exploration,
            self._generate_existing_node_review
        ]

    def generate_new_tasks(self, count: int = 5) -> list[str]:
        """自驱公理：自动生成新任务"""
        tasks = []

        strategies_count = min(3, len(self.generation_strategies))
        selected_strategies = random.sample(self.generation_strategies, strategies_count)
        for strategy in selected_strategies:
            generated = strategy()
            tasks.extend(generated)

        unique_tasks = list(dict.fromkeys(tasks))

        return unique_tasks[:count]

    def _generate_from_high_weight_edges(self) -> list[str]:
        """策略1：从高权重边生成任务"""
        tasks = []

        sorted_edges = sorted(self.kg.edges, key=lambda e: e.weight, reverse=True)[:5]

        for edge in sorted_edges:
            if edge.weight > 0.5:
                task = f"探索关联_{edge.source}_{edge.relation}_{edge.target}"
                tasks.append(task)

        return tasks

    def _generate_from_chain_reasoning(self) -> list[str]:
        """策略2：从链式推理生成任务"""
        tasks = []

        valid_nodes = [n for n in self.kg.nodes.values() if n.valid]
        if not valid_nodes:
            return tasks

        start_node = random.choice(valid_nodes).name
        chains = self.reasoner.chain_reasoning(start_node, depth=2)

        for chain in chains[:3]:
            if chain["weight"] > 0.3:
                path = chain["path"]
                if path:
                    task = f"推理验证_{'_'.join([p[0] for p in path])}"
                    tasks.append(task)

        return tasks

    def _generate_from_patterns(self) -> list[str]:
        """策略3：从频繁模式生成任务"""
        tasks = []

        patterns = self.reasoner.mine_patterns()

        for relation, count in patterns[:2]:
            if count >= 2:
                task = f"模式验证_{relation}_出现{count}次"
                tasks.append(task)

        return tasks

    def _generate_from_subgraph_exploration(self) -> list[str]:
        """策略4：从子图探索生成任务"""
        tasks = []

        node_degrees = {}
        for edge in self.kg.edges:
            node_degrees[edge.source] = node_degrees.get(edge.source, 0) + 1
            node_degrees[edge.target] = node_degrees.get(edge.target, 0) + 1

        top_nodes = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)[:3]

        for node, degree in top_nodes:
            subgraph_nodes, subgraph_edges = self.kg.get_subgraph([node], depth=1)
            if len(subgraph_nodes) > 2:
                task = f"子图分析_{node}_连接{degree}个节点"
                tasks.append(task)

        return tasks

    def _generate_existing_node_review(self) -> list[str]:
        """策略5：生成现有节点复盘任务"""
        tasks = []

        valid_nodes = [n for n in self.kg.nodes.values() if n.valid]
        if len(valid_nodes) > 0:
            sample_size = min(5, len(valid_nodes))
            sample_nodes = random.sample(valid_nodes, sample_size)

            for node in sample_nodes:
                associations = self.kg.find_strong_associations(node.name, threshold=0.3)
                if associations:
                    task = f"复盘回顾_{node.name}_包含{len(associations)}个关联"
                    tasks.append(task)

        return tasks

    def generate_adaptive_tasks(self, system_state: dict) -> list[str]:
        """根据系统状态自适应生成任务"""
        tasks = []

        queue_size = system_state.get("task_queue_size", 0)
        node_count = system_state.get("knowledge_nodes", 0)
        edge_count = system_state.get("knowledge_edges", 0)

        if queue_size < 5:
            tasks.extend(self._generate_exploration_tasks())

        if node_count < 10:
            tasks.extend(self._generate_knowledge_acquisition_tasks())

        if edge_count < node_count * 0.5 and node_count > 5:
            tasks.extend(self._generate_association_tasks())

        if not tasks:
            tasks = self.generate_new_tasks(count=3)

        return tasks

    def _generate_exploration_tasks(self) -> list[str]:
        """生成探索任务"""
        return [
            "探索_随机节点关联",
            "探索_新知识领域",
            "探索_跨领域连接"
        ]

    def _generate_knowledge_acquisition_tasks(self) -> list[str]:
        """生成知识积累任务"""
        return [
            "积累_创建新认知节点",
            "积累_建立初始关联",
            "积累_扩展知识边界"
        ]

    def _generate_association_tasks(self) -> list[str]:
        """生成关联发现任务"""
        return [
            "关联_发现隐含连接",
            "关联_强化现有关系",
            "关联_推理传递关系"
        ]

    def generate_startup_tasks(self) -> list[str]:
        """生成启动任务：系统第一次运行时"""
        return [
            "系统初始认知迭代",
            "建立基础认知网络",
            "设置初始关联权重"
        ]
