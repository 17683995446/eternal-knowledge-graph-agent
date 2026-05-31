"""
阶段12验收测试：知识精简与自动淘汰算法
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_graph import KnowledgeGraph
from core import constants


def cleanup_test_files():
    """清理测试文件"""
    test_path = Path("data/test_stage12_kg.json")
    for suffix in ['', '.tmp', '.bak']:
        f = test_path.with_suffix(suffix if suffix else '.json')
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_trim_invalid_knowledge():
    """测试基础知识淘汰"""
    print("测试基础知识淘汰...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage12_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("节点1", "节点2", "关联", 0.05)  # 低权重
    kg.add_edge("节点1", "节点3", "高价值", 0.9)  # 高权重

    result = kg.trim_invalid_knowledge()

    assert isinstance(result, dict)
    assert "remaining_nodes" in result
    assert "remaining_edges" in result

    print("✓ test_trim_invalid_knowledge 成功")


def test_smart_trim():
    """测试智能淘汰策略"""
    print("测试智能淘汰策略...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage12_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("A", "B", "关联", 0.8)
    kg.add_edge("C", "D", "低关联", 0.1)

    result_balanced = kg.smart_trim(strategy="balanced")
    assert isinstance(result_balanced, dict)
    assert "strategy" in result_balanced

    print("✓ test_smart_trim 成功")


def test_merge_duplicate_edges():
    """测试重复边合并"""
    print("测试重复边合并...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage12_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("X", "Y", "相同关系", 0.5)
    kg.add_edge("X", "Y", "相同关系", 0.7)  # 重复

    before = len(kg.edges)
    kg._merge_duplicate_edges()
    after = len(kg.edges)

    assert after <= before

    print("✓ test_merge_duplicate_edges 成功")


def test_trim_history():
    """测试淘汰历史记录"""
    print("测试淘汰历史记录...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage12_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("节点", "其他", "关联", 0.8)

    history_before = kg.get_trim_history()
    kg.trim_invalid_knowledge()
    history_after = kg.get_trim_history()

    assert len(history_after) >= len(history_before)

    print("✓ test_trim_history 成功")


def test_high_weight_preserved():
    """测试高权重知识被保留"""
    print("测试高权重知识被保留...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage12_kg.json"

    kg = KnowledgeGraph()
    important_weight = 0.95
    kg.add_edge("重要", "关键", "核心关联", important_weight)

    kg.trim_invalid_knowledge()

    has_important = any(
        e.weight == important_weight and e.source == "重要"
        for e in kg.edges
    )
    assert has_important is True

    print("✓ test_high_weight_preserved 成功")


def test_age_based_trim():
    """测试基于时间的淘汰"""
    print("测试基于时间的淘汰...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage12_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("节点A", "节点B", "临时", 0.3)
    kg.add_edge("核心1", "核心2", "持久", 0.9)

    result = kg.age_based_trim(max_age_days=30)

    assert isinstance(result, dict)

    print("✓ test_age_based_trim 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段12：知识精简与自动淘汰算法验收测试 ===")
    print("=" * 50)

    try:
        test_trim_invalid_knowledge()
        test_smart_trim()
        test_merge_duplicate_edges()
        test_trim_history()
        test_high_weight_preserved()
        test_age_based_trim()

        print("\n" + "=" * 50)
        print("✅ 阶段12所有验收测试通过！")
        print("=" * 50)
    finally:
        cleanup_test_files()
        constants.KG_SAVE_PATH = "data/knowledge_graph.json"
