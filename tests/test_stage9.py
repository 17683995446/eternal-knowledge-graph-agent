"""
阶段9验收测试：权重系统与关联推理
"""

import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 临时修改保存路径用于测试
from core import constants
original_save_path = constants.KG_SAVE_PATH
test_save_path = Path("data/test_stage9_kg.json")

from core.knowledge_graph import KnowledgeGraph
from core.constants import WEIGHT_HIGH


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


def test_calculate_edge_weight():
    """测试权重计算"""
    print("测试权重计算...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = str(test_save_path)

    kg = KnowledgeGraph()
    kg.add_node("A")
    kg.add_node("B")

    # 添加单个边
    kg.add_edge("A", "B", "test", 0.5)
    weight = kg.calculate_edge_weight("A", "B")
    assert weight >= 0.5

    print("✓ test_calculate_edge_weight 成功")


def test_update_edge_weight():
    """测试权重更新"""
    print("测试权重更新...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = str(test_save_path)

    kg = KnowledgeGraph()
    kg.add_edge("X", "Y", "test", 0.5)

    # 强化权重
    result = kg.update_edge_weight("X", "Y", "test", 0.2)
    assert result is True

    edge = kg._get_edge("X", "Y", "test")
    assert edge.weight == 0.7

    print("✓ test_update_edge_weight 成功")


def test_find_strong_associations():
    """测试强关联查找"""
    print("测试强关联查找...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = str(test_save_path)

    kg = KnowledgeGraph()

    # 添加多个关系
    kg.add_edge("Main", "A", "high", 0.8)
    kg.add_edge("Main", "B", "medium", 0.5)
    kg.add_edge("Main", "C", "low", 0.1)

    associations = kg.find_strong_associations("Main", threshold=0.3)

    assert len(associations) >= 1
    # 检查返回的元组格式
    for target, relation, weight in associations:
        assert isinstance(target, str)
        assert isinstance(relation, str)
        assert isinstance(weight, float)

    print("✓ test_find_strong_associations 成功")


def test_find_path():
    """测试路径查找"""
    print("测试路径查找...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = str(test_save_path)

    kg = KnowledgeGraph()

    # 构建一个简单的路径
    kg.add_edge("Start", "Middle", "step1", 0.7)
    kg.add_edge("Middle", "End", "step2", 0.6)

    # 查找路径
    paths = kg.find_path("Start", "End", max_depth=3)
    assert paths is not None
    assert len(paths) > 0

    # 测试无法找到的路径
    no_path = kg.find_path("Start", "NotFound", max_depth=3)
    assert no_path is None

    print("✓ test_find_path 成功")


def test_infer_new_relations():
    """测试新关系推理"""
    print("测试新关系推理...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = str(test_save_path)

    kg = KnowledgeGraph()

    # 构建一个可传递的关系网络
    kg.add_edge("A", "B", "rel1", 0.7)
    kg.add_edge("B", "C", "rel2", 0.6)

    # 直接测试方法存在并且可以调用
    inferred = kg.infer_new_relations("A")

    # 基本测试：返回的是列表，元素是元组
    assert isinstance(inferred, list)
    if len(inferred) > 0:
        for item in inferred:
            assert isinstance(item, tuple)
            assert len(item) == 3

    print("✓ test_infer_new_relations 成功")


def test_bfs_traverse():
    """测试BFS遍历"""
    print("测试BFS遍历...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = str(test_save_path)

    kg = KnowledgeGraph()

    # 构建一个小图
    kg.add_edge("Root", "Child1", "child", 0.8)
    kg.add_edge("Root", "Child2", "child", 0.7)
    kg.add_edge("Child1", "Grandchild", "grandchild", 0.6)

    traverse_result = kg.bfs_traverse("Root", max_depth=2)

    assert len(traverse_result) >= 2
    for node, relation, weight, depth in traverse_result:
        assert isinstance(node, str)
        assert depth >= 1

    print("✓ test_bfs_traverse 成功")


def test_get_subgraph():
    """测试子图获取"""
    print("测试子图获取...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = str(test_save_path)

    kg = KnowledgeGraph()

    # 构建一个小图
    kg.add_edge("Core", "Related1", "related", 0.8)
    kg.add_edge("Core", "Related2", "related", 0.7)
    kg.add_edge("Related1", "Peripheral", "peripheral", 0.6)

    nodes, edges = kg.get_subgraph(["Core"], depth=2)

    assert "Core" in nodes
    assert "Related1" in nodes
    assert len(edges) >= 2

    print("✓ test_get_subgraph 成功")


def test_weight_update_saved():
    """测试权重更新后保存"""
    print("测试权重更新后保存...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = str(test_save_path)

    kg = KnowledgeGraph()
    kg.add_edge("Test1", "Test2", "update_test", 0.5)

    # 更新权重
    kg.reinforce_edge("Test1", "Test2", "update_test", 0.3)

    # 重新加载验证保存成功
    kg2 = KnowledgeGraph()
    edge = kg2._get_edge("Test1", "Test2", "update_test")
    assert edge.weight >= 0.5

    print("✓ test_weight_update_saved 成功")


def test_associations_sorted():
    """测试关联关系按权重排序"""
    print("测试关联关系按权重排序...")

    cleanup_test_files()
    constants.KG_SAVE_PATH = str(test_save_path)

    kg = KnowledgeGraph()

    kg.add_edge("Center", "Low", "low", 0.3)
    kg.add_edge("Center", "Medium", "medium", 0.6)
    kg.add_edge("Center", "High", "high", 0.9)

    associations = kg.find_strong_associations("Center", threshold=0.0)

    # 验证是按权重降序排列
    weights = [w for (_, _, w) in associations]
    for i in range(len(weights) - 1):
        assert weights[i] >= weights[i + 1]

    print("✓ test_associations_sorted 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段9：权重系统与关联推理验收测试 ===")
    print("=" * 50)

    try:
        test_calculate_edge_weight()
        test_update_edge_weight()
        test_find_strong_associations()
        test_find_path()
        test_infer_new_relations()
        test_bfs_traverse()
        test_get_subgraph()
        test_weight_update_saved()
        test_associations_sorted()

        print("\n" + "=" * 50)
        print("✅ 阶段9所有验收测试通过！")
        print("=" * 50)
    finally:
        # 清理测试
        cleanup_test_files()
        # 恢复原始路径
        constants.KG_SAVE_PATH = original_save_path
