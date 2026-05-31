
"""
网页爬虫与知识自动构建 - 阶段44
支持网页爬取、文档解析、非结构化数据提取
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import json
from pathlib import Path


class CrawlSource(Enum):
    """爬取来源"""
    WEBPAGE = "webpage"
    DOCUMENT = "document"
    API = "api"
    DATABASE = "database"


@dataclass
class CrawledContent:
    """爬取内容"""
    source_url: str
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_entities: List[Dict] = field(default_factory=list)
    crawl_time: str = field(default_factory=lambda: datetime.now().isoformat())


class WebCrawler:
    """网页爬虫"""
    
    def __init__(self, domain_extractor):
        self.domain_extractor = domain_extractor
        self.crawl_history: List[str] = []
        self.max_content_length = 10000
    
    def crawl_text(self, 
                  text: str,
                  source: str = "unknown",
                  title: str = "") -> CrawledContent:
        """
        爬取文本内容
        
        Args:
            text: 文本内容
            source: 来源标识
            title: 标题
        
        Returns:
            爬取内容
        """
        # 清理文本
        cleaned_text = self._clean_text(text)
        
        # 提取实体
        entities = self._extract_entities_from_text(cleaned_text)
        
        # 截断过长内容
        if len(cleaned_text) > self.max_content_length:
            cleaned_text = cleaned_text[:self.max_content_length] + "..."
        
        content = CrawledContent(
            source_url=source,
            title=title or "未命名",
            content=cleaned_text,
            metadata={
                "length": len(cleaned_text),
                "entity_count": len(entities)
            },
            extracted_entities=entities
        )
        
        self.crawl_history.append(source)
        
        return content
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', ' ', text)
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fa5.,;:!?-]', '', text)
        return text.strip()
    
    def _extract_entities_from_text(self, text: str) -> List[Dict]:
        """从文本提取实体"""
        entities = []
        
        # 技术实体
        tech_pattern = r'\b(Python|Java|JavaScript|C\+\+|Go|Rust|SQL|HTML|CSS|React|Vue|Angular)\b'
        for match in re.finditer(tech_pattern, text, re.IGNORECASE):
            entities.append({
                "text": match.group(),
                "label": "technology",
                "start": match.start(),
                "end": match.end()
            })
        
        # 疾病实体
        disease_pattern = r'(感冒|流感|发烧|咳嗽|头痛|肺炎|高血压|糖尿病)'
        for match in re.finditer(disease_pattern, text):
            entities.append({
                "text": match.group(),
                "label": "disease",
                "start": match.start(),
                "end": match.end()
            })
        
        # 学科实体
        subject_pattern = r'(数学|物理|化学|生物|历史|地理|英语|语文|政治)'
        for match in re.finditer(subject_pattern, text):
            entities.append({
                "text": match.group(),
                "label": "subject",
                "start": match.start(),
                "end": match.end()
            })
        
        return entities
    
    def parse_document(self, 
                      content: str,
                      doc_type: str = "text") -> List[CrawledContent]:
        """
        解析文档
        
        Args:
            content: 文档内容
            doc_type: 文档类型
        
        Returns:
            解析后的内容列表
        """
        results = []
        
        if doc_type == "text":
            # 按段落分割
            paragraphs = content.split('\n\n')
            for i, para in enumerate(paragraphs):
                if len(para.strip()) > 50:
                    crawled = self.crawl_text(
                        para.strip(),
                        source=f"document_para_{i}",
                        title=f"段落 {i+1}"
                    )
                    results.append(crawled)
        
        elif doc_type == "json":
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    for i, item in enumerate(data):
                        if isinstance(item, dict):
                            text = json.dumps(item, ensure_ascii=False)
                            crawled = self.crawl_text(
                                text,
                                source=f"json_item_{i}",
                                title=item.get("name", f"Item {i}")
                            )
                            results.append(crawled)
            except json.JSONDecodeError:
                pass
        
        return results
    
    def build_knowledge_from_crawled(self, 
                                    crawled_content: CrawledContent) -> List[Any]:
        """从爬取内容构建知识"""
        # 使用抽取器提取知识
        from core.domain_knowledge_extraction import ExtractionSource
        
        result = self.domain_extractor.extract_from_text(
            crawled_content.content
        )
        
        return result.extracted_knowledges
    
    def get_crawl_stats(self) -> Dict[str, Any]:
        """获取爬取统计"""
        return {
            "total_crawls": len(self.crawl_history),
            "unique_sources": len(set(self.crawl_history)),
            "recent_sources": self.crawl_history[-10:] if self.crawl_history else []
        }

