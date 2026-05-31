
"""
领域知识问答系统 - 阶段38
支持基于领域知识的智能问答
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re

from core.domain_knowledge_manager import DomainKnowledge, DomainType


class QuestionType(Enum):
    """问题类型"""
    DEFINITION = "definition"  # 定义
    FACT = "fact"  # 事实
    COMPARISON = "comparison"  # 比较
    PROCEDURE = "procedure"  # 流程
    RELATION = "relation"  # 关系
    UNKNOWN = "unknown"  # 未知


@dataclass
class Answer:
    """答案"""
    question: str
    answer_text: str
    confidence: float
    sources: List[DomainKnowledge] = field(default_factory=list)
    question_type: QuestionType = QuestionType.UNKNOWN
    related_questions: List[str] = field(default_factory=list)


@dataclass
class QAContext:
    """问答上下文"""
    session_id: str
    history: List[Dict[str, str]] = field(default_factory=list)
    current_domain: Optional[DomainType] = None


class DomainKnowledgeQA:
    """领域知识问答系统"""
    
    def __init__(self, domain_manager, domain_searcher):
        self.domain_manager = domain_manager
        self.domain_searcher = domain_searcher
        self.contexts: Dict[str, QAContext] = {}
    
    def _detect_question_type(self, question: str) -> QuestionType:
        """检测问题类型"""
        question_lower = question.lower()
        
        # 定义类问题
        definition_patterns = [
            r"什么是|什么是|.*?是什么|.*?的定义|.*?的意思",
            r"define|what is|what are"
        ]
        for pattern in definition_patterns:
            if re.search(pattern, question_lower):
                return QuestionType.DEFINITION
        
        # 比较类问题
        comparison_patterns = [
            r".*?和.*?的区别|.*?与.*?的比较|.*?vs.*?",
            r"difference between|compare|versus|vs"
        ]
        for pattern in comparison_patterns:
            if re.search(pattern, question_lower):
                return QuestionType.COMPARISON
        
        # 流程类问题
        procedure_patterns = [
            r"如何|怎么|步骤|流程|方法",
            r"how to|how do|steps|process|method"
        ]
        for pattern in procedure_patterns:
            if re.search(pattern, question_lower):
                return QuestionType.PROCEDURE
        
        # 关系类问题
        relation_patterns = [
            r".*?和.*?的关系|.*?对.*?的影响",
            r"relationship|relation|impact|effect"
        ]
        for pattern in relation_patterns:
            if re.search(pattern, question_lower):
                return QuestionType.RELATION
        
        return QuestionType.FACT
    
    def _extract_keywords(self, question: str) -> List[str]:
        """提取关键词"""
        # 移除停用词
        stop_words = {"的", "是", "在", "了", "和", "有", "我", "他", "她", "这", "那", "就", "都", "而", "及", "与", "着", "或", "什么", "如何", "怎么", "吗", "呢"}
        
        # 分词（简单实现）
        words = re.findall(r'\w+', question)
        keywords = [w for w in words if w not in stop_words and len(w) > 1]
        
        return keywords
    
    def ask(self, 
           question: str,
           session_id: str = "default",
           domain_type: Optional[DomainType] = None) -> Answer:
        """
        回答问题
        
        Args:
            question: 问题
            session_id: 会话ID
            domain_type: 领域类型限制
        
        Returns:
            答案
        """
        # 获取或创建上下文
        if session_id not in self.contexts:
            self.contexts[session_id] = QAContext(session_id=session_id)
        context = self.contexts[session_id]
        
        # 检测问题类型
        question_type = self._detect_question_type(question)
        
        # 提取关键词
        keywords = self._extract_keywords(question)
        
        # 搜索相关知识
        search_results = self.domain_searcher.search(
            query=question,
            search_type=self.domain_searcher.SearchType.HYBRID if hasattr(self.domain_searcher, 'SearchType') else None,
            domain_type=domain_type or context.current_domain,
            limit=5
        )
        
        # 生成答案
        if search_results:
            answer = self._generate_answer(question, question_type, search_results)
        else:
            answer = Answer(
                question=question,
                answer_text="抱歉，我暂时没有找到相关的知识来回答这个问题。",
                confidence=0.0,
                question_type=question_type
            )
        
        # 更新上下文
        context.history.append({"question": question, "answer": answer.answer_text})
        if search_results:
            context.current_domain = search_results[0].knowledge.domain_type
        
        return answer
    
    def _generate_answer(self, 
                        question: str,
                        question_type: QuestionType,
                        search_results: List[Any]) -> Answer:
        """生成答案"""
        if not search_results:
            return Answer(
                question=question,
                answer_text="未找到相关知识",
                confidence=0.0,
                question_type=question_type
            )
        
        # 获取最相关的知识
        top_result = search_results[0]
        knowledge = top_result.knowledge
        
        # 根据问题类型生成答案
        if question_type == QuestionType.DEFINITION:
            answer_text = self._generate_definition_answer(knowledge)
        elif question_type == QuestionType.COMPARISON:
            answer_text = self._generate_comparison_answer(question, search_results)
        elif question_type == QuestionType.PROCEDURE:
            answer_text = self._generate_procedure_answer(knowledge)
        elif question_type == QuestionType.RELATION:
            answer_text = self._generate_relation_answer(knowledge, search_results)
        else:
            answer_text = self._generate_fact_answer(knowledge)
        
        # 收集来源
        sources = [r.knowledge for r in search_results[:3]]
        
        # 生成相关问题
        related_questions = self._generate_related_questions(knowledge)
        
        return Answer(
            question=question,
            answer_text=answer_text,
            confidence=top_result.score,
            sources=sources,
            question_type=question_type,
            related_questions=related_questions
        )
    
    def _generate_definition_answer(self, knowledge: DomainKnowledge) -> str:
        """生成定义类答案"""
        name = knowledge.name
        content = knowledge.content
        
        # 构建定义描述
        parts = [f"{name}是"]
        
        # 添加关键属性
        if "description" in content:
            parts.append(content["description"])
        elif "skill_name" in content:
            parts.append(f"一种{content.get('category', '相关')}技能")
            if "level" in content:
                parts.append(f"，级别为{content['level']}")
        elif "condition_name" in content:
            parts.append(f"一种{content.get('category', '常见')}健康状况")
            if "symptoms" in content:
                symptoms = content["symptoms"]
                if isinstance(symptoms, list):
                    parts.append(f"，主要症状包括：{', '.join(symptoms)}")
        elif "subject_name" in content:
            parts.append(f"一门{content.get('grade_level', '')}学科")
            if "core_concepts" in content:
                concepts = content["core_concepts"]
                if isinstance(concepts, list):
                    parts.append(f"，核心概念包括：{', '.join(concepts)}")
        else:
            # 通用描述
            desc_parts = []
            for key, value in content.items():
                if key != "name" and value:
                    if isinstance(value, list):
                        desc_parts.append(f"{key}：{', '.join(str(v) for v in value)}")
                    else:
                        desc_parts.append(f"{key}：{value}")
            if desc_parts:
                parts.append("，".join(desc_parts[:3]))
        
        return "".join(parts) + "。"
    
    def _generate_comparison_answer(self, question: str, search_results: List[Any]) -> str:
        """生成比较类答案"""
        if len(search_results) < 2:
            return "需要至少两个对象进行比较。"
        
        k1 = search_results[0].knowledge
        k2 = search_results[1].knowledge
        
        differences = []
        
        # 比较内容
        for key in set(k1.content.keys()) & set(k2.content.keys()):
            if k1.content[key] != k2.content[key]:
                differences.append(f"{key}：{k1.name}为{k1.content[key]}，{k2.name}为{k2.content[key]}")
        
        if differences:
            return f"{k1.name}和{k2.name}的主要区别：\n" + "\n".join(f"- {d}" for d in differences[:5])
        else:
            return f"{k1.name}和{k2.name}在已知属性上较为相似。"
    
    def _generate_procedure_answer(self, knowledge: DomainKnowledge) -> str:
        """生成流程类答案"""
        content = knowledge.content
        
        if "steps" in content and isinstance(content["steps"], list):
            steps = content["steps"]
            return f"{knowledge.name}的步骤：\n" + "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
        elif "treatments" in content and isinstance(content["treatments"], list):
            treatments = content["treatments"]
            return f"{knowledge.name}的治疗方法：\n" + "\n".join(f"{i+1}. {t}" for i, t in enumerate(treatments))
        elif "prerequisites" in content and isinstance(content["prerequisites"], list):
            prereqs = content["prerequisites"]
            return f"学习{knowledge.name}的前提条件：\n" + "\n".join(f"- {p}" for p in prereqs)
        else:
            return f"关于{knowledge.name}的流程信息：{json.dumps(content, ensure_ascii=False)}"
    
    def _generate_relation_answer(self, knowledge: DomainKnowledge, search_results: List[Any]) -> str:
        """生成关系类答案"""
        related = [r.knowledge.name for r in search_results[1:4]]
        
        if related:
            return f"{knowledge.name}与以下知识相关：{', '.join(related)}。"
        else:
            return f"{knowledge.name}的相关信息：{knowledge.content}"
    
    def _generate_fact_answer(self, knowledge: DomainKnowledge) -> str:
        """生成事实类答案"""
        content = knowledge.content
        
        # 提取关键信息
        facts = []
        for key, value in content.items():
            if key != "name" and value:
                if isinstance(value, list):
                    facts.append(f"{key}：{', '.join(str(v) for v in value)}")
                else:
                    facts.append(f"{key}：{value}")
        
        if facts:
            return f"关于{knowledge.name}：\n" + "\n".join(f"- {f}" for f in facts[:5])
        else:
            return f"{knowledge.name}的相关信息已记录。"
    
    def _generate_related_questions(self, knowledge: DomainKnowledge) -> List[str]:
        """生成相关问题"""
        questions = []
        
        # 基于内容生成问题
        if "level" in knowledge.content:
            questions.append(f"{knowledge.name}的级别是什么？")
        if "category" in knowledge.content:
            questions.append(f"{knowledge.name}属于什么类别？")
        if "symptoms" in knowledge.content:
            questions.append(f"{knowledge.name}的症状有哪些？")
        if "applications" in knowledge.content:
            questions.append(f"{knowledge.name}可以应用于哪些领域？")
        if "prerequisites" in knowledge.content:
            questions.append(f"学习{knowledge.name}需要什么基础？")
        
        return questions[:3]
    
    def get_conversation_history(self, session_id: str = "default") -> List[Dict[str, str]]:
        """获取对话历史"""
        if session_id in self.contexts:
            return self.contexts[session_id].history
        return []
    
    def clear_conversation(self, session_id: str = "default"):
        """清除对话历史"""
        if session_id in self.contexts:
            self.contexts[session_id].history = []
            self.contexts[session_id].current_domain = None

