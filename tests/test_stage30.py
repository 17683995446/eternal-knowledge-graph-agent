
import os
import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def get_unique_name(base):
    return base + "_" + str(int(time.time() * 1000000)) + "_" + str(random.randint(1000, 9999))


def test_version_manager_basics():
    """测试版本管理器基础功能"""
    print("\n=== 测试1: 版本管理器基础功能 ===")
    
    from core.knowledge_version_manager import KnowledgeVersionManager
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    version_manager = KnowledgeVersionManager(kg)
    
    assert version_manager is not None, "版本管理器应该能创建"
    print("✓ 版本管理器创建成功")
    
    stats = version_manager.get_version_stats()
    assert "total_versions" in stats, "统计应该包含总版本数"
    assert "snapshot_count" in stats, "统计应该包含快照数"
    print("✓ 版本统计功能正常")
    
    print("✓ 测试1通过!")
    return True


def test_node_creation_recording():
    """测试节点创建记录"""
    print("\n=== 测试2: 节点创建记录 ===")
    
    from core.knowledge_version_manager import KnowledgeVersionManager, VersionAction
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    version_manager = KnowledgeVersionManager(kg)
    
    initial_version_count = len(version_manager.versions)
    
    node_name = get_unique_name("TestNode")
    node = kg.add_node(node_name)
    
    version = version_manager.record_node_creation(node, "Test node creation")
    
    assert version is not None, "应该能记录版本"
    assert version.action == VersionAction.CREATE, "操作类型应该是CREATE"
    assert version.knowledge_type == "node", "知识类型应该是node"
    assert version.new_state is not None, "新状态不应该为空"
    print("✓ 节点创建记录成功")
    
    assert len(version_manager.versions) == initial_version_count + 1, "版本数应该增加"
    print("✓ 版本列表更新成功")
    
    print("✓ 测试2通过!")
    return True


def test_snapshot_creation():
    """测试快照创建"""
    print("\n=== 测试3: 快照创建 ===")
    
    from core.knowledge_version_manager import KnowledgeVersionManager
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    version_manager = KnowledgeVersionManager(kg)
    
    snapshot_name = get_unique_name("TestSnapshot")
    snapshot = version_manager.create_snapshot(snapshot_name, "Test snapshot")
    
    assert snapshot is not None, "应该能创建快照"
    assert snapshot.snapshot_name == snapshot_name, "快照名称应该匹配"
    assert snapshot.node_count == len(kg.nodes), "节点数应该匹配"
    assert snapshot.edge_count == len(kg.edges), "边数应该匹配"
    print("✓ 快照创建成功")
    
    snapshots = version_manager.get_snapshots()
    assert len(snapshots) >= 1, "应该至少有1个快照"
    print(f"✓ 快照列表更新成功 ({len(snapshots)} 个快照)")
    
    print("✓ 测试3通过!")
    return True


def test_version_history():
    """测试版本历史查询"""
    print("\n=== 测试4: 版本历史查询 ===")
    
    from core.knowledge_version_manager import KnowledgeVersionManager
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    version_manager = KnowledgeVersionManager(kg)
    
    node_name = get_unique_name("HistoryTestNode")
    node = kg.add_node(node_name)
    version_manager.record_node_creation(node, "Creating node for history test")
    
    history = version_manager.get_version_history()
    assert len(history) > 0, "应该有版本历史"
    print(f"✓ 版本历史查询成功 ({len(history)} 条记录)")
    
    history_for_node = version_manager.get_version_history(knowledge_id=node.id)
    assert len(history_for_node) > 0, "应该有该节点的版本历史"
    print("✓ 按节点查询版本历史成功")
    
    print("✓ 测试4通过!")
    return True


def test_agent_integration():
    """测试Agent集成"""
    print("\n=== 测试5: Agent集成 ===")
    
    from core.agent import EternalSelfAgent
    
    agent = EternalSelfAgent(agent_id=get_unique_name("test_version_agent"))
    
    assert hasattr(agent, 'version_manager'), "Agent应该有版本管理器"
    print("✓ Agent版本管理器存在")
    
    snapshot_name = get_unique_name("AgentSnapshot")
    snapshot = agent.create_version_snapshot(snapshot_name, "Agent test snapshot")
    assert snapshot is not None, "应该能创建快照"
    print("✓ Agent创建快照成功")
    
    snapshots = agent.get_all_snapshots()
    assert len(snapshots) >= 1, "应该至少有1个快照"
    print("✓ Agent获取快照列表成功")
    
    history = agent.get_version_history()
    assert history is not None, "应该能获取版本历史"
    print("✓ Agent获取版本历史成功")
    
    stats = agent.get_version_stats()
    assert stats is not None, "应该能获取版本统计"
    assert "total_versions" in stats, "统计应该包含总版本数"
    print("✓ Agent获取版本统计成功")
    
    agent.shutdown()
    
    print("✓ 测试5通过!")
    return True


def run_all_tests():
    """运行所有验收测试"""
    print("=" * 60)
    print("阶段30验收测试: 知识版本管理与回滚")
    print("=" * 60)
    
    tests = [
        test_version_manager_basics,
        test_node_creation_recording,
        test_snapshot_creation,
        test_version_history,
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
