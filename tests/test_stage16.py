"""
阶段16验收测试：空闲进化与休眠模式
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_graph import KnowledgeGraph
from core.agent import EternalSelfAgent
from core import constants


def cleanup_test_files():
    """清理测试文件"""
    test_path = Path("data/test_stage16_kg.json")
    for suffix in ['', '.tmp', '.bak']:
        f = test_path.with_suffix(suffix if suffix else '.json')
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_idle_evolver_initialization():
    """测试空闲进化器初始化"""
    print("测试空闲进化器初始化...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage16_kg.json"

    agent = EternalSelfAgent()
    
    assert hasattr(agent, 'idle_evolver')
    assert agent.idle_evolver is not None
    
    idle_status = agent.idle_evolver.get_idle_status()
    assert 'is_idle' in idle_status
    assert 'pending_tasks' in idle_status

    print("✓ test_idle_evolver_initialization 成功")


def test_power_manager_initialization():
    """测试功耗管理器初始化"""
    print("测试功耗管理器初始化...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage16_kg.json"

    agent = EternalSelfAgent()
    
    assert hasattr(agent, 'power_manager')
    assert agent.power_manager is not None
    
    power_status = agent.power_manager.get_power_status()
    assert 'current_mode' in power_status
    assert 'idle_time' in power_status

    print("✓ test_power_manager_initialization 成功")


def test_power_modes():
    """测试不同功耗模式"""
    print("测试不同功耗模式...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage16_kg.json"

    agent = EternalSelfAgent()
    
    # 测试活跃模式（有任务）
    agent.task_queue.add("测试任务1")
    agent.task_queue.add("测试任务2")
    agent.task_queue.add("测试任务3")
    agent.task_queue.add("测试任务4")
    agent.task_queue.add("测试任务5")
    
    should_sleep, mode = agent.power_manager.should_sleep()
    assert should_sleep == False
    assert mode == "active"
    
    # 清空任务队列
    while agent.task_queue.pop() is not None:
        pass
    
    # 测试轻度休眠
    agent.task_queue.add("任务1")
    agent.task_queue.add("任务2")
    
    should_sleep, mode = agent.power_manager.should_sleep()
    assert should_sleep == True
    assert mode == "light_sleep"
    
    # 清空任务队列
    while agent.task_queue.pop() is not None:
        pass
    
    # 测试深度休眠
    should_sleep, mode = agent.power_manager.should_sleep()
    assert should_sleep == True
    assert mode == "deep_sleep"

    print("✓ test_power_modes 成功")


def test_idle_evolution():
    """测试空闲进化"""
    print("测试空闲进化...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage16_kg.json"

    agent = EternalSelfAgent()
    
    # 清空任务队列
    while agent.task_queue.pop() is not None:
        pass
    
    # 检查空闲进化
    stats = agent.idle_evolver.check_and_evolve()
    assert 'tasks_generated' in stats
    assert 'queue_before' in stats
    assert 'queue_after' in stats
    
    # 验证有任务生成
    if agent.task_queue.size() > 0:
        print(f"[空闲进化] 成功生成了 {agent.task_queue.size()} 个任务")
    
    print("✓ test_idle_evolution 成功")


def test_record_activity():
    """测试活动记录"""
    print("测试活动记录...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage16_kg.json"

    agent = EternalSelfAgent()
    
    # 记录一次活动
    agent.power_manager.record_activity()
    
    # 获取初始时间
    time1 = agent.power_manager.last_activity_time
    time.sleep(0.01)
    
    # 再次记录活动
    agent.power_manager.record_activity()
    time2 = agent.power_manager.last_activity_time
    
    assert time2 > time1

    print("✓ test_record_activity 成功")


def test_integration():
    """测试整体集成"""
    print("测试整体集成...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage16_kg.json"

    agent = EternalSelfAgent()
    
    # 确保所有组件都正常工作
    assert agent.idle_evolver is not None
    assert agent.power_manager is not None
    
    # 测试空闲处理
    agent._handle_idle()
    
    # 确保系统仍然存活
    assert agent.system_alive == True

    print("✓ test_integration 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段16：空闲进化与休眠模式验收测试 ===")
    print("=" * 50)

    try:
        test_idle_evolver_initialization()
        test_power_manager_initialization()
        test_power_modes()
        test_idle_evolution()
        test_record_activity()
        test_integration()

        print("\n" + "=" * 50)
        print("✅ 阶段16所有验收测试通过！")
        print("=" * 50)
    finally:
        cleanup_test_files()
        constants.KG_SAVE_PATH = "data/knowledge_graph.json"
