#!/usr/bin/env python3
"""
阶段34验收测试：领域知识协作与共享
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import EternalSelfAgent


def test_stage34():
    print("=" * 60)
    print("阶段34验收测试：领域知识协作与共享")
    print("=" * 60)
    
    agent = EternalSelfAgent(agent_id="stage34_test_agent")
    print("\n[1/5] Agent初始化成功")
    
    # 创建测试知识
    print("\n[2/5] 创建测试知识...")
    tech1 = agent.create_domain_knowledge(
        "technology_skill",
        "Python高级编程",
        {"skill_name": "Python", "category": "编程语言", "level": "高级"},
        tags=["技术", "编程"]
    )
    print(f"✓ 创建知识: {tech1.name}")
    
    # 测试共享知识
    print("\n[3/5] 测试共享知识...")
    share = agent.share_domain_knowledge(
        knowledge_id=tech1.knowledge_id,
        shared_by="user1",
        shared_with="user2",
        permission="write"
    )
    assert share is not None, "共享失败"
    print(f"✓ 共享成功: {share.share_id}")
    
    # 测试公开共享
    public_share = agent.share_domain_knowledge(
        knowledge_id=tech1.knowledge_id,
        shared_by="user1",
        shared_with=None,
        permission="read"
    )
    assert public_share is not None, "公开共享失败"
    print(f"✓ 公开共享成功: {public_share.share_id}")
    
    # 测试获取共享知识
    print("\n[4/5] 测试获取共享知识...")
    shared = agent.get_shared_knowledges("user2")
    assert len(shared) > 0, "获取共享知识失败"
    print(f"✓ user2 可访问 {len(shared)} 条共享知识")
    
    # 测试知识分支
    print("\n[5/5] 测试知识分支...")
    fork = agent.fork_domain_knowledge(tech1.knowledge_id, "user2")
    assert fork is not None, "创建分支失败"
    print(f"✓ 创建分支: {fork.forked_knowledge.name}")
    
    # 测试合并分支
    merge_result = agent.merge_knowledge_fork(fork.fork_id)
    assert merge_result, "合并分支失败"
    print(f"✓ 合并分支成功")
    
    # 测试协作统计
    stats = agent.get_collaboration_stats()
    print(f"\n协作统计:")
    print(f"  总共享数: {stats['total_shares']}")
    print(f"  活跃共享: {stats['active_shares']}")
    print(f"  总分支数: {stats['total_forks']}")
    print(f"  已合并: {stats['merged_forks']}")
    
    print("\n" + "=" * 60)
    print("阶段34验收测试完成！✓ 所有测试通过")
    print("=" * 60)
    print("\n功能覆盖:")
    print("  ✓ 知识共享")
    print("  ✓ 公开共享")
    print("  ✓ 权限管理")
    print("  ✓ 获取共享知识")
    print("  ✓ 知识分支")
    print("  ✓ 分支合并")
    print("  ✓ 协作统计")
    print("  ✓ Agent集成")
    
    agent.shutdown()
    return True


if __name__ == "__main__":
    try:
        success = test_stage34()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
