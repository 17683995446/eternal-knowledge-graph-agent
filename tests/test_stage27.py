"""
阶段27验收测试：时间序列知识处理
测试时间戳、时间范围查询、知识演变追踪功能
"""
import os
import sys
import time
import shutil
import random
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))


def get_unique_name(base: str) -> str:
    """生成唯一的名称"""
    return f"{base}_{int(time.time() * 1000000)}_{random.randint(1000, 9999)}"


def test_temporal_kg_basics():
    """测试时间序列知识图谱基础功能"""
    print("\n=== 测试1: 时间序列知识图谱基础功能 ===")
    
    from core.temporal_knowledge import TemporalKnowledgeGraph
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    temporal_kg = TemporalKnowledgeGraph(kg)
    
    assert temporal_kg is not None, "时间序列知识图谱应该能创建"
    print("✓ 时间序列知识图谱创建成功")
    
    assert len(temporal_kg.temporal_nodes) > 0, "应该有初始化的节点"
    print(f"✓ 从现有知识图谱初始化成功，{len(temporal_kg.temporal_nodes)} 个节点")
    
    print("✓ 测试1通过!")
    return True


def test_temporal_node_creation():
    """测试时间节点创建"""
    print("\n=== 测试2: 时间节点创建 ===")
    
    from core.temporal_knowledge import TemporalKnowledgeGraph, TimeEventType
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    temporal_kg = TemporalKnowledgeGraph(kg)
    
    initial_node_count = len(temporal_kg.temporal_nodes)
    
    # 创建测试节点
    node_name1 = get_unique_name("测试节点1")
    node = temporal_kg.add_temporal_node(node_name1, {"type": "test"})
    assert node is not None, "节点应该能创建"
    assert node.name == node_name1, "节点名称应该正确"
    assert len(node.history) > 0, "节点应该有历史记录"
    assert node.history[0].event_type == TimeEventType.CREATED, "第一个事件应该是创建"
    print("✓ 时间节点创建成功")
    
    # 创建带有效期的节点
    node_name2 = get_unique_name("测试节点2")
    valid_from = datetime.now().isoformat()
    valid_until = (datetime.now() + timedelta(days=30)).isoformat()
    node2 = temporal_kg.add_temporal_node(node_name2, {"type": "test2"}, 
                                          valid_from=valid_from, valid_until=valid_until)
    assert node2.valid_from is not None, "应该有开始时间"
    assert node2.valid_until is not None, "应该有结束时间"
    print("✓ 带有效期的节点创建成功")
    
    assert len(temporal_kg.temporal_nodes) == initial_node_count + 2, f"应该增加2个节点"
    print(f"✓ 时间节点数量正确: {len(temporal_kg.temporal_nodes)}")
    
    print("✓ 测试2通过!")
    return True


def test_temporal_edge_creation():
    """测试时间边创建"""
    print("\n=== 测试3: 时间边创建 ===")
    
    from core.temporal_knowledge import TemporalKnowledgeGraph
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    temporal_kg = TemporalKnowledgeGraph(kg)
    
    initial_edge_count = len(temporal_kg.temporal_edges)
    
    # 创建测试节点和边
    source_name = get_unique_name("源节点")
    target_name = get_unique_name("目标节点")
    temporal_kg.add_temporal_node(source_name)
    temporal_kg.add_temporal_node(target_name)
    
    edge = temporal_kg.add_temporal_edge(source_name, target_name, "相关", 0.8)
    assert edge is not None, "边应该能创建"
    assert edge.relation == "相关", "关系应该正确"
    assert edge.weight == 0.8, "权重应该正确"
    print("✓ 时间边创建成功")
    
    # 创建带有效期的边
    valid_from = datetime.now().isoformat()
    valid_until = (datetime.now() + timedelta(days=7)).isoformat()
    edge2 = temporal_kg.add_temporal_edge(source_name, target_name, "包含", 0.9,
                                          valid_from=valid_from, valid_until=valid_until)
    assert edge2.valid_from is not None, "边应该有开始时间"
    assert edge2.valid_until is not None, "边应该有结束时间"
    print("✓ 带有效期的边创建成功")
    
    assert len(temporal_kg.temporal_edges) == initial_edge_count + 2, "应该增加2条边"
    print(f"✓ 时间边数量正确: {len(temporal_kg.temporal_edges)}")
    
    print("✓ 测试3通过!")
    return True


def test_time_range_query():
    """测试时间范围查询"""
    print("\n=== 测试4: 时间范围查询 ===")
    
    from core.temporal_knowledge import TemporalKnowledgeGraph
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    temporal_kg = TemporalKnowledgeGraph(kg)
    
    # 创建一些测试数据
    node_a_name = get_unique_name("节点A")
    node_b_name = get_unique_name("节点B")
    
    node_a = temporal_kg.add_temporal_node(node_a_name)
    time.sleep(0.05)  # 稍微延迟一下确保时间戳不同
    node_b = temporal_kg.add_temporal_node(node_b_name)
    edge = temporal_kg.add_temporal_edge(node_a_name, node_b_name, "关联", 0.7)
    
    # 测试查询
    now = datetime.now()
    one_hour_ago = (now - timedelta(hours=1)).isoformat()
    one_hour_later = (now + timedelta(hours=1)).isoformat()
    
    nodes, edges = temporal_kg.query_by_time_range(one_hour_ago, one_hour_later)
    
    # 验证我们的测试节点在结果中
    found_a = any(n.node_id == node_a.node_id for n in nodes)
    found_b = any(n.node_id == node_b.node_id for n in nodes)
    found_edge = any(e.edge_id == edge.edge_id for e in edges)
    
    assert found_a, "节点A应该在查询结果中"
    assert found_b, "节点B应该在查询结果中"
    assert found_edge, "边应该在查询结果中"
    print("✓ 时间范围查询成功")
    
    print("✓ 测试4通过!")
    return True


def test_history_tracking():
    """测试历史记录追踪"""
    print("\n=== 测试5: 历史记录追踪 ===")
    
    from core.temporal_knowledge import TemporalKnowledgeGraph, TimeEventType
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    temporal_kg = TemporalKnowledgeGraph(kg)
    
    node_name = get_unique_name("历史测试节点")
    node = temporal_kg.add_temporal_node(node_name)
    initial_history_count = len(node.history)
    
    # 更新节点属性
    result = temporal_kg.update_node_attributes(node.node_id, {"updated": True}, "测试用户")
    assert result, "应该能更新节点属性"
    
    # 检查历史记录
    history = temporal_kg.get_node_history(node.node_id)
    assert len(history) > initial_history_count, "历史记录应该增加"
    assert any(h.event_type == TimeEventType.MODIFIED for h in history), "应该有修改事件"
    print("✓ 节点历史记录追踪成功")
    
    # 创建边并测试历史
    target_name = get_unique_name("边测试节点")
    temporal_kg.add_temporal_node(target_name)
    edge = temporal_kg.add_temporal_edge(node_name, target_name, "测试", 0.5)
    
    edge_history = temporal_kg.get_edge_history(edge.edge_id)
    assert len(edge_history) > 0, "边应该有历史记录"
    print("✓ 边历史记录追踪成功")
    
    print("✓ 测试5通过!")
    return True


def test_snapshot_functionality():
    """测试快照功能"""
    print("\n=== 测试6: 快照功能 ===")
    
    # 清理之前的测试快照
    snapshot_dir = Path("data/snapshots")
    if snapshot_dir.exists():
        shutil.rmtree(snapshot_dir)
    
    from core.temporal_knowledge import TemporalKnowledgeGraph
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    temporal_kg = TemporalKnowledgeGraph(kg)
    
    initial_node_count = len(temporal_kg.temporal_nodes)
    initial_edge_count = len(temporal_kg.temporal_edges)
    
    # 添加一些测试数据
    node1_name = get_unique_name("快照测试节点1")
    node2_name = get_unique_name("快照测试节点2")
    node1 = temporal_kg.add_temporal_node(node1_name)
    node2 = temporal_kg.add_temporal_node(node2_name)
    edge = temporal_kg.add_temporal_edge(node1_name, node2_name, "测试", 0.6)
    
    # 创建快照
    snapshot = temporal_kg.take_snapshot("测试快照", {"test": "metadata"})
    assert snapshot is not None, "快照应该能创建"
    assert snapshot.snapshot_id.startswith("snapshot_"), "快照ID格式应该正确"
    print("✓ 快照创建成功")
    
    # 列出快照
    snapshots = temporal_kg.list_snapshots()
    assert len(snapshots) >= 1, "应该有至少一个快照"
    print(f"✓ 快照列表功能正常，{len(snapshots)} 个快照")
    
    # 验证快照文件存在
    snapshot_file = snapshot_dir / f"{snapshot.snapshot_id}.json"
    assert snapshot_file.exists(), "快照文件应该存在"
    print("✓ 快照文件保存成功")
    
    print("✓ 测试6通过!")
    return True


def test_temporal_stats():
    """测试时间统计功能"""
    print("\n=== 测试7: 时间统计功能 ===")
    
    from core.temporal_knowledge import TemporalKnowledgeGraph
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    temporal_kg = TemporalKnowledgeGraph(kg)
    
    # 添加一些测试数据
    node1_name = get_unique_name("统计测试节点1")
    node2_name = get_unique_name("统计测试节点2")
    temporal_kg.add_temporal_node(node1_name)
    temporal_kg.add_temporal_node(node2_name)
    temporal_kg.add_temporal_edge(node1_name, node2_name, "相关", 0.7)
    
    stats = temporal_kg.get_temporal_stats()
    assert "total_nodes" in stats, "应该有总节点数"
    assert "total_edges" in stats, "应该有总边数"
    assert "recent_changes" in stats, "应该有最近变化统计"
    print("✓ 时间统计功能正常")
    
    print("✓ 测试7通过!")
    return True


def test_agent_integration():
    """测试Agent集成"""
    print("\n=== 测试8: Agent时间序列知识处理集成 ===")
    
    from core.agent import EternalSelfAgent
    
    agent = EternalSelfAgent(agent_id=get_unique_name("test_temporal_agent"))
    
    assert hasattr(agent, "temporal_kg"), "Agent应该有时间序列知识管理器"
    print("✓ Agent时间序列知识管理器存在")
    
    # 测试添加节点
    node_name = get_unique_name("Agent测试节点")
    node = agent.add_temporal_node(node_name, {"source": "agent"})
    assert node is not None, "应该能添加时间节点"
    print("✓ Agent添加时间节点成功")
    
    # 测试添加边
    target_name = get_unique_name("Agent测试目标节点")
    agent.add_temporal_node(target_name)
    edge = agent.add_temporal_edge(node_name, target_name, "连接", 0.8)
    assert edge is not None, "应该能添加时间边"
    print("✓ Agent添加时间边成功")
    
    # 测试统计
    stats = agent.get_temporal_stats()
    assert stats is not None, "应该能获取统计"
    print("✓ Agent时间统计获取成功")
    
    # 测试快照
    snapshot = agent.take_snapshot("Agent测试快照")
    assert snapshot is not None, "应该能创建快照"
    print("✓ Agent快照功能正常")
    
    agent.shutdown()
    
    print("✓ 测试8通过!")
    return True


def run_all_tests():
    """运行所有验收测试"""
    print("=" * 60)
    print("阶段27验收测试：时间序列知识处理")
    print("=" * 60)
    
    tests = [
        test_temporal_kg_basics,
        test_temporal_node_creation,
        test_temporal_edge_creation,
        test_time_range_query,
        test_history_tracking,
        test_snapshot_functionality,
        test_temporal_stats,
        test_agent_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n  测试失败: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
