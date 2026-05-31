
"""
自驱进化层 + 存续保活层主体类
"""

import time
from typing import List, Optional, Dict, Any
from core.knowledge_graph import KnowledgeGraph
from core.constants import LOOP_DELAY, EVOLVE_STEP
from core.survival import SurvivalGuard, isolated
from core.task_queue import TaskQueue
from core.health import HealthChecker
from core.state_machine import SystemState, StateMachine
from core.evolution import EvolutionLayer
from core.plugins import PluginManager


class EternalSelfAgent:
    """自驱进化层 + 存续保活层主体类"""
    def __init__(self, agent_id: str = "main_agent", role: str = "hybrid"):
        # 存续保活层
        self.system_alive = True
        self.run_counter = 0
        self.error_count_today = 0
        self.last_error_time = 0
        self.agent_id = agent_id
        
        # 健康检查器
        self.survival_guard = SurvivalGuard(self)
        self.health_checker = HealthChecker(self)
        
        # 状态机
        self.state_machine = StateMachine()
        
        # 知识记忆层
        self.knowledge_graph = KnowledgeGraph()
        
        # 任务队列
        self.task_queue = TaskQueue()
        
        # 自驱进化层
        self.evolution_layer = EvolutionLayer(self.knowledge_graph, self.task_queue)
        
        # 空闲进化器和功耗管理器
        from core.idle_evolution import IdleEvolver
        from core.power_manager import PowerManager
        self.idle_evolver = IdleEvolver(self)
        self.power_manager = PowerManager(self)
        
        # 学习追踪器和自适应进化引擎
        from core.learning import (
            LearningTracker, 
            KnowledgeQualityAssessor, 
            AdaptiveEvolutionEngine
        )
        self.learning_tracker = LearningTracker()
        self.quality_assessor = KnowledgeQualityAssessor(self.knowledge_graph)
        self.evolution_engine = AdaptiveEvolutionEngine(
            self.knowledge_graph,
            self.learning_tracker,
            self.quality_assessor
        )
        
        # 多Agent协调器
        from core.multi_agent import (
            MultiAgentCoordinator,
            AgentRole
        )
        agent_role = AgentRole(role)
        self.multi_agent_coordinator = MultiAgentCoordinator(
            own_agent_id=agent_id,
            role=agent_role
        )
        
        # Web服务器
        self.web_server = None
        self.web_config = None
        
        # 插件管理器
        self.plugin_manager = PluginManager()
        self.plugin_manager.set_agent(self)
        
        # 规则推理引擎
        from core.reasoning_engine import RuleEngine
        self.reasoning_engine = RuleEngine(self.knowledge_graph)
        
        # 时间序列知识管理器
        from core.temporal_knowledge import TemporalKnowledgeGraph
        self.temporal_kg = TemporalKnowledgeGraph(self.knowledge_graph)
        
        # 知识冲突检测与解决器
        from core.knowledge_conflict_resolver import KnowledgeConflictResolver, ResolutionStrategy
        self.conflict_resolver = KnowledgeConflictResolver(self.knowledge_graph)
        
        # 知识验证与置信度评分器
        from core.knowledge_verifier import KnowledgeVerifier, KnowledgeSource
        self.knowledge_verifier = KnowledgeVerifier(self.knowledge_graph)
        
        # 知识版本管理器
        from core.knowledge_version_manager import KnowledgeVersionManager
        self.version_manager = KnowledgeVersionManager(self.knowledge_graph)
        
        # 专业领域知识管理器
        from core.domain_knowledge_manager import DomainKnowledgeManager
        self.domain_knowledge_manager = DomainKnowledgeManager(self.knowledge_graph)
        
        # 领域知识搜索与推荐器
        from core.domain_knowledge_search import DomainKnowledgeSearcher, SearchType
        self.domain_searcher = DomainKnowledgeSearcher(self.domain_knowledge_manager)
        
        # 领域知识导入导出管理器
        from core.domain_knowledge_io import DomainKnowledgeIO
        self.domain_io = DomainKnowledgeIO(self.domain_knowledge_manager)
        
        # 领域知识协作管理器
        from core.domain_knowledge_collaboration import DomainKnowledgeCollaboration
        self.domain_collaboration = DomainKnowledgeCollaboration(self.domain_knowledge_manager)
        
        # 领域知识可视化管理器
        from core.domain_knowledge_visualization import DomainKnowledgeVisualization
        self.domain_visualization = DomainKnowledgeVisualization(self.domain_knowledge_manager)
        
        # 领域知识质量管理器
        from core.domain_knowledge_quality import DomainKnowledgeQuality
        self.domain_quality = DomainKnowledgeQuality(self.domain_knowledge_manager)
        
        # 领域知识抽取器
        from core.domain_knowledge_extraction import DomainKnowledgeExtractor
        self.domain_extractor = DomainKnowledgeExtractor(self.domain_knowledge_manager)
        
        # 领域知识问答系统
        from core.domain_knowledge_qa import DomainKnowledgeQA
        self.domain_qa = DomainKnowledgeQA(self.domain_knowledge_manager, self.domain_searcher)
        
        # 领域知识API接口
        from core.domain_knowledge_api import DomainKnowledgeAPI
        self.domain_api = DomainKnowledgeAPI(self)
        
        # 自适应学习框架
        from core.adaptive_learning import AdaptiveLearningFramework
        self.adaptive_learning = AdaptiveLearningFramework(
            self.domain_knowledge_manager, self.domain_searcher
        )
        
        # 自然语言理解引擎
        from core.nlu_engine import NLUEngine
        self.nlu_engine = NLUEngine()
        
        # 对话管理系统
        from core.dialogue_manager import DialogueManager
        self.dialogue_manager = DialogueManager(self.domain_qa, self.domain_knowledge_manager)
        
        # 网页爬虫
        from core.web_crawler import WebCrawler
        self.web_crawler = WebCrawler(self.domain_extractor)
        
        # 多语言支持
        from core.multilingual_support import MultilingualSupport
        self.multilingual = MultilingualSupport()
        
        # 元学习系统
        from core.meta_learning import MetaLearning
        self.meta_learning = MetaLearning()
        
        # 迁移学习系统
        from core.transfer_learning import TransferLearning
        self.transfer_learning = TransferLearning(self.domain_knowledge_manager)
        
        # 终身学习系统
        from core.lifelong_learning import LifelongLearning
        self.lifelong_learning = LifelongLearning(self.domain_knowledge_manager)
        
        # 主动学习系统
        from core.active_learning import ActiveLearning
        self.active_learning = ActiveLearning(self.domain_knowledge_manager)
        
        # 持续优化系统
        from core.continuous_optimization import ContinuousOptimization
        self.continuous_optimization = ContinuousOptimization()
        
        # 高级应用系统
        from core.advanced_applications import AdvancedApplications
        self.advanced_applications = AdvancedApplications(self)
        
        # 前沿探索系统
        from core.future_exploration import FutureExploration
        self.future_exploration = FutureExploration(self)
        
        print(f"[系统启动] 永动知识图谱智能体初始化完成: {agent_id} ({role})")

    def enable_web_interface(self, host: str = "127.0.0.1", port: int = 8080, 
                           enable_cors: bool = True) -> None:
        """启用Web界面"""
        from core.web_service import EternalAgentWebServer, WebServerConfig
        
        self.web_config = WebServerConfig(
            host=host,
            port=port,
            enable_cors=enable_cors
        )
        
        self.web_server = EternalAgentWebServer(
            agent=self,
            config=self.web_config
        )
        self.web_server.start()

    def disable_web_interface(self) -> None:
        """禁用Web界面"""
        if self.web_server:
            self.web_server.stop()
            self.web_server = None
            self.web_config = None

    def health_check(self):
        """存续公理：周期自检 + 周期性进化"""
        self.run_counter += 1
        
        # 调用存续守卫检查系统健康
        self.survival_guard.check_system_health()
        
        # 定期健康检查
        if self.health_checker.should_check():
            status = self.health_checker.check()
            anomalies = self.health_checker.check_anomalies()
            
            if anomalies:
                for anomaly in anomalies:
                    print(f"[健康告警] {anomaly}")
            
            # 定期清理（每100次迭代）
            if self.run_counter % 100 == 0:
                self.health_checker.auto_cleanup()
        
        # 每固定步数自动精简知识、迭代认知
        if self.run_counter % EVOLVE_STEP == 0:
            self._periodic_evolve()
        
        # 学习追踪：定期评估知识质量
        if self.run_counter % 50 == 0:
            self._periodic_learning()
        
        # 多Agent通信处理
        if self.run_counter % 10 == 0:
            self._process_multi_agent_communication()

    def _process_multi_agent_communication(self):
        """处理多Agent间的通信"""
        results = self.multi_agent_coordinator.process_agent_communication()
        for result in results:
            if result['type'] == 'task_assignments':
                print(f"[多Agent] 任务分配: {result['assignments']}")
            elif result['type'] == 'health_alert':
                print(f"[多Agent] 健康告警: {result['agents']}")

    def _periodic_learning(self):
        """周期性学习评估"""
        print(f"[学习评估] 第 {self.run_counter} 次迭代触发")
        
        # 评估知识质量
        qualities = self.quality_assessor.assess_all_knowledge(self.learning_tracker)
        if qualities:
            avg_quality = sum(q.quality_score for q in qualities) / len(qualities)
            print(f"[学习评估] 平均知识质量: {avg_quality:.3f}")
        
        # 获取系统状态和建议
        report = self.evolution_engine.get_evolution_report()
        if report['recommendations']:
            print(f"[学习建议] {report['recommendations'][0]}")

    def _periodic_evolve(self):
        """周期性知识进化"""
        print(f"[周期进化] 第 {self.run_counter} 次迭代触发")
        
        # 知识精简
        self.knowledge_graph.trim_invalid_knowledge()
        
        # 执行自适应进化
        evolve_result = self.evolution_engine.execute_adaptive_evolution()
        print(f"[自适应进化] 策略: {evolve_result['strategy']}, "
              f"精简节点: {evolve_result['trimmed_nodes']}, "
              f"新推理: {evolve_result['new_inferences']}")
        
        # 健康检查摘要
        print(self.health_checker.get_summary())

    def self_repair(self):
        """存续公理：故障自愈、异常隔离"""
        import time

        print("[自愈] 检测到系统异常，开始自愈程序...")

        try:
            # 1. 重新加载知识图谱
            self.knowledge_graph.load()

            # 2. 重置错误计数
            self.error_count_today = 0

            # 3. 短暂休眠
            time.sleep(1)

            # 4. 记录自愈事件
            self.knowledge_graph.add_node(
                f"系统自愈_{self.run_counter}",
                {"type": "survival_event", "trigger": "self_repair"}
            )
            self.knowledge_graph.add_edge(
                f"系统自愈_{self.run_counter}",
                "系统存续",
                "维护事件",
                0.9
            )

            print("[自愈] 系统已恢复正常")
        except Exception as e:
            print(f"[自愈失败] {e}")
            pass

    def get_current_task(self):
        """获取当前待执行任务"""
        return self.task_queue.pop()

    def idle_self_evolve(self):
        """自驱公理：空闲时自动复盘、梳理知识"""
        print("[空闲进化] 系统静默休眠，维持循环不退出")
        time.sleep(LOOP_DELAY)

    @isolated
    def execute_task(self, task):
        """核心闭环：任务执行 -> 沉淀知识 -> 生成新任务"""
        print(f"[任务执行] {task}")
        
        # 学习追踪：开始任务
        task_type = self._classify_task(task)
        self.learning_tracker.start_task(
            task_id=f"task_{self.run_counter}",
            task_type=task_type,
            task_content=task
        )

        try:
            # 带策略的任务执行
            self.execute_task_with_strategy(task)

            # 1. 调取历史知识辅助当前决策
            derive_tasks = self.knowledge_graph_derive_new_tasks(task)

            # 2. 本次任务行为沉淀为新知识
            self._沉淀_task_knowledge(task)

            # 3. 知识驱动自驱：新生任务入队，维持永动闭环
            self._enqueue_derived_tasks(derive_tasks)

            # 4. 生成自驱任务
            self._generate_self_drive_tasks(task)

            print(f"[任务完成] {task} -> 衍生 {len(derive_tasks)} 个关联任务")
            
            # 学习追踪：记录成功
            knowledge_used = self._get_used_knowledge()
            self.learning_tracker.end_task(
                success=True,
                result="Task completed successfully",
                knowledge_used=knowledge_used
            )
            
            # 发出Web事件
            if self.web_server:
                self.web_server.emit_event("task_completed", {
                    "task": task,
                    "success": True
                })

            # 返回新任务
            next_iter_task = f"系统迭代任务_{self.run_counter}"
            return [next_iter_task] + derive_tasks
            
        except Exception as e:
            # 学习追踪：记录失败
            self.learning_tracker.end_task(
                success=False,
                error=str(e),
                knowledge_used=[]
            )
            
            # 发出Web事件
            if self.web_server:
                self.web_server.emit_event("task_failed", {
                    "task": task,
                    "error": str(e)
                })
            raise

    def _classify_task(self, task: str) -> str:
        """分类任务类型"""
        if task.startswith("知识推演"):
            return "deduction"
        elif task.startswith("复盘"):
            return "review"
        elif task.startswith("探索"):
            return "exploration"
        elif task.startswith("巩固"):
            return "consolidation"
        elif task.startswith("自我反思"):
            return "reflection"
        else:
            return "generic"

    def _get_used_knowledge(self) -> List[str]:
        """获取本次任务使用的知识节点ID列表"""
        used_knowledge = []
        # 返回最近添加的节点
        recent_nodes = list(self.knowledge_graph.nodes.keys())[-5:]
        return recent_nodes

    def execute_task_with_strategy(self, task: str):
        """带策略的任务执行"""
        if task.startswith("知识推演"):
            self._execute_deduction_task(task)
        elif task.startswith("复盘"):
            self._execute_review_task(task)
        elif task.startswith("探索"):
            self._execute_exploration_task(task)
        elif task.startswith("巩固"):
            self._execute_consolidation_task(task)
        else:
            self._execute_generic_task(task)

    def _execute_deduction_task(self, task: str):
        """执行推演任务"""
        target = task.replace("知识推演任务:", "")
        
        associations = self.knowledge_graph.find_strong_associations(target, threshold=0.3)
        
        for neighbor, relation, weight in associations:
            self.knowledge_graph.reinforce_edge(target, neighbor, relation, boost=0.05)
        
        print(f"[推演任务] 分析 {target} 的 {len(associations)} 个关联")

    def _execute_review_task(self, task: str):
        """执行复盘任务"""
        parts = task.split("_")
        if len(parts) >= 2:
            node_name = parts[1]
            
            node = self.knowledge_graph._get_node_by_name(node_name)
            if node:
                if node.attr.get("execution_count", 0) > 3:
                    self.knowledge_graph.add_edge(
                        node_name,
                        "高价值经验",
                        "经验积累",
                        0.9
                    )

    def _execute_exploration_task(self, task: str):
        """执行探索任务"""
        self.evolution_layer.evolve()

    def _execute_consolidation_task(self, task: str):
        """执行巩固任务"""
        parts = task.split("_")
        if len(parts) >= 4:
            source = parts[1]
            relation = parts[2]
            target = parts[3]
            
            self.knowledge_graph.reinforce_edge(source, target, relation, boost=0.1)

    def _execute_generic_task(self, task: str):
        """执行通用任务"""
        self.knowledge_graph.add_node(
            task,
            {"type": "generic_task", "category": "general"}
        )

    def _沉淀_task_knowledge(self, task: str):
        """将任务执行沉淀为知识"""
        self.knowledge_graph.add_node(
            task,
            {
                "type": "executed_task",
                "executed_at": self._get_timestamp(),
                "run_counter": self.run_counter
            }
        )
        
        next_iter_task = f"系统迭代任务_{self.run_counter}"
        self.knowledge_graph.add_edge(
            task,
            next_iter_task,
            "自主衍生",
            0.8
        )
        
        node = self.knowledge_graph._get_node_by_name(task)
        if node:
            node.attr["execution_count"] = node.attr.get("execution_count", 0) + 1
            node.attr["last_executed_at"] = self._get_timestamp()
        
        # 学习追踪：记录产生的知识
        self.learning_tracker.record_knowledge_produced(node.id if node else "")
        
        self.knowledge_graph.save()

    def _enqueue_derived_tasks(self, derive_tasks: list):
        """将衍生任务加入队列"""
        for task in derive_tasks:
            self.task_queue.add_unique(task)

    def _generate_self_drive_tasks(self, completed_task: str):
        """生成自驱任务"""
        self_task = f"自我反思_{completed_task}"
        self.task_queue.add_unique(self_task)
        
        if self.run_counter % 20 == 0:
            explore_task = f"探索新领域_{self.run_counter}"
            self.task_queue.add_unique(explore_task)

    def knowledge_graph_derive_new_tasks(self, node_name: str) -> list:
        """知识驱动推演新任务"""
        new_tasks = []
        
        associations = self.knowledge_graph.find_strong_associations(node_name, threshold=0.2)
        
        for target, relation, weight in associations:
            task = f"知识推演任务:{target}"
            new_tasks.append(task)
        
        inferred = self.knowledge_graph.infer_new_relations(node_name)
        for target, relation, weight in inferred:
            if weight > 0.2:
                task = f"推理关联_{node_name}_{relation}_{target}"
                new_tasks.append(task)
        
        return list(dict.fromkeys(new_tasks))

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()

    def safe_execute(self, func, *args, **kwargs):
        """安全执行：确保异常不穿透"""
        return self.survival_guard.guard(func)(*args, **kwargs)

    def get_status(self) -> dict:
        """获取系统状态"""
        recent_perf = self.learning_tracker.get_recent_performance()
        
        return {
            "system_alive": self.system_alive,
            "run_counter": self.run_counter,
            "knowledge_nodes": len(self.knowledge_graph.nodes),
            "knowledge_edges": len(self.knowledge_graph.edges),
            "task_queue_size": self.task_queue.size(),
            "error_count_today": self.error_count_today,
            "recent_success_rate": recent_perf['success_rate'],
            "evolution_strategy": self.evolution_engine.current_strategy.value,
            "agent_id": self.agent_id,
            "web_enabled": self.web_server is not None
        }

    def get_learning_report(self) -> dict:
        """获取学习报告"""
        return self.evolution_engine.get_evolution_report()

    def get_multi_agent_status(self) -> dict:
        """获取多Agent状态"""
        return self.multi_agent_coordinator.get_system_status()

    def register_agent(self, agent_id: str, role: str = "worker",
                      capabilities: list = None) -> None:
        """注册其他Agent"""
        from core.multi_agent import AgentInfo, AgentRole
        
        agent_info = AgentInfo(
            agent_id=agent_id,
            role=AgentRole(role),
            address=f"local:{agent_id}",
            capabilities=capabilities or ["general"]
        )
        self.multi_agent_coordinator.register_remote_agent(agent_info)
        print(f"[Agent] 注册协作Agent: {agent_id} ({role})")

    def assign_task_to_agent(self, task: dict, target_agent: str = None) -> Optional[str]:
        """分配任务给Agent"""
        if target_agent:
            self.multi_agent_coordinator.queue_task(task)
            return target_agent
        else:
            return self.multi_agent_coordinator.assign_task(task)

    def add_initial_tasks(self, tasks):
        """添加初始任务"""
        self.task_queue.add_batch_unique(tasks)

    def eternal_loop(self):
        """终极永动循环（系统心脏，永不退出）"""
        print("[主循环] 永动循环启动")
        self.state_machine.transition_to(SystemState.RUNNING, "系统启动")

        while self.system_alive:
            try:
                # 1. 状态检查
                self.health_check()

                # 2. 获取任务
                task = self.get_current_task()

                # 3. 根据状态执行
                if task is None:
                    self._handle_idle()
                else:
                    self._handle_task_execution(task)

                # 4. 休眠
                time.sleep(LOOP_DELAY)

            except KeyboardInterrupt:
                print("[主循环] 收到中断信号")
                self.shutdown()
                break
            except Exception as e:
                self._handle_loop_exception(e)

    def _handle_idle(self):
        """处理空闲状态"""
        self.state_machine.transition_to(SystemState.IDLE, "无待执行任务")

        evolve_stats = self.idle_evolver.check_and_evolve()

        if evolve_stats.get("tasks_generated", 0) > 0:
            self.state_machine.transition_to(SystemState.EVOLVING, "空闲进化")
            print(f"[空闲进化] 生成了 {evolve_stats['tasks_generated']} 个任务")
            self.state_machine.transition_to(SystemState.RUNNING, "进化完成")
            self.power_manager.record_activity()
        else:
            should_sleep, mode = self.power_manager.should_sleep()
            if should_sleep:
                self.power_manager.sleep(mode)

    def _handle_task_execution(self, task: str):
        """处理任务执行"""
        self.state_machine.transition_to(SystemState.RUNNING, f"执行任务: {task}")

        new_tasks = self.safe_execute(self.execute_task, task)
        if new_tasks:
            self.task_queue.add_batch_unique(new_tasks)

        self.task_queue.mark_completed(task)

    def _handle_loop_exception(self, exception: Exception):
        """处理循环中的异常"""
        print(f"[循环异常] {type(exception).__name__}: {exception}")

        self.error_count_today += 1

        if self.state_machine.can_transition_to(SystemState.ERROR):
            self.state_machine.transition_to(SystemState.ERROR, str(exception))
            self.self_repair()
    
    # 插件系统相关方法
    def load_plugin(self, plugin_path: str, plugin_id: Optional[str] = None) -> bool:
        """加载插件"""
        success = self.plugin_manager.load_plugin(plugin_path, plugin_id)
        if success:
            print(f"[插件] 插件加载成功: {plugin_path}")
        return success
    
    def activate_plugin(self, plugin_id: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """激活插件"""
        success = self.plugin_manager.activate_plugin(plugin_id, config)
        if success:
            print(f"[插件] 插件激活成功: {plugin_id}")
        return success
    
    def deactivate_plugin(self, plugin_id: str) -> bool:
        """停用插件"""
        success = self.plugin_manager.deactivate_plugin(plugin_id)
        if success:
            print(f"[插件] 插件停用成功: {plugin_id}")
        return success
    
    def get_plugin_status(self) -> List[Dict[str, Any]]:
        """获取插件状态"""
        infos = self.plugin_manager.get_all_plugin_infos()
        return [{
            "plugin_id": info.plugin_id,
            "name": info.name,
            "version": info.version,
            "type": info.plugin_type.value,
            "status": info.status.value,
            "last_used": info.last_used
        } for info in infos]
    
    def extract_knowledge_from_source(self, source: Any, **kwargs) -> List[Dict[str, Any]]:
        """使用插件从源抽取知识"""
        knowledge = self.plugin_manager.extract_knowledge(source, **kwargs)
        
        for item in knowledge:
            if item["type"] == "node":
                self.knowledge_graph.add_node(item["name"], item.get("properties", {}))
            elif item["type"] == "edge":
                self.knowledge_graph.add_edge(
                    item["source"],
                    item["target"],
                    item["relation_type"],
                    item.get("properties", {}).get("confidence", 0.5)
                )
        
        print(f"[知识抽取] 从源抽取并添加了 {len(knowledge)} 条知识")
        return knowledge
    
    def discover_plugins(self) -> List[str]:
        """发现插件目录中的插件"""
        plugins = self.plugin_manager.discover_plugins()
        print(f"[插件] 发现 {len(plugins)} 个插件")
        return plugins
    
    def add_inference_rule(self, rule: Any) -> bool:
        """添加推理规则"""
        return self.reasoning_engine.add_rule(rule)
    
    def remove_inference_rule(self, rule_id: str) -> bool:
        """删除推理规则"""
        return self.reasoning_engine.remove_rule(rule_id)
    
    def run_inference(self, focus_node: Optional[str] = None, 
                     max_depth: int = 3) -> List[Any]:
        """运行推理"""
        results = self.reasoning_engine.infer(focus_node, max_depth)
        print(f"[推理] 完成推理，获得 {len(results)} 个结果")
        return results
    
    def apply_inference_results(self, results: List[Any]) -> int:
        """应用推理结果到知识图谱"""
        count = self.reasoning_engine.apply_inference_results(results)
        print(f"[推理] 应用推理结果，添加了 {count} 条知识")
        return count
    
    def get_inference_stats(self) -> Dict[str, Any]:
        """获取推理统计信息"""
        return self.reasoning_engine.get_inference_stats()
    
    def auto_infer_and_apply(self, focus_node: Optional[str] = None,
                            max_depth: int = 3) -> int:
        """自动推理并应用结果"""
        results = self.run_inference(focus_node, max_depth)
        if results:
            return self.apply_inference_results(results)
        return 0
    
    def add_temporal_node(self, name: str, attr: Dict[str, Any] = None,
                         valid_from: Optional[str] = None,
                         valid_until: Optional[str] = None) -> Any:
        """添加带时间属性的节点"""
        return self.temporal_kg.add_temporal_node(name, attr, valid_from, valid_until)
    
    def add_temporal_edge(self, source: str, target: str, relation: str,
                         weight: float = 0.5,
                         valid_from: Optional[str] = None,
                         valid_until: Optional[str] = None) -> Any:
        """添加带时间属性的边"""
        return self.temporal_kg.add_temporal_edge(source, target, relation, weight, valid_from, valid_until)
    
    def query_by_time_range(self, start_time: str, end_time: str,
                          include_invalid: bool = False):
        """按时间范围查询节点和边"""
        return self.temporal_kg.query_by_time_range(start_time, end_time, include_invalid)
    
    def take_snapshot(self, description: str = "", 
                     metadata: Dict[str, Any] = None):
        """创建知识图谱快照"""
        return self.temporal_kg.take_snapshot(description, metadata)
    
    def list_snapshots(self):
        """列出所有快照"""
        return self.temporal_kg.list_snapshots()
    
    def get_temporal_stats(self) -> Dict[str, Any]:
        """获取时间序列统计信息"""
        return self.temporal_kg.get_temporal_stats()
    
    def get_node_history(self, node_id: str):
        """获取节点历史记录"""
        return self.temporal_kg.get_node_history(node_id)
    
    def get_edge_history(self, edge_id: str):
        """获取边历史记录"""
        return self.temporal_kg.get_edge_history(edge_id)
    
    def detect_conflicts(self):
        """检测知识冲突"""
        conflicts = self.conflict_resolver.detect_all_conflicts()
        print(f"[冲突检测] 检测到 {len(conflicts)} 个冲突")
        return conflicts
    
    def resolve_conflicts(self, strategy: Any = None):
        """自动解决冲突"""
        if strategy is None:
            from core.knowledge_conflict_resolver import ResolutionStrategy
            strategy = ResolutionStrategy.KEEP_NEWEST
        
        results = self.conflict_resolver.auto_resolve_all(strategy)
        print(f"[冲突解决] 解决了 {len(results)} 个冲突")
        return results
    
    def get_conflict_stats(self):
        """获取冲突统计信息"""
        return self.conflict_resolver.get_conflict_stats()
    
    def verify_all_knowledge(self):
        """验证所有知识"""
        print("[知识验证] 开始验证所有节点和边")
        
        nodes = list(self.knowledge_graph.nodes.values())
        node_confs = self.knowledge_verifier.batch_verify_nodes(nodes)
        
        edges = list(self.knowledge_graph.edges)
        edge_confs = self.knowledge_verifier.batch_verify_edges(edges)
        
        self.knowledge_verifier.save_confidences()
        
        print(f"[知识验证] 完成验证: {len(node_confs)} 个节点, {len(edge_confs)} 条边")
        return node_confs + edge_confs
    
    def register_knowledge_source(self, source_id, source_type, initial_credibility=0.7):
        """注册知识来源"""
        self.knowledge_verifier.register_source(source_id, source_type, initial_credibility)
    
    def get_knowledge_verification_stats(self):
        """获取验证统计"""
        return self.knowledge_verifier.get_verification_stats()
    
    def get_node_confidence(self, knowledge_id):
        """获取节点置信度"""
        return self.knowledge_verifier.get_knowledge_confidence(knowledge_id)
    
    def update_knowledge_confidence(self, knowledge_id, new_confidence, reason):
        """更新知识置信度"""
        return self.knowledge_verifier.update_confidence(knowledge_id, new_confidence, reason)
    
    def create_version_snapshot(self, name, description=""):
        """创建版本快照"""
        return self.version_manager.create_snapshot(name, description)
    
    def restore_version_snapshot(self, snapshot_id):
        """恢复版本快照"""
        return self.version_manager.restore_snapshot(snapshot_id)
    
    def get_version_history(self, knowledge_id=None, knowledge_type=None):
        """获取版本历史"""
        return self.version_manager.get_version_history(knowledge_id, knowledge_type)
    
    def get_version_stats(self):
        """获取版本统计"""
        return self.version_manager.get_version_stats()
    
    def get_all_snapshots(self):
        """获取所有快照"""
        return self.version_manager.get_snapshots()
    
    # 专业领域知识管理相关方法
    def create_domain_knowledge(self, template_id, name, content, tags=None, sources=None):
        """基于模板创建领域知识"""
        knowledge = self.domain_knowledge_manager.create_knowledge_from_template(
            template_id, name, content, tags, sources
        )
        if knowledge:
            print(f"[领域知识] 创建知识: {name} (ID: {knowledge.knowledge_id})")
        return knowledge
    
    def get_domain_knowledge(self, knowledge_id):
        """获取领域知识"""
        return self.domain_knowledge_manager.get_domain_knowledge(knowledge_id)
    
    def search_domain_knowledge(self, keyword, domain_type=None, tags=None):
        """搜索领域知识"""
        return self.domain_knowledge_manager.search_domain_knowledge(keyword, domain_type, tags)
    
    def update_domain_knowledge(self, knowledge_id, content_updates):
        """更新领域知识"""
        success = self.domain_knowledge_manager.update_knowledge(knowledge_id, content_updates)
        if success:
            print(f"[领域知识] 更新知识: {knowledge_id}")
        return success
    
    def delete_domain_knowledge(self, knowledge_id):
        """删除领域知识"""
        success = self.domain_knowledge_manager.delete_knowledge(knowledge_id)
        if success:
            print(f"[领域知识] 删除知识: {knowledge_id}")
        return success
    
    def enhance_knowledge_with_graph(self, knowledge):
        """利用知识图谱增强领域知识"""
        enhanced = self.domain_knowledge_manager.enhance_knowledge_with_graph(knowledge)
        print(f"[领域知识] 增强知识: {enhanced.name}")
        return enhanced
    
    def list_domain_templates(self, domain_type=None):
        """列出领域模板"""
        return self.domain_knowledge_manager.list_templates(domain_type)
    
    def get_domain_template(self, template_id):
        """获取领域模板"""
        return self.domain_knowledge_manager.get_template(template_id)
    
    def add_domain_template(self, template):
        """添加领域模板"""
        success = self.domain_knowledge_manager.add_template(template)
        if success:
            print(f"[领域知识] 添加模板: {template.template_name}")
        return success
    
    def get_domain_stats(self):
        """获取领域统计信息"""
        return self.domain_knowledge_manager.get_domain_stats()
    
    # 领域知识搜索与推荐方法
    def search_domain_knowledge(self, 
                               query: str, 
                               search_type: str = "hybrid",
                               domain_type = None,
                               tags = None,
                               limit: int = 10):
        """搜索领域知识"""
        from core.domain_knowledge_search import SearchType
        
        st_map = {
            "keyword": SearchType.KEYWORD,
            "semantic": SearchType.SEMANTIC,
            "hybrid": SearchType.HYBRID
        }
        st = st_map.get(search_type.lower(), SearchType.HYBRID)
        
        results = self.domain_searcher.search(
            query=query,
            search_type=st,
            domain_type=domain_type,
            tags=tags,
            limit=limit
        )
        
        # 记录浏览
        for result in results:
            self.domain_searcher.record_view(result.knowledge.knowledge_id)
        
        return results
    
    def get_domain_recommendations(self,
                                  source_knowledge_id = None,
                                  source_tags = None,
                                  limit: int = 5,
                                  recommend_types = None):
        """获取领域知识推荐"""
        return self.domain_searcher.get_recommendations(
            source_knowledge_id=source_knowledge_id,
            source_tags=source_tags,
            limit=limit,
            recommend_types=recommend_types
        )
    
    def get_search_statistics(self):
        """获取搜索统计信息"""
        return self.domain_searcher.get_search_statistics()
    
    # 领域知识导入导出方法
    def export_domain_knowledges(self, knowledge_ids=None, domain_type=None, format="json", file_name=None):
        """导出领域知识"""
        from core.domain_knowledge_io import ExportFormat
        fmt_map = {"json": ExportFormat.JSON, "csv": ExportFormat.CSV, "xml": ExportFormat.XML}
        fmt = fmt_map.get(format.lower(), ExportFormat.JSON)
        
        result = self.domain_io.export_knowledges(
            knowledge_ids=knowledge_ids,
            domain_type=domain_type,
            format=fmt,
            file_name=file_name
        )
        if result.success:
            print(f"[导出] 成功导出 {result.record_count} 条知识到 {result.file_path}")
        else:
            print(f"[导出] 导出失败: {result.error}")
        return result
    
    def import_domain_knowledges(self, file_path, format=None, skip_existing=True):
        """导入领域知识"""
        from core.domain_knowledge_io import ImportFormat
        fmt = None
        if format:
            fmt_map = {"json": ImportFormat.JSON, "csv": ImportFormat.CSV, "xml": ImportFormat.XML}
            fmt = fmt_map.get(format.lower())
        
        result = self.domain_io.import_knowledges(
            file_path=file_path,
            format=fmt,
            skip_existing=skip_existing
        )
        print(f"[导入] 成功导入 {result.success_count} 条知识，失败 {result.failed_count} 条")
        if result.errors:
            for error in result.errors[:3]:
                print(f"  错误: {error}")
        return result
    
    def migrate_knowledge_graph_to_domains(self):
        """从知识图谱迁移数据到领域知识系统"""
        result = self.domain_io.migrate_from_knowledge_graph()
        print(f"[迁移] 成功迁移 {result.success_count} 个节点，失败 {result.failed_count} 个")
        return result
    
    def get_export_history(self):
        """获取导出历史"""
        return self.domain_io.get_export_history()
    
    # 领域知识协作方法
    def share_domain_knowledge(self, knowledge_id, shared_by, shared_with=None, permission="read", expires_at=None):
        """共享领域知识"""
        return self.domain_collaboration.share_knowledge(
            knowledge_id=knowledge_id,
            shared_by=shared_by,
            shared_with=shared_with,
            permission=permission,
            expires_at=expires_at
        )
    
    def revoke_knowledge_share(self, share_id):
        """撤销共享"""
        return self.domain_collaboration.revoke_share(share_id)
    
    def get_shared_knowledges(self, user_id):
        """获取用户可访问的共享知识"""
        return self.domain_collaboration.get_shared_knowledges(user_id)
    
    def fork_domain_knowledge(self, knowledge_id, forked_by):
        """创建知识分支"""
        return self.domain_collaboration.fork_knowledge(knowledge_id, forked_by)
    
    def merge_knowledge_fork(self, fork_id):
        """合并分支"""
        return self.domain_collaboration.merge_fork(fork_id)
    
    def get_collaboration_stats(self):
        """获取协作统计"""
        return self.domain_collaboration.get_collaboration_stats()
    
    # 领域知识可视化方法
    def generate_domain_graph(self, domain_type=None, include_relations=True):
        """生成领域知识图谱"""
        return self.domain_visualization.generate_domain_graph(
            domain_type=domain_type,
            include_relations=include_relations
        )
    
    def generate_domain_distribution(self):
        """生成领域分布统计"""
        return self.domain_visualization.generate_domain_distribution()
    
    def generate_tag_cloud(self, top_n=20):
        """生成标签云"""
        return self.domain_visualization.generate_tag_cloud(top_n)
    
    def generate_confidence_chart(self):
        """生成置信度分布图"""
        return self.domain_visualization.generate_confidence_chart()
    
    def export_graph_to_json(self, graph, file_name=None):
        """导出图谱为JSON"""
        return self.domain_visualization.export_to_json(graph, file_name)
    
    def export_graph_to_html(self, graph, file_name=None):
        """导出图谱为HTML"""
        return self.domain_visualization.export_to_html(graph, file_name)
    
    def get_visualization_summary(self):
        """获取可视化摘要"""
        return self.domain_visualization.get_visualization_summary()
    
    # 领域知识质量评估方法
    def evaluate_knowledge_quality(self, knowledge_id):
        """评估知识质量"""
        return self.domain_quality.evaluate_knowledge(knowledge_id)
    
    def batch_evaluate_quality(self):
        """批量评估所有知识质量"""
        return self.domain_quality.batch_evaluate()
    
    def get_low_quality_knowledges(self, threshold=0.5):
        """获取低质量知识"""
        return self.domain_quality.get_low_quality_knowledges(threshold)
    
    def get_quality_report(self, knowledge_id):
        """获取质量报告"""
        return self.domain_quality.get_quality_report(knowledge_id)
    
    def generate_optimization_plan(self):
        """生成优化计划"""
        return self.domain_quality.generate_optimization_plan()
    
    # 领域知识抽取方法
    def extract_knowledge_from_text(self, text, domain_type=None):
        """从文本中抽取知识"""
        from core.domain_knowledge_manager import DomainType
        dt = None
        if domain_type:
            dt = DomainType(domain_type)
        return self.domain_extractor.extract_from_text(text, dt)
    
    def extract_knowledge_from_structured_data(self, data, domain_type, field_mapping):
        """从结构化数据中抽取知识"""
        from core.domain_knowledge_manager import DomainType
        dt = DomainType(domain_type)
        return self.domain_extractor.extract_from_structured_data(data, dt, field_mapping)
    
    def register_extracted_knowledges(self, extraction_result):
        """批量注册抽取的知识"""
        return self.domain_extractor.batch_register(extraction_result)
    
    def get_extraction_stats(self):
        """获取抽取统计"""
        return self.domain_extractor.get_extraction_stats()
    
    # 领域知识问答方法
    def ask_domain_question(self, question, session_id="default", domain_type=None):
        """回答领域知识问题"""
        from core.domain_knowledge_manager import DomainType
        dt = None
        if domain_type:
            dt = DomainType(domain_type)
        return self.domain_qa.ask(question, session_id, dt)
    
    def get_qa_history(self, session_id="default"):
        """获取问答历史"""
        return self.domain_qa.get_conversation_history(session_id)
    
    def clear_qa_history(self, session_id="default"):
        """清除问答历史"""
        return self.domain_qa.clear_conversation(session_id)
    
    # 自适应学习方法
    def add_feedback(self, knowledge_id, user_id, feedback_type, rating=None, comment="", correction=None):
        """添加用户反馈"""
        return self.adaptive_learning.add_feedback(
            knowledge_id, user_id, feedback_type, rating, comment, correction
        )
    
    def get_knowledge_feedback_stats(self, knowledge_id):
        """获取知识反馈统计"""
        return self.adaptive_learning.get_knowledge_feedback_stats(knowledge_id)
    
    def create_ab_test(self, test_name, variants):
        """创建A/B测试"""
        return self.adaptive_learning.create_ab_test(test_name, variants)
    
    def get_ab_test_results(self, test_id):
        """获取A/B测试结果"""
        return self.adaptive_learning.get_ab_test_results(test_id)
    
    def get_learning_stats(self):
        """获取学习统计"""
        return self.adaptive_learning.get_learning_stats()
    
    # 自然语言理解方法
    def parse_natural_language(self, text):
        """解析自然语言"""
        return self.nlu_engine.parse(text)
    
    def extract_keywords(self, text, top_n=5):
        """提取关键词"""
        return self.nlu_engine.extract_keywords(text, top_n)
    
    # 对话管理方法
    def chat(self, user_input, session_id="default"):
        """对话交互"""
        return self.dialogue_manager.process_input(user_input, session_id)
    
    def get_chat_history(self, session_id="default"):
        """获取对话历史"""
        return self.dialogue_manager.get_dialogue_history(session_id)
    
    def clear_chat(self, session_id="default"):
        """清除对话"""
        return self.dialogue_manager.clear_dialogue(session_id)
    
    # 网页爬虫方法
    def crawl_text(self, text, source="unknown", title=""):
        """爬取文本"""
        return self.web_crawler.crawl_text(text, source, title)
    
    def parse_document(self, content, doc_type="text"):
        """解析文档"""
        return self.web_crawler.parse_document(content, doc_type)
    
    # 多语言方法
    def detect_language(self, text):
        """检测语言"""
        return self.multilingual.detect_language(text)
    
    def translate(self, text, source_lang, target_lang):
        """翻译文本"""
        return self.multilingual.translate(text, source_lang, target_lang)
    
    # 元学习方法
    def analyze_learning_pattern(self, knowledge_id, learning_history):
        """分析学习模式"""
        return self.meta_learning.analyze_learning_pattern(knowledge_id, learning_history)
    
    def recommend_strategy(self, domain_type, user_pattern):
        """推荐学习策略"""
        return self.meta_learning.recommend_strategy(domain_type, user_pattern)
    
    # 迁移学习方法
    def transfer_knowledge(self, source_knowledge_id, target_domain, adaptation_rules=None):
        """迁移知识"""
        return self.transfer_learning.transfer_knowledge(source_knowledge_id, target_domain, adaptation_rules)
    
    def find_transfer_candidates(self, source_domain, target_domain, min_similarity=0.3):
        """查找迁移候选"""
        return self.transfer_learning.find_transfer_candidates(source_domain, target_domain, min_similarity)
    
    # 终身学习方法
    def record_learning(self, knowledge_id, difficulty=3):
        """记录学习"""
        return self.lifelong_learning.record_learning(knowledge_id, difficulty)
    
    def get_retention_status(self, knowledge_id):
        """获取知识保持状态"""
        return self.lifelong_learning.get_retention_status(knowledge_id)
    
    def get_review_recommendations(self):
        """获取复习推荐"""
        return self.lifelong_learning.get_review_recommendations()
    
    # 主动学习方法
    def get_uncertain_samples(self, sample_size=5):
        """获取不确定样本"""
        return self.active_learning.select_samples_for_labeling(sample_size)
    
    def suggest_queries(self, domain_type=None, limit=3):
        """建议查询"""
        return self.active_learning.suggest_queries(domain_type, limit)
    
    # 持续优化方法
    def record_performance(self, metric_name, value):
        """记录性能指标"""
        return self.continuous_optimization.record_metric(metric_name, value)
    
    def get_performance_report(self):
        """获取性能报告"""
        return self.continuous_optimization.get_performance_report()
    
    # 高级应用方法
    def execute_service(self, service_request):
        """执行服务"""
        return self.advanced_applications.execute_service(service_request)
    
    def create_workflow(self, workflow_name, steps):
        """创建工作流"""
        return self.advanced_applications.create_workflow(workflow_name, steps)
    
    def execute_workflow(self, workflow_id):
        """执行工作流"""
        return self.advanced_applications.execute_workflow(workflow_id)
    
    def get_available_services(self):
        """获取可用服务"""
        return self.advanced_applications.get_available_services()
    
    # 前沿探索方法
    def simulate_consciousness(self, input_context):
        """模拟意识"""
        return self.future_exploration.simulate_consciousness(input_context)
    
    def generate_creative_content(self, topic, content_type="idea"):
        """生成创意内容"""
        return self.future_exploration.generate_creative_content(topic, content_type)
    
    def ethical_evaluation(self, action, context):
        """伦理评估"""
        return self.future_exploration.ethical_evaluation(action, context)
    
    def get_consciousness_report(self):
        """获取意识报告"""
        return self.future_exploration.get_consciousness_report()

    def shutdown(self):
        """优雅关闭"""
        print("[关闭] 开始优雅关闭...")
        self.state_machine.transition_to(SystemState.SHUTDOWN, "用户请求关闭")
        self.system_alive = False
        
        # 保存插件配置
        self.plugin_manager.save_plugin_configs()
        
        # 停止Web服务器
        if self.web_server:
            self.disable_web_interface()

        # 保存最终状态
        self.knowledge_graph.save()

        print("[关闭] 系统已关闭")
