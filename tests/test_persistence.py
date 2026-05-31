"""
阶段3 验收测试：本地文件持久化系统
"""

import sys
import json
import shutil
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 临时修改保存路径用于测试
from core import constants
original_save_path = constants.KG_SAVE_PATH
test_save_path = Path("data/test_kg_persistence.json")
constants.KG_SAVE_PATH = str(test_save_path)

from core.knowledge_graph import KnowledgeGraph, Node, Edge


def cleanup_test_files():
    """清理测试文件"""
    test_files = [
        test_save_path,
        test_save_path.with_suffix('.tmp'),
        test_save_path.with_suffix('.bak')
    ]
    
    for f in test_files:
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_initial_run_creates_file():
    """首次运行自动创建文件"""
    cleanup_test_files()
    
    # 创建新的图谱实例
    kg = KnowledgeGraph()
    
    assert test_save_path.exists()
    assert test_save_path.is_file()
    print("✓ test_initial_run_creates_file 成功")


def test_data_saved_and_restored():
    """数据保存与恢复测试"""
    cleanup_test_files()
    
    # 创建并填充图谱
    kg1 = KnowledgeGraph()
    kg1.add_node("节点1")
    kg1.add_node("节点2")
    kg1.add_edge("节点1", "节点2", "关联关系", 0.75)
    
    # 重新加载
    kg2 = KnowledgeGraph()
    
    assert len(kg2.nodes) == 2
    assert len(kg2.edges) == 1
    
    # 验证边
    edge = kg2.edges[0]
    assert edge.source == "节点1"
    assert edge.target == "节点2"
    assert edge.relation == "关联关系"
    assert edge.weight == 0.75
    print("✓ test_data_saved_and_restored 成功")


def test_file_contains_metadata():
    """文件包含元数据验证"""
    cleanup_test_files()
    
    kg = KnowledgeGraph()
    kg.add_node("测试节点")
    
    # 读取文件内容
    with open(test_save_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert "version" in data
    assert data["version"] == "1.0"
    assert "schema" in data
    assert data["schema"] == "eternal_agent_kg_v1"
    assert "saved_at" in data
    assert "node_count" in data
    assert "edge_count" in data
    print("✓ test_file_contains_metadata 成功")


def test_backup_file_created():
    """测试备份文件创建"""
    cleanup_test_files()
    
    kg = KnowledgeGraph()
    kg.add_node("初始节点")
    
    # 再次修改保存
    kg.add_node("第二个节点")
    
    backup_path = test_save_path.with_suffix('.bak')
    assert backup_path.exists()
    print("✓ test_backup_file_created 成功")


def test_restore_from_corrupted_file():
    """测试损坏文件时的恢复"""
    cleanup_test_files()
    
    # 创建正常文件
    kg1 = KnowledgeGraph()
    kg1.add_node("重要节点")
    
    # 创建备份
    backup_path = test_save_path.with_suffix('.bak')
    shutil.copy(str(test_save_path), str(backup_path))
    
    # 损坏主文件
    with open(test_save_path, 'w', encoding='utf-8') as f:
        f.write("这不是有效的JSON数据！{]")
    
    # 重新加载
    kg2 = KnowledgeGraph()
    
    # 应该从备份恢复
    assert len(kg2.nodes) >= 1
    print("✓ test_restore_from_corrupted_file 成功")


def test_incomplete_data_loading():
    """测试不完整数据的加载（跳过错误项）"""
    cleanup_test_files()
    
    # 创建不完整数据
    bad_data = {
        "version": "1.0",
        "schema": "eternal_agent_kg_v1",
        "nodes": [
            {"id": "1", "name": "好节点", "attr": {}, "created_at": "2024-01-01T00:00:00", "valid": True},
            {"invalid": "没有name字段的节点"}  # 损坏的节点
        ],
        "edges": [
            {"source": "好节点", "target": "目标", "relation": "rel", "weight": 0.5, "created_at": "2024-01-01T00:00:00"},
            {"invalid": "没有source字段的边"}  # 损坏的边
        ]
    }
    
    with open(test_save_path, 'w', encoding='utf-8') as f:
        json.dump(bad_data, f)
    
    # 加载应该成功，跳过损坏项
    kg = KnowledgeGraph()
    assert len(kg.nodes) == 1  # 只有好节点
    print("✓ test_incomplete_data_loading 成功")


def test_multiple_save_operations():
    """测试多次保存操作"""
    cleanup_test_files()
    
    kg = KnowledgeGraph()
    
    # 多次添加
    for i in range(5):
        kg.add_node(f"节点{i}")
        if i > 0:
            kg.add_edge(f"节点{i-1}", f"节点{i}", "序列", 0.5)
    
    # 最后加载验证
    final_kg = KnowledgeGraph()
    assert len(final_kg.nodes) == 5
    assert len(final_kg.edges) == 4
    print("✓ test_multiple_save_operations 成功")


if __name__ == "__main__":
    print("=" * 50)
    print("=== 阶段3：本地文件持久化系统验收测试 ===")
    print("=" * 50)
    
    try:
        test_initial_run_creates_file()
        test_data_saved_and_restored()
        test_file_contains_metadata()
        test_backup_file_created()
        test_restore_from_corrupted_file()
        test_incomplete_data_loading()
        test_multiple_save_operations()
        
        print("\n" + "=" * 50)
        print("✅ 阶段3所有验收测试通过！")
        print("=" * 50)
    finally:
        cleanup_test_files()
        # 恢复原始路径
        constants.KG_SAVE_PATH = original_save_path
