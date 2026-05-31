"""
阶段6验收测试：任务队列系统实现
"""

import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.task_queue import TaskQueue, Task
from core.agent import EternalSelfAgent
from core.constants import TASK_QUEUE_MAX


def test_basic_queue_operations():
    """测试基础队列操作"""
    print("测试基础队列操作...")
    queue = TaskQueue(max_size=10)

    # 添加任务
    assert queue.add("任务1")
    assert queue.add("任务2")
    assert queue.add("任务3")

    # 检查队列大小
    assert queue.size() == 3

    # 弹出任务
    task1 = queue.pop()
    assert task1 == "任务1"

    # 检查队列大小
    assert queue.size() == 2

    print("✓ test_basic_queue_operations 成功")


def test_queue_limit():
    """测试队列大小限制"""
    print("测试队列大小限制...")
    queue = TaskQueue(max_size=5)

    # 添加超过限制的任务
    for i in range(10):
        queue.add(f"任务{i}")

    # 队列大小不超过限制
    assert queue.size() <= 5

    print("✓ test_queue_limit 成功")


def test_duplicate_prevention():
    """测试任务去重"""
    print("测试任务去重...")
    queue = TaskQueue(max_size=10)

    # 尝试添加重复任务
    queue.add("重复任务")
    queue.add("重复任务")  # 重复添加
    queue.add("重复任务")

    assert queue.size() == 1

    print("✓ test_duplicate_prevention 成功")


def test_completed_tasks_not_repeated():
    """测试已完成任务不重复执行"""
    print("测试已完成任务不重复执行...")
    queue = TaskQueue(max_size=10)

    queue.add("任务A")
    task = queue.pop()
    assert task == "任务A"

    queue.mark_completed(task)

    # 尝试重新添加
    assert not queue.add("任务A")

    print("✓ test_completed_tasks_not_repeated 成功")


def test_priority_queue():
    """测试优先队列"""
    print("测试优先队列...")
    queue = TaskQueue(max_size=10)

    # 添加普通任务
    queue.add("普通任务1")
    queue.add("普通任务2")

    # 添加优先任务
    queue.add("紧急任务", priority=True)
    queue.add("普通任务3")

    # 优先任务应该先出队
    first = queue.pop()
    assert first == "紧急任务"

    print("✓ test_priority_queue 成功")


def test_batch_add():
    """测试批量添加任务"""
    print("测试批量添加任务...")
    queue = TaskQueue(max_size=10)

    tasks = ["批量任务1", "批量任务2", "批量任务3"]
    added = queue.add_batch(tasks)

    assert added == 3
    assert queue.size() == 3

    print("✓ test_batch_add 成功")


def test_batch_unique_add():
    """测试批量添加唯一任务"""
    print("测试批量添加唯一任务...")
    queue = TaskQueue(max_size=10)

    # 包含重复的任务
    tasks = ["任务X", "任务X", "任务Y", "任务Y"]
    added = queue.add_batch_unique(tasks)

    assert added == 2  # 只添加了2个唯一任务
    assert queue.size() == 2

    print("✓ test_batch_unique_add 成功")


def test_task_metadata():
    """测试任务元数据"""
    print("测试任务元数据...")
    queue = TaskQueue(max_size=10)

    task_obj = Task(
        name="元数据任务",
        priority=1,
        metadata={"type": "test", "info": "important"}
    )

    assert queue.add_with_metadata(task_obj)

    info = queue.get_task_info("元数据任务")
    assert info is not None
    assert info.priority == 1
    assert info.metadata["type"] == "test"

    print("✓ test_task_metadata 成功")


def test_task_retry():
    """测试任务重试机制"""
    print("测试任务重试机制...")
    queue = TaskQueue(max_size=10)

    queue.add("可重试任务")
    queue.pop()  # 取出任务，假装执行失败

    # 重新添加任务
    # 假设任务还没有标记完成，所以可以重新添加
    queue.add("可重试任务")
    task_info = queue.get_task_info("可重试任务")
    assert task_info is not None

    # 增加重试次数
    can_retry = queue.increment_retry("可重试任务")
    assert can_retry is True

    print("✓ test_task_retry 成功")


def test_agent_with_task_queue():
    """测试Agent集成任务队列"""
    print("测试Agent集成任务队列...")

    # 创建Agent并添加初始任务
    agent = EternalSelfAgent()
    agent.add_initial_tasks(["初始任务1", "初始任务2"])

    # 检查任务队列有初始任务
    assert agent.task_queue.size() == 2

    # 执行任务
    task1 = agent.get_current_task()
    assert task1 == "初始任务1"

    new_tasks = agent.execute_task(task1)
    agent.task_queue.add_batch_unique(new_tasks)
    agent.task_queue.mark_completed(task1)

    assert "初始任务1" in agent.task_queue.completed

    print("✓ test_agent_with_task_queue 成功")


def test_queue_clear():
    """测试队列清空"""
    print("测试队列清空...")
    queue = TaskQueue(max_size=10)

    queue.add_batch(["任务1", "任务2", "任务3"])
    assert queue.size() == 3

    queue.clear()
    assert queue.is_empty() is True

    print("✓ test_queue_clear 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段6：任务队列系统验收测试 ===")
    print("=" * 50)

    try:
        test_basic_queue_operations()
        test_queue_limit()
        test_duplicate_prevention()
        test_completed_tasks_not_repeated()
        test_priority_queue()
        test_batch_add()
        test_batch_unique_add()
        test_task_metadata()
        test_task_retry()
        test_agent_with_task_queue()
        test_queue_clear()

        print("\n" + "=" * 50)
        print("✅ 阶段6所有验收测试通过！")
        print("=" * 50)
    finally:
        # 清理测试
        pass
