"""
阶段11验收测试：任务衍生与自驱生成器
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_graph import KnowledgeGraph
from core.task_generator import TaskGenerator
from core import constants


def cleanup_test_files():
    """清理测试文件"""
    test_path = Path("data/test_stage11_kg.json")
    for suffix in ['', '.tmp', '.bak']:
        f = test_path.with_suffix(suffix if suffix else '.json')
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_task_generator_init():
    """测试任务生成器初始化"""
    print("测试任务生成器初始化...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage11_kg.json"

    kg = KnowledgeGraph()
    generator = TaskGenerator(kg)

    assert generator is not None
    assert generator.kg is kg
    assert generator.reasoner is not None

    print("✓ test_task_generator_init 成功")


def test_generate_new_tasks():
    """测试生成新任务"""
    print("测试生成新任务...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage11_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("核心", "节点A", "关联", 0.8)
    kg.add_edge("核心", "节点B", "关联", 0.7)
    kg.add_edge("节点A", "节点C", "深层", 0.6)

    generator = TaskGenerator(kg)
    tasks = generator.generate_new_tasks(count=3)

    assert isinstance(tasks, list)
    assert len(tasks) <= 3

    print("✓ test_generate_new_tasks 成功")


def test_strategy_from_high_weight():
    """测试从高权重边生成策略"""
    print("测试从高权重边生成策略...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage11_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("节点1", "节点2", "高权重", 0.9)
    kg.add_edge("节点3", "节点4", "中权重", 0.5)

    generator = TaskGenerator(kg)
    tasks = generator._generate_from_high_weight_edges()

    assert isinstance(tasks, list)
    for task in tasks:
        assert "探索关联" in task

    print("✓ test_strategy_from_high_weight 成功")


def test_strategy_from_chain_reasoning():
    """测试从链式推理生成策略"""
    print("测试从链式推理生成策略...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage11_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("A", "B", "链1", 0.8)
    kg.add_edge("B", "C", "链2", 0.7)

    generator = TaskGenerator(kg)
    tasks = generator._generate_from_chain_reasoning()

    assert isinstance(tasks, list)
    for task in tasks:
        assert "推理验证" in task

    print("✓ test_strategy_from_chain_reasoning 成功")


def test_strategy_from_patterns():
    """测试从模式生成策略"""
    print("测试从模式生成策略...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage11_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("X", "Y", "频繁关系", 0.7)
    kg.add_edge("M", "N", "频繁关系", 0.6)

    generator = TaskGenerator(kg)
    tasks = generator._generate_from_patterns()

    assert isinstance(tasks, list)

    print("✓ test_strategy_from_patterns 成功")


def test_adaptive_tasks():
    """测试自适应任务生成"""
    print("测试自适应任务生成...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage11_kg.json"

    kg = KnowledgeGraph()
    generator = TaskGenerator(kg)

    state_empty_queue = {
        "task_queue_size": 3,
        "knowledge_nodes": 5,
        "knowledge_edges": 3
    }
    tasks_empty = generator.generate_adaptive_tasks(state_empty_queue)

    assert isinstance(tasks_empty, list)

    print("✓ test_adaptive_tasks 成功")


def test_startup_tasks():
    """测试启动任务生成"""
    print("测试启动任务生成...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage11_kg.json"

    kg = KnowledgeGraph()
    generator = TaskGenerator(kg)

    tasks = generator.generate_startup_tasks()

    assert isinstance(tasks, list)
    assert len(tasks) > 0

    print("✓ test_startup_tasks 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段11：任务衍生与自驱生成器验收测试 ===")
    print("=" * 50)

    try:
        test_task_generator_init()
        test_generate_new_tasks()
        test_strategy_from_high_weight()
        test_strategy_from_chain_reasoning()
        test_strategy_from_patterns()
        test_adaptive_tasks()
        test_startup_tasks()

        print("\n" + "=" * 50)
        print("✅ 阶段11所有验收测试通过！")
        print("=" * 50)
    finally:
        cleanup_test_files()
        constants.KG_SAVE_PATH = "data/knowledge_graph.json"
