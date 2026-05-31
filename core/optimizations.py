"""
基于第一性原理，轻量化永动知识图谱智能体 - 性能优化模块
包含性能优化、资源管理等功能
"""

import time
from typing import Dict, Any, Optional
from core.knowledge_graph import KnowledgeGraph


class PerformanceOptimizer:
    """性能优化器，提供各种性能优化功能"""

    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
        self._node_name_index: Dict[str, str] = {}  # 节点名 -> 节点ID索引
        self._outgoing_edges: Dict[str, list] = {}  # 节点名 -> 出边列表
        self._incoming_edges: Dict[str, list] = {}  # 节点名 -> 入边列表
        self._dirty: bool = False
        self._last_save_time: float = 0
        self._pending_saves: int = 0
        self._save_interval: float = 5.0  # 保存间隔（秒）
        self._batch_size: int = 10  # 批量保存大小

        # 初始化索引
        self._rebuild_indices()

    def _rebuild_indices(self):
        """重建所有索引"""
        # 重建节点名索引
        self._node_name_index.clear()
        for node_id, node in self.kg.nodes.items():
            self._node_name_index[node.name] = node_id

        # 重建边索引
        self._outgoing_edges.clear()
        self._incoming_edges.clear()

        # 初始化所有节点的空列表
        for node_name in self._node_name_index.keys():
            self._outgoing_edges[node_name] = []
            self._incoming_edges[node_name] = []

        # 填充边索引
        for edge in self.kg.edges:
            if edge.source in self._outgoing_edges:
                self._outgoing_edges[edge.source].append(edge)
            if edge.target in self._incoming_edges:
                self._incoming_edges[edge.target].append(edge)

    def get_node_by_name_fast(self, name: str):
        """快速根据节点名获取节点"""
        node_id = self._node_name_index.get(name)
        if node_id:
            return self.kg.nodes.get(node_id)
        return None

    def update_edge_indices(self, edge):
        """更新边索引"""
        # 更新出边索引
        if edge.source not in self._outgoing_edges:
            self._outgoing_edges[edge.source] = []
        self._outgoing_edges[edge.source].append(edge)

        # 更新入边索引
        if edge.target not in self._incoming_edges:
            self._incoming_edges[edge.target] = []
        self._incoming_edges[edge.target].append(edge)

    def update_node_index(self, node):
        """更新节点索引"""
        self._node_name_index[node.name] = node.id
        if node.name not in self._outgoing_edges:
            self._outgoing_edges[node.name] = []
        if node.name not in self._incoming_edges:
            self._incoming_edges[node.name] = []

    def save_lazy(self):
        """延迟保存：减少IO频率"""
        self._dirty = True
        current_time = time.time()
        time_since_last_save = current_time - self._last_save_time

        # 如果距离上次保存超过间隔时间，强制保存
        if time_since_last_save > self._save_interval or self._dirty:
            self.kg.save()
            self._dirty = False
            self._last_save_time = current_time
            self._pending_saves = 0

    def save_batch(self):
        """批量保存"""
        self._pending_saves += 1
        if self._pending_saves >= self._batch_size:
            # 使用原始保存方法，避免递归
            if hasattr(self.kg, '_original_save'):
                self.kg._original_save()
            else:
                # 如果没有原始保存引用，使用当前的方法（但可能有风险）
                self.kg.save()
            self._pending_saves = 0
            self._last_save_time = time.time()

    def force_save(self):
        """强制保存"""
        # 使用原始保存方法，避免递归
        if hasattr(self.kg, '_original_save'):
            self.kg._original_save()
        else:
            self.kg.save()
        self._dirty = False
        self._pending_saves = 0
        self._last_save_time = time.time()

    def optimize_memory(self):
        """内存优化"""
        # 清理临时数据结构（如果有的话）

        # 压缩节点属性：移除空属性
        for node in self.kg.nodes.values():
            if hasattr(node, 'attr') and isinstance(node.attr, dict):
                # 移除值为None或空字符串的属性
                node.attr = {
                    k: v for k, v in node.attr.items()
                    if v is not None and v != ""
                }

        # 清理已完成任务的临时记录
        if hasattr(self.kg, 'task_queue'):
            if hasattr(self.kg.task_queue, 'completed'):
                max_completed_history = 1000
                completed_set = self.kg.task_queue.completed
                if isinstance(completed_set, set) and len(completed_set) > max_completed_history:
                    # 将集合转换为列表，保留最近的项目
                    completed_list = list(completed_set)
                    self.kg.task_queue.completed = set(completed_list[-max_completed_history:])

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        return {
            "node_count": len(self.kg.nodes),
            "edge_count": len(self.kg.edges),
            "indexed_nodes": len(self._node_name_index),
            "is_dirty": self._dirty,
            "pending_saves": self._pending_saves,
            "time_since_last_save": time.time() - self._last_save_time
        }


def patch_knowledge_graph(kg: KnowledgeGraph) -> PerformanceOptimizer:
    """为知识图谱打补丁，添加优化功能"""
    # 首先保存原始方法，避免被覆盖后无法访问
    if not hasattr(kg, '_original_add_node'):
        kg._original_add_node = kg.add_node
    if not hasattr(kg, '_original_add_edge'):
        kg._original_add_edge = kg.add_edge
    if not hasattr(kg, '_original_save'):
        kg._original_save = kg.save

    optimizer = PerformanceOptimizer(kg)

    # 重写 add_node 方法，自动更新索引
    def optimized_add_node(name: str, attr: Optional[dict] = None):
        node = kg._original_add_node(name, attr)
        optimizer.update_node_index(node)
        return node

    # 重写 add_edge 方法，自动更新索引
    def optimized_add_edge(source: str, target: str, relation: str, weight: float):
        edge = kg._original_add_edge(source, target, relation, weight)
        optimizer.update_edge_indices(edge)
        return edge

    # 重写 save 方法，支持延迟保存（避免无限递归）
    def optimized_save():
        # 直接调用原始保存，不触发save_batch
        return kg._original_save()

    # 应用补丁
    kg.add_node = optimized_add_node
    kg.add_edge = optimized_add_edge
    kg.save = optimized_save

    # 添加优化器引用
    kg.optimizer = optimizer

    return optimizer
