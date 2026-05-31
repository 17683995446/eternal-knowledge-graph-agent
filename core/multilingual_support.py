
"""
跨语言知识处理 - 阶段45
支持多语言、翻译集成、跨语言知识对齐
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Language(Enum):
    """支持的语言"""
    CHINESE = "zh"
    ENGLISH = "en"
    JAPANESE = "ja"
    KOREAN = "ko"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    RUSSIAN = "ru"


@dataclass
class Translation:
    """翻译结果"""
    source_text: str
    target_text: str
    source_lang: str
    target_lang: str
    confidence: float = 0.0


@dataclass
class MultilingualKnowledge:
    """多语言知识"""
    knowledge_id: str
    translations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    primary_language: str = "zh"
    aligned_entities: List[Dict] = field(default_factory=list)


class MultilingualSupport:
    """多语言支持系统"""
    
    def __init__(self):
        self.language_detectors = {
            Language.CHINESE: lambda text: any('\u4e00' <= c <= '\u9fff' for c in text),
            Language.ENGLISH: lambda text: text.isascii() and any(c.isalpha() for c in text),
            Language.JAPANESE: lambda text: any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text),
        }
        
        # 简单翻译字典（示例）
        self.translation_dict = {
            ("zh", "en"): {
                "Python": "Python",
                "编程": "programming",
                "语言": "language",
                "技术": "technology",
                "健康": "health",
                "教育": "education",
                "金融": "finance",
                "法律": "legal",
                "科学": "science",
                "感冒": "cold",
                "症状": "symptom",
                "治疗": "treatment",
                "数学": "mathematics",
                "物理": "physics",
                "化学": "chemistry",
            },
            ("en", "zh"): {
                "Python": "Python",
                "programming": "编程",
                "language": "语言",
                "technology": "技术",
                "health": "健康",
                "education": "教育",
                "finance": "金融",
                "legal": "法律",
                "science": "科学",
                "cold": "感冒",
                "symptom": "症状",
                "treatment": "治疗",
                "mathematics": "数学",
                "physics": "物理",
                "chemistry": "化学",
            }
        }
    
    def detect_language(self, text: str) -> str:
        """检测语言"""
        for lang, detector in self.language_detectors.items():
            if detector(text):
                return lang.value
        return "unknown"
    
    def translate(self, 
                 text: str,
                 source_lang: str,
                 target_lang: str) -> Translation:
        """
        翻译文本
        
        Args:
            text: 原文
            source_lang: 源语言代码
            target_lang: 目标语言代码
        
        Returns:
            翻译结果
        """
        dict_key = (source_lang, target_lang)
        
        if dict_key in self.translation_dict:
            # 查找词典
            translated = self.translation_dict[dict_key].get(text, text)
            return Translation(
                source_text=text,
                target_text=translated,
                source_lang=source_lang,
                target_lang=target_lang,
                confidence=0.8 if translated != text else 0.3
            )
        
        # 无法翻译，返回原文
        return Translation(
            source_text=text,
            target_text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            confidence=0.1
        )
    
    def translate_knowledge(self, 
                           knowledge_content: Dict[str, Any],
                           source_lang: str,
                           target_lang: str) -> Dict[str, Any]:
        """翻译知识内容"""
        translated = {}
        
        for key, value in knowledge_content.items():
            if isinstance(value, str):
                result = self.translate(value, source_lang, target_lang)
                translated[key] = result.target_text
            elif isinstance(value, list):
                translated_list = []
                for item in value:
                    if isinstance(item, str):
                        result = self.translate(item, source_lang, target_lang)
                        translated_list.append(result.target_text)
                    else:
                        translated_list.append(item)
                translated[key] = translated_list
            else:
                translated[key] = value
        
        return translated
    
    def align_knowledges(self, 
                        knowledge_list: List[Any],
                        languages: List[str]) -> List[MultilingualKnowledge]:
        """对齐多语言知识"""
        aligned = []
        
        for knowledge in knowledge_list:
            mk = MultilingualKnowledge(
                knowledge_id=knowledge.knowledge_id if hasattr(knowledge, 'knowledge_id') else str(id(knowledge)),
                primary_language=languages[0] if languages else "zh"
            )
            
            # 添加各语言版本
            for lang in languages:
                if lang == mk.primary_language:
                    mk.translations[lang] = {
                        "name": knowledge.name if hasattr(knowledge, 'name') else "",
                        "content": knowledge.content if hasattr(knowledge, 'content') else {}
                    }
                else:
                    # 翻译内容
                    translated_content = self.translate_knowledge(
                        knowledge.content if hasattr(knowledge, 'content') else {},
                        mk.primary_language,
                        lang
                    )
                    translated_name = self.translate(
                        knowledge.name if hasattr(knowledge, 'name') else "",
                        mk.primary_language,
                        lang
                    )
                    mk.translations[lang] = {
                        "name": translated_name.target_text,
                        "content": translated_content
                    }
            
            aligned.append(mk)
        
        return aligned
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """获取支持的语言列表"""
        return [
            {"code": lang.value, "name": lang.name}
            for lang in Language
        ]
    
    def get_translation_stats(self) -> Dict[str, Any]:
        """获取翻译统计"""
        total_pairs = sum(len(d) for d in self.translation_dict.values())
        
        return {
            "supported_language_pairs": len(self.translation_dict),
            "total_translation_entries": total_pairs,
            "supported_languages": [lang.value for lang in Language]
        }

