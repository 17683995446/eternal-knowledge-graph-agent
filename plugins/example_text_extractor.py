
"""
示例文本知识抽取插件
"""

import sys
import os

# 添加父目录到路径，以便导入插件基类
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.plugins import KnowledgeExtractorPlugin, PluginType
from core.document_extractor import DocumentKnowledgeExtractor
from typing import List, Dict, Any


class ExampleTextExtractorPlugin(KnowledgeExtractorPlugin):
    """示例文本知识抽取插件"""
    
    def __init__(self):
        super().__init__()
        self._extractor = None
    
    def get_name(self) -> str:
        return "Example Text Extractor"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_author(self) -> str:
        return "Eternal Agent Team"
    
    def get_description(self) -> str:
        return "A plugin that extracts knowledge from text documents using simple pattern matching"
    
    def get_plugin_type(self) -> PluginType:
        return PluginType.KNOWLEDGE_EXTRACTOR
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            "min_confidence": 0.4,
            "max_entities": 100,
            "enable_keyword_extraction": True
        }
    
    def initialize(self, agent, config=None) -> bool:
        super().initialize(agent, config)
        self._extractor = DocumentKnowledgeExtractor()
        return True
    
    def extract(self, source, **kwargs) -> List[Dict[str, Any]]:
        """从文本源抽取知识"""
        if not self._extractor:
            return []
        
        min_confidence = self._info.config.get("min_confidence", 0.4)
        max_entities = self._info.config.get("max_entities", 100)
        
        result = None
        
        # 判断源类型
        if isinstance(source, str):
            if os.path.isfile(source):
                result = self._extractor.extract_from_file(source)
            else:
                result = self._extractor.extract_from_text(source)
        
        if not result:
            return []
        
        # 转换为知识图谱格式
        knowledge = self._extractor.extraction_result_to_knowledge_graph(result)
        
        # 过滤低置信度的
        filtered_knowledge = []
        entity_count = 0
        
        for item in knowledge:
            if item.get("properties", {}).get("confidence", 0) >= min_confidence:
                if item["type"] == "node" and entity_count >= max_entities:
                    continue
                if item["type"] == "node":
                    entity_count += 1
                filtered_knowledge.append(item)
        
        return filtered_knowledge

