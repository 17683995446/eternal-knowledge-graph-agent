"""
时间序列知识处理 - 阶段27
支持时间戳、时间范围查询、知识演变追踪
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
from pathlib import Path


class TimeEventType(Enum):
    """时间事件类型"""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    VERIFIED = "verified"
    INFERRED = "inferred"
    IMPORTED = "imported"


@dataclass
class TimeEvent:
    """时间事件记录"""
    event_type: TimeEventType
    timestamp: str
    description: str
    actor: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemporalNode:
    """带时间属性的节点"""
    node_id: str
    name: str
    created_at: str
    modified_at: str
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    history: List[TimeEvent] = field(default_factory=list)
    attr: Dict[str, Any] = field(default_factory=dict)
    
    def add_event(self, event: TimeEvent):
        """添加时间事件"""
        self.history.append(event)
        self.modified_at = event.timestamp


@dataclass
class TemporalEdge:
    """带时间属性的边"""
    edge_id: str
    source: str
    target: str
    relation: str
    weight: float
    created_at: str
    modified_at: str
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    history: List[TimeEvent] = field(default_factory=list)
    
    def add_event(self, event: TimeEvent):
        """添加时间事件"""
        self.history.append(event)
        self.modified_at = event.timestamp


@dataclass
class KnowledgeSnapshot:
    """知识图谱快照"""
    snapshot_id: str
    timestamp: str
    description: str
    node_count: int
    edge_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class TemporalKnowledgeGraph:
    """时间序列知识图谱管理器"""
    
    def __init__(self, knowledge_graph: Any):
        self.kg = knowledge_graph
        self.temporal_nodes: Dict[str, TemporalNode] = {}
        self.temporal_edges: Dict[str, TemporalEdge] = {}
        self.snapshots: List[KnowledgeSnapshot] = []
        self.snapshot_dir = Path("data/snapshots")
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        self._initialize_from_kg()
    
    def _initialize_from_kg(self):
        """从现有知识图谱初始化"""
        for node in self.kg.nodes.values():
            temporal_node = TemporalNode(
                node_id=node.id,
                name=node.name,
                created_at=node.created_at,
                modified_at=node.created_at,
                attr=node.attr
            )
            # 添加创建事件
            temporal_node.add_event(TimeEvent(
                event_type=TimeEventType.CREATED,
                timestamp=node.created_at,
                description="节点初始创建"
            ))
            self.temporal_nodes[node.id] = temporal_node
        
        for edge in self.kg.edges:
            edge_id = f"{edge.source}_{edge.relation}_{edge.target}"
            temporal_edge = TemporalEdge(
                edge_id=edge_id,
                source=edge.source,
                target=edge.target,
                relation=edge.relation,
                weight=edge.weight,
                created_at=edge.created_at,
                modified_at=edge.created_at
            )
            temporal_edge.add_event(TimeEvent(
                event_type=TimeEventType.CREATED,
                timestamp=edge.created_at,
                description="边初始创建"
            ))
            self.temporal_edges[edge_id] = temporal_edge
    
    def add_temporal_node(self, name: str, attr: Dict[str, Any] = None,
                         valid_from: Optional[str] = None,
                         valid_until: Optional[str] = None) -> TemporalNode:
        """添加时间节点"""
        node = self.kg.add_node(name, attr)
        
        temporal_node = TemporalNode(
            node_id=node.id,
            name=node.name,
            created_at=node.created_at,
            modified_at=node.created_at,
            valid_from=valid_from,
            valid_until=valid_until,
            attr=attr or {}
        )
        
        temporal_node.add_event(TimeEvent(
            event_type=TimeEventType.CREATED,
            timestamp=datetime.now().isoformat(),
            description="添加节点"
        ))
        
        self.temporal_nodes[node.id] = temporal_node
        return temporal_node
    
    def add_temporal_edge(self, source: str, target: str, relation: str,
                         weight: float = 0.5,
                         valid_from: Optional[str] = None,
                         valid_until: Optional[str] = None) -> TemporalEdge:
        """添加时间边"""
        edge = self.kg.add_edge(source, target, relation, weight)
        
        edge_id = f"{edge.source}_{edge.relation}_{edge.target}"
        temporal_edge = TemporalEdge(
            edge_id=edge_id,
            source=edge.source,
            target=edge.target,
            relation=edge.relation,
            weight=edge.weight,
            created_at=edge.created_at,
            modified_at=edge.created_at,
            valid_from=valid_from,
            valid_until=valid_until
        )
        
        temporal_edge.add_event(TimeEvent(
            event_type=TimeEventType.CREATED,
            timestamp=datetime.now().isoformat(),
            description="添加边"
        ))
        
        self.temporal_edges[edge_id] = temporal_edge
        return temporal_edge
    
    def update_node_attributes(self, node_id: str, new_attr: Dict[str, Any],
                             actor: Optional[str] = None) -> bool:
        """更新节点属性"""
        if node_id not in self.temporal_nodes:
            return False
        
        temporal_node = self.temporal_nodes[node_id]
        temporal_node.attr.update(new_attr)
        
        # 记录修改事件
        event = TimeEvent(
            event_type=TimeEventType.MODIFIED,
            timestamp=datetime.now().isoformat(),
            description="更新节点属性",
            actor=actor,
            metadata={"updated_attrs": list(new_attr.keys())}
        )
        temporal_node.add_event(event)
        
        # 更新原始知识图谱
        for node in self.kg.nodes.values():
            if node.id == node_id:
                node.attr.update(new_attr)
                break
        
        return True
    
    def update_edge_weight(self, edge_id: str, new_weight: float,
                         actor: Optional[str] = None) -> bool:
        """更新边权重"""
        if edge_id not in self.temporal_edges:
            return False
        
        temporal_edge = self.temporal_edges[edge_id]
        old_weight = temporal_edge.weight
        temporal_edge.weight = new_weight
        
        # 记录修改事件
        event = TimeEvent(
            event_type=TimeEventType.MODIFIED,
            timestamp=datetime.now().isoformat(),
            description="更新边权重",
            actor=actor,
            metadata={"old_weight": old_weight, "new_weight": new_weight}
        )
        temporal_edge.add_event(event)
        
        # 更新原始知识图谱
        for edge in self.kg.edges:
            if f"{edge.source}_{edge.relation}_{edge.target}" == edge_id:
                edge.weight = new_weight
                break
        
        return True
    
    def query_by_time_range(self, start_time: str, end_time: str,
                          include_invalid: bool = False) -> Tuple[List[TemporalNode], List[TemporalEdge]]:
        """按时间范围查询节点和边"""
        filtered_nodes = []
        filtered_edges = []
        
        for node in self.temporal_nodes.values():
            if self._is_in_time_range(node, start_time, end_time, include_invalid):
                filtered_nodes.append(node)
        
        for edge in self.temporal_edges.values():
            if self._is_in_time_range(edge, start_time, end_time, include_invalid):
                filtered_edges.append(edge)
        
        return filtered_nodes, filtered_edges
    
    def _is_in_time_range(self, item: Any, start_time: str, end_time: str,
                        include_invalid: bool) -> bool:
        """检查项是否在时间范围内"""
        if include_invalid:
            return True
        
        item_created = item.created_at
        
        if item.valid_from and item.valid_until:
            return (item.valid_from <= end_time and 
                   (item.valid_until >= start_time or item.valid_until is None))
        elif item.valid_from:
            return item.valid_from <= end_time
        elif item.valid_until:
            return item.valid_until >= start_time
        else:
            return start_time <= item_created <= end_time
    
    def get_node_history(self, node_id: str) -> Optional[List[TimeEvent]]:
        """获取节点历史记录"""
        if node_id in self.temporal_nodes:
            return self.temporal_nodes[node_id].history
        return None
    
    def get_edge_history(self, edge_id: str) -> Optional[List[TimeEvent]]:
        """获取边历史记录"""
        if edge_id in self.temporal_edges:
            return self.temporal_edges[edge_id].history
        return None
    
    def take_snapshot(self, description: str = "", 
                     metadata: Dict[str, Any] = None) -> KnowledgeSnapshot:
        """创建知识图谱快照"""
        snapshot_id = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now().isoformat()
        
        snapshot = KnowledgeSnapshot(
            snapshot_id=snapshot_id,
            timestamp=timestamp,
            description=description,
            node_count=len(self.temporal_nodes),
            edge_count=len(self.temporal_edges),
            metadata=metadata or {}
        )
        
        # 保存快照数据
        snapshot_data = {
            "snapshot": {
                "snapshot_id": snapshot.snapshot_id,
                "timestamp": snapshot.timestamp,
                "description": snapshot.description,
                "node_count": snapshot.node_count,
                "edge_count": snapshot.edge_count,
                "metadata": snapshot.metadata
            },
            "nodes": [
                {
                    "node_id": n.node_id,
                    "name": n.name,
                    "created_at": n.created_at,
                    "modified_at": n.modified_at,
                    "valid_from": n.valid_from,
                    "valid_until": n.valid_until,
                    "attr": n.attr
                }
                for n in self.temporal_nodes.values()
            ],
            "edges": [
                {
                    "edge_id": e.edge_id,
                    "source": e.source,
                    "target": e.target,
                    "relation": e.relation,
                    "weight": e.weight,
                    "created_at": e.created_at,
                    "modified_at": e.modified_at,
                    "valid_from": e.valid_from,
                    "valid_until": e.valid_until
                }
                for e in self.temporal_edges.values()
            ]
        }
        
        snapshot_file = self.snapshot_dir / f"{snapshot_id}.json"
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot_data, f, ensure_ascii=False, indent=2)
        
        self.snapshots.append(snapshot)
        
        print(f"[快照] 创建快照 {snapshot_id}，包含 {snapshot.node_count} 个节点和 {snapshot.edge_count} 条边")
        return snapshot
    
    def list_snapshots(self) -> List[KnowledgeSnapshot]:
        """列出所有快照"""
        # 从文件系统加载快照信息
        if not self.snapshots:
            for snapshot_file in sorted(self.snapshot_dir.glob("snapshot_*.json"), reverse=True):
                try:
                    with open(snapshot_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        snapshot_info = data["snapshot"]
                        snapshot = KnowledgeSnapshot(
                            snapshot_id=snapshot_info["snapshot_id"],
                            timestamp=snapshot_info["timestamp"],
                            description=snapshot_info.get("description", ""),
                            node_count=snapshot_info["node_count"],
                            edge_count=snapshot_info["edge_count"],
                            metadata=snapshot_info.get("metadata", {})
                        )
                        self.snapshots.append(snapshot)
                except Exception:
                    pass
        
        return self.snapshots
    
    def get_temporal_stats(self) -> Dict[str, Any]:
        """获取时间序列统计信息"""
        now = datetime.now()
        one_day_ago = (now - timedelta(days=1)).isoformat()
        one_week_ago = (now - timedelta(weeks=1)).isoformat()
        one_month_ago = (now - timedelta(days=30)).isoformat()
        
        nodes_24h = sum(1 for n in self.temporal_nodes.values() 
                       if n.modified_at >= one_day_ago)
        nodes_7d = sum(1 for n in self.temporal_nodes.values() 
                      if n.modified_at >= one_week_ago)
        nodes_30d = sum(1 for n in self.temporal_nodes.values() 
                       if n.modified_at >= one_month_ago)
        
        edges_24h = sum(1 for e in self.temporal_edges.values() 
                       if e.modified_at >= one_day_ago)
        edges_7d = sum(1 for e in self.temporal_edges.values() 
                      if e.modified_at >= one_week_ago)
        edges_30d = sum(1 for e in self.temporal_edges.values() 
                       if e.modified_at >= one_month_ago)
        
        return {
            "total_nodes": len(self.temporal_nodes),
            "total_edges": len(self.temporal_edges),
            "recent_changes": {
                "24h": {"nodes": nodes_24h, "edges": edges_24h},
                "7d": {"nodes": nodes_7d, "edges": edges_7d},
                "30d": {"nodes": nodes_30d, "edges": edges_30d}
            },
            "snapshot_count": len(self.snapshots),
            "oldest_node": min((n.created_at for n in self.temporal_nodes.values()), 
                            default=None),
            "newest_node": max((n.created_at for n in self.temporal_nodes.values()), 
                            default=None)
        }
    
    def record_inference_event(self, node_id: str, description: str,
                            confidence: float,
                            actor: Optional[str] = None):
        """记录推理事件"""
        if node_id in self.temporal_nodes:
            event = TimeEvent(
                event_type=TimeEventType.INFERRED,
                timestamp=datetime.now().isoformat(),
                description=description,
                actor=actor,
                metadata={"confidence": confidence}
            )
            self.temporal_nodes[node_id].add_event(event)
    
    def set_validity_period(self, item_id: str, is_node: bool,
                          valid_from: Optional[str],
                          valid_until: Optional[str]) -> bool:
        """设置有效期"""
        if is_node:
            if item_id in self.temporal_nodes:
                self.temporal_nodes[item_id].valid_from = valid_from
                self.temporal_nodes[item_id].valid_until = valid_until
                return True
        else:
            if item_id in self.temporal_edges:
                self.temporal_edges[item_id].valid_from = valid_from
                self.temporal_edges[item_id].valid_until = valid_until
                return True
        return False
