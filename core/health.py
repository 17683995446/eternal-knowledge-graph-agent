"""
基于第一性原理，轻量化永动知识图谱智能体 - 健康检查与资源监控
实现存续公理：周期性系统健康检查和资源监控
"""

import time
import gc
from dataclasses import dataclass


@dataclass
class HealthStatus:
    """健康状态快照"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    task_queue_size: int
    knowledge_nodes: int
    knowledge_edges: int
    run_counter: int
    errors_today: int


class HealthChecker:
    """健康检查器：周期性监控系统状态（轻量版，无外部依赖）"""

    def __init__(self, agent):
        self.agent = agent
        self.start_time = time.time()
        self.last_check_time = self.start_time
        self.check_interval = 10  # 检查间隔（秒）
        self.status_history = []
        self.max_history = 100

    def check(self) -> HealthStatus:
        """执行健康检查"""
        current_time = time.time()

        status = HealthStatus(
            timestamp=current_time,
            cpu_percent=self._get_cpu_usage(),
            memory_percent=self._get_memory_usage(),
            memory_mb=self._get_memory_mb(),
            task_queue_size=self.agent.task_queue.size(),
            knowledge_nodes=len(self.agent.knowledge_graph.nodes),
            knowledge_edges=len(self.agent.knowledge_graph.edges),
            run_counter=self.agent.run_counter,
            errors_today=getattr(self.agent, 'error_count_today', 0)
        )

        self.status_history.append(status)
        if len(self.status_history) > self.max_history:
            self.status_history.pop(0)

        self.last_check_time = current_time
        return status

    def _get_cpu_usage(self) -> float:
        """获取CPU使用率（简化版，无外部依赖）"""
        # 因为不使用psutil，返回一个模拟值
        return 0.0

    def _get_memory_usage(self) -> float:
        """获取内存使用率（简化版，无外部依赖）"""
        # 简化版实现，不依赖外部库
        return 0.0

    def _get_memory_mb(self) -> float:
        """获取内存使用量（MB，简化版）"""
        # 使用gc估算内存使用
        gc.collect()
        # 简单估算
        import sys
        total_size = 0
        # 计算一些关键对象的大小
        for obj in [self.agent.knowledge_graph, self.agent.task_queue]:
            total_size += sys.getsizeof(obj)
        return total_size / (1024 * 1024)

    def should_check(self) -> bool:
        """判断是否应该执行检查"""
        return (time.time() - self.last_check_time) >= self.check_interval

    def get_summary(self) -> str:
        """获取健康摘要"""
        if not self.status_history:
            return "系统尚未执行健康检查"

        latest = self.status_history[-1]
        uptime = time.time() - self.start_time
        uptime_hours = uptime / 3600

        return (
            f"[健康摘要] 运行时间: {uptime_hours:.1f}h | "
            f"循环次数: {latest.run_counter} | "
            f"任务队列: {latest.task_queue_size} | "
            f"知识图谱: {latest.knowledge_nodes}节点/{latest.knowledge_edges}边"
        )

    def check_anomalies(self) -> list[str]:
        """检测异常"""
        anomalies = []

        if not self.status_history:
            return anomalies

        latest = self.status_history[-1]

        # 任务队列异常检测
        from core.constants import TASK_QUEUE_MAX
        if latest.task_queue_size >= TASK_QUEUE_MAX:
            anomalies.append("任务队列已满载")

        # 知识图谱异常检测
        if latest.knowledge_nodes == 0 and latest.run_counter > 10:
            anomalies.append("知识图谱为空，可能存在数据丢失")

        return anomalies

    def auto_cleanup(self):
        """自动资源清理"""
        # 清理过旧的历史状态
        if len(self.status_history) > self.max_history:
            self.status_history = self.status_history[-self.max_history:]

        # 清理已完成且过旧的任务记录
        if hasattr(self.agent.task_queue, 'completed'):
            max_completed_history = 500
            if len(self.agent.task_queue.completed) > max_completed_history:
                # 只保留最近的记录
                completed_list = list(self.agent.task_queue.completed)
                self.agent.task_queue.completed = set(completed_list[-max_completed_history:])
                print(f"[自动清理] 已完成任务记录清理至 {max_completed_history} 条")

        # 强制垃圾回收
        gc.collect()
        print("[自动清理] 资源清理完成")
