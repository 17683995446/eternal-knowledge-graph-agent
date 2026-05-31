"""
阶段4 验收测试：节点与边的基本CRUD操作
"""

import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 临时修改保存路径用于测试
from core import constants
original_save_path = constants.KG_SAVE_PATH
test_save_path = Path("data/test_kg_crud.json")
constants.KG_SAVE_PATH = str(test_save_path)

from core.knowledge_graph import KnowledgeGraph


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


def test_add_node_deduplication():
    """测试add_node自动去重"""
    cleanup_test_files()
    
    kg = KnowledgeGraph()
    
    node1 = kg.add_node("测试节点")
    node2 = kg.add_node("测试节点")
    
    # 应该返回同一个实例
    assert node1.id == node2.id
    assert len(kg.nodes) == 1
    print("✓ test_add_node_deduplication 成功")


def test_add_edge_creates_nodes():
    """测试add_edge自动创建关联节点"""
    cleanup_test_files()
    
    kg = KnowledgeGraph()
    
    # 添加边，源节点和目标节点都不存在
    kg.add_edge("节点A", "节点B", "关联关系", 0.7)
    
    # 两个节点应该都自动创建了
    assert kg.get_node_by_name("节点A") is not None
    assert kg.get_node_by_name("节点B") is not None
    assert len(kg.nodes) == 2
    assert len(kg.edges) == 1
    print("✓ test_add_edge_creates_nodes 成功")


def test_add_edge_updates_existing():
    """测试add_edge更新现有边的权重"""
    cleanup_test_files()
    
    kg = KnowledgeGraph()
    
    kg.add_edge("A", "B", "rel", 0.5)
    edge1 = kg.edges[0]
    
    # 再次添加相同的边，权重更高
    kg.add_edge("A", "B", "rel", 0.9)
    
    # 应该是同一个边，权重更新了
    assert len(kg.edges) == 1
    assert edge1.weight == 0.9  # 取最大值
    print("✓ test_add_edge_updates_existing 成功")


def test_query_edges():
    """测试边查询方法"""
    cleanup_test_files()
    
    kg = KnowledgeGraph()
    
    kg.add_edge("中心", "左", "左连接", 0.6)
    kg.add_edge("中心", "右", "右连接", 0.7)
    kg.add_edge("上", "中心", "上连接", 0.8)
    kg.add_edge("下", "中心", "下连接", 0.9)
    
    # 查询出发边
    from_center = kg.get_edges_from("中心")
    assert len(from_center) == 2
    
    # 查询入边
    to_center = kg.get_edges_to("中心")
    assert len(to_center) == 2
    print("✓ test_query_edges 成功")


def test_get_neighbors():
    """测试获取邻居"""
    cleanup_test_files()
    
    kg = KnowledgeGraph()
    
    kg.add_edge("中心", "左", "左连接", 0.4)
    kg.add_edge("中心", "右", "右连接", 0.8)
    
    # 无阈值
    all_neighbors = kg.get_neighbors("中心")
    assert len(all_neighbors) == 2
    
    # 高阈值
    high_neighbors = kg.get_neighbors("中心", 0.5)
    assert len(high_neighbors) == 1
    print("✓ test_get_neighbors 成功")


def test_delete_node_cascades():
    """测试删除节点级联清理边"""
    cleanup_test_files()
    
    kg = KnowledgeGraph()
    
    kg.add_edge("A", "B", "ab", 0.5)
    kg.add_edge("B", "C", "bc", 0.6)
    kg.add_edge("C", "D", "cd", 0.7)
    
    # 删除节点B
    result = kg.delete_node("B")
    
    assert result is True
    assert kg.get_node_by_name("B") is None
    assert len(kg.edges) == 1  # 只剩下 C->D
    assert len(kg.nodes) == 3  # A、C、D 还在
    print("✓ test_delete_node_cascades 成功")


def test_update_node_attr():
    """测试节点属性更新"""
    cleanup_test_files()
    
    kg = KnowledgeGraph()
    
    kg.add_node("节点", {"初始": "值"})
    node = kg.get_node_by_name("节点")
    
    # 更新属性
    result = kg.update_node_attr("节点", {"新属性": "新值"})
    
    assert result is True
    assert node.attr["初始"] == "值"
    assert node.attr["新属性"] == "新值"
    print("✓ test_update_node_attr 成功")


def test_invalidate_node():
    """测试节点无效化"""
    cleanup_test_files()
    
    kg = KnowledgeGraph()
    
    kg.add_node("节点", {})
    result = kg.invalidate_node("节点")
    
    assert result is True
    
    node = kg.get_node_by_name("节点")
    assert node is not None
    assert node.valid is False
    print("✓ test_invalidate_node 成功")


def test_edge_weight_operations():
    """测试边权重操作"""
    cleanup_test_files()
    
    kg = KnowledgeGraph()
    
    kg.add_edge("A", "B", "test", 0.5)
    
    # 强化
    edge = kg._get_edge("A", "B", "test")
    edge.weight = 0.7
    kg.save()
    
    # 验证
    assert kg.edges[0].weight == 0.7
    
    # 弱化
    edge.weight = 0.4
    kg.save()
    
    assert kg.edges[0].weight == 0.4
    print("✓ test_edge_weight_operations 成功")


def test_all_operations_auto_save():
    """测试所有操作后自动save"""
    cleanup_test_files()
    
    kg1 = KnowledgeGraph()
    
    kg1.add_node("节点1")
    kg1.add_edge("节点1", "节点2", "rel", 0.5)
    kg1.update_node_attr("节点1", {"key": "value"})
    
    # 重新加载验证
    kg2 = KnowledgeGraph()
    assert len(kg2.nodes) == 2
    assert len(kg2.edges) == 1
    
    node = kg2.get_node_by_name("节点1")
    assert node.attr["key"] == "value"
    print("✓ test_all_operations_auto_save 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段4：节点与边的基本CRUD操作验收测试 ===")
    print("=" * 50)
    
    try:
        test_add_node_deduplication()
        test_add_edge_creates_nodes()
        test_add_edge_updates_existing()
        test_query_edges()
        test_get_neighbors()
        test_delete_node_cascades()
        test_update_node_attr()
        test_invalidate_node()
        test_edge_weight_operations()
        test_all_operations_auto_save()
        
        print("\n" + "=" * 50)
        print("✅ 阶段4所有验收测试通过！")
        print("=" * 50)
    finally:
        cleanup_test_files()
        # 恢复原始路径
        constants.KG_SAVE_PATH = original_save_path
