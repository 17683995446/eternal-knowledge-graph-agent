"""
阶段2 验收测试：知识图谱基础数据结构
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_graph import Node, Edge


def test_node_creation_basic():
    """基本节点创建测试"""
    node = Node("测试任务")
    assert node.name == "测试任务"
    assert node.valid == True
    assert node.id is not None
    print("✓ test_node_creation_basic 成功")


def test_node_creation_with_attr():
    """带属性的节点创建测试"""
    attr = {"type": "task", "priority": "high"}
    node = Node("任务节点", attr)
    assert node.name == "任务节点"
    assert node.attr["type"] == "task"
    assert node.attr["priority"] == "high"
    print("✓ test_node_creation_with_attr 成功")


def test_node_invalid_name():
    """测试无效节点名称"""
    try:
        Node(None)
        assert False, "应该抛出异常"
    except ValueError:
        pass
    
    try:
        Node("")
        assert False, "应该抛出异常"
    except ValueError:
        pass
    
    try:
        Node(123)
        assert False, "应该抛出异常"
    except ValueError:
        pass
    
    print("✓ test_node_invalid_name 成功")


def test_node_attr_conversion():
    """测试非字典属性转换"""
    node = Node("测试", "字符串属性")
    assert node.attr["raw_value"] == "字符串属性"
    
    node2 = Node("测试2", 12345)
    assert node2.attr["raw_value"] == "12345"
    print("✓ test_node_attr_conversion 成功")


def test_node_serialization():
    """节点序列化/反序列化测试"""
    node = Node("测试节点", {"type": "task"})
    data = node.to_dict()
    restored = Node.from_dict(data)
    
    assert restored.name == node.name
    assert restored.attr == node.attr
    assert restored.id == node.id
    assert restored.created_at == node.created_at
    print("✓ test_node_serialization 成功")


def test_node_timestamp_format():
    """测试时间戳格式（ISO 8601）"""
    node = Node("测试时间节点")
    # 验证时间戳是 ISO 格式
    parsed = datetime.fromisoformat(node.created_at)
    assert isinstance(parsed, datetime)
    print("✓ test_node_timestamp_format 成功")


def test_edge_creation_basic():
    """基本边创建测试"""
    edge = Edge("任务A", "任务B", "自主衍生", 0.8)
    assert edge.source == "任务A"
    assert edge.target == "任务B"
    assert edge.relation == "自主衍生"
    assert edge.weight == 0.8
    print("✓ test_edge_creation_basic 成功")


def test_edge_weight_normalization():
    """测试权重归一化"""
    # 测试各种边界值
    test_cases = [
        (0.5, 0.5),
        (0.0, 0.0),
        (1.0, 1.0),
        (-0.5, 0.0),   # 低于边界
        (1.5, 1.0),    # 高于边界
        (100, 1.0),
        ("invalid", 0.5),  # 无效类型
        (None, 0.5)
    ]
    
    for input_w, expected_w in test_cases:
        edge = Edge("A", "B", "test", input_w)
        assert edge.weight == expected_w
        assert 0.0 <= edge.weight <= 1.0
    
    print("✓ test_edge_weight_normalization 成功")


def test_edge_invalid_params():
    """测试无效边参数"""
    try:
        Edge(None, "B", "rel", 0.5)
        assert False, "应该抛出异常"
    except ValueError:
        pass
    
    try:
        Edge("A", None, "rel", 0.5)
        assert False, "应该抛出异常"
    except ValueError:
        pass
    
    try:
        Edge("A", "B", "", 0.5)
        assert False, "应该抛出异常"
    except ValueError:
        pass
    
    print("✓ test_edge_invalid_params 成功")


def test_edge_serialization():
    """边序列化/反序列化测试"""
    edge = Edge("源节点", "目标节点", "关联关系", 0.65)
    data = edge.to_dict()
    restored = Edge.from_dict(data)
    
    assert restored.source == edge.source
    assert restored.target == edge.target
    assert restored.relation == edge.relation
    assert restored.weight == edge.weight
    print("✓ test_edge_serialization 成功")


def test_edge_timestamp_format():
    """测试边时间戳格式"""
    edge = Edge("A", "B", "rel", 0.5)
    parsed = datetime.fromisoformat(edge.created_at)
    assert isinstance(parsed, datetime)
    print("✓ test_edge_timestamp_format 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段2：知识图谱基础数据结构验收测试 ===")
    print("=" * 50)
    
    test_node_creation_basic()
    test_node_creation_with_attr()
    test_node_invalid_name()
    test_node_attr_conversion()
    test_node_serialization()
    test_node_timestamp_format()
    test_edge_creation_basic()
    test_edge_weight_normalization()
    test_edge_invalid_params()
    test_edge_serialization()
    test_edge_timestamp_format()
    
    print("\n" + "=" * 50)
    print("✅ 阶段2所有验收测试通过！")
    print("=" * 50)
