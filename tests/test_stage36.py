#!/usr/bin/env python3
"""
阶段36验收测试：领域知识质量评估与优化
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import EternalSelfAgent


def test_stage36():
    print("=" * 60)
    print("阶段36验收测试：领域知识质量评估与优化")
    print("=" * 60)
    
    agent = EternalSelfAgent(agent_id="stage36_test_agent")
    print("\n[1/5] Agent初始化成功")
    
    # 创建测试知识（有缺陷的）
    print("\n[2/5] 创建测试知识...")
    
    # 高质量知识
    good_knowledge = agent.create_domain_knowledge(
        "technology_skill",
        "Python高级编程指南",
        {
            "skill_name": "Python",
            "category": "编程语言",
            "level": "高级",
            "prerequisites": ["基础编程"],
            "applications": ["Web开发", "数据分析", "AI"]
        },
        tags=["技术", "编程", "Python"],
        sources=["官方文档", "实践经验"]
    )
    
    # 低质量知识（缺少字段和标签）
    poor_knowledge = agent.create_domain_knowledge(
        "technology_skill",
        "JS",
        {"skill_name": "JavaScript", "category": "编程", "level": "初级"},
        tags=["技术"]
    )
    
    print(f"✓ 创建 {len(agent.domain_knowledge_manager.domain_knowledges)} 条知识")
    
    # 测试单条知识评估
    print("\n[3/5] 测试单条知识质量评估...")
    report = agent.evaluate_knowledge_quality(good_knowledge.knowledge_id)
    assert report is not None, "评估失败"
    print(f"✓ '{good_knowledge.name}' 质量评估:")
    print(f"  总分: {report.overall_score}")
    print(f"  等级: {report.quality_level.value}")
    print(f"  完整性: {report.completeness_score}")
    print(f"  准确性: {report.accuracy_score}")
    print(f"  一致性: {report.consistency_score}")
    print(f"  新鲜度: {report.freshness_score}")
    
    poor_report = agent.evaluate_knowledge_quality(poor_knowledge.knowledge_id)
    assert poor_report is not None, "评估失败"
    print(f"\n✓ '{poor_knowledge.name}' 质量评估:")
    print(f"  总分: {poor_report.overall_score}")
    print(f"  等级: {poor_report.quality_level.value}")
    print(f"  问题数: {len(poor_report.issues)}")
    for issue in poor_report.issues[:3]:
        print(f"    - [{issue['severity']}] {issue['message']}")
    
    # 测试批量评估
    print("\n[4/5] 测试批量评估...")
    metrics = agent.batch_evaluate_quality()
    assert metrics.total_knowledges > 0, "批量评估失败"
    print(f"✓ 批量评估完成:")
    print(f"  总知识数: {metrics.total_knowledges}")
    print(f"  平均质量分: {metrics.avg_quality_score}")
    print(f"  质量分布: {metrics.quality_distribution}")
    print(f"  平均完整性: {metrics.completeness_avg}")
    print(f"  平均准确性: {metrics.accuracy_avg}")
    
    # 测试低质量知识获取
    print("\n[5/5] 测试低质量知识获取和优化计划...")
    low_quality = agent.get_low_quality_knowledges(threshold=0.8)
    print(f"✓ 低质量知识: {len(low_quality)} 条")
    
    # 测试优化计划
    plan = agent.generate_optimization_plan()
    assert plan is not None, "优化计划生成失败"
    print(f"✓ 优化计划生成完成:")
    print(f"  待优化项: {plan['total_issues']}")
    print(f"  优先行动: {len(plan['priority_actions'])} 项")
    if plan['suggestions']:
        print(f"  主要建议: {plan['suggestions'][0]['action']} ({plan['suggestions'][0]['count']} 次)")
    
    print("\n" + "=" * 60)
    print("阶段36验收测试完成！✓ 所有测试通过")
    print("=" * 60)
    print("\n功能覆盖:")
    print("  ✓ 单条知识质量评估")
    print("  ✓ 完整性评估")
    print("  ✓ 准确性评估")
    print("  ✓ 一致性评估")
    print("  ✓ 新鲜度评估")
    print("  ✓ 批量评估")
    print("  ✓ 低质量知识识别")
    print("  ✓ 优化计划生成")
    print("  ✓ Agent集成")
    
    agent.shutdown()
    return True


if __name__ == "__main__":
    try:
        success = test_stage36()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
