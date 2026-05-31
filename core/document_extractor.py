
"""
文档知识抽取模块 - 永动知识图谱Agent
支持从各种文档格式中抽取知识
"""

import re
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time


class DocumentType(Enum):
    """文档类型枚举"""
    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
    CSV = "csv"
    UNKNOWN = "unknown"


@dataclass
class ExtractedEntity:
    """抽取的实体"""
    entity_type: str
    entity_name: str
    properties: Dict[str, Any]
    source: str
    confidence: float = 0.5


@dataclass
class ExtractedRelation:
    """抽取的关系"""
    source_entity: str
    relation_type: str
    target_entity: str
    properties: Dict[str, Any]
    source: str
    confidence: float = 0.5


@dataclass
class ExtractionResult:
    """抽取结果"""
    entities: List[ExtractedEntity]
    relations: List[ExtractedRelation]
    metadata: Dict[str, Any]


class DocumentKnowledgeExtractor:
    """文档知识抽取器"""
    
    def __init__(self):
        # 实体模式
        self._entity_patterns = {
            "person": [
                r'[A-Z][a-z]+ [A-Z][a-z]+',
            ],
            "organization": [
                r'[A-Z][a-zA-Z]+ (?:Inc|Corp|LLC|Ltd|Company|Group)',
                r'[A-Z][a-zA-Z]+ (?:University|Institute|Laboratory)',
            ],
            "location": [
                r'(?:New York|Los Angeles|Chicago|Houston|Phoenix)',
                r'(?:USA|UK|China|Japan|Germany|France)',
            ],
            "concept": [
                r'"[^"]+"',
            ],
        }
        
        # 关系模式
        self._relation_patterns = {
            "is_a": [
                r'(\w+) is a (\w+)',
                r'(\w+) are (\w+)',
            ],
            "has": [
                r'(\w+) has (\w+)',
                r'(\w+) have (\w+)',
            ],
            "related_to": [
                r'(\w+) and (\w+)',
                r'(\w+) with (\w+)',
            ],
        }
        
        # 停用词
        self._stopwords = {
            "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
            "be", "been", "being", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "may", "might", "must", "can",
            "to", "of", "in", "for", "on", "with", "at", "by", "from", "up",
            "about", "into", "through", "during", "before", "after", "above",
            "below", "between", "under", "again", "further", "then", "once",
            "here", "there", "when", "where", "why", "how", "all", "each",
            "few", "more", "most", "other", "some", "such", "no", "nor", "not",
            "only", "own", "same", "so", "than", "too", "very", "s", "t", "just",
        }
    
    def detect_document_type(self, filepath: str) -> DocumentType:
        """
        检测文档类型
        
        Args:
            filepath: 文件路径
            
        Returns:
            文档类型
        """
        ext = os.path.splitext(filepath)[1].lower()
        if ext in ['.txt']:
            return DocumentType.TEXT
        elif ext in ['.md', '.markdown']:
            return DocumentType.MARKDOWN
        elif ext in ['.json']:
            return DocumentType.JSON
        elif ext in ['.csv']:
            return DocumentType.CSV
        else:
            return DocumentType.UNKNOWN
    
    def read_document(self, filepath: str) -> Optional[str]:
        """
        读取文档内容
        
        Args:
            filepath: 文件路径
            
        Returns:
            文档内容
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def extract_from_text(self, text: str, source: str = "text") -> ExtractionResult:
        """
        从纯文本中抽取知识
        
        Args:
            text: 文本内容
            source: 来源标识
            
        Returns:
            抽取结果
        """
        entities: List[ExtractedEntity] = []
        relations: List[ExtractedRelation] = []
        entity_names = set()
        
        # 分句
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # 抽取实体
            sentence_entities = self._extract_entities_from_sentence(sentence, source)
            for entity in sentence_entities:
                if entity.entity_name not in entity_names:
                    entities.append(entity)
                    entity_names.add(entity.entity_name)
            
            # 抽取关系
            sentence_relations = self._extract_relations_from_sentence(sentence, source, [e.entity_name for e in sentence_entities])
            relations.extend(sentence_relations)
        
        # 抽取关键词作为概念
        keywords = self._extract_keywords(text)
        for keyword in keywords[:20]:  # 限制数量
            if keyword not in entity_names and keyword not in self._stopwords and len(keyword) > 2:
                entities.append(ExtractedEntity(
                    entity_type="concept",
                    entity_name=keyword,
                    properties={"source": "keyword_extraction"},
                    source=source,
                    confidence=0.4
                ))
                entity_names.add(keyword)
        
        return ExtractionResult(
            entities=entities,
            relations=relations,
            metadata={
                "source": source,
                "sentence_count": len(sentences),
                "entity_count": len(entities),
                "relation_count": len(relations),
                "timestamp": time.time()
            }
        )
    
    def extract_from_markdown(self, text: str, source: str = "markdown") -> ExtractionResult:
        """
        从Markdown中抽取知识
        
        Args:
            text: Markdown内容
            source: 来源标识
            
        Returns:
            抽取结果
        """
        # 先提取纯文本
        plain_text = self._markdown_to_plain_text(text)
        
        # 从纯文本抽取
        result = self.extract_from_text(plain_text, source)
        
        # 添加Markdown特定元数据
        titles = self._extract_markdown_titles(text)
        result.metadata["titles"] = titles
        
        return result
    
    def extract_from_json(self, json_data: Dict[str, Any], source: str = "json") -> ExtractionResult:
        """
        从JSON中抽取知识
        
        Args:
            json_data: JSON数据
            source: 来源标识
            
        Returns:
            抽取结果
        """
        entities: List[ExtractedEntity] = []
        relations: List[ExtractedRelation] = []
        
        # 递归处理JSON
        self._process_json_object(json_data, "", entities, relations, source)
        
        return ExtractionResult(
            entities=entities,
            relations=relations,
            metadata={
                "source": source,
                "entity_count": len(entities),
                "relation_count": len(relations),
                "timestamp": time.time()
            }
        )
    
    def extract_from_file(self, filepath: str) -> Optional[ExtractionResult]:
        """
        从文件中抽取知识
        
        Args:
            filepath: 文件路径
            
        Returns:
            抽取结果
        """
        doc_type = self.detect_document_type(filepath)
        content = self.read_document(filepath)
        
        if not content:
            return None
        
        source = os.path.basename(filepath)
        
        if doc_type == DocumentType.TEXT:
            return self.extract_from_text(content, source)
        elif doc_type == DocumentType.MARKDOWN:
            return self.extract_from_markdown(content, source)
        elif doc_type == DocumentType.JSON:
            try:
                json_data = json.loads(content)
                return self.extract_from_json(json_data, source)
            except Exception:
                return self.extract_from_text(content, source)
        else:
            return self.extract_from_text(content, source)
    
    def extraction_result_to_knowledge_graph(self, result: ExtractionResult) -> List[Dict[str, Any]]:
        """
        将抽取结果转换为知识图谱数据
        
        Args:
            result: 抽取结果
            
        Returns:
            知识图谱数据（节点和边）
        """
        knowledge = []
        
        # 添加实体节点
        for entity in result.entities:
            knowledge.append({
                "type": "node",
                "name": entity.entity_name,
                "node_type": entity.entity_type,
                "properties": {
                    **entity.properties,
                    "source": entity.source,
                    "confidence": entity.confidence
                }
            })
        
        # 添加关系边
        for relation in result.relations:
            knowledge.append({
                "type": "edge",
                "source": relation.source_entity,
                "target": relation.target_entity,
                "relation_type": relation.relation_type,
                "properties": {
                    **relation.properties,
                    "source": relation.source,
                    "confidence": relation.confidence
                }
            })
        
        return knowledge
    
    def _extract_entities_from_sentence(self, sentence: str, source: str) -> List[ExtractedEntity]:
        """从句子中抽取实体"""
        entities = []
        for entity_type, patterns in self._entity_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, sentence)
                for match in matches:
                    entity_name = match.strip() if isinstance(match, str) else match[0].strip()
                    entity_name = entity_name.strip('"')
                    if len(entity_name) > 1:
                        entities.append(ExtractedEntity(
                            entity_type=entity_type,
                            entity_name=entity_name,
                            properties={"extracted_from": sentence},
                            source=source,
                            confidence=0.6
                        ))
        return entities
    
    def _extract_relations_from_sentence(self, sentence: str, source: str, entity_names: List[str]) -> List[ExtractedRelation]:
        """从句子中抽取关系"""
        relations = []
        for relation_type, patterns in self._relation_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    if len(match) >= 2:
                        source_entity = match[0].strip()
                        target_entity = match[1].strip()
                        if source_entity in entity_names or target_entity in entity_names:
                            relations.append(ExtractedRelation(
                                source_entity=source_entity,
                                relation_type=relation_type,
                                target_entity=target_entity,
                                properties={"extracted_from": sentence},
                                source=source,
                                confidence=0.5
                            ))
        return relations
    
    def _extract_keywords(self, text: str, top_n: int = 20) -> List[str]:
        """抽取关键词"""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_freq = {}
        for word in words:
            if word not in self._stopwords:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]
    
    def _markdown_to_plain_text(self, markdown: str) -> str:
        """简单的Markdown转纯文本"""
        text = markdown
        text = re.sub(r'#+\s*', '', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
        text = re.sub(r'\[([^\]]*)\]\([^)]+\)', r'\1', text)
        return text
    
    def _extract_markdown_titles(self, markdown: str) -> List[str]:
        """提取Markdown标题"""
        titles = re.findall(r'^#+\s*(.+)$', markdown, re.MULTILINE)
        return [title.strip() for title in titles]
    
    def _process_json_object(self, obj: Any, path: str, entities: List[ExtractedEntity], 
                            relations: List[ExtractedRelation], source: str) -> None:
        """递归处理JSON对象"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                if isinstance(value, (str, int, float, bool)):
                    entities.append(ExtractedEntity(
                        entity_type="json_field",
                        entity_name=current_path,
                        properties={"value": str(value), "data_type": type(value).__name__},
                        source=source,
                        confidence=0.8
                    ))
                
                self._process_json_object(value, current_path, entities, relations, source)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                self._process_json_object(item, current_path, entities, relations, source)

