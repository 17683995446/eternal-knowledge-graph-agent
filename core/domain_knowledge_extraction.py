
"""
领域知识自动化抽取与构建系统 - 阶段37
支持从文本、网页、文档中自动抽取领域知识
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import re
from pathlib import Path

from core.domain_knowledge_manager import DomainKnowledge, DomainType, KnowledgeTemplate


class ExtractionSource(Enum):
    """抽取来源"""
    TEXT = "text"
    WEBPAGE = "webpage"
    DOCUMENT = "document"
    STRUCTURED_DATA = "structured_data"


@dataclass
class ExtractionResult:
    """抽取结果"""
    source_type: ExtractionSource
    extracted_knowledges: List[DomainKnowledge] = field(default_factory=list)
    raw_entities: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    errors: List[str] = field(default_factory=list)


@dataclass
class EntityPattern:
    """实体模式"""
    name: str
    domain_type: DomainType
    patterns: List[str] = field(default_factory=list)
    required_fields: List[str] = field(default_factory=list)


class DomainKnowledgeExtractor:
    """领域知识抽取器"""
    
    def __init__(self, domain_manager):
        self.domain_manager = domain_manager
        self.patterns: Dict[str, EntityPattern] = {}
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """初始化抽取模式"""
        # 技术技能模式
        self.patterns["technology"] = EntityPattern(
            name="技术技能",
            domain_type=DomainType.TECHNOLOGY,
            patterns=[
                r"(\w+)\s*(?:编程|开发|技术|框架|工具)",
                r"(?:学习|掌握|使用)\s*(\w+)",
            ],
            required_fields=["skill_name", "category"]
        )
        
        # 健康状况模式
        self.patterns["healthcare"] = EntityPattern(
            name="健康状况",
            domain_type=DomainType.HEALTHCARE,
            patterns=[
                r"(\w+)(?:症|病|炎|癌|感染)",
                r"(?:症状|表现).*?[:：]\s*(.+)",
            ],
            required_fields=["condition_name", "symptoms"]
        )
        
        # 教育学科模式
        self.patterns["education"] = EntityPattern(
            name="教育学科",
            domain_type=DomainType.EDUCATION,
            patterns=[
                r"(\w+)(?:学|课程|学科|专业)",
                r"(?:学习|教授|研究)\s*(\w+)",
            ],
            required_fields=["subject_name", "grade_level"]
        )
    
    def extract_from_text(self, 
                         text: str,
                         domain_type: Optional[DomainType] = None) -> ExtractionResult:
        """
        从文本中抽取知识
        
        Args:
            text: 输入文本
            domain_type: 指定领域类型，None则自动检测
        
        Returns:
            抽取结果
        """
        result = ExtractionResult(source_type=ExtractionSource.TEXT)
        
        if domain_type:
            # 使用指定领域模式
            pattern = self._get_pattern_by_domain(domain_type)
            if pattern:
                knowledges = self._extract_with_pattern(text, pattern)
                result.extracted_knowledges.extend(knowledges)
        else:
            # 尝试所有领域模式
            for pattern in self.patterns.values():
                knowledges = self._extract_with_pattern(text, pattern)
                result.extracted_knowledges.extend(knowledges)
        
        # 计算置信度
        if result.extracted_knowledges:
            result.confidence = sum(k.confidence for k in result.extracted_knowledges) / len(result.extracted_knowledges)
        
        return result
    
    def _get_pattern_by_domain(self, domain_type: DomainType) -> Optional[EntityPattern]:
        """根据领域类型获取模式"""
        for pattern in self.patterns.values():
            if pattern.domain_type == domain_type:
                return pattern
        return None
    
    def _extract_with_pattern(self, text: str, pattern: EntityPattern) -> List[DomainKnowledge]:
        """使用模式抽取知识"""
        knowledges = []
        
        # 使用正则表达式匹配
        for regex_pattern in pattern.patterns:
            matches = re.finditer(regex_pattern, text, re.IGNORECASE)
            for match in matches:
                entity_name = match.group(1).strip()
                if len(entity_name) < 2:
                    continue
                
                # 尝试提取更多属性
                content = self._extract_entity_attributes(text, entity_name, pattern)
                
                knowledge = DomainKnowledge(
                    knowledge_id=f"extracted_{pattern.domain_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(knowledges)}",
                    domain_type=pattern.domain_type,
                    name=entity_name,
                    content=content,
                    confidence=0.6,
                    tags=[pattern.domain_type.value, "auto_extracted"],
                    sources=["text_extraction"]
                )
                
                knowledges.append(knowledge)
        
        return knowledges
    
    def _extract_entity_attributes(self, text: str, entity_name: str, pattern: EntityPattern) -> Dict[str, Any]:
        """提取实体属性"""
        content = {"name": entity_name}
        
        # 查找实体周围的上下文
        entity_pos = text.find(entity_name)
        if entity_pos >= 0:
            # 获取前后100个字符的上下文
            start = max(0, entity_pos - 100)
            end = min(len(text), entity_pos + len(entity_name) + 100)
            context = text[start:end]
            
            # 根据领域类型提取特定属性
            if pattern.domain_type == DomainType.TECHNOLOGY:
                content.update(self._extract_tech_attributes(context, entity_name))
            elif pattern.domain_type == DomainType.HEALTHCARE:
                content.update(self._extract_health_attributes(context, entity_name))
            elif pattern.domain_type == DomainType.EDUCATION:
                content.update(self._extract_education_attributes(context, entity_name))
        
        return content
    
    def _extract_tech_attributes(self, context: str, entity_name: str) -> Dict[str, Any]:
        """提取技术属性"""
        attrs = {}
        
        # 提取类别
        category_patterns = [
            r"(?:属于|是)\s*(\w+)(?:语言|框架|工具|技术)",
            r"(\w+)(?:语言|框架|工具|技术)",
        ]
        for pattern in category_patterns:
            match = re.search(pattern, context)
            if match:
                attrs["category"] = match.group(1)
                break
        
        # 提取级别
        level_patterns = [
            r"(初级|中级|高级|专家)",
            r"(入门|进阶|精通)",
        ]
        for pattern in level_patterns:
            match = re.search(pattern, context)
            if match:
                attrs["level"] = match.group(1)
                break
        
        # 提取应用
        app_match = re.search(r"(?:用于|应用).*?[:：]\s*(.+?)(?:。|$)", context)
        if app_match:
            attrs["applications"] = [a.strip() for a in app_match.group(1).split("、")]
        
        return attrs
    
    def _extract_health_attributes(self, context: str, entity_name: str) -> Dict[str, Any]:
        """提取健康属性"""
        attrs = {}
        
        # 提取症状
        symptom_match = re.search(r"(?:症状|表现).*?[:：]\s*(.+?)(?:。|$)", context)
        if symptom_match:
            attrs["symptoms"] = [s.strip() for s in symptom_match.group(1).split("、")]
        
        # 提取原因
        cause_match = re.search(r"(?:原因|病因).*?[:：]\s*(.+?)(?:。|$)", context)
        if cause_match:
            attrs["causes"] = [c.strip() for c in cause_match.group(1).split("、")]
        
        # 提取治疗
        treatment_match = re.search(r"(?:治疗|疗法).*?[:：]\s*(.+?)(?:。|$)", context)
        if treatment_match:
            attrs["treatments"] = [t.strip() for t in treatment_match.group(1).split("、")]
        
        return attrs
    
    def _extract_education_attributes(self, context: str, entity_name: str) -> Dict[str, Any]:
        """提取教育属性"""
        attrs = {}
        
        # 提取级别
        level_match = re.search(r"(?:级别|阶段|年级).*?[:：]\s*(.+?)(?:。|$)", context)
        if level_match:
            attrs["grade_level"] = level_match.group(1).strip()
        
        # 提取核心概念
        concept_match = re.search(r"(?:核心|重点|概念).*?[:：]\s*(.+?)(?:。|$)", context)
        if concept_match:
            attrs["core_concepts"] = [c.strip() for c in concept_match.group(1).split("、")]
        
        return attrs
    
    def extract_from_structured_data(self, 
                                    data: List[Dict[str, Any]],
                                    domain_type: DomainType,
                                    field_mapping: Dict[str, str]) -> ExtractionResult:
        """
        从结构化数据中抽取知识
        
        Args:
            data: 结构化数据列表
            domain_type: 领域类型
            field_mapping: 字段映射 {目标字段: 源字段}
        
        Returns:
            抽取结果
        """
        result = ExtractionResult(source_type=ExtractionSource.STRUCTURED_DATA)
        
        for i, item in enumerate(data):
            try:
                content = {}
                for target_field, source_field in field_mapping.items():
                    if source_field in item:
                        content[target_field] = item[source_field]
                
                # 生成名称
                name = content.get("name", content.get("skill_name", content.get("condition_name", f"Item_{i}")))
                
                knowledge = DomainKnowledge(
                    knowledge_id=f"structured_{domain_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}",
                    domain_type=domain_type,
                    name=name,
                    content=content,
                    confidence=0.8,
                    tags=[domain_type.value, "structured_data"],
                    sources=["structured_import"]
                )
                
                result.extracted_knowledges.append(knowledge)
            except Exception as e:
                result.errors.append(f"处理第{i}条数据失败: {str(e)}")
        
        if result.extracted_knowledges:
            result.confidence = 0.8
        
        return result
    
    def batch_register(self, result: ExtractionResult) -> Dict[str, int]:
        """批量注册抽取的知识"""
        stats = {"success": 0, "failed": 0}
        
        for knowledge in result.extracted_knowledges:
            success = self.domain_manager.register_domain_knowledge(knowledge)
            if success:
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        return stats
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """获取抽取统计"""
        return {
            "total_patterns": len(self.patterns),
            "patterns": [
                {
                    "name": p.name,
                    "domain": p.domain_type.value,
                    "pattern_count": len(p.patterns)
                }
                for p in self.patterns.values()
            ]
        }

