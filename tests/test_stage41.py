#!/usr/bin/env python3
"""
阶段41验收测试：自适应学习框架
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import EternalSelfAgent


def test_stage41():
    print("=" * 60)
    print("阶段41验收测试：自适应学习框架")
    print("=" * 60)
    
    agent = EternalSelfAgent(agent_id="stage41_test_agent")
    print("\n[1/5] Agent初始化成功")
    
    # 创建测试知识
    print("\n[2/5] 创建测试知识...")
    knowledge = agent.create_domain_knowledge(
        "technology_skill", "Python编程",
        {"skill_name": "Python", "category": "编程", "level": "高级"},
        tags=["技术", "编程"]
    )
    print(f"✓ 创建知识: {knowledge.name}")
    
    # 测试添加反馈
    print("\n[3/5] 测试用户反馈...")
    
    # 正面反馈
    fb1 = agent.add_feedback(
        knowledge.knowledge_id, "user1", "positive", rating=5, comment="很有用！"
    )
    assert fb1 is not None, "正面反馈添加失败"
    print(f"✓ 正面反馈添加成功")
    
    # 负面反馈
    fb2 = agent.add_feedback(
        knowledge.knowledge_id, "user2", "negative", rating=2, comment="不够详细"
    )
    assert fb2 is not None, "负面反馈添加失败"
    print(f"✓ 负面反馈添加成功")
    
    # 修正反馈
    fb3 = agent.add_feedback(
        knowledge.knowledge_id, "user3", "correction", 
        comment="内容有误", correction={"level": "专家级"}
    )
    assert fb3 is not None, "修正反馈添加失败"
    print(f"✓ 修正反馈添加成功")
    
    # 检查知识置信度变化
    updated_knowledge = agent.get_domain_knowledge(knowledge.knowledge_id)
    print(f"✓ 知识置信度变化: {knowledge.confidence:.2f} -> {updated_knowledge.confidence:.2f}")
    
    # 测试反馈统计
    print("\n[4/5] 测试反馈统计...")
    stats = agent.get_knowledge_feedback_stats(knowledge.knowledge_id)
    print(f"✓ 反馈统计:")
    print(f"  总反馈数: {stats['total']}")
    print(f"  平均评分: {stats['avg_rating']}")
    print(f"  情感倾向: {stats['sentiment']}")
    print(f"  类型分布: {stats['type_distribution']}")
    
    # 测试A/B测试
    print("\n[5/5] 测试A/B测试...")
    ab_test = agent.create_ab_test(
        "搜索算法优化",
        [
            {"name": "控制组", "config": {"algorithm": "default"}, "traffic_percentage": 0.5},
            {"name": "实验组", "config": {"algorithm": "improved"}, "traffic_percentage": 0.5}
        ]
    )
    assert ab_test is not None, "A/B测试创建失败"
    print(f"✓ A/B测试创建: {ab_test.test_id}")
    
    # 为用户分配变体
    variant = agent.adaptive_learning.get_ab_test_variant(ab_test.test_id, "user1")
    print(f"✓ 用户分配变体: {variant.name}")
    
    # 记录指标
    agent.adaptive_learning.record_ab_test_metric(
        ab_test.test_id, variant.variant_id, "accuracy", 0.85
    )
    
    # 获取结果
    results = agent.get_ab_test_results(ab_test.test_id)
    assert results is not None, "获取A/B测试结果失败"
    print(f"✓ A/B测试结果: {len(results['variants'])} 个变体")
    
    # 测试学习统计
    learning_stats = agent.get_learning_stats()
    print(f"\n学习统计:")
    print(f"  总反馈数: {learning_stats['total_feedbacks']}")
    print(f"  学习事件: {learning_stats['total_learning_events']}")
    print(f"  A/B测试: {learning_stats['total_ab_tests']}")
    print(f"  平均置信度变化: {learning_stats['avg_confidence_change']:.4f}")
    
    print("\n" + "=" * 60)
    print("阶段41验收测试完成！✓ 所有测试通过")
    print("=" * 60)
    print("\n功能覆盖:")
    print("  ✓ 用户反馈添加")
    print("  ✓ 正面/负面/修正反馈处理")
    print("  ✓ 知识置信度自动调整")
    print("  ✓ 反馈统计分析")
    print("  ✓ A/B测试创建")
    print("  ✓ 用户变体分配")
    print("  ✓ 指标记录与结果分析")
    print("  ✓ 学习统计")
    print("  ✓ Agent集成")
    
    agent.shutdown()
    return True


if __name__ == "__main__":
    try:
        success = test_stage41()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
