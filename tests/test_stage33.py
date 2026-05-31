#!/usr/bin/env python3
"""
阶段33验收测试：领域知识导入导出与数据迁移
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import EternalSelfAgent
from core.domain_knowledge_manager import DomainType


def test_stage33():
    print("=" * 60)
    print("阶段33验收测试：领域知识导入导出与数据迁移")
    print("=" * 60)
    
    agent = EternalSelfAgent(agent_id="stage33_test_agent")
    print("\n[1/6] Agent初始化成功")
    
    # 创建测试知识
    print("\n[2/6] 创建测试知识...")
    tech1 = agent.create_domain_knowledge(
        "technology_skill",
        "Python高级编程",
        {"skill_name": "Python", "category": "编程语言", "level": "高级"},
        tags=["技术", "编程", "Python"]
    )
    health1 = agent.create_domain_knowledge(
        "health_condition",
        "普通感冒",
        {"condition_name": "感冒", "symptoms": ["流鼻涕"], "causes": ["病毒"]},
        tags=["医疗", "健康"]
    )
    edu1 = agent.create_domain_knowledge(
        "education_subject",
        "线性代数",
        {"subject_name": "线性代数", "grade_level": "大学", "core_concepts": ["向量"]},
        tags=["教育", "数学"]
    )
    print(f"✓ 创建 {len(agent.domain_knowledge_manager.domain_knowledges)} 条知识")
    
    # 测试JSON导出
    print("\n[3/6] 测试JSON导出...")
    result_json = agent.export_domain_knowledges(format="json")
    assert result_json.success, f"JSON导出失败: {result_json.error}"
    print(f"✓ JSON导出成功: {result_json.file_path} ({result_json.record_count} 条)")
    
    # 测试CSV导出
    print("\n测试CSV导出...")
    result_csv = agent.export_domain_knowledges(format="csv")
    assert result_csv.success, f"CSV导出失败: {result_csv.error}"
    print(f"✓ CSV导出成功: {result_csv.file_path} ({result_csv.record_count} 条)")
    
    # 测试XML导出
    print("\n测试XML导出...")
    result_xml = agent.export_domain_knowledges(format="xml")
    assert result_xml.success, f"XML导出失败: {result_xml.error}"
    print(f"✓ XML导出成功: {result_xml.file_path} ({result_xml.record_count} 条)")
    
    # 测试JSON导入
    print("\n[4/6] 测试JSON导入...")
    # 先删除一条知识
    agent.delete_domain_knowledge(tech1.knowledge_id)
    # 再导入
    import_result = agent.import_domain_knowledges(result_json.file_path, format="json")
    assert import_result.success_count > 0, "JSON导入失败"
    print(f"✓ JSON导入成功: {import_result.success_count} 条")
    
    # 测试CSV导入（先清空再导入）
    print("\n测试CSV导入...")
    # 删除所有知识
    for kid in list(agent.domain_knowledge_manager.domain_knowledges.keys()):
        agent.delete_domain_knowledge(kid)
    import_result_csv = agent.import_domain_knowledges(result_csv.file_path, format="csv", skip_existing=False)
    assert import_result_csv.success_count > 0, "CSV导入失败"
    print(f"✓ CSV导入成功: {import_result_csv.success_count} 条")
    
    # 测试知识图谱迁移
    print("\n[5/6] 测试知识图谱迁移...")
    migrate_result = agent.migrate_knowledge_graph_to_domains()
    print(f"✓ 迁移完成: {migrate_result.success_count} 成功, {migrate_result.failed_count} 失败")
    
    # 测试导出历史
    print("\n[6/6] 测试导出历史...")
    history = agent.get_export_history()
    assert len(history) >= 3, "导出历史记录不足"
    print(f"✓ 导出历史: {len(history)} 个文件")
    for h in history[:3]:
        print(f"  {h['file_name']} ({h['format']}) - {h['size_bytes']} bytes")
    
    print("\n" + "=" * 60)
    print("阶段33验收测试完成！✓ 所有测试通过")
    print("=" * 60)
    print("\n功能覆盖:")
    print("  ✓ JSON导出")
    print("  ✓ CSV导出")
    print("  ✓ XML导出")
    print("  ✓ JSON导入")
    print("  ✓ CSV导入")
    print("  ✓ 知识图谱迁移")
    print("  ✓ 导出历史")
    print("  ✓ Agent集成")
    
    agent.shutdown()
    return True


if __name__ == "__main__":
    try:
        success = test_stage33()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
