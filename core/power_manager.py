"""
基于第一性原理，轻量化永动知识图谱智能体 - 功耗管理模块
存续公理核心实现：实现低功耗休眠模式
"""

import time
from typing import TYPE_CHECKING, Tuple, Dict, Any

if TYPE_CHECKING:
    from core.agent import EternalSelfAgent

from core.constants import LOOP_DELAY


class PowerManager:
    """功耗管理器：实现低功耗休眠模式"""

    def __init__(self, agent: "EternalSelfAgent"):
        self.agent = agent
        self.light_sleep_threshold = 5  # 任务队列少于5个时轻度休眠
        self.deep_sleep_threshold = 0   # 队列为空时深度休眠
        self.light_sleep_delay = LOOP_DELAY * 2
        self.deep_sleep_delay = LOOP_DELAY * 5
        self.last_activity_time = time.time()

    def should_sleep(self) -> Tuple[bool, str]:
        """判断是否应该休眠"""
        queue_size = self.agent.task_queue.size()

        if queue_size == 0:
            return True, "deep_sleep"
        elif queue_size < self.light_sleep_threshold:
            return True, "light_sleep"
        else:
            return False, "active"

    def sleep(self, mode: str):
        """执行休眠"""
        if mode == "deep_sleep":
            time.sleep(self.deep_sleep_delay)
            print(f"[功耗管理] 深度休眠 {self.deep_sleep_delay}秒")
        elif mode == "light_sleep":
            time.sleep(self.light_sleep_delay)
            print(f"[功耗管理] 轻度休眠 {self.light_sleep_delay}秒")

        self.last_activity_time = time.time()

    def record_activity(self):
        """记录活动"""
        self.last_activity_time = time.time()

    def get_power_status(self) -> Dict[str, Any]:
        """获取功耗状态"""
        idle_time = time.time() - self.last_activity_time

        return {
            "current_mode": self.should_sleep()[1],
            "idle_time": idle_time,
            "task_queue_size": self.agent.task_queue.size(),
            "can_deep_sleep": self.agent.task_queue.size() == 0
        }
