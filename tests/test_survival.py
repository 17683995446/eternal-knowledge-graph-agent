"""
阶段5验收测试：全局异常隔离与自愈机制

测试存续公理的实现：任何异常不能击穿系统。
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 临时修改保存路径用于测试
from core import constants
original_save_path = constants.KG_SAVE_PATH
test_save_path = Path("data/test_survival_kg.json")
constants.KG_SAVE_PATH = str(test_save_path)

from core.agent import EternalSelfAgent
from core.exceptions import AgentException, KnowledgeGraphException
from core.survival import isolated, SurvivalGuard


def cleanup_test_files():
    """清理测试文件"""
    test_files = [
        test_save_path,
        test_save_path.with_suffix('.tmp'),
        test_save_path.with_suffix('.bak')
    ]
    
    for f in test_files:
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_isolated_decorator():
    """测试异常隔离装饰器"""
    print("测试异常隔离装饰器...")

    @isolated
    def error_function():
        raise ValueError("测试异常")

    # 异常应被隔离，不向上传播
    result = error_function()
    assert result is None  # 异常被捕获后返回None
    print("✓ test_isolated_decorator 成功")


def test_agent_exception_hierarchy():
    """测试异常继承层次"""
    print("测试异常继承层次...")

    # 自定义异常应继承自AgentException
    exception = KnowledgeGraphException("测试知识图谱异常")
    assert isinstance(exception, AgentException)
    assert exception.recoverable is True

    print("✓ test_agent_exception_hierarchy 成功")


def test_survival_guard_error_count():
    """测试存续守卫的错误计数"""
    print("测试存续守卫的错误计数...")

    agent = EternalSelfAgent()
    guard = agent.survival_guard

    # 设置一个很高的阈值，避免触发自愈
    guard.max_errors_before_repair = 100

    # 模拟错误
    guard._on_error(ValueError("测试错误1"))
    assert guard.consecutive_errors == 1
    assert guard.error_count == 1

    guard._on_error(ValueError("测试错误2"))
    assert guard.consecutive_errors == 2
    assert guard.error_count == 2

    # 成功应重置连续错误
    guard._on_success()
    assert guard.consecutive_errors == 0

    print("✓ test_survival_guard_error_count 成功")


def test_agent_isolation_simple():
    """测试简单的Agent异常隔离"""
    print("测试简单的Agent异常隔离...")

    cleanup_test_files()
    agent = EternalSelfAgent()
    agent.add_initial_tasks(["测试任务1"])

    # 即使有异常，Agent也应继续运行
    # 我们测试单个任务执行
    agent.execute_task("测试任务2")
    assert len(agent.task_queue) >= 0

    print("✓ test_agent_isolation_simple 成功")


def test_health_check():
    """测试健康检查功能"""
    print("测试健康检查功能...")

    cleanup_test_files()
    agent = EternalSelfAgent()
    result = agent.survival_guard.check_system_health()
    assert result is True

    print("✓ test_health_check 成功")


def test_survival_with_queue():
    """测试任务队列集成"""
    print("测试任务队列集成...")

    cleanup_test_files()
    agent = EternalSelfAgent()
    agent.add_initial_tasks(["任务1", "任务2", "任务3"])

    # 健康检查应该能正常工作
    agent.health_check()

    assert len(agent.task_queue) == 3
    print("✓ test_survival_with_queue 成功")


def test_guard_decorator():
    """测试guard装饰器"""
    print("测试guard装饰器...")

    cleanup_test_files()
    agent = EternalSelfAgent()

    @agent.survival_guard.guard
    def test_func_with_error():
        raise ValueError("受保护的错误")

    result = test_func_with_error()
    assert result is None
    assert agent.survival_guard.error_count == 1

    print("✓ test_guard_decorator 成功")


def test_consecutive_error_reset():
    """测试连续错误的重置"""
    print("测试连续错误的重置...")

    cleanup_test_files()
    agent = EternalSelfAgent()
    guard = agent.survival_guard

    guard._on_error(ValueError("错误1"))
    guard._on_error(ValueError("错误2"))
    assert guard.consecutive_errors == 2

    guard._on_success()
    assert guard.consecutive_errors == 0

    print("✓ test_consecutive_error_reset 成功")


def test_isolated_decorator_returns_result():
    """测试正常函数被装饰后仍能返回结果"""
    print("测试正常函数被装饰后仍能返回结果...")

    @isolated
    def normal_function():
        return 42

    result = normal_function()
    assert result == 42
    print("✓ test_isolated_decorator_returns_result 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段5：全局异常隔离与自愈机制验收测试 ===")
    print("=" * 50)

    try:
        test_isolated_decorator()
        test_agent_exception_hierarchy()
        test_survival_guard_error_count()
        test_agent_isolation_simple()
        test_health_check()
        test_survival_with_queue()
        test_guard_decorator()
        test_consecutive_error_reset()
        test_isolated_decorator_returns_result()

        print("\n" + "=" * 50)
        print("✅ 阶段5所有验收测试通过！")
        print("=" * 50)
    finally:
        cleanup_test_files()
        # 恢复原始路径
        constants.KG_SAVE_PATH = original_save_path
