"""
知识冲突检测与解决 - 阶段28
支持检测重复知识、冲突知识，并提供解决策略
"""
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ConflictType(Enum):
    """冲突类型"""
    DUPLICATE_NODE = "duplicate_node"
    DUPLICATE_EDGE = "duplicate_edge"
    CONFLICTING_EDGE = "conflicting_edge"
    INCONSISTENT_ATTRS = "inconsistent_attrs"
    WEIGHT_CONFLICT = "weight_conflict"


class ResolutionStrategy(Enum):
    """解决策略"""
    KEEP_NEWEST = "keep_newest"
    KEEP_HIGHEST_WEIGHT = "keep_highest_weight"
    KEEP_OLDEST = "keep_oldest"
    MERGE = "merge"
    MANUAL = "manual"


@dataclass
class Conflict:
    """冲突记录"""
    conflict_id: str
    conflict_type: ConflictType
    items: List[Any]
    description: str
    timestamp: str = None
    resolution: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ResolutionResult:
    """解决结果"""
    conflict_id: str
    strategy_used: ResolutionStrategy
    items_removed: List[str]
    items_kept: List[str]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class KnowledgeConflictResolver:
    """知识冲突解决器"""
    
    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph
        self.conflicts = []
        self.resolution_history = []
    
    def detect_all_conflicts(self):
        """检测所有冲突"""
        self.conflicts = []
        self.conflicts.extend(self._detect_duplicate_nodes())
        self.conflicts.extend(self._detect_duplicate_edges())
        self.conflicts.extend(self._detect_conflicting_edges())
        return self.conflicts
    
    def _detect_duplicate_nodes(self):
        """检测重复节点"""
        conflicts = []
        name_to_nodes = {}
        
        for node in self.kg.nodes.values():
            if node.name not in name_to_nodes:
                name_to_nodes[node.name] = []
            name_to_nodes[node.name].append(node)
        
        for name, nodes in name_to_nodes.items():
            if len(nodes) > 1:
                conflict = Conflict(
                    conflict_id="dup_node_" + name,
                    conflict_type=ConflictType.DUPLICATE_NODE,
                    items=nodes,
                    description="Found " + str(len(nodes)) + " nodes with same name"
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def _detect_duplicate_edges(self):
        """检测重复边"""
        conflicts = []
        edge_key_to_edges = {}
        
        for edge in self.kg.edges:
            edge_key = edge.source + "_" + edge.target + "_" + edge.relation
            if edge_key not in edge_key_to_edges:
                edge_key_to_edges[edge_key] = []
            edge_key_to_edges[edge_key].append(edge)
        
        for edge_key, edges in edge_key_to_edges.items():
            if len(edges) > 1:
                conflict = Conflict(
                    conflict_id="dup_edge_" + edge_key,
                    conflict_type=ConflictType.DUPLICATE_EDGE,
                    items=edges,
                    description="Found " + str(len(edges)) + " duplicate edges"
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def _detect_conflicting_edges(self):
        """检测冲突边"""
        conflicts = []
        pair_to_edges = {}
        
        for edge in self.kg.edges:
            pair = (edge.source, edge.target)
            if pair not in pair_to_edges:
                pair_to_edges[pair] = []
            pair_to_edges[pair].append(edge)
        
        for (source, target), edges in pair_to_edges.items():
            if len(edges) > 1:
                relations = set(e.relation for e in edges)
                if len(relations) > 1:
                    conflict = Conflict(
                        conflict_id="conflict_edge_" + source + "_" + target,
                        conflict_type=ConflictType.CONFLICTING_EDGE,
                        items=edges,
                        description="Found conflicting edges with different relations"
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def resolve_conflict(self, conflict, strategy=None):
        """解决冲突"""
        if strategy is None:
            strategy = ResolutionStrategy.KEEP_NEWEST
        
        result = None
        
        if conflict.conflict_type in [ConflictType.DUPLICATE_NODE, ConflictType.DUPLICATE_EDGE]:
            if strategy == ResolutionStrategy.KEEP_NEWEST:
                result = self._resolve_keep_newest(conflict)
            elif strategy == ResolutionStrategy.KEEP_OLDEST:
                result = self._resolve_keep_oldest(conflict)
            elif strategy == ResolutionStrategy.MERGE:
                result = self._resolve_merge(conflict)
        elif conflict.conflict_type == ConflictType.CONFLICTING_EDGE:
            if strategy == ResolutionStrategy.KEEP_HIGHEST_WEIGHT:
                result = self._resolve_keep_highest_weight(conflict)
        
        if result:
            self.resolution_history.append(result)
        
        return result
    
    def _resolve_keep_newest(self, conflict):
        """保留最新项"""
        if not conflict.items:
            return None
        
        sorted_items = sorted(conflict.items, key=lambda x: x.created_at, reverse=True)
        keep_item = sorted_items[0]
        removed_items = [x for x in sorted_items if x != keep_item]
        
        result = ResolutionResult(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.KEEP_NEWEST,
            items_removed=[self._get_item_id(x) for x in removed_items],
            items_kept=[self._get_item_id(keep_item)]
        )
        
        self._remove_items(removed_items)
        return result
    
    def _resolve_keep_oldest(self, conflict):
        """保留最早项"""
        if not conflict.items:
            return None
        
        sorted_items = sorted(conflict.items, key=lambda x: x.created_at)
        keep_item = sorted_items[0]
        removed_items = [x for x in sorted_items if x != keep_item]
        
        result = ResolutionResult(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.KEEP_OLDEST,
            items_removed=[self._get_item_id(x) for x in removed_items],
            items_kept=[self._get_item_id(keep_item)]
        )
        
        self._remove_items(removed_items)
        return result
    
    def _resolve_keep_highest_weight(self, conflict):
        """保留最高权重项"""
        if not conflict.items:
            return None
        
        sorted_items = sorted(conflict.items, key=lambda x: getattr(x, 'weight', 0.5), reverse=True)
        keep_item = sorted_items[0]
        removed_items = [x for x in sorted_items if x != keep_item]
        
        result = ResolutionResult(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.KEEP_HIGHEST_WEIGHT,
            items_removed=[self._get_item_id(x) for x in removed_items],
            items_kept=[self._get_item_id(keep_item)]
        )
        
        self._remove_items(removed_items)
        return result
    
    def _resolve_merge(self, conflict):
        """合并项"""
        if not conflict.items:
            return None
        
        if conflict.conflict_type == ConflictType.DUPLICATE_NODE and len(conflict.items) > 1:
            keep_item = conflict.items[0]
            for item in conflict.items[1:]:
                if hasattr(item, 'attr'):
                    for key, value in item.attr.items():
                        if key not in keep_item.attr:
                            keep_item.attr[key] = value
        
        removed_items = conflict.items[1:]
        
        result = ResolutionResult(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.MERGE,
            items_removed=[self._get_item_id(x) for x in removed_items],
            items_kept=[self._get_item_id(conflict.items[0])]
        )
        
        self._remove_items(removed_items)
        return result
    
    def _get_item_id(self, item):
        """获取项ID"""
        if hasattr(item, 'id'):
            return item.id
        elif hasattr(item, 'source') and hasattr(item, 'target') and hasattr(item, 'relation'):
            return item.source + "_" + item.relation + "_" + item.target
        else:
            return str(item)
    
    def _remove_items(self, items):
        """移除项"""
        for item in items:
            if hasattr(item, 'id') and item.id in self.kg.nodes:
                del self.kg.nodes[item.id]
            elif hasattr(item, 'source') and hasattr(item, 'target'):
                self.kg.edges = [e for e in self.kg.edges if e is not item]
        
        self.kg.save()
    
    def auto_resolve_all(self, strategy=None):
        """自动解决所有冲突"""
        if strategy is None:
            strategy = ResolutionStrategy.KEEP_NEWEST
        
        if not self.conflicts:
            self.detect_all_conflicts()
        
        results = []
        for conflict in self.conflicts:
            result = self.resolve_conflict(conflict, strategy)
            if result:
                results.append(result)
        
        return results
    
    def get_conflict_stats(self):
        """获取冲突统计信息"""
        stats = {
            "total_conflicts": len(self.conflicts),
            "by_type": {},
            "total_resolved": len(self.resolution_history)
        }
        
        for conflict in self.conflicts:
            type_name = conflict.conflict_type.value
            if type_name not in stats["by_type"]:
                stats["by_type"][type_name] = 0
            stats["by_type"][type_name] += 1
        
        return stats
