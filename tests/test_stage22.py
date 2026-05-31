"""
阶段22验收测试：高级自驱学习与进化
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_graph import KnowledgeGraph
from core.learning import (
    LearningTracker, 
    KnowledgeQualityAssessor, 
    AdaptiveEvolutionEngine,
    EvolutionStrategy
)
from core import constants


def cleanup_test_files():
    """清理测试文件"""
    test_path = Path("data/test_stage22_kg.json")
    for suffix in ['', '.tmp', '.bak']:
        f = test_path.with_suffix(suffix if suffix else '.json')
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_learning_tracker():
    """测试学习追踪器"""
    print("\n=== 测试学习追踪器 ===")
    
    tracker = LearningTracker()
    
    # 测试任务追踪
    tracker.start_task("task_1", "deduction", "知识推演任务:测试")
    time.sleep(0.01)
    tracker.end_task(success=True, result="Success", knowledge_used=["node_1", "node_2"])
    
    tracker.start_task("task_2", "generic", "通用任务")
    time.sleep(0.01)
    tracker.end_task(success=True, knowledge_used=["node_3"])
    
    tracker.start_task("task_3", "exploration", "探索任务")
    time.sleep(0.01)
    tracker.end_task(success=False, error="Test error", knowledge_used=[])
    
    # 验证追踪记录
    assert len(tracker.task_history) == 3
    assert tracker.get_task_success_rate() == 2/3
    print(f"  任务成功率: {tracker.get_task_success_rate():.2%}")
    
    # 验证知识使用统计
    effectiveness = tracker.get_knowledge_effectiveness("node_1")
    assert effectiveness['usage_count'] == 1
    assert effectiveness['success_rate'] == 1.0
    print(f"  知识有效性: {effectiveness}")
    
    # 验证最近性能
    recent = tracker.get_recent_performance(window_size=5)
    assert recent['task_count'] == 3
    assert recent['knowledge_produced'] >= 0
    print(f"  最近性能: {recent}")
    
    print("✓ 学习追踪器测试通过")


def test_knowledge_quality_assessor():
    """测试知识质量评估器"""
    print("\n=== 测试知识质量评估器 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage22_kg.json"
    
    kg = KnowledgeGraph()
    tracker = LearningTracker()
    assessor = KnowledgeQualityAssessor(kg)
    
    # 添加测试节点
    for i in range(10):
        kg.add_node(f"测试节点_{i}", {"index": i})
    
    # 模拟知识使用
    for i in range(5):
        tracker.start_task(f"task_{i}", "generic", f"任务{i}")
        tracker.end_task(success=True, knowledge_used=[f"测试节点_{i}"])
    
    # 评估知识质量
    qualities = assessor.assess_all_knowledge(tracker)
    assert len(qualities) > 0
    print(f"  评估了 {len(qualities)} 个知识节点")
    
    # 验证质量分数计算
    for quality in qualities:
        assert 0 <= quality.quality_score <= 1
        print(f"  {quality.node_name}: 质量={quality.quality_score:.3f}, "
              f"使用={quality.usage_count}, 成功率={quality.success_rate:.2%}")
    
    # 获取低质量知识
    low_quality = assessor.get_low_quality_knowledge(tracker, threshold=0.5)
    print(f"  低质量知识数量: {len(low_quality)}")
    
    print("✓ 知识质量评估器测试通过")


def test_adaptive_evolution_engine():
    """测试自适应进化引擎"""
    print("\n=== 测试自适应进化引擎 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage22_kg.json"
    
    kg = KnowledgeGraph()
    tracker = LearningTracker()
    assessor = KnowledgeQualityAssessor(kg)
    engine = AdaptiveEvolutionEngine(kg, tracker, assessor)
    
    # 添加测试数据
    for i in range(20):
        kg.add_node(f"进化测试_{i}", {"value": i})
    
    # 模拟一些成功的任务
    for i in range(15):
        tracker.start_task(f"task_{i}", "generic", f"任务{i}")
        tracker.end_task(success=True, knowledge_used=[f"进化测试_{i}"])
    
    # 分析系统状态
    state = engine.analyze_system_state()
    print(f"  系统状态: 成功率={state['success_rate']:.2%}, "
          f"知识数={state['knowledge_count']}, "
          f"平均质量={state['avg_quality']:.3f}")
    
    # 选择进化策略
    strategy = engine.select_strategy()
    assert strategy in EvolutionStrategy
    print(f"  当前策略: {strategy.value}")
    
    # 获取策略参数
    params = engine.get_current_params()
    print(f"  策略参数: {params}")
    
    # 执行自适应进化
    result = engine.execute_adaptive_evolution()
    print(f"  进化结果: 策略={result['strategy']}, "
          f"精简={result['trimmed_nodes']}, "
          f"推理={result['new_inferences']}")
    
    # 获取进化报告
    report = engine.get_evolution_report()
    assert 'current_strategy' in report
    assert 'system_state' in report
    assert 'recommendations' in report
    print(f"  建议: {report['recommendations'][0]}")
    
    print("✓ 自适应进化引擎测试通过")


def test_evolution_strategy_selection():
    """测试进化策略选择"""
    print("\n=== 测试进化策略选择 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage22_kg.json"
    
    kg = KnowledgeGraph()
    tracker = LearningTracker()
    assessor = KnowledgeQualityAssessor(kg)
    engine = AdaptiveEvolutionEngine(kg, tracker, assessor)
    
    # 场景1：低成功率 -> 保守策略
    for i in range(5):
        tracker.start_task(f"task_{i}", "generic", f"任务{i}")
        tracker.end_task(success=False)  # 都失败
    
    strategy = engine.select_strategy()
    assert strategy == EvolutionStrategy.CONSERVATIVE
    print(f"  场景1 (低成功率): {strategy.value}")
    
    # 清空追踪器
    tracker.task_history.clear()
    
    # 场景2：高成功率 -> 激进策略
    for i in range(20):
        tracker.start_task(f"task_{i}", "generic", f"任务{i}")
        tracker.end_task(success=True)
    
    # 添加足够多的知识节点
    for i in range(20):
        kg.add_node(f"高质量节点_{i}")
    
    strategy = engine.select_strategy()
    assert strategy in [EvolutionStrategy.BALANCED, EvolutionStrategy.AGGRESSIVE]
    print(f"  场景2 (高成功率): {strategy.value}")
    
    print("✓ 进化策略选择测试通过")


def test_integration_with_agent():
    """测试与智能体的集成"""
    print("\n=== 测试与智能体的集成 ===")
    
    from core.agent import EternalSelfAgent
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage22_kg.json"
    
    agent = EternalSelfAgent()
    
    # 验证学习组件存在
    assert hasattr(agent, 'learning_tracker')
    assert hasattr(agent, 'quality_assessor')
    assert hasattr(agent, 'evolution_engine')
    
    # 验证学习追踪功能
    agent.learning_tracker.start_task("test_task", "generic", "测试任务")
    agent.learning_tracker.end_task(success=True)
    assert len(agent.learning_tracker.task_history) > 0
    
    # 执行一些任务
    for i in range(5):
        agent.knowledge_graph.add_node(f"集成测试_{i}")
    
    # 获取学习报告
    report = agent.get_learning_report()
    assert 'current_strategy' in report
    print(f"  当前策略: {report['current_strategy']}")
    
    # 获取系统状态
    status = agent.get_status()
    assert 'evolution_strategy' in status
    assert 'recent_success_rate' in status
    print(f"  成功率: {status['recent_success_rate']:.2%}")
    
    print("✓ 智能体集成测试通过")


def test_long_term_learning():
    """测试长期学习效果"""
    print("\n=== 测试长期学习效果 ===")
    
    cleanup_test_files()
    constants.KG_SAVE_PATH = "data/test_stage22_kg.json"
    
    kg = KnowledgeGraph()
    tracker = LearningTracker()
    assessor = KnowledgeQualityAssessor(kg)
    engine = AdaptiveEvolutionEngine(kg, tracker, assessor)
    
    # 模拟长期学习过程
    print("  模拟50次任务执行...")
    
    for i in range(50):
        # 添加新知识
        kg.add_node(f"长期学习_{i}", {"iteration": i})
        
        # 模拟任务执行
        success = (i % 10) < 7  # 70%成功率
        tracker.start_task(f"task_{i}", "generic", f"任务{i}")
        tracker.end_task(
            success=success,
            knowledge_used=[f"长期学习_{i}"] if i > 0 else []
        )
    
    # 评估质量
    qualities = assessor.assess_all_knowledge(tracker)
    print(f"  评估了 {len(qualities)} 个知识节点")
    
    # 分析状态
    state = engine.analyze_system_state()
    print(f"  最终成功率: {state['success_rate']:.2%}")
    print(f"  平均质量: {state['avg_quality']:.3f}")
    
    # 执行进化
    result = engine.execute_adaptive_evolution()
    print(f"  最终进化: 策略={result['strategy']}")
    
    # 验证知识增长
    assert len(kg.nodes) > 40
    assert len(tracker.task_history) == 50
    
    print("✓ 长期学习效果测试通过")


if __name__ == "__main__":
    print("=" * 70)
    print("=== 阶段22：高级自驱学习与进化验收测试 ===")
    print("=" * 70)
    
    try:
        test_learning_tracker()
        test_knowledge_quality_assessor()
        test_adaptive_evolution_engine()
        test_evolution_strategy_selection()
        test_integration_with_agent()
        test_long_term_learning()
        
        print("\n" + "=" * 70)
        print("✅ 阶段22所有验收测试通过！")
        print("=" * 70)
    finally:
        cleanup_test_files()
        constants.KG_SAVE_PATH = "data/knowledge_graph.json"
