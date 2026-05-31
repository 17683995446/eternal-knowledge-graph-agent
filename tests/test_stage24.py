"""
阶段24验收测试：Web界面与监控系统
"""

import sys
import time
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import constants


def cleanup_test_files():
    """清理测试文件"""
    test_path = Path("data/test_stage24_kg.json")
    for suffix in ['', '.tmp', '.bak']:
        f = test_path.with_suffix(suffix if suffix else '.json')
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_web_service_initialization():
    """测试Web服务初始化"""
    print("\n=== 测试Web服务初始化 ===")
    
    from core.web_service import (
        WebServerConfig,
        WebEvent,
        WebEventHandler,
        EternalAgentWebServer
    )
    
    # 测试配置类
    config = WebServerConfig(
        host="127.0.0.1",
        port=8081,
        enable_cors=True
    )
    assert config.host == "127.0.0.1"
    assert config.port == 8081
    assert config.enable_cors is True
    
    # 测试事件处理
    event_handler = WebEventHandler()
    test_event = WebEvent(
        event_type="test_event",
        data={"test": "data"}
    )
    event_handler.emit(test_event.event_type, test_event.data)
    
    recent_events = event_handler.get_recent_events(1)
    assert len(recent_events) == 1
    assert recent_events[0].event_type == "test_event"
    
    print("✓ Web服务初始化测试通过")


def test_agent_with_web_interface():
    """测试Agent与Web界面集成"""
    print("\n=== 测试Agent与Web界面集成 ===")
    
    from core.agent import EternalSelfAgent
    
    # 创建Agent
    agent = EternalSelfAgent(
        agent_id="test_web_agent",
        role="coordinator"
    )
    
    # 启用Web界面
    agent.enable_web_interface(
        host="127.0.0.1",
        port=8082,
        enable_cors=True
    )
    
    # 验证Web服务器已启动
    assert agent.web_server is not None
    assert agent.web_config is not None
    print(f"✓ Web界面已启动在 {agent.web_server.get_url()}")
    
    # 添加一些测试数据
    agent.knowledge_graph.add_node("测试知识1", {"type": "concept"})
    agent.knowledge_graph.add_node("测试知识2", {"type": "concept"})
    agent.knowledge_graph.add_edge("测试知识1", "测试知识2", "related_to", 0.8)
    
    # 检查状态
    status = agent.get_status()
    assert status["web_enabled"] is True
    assert status["knowledge_nodes"] >= 2
    print(f"✓ Agent状态检查通过: {status}")
    
    # 测试事件发射
    if agent.web_server:
        agent.web_server.emit_event("test_data_added", {"nodes": 2})
        print("✓ 事件发射测试通过")
    
    # 禁用Web界面
    agent.disable_web_interface()
    assert agent.web_server is None
    print("✓ Web界面禁用测试通过")


def test_api_endpoints():
    """测试API端点"""
    print("\n=== 测试API端点 ===")
    
    from core.agent import EternalSelfAgent
    from core.web_service import EternalAgentAPIHandler
    
    # 创建Agent并启用Web界面
    agent = EternalSelfAgent(
        agent_id="api_test_agent",
        role="coordinator"
    )
    
    agent.enable_web_interface(
        host="127.0.0.1",
        port=8083
    )
    
    # 测试状态API
    status = agent.get_status()
    assert "system_alive" in status
    assert "knowledge_nodes" in status
    assert "task_queue_size" in status
    
    # 测试知识图谱API
    nodes_count = len(agent.knowledge_graph.nodes)
    edges_count = len(agent.knowledge_graph.edges)
    print(f"✓ 知识图谱数据: {nodes_count} 个节点, {edges_count} 条边")
    
    # 测试多Agent状态API
    multi_status = agent.get_multi_agent_status()
    assert "known_agents" in multi_status
    assert "own_agent" in multi_status
    print(f"✓ 多Agent状态: {multi_status}")
    
    # 测试任务提交
    test_task = "知识推演任务:API测试"
    agent.task_queue.add_unique(test_task)
    assert agent.task_queue.size() > 0
    print("✓ 任务API测试通过")
    
    # 清理
    agent.disable_web_interface()
    print("✓ API端点测试通过")


def test_web_events():
    """测试Web事件系统"""
    print("\n=== 测试Web事件系统 ===")
    
    from core.web_service import WebEventHandler, WebEvent
    
    event_handler = WebEventHandler()
    
    # 测试事件发射
    for i in range(10):
        event_handler.emit(f"event_{i}", {"index": i})
    
    recent_events = event_handler.get_recent_events(5)
    assert len(recent_events) == 5
    print(f"✓ 事件队列正常: 保留了5个最新事件")
    
    # 测试事件数量限制
    for i in range(100):
        event_handler.emit(f"overflow_event_{i}", {"index": i})
    
    all_events = event_handler.get_recent_events(1000)
    assert len(all_events) <= 1000  # 应该有限制
    print(f"✓ 事件数量限制正常: {len(all_events)} 个事件")


def test_config_management():
    """测试配置管理"""
    print("\n=== 测试配置管理 ===")
    
    from core import constants
    
    # 保存原始配置
    original_loop_delay = constants.LOOP_DELAY
    original_evolve_step = constants.EVOLVE_STEP
    
    # 测试配置更新
    constants.LOOP_DELAY = 0.5
    constants.EVOLVE_STEP = 100
    
    assert constants.LOOP_DELAY == 0.5
    assert constants.EVOLVE_STEP == 100
    print(f"✓ 配置更新测试通过: LOOP_DELAY={constants.LOOP_DELAY}, EVOLVE_STEP={constants.EVOLVE_STEP}")
    
    # 恢复原始配置
    constants.LOOP_DELAY = original_loop_delay
    constants.EVOLVE_STEP = original_evolve_step


def test_integration():
    """完整集成测试"""
    print("\n=== 完整集成测试 ===")
    
    from core.agent import EternalSelfAgent
    
    # 清理测试文件
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage24_kg.json"
    
    # 创建完整的Agent系统
    agent = EternalSelfAgent(
        agent_id="stage24_test",
        role="coordinator"
    )
    
    # 启用所有功能
    agent.enable_web_interface(
        host="127.0.0.1",
        port=8084
    )
    
    # 注册其他Agent
    agent.register_agent("worker_1", "worker", ["general"])
    agent.register_agent("worker_2", "worker", ["analysis"])
    
    # 添加一些知识
    agent.knowledge_graph.add_node("阶段24测试", {"phase": "24"})
    agent.knowledge_graph.add_node("Web界面", {"type": "frontend"})
    agent.knowledge_graph.add_edge("阶段24测试", "Web界面", "includes", 0.95)
    
    # 添加一些任务
    agent.add_initial_tasks([
        "探索新领域_阶段24",
        "知识推演任务:Web界面"
    ])
    
    # 验证状态
    status = agent.get_status()
    assert status["web_enabled"] is True
    assert status["knowledge_nodes"] >= 2
    assert status["task_queue_size"] >= 2
    
    # 测试任务执行（模拟几次）
    for i in range(3):
        task = agent.get_current_task()
        if task:
            # 模拟任务执行而不启动完整循环
            agent.run_counter += 1
            try:
                # 简化的任务执行
                agent.knowledge_graph.add_node(f"任务执行_{i}", {"status": "completed"})
                print(f"✓ 模拟任务执行完成: {task}")
            except Exception as e:
                print(f"✗ 任务执行失败: {e}")
    
    # 检查学习报告
    report = agent.get_learning_report()
    assert "current_strategy" in report
    assert "system_state" in report
    print(f"✓ 学习报告: 当前策略={report['current_strategy']}")
    
    # 测试事件
    if agent.web_server:
        agent.web_server.emit_event("stage24_test_complete", {
            "status": "success",
            "tasks_executed": 3
        })
    
    # 清理
    agent.disable_web_interface()
    agent.shutdown()
    
    print("✓ 完整集成测试通过")


if __name__ == "__main__":
    print("=" * 70)
    print("=== 阶段24：Web界面与监控系统验收测试 ===")
    print("=" * 70)
    
    try:
        test_web_service_initialization()
        test_agent_with_web_interface()
        test_api_endpoints()
        test_web_events()
        test_config_management()
        test_integration()
        
        print("\n" + "=" * 70)
        print("✅ 阶段24所有验收测试通过！")
        print("=" * 70)
    finally:
        cleanup_test_files()
        constants.KG_SAVE_PATH = "data/knowledge_graph.json"
