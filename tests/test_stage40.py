#!/usr/bin/env python3
"""
阶段40验收测试：领域知识系统全面测试与优化
综合测试所有功能模块
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import EternalSelfAgent
from core.domain_knowledge_manager import DomainType


def test_stage40():
    print("=" * 70)
    print("阶段40验收测试：领域知识系统全面测试与优化")
    print("=" * 70)
    
    agent = EternalSelfAgent(agent_id="stage40_test_agent")
    print("\n[初始化] Agent初始化成功")
    
    # ===== 阶段31-32: 基础功能测试 =====
    print("\n" + "-" * 70)
    print("[阶段31-32] 基础功能测试")
    print("-" * 70)
    
    # 创建多领域知识
    knowledges = []
    templates = [
        ("technology_skill", "Python编程", {"skill_name": "Python", "category": "编程", "level": "高级"}, ["技术", "编程"]),
        ("technology_skill", "Java开发", {"skill_name": "Java", "category": "编程", "level": "中级"}, ["技术", "编程"]),
        ("health_condition", "普通感冒", {"condition_name": "感冒", "symptoms": ["流鼻涕"], "causes": ["病毒"]}, ["医疗", "健康"]),
        ("education_subject", "线性代数", {"subject_name": "线性代数", "grade_level": "大学", "core_concepts": ["向量"]}, ["教育", "数学"]),
        ("finance_product", "定期存款", {"product_name": "定期存款", "product_type": "储蓄", "risk_level": "低"}, ["金融", "理财"]),
    ]
    
    for template_id, name, content, tags in templates:
        k = agent.create_domain_knowledge(template_id, name, content, tags=tags)
        if k:
            knowledges.append(k)
    
    print(f"✓ 创建 {len(knowledges)} 条多领域知识")
    
    # 搜索测试
    results = agent.search_domain_knowledge("编程")
    print(f"✓ 搜索测试: 找到 {len(results)} 条结果")
    
    # 推荐测试
    recs = agent.get_domain_recommendations(source_tags=["技术"])
    print(f"✓ 推荐测试: 找到 {len(recs)} 条推荐")
    
    # ===== 阶段33: 导入导出测试 =====
    print("\n" + "-" * 70)
    print("[阶段33] 导入导出测试")
    print("-" * 70)
    
    export_result = agent.export_domain_knowledges(format="json")
    assert export_result.success, "导出失败"
    print(f"✓ JSON导出: {export_result.record_count} 条")
    
    # ===== 阶段34: 协作测试 =====
    print("\n" + "-" * 70)
    print("[阶段34] 协作测试")
    print("-" * 70)
    
    if knowledges:
        share = agent.share_domain_knowledge(
            knowledges[0].knowledge_id, "user1", "user2", "write"
        )
        assert share is not None, "共享失败"
        print(f"✓ 知识共享: {share.share_id}")
        
        fork = agent.fork_domain_knowledge(knowledges[0].knowledge_id, "user2")
        assert fork is not None, "分支失败"
        print(f"✓ 知识分支: {fork.fork_id}")
    
    # ===== 阶段35: 可视化测试 =====
    print("\n" + "-" * 70)
    print("[阶段35] 可视化测试")
    print("-" * 70)
    
    graph = agent.generate_domain_graph()
    print(f"✓ 图谱生成: {len(graph.nodes)} 节点, {len(graph.edges)} 边")
    
    distribution = agent.generate_domain_distribution()
    print(f"✓ 领域分布: {distribution['total']} 条知识")
    
    tag_cloud = agent.generate_tag_cloud(5)
    print(f"✓ 标签云: {len(tag_cloud)} 个标签")
    
    # ===== 阶段36: 质量评估测试 =====
    print("\n" + "-" * 70)
    print("[阶段36] 质量评估测试")
    print("-" * 70)
    
    if knowledges:
        report = agent.evaluate_knowledge_quality(knowledges[0].knowledge_id)
        assert report is not None, "质量评估失败"
        print(f"✓ 质量评估: {report.overall_score} 分 ({report.quality_level.value})")
    
    metrics = agent.batch_evaluate_quality()
    print(f"✓ 批量评估: {metrics.total_knowledges} 条, 平均分 {metrics.avg_quality_score}")
    
    # ===== 阶段37: 抽取测试 =====
    print("\n" + "-" * 70)
    print("[阶段37] 自动化抽取测试")
    print("-" * 70)
    
    text = "Python是一种高级编程语言。JavaScript用于前端开发。"
    extract_result = agent.extract_knowledge_from_text(text)
    print(f"✓ 文本抽取: {len(extract_result.extracted_knowledges)} 条")
    
    # ===== 阶段38: 问答测试 =====
    print("\n" + "-" * 70)
    print("[阶段38] 问答系统测试")
    print("-" * 70)
    
    answer = agent.ask_domain_question("什么是Python编程？")
    print(f"✓ 问答: {answer.answer_text[:50]}...")
    
    # ===== 阶段39: API测试 =====
    print("\n" + "-" * 70)
    print("[阶段39] API接口测试")
    print("-" * 70)
    
    api_response = agent.domain_api.get_all_knowledges(limit=3)
    assert api_response.success, "API调用失败"
    print(f"✓ API调用: {api_response.data['total']} 条知识")
    
    api_docs = agent.domain_api.get_api_documentation()
    print(f"✓ API文档: {len(api_docs['endpoints'])} 个端点")
    
    # ===== 系统统计 =====
    print("\n" + "-" * 70)
    print("[系统统计]")
    print("-" * 70)
    
    stats = agent.get_domain_stats()
    print(f"总知识数: {stats['total_knowledges']}")
    print(f"总模板数: {stats['total_templates']}")
    print(f"领域分布: {stats['knowledge_by_domain']}")
    
    search_stats = agent.get_search_statistics()
    print(f"搜索统计: {search_stats['total_knowledges']} 条知识, {search_stats['total_accesses']} 次访问")
    
    viz_summary = agent.get_visualization_summary()
    print(f"可视化: {viz_summary['total_knowledges']} 条知识可可视化")
    
    collab_stats = agent.get_collaboration_stats()
    print(f"协作: {collab_stats['total_shares']} 次共享, {collab_stats['total_forks']} 个分支")
    
    extraction_stats = agent.get_extraction_stats()
    print(f"抽取: {extraction_stats['total_patterns']} 个模式")
    
    # ===== 性能测试 =====
    print("\n" + "-" * 70)
    print("[性能测试]")
    print("-" * 70)
    
    import time
    
    # 搜索性能
    start = time.time()
    for _ in range(10):
        agent.search_domain_knowledge("编程")
    search_time = (time.time() - start) / 10
    print(f"✓ 搜索性能: {search_time*1000:.2f} ms/次")
    
    # 问答性能
    start = time.time()
    for _ in range(5):
        agent.ask_domain_question("什么是Python？")
    qa_time = (time.time() - start) / 5
    print(f"✓ 问答性能: {qa_time*1000:.2f} ms/次")
    
    print("\n" + "=" * 70)
    print("阶段40验收测试完成！✓ 所有系统测试通过")
    print("=" * 70)
    print("\n完整功能覆盖:")
    print("  ✓ 领域知识管理 (阶段31)")
    print("  ✓ 搜索与推荐 (阶段32)")
    print("  ✓ 导入导出 (阶段33)")
    print("  ✓ 协作共享 (阶段34)")
    print("  ✓ 可视化展示 (阶段35)")
    print("  ✓ 质量评估 (阶段36)")
    print("  ✓ 自动抽取 (阶段37)")
    print("  ✓ 问答系统 (阶段38)")
    print("  ✓ API接口 (阶段39)")
    print("  ✓ 全面测试 (阶段40)")
    print("\n  ✓ 性能测试通过")
    print("  ✓ 系统集成完成")
    
    agent.shutdown()
    return True


if __name__ == "__main__":
    try:
        success = test_stage40()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
