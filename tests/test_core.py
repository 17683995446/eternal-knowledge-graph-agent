"""
测试核心模块
"""

import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_graph import Node, Edge, KnowledgeGraph


def test_node_creation():
    """测试节点创建"""
    node = Node("测试任务")
    assert node.name == "测试任务"
    assert node.valid == True
    assert node.id is not None
    print("✓ test_node_creation 成功")


def test_edge_creation():
    """测试边创建"""
    edge = Edge("任务A", "任务B", "自主衍生", 0.8)
    assert edge.source == "任务A"
    assert edge.weight == 0.8
    print("✓ test_edge_creation 成功")


def test_serialization():
    """测试序列化"""
    node = Node("测试节点", {"type": "task"})
    data = node.to_dict()
    restored = Node.from_dict(data)
    assert restored.name == node.name
    assert restored.attr == node.attr
    print("✓ test_serialization 成功")


def test_knowledge_graph():
    """测试知识图谱"""
    # 临时修改保存路径
    import core.constants
    original_save_path = core.constants.KG_SAVE_PATH
    core.constants.KG_SAVE_PATH = "data/test_graph.json"
    
    # 创建临时数据目录
    Path("data").mkdir(parents=True, exist_ok=True)
    
    # 创建图谱
    kg = KnowledgeGraph()
    kg.add_node("测试节点1")
    kg.add_edge("测试节点1", "测试节点2", "测试关系", 0.9)
    
    # 验证
    assert len(kg.nodes) == 2
    assert len(kg.edges) == 1
    
    # 清理
    test_path = Path("data/test_graph.json")
    if test_path.exists():
        test_path.unlink()
    
    core.constants.KG_SAVE_PATH = original_save_path
    print("✓ test_knowledge_graph 成功")


if __name__ == "__main__":
    print("=== 阶段1 验收测试 ===")
    test_node_creation()
    test_edge_creation()
    test_serialization()
    test_knowledge_graph()
    print("\n✅ 所有测试通过！")
