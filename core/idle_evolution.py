"""
基于第一性原理，轻量化永动知识图谱智能体 - 空闲进化模块
自驱公理核心实现：系统在无任务时执行自我进化
"""

import time
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from core.agent import EternalSelfAgent
    from core.evolution import EvolutionLayer


class IdleEvolver:
    """空闲进化器：系统在无任务时执行自我进化"""

    def __init__(self, agent: "EternalSelfAgent"):
        self.agent = agent
        self.evolution_layer: "EvolutionLayer" = agent.evolution_layer
        self.idle_start_time = None
        self.max_idle_evolve_iterations = 5
        self.min_tasks_threshold = 3

    def check_and_evolve(self) -> Dict[str, Any]:
        """检查是否需要空闲进化"""
        queue_size = self.agent.task_queue.size()

        if queue_size < self.min_tasks_threshold:
            if self.idle_start_time is None:
                self.idle_start_time = time.time()

            return self._do_idle_evolve()
        else:
            self.idle_start_time = None
            return {"action": "no_idle_needed", "queue_size": queue_size}

    def _do_idle_evolve(self) -> Dict[str, Any]:
        """执行空闲进化"""
        idle_duration = time.time() - self.idle_start_time if self.idle_start_time else 0

        stats = {
            "idle_duration": idle_duration,
            "queue_before": self.agent.task_queue.size(),
            "tasks_generated": 0
        }

        # 根据空闲时间调整进化强度
        if idle_duration < 10:
            # 短期空闲，生成少量任务
            iterations = 1
        elif idle_duration < 60:
            # 中期空闲，标准进化
            iterations = 3
        else:
            # 长期空闲，强化进化
            iterations = self.max_idle_evolve_iterations

        # 执行进化
        total_generated = 0
        for _ in range(iterations):
            result = self.evolution_layer.evolve()
            total_generated += result["tasks_generated"]

        stats["tasks_generated"] = total_generated
        stats["queue_after"] = self.agent.task_queue.size()
        stats["iterations"] = iterations

        return stats

    def get_idle_status(self) -> Dict[str, Any]:
        """获取空闲状态"""
        return {
            "is_idle": self.agent.task_queue.size() < self.min_tasks_threshold,
            "idle_start_time": self.idle_start_time,
            "idle_duration": time.time() - self.idle_start_time if self.idle_start_time else 0,
            "pending_tasks": self.agent.task_queue.size()
        }
