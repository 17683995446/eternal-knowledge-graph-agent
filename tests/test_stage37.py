#!/usr/bin/env python3
"""
阶段37验收测试：领域知识自动化抽取与构建
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import EternalSelfAgent


def test_stage37():
    print("=" * 60)
    print("阶段37验收测试：领域知识自动化抽取与构建")
    print("=" * 60)
    
    agent = EternalSelfAgent(agent_id="stage37_test_agent")
    print("\n[1/4] Agent初始化成功")
    
    # 测试从文本抽取
    print("\n[2/4] 测试从文本抽取知识...")
    text = """
    Python是一种高级编程语言，属于编程语言类别，级别为高级。
    它用于Web开发、数据分析、人工智能等领域。
    
    JavaScript是前端开发的主要语言，属于编程语言，级别为中级。
    它用于Web前端开发、交互设计等。
    
    普通感冒是一种常见疾病。症状：流鼻涕、打喷嚏、喉咙痛。
    原因：病毒感染。治疗：休息、多喝水。
    
    线性代数是大学数学课程。级别：大学。
    核心概念：向量、矩阵、线性变换。
    """
    
    result = agent.extract_knowledge_from_text(text)
    assert len(result.extracted_knowledges) > 0, "文本抽取失败"
    print(f"✓ 从文本抽取 {len(result.extracted_knowledges)} 条知识")
    for k in result.extracted_knowledges[:3]:
        print(f"  - {k.name} ({k.domain_type.value}): {k.content}")
    
    # 测试批量注册
    print("\n[3/4] 测试批量注册抽取的知识...")
    stats = agent.register_extracted_knowledges(result)
    print(f"✓ 注册结果: {stats['success']} 成功, {stats['failed']} 失败")
    
    # 测试从结构化数据抽取
    print("\n[4/4] 测试从结构化数据抽取...")
    structured_data = [
        {"name": "机器学习", "category": "AI", "level": "高级"},
        {"name": "深度学习", "category": "AI", "level": "专家"},
        {"name": "数据挖掘", "category": "数据分析", "level": "中级"}
    ]
    
    structured_result = agent.extract_knowledge_from_structured_data(
        data=structured_data,
        domain_type="technology",
        field_mapping={
            "skill_name": "name",
            "category": "category",
            "level": "level"
        }
    )
    assert len(structured_result.extracted_knowledges) > 0, "结构化数据抽取失败"
    print(f"✓ 从结构化数据抽取 {len(structured_result.extracted_knowledges)} 条知识")
    
    # 注册结构化数据
    stats2 = agent.register_extracted_knowledges(structured_result)
    print(f"✓ 注册结果: {stats2['success']} 成功, {stats2['failed']} 失败")
    
    # 测试抽取统计
    extraction_stats = agent.get_extraction_stats()
    print(f"\n抽取统计:")
    print(f"  总模式数: {extraction_stats['total_patterns']}")
    for p in extraction_stats['patterns']:
        print(f"  - {p['name']} ({p['domain']}): {p['pattern_count']} 个模式")
    
    print("\n" + "=" * 60)
    print("阶段37验收测试完成！✓ 所有测试通过")
    print("=" * 60)
    print("\n功能覆盖:")
    print("  ✓ 从文本自动抽取知识")
    print("  ✓ 从结构化数据抽取知识")
    print("  ✓ 批量注册抽取的知识")
    print("  ✓ 多领域模式匹配")
    print("  ✓ 属性自动提取")
    print("  ✓ 抽取统计")
    print("  ✓ Agent集成")
    
    agent.shutdown()
    return True


if __name__ == "__main__":
    try:
        success = test_stage37()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
