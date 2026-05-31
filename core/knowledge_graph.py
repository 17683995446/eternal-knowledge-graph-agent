"""
知识记忆层核心类
"""

import json
import os
from pathlib import Path
from datetime import datetime
import hashlib

from core.constants import KG_SAVE_PATH, WEIGHT_HIGH, WEIGHT_TRIM


class Node:
    """节点：代表一次任务、一个认知、一个实体经验"""
    def __init__(self, name: str, attr: dict = None):
        # 边界检查：name不能为空
        if not name or not isinstance(name, str):
            raise ValueError("节点名称必须是非空字符串")
        
        self.id = self._generate_id(name)
        self.name = name
        
        # 边界检查：确保 attr 是字典类型
        self.attr = {}
        if attr is not None:
            if isinstance(attr, dict):
                self.attr = attr.copy()
            else:
                self.attr = {"raw_value": str(attr)}
        
        self.created_at = self._timestamp()
        self.valid = True  # 有效状态标记

    def _generate_id(self, name: str) -> str:
        """基于名称生成唯一ID"""
        # 使用固定格式避免重复
        unique_str = f"{name}_{datetime.now().isoformat()}_{id(self)}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:12]

    def _timestamp(self) -> str:
        """获取时间戳（ISO 8601 格式）"""
        return datetime.now().isoformat()

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "attr": self.attr,
            "created_at": self.created_at,
            "valid": self.valid
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Node':
        """从字典反序列化"""
        # 完整性检查
        required_fields = ["name", "id", "created_at"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"序列化数据缺少必需字段: {field}")
        
        node = cls(data["name"], data.get("attr", {}))
        node.id = data["id"]
        node.created_at = data["created_at"]
        node.valid = data.get("valid", True)
        return node


class Edge:
    """边：代表实体间的关联逻辑，附带权重值"""
    def __init__(self, source: str, target: str, relation: str, weight: float):
        # 边界检查：source 和 target 不能为空
        if not source or not isinstance(source, str):
            raise ValueError("源节点名称必须是非空字符串")
        if not target or not isinstance(target, str):
            raise ValueError("目标节点名称必须是非空字符串")
        if not relation or not isinstance(relation, str):
            raise ValueError("关系类型必须是非空字符串")
        
        self.source = source      # 源节点名称
        self.target = target      # 目标节点名称
        self.relation = relation  # 关系类型
        
        # 权重严格归一化到 [0.0, 1.0] 区间
        self.weight = self._normalize_weight(weight)
        self.created_at = self._timestamp()

    def _normalize_weight(self, weight: float) -> float:
        """严格归一化权重到 [0.0, 1.0] 区间"""
        try:
            weight = float(weight)
            return max(0.0, min(1.0, weight))
        except (ValueError, TypeError):
            return 0.5  # 默认值

    def _timestamp(self) -> str:
        """获取时间戳（ISO 8601 格式）"""
        return datetime.now().isoformat()

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "weight": self.weight,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Edge':
        """从字典反序列化"""
        # 完整性检查
        required_fields = ["source", "target", "relation", "weight"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"边序列化数据缺少必需字段: {field}")
        
        return cls(
            data["source"],
            data["target"],
            data["relation"],
            data["weight"]
        )


class KnowledgeGraph:
    """知识记忆层核心类"""
    def __init__(self):
        self.nodes = {}  # 节点字典 {node_id: Node}
        self.edges = []  # 边列表 [Edge, ...]
        self.save_path = Path(KG_SAVE_PATH)
        self.optimizer = None  # 性能优化器实例
        
        self.load()
        
        # 初始化性能优化器
        from core.optimizations import patch_knowledge_graph
        self.optimizer = patch_knowledge_graph(self)

    def load(self):
        """记忆加载：满足记忆公理 - 重启不丢失经验"""
        if self.save_path.exists():
            try:
                with open(self.save_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 版本兼容性处理
                self._handle_version_compatibility(data)
                
                # 重建节点字典
                self.nodes = {}
                for node_data in data.get("nodes", []):
                    try:
                        node = Node.from_dict(node_data)
                        self.nodes[node.id] = node
                    except Exception as e:
                        print(f"[记忆加载] 跳过无效节点: {e}")
                
                # 重建边列表
                self.edges = []
                for edge_data in data.get("edges", []):
                    try:
                        edge = Edge.from_dict(edge_data)
                        self.edges.append(edge)
                    except Exception as e:
                        print(f"[记忆加载] 跳过无效边: {e}")
                
                print(f"[记忆加载] 成功加载 {len(self.nodes)} 个节点, {len(self.edges)} 条边")
            except (json.JSONDecodeError, KeyError, IOError, OSError) as e:
                print(f"[记忆加载] 文件损坏或格式错误: {e}")
                
                # 尝试从备份恢复
                if not self._try_load_from_backup():
                    print("[记忆加载] 无法恢复，初始化空图谱")
                    self.nodes = {}
                    self.edges = []
                    self.save()
        else:
            print("[记忆加载] 无历史记录，初始化空图谱")
            self.save()

    def _handle_version_compatibility(self, data: dict):
        """处理不同版本的兼容性"""
        version = data.get("version", "unknown")
        schema = data.get("schema", "unknown")
        
        if version != "1.0" or schema != "eternal_agent_kg_v1":
            print(f"[记忆加载] 检测到旧版本格式 (v{version}/{schema})")
            # 这里可以添加版本迁移逻辑
            # 目前我们直接按 v1 格式处理

    def save(self):
        """记忆固化：满足记忆公理 - 所有行为永久结构化留存"""
        # 确保目录存在
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "version": "1.0",
            "schema": "eternal_agent_kg_v1",
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
            "saved_at": datetime.now().isoformat(),
            "node_count": len(self.nodes),
            "edge_count": len(self.edges)
        }
        
        self._save_atomic(data)

    def _save_atomic(self, data: dict):
        """原子写入：先写临时文件，再重命名，防止写入中断导致文件损坏"""
        import shutil
        
        temp_path = self.save_path.with_suffix('.tmp')
        backup_path = self.save_path.with_suffix('.bak')
        
        # 写入临时文件
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 如果主文件存在，先备份
        if self.save_path.exists():
            try:
                if backup_path.exists():
                    backup_path.unlink()  # 删除旧备份
                shutil.copy(str(self.save_path), str(backup_path))
            except Exception as e:
                print(f"[记忆存储] 备份警告: {e}")
        
        # 原子替换
        shutil.move(str(temp_path), str(self.save_path))

    def _try_load_from_backup(self) -> bool:
        """尝试从备份文件加载数据"""
        backup_path = self.save_path.with_suffix('.bak')
        
        if backup_path.exists():
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 重建数据
                self.nodes = {}
                for node_data in data.get("nodes", []):
                    try:
                        node = Node.from_dict(node_data)
                        self.nodes[node.id] = node
                    except Exception as e:
                        print(f"[备份加载] 跳过节点: {e}")
                
                self.edges = []
                for edge_data in data.get("edges", []):
                    try:
                        edge = Edge.from_dict(edge_data)
                        self.edges.append(edge)
                    except Exception as e:
                        print(f"[备份加载] 跳过边: {e}")
                
                print(f"[备份加载] 成功从备份恢复 {len(self.nodes)} 个节点, {len(self.edges)} 条边")
                return True
            except Exception as e:
                print(f"[备份加载] 备份也无法使用: {e}")
                return False
        
        return False

    def _timestamp(self) -> str:
        """获取时间戳（ISO 8601 格式）"""
        return datetime.now().isoformat()

    def add_node(self, name: str, attr: dict = None) -> Node:
        """新增认知实体"""
        # 检查是否已存在同名节点
        existing = self._get_node_by_name(name)
        if existing:
            return existing
        
        node = Node(name, attr)
        self.nodes[node.id] = node
        print(f"[节点创建] {name} (ID: {node.id})")
        self.save()
        return node

    def _get_node_by_name(self, name: str) -> Node | None:
        """根据名称查找节点"""
        for node in self.nodes.values():
            if node.name == name:
                return node
        return None

    def get_node(self, node_id: str) -> Node | None:
        """根据ID获取节点"""
        return self.nodes.get(node_id)

    def add_edge(self, source: str, target: str, relation: str, weight: float) -> Edge:
        """新增加权关系（智能迭代核心）"""
        # 自动保证头尾实体存在（记忆公理推导）
        self.add_node(source)
        self.add_node(target)
        
        # 检查是否已存在相同关系
        existing = self._get_edge(source, target, relation)
        if existing:
            # 存在则更新权重（知识强化）
            existing.weight = max(existing.weight, weight)
            self.save()
            return existing
        
        edge = Edge(source, target, relation, weight)
        self.edges.append(edge)
        print(f"[边创建] {source} --[{relation}:{weight}]--> {target}")
        self.save()
        return edge

    def _get_edge(self, source: str, target: str, relation: str) -> Edge | None:
        """查找是否存在指定关系"""
        for edge in self.edges:
            if edge.source == source and edge.target == target and edge.relation == relation:
                return edge
        return None

    def derive_new_tasks(self, node_name: str) -> list:
        """自驱核心：基于已有知识推演新生任务（永动来源）"""
        new_tasks = []
        for edge in self.edges:
            # 只采信高价值、高权重关联
            if edge.source == node_name and edge.weight > WEIGHT_HIGH:
                new_tasks.append(f"知识推演任务:{edge.target}")
        # 去重
        return list(dict.fromkeys(new_tasks))

    def _trim_low_weight_edges(self):
        """移除低权重边"""
        from core.constants import WEIGHT_TRIM
        before = len(self.edges)
        self.edges = [e for e in self.edges if e.weight > WEIGHT_TRIM]
        after = len(self.edges)
        
        if before > after:
            print(f"[知识精简] 移除 {before - after} 条低权重边")

    def _trim_invalid_nodes(self):
        """移除无效节点"""
        connected_nodes = set()
        for edge in self.edges:
            connected_nodes.add(edge.source)
            connected_nodes.add(edge.target)
        
        nodes_to_remove = []
        for node_id, node in self.nodes.items():
            if not node.valid and node.name not in connected_nodes:
                nodes_to_remove.append(node_id)
        
        for node_id in nodes_to_remove:
            del self.nodes[node_id]
        
        if nodes_to_remove:
            print(f"[知识精简] 移除 {len(nodes_to_remove)} 个无效孤立节点")

    # ==========================================
    # 查询方法
    # ==========================================
    def get_edges_from(self, node_name: str) -> list:
        """获取从指定节点出发的所有边"""
        return [e for e in self.edges if e.source == node_name]

    def get_edges_to(self, node_name: str) -> list:
        """获取指向指定节点的所有边"""
        return [e for e in self.edges if e.target == node_name]

    def get_neighbors(self, node_name: str, threshold: float = 0.0) -> list:
        """获取邻居节点及其关系"""
        neighbors = []
        for edge in self.edges:
            if edge.source == node_name and edge.weight >= threshold:
                neighbors.append((edge.target, edge.relation, edge.weight))
            elif edge.target == node_name and edge.weight >= threshold:
                neighbors.append((edge.source, edge.relation, edge.weight))
        return neighbors

    def get_node_by_name(self, name: str) -> Node | None:
        """根据名称获取节点（公开方法）"""
        return self._get_node_by_name(name)

    def get_all_nodes(self) -> list:
        """获取所有节点"""
        return list(self.nodes.values())

    def get_all_edges(self) -> list:
        """获取所有边"""
        return self.edges

    # ==========================================
    # 删除和更新方法
    # ==========================================
    def delete_node(self, node_name: str) -> bool:
        """删除节点及其关联边"""
        node = self._get_node_by_name(node_name)
        if not node:
            return False
        
        # 删除节点
        del self.nodes[node.id]
        
        # 删除相关边
        original_count = len(self.edges)
        self.edges = [
            e for e in self.edges
            if e.source != node_name and e.target != node_name
        ]
        
        deleted_edges = original_count - len(self.edges)
        self.save()
        
        print(f"[节点删除] {node_name}（清理了{deleted_edges}条边）")
        return True

    def delete_edge(self, source: str, target: str, relation: str) -> bool:
        """删除指定边"""
        original_count = len(self.edges)
        self.edges = [
            e for e in self.edges
            if not (e.source == source and e.target == target and e.relation == relation)
        ]
        
        if len(self.edges) < original_count:
            self.save()
            print(f"[边删除] {source} --[{relation}]--> {target}")
            return True
        
        return False

    def update_node_attr(self, node_name: str, attr: dict) -> bool:
        """更新节点属性"""
        node = self._get_node_by_name(node_name)
        if not node:
            return False
        
        node.attr.update(attr)
        self.save()
        print(f"[节点更新] {node_name} 属性已更新")
        return True

    def invalidate_node(self, node_name: str) -> bool:
        """标记节点为无效（软删除）"""
        node = self._get_node_by_name(node_name)
        if not node:
            return False
        
        node.valid = False
        self.save()
        print(f"[节点无效化] {node_name}")
        return True

    def reinforce_edge(self, source: str, target: str, relation: str, boost: float = 0.1) -> bool:
        """强化边权重"""
        edge = self._get_edge(source, target, relation)
        if not edge:
            return False
        
        edge.weight = min(1.0, edge.weight + boost)
        self.save()
        print(f"[边强化] {source} --[{relation}]--> {target} 权重提升至 {edge.weight:.2f}")
        return True

    def weaken_edge(self, source: str, target: str, relation: str, penalty: float = 0.1) -> bool:
        """弱化边权重"""
        edge = self._get_edge(source, target, relation)
        if not edge:
            return False

        edge.weight = max(0.0, edge.weight - penalty)
        self.save()
        print(f"[边弱化] {source} --[{relation}]--> {target} 权重降至 {edge.weight:.2f}")
        return True

    # ==========================================
    # 权重计算与更新
    # ==========================================
    def calculate_edge_weight(
        self,
        source: str,
        target: str,
        base_weight: float = 0.5,
        frequency_boost: float = 0.1,
        recency_boost: float = 0.05
    ) -> float:
        """计算边权重"""
        # 1. 获取基础权重
        weight = base_weight

        # 2. 频率加成：相同关系出现次数越多，权重越高
        edge_count = sum(
            1 for e in self.edges
            if e.source == source and e.target == target
        )
        weight += frequency_boost * min(edge_count - 1, 5)  # 最多加成0.5

        return min(1.0, max(0.0, weight))

    def update_edge_weight(self, source: str, target: str, relation: str, delta: float) -> bool:
        """更新边权重"""
        edge = self._get_edge(source, target, relation)
        if not edge:
            return False

        edge.weight = min(1.0, max(0.0, edge.weight + delta))
        self.save()
        return True

    # ==========================================
    # 关联推理
    # ==========================================
    def find_strong_associations(self, node_name: str, threshold: float = None) -> list[tuple]:
        """查找强关联关系"""
        if threshold is None:
            from core.constants import WEIGHT_HIGH
            threshold = WEIGHT_HIGH

        strong_edges = [
            e for e in self.edges
            if (e.source == node_name or e.target == node_name) and e.weight >= threshold
        ]

        associations = []
        for edge in strong_edges:
            if edge.source == node_name:
                associations.append((edge.target, edge.relation, edge.weight))
            else:
                associations.append((edge.source, edge.relation, edge.weight))

        return sorted(associations, key=lambda x: x[2], reverse=True)

    def find_path(self, start: str, end: str, max_depth: int = 3) -> list[list[str]] | None:
        """查找两节点间的路径（BFS）"""
        if start == end:
            return [[start]]

        visited = {start}
        queue = [(start, [start])]

        while queue:
            current, path = queue.pop(0)

            if len(path) > max_depth:
                continue

            for edge in self.edges:
                neighbor = None
                if edge.source == current and edge.target not in visited:
                    neighbor = edge.target
                elif edge.target == current and edge.source not in visited:
                    neighbor = edge.source

                if neighbor:
                    new_path = path + [neighbor]
                    if neighbor == end:
                        return [new_path]

                    visited.add(neighbor)
                    queue.append((neighbor, new_path))

        return None

    def infer_new_relations(self, node_name: str) -> list[tuple]:
        """基于传递性推理新关系"""
        inferred = []

        # 获取直接关联
        direct = self.find_strong_associations(node_name, threshold=0.3)

        for neighbor, relation, weight in direct:
            # 获取邻居的关联
            neighbor_associations = self.find_strong_associations(neighbor, threshold=0.3)

            for second_neighbor, second_relation, second_weight in neighbor_associations:
                if second_neighbor == node_name:
                    continue

                # 通过传递性推断新关系
                inferred_weight = weight * second_weight
                if inferred_weight >= 0.2:
                    inferred.append((second_neighbor, f"{relation}+{second_relation}", inferred_weight))

        return inferred

    # ==========================================
    # 图遍历算法
    # ==========================================
    def bfs_traverse(self, start: str, max_depth: int = 2) -> list[tuple]:
        """广度优先遍历"""
        result = []
        visited = {start}
        queue = [(start, 0)]

        while queue:
            current, depth = queue.pop(0)

            if depth > max_depth:
                continue

            for edge in self.edges:
                if edge.source == current and edge.target not in visited:
                    result.append((edge.target, edge.relation, edge.weight, depth + 1))
                    visited.add(edge.target)
                    queue.append((edge.target, depth + 1))
                elif edge.target == current and edge.source not in visited:
                    result.append((edge.source, edge.relation, edge.weight, depth + 1))
                    visited.add(edge.source)
                    queue.append((edge.source, depth + 1))

        return result

    def get_subgraph(self, center_nodes: list[str], depth: int = 1) -> tuple:
        """获取以指定节点为中心的子图"""
        relevant_nodes = set(center_nodes)
        relevant_edges = []

        for _ in range(depth):
            new_nodes = set()
            for edge in self.edges:
                if edge.source in relevant_nodes:
                    new_nodes.add(edge.target)
                    relevant_edges.append(edge)
                elif edge.target in relevant_nodes:
                    new_nodes.add(edge.source)
                    relevant_edges.append(edge)
            relevant_nodes.update(new_nodes)

        return relevant_nodes, relevant_edges

    def _merge_duplicate_edges(self):
        """合并重复边"""
        seen = {}
        merged_count = 0

        for edge in self.edges:
            key = (edge.source, edge.target, edge.relation)
            if key in seen:
                if edge.weight > seen[key].weight:
                    seen[key].weight = edge.weight
                merged_count += 1
            else:
                seen[key] = edge

        self.edges = list(seen.values())

        if merged_count > 0:
            print(f"[知识精简] 合并 {merged_count} 条重复边")

    def smart_trim(self, strategy: str = "balanced") -> dict:
        """智能淘汰策略"""
        from core.constants import WEIGHT_TRIM, WEIGHT_HIGH

        if strategy == "conservative":
            threshold = WEIGHT_TRIM
            keep_isolated_valid = True
        elif strategy == "aggressive":
            threshold = WEIGHT_HIGH
            keep_isolated_valid = False
        else:  # balanced
            threshold = (WEIGHT_TRIM + WEIGHT_HIGH) / 2
            keep_isolated_valid = True

        original_counts = (len(self.nodes), len(self.edges))

        connected_nodes = set()
        for edge in self.edges:
            if edge.weight > threshold:
                connected_nodes.add(edge.source)
                connected_nodes.add(edge.target)

        new_nodes = {}
        for node_id, node in self.nodes.items():
            if node.valid or node.name in connected_nodes:
                new_nodes[node_id] = node
            elif keep_isolated_valid and node.valid:
                new_nodes[node_id] = node

        self.nodes = new_nodes
        self.edges = [e for e in self.edges if e.weight > threshold]

        self.save()

        result = {
            "strategy": strategy,
            "nodes_removed": original_counts[0] - len(self.nodes),
            "edges_removed": original_counts[1] - len(self.edges),
            "remaining_nodes": len(self.nodes),
            "remaining_edges": len(self.edges)
        }

        self.record_trim(result)
        return result

    def age_based_trim(self, max_age_days: int = 30) -> dict:
        """基于时间的淘汰"""
        from datetime import datetime, timedelta

        cutoff_time = (datetime.now() - timedelta(days=max_age_days)).isoformat()

        old_edges = [e for e in self.edges if e.created_at < cutoff_time]
        important_old_edges = [e for e in old_edges if e.weight > 0.6]

        self.edges = [
            e for e in self.edges
            if e.created_at >= cutoff_time or e.weight > 0.6
        ]

        self.save()

        result = {
            "type": "age_based",
            "old_edges_found": len(old_edges),
            "important_kept": len(important_old_edges),
            "removed": len(old_edges) - len(important_old_edges)
        }

        self.record_trim(result)
        return result

    def get_trim_history(self) -> list[dict]:
        """获取淘汰历史"""
        if not hasattr(self, '_trim_history'):
            self._trim_history = []
        return self._trim_history

    def record_trim(self, stats: dict):
        """记录淘汰事件"""
        if not hasattr(self, '_trim_history'):
            self._trim_history = []

        from datetime import datetime
        stats['timestamp'] = datetime.now().isoformat()
        self._trim_history.append(stats)

        if len(self._trim_history) > 100:
            self._trim_history = self._trim_history[-100:]

    def trim_invalid_knowledge(self) -> dict:
        """自驱公理：自动淘汰低价值知识，防臃肿老化"""
        original_node_count = len(self.nodes)
        original_edge_count = len(self.edges)
        
        self._trim_low_weight_edges()
        self._trim_invalid_nodes()
        self._merge_duplicate_edges()
        
        self.save()
        
        result = {
            "trimmed_nodes": original_node_count - len(self.nodes),
            "trimmed_edges": original_edge_count - len(self.edges),
            "remaining_nodes": len(self.nodes),
            "remaining_edges": len(self.edges)
        }
        
        self.record_trim(result)
        return result

    # --- 语义增强功能 ---
    def init_semantic_search(self):
        """初始化语义搜索和导出功能"""
        from core.semantic import SemanticSearch, KnowledgeExporter
        self.semantic_search = SemanticSearch(self)
        self.exporter = KnowledgeExporter(self)
        print("[语义初始化] 语义搜索和导出功能已启用")

    def semantic_search_nodes(self, query: str, top_k: int = 10):
        """语义搜索节点"""
        if not hasattr(self, 'semantic_search'):
            self.init_semantic_search()
        return self.semantic_search.semantic_search(query, top_k)

    def find_similar_nodes(self, node_name: str, top_k: int = 5):
        """查找相似节点"""
        if not hasattr(self, 'semantic_search'):
            self.init_semantic_search()
        return self.semantic_search.find_similar_nodes(node_name, top_k)

    def update_node_vector(self, node_id: str, node_name: str, node_attr=None):
        """更新节点向量"""
        if not hasattr(self, 'semantic_search'):
            self.init_semantic_search()
        self.semantic_search.add_node_vector(node_id, node_name, node_attr)

    def export_to_json_ld(self):
        """导出为JSON-LD"""
        if not hasattr(self, 'exporter'):
            self.init_semantic_search()
        return self.exporter.export_json_ld()

    def export_to_turtle(self):
        """导出为Turtle"""
        if not hasattr(self, 'exporter'):
            self.init_semantic_search()
        return self.exporter.export_turtle()

    def export_to_graphviz(self):
        """导出为Graphviz"""
        if not hasattr(self, 'exporter'):
            self.init_semantic_search()
        return self.exporter.export_graphviz()

    def export_to_markdown(self):
        """导出为Markdown"""
        if not hasattr(self, 'exporter'):
            self.init_semantic_search()
        return self.exporter.export_markdown()

    # 重写add_node以自动更新向量
    def add_node(self, name: str, attr: dict = None):
        """新增认知实体"""
        # 检查是否已存在同名节点
        existing = self._get_node_by_name(name)
        if existing:
            return existing
        
        node = Node(name, attr)
        self.nodes[node.id] = node
        print(f"[节点创建] {name} (ID: {node.id})")
        self.save()
        
        # 自动更新语义索引
        if hasattr(self, 'semantic_search'):
            self.semantic_search.add_node_vector(node.id, name, attr)
            
        return node
