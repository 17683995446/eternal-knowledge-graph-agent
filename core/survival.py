"""
基于第一性原理，轻量化永动知识图谱智能体 - 存续模块

实现存续公理：系统永远运行，任何异常不击穿系统。
包含异常隔离、自愈机制、熔断保护等功能。
"""

import time
from typing import Any, Callable
from core.constants import TASK_QUEUE_MAX


def isolated(callable_func: Callable) -> Callable:
    """
    异常隔离装饰器：确保任何异常不穿透，只记录不传播

    符合存续公理：单个组件失败不应导致整个系统崩溃。

    Args:
        callable_func: 需要保护的可调用对象

    Returns:
        包装后的函数
    """
    def wrapper(*args, **kwargs) -> Any:
        try:
            return callable_func(*args, **kwargs)
        except KeyboardInterrupt:
            # 用户主动中断，不视为异常，重新抛出
            raise
        except Exception as e:
            # 记录异常但不向上传播
            print(f"[异常隔离] {type(e).__name__}: {e}")
            return None
    return wrapper


class SurvivalGuard:
    """
    存续守卫：全局异常处理与自愈机制

    符合存续公理：系统永远存在，连续错误触发自愈程序。
    """

    def __init__(self, agent):
        """
        初始化存续守卫

        Args:
            agent: 智能体实例
        """
        self.agent = agent
        self.error_count = 0
        self.max_errors_before_repair = 10
        self.consecutive_errors = 0

    def guard(self, func: Callable) -> Callable:
        """
        函数保护包装：提供异常捕获和计数

        Args:
            func: 需要保护的函数

        Returns:
            包装后的函数
        """
        def wrapper(*args, **kwargs) -> Any:
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self._on_error(e)
                return None
        return wrapper

    def _on_success(self) -> None:
        """成功处理：重置错误计数"""
        self.consecutive_errors = 0

    def _on_error(self, error: Exception) -> None:
        """
        错误处理：累计错误，触发自愈

        Args:
            error: 发生的异常
        """
        self.consecutive_errors += 1
        self.error_count += 1

        print(f"[错误计数] 连续错误: {self.consecutive_errors}/{self.max_errors_before_repair}")

        if self.consecutive_errors >= self.max_errors_before_repair:
            print("[自愈触发] 连续错误达到阈值，启动自愈程序")
            self._self_repair()

    def _self_repair(self) -> None:
        """
        自愈程序：重置状态，尝试恢复

        实现存续公理的核心：系统崩溃后能够自我恢复继续运行。
        """
        print("[自愈] 正在重启系统组件...")
        time.sleep(1)

        # 重新加载知识图谱
        try:
            self.agent.knowledge_graph.load()
            print("[自愈] 知识图谱重新加载完成")
        except Exception as e:
            print(f"[自愈警告] 知识图谱重新加载失败: {e}")

        # 清空错误计数
        self.consecutive_errors = 0

        print("[自愈] 系统已恢复")

    def check_system_health(self) -> bool:
        """
        系统健康检查

        Returns:
            系统是否健康
        """
        # 检查知识图谱文件
        if not self.agent.knowledge_graph.save_path.exists():
            print("[健康检查] 知识图谱文件丢失，初始化新文件")
            self.agent.knowledge_graph.save()

        # 检查任务队列（如果有队列实例）
        if hasattr(self.agent, 'task_queue'):
            queue_size = len(self.agent.task_queue)
            if queue_size > TASK_QUEUE_MAX * 0.9:
                print(f"[健康检查] 任务队列接近上限: {queue_size}/{TASK_QUEUE_MAX}")
                self._trigger_queue_protection()

        return True

    def _trigger_queue_protection(self) -> None:
        """
        任务队列熔断保护：在队列溢出前进行清理

        保留高优先级任务，清理低价值任务。
        """
        # 确保我们有任务队列
        if not hasattr(self.agent, 'task_queue'):
            return

        print("[熔断保护] 正在清理任务队列...")

        # 清空已完成任务记录，释放空间
        if hasattr(self.agent.task_queue, 'clear_completed'):
            self.agent.task_queue.clear_completed()

        # 对于队列已经由 deque 的最大长度已经处理了溢出
        print(f"[熔断保护] 已清空已完成任务记录")
