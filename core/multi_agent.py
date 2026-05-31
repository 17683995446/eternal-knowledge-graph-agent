"""
阶段23: 多Agent协作与分布式扩展
基于第一性原理，实现Agent通信协议、知识图谱分片、任务协作分配、负载均衡
"""
import json
import time
import random
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
from datetime import datetime


class MessageType(Enum):
    """Agent消息类型"""
    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETION = "task_completion"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    HEALTH_CHECK = "health_check"
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"
    DISCOVERY = "discovery"


class AgentRole(Enum):
    """Agent角色"""
    COORDINATOR = "coordinator"  # 协调者
    WORKER = "worker"            # 工作者
    HYBRID = "hybrid"            # 混合角色


@dataclass
class AgentMessage:
    """Agent间消息结构"""
    message_id: str
    from_agent: str
    to_agent: Optional[str] = None
    message_type: MessageType = MessageType.DISCOVERY
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    ttl: int = 10

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "ttl": self.ttl
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        return cls(
            message_id=data["message_id"],
            from_agent=data["from_agent"],
            to_agent=data.get("to_agent"),
            message_type=MessageType(data["message_type"]),
            content=data.get("content", {}),
            timestamp=data.get("timestamp", time.time()),
            ttl=data.get("ttl", 10)
        )


class MessageQueue:
    """分布式消息队列"""

    def __init__(self, max_size: int = 1000):
        self.queue: deque[AgentMessage] = deque(maxlen=max_size)
        self.processed_messages: Set[str] = set()
        self.max_size = max_size

    def enqueue(self, message: AgentMessage) -> bool:
        """将消息入队"""
        if message.message_id in self.processed_messages:
            return False

        if len(self.queue) >= self.max_size:
            # 队列已满，丢弃最早的消息
            self.queue.popleft()

        self.queue.append(message)
        return True

    def dequeue(self) -> Optional[AgentMessage]:
        """从队列中取出消息"""
        if not self.queue:
            return None

        message = self.queue.popleft()
        self.processed_messages.add(message.message_id)

        # 清理过期的处理记录（保留最近10000条）
        if len(self.processed_messages) > 10000:
            self.processed_messages = set(list(self.processed_messages)[-10000:])

        return message

    def peek(self) -> Optional[AgentMessage]:
        """查看队列头部消息"""
        if not self.queue:
            return None
        return self.queue[0]

    def size(self) -> int:
        """获取队列大小"""
        return len(self.queue)


@dataclass
class AgentInfo:
    """Agent信息"""
    agent_id: str
    role: AgentRole
    address: str
    status: str = "active"
    load: float = 0.0
    last_heartbeat: float = field(default_factory=time.time)
    capabilities: List[str] = field(default_factory=list)


class KnowledgeShard:
    """知识图谱分片"""

    def __init__(self, shard_id: str, owner_agent: str):
        self.shard_id = shard_id
        self.owner_agent = owner_agent
        self.nodes: Dict[str, Any] = {}
        self.edges: List[Any] = []
        self.version: int = 0
        self.last_update: float = time.time()

    def update_node(self, node_id: str, node_data: Any) -> None:
        """更新分片节点"""
        self.nodes[node_id] = node_data
        self.version += 1
        self.last_update = time.time()

    def delete_node(self, node_id: str) -> bool:
        """删除分片节点"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.version += 1
            self.last_update = time.time()
            return True
        return False

    def get_sync_data(self, since_version: int = 0) -> Dict[str, Any]:
        """获取同步数据"""
        return {
            "shard_id": self.shard_id,
            "version": self.version,
            "nodes": self.nodes,
            "edges": self.edges,
            "last_update": self.last_update
        }


class KnowledgeShardingManager:
    """知识图谱分片管理器"""

    def __init__(self, num_shards: int = 4):
        self.shards: Dict[str, KnowledgeShard] = {}
        self.num_shards = num_shards
        self.shard_assignment: Dict[str, str] = {}  # node_id -> shard_id

    def _get_shard_for_node(self, node_id: str) -> str:
        """根据节点ID获取分片ID"""
        hash_value = hash(node_id)
        shard_index = abs(hash_value) % self.num_shards
        return f"shard_{shard_index}"

    def assign_node_to_shard(self, node_id: str, agent_id: str) -> str:
        """分配节点到分片"""
        if node_id not in self.shard_assignment:
            shard_id = self._get_shard_for_node(node_id)
            if shard_id not in self.shards:
                self.shards[shard_id] = KnowledgeShard(shard_id, agent_id)
            self.shard_assignment[node_id] = shard_id
        return self.shard_assignment[node_id]

    def get_shard(self, node_id: str) -> Optional[KnowledgeShard]:
        """获取节点所在的分片"""
        shard_id = self.shard_assignment.get(node_id)
        return self.shards.get(shard_id) if shard_id else None

    def get_all_shards(self) -> Dict[str, KnowledgeShard]:
        """获取所有分片"""
        return self.shards.copy()

    def get_shards_by_agent(self, agent_id: str) -> List[KnowledgeShard]:
        """获取指定Agent拥有的分片"""
        return [shard for shard in self.shards.values() if shard.owner_agent == agent_id]


class TaskAllocator:
    """任务分配器 - 基于负载均衡的任务分配"""

    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.task_queue: deque[Dict[str, Any]] = deque()

    def register_agent(self, agent_info: AgentInfo) -> None:
        """注册Agent"""
        self.agents[agent_info.agent_id] = agent_info
        print(f"[任务分配器] 注册Agent: {agent_info.agent_id} ({agent_info.role.value})")

    def unregister_agent(self, agent_id: str) -> None:
        """注销Agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            print(f"[任务分配器] 注销Agent: {agent_id}")

    def update_agent_load(self, agent_id: str, load: float) -> None:
        """更新Agent负载"""
        if agent_id in self.agents:
            self.agents[agent_id].load = min(1.0, max(0.0, load))
            self.agents[agent_id].last_heartbeat = time.time()

    def select_best_agent(self, capabilities: Optional[List[str]] = None) -> Optional[str]:
        """选择最佳Agent分配任务"""
        active_agents = [
            agent for agent in self.agents.values()
            if agent.status == "active"
        ]

        if not active_agents:
            return None

        # 筛选具有所需能力的Agent
        if capabilities:
            active_agents = [
                agent for agent in active_agents
                if any(cap in agent.capabilities for cap in capabilities)
            ]
            if not active_agents:
                # 如果没有匹配的，回退到任意活跃Agent
                active_agents = [
                    agent for agent in self.agents.values()
                    if agent.status == "active"
                ]
                if not active_agents:
                    return None

        # 基于负载选择最佳Agent
        sorted_agents = sorted(
            active_agents,
            key=lambda a: a.load
        )

        # 优先选择负载最低的Worker或Hybrid
        for agent in sorted_agents:
            if agent.role in [AgentRole.WORKER, AgentRole.HYBRID]:
                return agent.agent_id

        # 如果没有，选择负载最低的
        return sorted_agents[0].agent_id

    def allocate_task(self, task: Dict[str, Any]) -> Optional[str]:
        """分配任务"""
        capabilities = task.get("capabilities", [])
        target_agent = self.select_best_agent(capabilities)
        if target_agent:
            print(f"[任务分配器] 分配任务到Agent: {target_agent}")
        return target_agent

    def queue_task(self, task: Dict[str, Any]) -> None:
        """将任务加入队列"""
        self.task_queue.append(task)

    def process_queue(self) -> List[Tuple[str, Dict[str, Any]]]:
        """处理任务队列，分配所有待处理任务"""
        assignments = []
        while self.task_queue:
            task = self.task_queue.popleft()
            target_agent = self.allocate_task(task)
            if target_agent:
                assignments.append((target_agent, task))
            else:
                # 没有可用Agent，放回队列
                self.task_queue.append(task)
                break
        return assignments


class AgentMonitor:
    """Agent系统监控器"""

    def __init__(self, heartbeat_timeout: float = 30.0):
        self.agent_states: Dict[str, AgentInfo] = {}
        self.heartbeat_timeout = heartbeat_timeout
        self.metrics: Dict[str, List[float]] = {}
        self.alert_thresholds: Dict[str, float] = {
            "high_load": 0.8,
            "timeout": heartbeat_timeout
        }

    def register_agent(self, agent_info: AgentInfo) -> None:
        """注册监控的Agent"""
        self.agent_states[agent_info.agent_id] = agent_info
        self.metrics[agent_info.agent_id] = []
        print(f"[监控器] 开始监控Agent: {agent_info.agent_id}")

    def update_agent_state(self, agent_id: str, status: str, load: float) -> None:
        """更新Agent状态"""
        if agent_id in self.agent_states:
            self.agent_states[agent_id].status = status
            self.agent_states[agent_id].load = load
            self.agent_states[agent_id].last_heartbeat = time.time()

            # 记录指标
            self.metrics[agent_id].append(load)
            # 保持最近100条
            if len(self.metrics[agent_id]) > 100:
                self.metrics[agent_id] = self.metrics[agent_id][-100:]

    def check_agent_health(self) -> List[str]:
        """检查Agent健康状态，返回不健康的Agent列表"""
        unhealthy_agents = []
        current_time = time.time()

        for agent_id, agent in self.agent_states.items():
            time_since_heartbeat = current_time - agent.last_heartbeat
            if time_since_heartbeat > self.heartbeat_timeout:
                agent.status = "unhealthy"
                unhealthy_agents.append(agent_id)
                print(f"[监控器] Agent {agent_id} 健康检查失败，标记为unhealthy")
            elif agent.load > self.alert_thresholds["high_load"]:
                print(f"[监控器] Agent {agent_id} 负载过高: {agent.load:.2f}")

        return unhealthy_agents

    def get_system_load(self) -> Dict[str, Any]:
        """获取系统整体负载情况"""
        active_agents = [
            agent for agent in self.agent_states.values()
            if agent.status == "active"
        ]

        if not active_agents:
            return {
                "total_agents": len(self.agent_states),
                "active_agents": 0,
                "avg_load": 0.0,
                "max_load": 0.0
            }

        loads = [agent.load for agent in active_agents]
        return {
            "total_agents": len(self.agent_states),
            "active_agents": len(active_agents),
            "avg_load": sum(loads) / len(loads),
            "max_load": max(loads) if loads else 0.0
        }

    def get_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """获取特定Agent的指标"""
        if agent_id not in self.agent_states or agent_id not in self.metrics:
            return {}

        metrics = self.metrics[agent_id]
        agent = self.agent_states[agent_id]

        return {
            "agent_id": agent_id,
            "status": agent.status,
            "current_load": agent.load,
            "avg_load": sum(metrics) / len(metrics) if metrics else 0.0,
            "metrics_count": len(metrics)
        }


class MultiAgentCoordinator:
    """多Agent协调器"""

    def __init__(self, own_agent_id: str, role: AgentRole = AgentRole.HYBRID):
        self.own_agent_id = own_agent_id
        self.role = role
        self.message_queue = MessageQueue()
        self.sharding_manager = KnowledgeShardingManager()
        self.task_allocator = TaskAllocator()
        self.monitor = AgentMonitor()
        self.known_agents: Dict[str, AgentInfo] = {}

        # 注册自己
        self_info = AgentInfo(
            agent_id=own_agent_id,
            role=role,
            address=f"local:{own_agent_id}",
            capabilities=["general", "coordination"]
        )
        self.known_agents[own_agent_id] = self_info
        self.task_allocator.register_agent(self_info)
        self.monitor.register_agent(self_info)

        print(f"[多Agent协调器] 初始化完成: {own_agent_id} ({role.value})")

    def send_message(self, to_agent: str, message_type: MessageType,
                    content: Dict[str, Any]) -> str:
        """发送消息"""
        message_id = f"msg_{int(time.time())}_{random.randint(1000, 9999)}"
        message = AgentMessage(
            message_id=message_id,
            from_agent=self.own_agent_id,
            to_agent=to_agent,
            message_type=message_type,
            content=content
        )

        # 在本地模式下，直接入队
        if to_agent in self.known_agents:
            print(f"[协调器] 发送消息: {message_type.value} 到 {to_agent}")
            # 这里简化实现，实际分布式需要网络传输
            # 暂时直接入自己的队列用于模拟
            self.message_queue.enqueue(message)

        return message_id

    def broadcast_message(self, message_type: MessageType,
                         content: Dict[str, Any]) -> List[str]:
        """广播消息到所有已知Agent"""
        message_ids = []
        for agent_id in self.known_agents:
            if agent_id != self.own_agent_id:
                msg_id = self.send_message(agent_id, message_type, content)
                message_ids.append(msg_id)
        return message_ids

    def receive_message(self) -> Optional[AgentMessage]:
        """接收消息"""
        message = self.message_queue.dequeue()
        if message:
            print(f"[协调器] 接收消息: {message.message_type.value} 来自 {message.from_agent}")
        return message

    def register_remote_agent(self, agent_info: AgentInfo) -> None:
        """注册远程Agent"""
        if agent_info.agent_id not in self.known_agents:
            self.known_agents[agent_info.agent_id] = agent_info
            self.task_allocator.register_agent(agent_info)
            self.monitor.register_agent(agent_info)
            print(f"[协调器] 注册远程Agent: {agent_info.agent_id}")

    def process_agent_communication(self) -> List[Dict[str, Any]]:
        """处理Agent间通信，返回处理结果"""
        processed_results = []

        while True:
            message = self.receive_message()
            if not message:
                break

            result = self._handle_message(message)
            if result:
                processed_results.append(result)

        # 检查Agent健康状态
        unhealthy_agents = self.monitor.check_agent_health()
        if unhealthy_agents:
            processed_results.append({
                "type": "health_alert",
                "agents": unhealthy_agents
            })

        # 处理任务队列
        assignments = self.task_allocator.process_queue()
        if assignments:
            processed_results.append({
                "type": "task_assignments",
                "assignments": assignments
            })

        return processed_results

    def _handle_message(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """处理收到的消息"""
        if message.message_type == MessageType.DISCOVERY:
            return self._handle_discovery(message)
        elif message.message_type == MessageType.HEALTH_CHECK:
            return self._handle_health_check(message)
        elif message.message_type == MessageType.TASK_ASSIGNMENT:
            return self._handle_task_assignment(message)
        elif message.message_type == MessageType.TASK_COMPLETION:
            return self._handle_task_completion(message)
        elif message.message_type == MessageType.KNOWLEDGE_SHARING:
            return self._handle_knowledge_sharing(message)
        elif message.message_type == MessageType.SYNC_REQUEST:
            return self._handle_sync_request(message)
        else:
            return {"type": "ignored", "message_id": message.message_id}

    def _handle_discovery(self, message: AgentMessage) -> Dict[str, Any]:
        """处理发现消息"""
        agent_info = AgentInfo(
            agent_id=message.from_agent,
            role=AgentRole(message.content.get("role", "worker")),
            address=message.content.get("address", ""),
            capabilities=message.content.get("capabilities", [])
        )
        self.register_remote_agent(agent_info)
        return {"type": "discovery", "agent": message.from_agent}

    def _handle_health_check(self, message: AgentMessage) -> Dict[str, Any]:
        """处理健康检查消息"""
        agent_id = message.from_agent
        load = message.content.get("load", 0.0)
        self.monitor.update_agent_state(agent_id, "active", load)
        return {"type": "health_check", "agent": agent_id}

    def _handle_task_assignment(self, message: AgentMessage) -> Dict[str, Any]:
        """处理任务分配消息"""
        task = message.content.get("task", {})
        return {"type": "task_received", "task": task, "from": message.from_agent}

    def _handle_task_completion(self, message: AgentMessage) -> Dict[str, Any]:
        """处理任务完成消息"""
        task = message.content.get("task", {})
        result = message.content.get("result", {})
        agent_id = message.from_agent
        self.task_allocator.update_agent_load(agent_id, result.get("load", 0.0))
        return {"type": "task_completed", "task": task, "from": agent_id}

    def _handle_knowledge_sharing(self, message: AgentMessage) -> Dict[str, Any]:
        """处理知识共享消息"""
        shard_data = message.content.get("shard_data", {})
        if shard_data:
            shard_id = shard_data.get("shard_id")
            if shard_id not in self.sharding_manager.shards:
                # 简化实现
                pass
        return {"type": "knowledge_received", "from": message.from_agent}

    def _handle_sync_request(self, message: AgentMessage) -> Dict[str, Any]:
        """处理同步请求消息"""
        return {"type": "sync_response", "to": message.from_agent}

    def assign_task(self, task: Dict[str, Any]) -> Optional[str]:
        """分配任务到合适的Agent"""
        return self.task_allocator.allocate_task(task)

    def queue_task(self, task: Dict[str, Any]) -> None:
        """将任务加入分配队列"""
        self.task_allocator.queue_task(task)

    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        load_info = self.monitor.get_system_load()
        return {
            "own_agent": self.own_agent_id,
            "role": self.role.value,
            "known_agents": list(self.known_agents.keys()),
            "queue_size": self.message_queue.size(),
            "load_info": load_info
        }
