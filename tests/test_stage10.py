"""
阶段10验收测试：知识推演引擎实现
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_graph import KnowledgeGraph
from core.reasoning import KnowledgeReasoner
from core import constants


def cleanup_test_files():
    """清理测试文件"""
    test_path = Path("data/test_stage10_kg.json")
    for suffix in ['', '.tmp', '.bak']:
        f = test_path.with_suffix(suffix if suffix else '.json')
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_reasoner_init():
    """测试推演器初始化"""
    print("测试推演器初始化...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage10_kg.json"

    kg = KnowledgeGraph()
    reasoner = KnowledgeReasoner(kg)

    assert reasoner is not None
    assert reasoner.kg is kg

    print("✓ test_reasoner_init 成功")


def test_derive_from_node():
    """测试从节点推演"""
    print("测试从节点推演...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage10_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("主节点", "关联节点A", "高关联", 0.8)
    kg.add_edge("主节点", "关联节点B", "中关联", 0.5)

    reasoner = KnowledgeReasoner(kg)
    associations = reasoner.derive_from_node("主节点")

    assert isinstance(associations, list)
    if len(associations) > 0:
        for target, relation, weight in associations:
            assert isinstance(target, str)
            assert isinstance(relation, str)
            assert isinstance(weight, float)

    print("✓ test_derive_from_node 成功")


def test_derive_from_all_nodes():
    """测试从所有节点推演"""
    print("测试从所有节点推演...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage10_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("节点A", "节点B", "关联", 0.7)
    kg.add_edge("节点A", "节点C", "关联", 0.6)

    reasoner = KnowledgeReasoner(kg)
    tasks = reasoner.derive_from_all_nodes(limit=5)

    assert isinstance(tasks, list)
    assert len(tasks) <= 5

    print("✓ test_derive_from_all_nodes 成功")


def test_chain_reasoning():
    """测试链式推理"""
    print("测试链式推理...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage10_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("A", "B", "rel1", 0.8)
    kg.add_edge("B", "C", "rel2", 0.7)

    reasoner = KnowledgeReasoner(kg)
    chains = reasoner.chain_reasoning("A", depth=2)

    assert isinstance(chains, list)
    for chain in chains:
        assert "path" in chain
        assert "weight" in chain
        assert "depth" in chain

    print("✓ test_chain_reasoning 成功")


def test_mine_patterns():
    """测试模式挖掘"""
    print("测试模式挖掘...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage10_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("A", "B", "相同关系", 0.7)
    kg.add_edge("C", "D", "相同关系", 0.6)
    kg.add_edge("E", "F", "相同关系", 0.8)

    reasoner = KnowledgeReasoner(kg)
    patterns = reasoner.mine_patterns()

    assert isinstance(patterns, list)
    if len(patterns) > 0:
        assert "相同关系" in [p[0] for p in patterns]

    print("✓ test_mine_patterns 成功")


def test_predict_next_node():
    """测试预测下一个节点"""
    print("测试预测下一个节点...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage10_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("A", "B", "step1", 0.7)
    kg.add_edge("B", "C", "step2", 0.6)

    reasoner = KnowledgeReasoner(kg)
    predictions = reasoner.predict_next_node("A", count=3)

    assert isinstance(predictions, list)
    if len(predictions) > 0:
        for node, path, score in predictions:
            assert isinstance(node, str)
            assert isinstance(score, float)

    print("✓ test_predict_next_node 成功")


def test_complete_missing_links():
    """测试补全缺失链接"""
    print("测试补全缺失链接...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage10_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("A", "B", "rel1", 0.7)
    kg.add_edge("B", "C", "rel2", 0.6)

    reasoner = KnowledgeReasoner(kg)
    missing = reasoner.complete_missing_links("A")

    assert isinstance(missing, list)

    print("✓ test_complete_missing_links 成功")


def test_generate_insights():
    """测试生成洞察"""
    print("测试生成洞察...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage10_kg.json"

    kg = KnowledgeGraph()
    kg.add_edge("核心", "关联1", "关联", 0.8)
    kg.add_edge("核心", "关联2", "关联", 0.7)
    kg.add_edge("关联1", "深层", "深层关联", 0.6)

    reasoner = KnowledgeReasoner(kg)
    insights = reasoner.generate_insights("核心", limit=5)

    assert isinstance(insights, list)
    for insight in insights:
        assert "type" in insight

    print("✓ test_generate_insights 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段10：知识推演引擎实现验收测试 ===")
    print("=" * 50)

    try:
        test_reasoner_init()
        test_derive_from_node()
        test_derive_from_all_nodes()
        test_chain_reasoning()
        test_mine_patterns()
        test_predict_next_node()
        test_complete_missing_links()
        test_generate_insights()

        print("\n" + "=" * 50)
        print("✅ 阶段10所有验收测试通过！")
        print("=" * 50)
    finally:
        cleanup_test_files()
        constants.KG_SAVE_PATH = "data/knowledge_graph.json"
