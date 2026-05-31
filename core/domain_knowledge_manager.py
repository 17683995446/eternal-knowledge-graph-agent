
"""
专业领域知识适配系统 - 阶段31
支持专业领域知识的注册、模板管理、知识增强和扩展
"""
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
from pathlib import Path


class DomainType(Enum):
    """专业领域类型"""
    GENERAL = "general"
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    FINANCE = "finance"
    LEGAL = "legal"
    SCIENCE = "science"
    LANGUAGE = "language"
    CUSTOM = "custom"


@dataclass
class KnowledgeTemplate:
    """知识模板"""
    template_id: str
    template_name: str
    domain_type: DomainType
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DomainKnowledge:
    """领域知识"""
    knowledge_id: str
    domain_type: DomainType
    name: str
    content: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.8
    tags: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DomainAdaptor:
    """领域适配器"""
    adaptor_id: str
    domain_type: DomainType
    name: str
    description: str = ""
    enhancement_rules: List[Dict[str, Any]] = field(default_factory=list)
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class DomainKnowledgeManager:
    """专业领域知识管理器"""
    
    def __init__(self, knowledge_graph: Any):
        self.kg = knowledge_graph
        self.templates: Dict[str, KnowledgeTemplate] = {}
        self.domain_knowledges: Dict[str, DomainKnowledge] = {}
        self.adaptors: Dict[str, DomainAdaptor] = {}
        
        self.data_dir = Path("data/domains")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self._initialize_default_templates()
        self._load_stored_knowledge()
    
    def _initialize_default_templates(self):
        """初始化默认知识模板"""
        # 通用知识模板
        self.templates["general_concept"] = KnowledgeTemplate(
            template_id="general_concept",
            template_name="通用概念模板",
            domain_type=DomainType.GENERAL,
            required_fields=["name", "description"],
            optional_fields=["category", "examples", "related_concepts"],
            validation_rules={
                "name": {"type": str, "min_length": 1, "max_length": 200},
                "description": {"type": str, "min_length": 10}
            },
            description="用于存储通用概念知识的基础模板"
        )
        
        # 技术领域模板
        self.templates["technology_skill"] = KnowledgeTemplate(
            template_id="technology_skill",
            template_name="技术技能模板",
            domain_type=DomainType.TECHNOLOGY,
            required_fields=["skill_name", "category", "level"],
            optional_fields=["prerequisites", "applications", "tools", "certifications"],
            validation_rules={
                "skill_name": {"type": str, "min_length": 1},
                "level": {"type": str}
            },
            description="用于存储技术技能知识的模板"
        )
        
        # 教育领域模板
        self.templates["education_subject"] = KnowledgeTemplate(
            template_id="education_subject",
            template_name="学科知识模板",
            domain_type=DomainType.EDUCATION,
            required_fields=["subject_name", "grade_level", "core_concepts"],
            optional_fields=["prerequisites", "textbooks", "resources"],
            validation_rules={
                "subject_name": {"type": str, "min_length": 1},
                "core_concepts": {"type": list}
            },
            description="用于存储教育学科知识的模板"
        )
        
        # 医疗健康模板
        self.templates["health_condition"] = KnowledgeTemplate(
            template_id="health_condition",
            template_name="健康状况模板",
            domain_type=DomainType.HEALTHCARE,
            required_fields=["condition_name", "symptoms", "causes"],
            optional_fields=["treatments", "prevention", "medical_references"],
            validation_rules={
                "condition_name": {"type": str, "min_length": 1},
                "symptoms": {"type": list},
                "causes": {"type": list}
            },
            description="用于存储医疗健康知识的模板"
        )
        
        # 金融领域模板
        self.templates["finance_product"] = KnowledgeTemplate(
            template_id="finance_product",
            template_name="金融产品模板",
            domain_type=DomainType.FINANCE,
            required_fields=["product_name", "product_type", "risk_level"],
            optional_fields=["description", "interest_rate", "term", "eligibility"],
            validation_rules={
                "product_name": {"type": str, "min_length": 1},
                "risk_level": {"type": str}
            },
            description="用于存储金融产品知识的模板"
        )
        
        # 法律领域模板
        self.templates["legal_regulation"] = KnowledgeTemplate(
            template_id="legal_regulation",
            template_name="法律法规模板",
            domain_type=DomainType.LEGAL,
            required_fields=["regulation_name", "issuing_authority", "effective_date"],
            optional_fields=["content_summary", "applicable_scope", "penalties"],
            validation_rules={
                "regulation_name": {"type": str, "min_length": 1},
                "effective_date": {"type": str}
            },
            description="用于存储法律法规知识的模板"
        )
        
        # 科学领域模板
        self.templates["science_theory"] = KnowledgeTemplate(
            template_id="science_theory",
            template_name="科学理论模板",
            domain_type=DomainType.SCIENCE,
            required_fields=["theory_name", "field", "key_principles"],
            optional_fields=["founder", "year", "evidence", "applications"],
            validation_rules={
                "theory_name": {"type": str, "min_length": 1},
                "key_principles": {"type": list}
            },
            description="用于存储科学理论知识的模板"
        )
        
        # 语言领域模板
        self.templates["language_vocabulary"] = KnowledgeTemplate(
            template_id="language_vocabulary",
            template_name="语言词汇模板",
            domain_type=DomainType.LANGUAGE,
            required_fields=["word", "language", "part_of_speech"],
            optional_fields=["definition", "pronunciation", "examples", "synonyms", "antonyms"],
            validation_rules={
                "word": {"type": str, "min_length": 1},
                "language": {"type": str}
            },
            description="用于存储语言词汇知识的模板"
        )
    
    def _load_stored_knowledge(self):
        """加载存储的领域知识"""
        knowledge_file = self.data_dir / "domain_knowledges.json"
        if knowledge_file.exists():
            try:
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for k_data in data.get("knowledges", []):
                    domain_type = DomainType(k_data.get("domain_type", "custom"))
                    knowledge = DomainKnowledge(
                        knowledge_id=k_data["knowledge_id"],
                        domain_type=domain_type,
                        name=k_data["name"],
                        content=k_data.get("content", {}),
                        confidence=k_data.get("confidence", 0.8),
                        tags=k_data.get("tags", []),
                        sources=k_data.get("sources", []),
                        created_at=k_data.get("created_at"),
                        updated_at=k_data.get("updated_at")
                    )
                    self.domain_knowledges[knowledge.knowledge_id] = knowledge
            except Exception as e:
                print(f"加载领域知识失败: {e}")
    
    def _save_knowledge(self):
        """保存领域知识"""
        knowledge_file = self.data_dir / "domain_knowledges.json"
        
        data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "knowledges": []
        }
        
        for knowledge in self.domain_knowledges.values():
            data["knowledges"].append({
                "knowledge_id": knowledge.knowledge_id,
                "domain_type": knowledge.domain_type.value,
                "name": knowledge.name,
                "content": knowledge.content,
                "confidence": knowledge.confidence,
                "tags": knowledge.tags,
                "sources": knowledge.sources,
                "created_at": knowledge.created_at,
                "updated_at": knowledge.updated_at
            })
        
        try:
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存领域知识失败: {e}")
            return False
    
    def add_template(self, template: KnowledgeTemplate) -> bool:
        """添加知识模板"""
        if template.template_id in self.templates:
            print(f"模板 {template.template_id} 已存在")
            return False
        
        self.templates[template.template_id] = template
        print(f"添加知识模板: {template.template_name}")
        return True
    
    def get_template(self, template_id: str) -> Optional[KnowledgeTemplate]:
        """获取知识模板"""
        return self.templates.get(template_id)
    
    def list_templates(self, domain_type: Optional[DomainType] = None) -> List[KnowledgeTemplate]:
        """列出知识模板"""
        if domain_type:
            return [t for t in self.templates.values() if t.domain_type == domain_type]
        return list(self.templates.values())
    
    def register_domain_knowledge(self, knowledge: DomainKnowledge) -> bool:
        """注册领域知识"""
        if knowledge.knowledge_id in self.domain_knowledges:
            print(f"领域知识 {knowledge.knowledge_id} 已存在")
            return False
        
        self.domain_knowledges[knowledge.knowledge_id] = knowledge
        self._save_knowledge()
        
        print(f"注册领域知识: {knowledge.name}")
        return True
    
    def get_domain_knowledge(self, knowledge_id: str) -> Optional[DomainKnowledge]:
        """获取领域知识"""
        return self.domain_knowledges.get(knowledge_id)
    
    def search_domain_knowledge(self, keyword: str, 
                               domain_type: Optional[DomainType] = None,
                               tags: Optional[List[str]] = None) -> List[DomainKnowledge]:
        """搜索领域知识"""
        results = []
        
        for knowledge in self.domain_knowledges.values():
            match = keyword.lower() in knowledge.name.lower()
            
            if domain_type and knowledge.domain_type != domain_type:
                match = False
            
            if tags:
                tag_match = any(tag in knowledge.tags for tag in tags)
                if not tag_match:
                    match = False
            
            if match:
                results.append(knowledge)
        
        return results
    
    def enhance_knowledge_with_graph(self, knowledge: DomainKnowledge) -> DomainKnowledge:
        """利用知识图谱增强领域知识"""
        # 查找相关的知识图谱节点
        related_nodes = []
        for node in self.kg.nodes.values():
            if knowledge.name.lower() in node.name.lower():
                related_nodes.append(node)
            elif any(tag.lower() in node.name.lower() for tag in knowledge.tags):
                related_nodes.append(node)
        
        # 添加相关信息到领域知识
        if related_nodes:
            knowledge.content["related_graph_nodes"] = [
                {"name": n.name, "id": n.id} for n in related_nodes
            ]
        
        # 查找相关的边
        related_edges = []
        for edge in self.kg.edges:
            if (knowledge.name.lower() in edge.source.lower() or 
                knowledge.name.lower() in edge.target.lower()):
                related_edges.append(edge)
        
        if related_edges:
            knowledge.content["related_graph_edges"] = [
                {"source": e.source, "target": e.target, "relation": e.relation} 
                for e in related_edges
            ]
        
        knowledge.updated_at = datetime.now().isoformat()
        self._save_knowledge()
        
        return knowledge
    
    def add_adaptor(self, adaptor: DomainAdaptor) -> bool:
        """添加领域适配器"""
        if adaptor.adaptor_id in self.adaptors:
            print(f"领域适配器 {adaptor.adaptor_id} 已存在")
            return False
        
        self.adaptors[adaptor.adaptor_id] = adaptor
        print(f"添加领域适配器: {adaptor.name}")
        return True
    
    def get_adaptor(self, adaptor_id: str) -> Optional[DomainAdaptor]:
        """获取领域适配器"""
        return self.adaptors.get(adaptor_id)
    
    def list_adaptors(self, domain_type: Optional[DomainType] = None) -> List[DomainAdaptor]:
        """列出领域适配器"""
        if domain_type:
            return [a for a in self.adaptors.values() if a.domain_type == domain_type]
        return list(self.adaptors.values())
    
    def validate_against_template(self, content: Dict[str, Any], 
                                   template: KnowledgeTemplate) -> tuple[bool, List[str]]:
        """验证内容是否符合模板要求"""
        errors = []
        
        for field in template.required_fields:
            if field not in content or content[field] is None:
                errors.append(f"缺少必填字段: {field}")
        
        if template.validation_rules:
            for field, rules in template.validation_rules.items():
                if field in content:
                    value = content[field]
                    if "type" in rules:
                        expected_type = rules["type"]
                        if not isinstance(value, expected_type):
                            errors.append(f"字段 {field} 类型错误，期望 {expected_type.__name__}")
                    if "min_length" in rules and isinstance(value, str):
                        if len(value) < rules["min_length"]:
                            errors.append(f"字段 {field} 长度不足，至少 {rules['min_length']} 字符")
                    if "max_length" in rules and isinstance(value, str):
                        if len(value) > rules["max_length"]:
                            errors.append(f"字段 {field} 长度超限，最多 {rules['max_length']} 字符")
        
        return len(errors) == 0, errors
    
    def create_knowledge_from_template(self, template_id: str, name: str,
                                      content: Dict[str, Any],
                                      tags: Optional[List[str]] = None,
                                      sources: Optional[List[str]] = None) -> Optional[DomainKnowledge]:
        """基于模板创建领域知识"""
        template = self.get_template(template_id)
        if not template:
            print(f"模板 {template_id} 不存在")
            return None
        
        is_valid, errors = self.validate_against_template(content, template)
        if not is_valid:
            print(f"验证失败: {errors}")
            return None
        
        knowledge_id = f"{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        knowledge = DomainKnowledge(
            knowledge_id=knowledge_id,
            domain_type=template.domain_type,
            name=name,
            content=content,
            tags=tags or [],
            sources=sources or []
        )
        
        self.register_domain_knowledge(knowledge)
        return knowledge
    
    def update_knowledge(self, knowledge_id: str, content_updates: Dict[str, Any]) -> bool:
        """更新领域知识"""
        knowledge = self.get_domain_knowledge(knowledge_id)
        if not knowledge:
            print(f"领域知识 {knowledge_id} 不存在")
            return False
        
        knowledge.content.update(content_updates)
        knowledge.updated_at = datetime.now().isoformat()
        self._save_knowledge()
        
        print(f"更新领域知识: {knowledge.name}")
        return True
    
    def delete_knowledge(self, knowledge_id: str) -> bool:
        """删除领域知识"""
        if knowledge_id not in self.domain_knowledges:
            print(f"领域知识 {knowledge_id} 不存在")
            return False
        
        del self.domain_knowledges[knowledge_id]
        self._save_knowledge()
        
        print(f"删除领域知识: {knowledge_id}")
        return True
    
    def get_domain_stats(self) -> Dict[str, Any]:
        """获取领域统计信息"""
        domain_counts = {}
        for knowledge in self.domain_knowledges.values():
            domain_name = knowledge.domain_type.value
            domain_counts[domain_name] = domain_counts.get(domain_name, 0) + 1
        
        return {
            "total_knowledges": len(self.domain_knowledges),
            "total_templates": len(self.templates),
            "total_adaptors": len(self.adaptors),
            "knowledge_by_domain": domain_counts,
            "domains_available": [dt.value for dt in DomainType]
        }

