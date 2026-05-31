
import os
import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def get_unique_name(base):
    return base + "_" + str(int(time.time() * 1000000)) + "_" + str(random.randint(1000, 9999))


def test_verifier_basics():
    """测试验证器基础功能"""
    print("\n=== 测试1: 验证器基础功能 ===")
    
    from core.knowledge_verifier import KnowledgeVerifier, KnowledgeSource, VerificationStatus
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    verifier = KnowledgeVerifier(kg)
    
    assert verifier is not None, "验证器应该能创建"
    print("✓ 验证器创建成功")
    
    stats = verifier.get_verification_stats()
    assert "total_nodes" in stats, "统计应该包含节点总数"
    assert "source_count" in stats, "统计应该包含来源数"
    print("✓ 统计功能正常")
    
    print("✓ 测试1通过!")
    return True


def test_source_credibility():
    """测试来源可信度"""
    print("\n=== 测试2: 来源可信度管理 ===")
    
    from core.knowledge_verifier import KnowledgeVerifier, KnowledgeSource
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    verifier = KnowledgeVerifier(kg)
    
    source_id = "test_source_1"
    verifier.register_source(source_id, KnowledgeSource.USER_INPUT, 0.7)
    
    credibility = verifier.get_source_credibility(source_id)
    assert abs(credibility - 0.7) < 0.01, "初始可信度应该是0.7"
    print("✓ 来源注册成功")
    
    verifier.update_source_credibility(source_id, True)
    new_credibility = verifier.get_source_credibility(source_id)
    assert new_credibility > 0.7, "可信度应该增加"
    print("✓ 成功验证会增加可信度")
    
    verifier.update_source_credibility(source_id, False)
    final_credibility = verifier.get_source_credibility(source_id)
    assert final_credibility < new_credibility, "失败验证会降低可信度"
    print("✓ 失败验证会降低可信度")
    
    print("✓ 测试2通过!")
    return True


def test_node_verification():
    """测试节点验证"""
    print("\n=== 测试3: 节点验证 ===")
    
    from core.knowledge_verifier import KnowledgeVerifier, VerificationStatus
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    verifier = KnowledgeVerifier(kg)
    
    node_name = get_unique_name("TestNode")
    node = kg.add_node(node_name, {"source_id": "test_source"})
    
    confidence = verifier.verify_node(node)
    
    assert confidence is not None, "验证应该返回置信度对象"
    assert confidence.knowledge_type == "node", "知识类型应该是node"
    assert 0.0 <= confidence.confidence <= 1.0, "置信度应该在0-1之间"
    assert confidence.verification_status in VerificationStatus, "验证状态应该有效"
    print("✓ 节点验证成功")
    
    stats = verifier.get_verification_stats()
    assert stats["total_nodes"] >= 1, "应该有至少一个节点"
    print("✓ 验证统计更新成功")
    
    print("✓ 测试3通过!")
    return True


def test_edge_verification():
    """测试边验证"""
    print("\n=== 测试4: 边验证 ===")
    
    from core.knowledge_verifier import KnowledgeVerifier, VerificationStatus
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    verifier = KnowledgeVerifier(kg)
    
    source_name = get_unique_name("SourceNode")
    target_name = get_unique_name("TargetNode")
    
    kg.add_node(source_name)
    kg.add_node(target_name)
    
    edge = kg.add_edge(source_name, target_name, "related_to", 0.8)
    
    confidence = verifier.verify_edge(edge)
    
    assert confidence is not None, "验证应该返回置信度对象"
    assert confidence.knowledge_type == "edge", "知识类型应该是edge"
    assert 0.0 <= confidence.confidence <= 1.0, "置信度应该在0-1之间"
    print("✓ 边验证成功")
    
    stats = verifier.get_verification_stats()
    assert stats["total_edges"] >= 1, "应该有至少一条边"
    print("✓ 验证统计更新成功")
    
    print("✓ 测试4通过!")
    return True


def test_confidence_update():
    """测试置信度更新"""
    print("\n=== 测试5: 置信度更新 ===")
    
    from core.knowledge_verifier import KnowledgeVerifier
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    verifier = KnowledgeVerifier(kg)
    
    node_name = get_unique_name("TestNode")
    node = kg.add_node(node_name)
    
    confidence = verifier.verify_node(node)
    initial_confidence = confidence.confidence
    
    success = verifier.update_confidence(confidence.knowledge_id, 0.85, "Manual adjustment")
    assert success, "应该能更新置信度"
    print("✓ 置信度更新成功")
    
    updated_confidence = verifier.get_knowledge_confidence(confidence.knowledge_id)
    assert abs(updated_confidence.confidence - 0.85) < 0.01, "置信度应该被更新"
    print("✓ 更新后的置信度正确")
    
    print("✓ 测试5通过!")
    return True


def test_agent_integration():
    """测试Agent集成"""
    print("\n=== 测试6: Agent集成 ===")
    
    from core.agent import EternalSelfAgent
    from core.knowledge_verifier import KnowledgeSource
    
    agent = EternalSelfAgent(agent_id=get_unique_name("test_verifier_agent"))
    
    assert hasattr(agent, 'knowledge_verifier'), "Agent应该有知识验证器"
    print("✓ Agent知识验证器存在")
    
    agent.register_knowledge_source("test_integration", KnowledgeSource.USER_INPUT, 0.75)
    print("✓ 知识来源注册成功")
    
    node_name = get_unique_name("AgentTestNode")
    agent.knowledge_graph.add_node(node_name, {"source_id": "test_integration"})
    
    confidence_results = agent.verify_all_knowledge()
    assert confidence_results is not None, "应该能验证知识"
    print(f"✓ 知识验证成功: {len(confidence_results)} 个结果")
    
    stats = agent.get_knowledge_verification_stats()
    assert stats is not None, "应该能获取验证统计"
    print("✓ 验证统计获取成功")
    
    agent.shutdown()
    
    print("✓ 测试6通过!")
    return True


def run_all_tests():
    """运行所有验收测试"""
    print("=" * 60)
    print("阶段29验收测试: 知识验证与置信度评分")
    print("=" * 60)
    
    tests = [
        test_verifier_basics,
        test_source_credibility,
        test_node_verification,
        test_edge_verification,
        test_confidence_update,
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
