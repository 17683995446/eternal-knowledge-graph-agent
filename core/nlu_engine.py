
"""
自然语言理解引擎 - 阶段42
支持分词、实体识别、关系抽取、意图理解
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re


class IntentType(Enum):
    """意图类型"""
    QUERY = "query"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"
    COMPARE = "compare"
    EXPLAIN = "explain"
    GREETING = "greeting"
    UNKNOWN = "unknown"


@dataclass
class Entity:
    """实体"""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0


@dataclass
class Relation:
    """关系"""
    subject: str
    predicate: str
    object: str
    confidence: float = 1.0


@dataclass
class NLUResult:
    """自然语言理解结果"""
    text: str
    intent: IntentType
    entities: List[Entity] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    tokens: List[str] = field(default_factory=list)
    confidence: float = 0.0


class NLUEngine:
    """自然语言理解引擎"""
    
    def __init__(self):
        # 停用词
        self.stop_words = {"的", "是", "在", "了", "和", "有", "我", "他", "她", "这", "那", "就", "都", "而", "及", "与", "着", "或", "一个", "没有", "我们", "你们", "他们", "什么", "怎么", "如何", "为什么", "吗", "呢", "吧"}
        
        # 意图关键词
        self.intent_keywords = {
            IntentType.QUERY: ["什么是", "什么是", "什么是", "查询", "查找", "搜索", "告诉我", "解释", "说明"],
            IntentType.CREATE: ["创建", "新建", "添加", "增加", "插入", "生成"],
            IntentType.UPDATE: ["更新", "修改", "编辑", "改变", "调整", "修正"],
            IntentType.DELETE: ["删除", "移除", "清除", "去掉", "销毁"],
            IntentType.SEARCH: ["搜索", "查找", "寻找", "查询", "检索", "找"],
            IntentType.COMPARE: ["比较", "对比", "区别", "差异", "vs", "versus"],
            IntentType.EXPLAIN: ["解释", "说明", "阐述", "讲解", "介绍", "描述"],
            IntentType.GREETING: ["你好", "您好", "嗨", "hello", "hi", "hey", "早上好", "下午好", "晚上好"]
        }
        
        # 实体模式
        self.entity_patterns = {
            "technology": [r"Python", r"Java", r"JavaScript", r"C\+\+", r"Go", r"Rust", r"SQL"],
            "disease": [r"感冒", r"流感", r"发烧", r"咳嗽", r"头痛", r"肺炎"],
            "subject": [r"数学", r"物理", r"化学", r"生物", r"历史", r"地理", r"英语"],
            "person": [r"[\u4e00-\u9fa5]{2,4}(?:先生|女士|老师|教授|博士)"]
        }
    
    def parse(self, text: str) -> NLUResult:
        """解析文本"""
        # 分词
        tokens = self._tokenize(text)
        
        # 识别意图
        intent = self._detect_intent(text)
        
        # 识别实体
        entities = self._extract_entities(text)
        
        # 抽取关系
        relations = self._extract_relations(text, entities)
        
        # 计算置信度
        confidence = self._calculate_confidence(intent, entities, len(tokens))
        
        return NLUResult(
            text=text,
            intent=intent,
            entities=entities,
            relations=relations,
            tokens=tokens,
            confidence=confidence
        )
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        # 简单分词：按非字符分割
        tokens = re.findall(r'\w+', text)
        # 过滤停用词
        tokens = [t for t in tokens if t not in self.stop_words and len(t) > 1]
        return tokens
    
    def _detect_intent(self, text: str) -> IntentType:
        """检测意图"""
        text_lower = text.lower()
        
        scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[intent] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        # 默认意图
        if "?" in text or "？" in text or any(w in text for w in ["什么", "怎么", "为什么", "吗", "呢"]):
            return IntentType.QUERY
        
        return IntentType.UNKNOWN
    
    def _extract_entities(self, text: str) -> List[Entity]:
        """提取实体"""
        entities = []
        
        for label, patterns in self.entity_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entity = Entity(
                        text=match.group(),
                        label=label,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.8
                    )
                    entities.append(entity)
        
        # 去重
        seen = set()
        unique_entities = []
        for e in entities:
            key = (e.text, e.start, e.end)
            if key not in seen:
                seen.add(key)
                unique_entities.append(e)
        
        return unique_entities
    
    def _extract_relations(self, text: str, entities: List[Entity]) -> List[Relation]:
        """抽取关系"""
        relations = []
        
        if len(entities) >= 2:
            # 简单的关系模式
            relation_patterns = [
                (r"(.*?)和(.*?)的关系", "related_to"),
                (r"(.*?)对(.*?)的影响", "affects"),
                (r"(.*?)包含(.*?)", "contains"),
                (r"(.*?)属于(.*?)", "belongs_to"),
            ]
            
            for pattern, predicate in relation_patterns:
                match = re.search(pattern, text)
                if match:
                    relations.append(Relation(
                        subject=match.group(1).strip(),
                        predicate=predicate,
                        object=match.group(2).strip(),
                        confidence=0.7
                    ))
        
        return relations
    
    def _calculate_confidence(self, intent: IntentType, entities: List[Entity], token_count: int) -> float:
        """计算置信度"""
        score = 0.5
        
        # 意图识别加分
        if intent != IntentType.UNKNOWN:
            score += 0.2
        
        # 实体识别加分
        score += min(len(entities) * 0.1, 0.2)
        
        # 文本长度适中加分
        if 5 <= token_count <= 50:
            score += 0.1
        
        return min(score, 1.0)
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """提取关键词"""
        tokens = self._tokenize(text)
        
        # 统计词频
        from collections import Counter
        freq = Counter(tokens)
        
        # 返回高频词
        return [word for word, count in freq.most_common(top_n)]

