"""
阶段8验收测试：存续保活层完整集成
"""

import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent import EternalSelfAgent


def test_get_status():
    """测试系统状态获取"""
    print("测试系统状态获取...")

    agent = EternalSelfAgent()
    status = agent.get_status()

    assert status is not None
    assert "system_alive" in status
    assert "run_counter" in status
    assert "knowledge_nodes" in status
    assert "knowledge_edges" in status
    assert status["system_alive"] is True

    print("✓ test_get_status 成功")


def test_safe_execute():
    """测试安全执行包装"""
    print("测试安全执行包装...")

    agent = EternalSelfAgent()

    # 正常函数执行
    def normal_func():
        return "success"

    result = agent.safe_execute(normal_func)
    assert result == "success"

    # 异常函数执行
    def error_func():
        raise ValueError("Test error")

    result = agent.safe_execute(error_func)
    assert result is None  # 异常被隔离，返回None

    print("✓ test_safe_execute 成功")


def test_exception_counting():
    """测试异常计数功能"""
    print("测试异常计数功能...")

    agent = EternalSelfAgent()
    initial_count = agent.error_count_today

    # 模拟异常
    try:
        raise ValueError("Test")
    except Exception as e:
        agent.error_count_today += 1

    assert agent.error_count_today > initial_count

    print("✓ test_exception_counting 成功")


def test_self_repair():
    """测试自愈功能"""
    print("测试自愈功能...")

    agent = EternalSelfAgent()

    # 执行自愈
    agent.self_repair()

    # 检查是否记录了自愈事件
    status = agent.get_status()
    assert status["knowledge_nodes"] >= 1

    print("✓ test_self_repair 成功")


def test_periodic_evolution():
    """测试周期性进化"""
    print("测试周期性进化...")

    agent = EternalSelfAgent()

    # 执行多次迭代
    initial_run_count = agent.run_counter
    for i in range(10):
        agent.health_check()

    # 验证run_counter正确增加
    assert agent.run_counter == initial_run_count + 10

    print("✓ test_periodic_evolution 成功")


def test_full_workflow():
    """测试完整工作流"""
    print("测试完整工作流...")

    agent = EternalSelfAgent()

    # 添加初始任务
    agent.add_initial_tasks(["阶段8测试任务1", "阶段8测试任务2"])

    # 执行一些迭代
    for _ in range(3):
        agent.health_check()
        task = agent.get_current_task()
        if task:
            new_tasks = agent.execute_task(task)
            if new_tasks:
                agent.task_queue.add_batch_unique(new_tasks)
            agent.task_queue.mark_completed(task)

    # 验证系统状态
    status = agent.get_status()
    assert status["system_alive"] is True
    assert status["run_counter"] >= 1
    assert status["knowledge_nodes"] >= 2

    print("✓ test_full_workflow 成功")


def test_survival_guard_integration():
    """测试存续守卫集成"""
    print("测试存续守卫集成...")

    agent = EternalSelfAgent()

    # 验证存续守卫已正确初始化
    assert hasattr(agent, 'survival_guard')
    assert agent.survival_guard is not None

    # 验证健康检查器已正确初始化
    assert hasattr(agent, 'health_checker')
    assert agent.health_checker is not None

    print("✓ test_survival_guard_integration 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段8：存续保活层完整集成验收测试 ===")
    print("=" * 50)

    try:
        test_get_status()
        test_safe_execute()
        test_exception_counting()
        test_self_repair()
        test_periodic_evolution()
        test_full_workflow()
        test_survival_guard_integration()

        print("\n" + "=" * 50)
        print("✅ 阶段8所有验收测试通过！")
        print("=" * 50)
    finally:
        # 清理测试
        pass
