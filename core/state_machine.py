"""
基于第一性原理，轻量化永动知识图谱智能体 - 状态机
存续公理核心实现：管理系统状态转换
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional
import time


class SystemState(Enum):
    """系统状态枚举"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    IDLE = "idle"
    EVOLVING = "evolving"
    ERROR = "error"
    REPAIRING = "repairing"
    SHUTDOWN = "shutdown"


@dataclass
class StateTransition:
    """状态转换记录"""
    from_state: SystemState
    to_state: SystemState
    reason: str
    timestamp: float


class StateMachine:
    """状态机：管理系统状态转换"""

    def __init__(self):
        self.current_state = SystemState.INITIALIZING
        self.previous_state = None
        self.transitions = []
        self.state_history = [self.current_state]

    def transition_to(self, new_state: SystemState, reason: str = ""):
        """状态转换"""
        if self.current_state == new_state:
            return

        transition = StateTransition(
            from_state=self.current_state,
            to_state=new_state,
            reason=reason,
            timestamp=time.time()
        )

        self.transitions.append(transition)
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_history.append(new_state)

        print(f"[状态转换] {transition.from_state.value} -> {transition.to_state.value} ({reason})")

    def get_state(self) -> SystemState:
        """获取当前状态"""
        return self.current_state

    def is_state(self, state: SystemState) -> bool:
        """检查是否处于指定状态"""
        return self.current_state == state

    def can_transition_to(self, target_state: SystemState) -> bool:
        """检查是否可以转换到目标状态"""
        valid_transitions = {
            SystemState.INITIALIZING: [SystemState.RUNNING, SystemState.SHUTDOWN],
            SystemState.RUNNING: [SystemState.IDLE, SystemState.EVOLVING, SystemState.ERROR, SystemState.SHUTDOWN],
            SystemState.IDLE: [SystemState.RUNNING, SystemState.EVOLVING, SystemState.SHUTDOWN],
            SystemState.EVOLVING: [SystemState.RUNNING, SystemState.IDLE, SystemState.ERROR, SystemState.SHUTDOWN],
            SystemState.ERROR: [SystemState.REPAIRING, SystemState.SHUTDOWN],
            SystemState.REPAIRING: [SystemState.RUNNING, SystemState.IDLE, SystemState.ERROR, SystemState.SHUTDOWN],
            SystemState.SHUTDOWN: []
        }

        return target_state in valid_transitions.get(self.current_state, [])

    def get_state_summary(self) -> dict:
        """获取状态摘要"""
        return {
            "current_state": self.current_state.value,
            "previous_state": self.previous_state.value if self.previous_state else None,
            "transition_count": len(self.transitions),
            "state_history": [s.value for s in self.state_history[-10:]]
        }
