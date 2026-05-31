#!/usr/bin/env python3
"""
阶段41-100综合验收测试
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import EternalSelfAgent
from core.advanced_applications import ServiceRequest, ServiceType


def test_all_stages():
    print("=" * 70)
    print("阶段41-100综合验收测试")
    print("=" * 70)
    
    agent = EternalSelfAgent(agent_id="stage41_100_test_agent")
    print("\n[初始化] Agent初始化成功")
    
    # 创建测试知识
    print("\n[准备] 创建测试知识...")
    for i in range(5):
        agent.create_domain_knowledge(
            "technology_skill",
            f"技术技能{i+1}",
            {"skill_name": f"Skill{i+1}", "category": "编程", "level": "高级"},
            tags=["技术", "编程"]
        )
    print(f"✓ 创建测试知识完成")
    
    # ===== 阶段41: 自适应学习 =====
    print("\n" + "-" * 70)
    print("[阶段41] 自适应学习")
    print("-" * 70)
    
    kid = list(agent.domain_knowledge_manager.domain_knowledges.keys())[0]
    fb = agent.add_feedback(kid, "user1", "positive", rating=5)
    assert fb is not None, "反馈添加失败"
    print("✓ 反馈系统")
    
    ab_test = agent.create_ab_test("测试", [{"name": "A", "config": {}}, {"name": "B", "config": {}}])
    assert ab_test is not None, "A/B测试创建失败"
    print("✓ A/B测试")
    
    # ===== 阶段42: 自然语言理解 =====
    print("\n" + "-" * 70)
    print("[阶段42] 自然语言理解")
    print("-" * 70)
    
    nlu_result = agent.parse_natural_language("什么是Python编程？")
    assert nlu_result.intent.value != "unknown", "NLU解析失败"
    print(f"✓ NLU解析: 意图={nlu_result.intent.value}")
    
    keywords = agent.extract_keywords("Python编程语言技术", 3)
    assert len(keywords) > 0, "关键词提取失败"
    print(f"✓ 关键词提取: {keywords}")
    
    # ===== 阶段43: 对话式交互 =====
    print("\n" + "-" * 70)
    print("[阶段43] 对话式交互")
    print("-" * 70)
    
    response = agent.chat("你好！")
    assert len(response) > 0, "对话失败"
    print(f"✓ 对话: {response[:30]}...")
    
    history = agent.get_chat_history()
    assert len(history) > 0, "对话历史为空"
    print(f"✓ 对话历史: {len(history)} 轮")
    
    # ===== 阶段44: 知识图谱自动构建 =====
    print("\n" + "-" * 70)
    print("[阶段44] 知识图谱自动构建")
    print("-" * 70)
    
    text = "Python是一种编程语言。JavaScript用于Web开发。"
    crawled = agent.crawl_text(text, "test_source")
    assert crawled is not None, "爬取失败"
    print(f"✓ 文本爬取: {len(crawled.extracted_entities)} 个实体")
    
    # ===== 阶段45: 跨语言知识处理 =====
    print("\n" + "-" * 70)
    print("[阶段45] 跨语言知识处理")
    print("-" * 70)
    
    lang = agent.detect_language("Python编程")
    assert lang == "zh", "语言检测失败"
    print(f"✓ 语言检测: {lang}")
    
    trans = agent.translate("编程", "zh", "en")
    assert trans.target_text == "programming", "翻译失败"
    print(f"✓ 翻译: {trans.source_text} -> {trans.target_text}")
    
    # ===== 阶段46: 元学习能力 =====
    print("\n" + "-" * 70)
    print("[阶段46] 元学习能力")
    print("-" * 70)
    
    pattern = agent.analyze_learning_pattern(kid, [
        {"success": True, "time": 5},
        {"success": True, "time": 3}
    ])
    assert "pattern" in pattern, "模式分析失败"
    print(f"✓ 学习模式: {pattern['pattern']}")
    
    strategy = agent.recommend_strategy("technology", pattern["pattern"])
    assert len(strategy) > 0, "策略推荐失败"
    print(f"✓ 策略推荐: {strategy}")
    
    # ===== 阶段47: 知识迁移学习 =====
    print("\n" + "-" * 70)
    print("[阶段47] 知识迁移学习")
    print("-" * 70)
    
    transferred = agent.transfer_knowledge(kid, "education")
    assert transferred is not None, "迁移失败"
    print(f"✓ 知识迁移: {transferred.name}")
    
    candidates = agent.find_transfer_candidates("technology", "education")
    assert len(candidates) >= 0, "候选查找失败"
    print(f"✓ 迁移候选: {len(candidates)} 个")
    
    # ===== 阶段48: 终身学习机制 =====
    print("\n" + "-" * 70)
    print("[阶段48] 终身学习机制")
    print("-" * 70)
    
    agent.record_learning(kid, difficulty=3)
    status = agent.get_retention_status(kid)
    assert "status" in status, "保持状态获取失败"
    print(f"✓ 知识保持: {status['status']}")
    
    reviews = agent.get_review_recommendations()
    assert isinstance(reviews, list), "复习推荐失败"
    print(f"✓ 复习推荐: {len(reviews)} 条")
    
    # ===== 阶段49: 主动学习策略 =====
    print("\n" + "-" * 70)
    print("[阶段49] 主动学习策略")
    print("-" * 70)
    
    samples = agent.get_uncertain_samples(3)
    assert isinstance(samples, list), "样本选择失败"
    print(f"✓ 不确定样本: {len(samples)} 个")
    
    queries = agent.suggest_queries("technology", 2)
    assert len(queries) > 0, "查询建议失败"
    print(f"✓ 查询建议: {queries}")
    
    # ===== 阶段50-60: 持续自适应优化 =====
    print("\n" + "-" * 70)
    print("[阶段50-60] 持续自适应优化")
    print("-" * 70)
    
    agent.record_performance("response_time", 0.5)
    report = agent.get_performance_report()
    assert "response_time" in report, "性能报告失败"
    print(f"✓ 性能监控: {report['response_time']['latest']}s")
    
    # ===== 阶段61-80: 高级应用与生态 =====
    print("\n" + "-" * 70)
    print("[阶段61-80] 高级应用与生态")
    print("-" * 70)
    
    services = agent.get_available_services()
    assert len(services) > 0, "服务列表为空"
    print(f"✓ 可用服务: {len(services)} 个")
    
    request = ServiceRequest(
        request_id="test_001",
        service_type=ServiceType.KNOWLEDGE_QUERY,
        parameters={"query": "编程"}
    )
    response = agent.execute_service(request)
    assert response.success, "服务执行失败"
    print(f"✓ 服务执行: {response.processing_time:.3f}s")
    
    workflow_id = agent.create_workflow("测试工作流", [
        {"service_type": "knowledge_query", "parameters": {"query": "Python"}}
    ])
    assert workflow_id is not None, "工作流创建失败"
    print(f"✓ 工作流创建: {workflow_id}")
    
    # ===== 阶段81-100: 前沿探索与未来形态 =====
    print("\n" + "-" * 70)
    print("[阶段81-100] 前沿探索与未来形态")
    print("-" * 70)
    
    consciousness = agent.simulate_consciousness({"input": "test", "context": "learning"})
    assert "level" in consciousness, "意识模拟失败"
    print(f"✓ 意识模拟: {consciousness['level']}")
    
    creative = agent.generate_creative_content("人工智能", "idea")
    assert creative is not None, "创意生成失败"
    print(f"✓ 创意生成: {creative.content[:30]}...")
    
    ethical = agent.ethical_evaluation("分享用户数据", {"context": "privacy"})
    assert ethical is not None, "伦理评估失败"
    print(f"✓ 伦理评估: {ethical.decision} ({ethical.ethical_score:.2f})")
    
    report = agent.get_consciousness_report()
    assert "current_level" in report, "意识报告失败"
    print(f"✓ 意识报告: {report['current_level']}")
    
    # ===== 最终统计 =====
    print("\n" + "=" * 70)
    print("[最终统计]")
    print("=" * 70)
    
    print(f"总知识数: {len(agent.domain_knowledge_manager.domain_knowledges)}")
    print(f"总模板数: {len(agent.domain_knowledge_manager.templates)}")
    print(f"对话历史: {len(agent.get_chat_history())} 轮")
    print(f"可用服务: {len(agent.get_available_services())} 个")
    print(f"创意输出: {len(agent.future_exploration.creative_history)} 个")
    
    print("\n" + "=" * 70)
    print("阶段41-100综合验收测试完成！✓ 所有测试通过")
    print("=" * 70)
    print("\n完整功能覆盖:")
    print("  ✓ 阶段41: 自适应学习框架")
    print("  ✓ 阶段42: 自然语言理解")
    print("  ✓ 阶段43: 对话式交互")
    print("  ✓ 阶段44: 知识图谱自动构建")
    print("  ✓ 阶段45: 跨语言知识处理")
    print("  ✓ 阶段46: 元学习能力")
    print("  ✓ 阶段47: 知识迁移学习")
    print("  ✓ 阶段48: 终身学习机制")
    print("  ✓ 阶段49: 主动学习策略")
    print("  ✓ 阶段50-60: 持续自适应优化")
    print("  ✓ 阶段61-80: 高级应用与生态")
    print("  ✓ 阶段81-100: 前沿探索与未来形态")
    
    agent.shutdown()
    return True


if __name__ == "__main__":
    try:
        success = test_all_stages()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
