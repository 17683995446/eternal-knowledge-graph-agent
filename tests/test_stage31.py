#!/usr/bin/env python3
"""
阶段31验收测试：专业领域知识适配与增强
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import EternalSelfAgent
from core.domain_knowledge_manager import DomainType


def test_stage31():
    """阶段31验收测试"""
    print("=" * 60)
    print("阶段31验收测试：专业领域知识适配与增强")
    print("=" * 60)
    
    # 1. 初始化 Agent
    print("\n[1/8] 初始化 Agent...")
    agent = EternalSelfAgent(agent_id="stage31_test_agent")
    print("✓ Agent 初始化成功")
    
    # 2. 测试领域模板管理
    print("\n[2/8] 测试领域模板管理...")
    templates = agent.list_domain_templates()
    print(f"✓ 已加载 {len(templates)} 个默认模板")
    
    # 按领域列出模板
    tech_templates = agent.list_domain_templates(DomainType.TECHNOLOGY)
    print(f"✓ 技术领域模板: {[t.template_name for t in tech_templates]}")
    
    health_templates = agent.list_domain_templates(DomainType.HEALTHCARE)
    print(f"✓ 医疗健康领域模板: {[t.template_name for t in health_templates]}")
    
    # 3. 测试基于模板创建领域知识
    print("\n[3/8] 测试基于模板创建领域知识...")
    
    # 创建技术知识
    tech_content = {
        "skill_name": "Python 编程",
        "category": "编程语言",
        "level": "高级",
        "prerequisites": ["基础编程概念", "计算机科学基础"],
        "applications": ["Web开发", "数据分析", "人工智能"],
        "tools": ["PyCharm", "VSCode", "Jupyter"]
    }
    tech_knowledge = agent.create_domain_knowledge(
        "technology_skill", 
        "Python 高级编程技能", 
        tech_content,
        tags=["技术", "编程", "Python"],
        sources=["经验积累", "培训"]
    )
    assert tech_knowledge is not None, "技术知识创建失败"
    print(f"✓ 技术知识创建成功: {tech_knowledge.name}")
    
    # 创建医疗知识
    health_content = {
        "condition_name": "普通感冒",
        "symptoms": ["流鼻涕", "打喷嚏", "喉咙痛", "轻微咳嗽"],
        "causes": ["病毒感染", "鼻病毒", "冠状病毒"],
        "treatments": ["休息", "多喝水", "非处方药物"],
        "prevention": ["勤洗手", "避免接触患者", "增强免疫力"]
    }
    health_knowledge = agent.create_domain_knowledge(
        "health_condition", 
        "普通感冒诊疗知识", 
        health_content,
        tags=["医疗", "感冒", "健康"],
        sources=["医学知识"]
    )
    assert health_knowledge is not None, "医疗知识创建失败"
    print(f"✓ 医疗知识创建成功: {health_knowledge.name}")
    
    # 创建教育知识
    edu_content = {
        "subject_name": "线性代数",
        "grade_level": "大学",
        "core_concepts": ["向量", "矩阵", "线性变换", "特征值"],
        "prerequisites": ["初等代数", "几何基础"],
        "textbooks": ["线性代数及其应用"],
        "resources": ["MIT公开课", "Khan学院"]
    }
    edu_knowledge = agent.create_domain_knowledge(
        "education_subject", 
        "线性代数课程知识", 
        edu_content,
        tags=["教育", "数学", "线性代数"],
        sources=["课程学习"]
    )
    assert edu_knowledge is not None, "教育知识创建失败"
    print(f"✓ 教育知识创建成功: {edu_knowledge.name}")
    
    # 4. 测试知识检索
    print("\n[4/8] 测试知识检索...")
    
    # 按ID获取
    retrieved = agent.get_domain_knowledge(tech_knowledge.knowledge_id)
    assert retrieved is not None, "按ID检索知识失败"
    assert retrieved.name == tech_knowledge.name, "检索的知识不匹配"
    print("✓ 按ID检索知识成功")
    
    # 关键词搜索
    search_results = agent.search_domain_knowledge("编程")
    assert len(search_results) >= 1, "关键词搜索失败"
    print(f"✓ 关键词搜索成功，找到 {len(search_results)} 条知识")
    
    # 按领域搜索
    domain_results = agent.search_domain_knowledge("", domain_type=DomainType.TECHNOLOGY)
    assert len(domain_results) >= 1, "按领域搜索失败"
    print(f"✓ 按领域搜索成功，找到 {len(domain_results)} 条知识")
    
    # 5. 测试知识更新
    print("\n[5/8] 测试知识更新...")
    update_success = agent.update_domain_knowledge(
        tech_knowledge.knowledge_id,
        {"certifications": ["Python专业认证", "数据科学家认证"]}
    )
    assert update_success, "知识更新失败"
    
    updated = agent.get_domain_knowledge(tech_knowledge.knowledge_id)
    assert "certifications" in updated.content, "更新内容未保存"
    print("✓ 知识更新成功")
    
    # 6. 测试知识图谱增强
    print("\n[6/8] 测试知识图谱增强...")
    
    # 先在知识图谱中添加一些相关节点
    agent.knowledge_graph.add_node("Python", {"type": "language"})
    agent.knowledge_graph.add_node("Web开发", {"type": "application"})
    agent.knowledge_graph.add_edge("Python", "Web开发", "用于", 0.8)
    
    enhanced = agent.enhance_knowledge_with_graph(tech_knowledge)
    assert enhanced is not None, "知识增强失败"
    print("✓ 知识增强成功")
    if "related_graph_nodes" in enhanced.content:
        print(f"  - 关联知识图谱节点: {len(enhanced.content['related_graph_nodes'])} 个")
    
    # 7. 测试领域统计
    print("\n[7/8] 测试领域统计...")
    stats = agent.get_domain_stats()
    print(f"✓ 领域统计信息:")
    print(f"  - 总知识数: {stats['total_knowledges']}")
    print(f"  - 总模板数: {stats['total_templates']}")
    print(f"  - 知识按领域分布: {stats['knowledge_by_domain']}")
    
    # 8. 测试知识删除
    print("\n[8/8] 测试知识删除...")
    delete_success = agent.delete_domain_knowledge(edu_knowledge.knowledge_id)
    assert delete_success, "知识删除失败"
    
    after_delete = agent.get_domain_knowledge(edu_knowledge.knowledge_id)
    assert after_delete is None, "删除的知识仍可检索"
    print("✓ 知识删除成功")
    
    # 完成所有测试
    print("\n" + "=" * 60)
    print("阶段31验收测试完成！✓ 所有测试通过")
    print("=" * 60)
    print("\n功能覆盖:")
    print("  ✓ 领域模板管理")
    print("  ✓ 基于模板创建领域知识")
    print("  ✓ 知识检索与搜索")
    print("  ✓ 知识更新与删除")
    print("  ✓ 知识图谱增强")
    print("  ✓ 领域统计")
    print("  ✓ Agent 集成")
    
    # 清理
    agent.shutdown()
    
    return True


if __name__ == "__main__":
    try:
        success = test_stage31()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
