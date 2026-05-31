"""
知识推理引擎 - 阶段26
支持规则定义、匹配和推理功能
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
import os
from pathlib import Path


class RuleType(Enum):
    """规则类型枚举"""
    IMPLICATION = "implication"           # 蕴含规则: A -> B
    EQUIVALENCE = "equivalence"           # 等价规则: A <-> B
    TRANSITIVE = "transitive"              # 传递规则: A -> B, B -> C => A -> C
    REFLEXIVE = "reflexive"               # 自反规则: A -> A
    SYMMETRIC = "symmetric"              # 对称规则: A -> B => B -> A


class RuleCondition:
    """规则条件"""
    def __init__(self, node_type: Optional[str] = None,
                 relation: Optional[str] = None,
                 node_name_pattern: Optional[str] = None,
                 attribute_conditions: Optional[Dict[str, Any]] = None):
        self.node_type = node_type
        self.relation = relation
        self.node_name_pattern = node_name_pattern
        self.attribute_conditions = attribute_conditions or {}
    
    def matches(self, node: Any, edge: Any = None) -> bool:
        """检查条件是否匹配"""
        if self.node_type and node.attr.get('node_type') != self.node_type:
            return False
        
        if self.node_name_pattern:
            import re
            if not re.search(self.node_name_pattern, node.name):
                return False
        
        for key, value in self.attribute_conditions.items():
            if node.attr.get(key) != value:
                return False
        
        if self.relation and edge:
            if edge.relation != self.relation:
                return False
        
        return True


@dataclass
class InferenceRule:
    """推理规则定义"""
    rule_id: str
    rule_type: RuleType
    name: str
    description: str
    
    conditions: List[RuleCondition]
    
    conclusions: List[Dict[str, Any]]
    
    priority: int = 0
    
    enabled: bool = True
    
    confidence: float = 1.0
    
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type.value,
            "name": self.name,
            "description": self.description,
            "conditions": [
                {
                    "node_type": c.node_type,
                    "relation": c.relation,
                    "node_name_pattern": c.node_name_pattern,
                    "attribute_conditions": c.attribute_conditions
                }
                for c in self.conditions
            ],
            "conclusions": self.conclusions,
            "priority": self.priority,
            "enabled": self.enabled,
            "confidence": self.confidence,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InferenceRule':
        """从字典反序列化"""
        conditions = []
        for cond_data in data.get("conditions", []):
            conditions.append(RuleCondition(
                node_type=cond_data.get("node_type"),
                relation=cond_data.get("relation"),
                node_name_pattern=cond_data.get("node_name_pattern"),
                attribute_conditions=cond_data.get("attribute_conditions", {})
            ))
        
        return cls(
            rule_id=data["rule_id"],
            rule_type=RuleType(data["rule_type"]),
            name=data["name"],
            description=data.get("description", ""),
            conditions=conditions,
            conclusions=data.get("conclusions", []),
            priority=data.get("priority", 0),
            enabled=data.get("enabled", True),
            confidence=data.get("confidence", 1.0),
            metadata=data.get("metadata", {})
        )


@dataclass
class InferenceResult:
    """推理结果"""
    rule_id: str
    inferred_nodes: List[Dict[str, Any]]
    inferred_edges: List[Dict[str, Any]]
    confidence: float
    explanation: str
    timestamp: str


class RuleEngine:
    """规则引擎"""
    
    def __init__(self, knowledge_graph: Any):
        self.knowledge_graph = knowledge_graph
        self.rules: Dict[str, InferenceRule] = {}
        self.inference_history: List[InferenceResult] = []
        self.rule_stats: Dict[str, int] = {}
        
        self._load_builtin_rules()
    
    def _load_builtin_rules(self):
        """加载内置规则"""
        builtin_rules = [
            InferenceRule(
                rule_id="builtin_transitive_1",
                rule_type=RuleType.TRANSITIVE,
                name="传递性推理规则",
                description="如果A指向B，且B指向C，则A可能指向C",
                conditions=[
                    RuleCondition(),
                    RuleCondition()
                ],
                conclusions=[
                    {"type": "edge", "source_var": 0, "target_var": 1, "relation_var": 2}
                ],
                priority=10,
                confidence=0.7
            ),
            InferenceRule(
                rule_id="builtin_symmetric_1",
                rule_type=RuleType.SYMMETRIC,
                name="对称性推理规则",
                description="如果A与B有关系R，则B与A可能有关系R",
                conditions=[
                    RuleCondition()
                ],
                conclusions=[
                    {"type": "edge", "source_var": 0, "target_var": 1, "relation_var": 2}
                ],
                priority=5,
                confidence=0.6
            )
        ]
        
        for rule in builtin_rules:
            self.rules[rule.rule_id] = rule
    
    def add_rule(self, rule: InferenceRule) -> bool:
        """添加推理规则"""
        if not rule.rule_id:
            return False
        
        self.rules[rule.rule_id] = rule
        self.rule_stats[rule.rule_id] = 0
        return True
    
    def remove_rule(self, rule_id: str) -> bool:
        """删除推理规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            if rule_id in self.rule_stats:
                del self.rule_stats[rule_id]
            return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[InferenceRule]:
        """获取规则"""
        return self.rules.get(rule_id)
    
    def get_all_rules(self) -> List[InferenceRule]:
        """获取所有规则"""
        return list(self.rules.values())
    
    def enable_rule(self, rule_id: str) -> bool:
        """启用规则"""
        rule = self.rules.get(rule_id)
        if rule:
            rule.enabled = True
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """禁用规则"""
        rule = self.rules.get(rule_id)
        if rule:
            rule.enabled = False
            return True
        return False
    
    def infer(self, focus_node: Optional[str] = None, max_depth: int = 3) -> List[InferenceResult]:
        """执行推理"""
        results = []
        visited = set()
        
        nodes_to_check = []
        if focus_node:
            for node_id, node in self.knowledge_graph.nodes.items():
                if node.name == focus_node or node_id == focus_node:
                    nodes_to_check.append(node)
        else:
            nodes_to_check = list(self.knowledge_graph.nodes.values())
        
        for node in nodes_to_check:
            self._infer_from_node(node, results, visited, depth=0, max_depth=max_depth)
        
        return results
    
    def _infer_from_node(self, node: Any, results: List[InferenceResult],
                         visited: set, depth: int, max_depth: int):
        """从节点开始推理"""
        if depth >= max_depth:
            return
        
        if node.id in visited:
            return
        
        visited.add(node.id)
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            rule_results = self._apply_rule(rule, node, depth)
            for rule_result in rule_results:
                results.append(rule_result)
                self.rule_stats[rule.rule_id] = self.rule_stats.get(rule.rule_id, 0) + 1
    
    def _apply_rule(self, rule: InferenceRule, start_node: Any, depth: int) -> List[InferenceResult]:
        """应用规则到节点"""
        results = []
        
        if rule.rule_type == RuleType.TRANSITIVE:
            results.extend(self._apply_transitive_rule(rule, start_node, depth))
        elif rule.rule_type == RuleType.SYMMETRIC:
            results.extend(self._apply_symmetric_rule(rule, start_node, depth))
        elif rule.rule_type == RuleType.IMPLICATION:
            results.extend(self._apply_implication_rule(rule, start_node, depth))
        elif rule.rule_type == RuleType.EQUIVALENCE:
            results.extend(self._apply_equivalence_rule(rule, start_node, depth))
        
        return results
    
    def _apply_transitive_rule(self, rule: InferenceRule, node: Any, depth: int) -> List[InferenceResult]:
        """应用传递性规则"""
        results = []
        
        outgoing_edges = [e for e in self.knowledge_graph.edges if e.source == node.name]
        
        for edge1 in outgoing_edges:
            intermediate_node_name = edge1.target
            
            intermediate_edges = [e for e in self.knowledge_graph.edges
                                 if e.source == intermediate_node_name]
            
            for edge2 in intermediate_edges:
                inferred_edge = {
                    "type": "edge",
                    "source": node.name,
                    "target": edge2.target,
                    "relation": f"inferred_from_{rule.rule_id}",
                    "weight": edge1.weight * edge2.weight * rule.confidence,
                    "metadata": {
                        "inferred": True,
                        "rule_id": rule.rule_id,
                        "path": [node.name, intermediate_node_name, edge2.target]
                    }
                }
                
                exists = any(
                    e.source == inferred_edge["source"] and
                    e.target == inferred_edge["target"] and
                    e.relation == inferred_edge["relation"]
                    for e in self.knowledge_graph.edges
                )
                
                if not exists:
                    from datetime import datetime
                    result = InferenceResult(
                        rule_id=rule.rule_id,
                        inferred_nodes=[],
                        inferred_edges=[inferred_edge],
                        confidence=rule.confidence * edge1.weight * edge2.weight,
                        explanation=f"通过传递性规则从 {node.name} -> {intermediate_node_name} -> {edge2.target} 推理",
                        timestamp=datetime.now().isoformat()
                    )
                    results.append(result)
        
        return results
    
    def _apply_symmetric_rule(self, rule: InferenceRule, node: Any, depth: int) -> List[InferenceResult]:
        """应用对称性规则"""
        results = []
        
        edges = [e for e in self.knowledge_graph.edges if e.source == node.name]
        
        for edge in edges:
            inferred_edge = {
                "type": "edge",
                "source": edge.target,
                "target": node.name,
                "relation": edge.relation,
                "weight": edge.weight * rule.confidence,
                "metadata": {
                    "inferred": True,
                    "rule_id": rule.rule_id,
                    "symmetric_of": f"{edge.source}-{edge.relation}-{edge.target}"
                }
            }
            
            exists = any(
                e.source == inferred_edge["source"] and
                e.target == inferred_edge["target"] and
                e.relation == inferred_edge["relation"]
                for e in self.knowledge_graph.edges
            )
            
            if not exists:
                from datetime import datetime
                result = InferenceResult(
                    rule_id=rule.rule_id,
                    inferred_nodes=[],
                    inferred_edges=[inferred_edge],
                    confidence=rule.confidence * edge.weight,
                    explanation=f"通过对称性规则，从 {edge.source} --{edge.relation}--> {edge.target} 推理得到反向关系",
                    timestamp=datetime.now().isoformat()
                )
                results.append(result)
        
        return results
    
    def _apply_implication_rule(self, rule: InferenceRule, node: Any, depth: int) -> List[InferenceResult]:
        """应用蕴含规则"""
        results = []
        
        if len(rule.conditions) == 0 or len(rule.conclusions) == 0:
            return results
        
        condition = rule.conditions[0]
        
        if condition.matches(node):
            inferred_nodes = []
            inferred_edges = []
            
            for conclusion in rule.conclusions:
                if conclusion.get("type") == "node":
                    inferred_nodes.append({
                        "name": conclusion.get("name", f"inferred_{rule.rule_id}"),
                        "attr": conclusion.get("attr", {}),
                        "metadata": {
                            "inferred": True,
                            "rule_id": rule.rule_id
                        }
                    })
                elif conclusion.get("type") == "edge":
                    inferred_edges.append({
                        "type": "edge",
                        "source": conclusion.get("source", node.name),
                        "target": conclusion.get("target"),
                        "relation": conclusion.get("relation"),
                        "weight": conclusion.get("weight", rule.confidence),
                        "metadata": {
                            "inferred": True,
                            "rule_id": rule.rule_id
                        }
                    })
            
            if inferred_nodes or inferred_edges:
                from datetime import datetime
                result = InferenceResult(
                    rule_id=rule.rule_id,
                    inferred_nodes=inferred_nodes,
                    inferred_edges=inferred_edges,
                    confidence=rule.confidence,
                    explanation=f"通过蕴含规则 '{rule.name}' 从节点 '{node.name}' 推理",
                    timestamp=datetime.now().isoformat()
                )
                results.append(result)
        
        return results
    
    def _apply_equivalence_rule(self, rule: InferenceRule, node: Any, depth: int) -> List[InferenceResult]:
        """应用等价规则"""
        results = []
        
        return results
    
    def apply_inference_results(self, results: List[InferenceResult]) -> int:
        """应用推理结果到知识图谱"""
        added_count = 0
        
        for result in results:
            for node_data in result.inferred_nodes:
                try:
                    self.knowledge_graph.add_node(
                        node_data["name"],
                        {**node_data.get("attr", {}), **node_data.get("metadata", {})}
                    )
                    added_count += 1
                except Exception:
                    pass
            
            for edge_data in result.inferred_edges:
                try:
                    self.knowledge_graph.add_edge(
                        edge_data["source"],
                        edge_data["target"],
                        edge_data["relation"],
                        edge_data.get("weight", 0.5)
                    )
                    added_count += 1
                except Exception:
                    pass
        
        return added_count
    
    def get_inference_stats(self) -> Dict[str, Any]:
        """获取推理统计信息"""
        return {
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules.values() if r.enabled),
            "rule_usage": self.rule_stats.copy(),
            "total_inferences": len(self.inference_history),
            "builtin_rules": len([r for r in self.rules.keys() if r.startswith("builtin_")]),
            "custom_rules": len([r for r in self.rules.keys() if not r.startswith("builtin_")])
        }
    
    def save_rules(self, filepath: str) -> bool:
        """保存规则到文件"""
        try:
            data = {
                "rules": [rule.to_dict() for rule in self.rules.values()],
                "stats": self.rule_stats
            }
            
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception:
            return False
    
    def load_rules(self, filepath: str) -> bool:
        """从文件加载规则"""
        try:
            if not os.path.exists(filepath):
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.rules.clear()
            self.rule_stats.clear()
            
            for rule_data in data.get("rules", []):
                rule = InferenceRule.from_dict(rule_data)
                self.rules[rule.rule_id] = rule
                self.rule_stats[rule.rule_id] = data.get("stats", {}).get(rule.rule_id, 0)
            
            self._load_builtin_rules()
            
            return True
        except Exception:
            return False
