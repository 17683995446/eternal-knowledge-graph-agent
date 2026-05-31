"""
阶段20验收测试：全面验证与复杂场景测试
"""

import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent import EternalSelfAgent
from core import constants

# 清理之前的测试文件
def cleanup_test_files():
    test_path = Path("data/test_stage20_kg.json")
    for suffix in ['', '.tmp', '.bak']:
        f = test_path.with_suffix(suffix if suffix else '.json')
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_initialization_completeness():
    """测试初始化完整性"""
    print("\n=== 测试初始化完整性 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage20_kg.json"
    
    agent = EternalSelfAgent()
    
    # 验证所有组件
    assert agent is not None
    assert agent.knowledge_graph is not None
    assert agent.task_queue is not None
    assert agent.evolution_layer is not None
    assert agent.idle_evolver is not None
    assert agent.power_manager is not None
    assert agent.state_machine is not None
    assert agent.health_checker is not None
    assert agent.survival_guard is not None
    assert hasattr(agent.knowledge_graph, 'optimizer')
    
    print("✓ 初始化完整性测试通过")


def test_full_cycle_execution():
    """测试完整周期执行"""
    print("\n=== 测试完整周期执行 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage20_kg.json"
    
    agent = EternalSelfAgent()
    
    # 清空默认任务
    while agent.task_queue.pop():
        pass
    
    # 添加测试任务
    test_tasks = [
        "测试执行任务1",
        "测试执行任务2",
        "知识推演任务:目标A",
        "探索新领域"
    ]
    agent.task_queue.add_batch(test_tasks)
    
    # 执行几次完整循环
    for i in range(5):
        task = agent.get_current_task()
        if task:
            result = agent.execute_task(task)
            print(f"执行任务: {task}")
        else:
            agent._handle_idle()
        agent.health_check()
    
    # 验证知识沉淀
    assert len(agent.knowledge_graph.nodes) > 0
    print(f"✓ 知识图谱沉淀了 {len(agent.knowledge_graph.nodes)} 个节点")
    print("✓ 完整周期执行测试通过")


def test_boundary_conditions():
    """测试边界条件"""
    print("\n=== 测试边界条件 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage20_kg.json"
    
    agent = EternalSelfAgent()
    
    # 清空队列
    while agent.task_queue.pop():
        pass
    
    # 测试空队列处理
    assert agent.get_current_task() is None
    print("✓ 空队列处理正常")
    
    # 测试边界值 - 节点添加
    edge_node_names = [
        "",
        None,
        "a"*1000,
        "特殊字符:!@#$%^&*()",
        "中文测试节点"
    ]
    
    valid_count = 0
    for name in edge_node_names:
        try:
            if name:
                agent.knowledge_graph.add_node(str(name))
                valid_count +=1
        except Exception:
            # 期望对于无效值会抛出异常
            pass
    
    print(f"✓ 边界条件测试通过，有效节点: {valid_count}")


def test_large_scale_operations():
    """测试大规模操作"""
    print("\n=== 测试大规模操作 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage20_kg.json"
    
    agent = EternalSelfAgent()
    
    # 添加大量节点
    node_count = 50
    print(f"添加 {node_count} 个节点...")
    
    for i in range(node_count):
        agent.knowledge_graph.add_node(f"批量测试节点_{i}")
    
    # 添加大量边
    edge_count = 0
    for i in range(node_count -1):
        for j in range(i+1, min(i+5, node_count)):
            agent.knowledge_graph.add_edge(
                f"批量测试节点_{i}",
                f"批量测试节点_{j}",
                f"关联类型_{random.randint(0,3)}",
                random.uniform(0.1, 0.9)
            )
            edge_count += 1
    
    print(f"✓ 成功添加 {len(agent.knowledge_graph.nodes)} 个节点")
    print(f"✓ 成功添加 {len(agent.knowledge_graph.edges)} 条边")
    
    # 测试查询性能
    start_time = time.time()
    
    # 测试邻居查询
    test_node = "批量测试节点_25"
    neighbors = agent.knowledge_graph.get_neighbors(test_node)
    
    query_time = time.time() - start_time
    print(f"✓ 邻居查询完成，耗时 {query_time:.4f}秒")


def test_error_isolation():
    """测试异常隔离"""
    print("\n=== 测试异常隔离 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage20_kg.json"
    
    agent = EternalSelfAgent()
    
    # 创建一个会报错的函数
    def failing_function():
        raise ValueError("这是一个故意抛出的错误")
    
    # 使用安全执行
    result = agent.safe_execute(failing_function)
    
    # 验证没有崩溃
    assert agent.system_alive is True
    assert result is None
    print("✓ 异常隔离测试通过，系统继续运行")


def test_state_machine_transitions():
    """测试状态机转换"""
    print("\n=== 测试状态机转换 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage20_kg.json"
    
    agent = EternalSelfAgent()
    
    from core.state_machine import SystemState
    
    initial_state = agent.state_machine.current_state
    
    # 转换到各种状态
    agent.state_machine.transition_to(SystemState.IDLE, "测试空闲")
    assert agent.state_machine.current_state == SystemState.IDLE
    
    agent.state_machine.transition_to(SystemState.EVOLVING, "测试进化")
    assert agent.state_machine.current_state == SystemState.EVOLVING
    
    agent.state_machine.transition_to(SystemState.RUNNING, "测试运行")
    assert agent.state_machine.current_state == SystemState.RUNNING
    
    # 验证有历史记录
    assert len(agent.state_machine.state_history) > 0
    print("✓ 状态机转换测试通过")


def test_power_mode_switching():
    """测试功耗模式切换"""
    print("\n=== 测试功耗模式切换 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage20_kg.json"
    
    agent = EternalSelfAgent()
    
    # 清空队列
    while agent.task_queue.pop():
        pass
    
    # 深度休眠模式
    should_sleep, mode = agent.power_manager.should_sleep()
    assert should_sleep
    assert mode == "deep_sleep"
    print("✓ 深度休眠模式正常")
    
    # 轻度休眠模式
    agent.task_queue.add("轻度任务1")
    agent.task_queue.add("轻度任务2")
    should_sleep, mode = agent.power_manager.should_sleep()
    assert should_sleep
    assert mode == "light_sleep"
    print("✓ 轻度休眠模式正常")
    
    # 活跃模式
    for i in range(3, 10):
        agent.task_queue.add(f"活跃任务_{i}")
    should_sleep, mode = agent.power_manager.should_sleep()
    assert not should_sleep
    assert mode == "active"
    print("✓ 活跃模式正常")


def test_knowledge_inference():
    """测试知识推理"""
    print("\n=== 测试知识推理 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage20_kg.json"
    
    agent = EternalSelfAgent()
    
    # 创建测试知识图谱
    agent.knowledge_graph.add_node("A")
    agent.knowledge_graph.add_node("B")
    agent.knowledge_graph.add_node("C")
    agent.knowledge_graph.add_edge("A", "B", "关联", 0.7)
    agent.knowledge_graph.add_edge("B", "C", "关联", 0.8)
    
    # 测试推理
    inferences = agent.knowledge_graph.infer_new_relations("A")
    print(f"推理结果: {inferences}")
    
    # 验证推理功能正常
    assert inferences is not None
    print("✓ 知识推理测试通过")


def test_idle_evolution():
    """测试空闲进化"""
    print("\n=== 测试空闲进化 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage20_kg.json"
    
    agent = EternalSelfAgent()
    
    # 清空任务
    while agent.task_queue.pop():
        pass
    
    initial_queue_size = agent.task_queue.size()
    
    # 执行空闲进化
    evolve_result = agent.idle_evolver.check_and_evolve()
    print(f"空闲进化结果: {evolve_result}")
    
    # 验证状态
    assert hasattr(agent.idle_evolver, 'get_idle_status')
    status = agent.idle_evolver.get_idle_status()
    print(f"空闲状态: {status}")
    
    print("✓ 空闲进化测试通过")


def test_memory_management():
    """测试内存管理"""
    print("\n=== 测试内存管理 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage20_kg.json"
    
    agent = EternalSelfAgent()
    
    # 测试优化器内存优化
    if hasattr(agent.knowledge_graph, 'optimizer'):
        agent.knowledge_graph.optimizer.optimize_memory()
        print("✓ 内存优化执行成功")
        
        # 获取性能统计
        stats = agent.knowledge_graph.optimizer.get_performance_stats()
        print(f"性能统计: {stats}")
        assert 'node_count' in stats
        assert 'edge_count' in stats
    
    print("✓ 内存管理测试通过")


def test_data_consistency():
    """测试数据一致性"""
    print("\n=== 测试数据一致性 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage20_kg.json"
    
    agent = EternalSelfAgent()
    
    # 添加初始节点
    agent.knowledge_graph.add_node("一致性测试节点", {"value": "test"})
    agent.knowledge_graph.save()
    
    # 重新加载
    new_agent = EternalSelfAgent()
    
    # 验证数据保持一致
    node = new_agent.knowledge_graph.get_node_by_name("一致性测试节点")
    assert node is not None
    print("✓ 数据一致性测试通过")


def test_comprehensive_scenario():
    """测试完整综合场景"""
    print("\n=== 测试完整综合场景 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage20_kg.json"
    
    agent = EternalSelfAgent()
    
    # 模拟真实运行
    test_cycles = 20
    print(f"执行 {test_cycles} 次完整循环...")
    
    tasks_executed = 0
    for i in range(test_cycles):
        # 健康检查
        agent.health_check()
        
        # 获取任务
        task = agent.get_current_task()
        
        if task:
            # 执行任务
            result = agent.execute_task(task)
            tasks_executed += 1
        else:
            # 空闲处理
            agent._handle_idle()
    
    print(f"执行了 {tasks_executed} 个任务")
    print(f"知识图谱大小: {len(agent.knowledge_graph.nodes)} 节点")
    print(f"任务队列大小: {agent.task_queue.size()}")
    
    # 验证系统仍然正常
    assert agent.system_alive is True
    print("✓ 综合场景测试通过")


if __name__ == "__main__":
    print("="*70)
    print("=== 阶段20：全面验证与复杂场景验收测试 ===")
    print("="*70)
    
    try:
        test_initialization_completeness()
        test_full_cycle_execution()
        test_boundary_conditions()
        test_large_scale_operations()
        test_error_isolation()
        test_state_machine_transitions()
        test_power_mode_switching()
        test_knowledge_inference()
        test_idle_evolution()
        test_memory_management()
        test_data_consistency()
        test_comprehensive_scenario()
        
        print("\n" + "="*70)
        print("✅ 阶段20所有验收测试通过！")
        print("="*70)
        
    finally:
        cleanup_test_files()
        constants.KG_SAVE_PATH = "data/knowledge_graph.json"
