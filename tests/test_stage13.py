"""
阶段13验收测试：自驱进化层完整实现
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_graph import KnowledgeGraph
from core.task_queue import TaskQueue
from core.evolution import EvolutionLayer
from core import constants


def cleanup_test_files():
    """清理测试文件"""
    test_path = Path("data/test_stage13_kg.json")
    for suffix in ['', '.tmp', '.bak']:
        f = test_path.with_suffix(suffix if suffix else '.json')
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_evolution_layer_init():
    """测试进化层初始化"""
    print("测试进化层初始化...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage13_kg.json"

    kg = KnowledgeGraph()
    task_queue = TaskQueue()
    evolution = EvolutionLayer(kg, task_queue)

    assert evolution is not None
    assert evolution.kg is kg
    assert evolution.task_queue is task_queue
    assert evolution.reasoner is not None
    assert evolution.task_generator is not None

    print("✓ test_evolution_layer_init 成功")


def test_evolve():
    """测试evolve方法"""
    print("测试evolve方法...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage13_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("核心", "节点1", "关联", 0.8)
    kg.add_edge("核心", "节点2", "关联", 0.7)

    task_queue = TaskQueue()
    evolution = EvolutionLayer(kg, task_queue)

    stats = evolution.evolve()

    assert isinstance(stats, dict)
    assert "evolution_count" in stats
    assert "tasks_generated" in stats

    print("✓ test_evolve 成功")


def test_idle_evolve():
    """测试空闲进化"""
    print("测试空闲进化...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage13_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("A", "B", "关联", 0.9)

    task_queue = TaskQueue()
    evolution = EvolutionLayer(kg, task_queue)

    total_stats = evolution.idle_evolve(iterations=2)

    assert isinstance(total_stats, dict)
    assert "iterations" in total_stats
    assert total_stats["iterations"] == 2

    print("✓ test_idle_evolve 成功")


def test_adaptive_evolve():
    """测试自适应进化"""
    print("测试自适应进化...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage13_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("测试", "内容", "测试关联", 0.8)

    task_queue = TaskQueue()
    evolution = EvolutionLayer(kg, task_queue)

    state_empty_queue = {"task_queue_size": 1, "memory_percent": 30}
    stats = evolution.adaptive_evolve(state_empty_queue)

    assert isinstance(stats, dict)
    assert "strategy" in stats

    print("✓ test_adaptive_evolve 成功")


def test_evolution_status():
    """测试进化状态获取"""
    print("测试进化状态获取...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage13_kg.json"

    kg = KnowledgeGraph()
    task_queue = TaskQueue()
    evolution = EvolutionLayer(kg, task_queue)

    status = evolution.get_evolution_status()

    assert isinstance(status, dict)
    assert "evolution_count" in status
    assert "knowledge_nodes" in status
    assert "knowledge_edges" in status

    print("✓ test_evolution_status 成功")


def test_evolution_recorded():
    """测试进化事件被记录到知识图谱"""
    print("测试进化事件被记录到知识图谱...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage13_kg.json"

    kg = KnowledgeGraph()
    task_queue = TaskQueue()
    evolution = EvolutionLayer(kg, task_queue)

    evolution.evolve()

    has_evolution_node = any(
        "进化迭代" in node.name
        for node in kg.nodes.values()
    )
    assert has_evolution_node is True

    print("✓ test_evolution_recorded 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段13：自驱进化层完整实现验收测试 ===")
    print("=" * 50)

    try:
        test_evolution_layer_init()
        test_evolve()
        test_idle_evolve()
        test_adaptive_evolve()
        test_evolution_status()
        test_evolution_recorded()

        print("\n" + "=" * 50)
        print("✅ 阶段13所有验收测试通过！")
        print("=" * 50)
    finally:
        cleanup_test_files()
        constants.KG_SAVE_PATH = "data/knowledge_graph.json"
