
"""
知识版本管理与回滚 - 阶段30
支持版本历史追踪、快照管理和回滚功能
"""
import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class VersionAction(Enum):
    """版本操作类型"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RESTORE = "restore"


@dataclass
class KnowledgeVersion:
    """知识版本记录"""
    version_id: str
    version_number: int
    timestamp: str
    action: VersionAction
    knowledge_type: str  # "node" or "edge"
    knowledge_id: str
    knowledge_name: str
    previous_state: Optional[Dict[str, Any]]
    new_state: Optional[Dict[str, Any]]
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeSnapshot:
    """知识快照"""
    snapshot_id: str
    snapshot_name: str
    timestamp: str
    description: str
    node_count: int
    edge_count: int
    snapshot_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeVersionManager:
    """知识版本管理器"""
    
    def __init__(self, knowledge_graph: Any):
        self.kg = knowledge_graph
        self.versions: List[KnowledgeVersion] = []
        self.snapshots: List[KnowledgeSnapshot] = []
        self.current_version_number = 0
        
        self.version_dir = Path("data/versions")
        self.snapshot_dir = Path("data/snapshots/versions")
        self.version_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        self._load_versions()
        self._load_snapshots()
    
    def _load_versions(self):
        """加载版本历史"""
        version_file = self.version_dir / "version_history.json"
        
        if version_file.exists():
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.versions = []
                for v_data in data.get("versions", []):
                    version = KnowledgeVersion(
                        version_id=v_data["version_id"],
                        version_number=v_data["version_number"],
                        timestamp=v_data["timestamp"],
                        action=VersionAction(v_data["action"]),
                        knowledge_type=v_data["knowledge_type"],
                        knowledge_id=v_data["knowledge_id"],
                        knowledge_name=v_data["knowledge_name"],
                        previous_state=v_data.get("previous_state"),
                        new_state=v_data.get("new_state"),
                        description=v_data.get("description", ""),
                        metadata=v_data.get("metadata", {})
                    )
                    self.versions.append(version)
                
                if self.versions:
                    self.current_version_number = max(v.version_number for v in self.versions)
            except Exception as e:
                print(f"加载版本历史失败: {e}")
    
    def _load_snapshots(self):
        """加载快照列表"""
        if self.snapshot_dir.exists():
            for snapshot_file in sorted(self.snapshot_dir.glob("*.json"), reverse=True):
                try:
                    with open(snapshot_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    snapshot = KnowledgeSnapshot(
                        snapshot_id=data["snapshot_id"],
                        snapshot_name=data["snapshot_name"],
                        timestamp=data["timestamp"],
                        description=data.get("description", ""),
                        node_count=data["node_count"],
                        edge_count=data["edge_count"],
                        snapshot_path=str(snapshot_file),
                        metadata=data.get("metadata", {})
                    )
                    self.snapshots.append(snapshot)
                except Exception:
                    pass
    
    def _save_versions(self):
        """保存版本历史"""
        version_file = self.version_dir / "version_history.json"
        
        data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "current_version_number": self.current_version_number,
            "versions": [
                {
                    "version_id": v.version_id,
                    "version_number": v.version_number,
                    "timestamp": v.timestamp,
                    "action": v.action.value,
                    "knowledge_type": v.knowledge_type,
                    "knowledge_id": v.knowledge_id,
                    "knowledge_name": v.knowledge_name,
                    "previous_state": v.previous_state,
                    "new_state": v.new_state,
                    "description": v.description,
                    "metadata": v.metadata
                }
                for v in self.versions
            ]
        }
        
        try:
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存版本历史失败: {e}")
            return False
    
    def record_node_creation(self, node: Any, description: str = ""):
        """记录节点创建"""
        self.current_version_number += 1
        
        version = KnowledgeVersion(
            version_id=f"v{self.current_version_number}",
            version_number=self.current_version_number,
            timestamp=datetime.now().isoformat(),
            action=VersionAction.CREATE,
            knowledge_type="node",
            knowledge_id=node.id,
            knowledge_name=node.name,
            previous_state=None,
            new_state=self._serialize_node(node),
            description=description,
            metadata={"source": "auto_record"}
        )
        
        self.versions.append(version)
        self._save_versions()
        return version
    
    def record_node_update(self, node: Any, previous_state: Dict[str, Any], description: str = ""):
        """记录节点更新"""
        self.current_version_number += 1
        
        version = KnowledgeVersion(
            version_id=f"v{self.current_version_number}",
            version_number=self.current_version_number,
            timestamp=datetime.now().isoformat(),
            action=VersionAction.UPDATE,
            knowledge_type="node",
            knowledge_id=node.id,
            knowledge_name=node.name,
            previous_state=previous_state,
            new_state=self._serialize_node(node),
            description=description,
            metadata={"source": "auto_record"}
        )
        
        self.versions.append(version)
        self._save_versions()
        return version
    
    def record_node_deletion(self, node: Any, description: str = ""):
        """记录节点删除"""
        self.current_version_number += 1
        
        version = KnowledgeVersion(
            version_id=f"v{self.current_version_number}",
            version_number=self.current_version_number,
            timestamp=datetime.now().isoformat(),
            action=VersionAction.DELETE,
            knowledge_type="node",
            knowledge_id=node.id,
            knowledge_name=node.name,
            previous_state=self._serialize_node(node),
            new_state=None,
            description=description,
            metadata={"source": "auto_record"}
        )
        
        self.versions.append(version)
        self._save_versions()
        return version
    
    def record_edge_creation(self, edge: Any, description: str = ""):
        """记录边创建"""
        self.current_version_number += 1
        
        version = KnowledgeVersion(
            version_id=f"v{self.current_version_number}",
            version_number=self.current_version_number,
            timestamp=datetime.now().isoformat(),
            action=VersionAction.CREATE,
            knowledge_type="edge",
            knowledge_id=f"{edge.source}_{edge.relation}_{edge.target}",
            knowledge_name=f"{edge.source} --[{edge.relation}]--> {edge.target}",
            previous_state=None,
            new_state=self._serialize_edge(edge),
            description=description,
            metadata={"source": "auto_record"}
        )
        
        self.versions.append(version)
        self._save_versions()
        return version
    
    def record_edge_deletion(self, edge: Any, description: str = ""):
        """记录边删除"""
        self.current_version_number += 1
        
        version = KnowledgeVersion(
            version_id=f"v{self.current_version_number}",
            version_number=self.current_version_number,
            timestamp=datetime.now().isoformat(),
            action=VersionAction.DELETE,
            knowledge_type="edge",
            knowledge_id=f"{edge.source}_{edge.relation}_{edge.target}",
            knowledge_name=f"{edge.source} --[{edge.relation}]--> {edge.target}",
            previous_state=self._serialize_edge(edge),
            new_state=None,
            description=description,
            metadata={"source": "auto_record"}
        )
        
        self.versions.append(version)
        self._save_versions()
        return version
    
    def _serialize_node(self, node: Any) -> Dict[str, Any]:
        """序列化节点"""
        return {
            "id": node.id,
            "name": node.name,
            "attr": node.attr,
            "created_at": node.created_at
        }
    
    def _deserialize_node(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """反序列化节点"""
        return data
    
    def _serialize_edge(self, edge: Any) -> Dict[str, Any]:
        """序列化边"""
        return {
            "source": edge.source,
            "target": edge.target,
            "relation": edge.relation,
            "weight": edge.weight,
            "created_at": edge.created_at
        }
    
    def _deserialize_edge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """反序列化边"""
        return data
    
    def create_snapshot(self, name: str, description: str = "") -> Optional[KnowledgeSnapshot]:
        """创建快照"""
        snapshot_id = f"snapshot_v{self.current_version_number}_{int(datetime.now().timestamp())}"
        snapshot_name = name or f"Auto-snapshot at v{self.current_version_number}"
        
        snapshot_data = {
            "snapshot_id": snapshot_id,
            "snapshot_name": snapshot_name,
            "timestamp": datetime.now().isoformat(),
            "version_number": self.current_version_number,
            "description": description,
            "node_count": len(self.kg.nodes),
            "edge_count": len(self.kg.edges),
            "metadata": {},
            "nodes": [
                self._serialize_node(node) for node in self.kg.nodes.values()
            ],
            "edges": [
                self._serialize_edge(edge) for edge in self.kg.edges
            ]
        }
        
        snapshot_file = self.snapshot_dir / f"{snapshot_id}.json"
        
        try:
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, ensure_ascii=False, indent=2)
            
            snapshot = KnowledgeSnapshot(
                snapshot_id=snapshot_id,
                snapshot_name=snapshot_name,
                timestamp=datetime.now().isoformat(),
                description=description,
                node_count=len(self.kg.nodes),
                edge_count=len(self.kg.edges),
                snapshot_path=str(snapshot_file)
            )
            
            self.snapshots.insert(0, snapshot)
            
            print(f"[快照] 创建快照: {snapshot_name} (v{self.current_version_number})")
            return snapshot
        except Exception as e:
            print(f"创建快照失败: {e}")
            return None
    
    def restore_snapshot(self, snapshot_id: str) -> bool:
        """恢复快照"""
        snapshot_file = self.snapshot_dir / f"{snapshot_id}.json"
        
        if not snapshot_file.exists():
            print(f"快照文件不存在: {snapshot_id}")
            return False
        
        try:
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.kg.nodes.clear()
            self.kg.edges.clear()
            
            for node_data in data.get("nodes", []):
                from core.knowledge_graph import Node
                node = Node(node_data["name"], node_data.get("attr", {}))
                node.id = node_data["id"]
                node.created_at = node_data.get("created_at", datetime.now().isoformat())
                self.kg.nodes[node.id] = node
            
            for edge_data in data.get("edges", []):
                from core.knowledge_graph import Edge
                edge = Edge(
                    edge_data["source"],
                    edge_data["target"],
                    edge_data["relation"],
                    edge_data.get("weight", 0.5)
                )
                edge.created_at = edge_data.get("created_at", datetime.now().isoformat())
                self.kg.edges.append(edge)
            
            self.kg.save()
            
            self.current_version_number += 1
            version = KnowledgeVersion(
                version_id=f"v{self.current_version_number}",
                version_number=self.current_version_number,
                timestamp=datetime.now().isoformat(),
                action=VersionAction.RESTORE,
                knowledge_type="snapshot",
                knowledge_id=snapshot_id,
                knowledge_name=data.get("snapshot_name", snapshot_id),
                previous_state=None,
                new_state={"nodes": len(self.kg.nodes), "edges": len(self.kg.edges)},
                description=f"Restored from snapshot: {data.get('snapshot_name', snapshot_id)}",
                metadata={"snapshot_version": data.get("version_number")}
            )
            self.versions.append(version)
            self._save_versions()
            
            print(f"[快照恢复] 成功恢复到: {data.get('snapshot_name', snapshot_id)}")
            return True
        except Exception as e:
            print(f"恢复快照失败: {e}")
            return False
    
    def get_version_history(self, knowledge_id: Optional[str] = None, 
                          knowledge_type: Optional[str] = None) -> List[KnowledgeVersion]:
        """获取版本历史"""
        filtered_versions = self.versions
        
        if knowledge_id:
            filtered_versions = [v for v in filtered_versions if v.knowledge_id == knowledge_id]
        
        if knowledge_type:
            filtered_versions = [v for v in filtered_versions if v.knowledge_type == knowledge_type]
        
        return filtered_versions
    
    def get_version_by_number(self, version_number: int) -> Optional[KnowledgeVersion]:
        """根据版本号获取版本"""
        for version in self.versions:
            if version.version_number == version_number:
                return version
        return None
    
    def get_snapshots(self) -> List[KnowledgeSnapshot]:
        """获取所有快照"""
        return self.snapshots
    
    def get_version_stats(self) -> Dict[str, Any]:
        """获取版本统计"""
        create_count = sum(1 for v in self.versions if v.action == VersionAction.CREATE)
        update_count = sum(1 for v in self.versions if v.action == VersionAction.UPDATE)
        delete_count = sum(1 for v in self.versions if v.action == VersionAction.DELETE)
        restore_count = sum(1 for v in self.versions if v.action == VersionAction.RESTORE)
        
        return {
            "total_versions": len(self.versions),
            "current_version_number": self.current_version_number,
            "create_count": create_count,
            "update_count": update_count,
            "delete_count": delete_count,
            "restore_count": restore_count,
            "snapshot_count": len(self.snapshots),
            "oldest_version": self.versions[0].timestamp if self.versions else None,
            "newest_version": self.versions[-1].timestamp if self.versions else None
        }
    
    def compare_versions(self, version1_number: int, version2_number: int) -> Dict[str, Any]:
        """比较两个版本"""
        version1 = self.get_version_by_number(version1_number)
        version2 = self.get_version_by_number(version2_number)
        
        if not version1 or not version2:
            return {"error": "Version not found"}
        
        diff = {
            "version1": version1_number,
            "version2": version2_number,
            "changes": []
        }
        
        if version1.new_state and version2.new_state:
            if version1.new_state != version2.new_state:
                diff["changes"].append({
                    "type": "modified",
                    "knowledge_id": version1.knowledge_id,
                    "before": version1.new_state,
                    "after": version2.new_state
                })
        
        return diff
