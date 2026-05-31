
import os
import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def get_unique_name(base):
    """生成唯一的名称"""
    return base + "_" + str(int(time.time() * 1000000)) + "_" + str(random.randint(1000, 9999))


def test_conflict_resolver_basics():
    """测试冲突解决器基础功能"""
    print("\n=== 测试1: 冲突解决器基础功能 ===")
    
    from core.knowledge_conflict_resolver import KnowledgeConflictResolver
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    resolver = KnowledgeConflictResolver(kg)
    
    assert resolver is not None, "冲突解决器应该能创建"
    print("✓ 冲突解决器创建成功")
    
    stats = resolver.get_conflict_stats()
    assert 'total_conflicts' in stats, "统计信息应该包含总冲突数"
    assert stats['total_conflicts'] == 0, "初始冲突数应该为0"
    print("✓ 统计功能正常")
    
    print("✓ 测试1通过!")
    return True


def test_duplicate_node_detection():
    """测试重复节点检测"""
    print("\n=== 测试2: 重复节点检测 ===")
    
    from core.knowledge_conflict_resolver import KnowledgeConflictResolver, ConflictType
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    resolver = KnowledgeConflictResolver(kg)
    
    node_name = get_unique_name("TestNode")
    
    node1 = kg.add_node(node_name, {"attr1": "value1"})
    
    from core.knowledge_graph import Node
    node2 = Node(node_name, {"attr1": "value2"})
    kg.nodes[node2.id] = node2
    
    conflicts = resolver.detect_all_conflicts()
    
    duplicate_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.DUPLICATE_NODE]
    assert len(duplicate_conflicts) >= 1, "应该检测到重复节点冲突"
    print("✓ 重复节点检测成功")
    
    print("✓ 测试2通过!")
    return True


def test_duplicate_edge_detection():
    """测试重复边检测"""
    print("\n=== 测试3: 重复边检测 ===")
    
    from core.knowledge_conflict_resolver import KnowledgeConflictResolver, ConflictType
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    resolver = KnowledgeConflictResolver(kg)
    
    source_name = get_unique_name("SourceNode")
    target_name = get_unique_name("TargetNode")
    kg.add_node(source_name)
    kg.add_node(target_name)
    
    kg.add_edge(source_name, target_name, "related_to", 0.8)
    kg.add_edge(source_name, target_name, "related_to", 0.6)
    
    conflicts = resolver.detect_all_conflicts()
    duplicate_edges = [c for c in conflicts if c.conflict_type == ConflictType.DUPLICATE_EDGE]
    assert len(duplicate_edges) >= 1, "应该检测到重复边冲突"
    print("✓ 重复边检测成功")
    
    print("✓ 测试3通过!")
    return True


def test_conflicting_edge_detection():
    """测试冲突边检测"""
    print("\n=== 测试4: 冲突边检测 ===")
    
    from core.knowledge_conflict_resolver import KnowledgeConflictResolver, ConflictType
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    resolver = KnowledgeConflictResolver(kg)
    
    source_name = get_unique_name("SourceNode")
    target_name = get_unique_name("TargetNode")
    kg.add_node(source_name)
    kg.add_node(target_name)
    
    kg.add_edge(source_name, target_name, "is_a", 0.9)
    kg.add_edge(source_name, target_name, "related_to", 0.7)
    
    conflicts = resolver.detect_all_conflicts()
    conflicting_edges = [c for c in conflicts if c.conflict_type == ConflictType.CONFLICTING_EDGE]
    assert len(conflicting_edges) >= 1, "应该检测到冲突边"
    print("✓ 冲突边检测成功")
    
    print("✓ 测试4通过!")
    return True


def test_agent_integration():
    """测试Agent集成"""
    print("\n=== 测试5: Agent集成 ===")
    
    from core.agent import EternalSelfAgent
    
    agent = EternalSelfAgent(agent_id=get_unique_name("test_conflict_agent"))
    
    assert hasattr(agent, 'conflict_resolver'), "Agent应该有冲突解决器"
    print("✓ Agent冲突解决器存在")
    
    node_name = get_unique_name("AgentTestNode")
    agent.knowledge_graph.add_node(node_name, {"type": "test"})
    
    from core.knowledge_graph import Node
    duplicate_node = Node(node_name, {"type": "conflict"})
    agent.knowledge_graph.nodes[duplicate_node.id] = duplicate_node
    
    conflicts = agent.detect_conflicts()
    assert conflicts is not None, "应该能检测到冲突"
    print(f"✓ Agent检测冲突成功")
    
    results = agent.resolve_conflicts()
    assert results is not None, "应该能解决冲突"
    print(f"✓ Agent解决冲突成功")
    
    stats = agent.get_conflict_stats()
    assert stats is not None, "应该能获取冲突统计"
    print("✓ Agent冲突统计获取成功")
    
    agent.shutdown()
    
    print("✓ 测试5通过!")
    return True


def run_all_tests():
    """运行所有验收测试"""
    print("=" * 60)
    print("阶段28验收测试：知识冲突检测与解决")
    print("=" * 60)
    
    tests = [
        test_conflict_resolver_basics,
        test_duplicate_node_detection,
        test_duplicate_edge_detection,
        test_conflicting_edge_detection,
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
