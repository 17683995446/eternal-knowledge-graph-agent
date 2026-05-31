"""
阶段17验收测试：系统初始化与启动流程
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.boot import BootStrapper
from core.agent import EternalSelfAgent
from core import constants


def cleanup_test_files():
    """清理测试文件"""
    test_path = Path("data/test_stage17_kg.json")
    for suffix in ['', '.tmp', '.bak']:
        f = test_path.with_suffix(suffix if suffix else '.json')
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_bootstrapper_initialization():
    """测试启动引导器初始化"""
    print("测试启动引导器初始化...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage17_kg.json"

    bootstrapper = BootStrapper()
    
    assert bootstrapper is not None
    assert hasattr(bootstrapper, 'errors')
    assert len(bootstrapper.errors) == 0

    print("✓ test_bootstrapper_initialization 成功")


def test_preflight_checks():
    """测试启动前检查"""
    print("测试启动前检查...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage17_kg.json"

    bootstrapper = BootStrapper()
    result = bootstrapper.run_preflight_checks()
    
    assert result == True, "启动前检查应该通过"
    assert len(bootstrapper.errors) == 0

    print("✓ test_preflight_checks 成功")


def test_initial_tasks_injection():
    """测试初始任务注入"""
    print("测试初始任务注入...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage17_kg.json"

    bootstrapper = BootStrapper()
    agent = EternalSelfAgent()
    
    # 清空任务队列
    while agent.task_queue.pop() is not None:
        pass
    
    # 注入初始任务
    bootstrapper._inject_initial_tasks(agent)
    
    # 检查任务是否被正确注入
    assert agent.task_queue.size() > 0
    print(f"[初始任务注入] 成功注入 {agent.task_queue.size()} 个任务")

    print("✓ test_initial_tasks_injection 成功")


def test_initialize_system():
    """测试完整系统初始化"""
    print("测试完整系统初始化...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage17_kg.json"

    bootstrapper = BootStrapper()
    
    # 注意：我们不实际运行完整初始化以避免启动循环
    # 而是测试各个组件
    agent = bootstrapper.initialize_system()
    
    assert agent is not None
    assert agent.system_alive == True
    assert agent.task_queue.size() > 0
    assert hasattr(agent, 'knowledge_graph')
    assert hasattr(agent, 'evolution_layer')

    print("✓ test_initialize_system 成功")


def test_data_directory_creation():
    """测试数据目录创建"""
    print("测试数据目录创建...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage17_kg.json"

    # 确保目录不存在
    data_dir = Path(constants.KG_SAVE_PATH).parent
    if data_dir.exists():
        try:
            for f in data_dir.glob("*"):
                f.unlink()
            data_dir.rmdir()
        except:
            pass

    bootstrapper = BootStrapper()
    bootstrapper._check_data_directory()
    
    # 检查目录是否创建成功
    assert data_dir.exists() == True

    print("✓ test_data_directory_creation 成功")


def test_python_version_check():
    """测试Python版本检查（集成测试）"""
    print("测试Python版本检查...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage17_kg.json"

    bootstrapper = BootStrapper()
    bootstrapper._check_python_version()
    
    # 我们假设测试环境Python版本足够新
    assert len(bootstrapper.errors) == 0 or "Python版本过低" not in str(bootstrapper.errors)

    print("✓ test_python_version_check 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段17：系统初始化与启动流程验收测试 ===")
    print("=" * 50)

    try:
        test_bootstrapper_initialization()
        test_preflight_checks()
        test_initial_tasks_injection()
        test_initialize_system()
        test_data_directory_creation()
        test_python_version_check()

        print("\n" + "=" * 50)
        print("✅ 阶段17所有验收测试通过！")
        print("=" * 50)
    finally:
        cleanup_test_files()
        constants.KG_SAVE_PATH = "data/knowledge_graph.json"
