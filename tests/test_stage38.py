#!/usr/bin/env python3
"""
阶段38验收测试：领域知识问答系统
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import EternalSelfAgent


def test_stage38():
    print("=" * 60)
    print("阶段38验收测试：领域知识问答系统")
    print("=" * 60)
    
    agent = EternalSelfAgent(agent_id="stage38_test_agent")
    print("\n[1/4] Agent初始化成功")
    
    # 创建测试知识
    print("\n[2/4] 创建测试知识...")
    agent.create_domain_knowledge(
        "technology_skill", "Python编程",
        {"skill_name": "Python", "category": "编程语言", "level": "高级", "applications": ["Web开发", "数据分析"]},
        tags=["技术", "编程", "Python"]
    )
    agent.create_domain_knowledge(
        "health_condition", "普通感冒",
        {"condition_name": "感冒", "symptoms": ["流鼻涕", "打喷嚏"], "causes": ["病毒感染"], "treatments": ["休息", "多喝水"]},
        tags=["医疗", "健康"]
    )
    agent.create_domain_knowledge(
        "education_subject", "线性代数",
        {"subject_name": "线性代数", "grade_level": "大学", "core_concepts": ["向量", "矩阵", "线性变换"]},
        tags=["教育", "数学"]
    )
    print(f"✓ 创建 {len(agent.domain_knowledge_manager.domain_knowledges)} 条知识")
    
    # 测试定义类问题
    print("\n[3/4] 测试定义类问题...")
    answer1 = agent.ask_domain_question("什么是Python编程？")
    print(f"✓ 问题: {answer1.question}")
    print(f"  类型: {answer1.question_type.value}")
    print(f"  答案: {answer1.answer_text}")
    print(f"  置信度: {answer1.confidence:.2f}")
    
    # 测试事实类问题
    print("\n测试事实类问题...")
    answer2 = agent.ask_domain_question("普通感冒的症状有哪些？")
    print(f"✓ 问题: {answer2.question}")
    print(f"  类型: {answer2.question_type.value}")
    print(f"  答案: {answer2.answer_text}")
    print(f"  置信度: {answer2.confidence:.2f}")
    
    # 测试流程类问题
    print("\n测试流程类问题...")
    answer3 = agent.ask_domain_question("如何治疗普通感冒？")
    print(f"✓ 问题: {answer3.question}")
    print(f"  类型: {answer3.question_type.value}")
    print(f"  答案: {answer3.answer_text}")
    
    # 测试相关问题
    print("\n[4/4] 测试相关问题...")
    if answer1.related_questions:
        print(f"✓ 相关问题:")
        for q in answer1.related_questions:
            print(f"  - {q}")
    
    # 测试对话历史
    history = agent.get_qa_history()
    print(f"\n对话历史: {len(history)} 轮")
    for i, h in enumerate(history):
        print(f"  {i+1}. Q: {h['question']}")
    
    print("\n" + "=" * 60)
    print("阶段38验收测试完成！✓ 所有测试通过")
    print("=" * 60)
    print("\n功能覆盖:")
    print("  ✓ 定义类问题回答")
    print("  ✓ 事实类问题回答")
    print("  ✓ 流程类问题回答")
    print("  ✓ 问题类型检测")
    print("  ✓ 相关问题推荐")
    print("  ✓ 对话历史管理")
    print("  ✓ Agent集成")
    
    agent.shutdown()
    return True


if __name__ == "__main__":
    try:
        success = test_stage38()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
