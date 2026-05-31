"""
阶段23验收测试：多Agent协作与分布式扩展
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import constants


def cleanup_test_files():
    """清理测试文件"""
    test_path = Path("data/test_stage23_kg.json")
    for suffix in ['', '.tmp', '.bak']:
        f = test_path.with_suffix(suffix if suffix else '.json')
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_message_queue():
    """测试消息队列"""
    print("\n=== 测试消息队列 ===")
    
    from core.multi_agent import MessageQueue, AgentMessage, MessageType
    
    queue = MessageQueue(max_size=100)
    
    # 创建测试消息
    msg1 = AgentMessage(
        message_id="msg1",
        from_agent="agent1",
        to_agent="agent2",
        message_type=MessageType.TASK_ASSIGNMENT,
        content={"task": "test_task"}
    )
    
    # 测试入队
    success = queue.enqueue(msg1)
    assert success is True
    assert queue.size() == 1
    
    # 测试出队
    dequeued_msg = queue.dequeue()
    assert dequeued_msg is not None
    assert dequeued_msg.message_id == "msg1"
    assert queue.size() == 0
    
    # 测试重复消息过滤
    queue.enqueue(msg1)
    success = queue.enqueue(msg1)  # 再次入队相同消息
    assert success is False
    
    print("✓ 消息队列测试通过")


def test_agent_registration():
    """测试Agent注册"""
    print("\n=== 测试Agent注册 ===")
    
    from core.multi_agent import MultiAgentCoordinator, AgentRole
    
    coordinator = MultiAgentCoordinator(
        own_agent_id="coordinator",
        role=AgentRole.COORDINATOR
    )
    
    # 验证初始状态
    status = coordinator.get_system_status()
    assert status['own_agent'] == "coordinator"
    assert status['role'] == "coordinator"
    
    # 注册Worker Agent
    from core.multi_agent import AgentInfo
    agent_info = AgentInfo(
        agent_id="worker1",
        role=AgentRole.WORKER,
        address="local:worker1",
        capabilities=["general", "processing"]
    )
    coordinator.register_remote_agent(agent_info)
    
    # 验证注册
    updated_status = coordinator.get_system_status()
    assert "worker1" in updated_status['known_agents']
    
    print("✓ Agent注册测试通过")


def test_task_allocation():
    """测试任务分配"""
    print("\n=== 测试任务分配 ===")
    
    from core.multi_agent import (
        MultiAgentCoordinator,
        AgentRole,
        AgentInfo
    )
    
    coordinator = MultiAgentCoordinator(
        own_agent_id="coordinator",
        role=AgentRole.COORDINATOR
    )
    
    # 注册多个Worker
    for i in range(3):
        agent_info = AgentInfo(
            agent_id=f"worker{i+1}",
            role=AgentRole.WORKER,
            address=f"local:worker{i+1}",
            capabilities=["general"]
        )
        coordinator.register_remote_agent(agent_info)
    
    # 分配任务
    task = {"description": "test_task", "capabilities": ["general"]}
    assigned_agent = coordinator.assign_task(task)
    
    # 验证分配
    assert assigned_agent is not None
    assert assigned_agent in ["worker1", "worker2", "worker3"]
    print(f"✓ 任务分配测试通过，分配给: {assigned_agent}")


def test_knowledge_sharding():
    """测试知识图谱分片"""
    print("\n=== 测试知识图谱分片 ===")
    
    from core.multi_agent import KnowledgeShardingManager
    
    sharding_mgr = KnowledgeShardingManager(num_shards=4)
    
    # 分配节点到分片
    for i in range(10):
        node_id = f"node{i}"
        shard_id = sharding_mgr.assign_node_to_shard(node_id, "agent1")
        print(f"  节点 node{i} 分配到分片: {shard_id}")
    
    # 获取分片
    shards = sharding_mgr.get_all_shards()
    assert len(shards) <= 4  # 最多4个分片
    
    print("✓ 知识图谱分片测试通过")


def test_system_monitoring():
    """测试系统监控"""
    print("\n=== 测试系统监控 ===")
    
    from core.multi_agent import AgentMonitor, AgentInfo, AgentRole
    
    monitor = AgentMonitor(heartbeat_timeout=30.0)
    
    # 注册Agent
    agent_info = AgentInfo(
        agent_id="monitor_test",
        role=AgentRole.WORKER,
        address="local:monitor_test",
        capabilities=["monitoring"]
    )
    monitor.register_agent(agent_info)
    
    # 更新状态
    monitor.update_agent_state("monitor_test", "active", 0.3)
    
    # 获取系统负载
    load_info = monitor.get_system_load()
    assert load_info['active_agents'] == 1
    assert load_info['avg_load'] == 0.3
    
    print("✓ 系统监控测试通过")


def test_multi_agent_integration():
    """测试与主Agent的集成"""
    print("\n=== 测试与主Agent的集成 ===")
    
    from core.agent import EternalSelfAgent
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage23_kg.json"
    
    # 创建主Agent
    agent = EternalSelfAgent(
        agent_id="main_coordinator",
        role="coordinator"
    )
    
    # 验证初始化
    assert agent.agent_id == "main_coordinator"
    assert hasattr(agent, "multi_agent_coordinator")
    
    # 注册协作Agent
    agent.register_agent("worker1", "worker", ["processing"])
    agent.register_agent("worker2", "worker", ["analysis"])
    
    # 获取状态
    multi_status = agent.get_multi_agent_status()
    print(f"  多Agent状态: {multi_status}")
    assert "worker1" in multi_status['known_agents']
    assert "worker2" in multi_status['known_agents']
    
    # 验证任务分配
    test_task = {
        "description": "test_integration_task",
        "capabilities": ["processing"]
    }
    assigned = agent.assign_task_to_agent(test_task)
    print(f"  任务分配结果: {assigned}")
    
    # 运行几次迭代来触发通信处理
    for i in range(15):
        agent.run_counter = i + 1
        if i + 1 == 10:
            agent._process_multi_agent_communication()
    
    print("✓ 与主Agent集成测试通过")


def test_full_collaboration_scenario():
    """测试完整协作场景"""
    print("\n=== 测试完整协作场景 ===")
    
    from core.multi_agent import (
        MultiAgentCoordinator,
        AgentRole,
        AgentInfo,
        MessageType
    )
    
    # 创建协调者
    coordinator = MultiAgentCoordinator(
        own_agent_id="coordinator",
        role=AgentRole.COORDINATOR
    )
    
    # 注册多个工作者
    for i in range(5):
        agent_info = AgentInfo(
            agent_id=f"worker{i+1}",
            role=AgentRole.WORKER,
            address=f"local:worker{i+1}",
            capabilities=["general", f"skill{i+1}"]
        )
        coordinator.register_remote_agent(agent_info)
    
    # 模拟任务分配
    tasks = [
        {"name": "task1", "capabilities": ["skill1"]},
        {"name": "task2", "capabilities": ["skill2"]},
        {"name": "task3", "capabilities": ["general"]}
    ]
    
    # 分配任务
    assignments = []
    for task in tasks:
        coordinator.queue_task(task)
    
    # 处理队列
    results = coordinator.process_agent_communication()
    for result in results:
        if result['type'] == 'task_assignments':
            assignments.extend(result['assignments'])
    
    print(f"  完成任务分配: {len(assignments)} 个任务")
    
    # 发送健康检查
    coordinator.broadcast_message(
        MessageType.HEALTH_CHECK,
        {"status": "checking"}
    )
    
    print("✓ 完整协作场景测试通过")


if __name__ == "__main__":
    print("=" * 70)
    print("=== 阶段23：多Agent协作与分布式扩展验收测试 ===")
    print("=" * 70)
    
    try:
        test_message_queue()
        test_agent_registration()
        test_task_allocation()
        test_knowledge_sharding()
        test_system_monitoring()
        test_multi_agent_integration()
        test_full_collaboration_scenario()
        
        print("\n" + "=" * 70)
        print("✅ 阶段23所有验收测试通过！")
        print("=" * 70)
    finally:
        cleanup_test_files()
        constants.KG_SAVE_PATH = "data/knowledge_graph.json"
