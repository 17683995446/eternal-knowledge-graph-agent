#!/usr/bin/env python3
"""
阶段39验收测试：领域知识API接口与外部集成
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import EternalSelfAgent


def test_stage39():
    print("=" * 60)
    print("阶段39验收测试：领域知识API接口与外部集成")
    print("=" * 60)
    
    agent = EternalSelfAgent(agent_id="stage39_test_agent")
    print("\n[1/5] Agent初始化成功")
    
    # 创建测试知识
    print("\n[2/5] 创建测试知识...")
    agent.create_domain_knowledge(
        "technology_skill", "Python编程",
        {"skill_name": "Python", "category": "编程语言", "level": "高级"},
        tags=["技术", "编程"]
    )
    agent.create_domain_knowledge(
        "health_condition", "普通感冒",
        {"condition_name": "感冒", "symptoms": ["流鼻涕"], "causes": ["病毒"]},
        tags=["医疗", "健康"]
    )
    print(f"✓ 创建 {len(agent.domain_knowledge_manager.domain_knowledges)} 条知识")
    
    # 测试获取所有知识
    print("\n[3/5] 测试API接口...")
    response = agent.domain_api.get_all_knowledges(limit=5)
    assert response.success, f"获取知识失败: {response.message}"
    print(f"✓ 获取知识列表: {response.data['total']} 条")
    
    # 测试获取单条知识
    knowledge_id = list(agent.domain_knowledge_manager.domain_knowledges.keys())[0]
    response = agent.domain_api.get_knowledge(knowledge_id)
    assert response.success, f"获取单条知识失败: {response.message}"
    print(f"✓ 获取单条知识: {response.data['name']}")
    
    # 测试搜索
    response = agent.domain_api.search_knowledges(query="Python")
    assert response.success, f"搜索失败: {response.message}"
    print(f"✓ 搜索: 找到 {response.data['total']} 条结果")
    
    # 测试创建知识
    response = agent.domain_api.create_knowledge(
        template_id="technology_skill",
        name="Java编程",
        content={"skill_name": "Java", "category": "编程语言", "level": "中级"},
        tags=["技术", "编程"]
    )
    assert response.success, f"创建知识失败: {response.message}"
    print(f"✓ 创建知识: {response.data['name']}")
    
    # 测试统计
    response = agent.domain_api.get_domain_stats()
    assert response.success, f"获取统计失败: {response.message}"
    print(f"✓ 获取统计: {response.data}")
    
    # 测试问答
    print("\n[4/5] 测试问答API...")
    response = agent.domain_api.ask_question("什么是Python编程？")
    assert response.success, f"问答失败: {response.message}"
    print(f"✓ 问答: {response.data['answer'][:50]}...")
    
    # 测试可视化数据
    print("\n[5/5] 测试可视化数据API...")
    response = agent.domain_api.get_visualization_data(viz_type="distribution")
    assert response.success, f"获取可视化数据失败: {response.message}"
    print(f"✓ 可视化数据: {len(response.data['distribution'])} 个领域")
    
    # 测试API文档
    response = agent.domain_api.get_api_documentation()
    assert "endpoints" in response, "API文档获取失败"
    print(f"✓ API文档: {len(response['endpoints'])} 个端点")
    
    print("\n" + "=" * 60)
    print("阶段39验收测试完成！✓ 所有测试通过")
    print("=" * 60)
    print("\n功能覆盖:")
    print("  ✓ 获取知识列表")
    print("  ✓ 获取单条知识")
    print("  ✓ 创建知识")
    print("  ✓ 搜索知识")
    print("  ✓ 获取统计")
    print("  ✓ 问答接口")
    print("  ✓ 可视化数据接口")
    print("  ✓ API文档")
    print("  ✓ Agent集成")
    
    agent.shutdown()
    return True


if __name__ == "__main__":
    try:
        success = test_stage39()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
