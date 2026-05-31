"""
阶段19验收测试：性能优化与资源管理
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_graph import KnowledgeGraph
from core.optimizations import PerformanceOptimizer, patch_knowledge_graph
from core import constants


def cleanup_test_files():
    """清理测试文件"""
    test_path = Path("data/test_stage19_kg.json")
    for suffix in ['', '.tmp', '.bak']:
        f = test_path.with_suffix(suffix if suffix else '.json')
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_performance_optimizer_initialization():
    """测试性能优化器初始化"""
    print("测试性能优化器初始化...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage19_kg.json"

    kg = KnowledgeGraph()
    optimizer = PerformanceOptimizer(kg)

    assert optimizer is not None
    assert optimizer.kg == kg

    print("✓ test_performance_optimizer_initialization 成功")


def test_index_optimization():
    """测试索引优化功能"""
    print("测试索引优化功能...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage19_kg.json"

    kg = KnowledgeGraph()
    optimizer = PerformanceOptimizer(kg)

    # 添加一些节点和边
    node1 = kg.add_node("测试节点1")
    node2 = kg.add_node("测试节点2")
    edge = kg.add_edge("测试节点1", "测试节点2", "测试关系", 0.8)

    # 手动更新索引（因为我们没有使用patch）
    optimizer.update_node_index(node1)
    optimizer.update_node_index(node2)
    optimizer.update_edge_indices(edge)

    # 测试快速查找
    found_node = optimizer.get_node_by_name_fast("测试节点1")
    assert found_node is not None
    assert found_node.name == "测试节点1"

    # 检查索引是否被正确填充
    stats = optimizer.get_performance_stats()
    assert stats["indexed_nodes"] >= 2

    print("✓ test_index_optimization 成功")


def test_lazy_saving():
    """测试延迟保存功能"""
    print("测试延迟保存功能...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage19_kg.json"

    kg = KnowledgeGraph()
    optimizer = PerformanceOptimizer(kg)

    # 添加一些数据
    kg.add_node("延迟保存测试节点")

    # 测试延迟保存
    optimizer.save_lazy()
    stats = optimizer.get_performance_stats()

    # 检查统计信息
    assert "time_since_last_save" in stats
    assert "is_dirty" in stats

    print("✓ test_lazy_saving 成功")


def test_batch_saving():
    """测试批量保存功能"""
    print("测试批量保存功能...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage19_kg.json"

    kg = KnowledgeGraph()
    optimizer = PerformanceOptimizer(kg)

    # 添加多个节点，触发批量保存
    for i in range(15):
        kg.add_node(f"批量测试节点_{i}")
        optimizer.save_batch()

    # 检查统计信息
    stats = optimizer.get_performance_stats()
    assert "pending_saves" in stats

    # 强制保存
    optimizer.force_save()

    print("✓ test_batch_saving 成功")


def test_memory_optimization():
    """测试内存优化功能"""
    print("测试内存优化功能...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage19_kg.json"

    kg = KnowledgeGraph()
    optimizer = PerformanceOptimizer(kg)

    # 添加带有空属性的节点
    kg.add_node("内存测试节点1", {"value": "test", "empty": None, "blank": ""})
    kg.add_node("内存测试节点2")

    # 进行内存优化
    optimizer.optimize_memory()

    # 验证优化（间接验证，因为我们无法直接测量内存）
    print("内存优化完成")

    print("✓ test_memory_optimization 成功")


def test_patch_knowledge_graph():
    """测试知识图谱打补丁功能"""
    print("测试知识图谱打补丁功能...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage19_kg.json"

    kg = KnowledgeGraph()

    # 打补丁
    optimizer = patch_knowledge_graph(kg)

    assert hasattr(kg, "optimizer")
    assert kg.optimizer == optimizer

    # 测试补丁后的方法
    kg.add_node("补丁测试节点")
    kg.add_edge("补丁测试节点", "另一个节点", "测试", 0.5)

    print("✓ test_patch_knowledge_graph 成功")


def test_performance_stats():
    """测试性能统计功能"""
    print("测试性能统计功能...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage19_kg.json"

    kg = KnowledgeGraph()
    optimizer = PerformanceOptimizer(kg)

    # 添加一些数据
    for i in range(10):
        kg.add_node(f"统计测试节点_{i}")
        if i > 0:
            kg.add_edge(f"统计测试节点_{i-1}", f"统计测试节点_{i}", "链接", 0.7)

    # 获取统计
    stats = optimizer.get_performance_stats()

    # 验证统计信息
    assert "node_count" in stats
    assert "edge_count" in stats
    assert "indexed_nodes" in stats
    assert "is_dirty" in stats
    assert "pending_saves" in stats
    assert "time_since_last_save" in stats

    print(f"性能统计: {stats}")
    print("✓ test_performance_stats 成功")


def test_optimization_integration():
    """测试优化功能的集成"""
    print("测试优化功能的集成...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage19_kg.json"

    # 创建知识图谱并打补丁
    kg = KnowledgeGraph()
    optimizer = patch_knowledge_graph(kg)

    # 执行一系列操作
    for i in range(20):
        kg.add_node(f"集成测试节点_{i}")

    for i in range(1, 20):
        kg.add_edge(f"集成测试节点_{i-1}", f"集成测试节点_{i}", f"关系_{i}", 0.6)

    # 执行优化
    optimizer.optimize_memory()

    # 获取最终统计
    stats = optimizer.get_performance_stats()
    print(f"集成测试完成，统计: {stats}")

    assert stats["node_count"] >= 20

    print("✓ test_optimization_integration 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段19：性能优化与资源管理验收测试 ===")
    print("=" * 50)

    try:
        test_performance_optimizer_initialization()
        test_index_optimization()
        test_lazy_saving()
        test_batch_saving()
        test_memory_optimization()
        test_patch_knowledge_graph()
        test_performance_stats()
        test_optimization_integration()

        print("\n" + "=" * 50)
        print("✅ 阶段19所有验收测试通过！")
        print("=" * 50)
    finally:
        cleanup_test_files()
        constants.KG_SAVE_PATH = "data/knowledge_graph.json"
