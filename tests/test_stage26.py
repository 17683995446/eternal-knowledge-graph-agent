"""
阶段26验收测试：知识推理引擎升级
测试规则定义、匹配、推理和应用功能
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_reasoning_engine_basics():
    """测试规则推理引擎基础功能"""
    print("\n=== 测试1: 规则推理引擎基础功能 ===")
    
    from core.reasoning_engine import (
        RuleEngine,
        InferenceRule,
        RuleCondition,
        RuleType
    )
    
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    engine = RuleEngine(kg)
    
    assert engine is not None, "规则引擎应该能创建"
    print("✓ 规则引擎创建成功")
    
    assert len(engine.rules) >= 2, "应该至少有2个内置规则"
    print(f"✓ 内置规则加载成功 ({len(engine.rules)} 个规则)")
    
    stats = engine.get_inference_stats()
    assert stats["total_rules"] >= 2, "统计信息应该正确"
    assert stats["builtin_rules"] >= 2, "应该有内置规则"
    print("✓ 规则统计功能正常")
    
    print("✓ 测试1通过!")
    return True


def test_rule_definition():
    """测试规则定义和添加"""
    print("\n=== 测试2: 规则定义和添加 ===")
    
    from core.reasoning_engine import (
        RuleEngine,
        InferenceRule,
        RuleCondition,
        RuleType
    )
    
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    engine = RuleEngine(kg)
    
    rule = InferenceRule(
        rule_id="test_rule_1",
        rule_type=RuleType.IMPLICATION,
        name="测试规则",
        description="测试用的蕴含规则",
        conditions=[
            RuleCondition(node_type="concept")
        ],
        conclusions=[
            {"type": "node", "name": "InferredConcept", "attr": {"source": "inference"}}
        ],
        priority=5,
        confidence=0.8
    )
    
    success = engine.add_rule(rule)
    assert success, "规则应该能添加"
    print("✓ 自定义规则添加成功")
    
    retrieved_rule = engine.get_rule("test_rule_1")
    assert retrieved_rule is not None, "规则应该能被获取"
    assert retrieved_rule.name == "测试规则", "规则名称应该匹配"
    print("✓ 规则获取成功")
    
    all_rules = engine.get_all_rules()
    assert len(all_rules) > 2, "应该有多个规则"
    print(f"✓ 获取所有规则成功 (共 {len(all_rules)} 个)")
    
    success = engine.enable_rule("test_rule_1")
    assert success, "规则应该能启用"
    print("✓ 规则启用成功")
    
    success = engine.disable_rule("test_rule_1")
    assert success, "规则应该能禁用"
    print("✓ 规则禁用成功")
    
    success = engine.remove_rule("test_rule_1")
    assert success, "规则应该能删除"
    print("✓ 规则删除成功")
    
    print("✓ 测试2通过!")
    return True


def test_transitive_inference():
    """测试传递性推理"""
    print("\n=== 测试3: 传递性推理 ===")
    
    from core.reasoning_engine import RuleEngine
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    
    kg.add_node("A", {"node_type": "concept"})
    kg.add_node("B", {"node_type": "concept"})
    kg.add_node("C", {"node_type": "concept"})
    
    kg.add_edge("A", "B", "related_to", 0.8)
    kg.add_edge("B", "C", "related_to", 0.9)
    
    print(f"✓ 创建测试图谱: {len(kg.nodes)} 个节点, {len(kg.edges)} 条边")
    
    engine = RuleEngine(kg)
    
    results = engine.infer(focus_node="A", max_depth=3)
    
    transitive_results = [r for r in results if "传递性" in r.explanation]
    assert len(transitive_results) > 0, "应该有传递性推理结果"
    print(f"✓ 传递性推理成功，获得 {len(transitive_results)} 个结果")
    
    count = engine.apply_inference_results(results)
    assert count > 0, "应该能应用推理结果"
    print(f"✓ 应用推理结果成功，添加了 {count} 条知识")
    
    new_edge_exists = any(
        e.source == "A" and e.target == "C" and "inferred_from" in e.relation
        for e in kg.edges
    )
    assert new_edge_exists, "应该存在推理出的新边 A -> C"
    print("✓ 推理出的新边存在于知识图谱中")
    
    print("✓ 测试3通过!")
    return True


def test_symmetric_inference():
    """测试对称性推理"""
    print("\n=== 测试4: 对称性推理 ===")
    
    from core.reasoning_engine import RuleEngine
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    
    kg.add_node("Alice", {"node_type": "person"})
    kg.add_node("Bob", {"node_type": "person"})
    
    kg.add_edge("Alice", "Bob", "knows", 0.9)
    
    print(f"✓ 创建测试图谱: {len(kg.nodes)} 个节点, {len(kg.edges)} 条边")
    
    engine = RuleEngine(kg)
    
    results = engine.infer(focus_node="Alice", max_depth=2)
    
    symmetric_results = [r for r in results if "对称性" in r.explanation]
    assert len(symmetric_results) > 0, "应该有对称性推理结果"
    print(f"✓ 对称性推理成功，获得 {len(symmetric_results)} 个结果")
    
    count = engine.apply_inference_results(results)
    assert count > 0, "应该能应用推理结果"
    print(f"✓ 应用推理结果成功，添加了 {count} 条知识")
    
    reverse_edge_exists = any(
        e.source == "Bob" and e.target == "Alice" and e.relation == "knows"
        for e in kg.edges
    )
    assert reverse_edge_exists, "应该存在推理出的反向边 Bob -> Alice"
    print("✓ 推理出的反向边存在于知识图谱中")
    
    print("✓ 测试4通过!")
    return True


def test_agent_integration():
    """测试Agent推理引擎集成"""
    print("\n=== 测试5: Agent推理引擎集成 ===")
    
    from core.agent import EternalSelfAgent
    
    agent = EternalSelfAgent(agent_id="test_reasoning_agent")
    
    assert hasattr(agent, "reasoning_engine"), "Agent应该有推理引擎"
    print("✓ Agent推理引擎存在")
    
    agent.knowledge_graph.add_node("X", {"node_type": "concept"})
    agent.knowledge_graph.add_node("Y", {"node_type": "concept"})
    agent.knowledge_graph.add_node("Z", {"node_type": "concept"})
    
    agent.knowledge_graph.add_edge("X", "Y", "part_of", 0.8)
    agent.knowledge_graph.add_edge("Y", "Z", "part_of", 0.9)
    
    print(f"✓ 添加测试数据到Agent知识图谱")
    
    from core.reasoning_engine import InferenceRule, RuleCondition, RuleType
    
    custom_rule = InferenceRule(
        rule_id="agent_test_rule",
        rule_type=RuleType.IMPLICATION,
        name="Agent测试规则",
        description="Agent集成测试用规则",
        conditions=[
            RuleCondition(node_type="concept")
        ],
        conclusions=[
            {"type": "node", "name": "InferredByAgent", "attr": {"inferred": True}}
        ],
        priority=10,
        confidence=0.9
    )
    
    success = agent.add_inference_rule(custom_rule)
    assert success, "应该能添加推理规则"
    print("✓ Agent添加推理规则成功")
    
    results = agent.run_inference(focus_node="X", max_depth=3)
    assert isinstance(results, list), "应该返回推理结果列表"
    print(f"✓ Agent推理执行成功，获得 {len(results)} 个结果")
    
    if results:
        count = agent.apply_inference_results(results)
        print(f"✓ Agent应用推理结果成功，添加了 {count} 条知识")
    
    stats = agent.get_inference_stats()
    assert "total_rules" in stats, "统计信息应该完整"
    print("✓ Agent推理统计正常")
    
    added_count = agent.auto_infer_and_apply(max_depth=2)
    print(f"✓ Agent自动推理并应用成功，添加了 {added_count} 条知识")
    
    success = agent.remove_inference_rule("agent_test_rule")
    assert success, "应该能删除推理规则"
    print("✓ Agent删除推理规则成功")
    
    agent.shutdown()
    
    print("✓ 测试5通过!")
    return True


def test_rule_save_load():
    """测试规则保存和加载"""
    print("\n=== 测试6: 规则保存和加载 ===")
    
    import tempfile
    
    from core.reasoning_engine import (
        RuleEngine,
        InferenceRule,
        RuleCondition,
        RuleType
    )
    
    from core.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    engine = RuleEngine(kg)
    
    custom_rule = InferenceRule(
        rule_id="save_test_rule",
        rule_type=RuleType.IMPLICATION,
        name="保存测试规则",
        description="测试规则保存和加载",
        conditions=[
            RuleCondition(node_type="concept")
        ],
        conclusions=[
            {"type": "node", "name": "SavedNode", "attr": {"source": "test"}}
        ],
        priority=7,
        confidence=0.85
    )
    
    engine.add_rule(custom_rule)
    print("✓ 添加测试规则")
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_path = temp_file.name
    temp_file.close()
    
    try:
        success = engine.save_rules(temp_path)
        assert success, "规则应该能保存"
        print("✓ 规则保存成功")
        
        kg2 = KnowledgeGraph()
        engine2 = RuleEngine(kg2)
        
        initial_count = len(engine2.rules)
        
        success = engine2.load_rules(temp_path)
        assert success, "规则应该能加载"
        print("✓ 规则加载成功")
        
        assert len(engine2.rules) > initial_count, "加载后规则数量应该增加"
        print(f"✓ 规则加载后数量正确 ({initial_count} -> {len(engine2.rules)})")
        
        loaded_rule = engine2.get_rule("save_test_rule")
        assert loaded_rule is not None, "应该能获取加载的规则"
        assert loaded_rule.name == "保存测试规则", "规则名称应该匹配"
        print("✓ 加载的规则内容正确")
        
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    print("✓ 测试6通过!")
    return True


def run_all_tests():
    """运行所有验收测试"""
    print("=" * 60)
    print("阶段26验收测试：知识推理引擎升级")
    print("=" * 60)
    
    tests = [
        test_reasoning_engine_basics,
        test_rule_definition,
        test_transitive_inference,
        test_symmetric_inference,
        test_agent_integration,
        test_rule_save_load
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
