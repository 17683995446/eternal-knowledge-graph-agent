"""
基于第一性原理，轻量化永动知识图谱智能体 - 知识推演引擎
自驱公理核心实现：基于已有知识自动生成新认知
"""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.knowledge_graph import KnowledgeGraph

from core.constants import WEIGHT_HIGH


class KnowledgeReasoner:
    """知识推演引擎：基于已有知识生成新认知"""

    def __init__(self, kg: "KnowledgeGraph"):
        self.kg = kg

    def derive_from_node(self, node_name: str) -> list[tuple]:
        """自驱公理：基于已有知识推演新生任务"""
        return self.kg.find_strong_associations(node_name, threshold=WEIGHT_HIGH)

    def derive_from_all_nodes(self, limit: int = 10) -> list[str]:
        """从所有高价值节点推演新任务"""
        derived_tasks = []

        for node in self.kg.nodes.values():
            if not node.valid:
                continue

            associations = self.derive_from_node(node.name)

            for target, relation, weight in associations:
                task = f"知识推演_{node.name}_{relation}_{target}"
                derived_tasks.append(task)

        return list(dict.fromkeys(derived_tasks))[:limit]

    def chain_reasoning(self, start_node: str, depth: int = 2) -> list[dict]:
        """链式推理：沿路径生成推理链"""
        reasoning_chain = []

        visited = {start_node}
        current_level = [(start_node, [], 0)]

        for level in range(depth):
            next_level = []

            for current, path, weight in current_level:
                neighbors = self.kg.find_strong_associations(current, threshold=0.3)

                for neighbor, relation, edge_weight in neighbors:
                    if neighbor in visited:
                        continue

                    new_path = path + [(current, relation, neighbor)]
                    total_weight = weight * edge_weight if weight > 0 else edge_weight

                    reasoning_chain.append({
                        "path": new_path,
                        "weight": total_weight,
                        "depth": level + 1
                    })

                    next_level.append((neighbor, new_path, total_weight))
                    visited.add(neighbor)

            current_level = next_level

        return sorted(reasoning_chain, key=lambda x: x["weight"], reverse=True)

    def mine_patterns(self) -> list[tuple]:
        """挖掘频繁模式"""
        relation_counts = {}
        relation_pairs = {}

        for edge in self.kg.edges:
            relation_counts[edge.relation] = relation_counts.get(edge.relation, 0) + 1

            pair = tuple(sorted([edge.source, edge.target]))
            key = (pair, edge.relation)
            relation_pairs[key] = relation_pairs.get(key, 0) + 1

        frequent_relations = [
            (rel, count) for rel, count in relation_counts.items()
            if count >= 2
        ]

        return sorted(frequent_relations, key=lambda x: x[1], reverse=True)

    def predict_next_node(self, current_node: str, count: int = 3) -> list[tuple]:
        """预测下一个可能的节点"""
        predictions = {}

        current_associations = self.kg.find_strong_associations(current_node, threshold=0.1)

        for neighbor, relation, weight in current_associations:
            neighbor_associations = self.kg.find_strong_associations(neighbor, threshold=0.1)

            for second_neighbor, second_relation, second_weight in neighbor_associations:
                if second_neighbor == current_node:
                    continue

                key = (second_neighbor, f"{relation}->{second_relation}")
                predictions[key] = predictions.get(key, 0) + weight * second_weight

        sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        return [(k[0], k[1], v) for k, v in sorted_predictions[:count]]

    def complete_missing_links(self, node_name: str) -> list[tuple]:
        """补全缺失链接"""
        neighbors = set()

        for edge in self.kg.edges:
            if edge.source == node_name:
                neighbors.add(edge.target)
            elif edge.target == node_name:
                neighbors.add(edge.source)

        missing_links = []

        for other_node in self.kg.nodes:
            if other_node == node_name or other_node in neighbors:
                continue

            has_link = any(
                (e.source == node_name and e.target == other_node) or
                (e.target == node_name and e.source == other_node)
                for e in self.kg.edges
            )

            if not has_link:
                other_neighbors = set()
                for edge in self.kg.edges:
                    if edge.source == other_node:
                        other_neighbors.add(edge.target)
                    elif edge.target == other_node:
                        other_neighbors.add(edge.source)

                common = neighbors & other_neighbors
                if common:
                    missing_links.append((other_node, list(common)))

        return missing_links

    def generate_insights(self, node_name: str = None, limit: int = 5) -> list[dict]:
        """生成洞察：从知识图谱中发现有价值的信息"""
        insights = []

        if node_name:
            node_associations = self.kg.find_strong_associations(node_name, threshold=0.3)
            for target, relation, weight in node_associations:
                insights.append({
                    "type": "direct_association",
                    "from": node_name,
                    "to": target,
                    "relation": relation,
                    "weight": weight
                })

            missing = self.complete_missing_links(node_name)
            for target, common in missing:
                insights.append({
                    "type": "potential_link",
                    "from": node_name,
                    "to": target,
                    "via": common
                })

        patterns = self.mine_patterns()
        for relation, count in patterns[:limit]:
            insights.append({
                "type": "frequent_pattern",
                "relation": relation,
                "count": count
            })

        return insights[:limit]
