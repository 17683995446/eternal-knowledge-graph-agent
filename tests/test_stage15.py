"""
阶段15验收测试：任务执行与知识沉淀闭环
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_graph import KnowledgeGraph
from core.agent import EternalSelfAgent
from core import constants


def cleanup_test_files():
    """清理测试文件"""
    test_path = Path("data/test_stage15_kg.json")
    for suffix in ['', '.tmp', '.bak']:
        f = test_path.with_suffix(suffix if suffix else '.json')
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_execute_task():
    """测试任务执行"""
    print("测试任务执行...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage15_kg.json"

    agent = EternalSelfAgent()
    new_tasks = agent.execute_task("测试任务1")

    assert isinstance(new_tasks, list)
    assert len(new_tasks) >= 1

    print("✓ test_execute_task 成功")


def test_knowledge_precipitation():
    """测试知识沉淀"""
    print("测试知识沉淀...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage15_kg.json"

    agent = EternalSelfAgent()
    agent.execute_task("沉淀测试任务")

    has_task_node = any(
        "沉淀测试任务" in node.name
        for node in agent.knowledge_graph.nodes.values()
    )
    assert has_task_node is True

    print("✓ test_knowledge_precipitation 成功")


def test_derived_tasks():
    """测试衍生任务"""
    print("测试衍生任务...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage15_kg.json"

    agent = EternalSelfAgent()
    agent.knowledge_graph.add_edge("A", "B", "测试关联", 0.9)
    derived = agent.knowledge_graph_derive_new_tasks("A")

    assert isinstance(derived, list)

    print("✓ test_derived_tasks 成功")


def test_task_strategies():
    """测试任务执行策略"""
    print("测试任务执行策略...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage15_kg.json"

    agent = EternalSelfAgent()
    
    # 测试通用任务
    agent._execute_generic_task("通用测试任务")
    has_generic = any(
        "通用测试任务" in node.name
        for node in agent.knowledge_graph.nodes.values()
    )
    assert has_generic is True

    # 测试推演任务
    agent.knowledge_graph.add_edge("推演源", "推演目标", "关联", 0.8)
    agent._execute_deduction_task("知识推演任务:推演源")

    print("✓ test_task_strategies 成功")


def test_self_drive_tasks():
    """测试自驱任务生成"""
    print("测试自驱任务生成...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage15_kg.json"

    agent = EternalSelfAgent()
    agent._generate_self_drive_tasks("已完成任务")

    has_reflect_task = any(
        "自我反思" in task
        for task in agent.task_queue.queue
    )
    assert has_reflect_task is True

    print("✓ test_self_drive_tasks 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段15：任务执行与知识沉淀闭环验收测试 ===")
    print("=" * 50)

    try:
        test_execute_task()
        test_knowledge_precipitation()
        test_derived_tasks()
        test_task_strategies()
        test_self_drive_tasks()

        print("\n" + "=" * 50)
        print("✅ 阶段15所有验收测试通过！")
        print("=" * 50)
    finally:
        cleanup_test_files()
        constants.KG_SAVE_PATH = "data/knowledge_graph.json"
