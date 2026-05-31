#!/usr/bin/env python3
"""
阶段32验收测试：领域知识搜索与推荐系统
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import EternalSelfAgent
from core.domain_knowledge_manager import DomainType


def test_stage32():
    """阶段32验收测试"""
    print("=" * 60)
    print("阶段32验收测试：领域知识搜索与推荐系统")
    print("=" * 60)
    
    # 1. 初始化 Agent
    print("\n[1/8] 初始化 Agent...")
    agent = EternalSelfAgent(agent_id="stage32_test_agent")
    print("✓ Agent 初始化成功")
    
    # 2. 创建测试知识
    print("\n[2/8] 创建测试知识...")
    
    # 技术知识
    tech1 = agent.create_domain_knowledge(
        "technology_skill",
        "Python高级编程",
        {"skill_name": "Python", "category": "编程语言", "level": "高级", "applications": ["Web开发", "数据分析"]},
        tags=["技术", "编程", "Python", "Web开发"]
    )
    
    tech2 = agent.create_domain_knowledge(
        "technology_skill",
        "JavaScript前端开发",
        {"skill_name": "JavaScript", "category": "编程语言", "level": "中级", "applications": ["Web开发", "前端"]},
        tags=["技术", "编程", "JavaScript", "Web开发", "前端"]
    )
    
    tech3 = agent.create_domain_knowledge(
        "technology_skill",
        "Java后端开发",
        {"skill_name": "Java", "category": "编程语言", "level": "高级", "applications": ["后端", "企业应用"]},
        tags=["技术", "编程", "Java", "后端"]
    )
    
    # 医疗知识
    health1 = agent.create_domain_knowledge(
        "health_condition",
        "普通感冒诊疗",
        {"condition_name": "感冒", "symptoms": ["流鼻涕", "咳嗽"], "causes": ["病毒"]},
        tags=["医疗", "健康", "感冒"]
    )
    
    health2 = agent.create_domain_knowledge(
        "health_condition",
        "流感预防",
        {"condition_name": "流感", "symptoms": ["发热", "头痛"], "causes": ["流感病毒"]},
        tags=["医疗", "健康", "流感"]
    )
    
    # 教育知识
    edu1 = agent.create_domain_knowledge(
        "education_subject",
        "线性代数基础",
        {"subject_name": "线性代数", "grade_level": "大学", "core_concepts": ["向量", "矩阵"]},
        tags=["教育", "数学", "线性代数"]
    )
    
    print(f"✓ 成功创建 {len(agent.domain_knowledge_manager.domain_knowledges)} 条领域知识")
    
    # 3. 测试关键词搜索
    print("\n[3/8] 测试关键词搜索...")
    keyword_results = agent.search_domain_knowledge(
        query="Python",
        search_type="keyword"
    )
    assert len(keyword_results) > 0, "关键词搜索失败"
    print(f"✓ 关键词搜索 'Python' 找到 {len(keyword_results)} 条结果")
    for result in keyword_results:
        print(f"  [{result.rank}] {result.knowledge.name} (分数: {result.score:.2f}) - {result.match_reason}")
    
    # 4. 测试语义搜索
    print("\n[4/8] 测试语义搜索...")
    semantic_results = agent.search_domain_knowledge(
        query="编程",
        search_type="semantic"
    )
    assert len(semantic_results) > 0, "语义搜索失败"
    print(f"✓ 语义搜索 '编程' 找到 {len(semantic_results)} 条结果")
    for result in semantic_results[:3]:
        print(f"  [{result.rank}] {result.knowledge.name} (分数: {result.score:.2f}) - {result.match_reason}")
    
    # 5. 测试混合搜索
    print("\n[5/8] 测试混合搜索...")
    hybrid_results = agent.search_domain_knowledge(
        query="Web开发",
        search_type="hybrid",
        limit=5
    )
    assert len(hybrid_results) > 0, "混合搜索失败"
    print(f"✓ 混合搜索 'Web开发' 找到 {len(hybrid_results)} 条结果")
    
    # 6. 测试相似知识推荐
    print("\n[6/8] 测试相似知识推荐...")
    source_id = tech1.knowledge_id
    similar_recs = agent.get_domain_recommendations(
        source_knowledge_id=source_id,
        recommend_types=["similar"],
        limit=3
    )
    assert len(similar_recs) > 0, "相似知识推荐失败"
    print(f"✓ 基于 '{tech1.name}' 找到 {len(similar_recs)} 条相似推荐")
    for rec in similar_recs:
        print(f"  {rec.knowledge.name} (分数: {rec.score:.2f}) - {rec.reason}")
    
    # 7. 测试标签推荐和热门推荐
    print("\n[7/8] 测试标签推荐和热门推荐...")
    
    # 模拟一些访问来增加热度
    print("  模拟知识访问以计算热度...")
    for _ in range(10):
        agent.domain_searcher.record_view(tech1.knowledge_id)
    for _ in range(5):
        agent.domain_searcher.record_view(tech2.knowledge_id)
    
    # 测试标签推荐
    tag_recs = agent.get_domain_recommendations(
        source_tags=["编程", "技术"],
        recommend_types=["related", "trending", "recent"],
        limit=5
    )
    assert len(tag_recs) > 0, "标签推荐失败"
    print(f"✓ 基于标签 ['编程', '技术'] 找到 {len(tag_recs)} 条推荐")
    for rec in tag_recs:
        print(f"  {rec.knowledge.name} ({rec.source_type}) - {rec.reason}")
    
    # 8. 测试搜索统计
    print("\n[8/8] 测试搜索统计...")
    stats = agent.get_search_statistics()
    assert stats["total_knowledges"] > 0, "搜索统计失败"
    print(f"✓ 搜索统计:")
    print(f"  总知识数: {stats['total_knowledges']}")
    print(f"  总访问数: {stats['total_accesses']}")
    print(f"  热门标签: {stats['top_tags'][:3]}")
    
    # 完成所有测试
    print("\n" + "=" * 60)
    print("阶段32验收测试完成！✓ 所有测试通过")
    print("=" * 60)
    print("\n功能覆盖:")
    print("  ✓ 关键词搜索")
    print("  ✓ 语义搜索")
    print("  ✓ 混合搜索")
    print("  ✓ 相似知识推荐")
    print("  ✓ 标签推荐")
    print("  ✓ 热门知识推荐")
    print("  ✓ 最近知识推荐")
    print("  ✓ 搜索统计与热度计算")
    print("  ✓ Agent集成")
    
    # 清理
    agent.shutdown()
    
    return True


if __name__ == "__main__":
    try:
        success = test_stage32()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
