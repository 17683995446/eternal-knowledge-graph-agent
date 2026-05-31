"""
基于第一性原理，轻量化永动知识图谱智能体 - 任务队列系统

实现有限长度任务队列，满足资源守恒约束，
支持优先级、批量操作和任务去重。
"""

from collections import deque
from typing import Any
from dataclasses import dataclass, field
import time

from core.constants import TASK_QUEUE_MAX


@dataclass
class Task:
    """任务元数据"""
    name: str
    created_at: float = field(default_factory=time.time)
    priority: int = 0  # 优先级：0普通, 1重要, 2紧急
    metadata: dict = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3


class TaskQueue:
    """有限长度任务队列（资源守恒约束）"""

    def __init__(self, max_size: int = TASK_QUEUE_MAX):
        self.max_size = max_size
        self.queue = deque(maxlen=max_size)
        self.completed = set()  # 已完成任务名称集合
        self.priority_queue = []  # 优先任务列表
        self.tasks = {}  # task_name -> Task

    def add(self, task: str, priority: bool = False) -> bool:
        """添加任务到队列"""
        if task in self.completed:
            return False

        # 检查队列是否已满
        if self.size() >= self.max_size:
            print(f"[队列满载] 拒绝任务: {task}")
            return False

        # 检查任务是否已在队列中
        if self._is_pending(task):
            return False

        # 创建任务元数据
        task_obj = Task(
            name=task,
            priority=2 if priority else 0
        )
        self.tasks[task] = task_obj

        if priority:
            self.priority_queue.append(task)
        else:
            self.queue.append(task)

        return True

    def add_unique(self, task: str) -> bool:
        """仅添加不存在的任务（去重）"""
        if task in self.completed or self._is_pending(task):
            return False
        return self.add(task)

    def add_batch(self, tasks: list[str]) -> int:
        """批量添加任务"""
        added = 0
        for task in tasks:
            if self.add(task):
                added += 1
        return added

    def add_batch_unique(self, tasks: list[str]) -> int:
        """批量添加不重复任务"""
        added = 0
        for task in tasks:
            if self.add_unique(task):
                added += 1
        return added

    def add_with_metadata(self, task_obj: Task) -> bool:
        """添加带元数据的任务"""
        task_name = task_obj.name

        if task_name in self.completed:
            return False

        if self.size() >= self.max_size:
            return False

        if self._is_pending(task_name):
            return False

        self.tasks[task_name] = task_obj

        if task_obj.priority > 0:
            self.priority_queue.append(task_name)
        else:
            self.queue.append(task_name)

        return True

    def pop(self) -> str | None:
        """弹出下一个任务（优先队列优先）"""
        if self.priority_queue:
            task = self.priority_queue.pop(0)
            return task
        if self.queue:
            task = self.queue.popleft()
            return task
        return None

    def peek(self) -> str | None:
        """查看下一个任务（不弹出）"""
        if self.priority_queue:
            return self.priority_queue[0]
        if self.queue:
            return self.queue[0]
        return None

    def mark_completed(self, task: str):
        """标记任务为已完成"""
        self.completed.add(task)
        if task in self.tasks:
            del self.tasks[task]

    def is_empty(self) -> bool:
        """检查队列是否为空"""
        return len(self.queue) == 0 and len(self.priority_queue) == 0

    def size(self) -> int:
        """获取队列大小"""
        return len(self.queue) + len(self.priority_queue)

    def clear(self):
        """清空队列"""
        self.queue.clear()
        self.priority_queue.clear()

    def clear_completed(self):
        """清空已完成任务记录（释放内存）"""
        self.completed.clear()

    def get_task_info(self, task_name: str) -> Task | None:
        """获取任务信息"""
        return self.tasks.get(task_name)

    def increment_retry(self, task_name: str) -> bool:
        """增加重试次数，返回是否可以继续重试"""
        task = self.tasks.get(task_name)
        if not task:
            return False

        task.retry_count += 1
        return task.retry_count <= task.max_retries

    def _is_pending(self, task: str) -> bool:
        """检查任务是否已在队列中"""
        return task in self.queue or task in self.priority_queue

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        return f"TaskQueue(pending={self.size()}, completed={len(self.completed)})"


# 全局唯一任务队列实例（可选）
GLOBAL_TASK_QUEUE = TaskQueue(max_size=TASK_QUEUE_MAX)
