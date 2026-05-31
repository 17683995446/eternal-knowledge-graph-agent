
"""
对话管理系统 - 阶段43
支持上下文保持、多轮对话、自然语言回复生成
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from core.nlu_engine import NLUEngine, IntentType


class DialogueState(Enum):
    """对话状态"""
    START = "start"
    IN_PROGRESS = "in_progress"
    WAITING_CLARIFICATION = "waiting_clarification"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class DialogueTurn:
    """对话轮次"""
    turn_id: int
    user_input: str
    system_response: str
    intent: str = ""
    entities: List[Dict] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DialogueContext:
    """对话上下文"""
    session_id: str
    turns: List[DialogueTurn] = field(default_factory=list)
    current_state: DialogueState = DialogueState.START
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    domain_context: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class DialogueManager:
    """对话管理器"""
    
    def __init__(self, domain_qa, domain_manager):
        self.nlu = NLUEngine()
        self.domain_qa = domain_qa
        self.domain_manager = domain_manager
        
        self.contexts: Dict[str, DialogueContext] = {}
        self.max_history = 10
    
    def process_input(self, 
                     user_input: str,
                     session_id: str = "default") -> str:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入
            session_id: 会话ID
        
        Returns:
            系统回复
        """
        # 获取或创建上下文
        if session_id not in self.contexts:
            self.contexts[session_id] = DialogueContext(session_id=session_id)
        
        context = self.contexts[session_id]
        
        # NLU解析
        nlu_result = self.nlu.parse(user_input)
        
        # 更新状态
        context.current_state = DialogueState.IN_PROGRESS
        
        # 生成回复
        response = self._generate_response(user_input, nlu_result, context)
        
        # 记录对话轮次
        turn = DialogueTurn(
            turn_id=len(context.turns) + 1,
            user_input=user_input,
            system_response=response,
            intent=nlu_result.intent.value,
            entities=[{"text": e.text, "label": e.label} for e in nlu_result.entities]
        )
        context.turns.append(turn)
        
        # 限制历史长度
        if len(context.turns) > self.max_history:
            context.turns = context.turns[-self.max_history:]
        
        return response
    
    def _generate_response(self, 
                          user_input: str,
                          nlu_result,
                          context: DialogueContext) -> str:
        """生成回复"""
        intent = nlu_result.intent
        
        if intent == IntentType.GREETING:
            return self._generate_greeting(context)
        elif intent == IntentType.QUERY:
            return self._generate_query_response(user_input, nlu_result, context)
        elif intent == IntentType.SEARCH:
            return self._generate_search_response(user_input, nlu_result)
        elif intent == IntentType.CREATE:
            return self._generate_create_response(user_input, nlu_result)
        elif intent == IntentType.COMPARE:
            return self._generate_compare_response(user_input, nlu_result)
        else:
            # 使用QA系统
            answer = self.domain_qa.ask(user_input, context.session_id)
            return answer.answer_text
    
    def _generate_greeting(self, context: DialogueContext) -> str:
        """生成问候回复"""
        greetings = [
            "你好！我是永动知识图谱智能体，有什么可以帮助你的吗？",
            "您好！很高兴为您服务，请问有什么需要了解的？",
            "你好！我可以帮您查询知识、解答问题，请随时提问。"
        ]
        
        # 根据对话历史选择
        if len(context.turns) == 0:
            return greetings[0]
        else:
            return "你好！还有什么我可以帮您的吗？"
    
    def _generate_query_response(self, 
                                user_input: str,
                                nlu_result,
                                context: DialogueContext) -> str:
        """生成查询回复"""
        # 使用QA系统
        answer = self.domain_qa.ask(user_input, context.session_id)
        
        if answer.confidence > 0.3:
            return answer.answer_text
        else:
            # 尝试搜索
            keywords = self.nlu.extract_keywords(user_input)
            if keywords:
                return f"抱歉，我没有找到关于'{' '.join(keywords)}'的详细信息。您可以尝试用其他方式描述您的问题。"
            return "抱歉，我不太理解您的问题。能否提供更多细节？"
    
    def _generate_search_response(self, 
                                 user_input: str,
                                 nlu_result) -> str:
        """生成搜索回复"""
        # 提取搜索关键词
        keywords = [e.text for e in nlu_result.entities]
        if not keywords:
            keywords = self.nlu.extract_keywords(user_input)
        
        if keywords:
            # 这里可以调用搜索功能
            return f"正在搜索与'{' '.join(keywords)}'相关的知识..."
        
        return "请告诉我您想搜索什么内容？"
    
    def _generate_create_response(self, 
                                 user_input: str,
                                 nlu_result) -> str:
        """生成创建回复"""
        entities = nlu_result.entities
        if entities:
            return f"您想要创建关于'{entities[0].text}'的知识吗？请提供更多详细信息。"
        return "您想要创建什么知识？请描述一下。"
    
    def _generate_compare_response(self, 
                                  user_input: str,
                                  nlu_result) -> str:
        """生成比较回复"""
        entities = nlu_result.entities
        if len(entities) >= 2:
            return f"您想要比较'{entities[0].text}'和'{entities[1].text}'吗？让我为您分析一下..."
        elif len(entities) == 1:
            return f"您想要比较'{entities[0].text}'和什么？请提供另一个对象。"
        return "您想要比较什么？请提供两个对象。"
    
    def get_dialogue_history(self, session_id: str = "default") -> List[Dict[str, str]]:
        """获取对话历史"""
        if session_id not in self.contexts:
            return []
        
        return [
            {
                "user": turn.user_input,
                "system": turn.system_response,
                "intent": turn.intent
            }
            for turn in self.contexts[session_id].turns
        ]
    
    def clear_dialogue(self, session_id: str = "default"):
        """清除对话"""
        if session_id in self.contexts:
            self.contexts[session_id].turns = []
            self.contexts[session_id].current_state = DialogueState.START
    
    def get_dialogue_stats(self, session_id: str = "default") -> Dict[str, Any]:
        """获取对话统计"""
        if session_id not in self.contexts:
            return {"total_turns": 0, "duration": 0}
        
        context = self.contexts[session_id]
        
        # 计算对话时长
        if context.turns:
            start_time = datetime.fromisoformat(context.created_at)
            last_time = datetime.fromisoformat(context.turns[-1].timestamp)
            duration = (last_time - start_time).total_seconds()
        else:
            duration = 0
        
        # 统计意图分布
        intent_counts = {}
        for turn in context.turns:
            intent = turn.intent
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        return {
            "total_turns": len(context.turns),
            "duration_seconds": duration,
            "current_state": context.current_state.value,
            "intent_distribution": intent_counts,
            "domain_context": context.domain_context
        }

