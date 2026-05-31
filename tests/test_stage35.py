#!/usr/bin/env python3
"""
阶段35验收测试：领域知识可视化与图谱展示
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import EternalSelfAgent
from core.domain_knowledge_manager import DomainType


def test_stage35():
    print("=" * 60)
    print("阶段35验收测试：领域知识可视化与图谱展示")
    print("=" * 60)
    
    agent = EternalSelfAgent(agent_id="stage35_test_agent")
    print("\n[1/6] Agent初始化成功")
    
    # 创建测试知识
    print("\n[2/6] 创建测试知识...")
    agent.create_domain_knowledge(
        "technology_skill", "Python编程",
        {"skill_name": "Python", "category": "编程", "level": "高级"},
        tags=["技术", "编程", "Python"]
    )
    agent.create_domain_knowledge(
        "technology_skill", "JavaScript开发",
        {"skill_name": "JavaScript", "category": "编程", "level": "中级"},
        tags=["技术", "编程", "前端"]
    )
    agent.create_domain_knowledge(
        "health_condition", "普通感冒",
        {"condition_name": "感冒", "symptoms": ["流鼻涕"], "causes": ["病毒"]},
        tags=["医疗", "健康"]
    )
    agent.create_domain_knowledge(
        "education_subject", "线性代数",
        {"subject_name": "线性代数", "grade_level": "大学", "core_concepts": ["向量"]},
        tags=["教育", "数学"]
    )
    print(f"✓ 创建 {len(agent.domain_knowledge_manager.domain_knowledges)} 条知识")
    
    # 测试生成领域图谱
    print("\n[3/6] 测试生成领域图谱...")
    graph = agent.generate_domain_graph()
    assert len(graph.nodes) > 0, "图谱生成失败"
    print(f"✓ 生成图谱: {len(graph.nodes)} 节点, {len(graph.edges)} 边")
    
    # 测试按领域过滤
    tech_graph = agent.generate_domain_graph(domain_type=DomainType.TECHNOLOGY)
    assert len(tech_graph.nodes) > 0, "技术领域图谱生成失败"
    print(f"✓ 技术领域图谱: {len(tech_graph.nodes)} 节点")
    
    # 测试领域分布
    print("\n[4/6] 测试领域分布统计...")
    distribution = agent.generate_domain_distribution()
    assert distribution["total"] > 0, "领域分布统计失败"
    print(f"✓ 领域分布: {distribution['total']} 条知识")
    for d in distribution["distribution"]:
        print(f"  {d['domain']}: {d['count']} ({d['percentage']}%)")
    
    # 测试标签云
    print("\n[5/6] 测试标签云...")
    tag_cloud = agent.generate_tag_cloud(top_n=5)
    assert len(tag_cloud) > 0, "标签云生成失败"
    print(f"✓ 标签云: {len(tag_cloud)} 个标签")
    for tag in tag_cloud:
        print(f"  {tag['text']}: {tag['count']} 次 (大小: {tag['size']})")
    
    # 测试置信度分布
    print("\n[6/6] 测试置信度分布...")
    confidence_chart = agent.generate_confidence_chart()
    assert len(confidence_chart["values"]) > 0, "置信度分布生成失败"
    print(f"✓ 置信度分布:")
    for r, v in zip(confidence_chart["ranges"], confidence_chart["values"]):
        print(f"  {r}: {v} 条")
    
    # 测试导出
    print("\n测试导出...")
    json_path = agent.export_graph_to_json(graph)
    assert os.path.exists(json_path), "JSON导出失败"
    print(f"✓ JSON导出: {json_path}")
    
    html_path = agent.export_graph_to_html(graph)
    assert os.path.exists(html_path), "HTML导出失败"
    print(f"✓ HTML导出: {html_path}")
    
    # 测试可视化摘要
    summary = agent.get_visualization_summary()
    assert summary["total_knowledges"] > 0, "可视化摘要失败"
    print(f"✓ 可视化摘要: {summary['total_knowledges']} 条知识")
    
    print("\n" + "=" * 60)
    print("阶段35验收测试完成！✓ 所有测试通过")
    print("=" * 60)
    print("\n功能覆盖:")
    print("  ✓ 领域知识图谱生成")
    print("  ✓ 按领域过滤图谱")
    print("  ✓ 领域分布统计")
    print("  ✓ 标签云生成")
    print("  ✓ 置信度分布图")
    print("  ✓ JSON导出")
    print("  ✓ HTML交互式导出")
    print("  ✓ 可视化摘要")
    print("  ✓ Agent集成")
    
    agent.shutdown()
    return True


if __name__ == "__main__":
    try:
        success = test_stage35()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
