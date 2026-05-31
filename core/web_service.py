"""
阶段24：Web界面与监控系统
基于轻量级HTTP框架的Web服务，提供知识图谱可视化、监控和配置管理
"""
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass, field

from core import constants
from core.knowledge_graph import KnowledgeGraph
from core.multi_agent import MultiAgentCoordinator


@dataclass
class WebServerConfig:
    """Web服务器配置"""
    host: str = "127.0.0.1"
    port: int = 8080
    enable_cors: bool = True


@dataclass
class WebEvent:
    """Web事件数据结构"""
    event_type: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)


class WebEventHandler:
    """Web事件处理器，管理实时事件流"""
    
    def __init__(self):
        self.events: List[WebEvent] = []
        self.max_events: int = 1000
        self.subscribers: List[Any] = []
    
    def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """发出事件"""
        event = WebEvent(event_type=event_type, data=data)
        self.events.append(event)
        
        # 保持最多max_events个事件
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        # 通知订阅者
        for subscriber in self.subscribers:
            try:
                subscriber.on_event(event)
            except Exception:
                pass
    
    def get_recent_events(self, limit: int = 100) -> List[WebEvent]:
        """获取最近的事件"""
        return self.events[-limit:]


class EternalAgentAPIHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""
    
    agent = None
    event_handler = None
    template_path = None
    
    def do_GET(self) -> None:
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        try:
            if path == "/" or path == "/index.html":
                self._serve_index()
            elif path == "/api/status":
                self._handle_api_status()
            elif path == "/api/knowledge/graph":
                self._handle_api_knowledge_graph()
            elif path == "/api/knowledge/nodes":
                self._handle_api_knowledge_nodes(query_params)
            elif path == "/api/knowledge/edges":
                self._handle_api_knowledge_edges(query_params)
            elif path == "/api/tasks":
                self._handle_api_tasks()
            elif path == "/api/events":
                self._handle_api_events(query_params)
            elif path == "/api/agents":
                self._handle_api_agents()
            elif path == "/api/plugins":
                self._handle_api_plugins()
            elif path == "/api/config":
                self._handle_api_config_get()
            elif path == "/api/health":
                self._handle_api_health()
            else:
                self._send_response(404, {"error": "Not found"})
        except Exception as e:
            self._send_response(500, {"error": str(e)})
    
    def do_POST(self) -> None:
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = json.loads(self.rfile.read(content_length)) if content_length > 0 else {}
            
            if path == "/api/config":
                self._handle_api_config_set(post_data)
            elif path == "/api/tasks":
                self._handle_api_task_submit(post_data)
            elif path == "/api/plugins/load":
                self._handle_api_plugins_load(post_data)
            elif path == "/api/plugins/activate":
                self._handle_api_plugins_activate(post_data)
            elif path == "/api/plugins/deactivate":
                self._handle_api_plugins_deactivate(post_data)
            elif path == "/api/knowledge/extract":
                self._handle_api_knowledge_extract(post_data)
            else:
                self._send_response(404, {"error": "Not found"})
        except Exception as e:
            self._send_response(500, {"error": str(e)})
    
    def _serve_index(self) -> None:
        """提供主页面"""
        html = self._generate_html()
        self._send_response_html(html)
    
    def _generate_html(self) -> str:
        """生成主HTML页面"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>永动知识图谱智能体 - 控制面板</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header h1 {
            color: #667eea;
            font-size: 28px;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 18px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .stat-value {
            font-weight: bold;
            color: #764ba2;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
        }
        .btn:hover {
            background: #764ba2;
        }
        .btn-danger {
            background: #e74c3c;
        }
        .btn-danger:hover {
            background: #c0392b;
        }
        #graph-container {
            width: 100%;
            height: 500px;
            background: #f8f9fa;
            border-radius: 8px;
            overflow: hidden;
        }
        .node-info {
            margin-top: 15px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
        }
        .log-container {
            background: #1e1e1e;
            color: #00ff00;
            padding: 15px;
            border-radius: 8px;
            height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        .config-form label {
            display: block;
            margin-bottom: 5px;
            color: #666;
        }
        .config-form input, .config-form select {
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 永动知识图谱智能体</h1>
            <p>基于三大核心公理的自驱进化智能系统</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📊 系统状态</h3>
                <div id="status-container">
                    <div class="stat">
                        <span>系统运行时间</span>
                        <span class="stat-value" id="uptime">-</span>
                    </div>
                    <div class="stat">
                        <span>知识节点数</span>
                        <span class="stat-value" id="node-count">-</span>
                    </div>
                    <div class="stat">
                        <span>知识边数</span>
                        <span class="stat-value" id="edge-count">-</span>
                    </div>
                    <div class="stat">
                        <span>任务队列大小</span>
                        <span class="stat-value" id="task-count">-</span>
                    </div>
                    <div class="stat">
                        <span>Agent数量</span>
                        <span class="stat-value" id="agent-count">-</span>
                    </div>
                </div>
                <button class="btn" onclick="refreshStatus()">刷新状态</button>
            </div>
            
            <div class="card">
                <h3>⚡ 快速操作</h3>
                <button class="btn" onclick="addTestNode()">添加测试节点</button>
                <button class="btn" onclick="triggerEvolution()">触发进化</button>
                <button class="btn btn-danger" onclick="clearLogs()">清空日志</button>
            </div>
            
            <div class="card">
                <h3>🏥 健康检查</h3>
                <div id="health-status">
                    <div class="stat">
                        <span>健康状态</span>
                        <span class="stat-value" id="health-state">检查中...</span>
                    </div>
                    <div class="stat">
                        <span>最后检查</span>
                        <span class="stat-value" id="health-check-time">-</span>
                    </div>
                </div>
                <button class="btn" onclick="checkHealth()">立即检查</button>
            </div>
        </div>
        
        <div class="card">
            <h3>🔍 知识图谱可视化</h3>
            <div id="graph-container">
                <svg id="knowledge-graph" width="100%" height="100%"></svg>
            </div>
            <div class="node-info" id="node-info">
                点击节点查看详情
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📝 任务管理</h3>
                <div id="tasks-container">
                    <p>加载任务中...</p>
                </div>
                <form id="task-form" class="config-form" onsubmit="return submitTask(event)">
                    <label>新任务描述</label>
                    <input type="text" id="new-task" placeholder="输入任务描述...">
                    <button class="btn" type="submit">提交任务</button>
                </form>
            </div>
            
            <div class="card">
                <h3>⚙️ 配置管理</h3>
                <form id="config-form" class="config-form" onsubmit="return updateConfig(event)">
                    <label>主循环间隔 (秒)</label>
                    <input type="number" id="loop-delay" min="0.1" step="0.1" value="1">
                    <label>进化步数间隔</label>
                    <input type="number" id="evolve-step" min="1" step="1" value="50">
                    <button class="btn" type="submit">更新配置</button>
                </form>
            </div>
        </div>
        
        <div class="card">
            <h3>📜 实时日志</h3>
            <div class="log-container" id="log-container"></div>
        </div>
    </div>

    <script>
        let logs = [];
        let refreshInterval = null;
        
        function addLog(message, type = "info") {
            const time = new Date().toLocaleTimeString();
            logs.push({ time, message, type });
            if (logs.length > 100) logs.shift();
            renderLogs();
        }
        
        function renderLogs() {
            const container = document.getElementById("log-container");
            container.innerHTML = logs.map(log => `
                <div style="color: ${log.type === 'error' ? '#ff6666' : '#00ff00'}">
                    [${log.time}] ${log.message}
                </div>
            `).join("");
            container.scrollTop = container.scrollHeight;
        }
        
        function clearLogs() {
            logs = [];
            renderLogs();
            addLog("日志已清空");
        }
        
        async function fetchAPI(url, options = {}) {
            try {
                const response = await fetch(url, options);
                return await response.json();
            } catch (e) {
                addLog("请求失败: " + e.message, "error");
                return null;
            }
        }
        
        async function refreshStatus() {
            const data = await fetchAPI("/api/status");
            if (data) {
                document.getElementById("uptime").textContent = data.uptime || "-";
                document.getElementById("node-count").textContent = data.node_count || 0;
                document.getElementById("edge-count").textContent = data.edge_count || 0;
                document.getElementById("task-count").textContent = data.task_queue_size || 0;
                document.getElementById("agent-count").textContent = data.agent_count || 0;
                addLog("状态已刷新");
            }
        }
        
        async function checkHealth() {
            const data = await fetchAPI("/api/health");
            if (data) {
                document.getElementById("health-state").textContent = data.status || "未知";
                document.getElementById("health-check-time").textContent = data.timestamp || "-";
                document.getElementById("health-state").style.color = data.status === "healthy" ? "#27ae60" : "#e74c3c";
                addLog("健康检查完成");
            }
        }
        
        async function renderGraph() {
            const data = await fetchAPI("/api/knowledge/graph");
            if (data && data.nodes && data.edges) {
                const svg = document.getElementById("knowledge-graph");
                const rect = svg.getBoundingClientRect();
                const width = rect.width;
                const height = rect.height;
                
                let svgContent = '';
                
                // 绘制边
                data.edges.forEach((edge, i) => {
                    const sourceNode = data.nodes.find(n => n.id === edge.source);
                    const targetNode = data.nodes.find(n => n.id === edge.target);
                    if (sourceNode && targetNode) {
                        const x1 = (sourceNode.id.charCodeAt(0) % 800) + 100;
                        const y1 = (sourceNode.id.charCodeAt(0) % 400) + 50;
                        const x2 = (targetNode.id.charCodeAt(0) % 800) + 100;
                        const y2 = (targetNode.id.charCodeAt(0) % 400) + 50;
                        
                        const weight = Math.min(5, Math.max(1, edge.weight * 5));
                        const opacity = Math.min(0.8, Math.max(0.2, edge.weight));
                        
                        svgContent += `
                            <line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" 
                                  stroke="#667eea" stroke-width="${weight}" 
                                  opacity="${opacity}"/>
                        `;
                    }
                });
                
                // 绘制节点
                data.nodes.forEach(node => {
                    const x = (node.id.charCodeAt(0) % 800) + 100;
                    const y = (node.id.charCodeAt(0) % 400) + 50;
                    const radius = Math.min(30, Math.max(10, (node.name.length % 20) + 10));
                    
                    svgContent += `
                        <circle cx="${x}" cy="${y}" r="${radius}" fill="#764ba2" 
                                stroke="#667eea" stroke-width="2" 
                                onclick="showNodeInfo('${node.id}')" 
                                style="cursor: pointer;"/>
                        <text x="${x}" y="${y + 4}" text-anchor="middle" fill="white" 
                              font-size="10" style="pointer-events: none;">
                            ${node.name.substring(0, 6)}
                        </text>
                    `;
                });
                
                svg.innerHTML = svgContent;
            }
        }
        
        async function showNodeInfo(nodeId) {
            const data = await fetchAPI(`/api/knowledge/nodes?id=${nodeId}`);
            if (data && data.nodes && data.nodes.length > 0) {
                const node = data.nodes[0];
                document.getElementById("node-info").innerHTML = `
                    <strong>${node.name}</strong><br/>
                    ${node.attr ? JSON.stringify(node.attr) : ''}<br/>
                    创建于: ${node.created_at}
                `;
                addLog("查看节点: " + node.name);
            }
        }
        
        async function renderTasks() {
            const data = await fetchAPI("/api/tasks");
            if (data) {
                const container = document.getElementById("tasks-container");
                if (data.tasks && data.tasks.length > 0) {
                    container.innerHTML = data.tasks.map(task => `
                        <div class="stat">
                            <span>${task.description || task}</span>
                            <span class="stat-value">${task.status || 'pending'}</span>
                        </div>
                    `).join("");
                } else {
                    container.innerHTML = "<p>暂无待处理任务</p>";
                }
            }
        }
        
        async function submitTask(event) {
            event.preventDefault();
            const taskDesc = document.getElementById("new-task").value;
            if (taskDesc) {
                await fetchAPI("/api/tasks", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ task: taskDesc })
                });
                document.getElementById("new-task").value = "";
                addLog("任务已提交: " + taskDesc);
                refreshStatus();
                renderTasks();
            }
            return false;
        }
        
        async function updateConfig(event) {
            event.preventDefault();
            const loopDelay = parseFloat(document.getElementById("loop-delay").value);
            const evolveStep = parseInt(document.getElementById("evolve-step").value);
            
            await fetchAPI("/api/config", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ loop_delay: loopDelay, evolve_step: evolveStep })
            });
            
            addLog("配置已更新");
            return false;
        }
        
        async function addTestNode() {
            const nodeName = "测试节点_" + Date.now();
            addLog("添加节点: " + nodeName);
            refreshStatus();
            renderGraph();
        }
        
        async function triggerEvolution() {
            addLog("触发进化...");
            refreshStatus();
        }
        
        async function loadConfig() {
            const data = await fetchAPI("/api/config");
            if (data) {
                document.getElementById("loop-delay").value = data.loop_delay || 1;
                document.getElementById("evolve-step").value = data.evolve_step || 50;
            }
        }
        
        async function refreshEvents() {
            const data = await fetchAPI("/api/events?limit=50");
            if (data && data.events) {
                data.events.forEach(event => {
                    addLog(`[${event.event_type}] ${JSON.stringify(event.data)}`);
                });
            }
        }
        
        async function init() {
            addLog("系统初始化中...");
            await Promise.all([
                refreshStatus(),
                checkHealth(),
                renderGraph(),
                renderTasks(),
                loadConfig(),
                refreshEvents()
            ]);
            
            refreshInterval = setInterval(() => {
                refreshStatus();
                renderGraph();
                renderTasks();
            }, 5000);
            
            addLog("系统已就绪！");
        }
        
        window.addEventListener("load", init);
    </script>
</body>
</html>
"""
    
    def _handle_api_status(self) -> None:
        """处理状态API请求"""
        if self.agent:
            status = self.agent.get_status()
            response = {
                "uptime": "运行中",
                "node_count": status.get("knowledge_nodes", 0),
                "edge_count": status.get("knowledge_edges", 0),
                "task_queue_size": status.get("task_queue_size", 0),
                "agent_count": len(status.get("agent_id", 1)),
                "status": status
            }
            self._send_response(200, response)
        else:
            self._send_response(200, {"error": "Agent not initialized"})
    
    def _handle_api_knowledge_graph(self) -> None:
        """处理知识图谱API请求"""
        if self.agent and hasattr(self.agent, "knowledge_graph"):
            kg = self.agent.knowledge_graph
            
            nodes = []
            for node_id, node in kg.nodes.items():
                nodes.append({
                    "id": node_id,
                    "name": node.name,
                    "created_at": node.created_at,
                    "attr": node.attr
                })
            
            edges = []
            for edge in kg.edges:
                source_node = kg._get_node_by_name(edge.source)
                target_node = kg._get_node_by_name(edge.target)
                if source_node and target_node:
                    edges.append({
                        "id": f"{edge.source}_{edge.target}_{edge.relation}",
                        "source": source_node.id,
                        "target": target_node.id,
                        "relation": edge.relation,
                        "weight": edge.weight
                    })
            
            response = {
                "nodes": nodes,
                "edges": edges
            }
            self._send_response(200, response)
        else:
            self._send_response(404, {"error": "Knowledge graph not available"})
    
    def _handle_api_knowledge_nodes(self, params: Dict) -> None:
        """处理知识节点API请求"""
        if self.agent and hasattr(self.agent, "knowledge_graph"):
            kg = self.agent.knowledge_graph
            
            node_id = params.get("id", [None])[0]
            nodes = []
            
            if node_id:
                if node_id in kg.nodes:
                    node = kg.nodes[node_id]
                    nodes.append({
                        "id": node_id,
                        "name": node.name,
                        "created_at": node.created_at,
                        "attr": node.attr
                    })
            else:
                for nid, node in kg.nodes.items():
                    nodes.append({
                        "id": nid,
                        "name": node.name,
                        "created_at": node.created_at,
                        "attr": node.attr
                    })
            
            self._send_response(200, {"nodes": nodes})
        else:
            self._send_response(404, {"error": "Not available"})
    
    def _handle_api_knowledge_edges(self, params: Dict) -> None:
        """处理知识边API请求"""
        if self.agent and hasattr(self.agent, "knowledge_graph"):
            kg = self.agent.knowledge_graph
            edges = []
            
            for edge in kg.edges:
                edges.append({
                    "source": edge.source,
                    "target": edge.target,
                    "relation": edge.relation,
                    "weight": edge.weight,
                    "created_at": edge.created_at
                })
            
            self._send_response(200, {"edges": edges})
        else:
            self._send_response(404, {"error": "Not available"})
    
    def _handle_api_tasks(self) -> None:
        """处理任务API请求"""
        if self.agent and hasattr(self.agent, "task_queue"):
            tasks = []
            queue = self.agent.task_queue
            
            # 简单获取队列任务
            if hasattr(queue, 'queue'):
                for task in queue.queue:
                    tasks.append({"description": task, "status": "pending"})
            
            self._send_response(200, {"tasks": tasks})
        else:
            self._send_response(404, {"error": "Not available"})
    
    def _handle_api_task_submit(self, data: Dict) -> None:
        """处理任务提交API请求"""
        if self.agent and hasattr(self.agent, "task_queue"):
            task = data.get("task")
            if task:
                self.agent.task_queue.add_unique(task)
                if self.event_handler:
                    self.event_handler.emit("task_submitted", {"task": task})
                self._send_response(200, {"success": True, "task": task})
            else:
                self._send_response(400, {"error": "No task provided"})
        else:
            self._send_response(404, {"error": "Not available"})
    
    def _handle_api_events(self, params: Dict) -> None:
        """处理事件API请求"""
        if self.event_handler:
            limit = int(params.get("limit", [50])[0])
            events = self.event_handler.get_recent_events(limit)
            events_dict = [
                {
                    "event_type": e.event_type,
                    "data": e.data,
                    "timestamp": e.timestamp
                } for e in events
            ]
            self._send_response(200, {"events": events_dict})
        else:
            self._send_response(200, {"events": []})
    
    def _handle_api_agents(self) -> None:
        """处理Agent API请求"""
        if self.agent and hasattr(self.agent, "multi_agent_coordinator"):
            status = self.agent.get_multi_agent_status()
            self._send_response(200, status)
        else:
            self._send_response(404, {"error": "Not available"})
    
    def _handle_api_config_get(self) -> None:
        """处理配置获取API请求"""
        config = {
            "loop_delay": constants.LOOP_DELAY,
            "evolve_step": constants.EVOLVE_STEP
        }
        self._send_response(200, config)
    
    def _handle_api_config_set(self, data: Dict) -> None:
        """处理配置更新API请求"""
        if "loop_delay" in data:
            constants.LOOP_DELAY = float(data["loop_delay"])
        if "evolve_step" in data:
            constants.EVOLVE_STEP = int(data["evolve_step"])
        
        if self.event_handler:
            self.event_handler.emit("config_updated", data)
        
        self._send_response(200, {"success": True})
    
    def _handle_api_health(self) -> None:
        """处理健康检查API请求"""
        health_status = "healthy"
        timestamp = datetime.now().isoformat()
        
        response = {
            "status": health_status,
            "timestamp": timestamp
        }
        self._send_response(200, response)
    
    def _handle_api_plugins(self) -> None:
        """处理插件列表API请求"""
        if self.agent and hasattr(self.agent, "get_plugin_status"):
            plugins = self.agent.get_plugin_status()
            discovered = self.agent.discover_plugins() if hasattr(self.agent, "discover_plugins") else []
            response = {
                "plugins": plugins,
                "discovered": discovered
            }
            self._send_response(200, response)
        else:
            self._send_response(404, {"error": "Not available"})
    
    def _handle_api_plugins_load(self, data: Dict) -> None:
        """处理插件加载API请求"""
        if self.agent and hasattr(self.agent, "load_plugin"):
            plugin_path = data.get("path")
            plugin_id = data.get("id")
            if plugin_path:
                success = self.agent.load_plugin(plugin_path, plugin_id)
                self._send_response(200, {"success": success, "plugin_path": plugin_path})
            else:
                self._send_response(400, {"error": "No plugin path provided"})
        else:
            self._send_response(404, {"error": "Not available"})
    
    def _handle_api_plugins_activate(self, data: Dict) -> None:
        """处理插件激活API请求"""
        if self.agent and hasattr(self.agent, "activate_plugin"):
            plugin_id = data.get("id")
            config = data.get("config")
            if plugin_id:
                success = self.agent.activate_plugin(plugin_id, config)
                self._send_response(200, {"success": success, "plugin_id": plugin_id})
            else:
                self._send_response(400, {"error": "No plugin ID provided"})
        else:
            self._send_response(404, {"error": "Not available"})
    
    def _handle_api_plugins_deactivate(self, data: Dict) -> None:
        """处理插件停用API请求"""
        if self.agent and hasattr(self.agent, "deactivate_plugin"):
            plugin_id = data.get("id")
            if plugin_id:
                success = self.agent.deactivate_plugin(plugin_id)
                self._send_response(200, {"success": success, "plugin_id": plugin_id})
            else:
                self._send_response(400, {"error": "No plugin ID provided"})
        else:
            self._send_response(404, {"error": "Not available"})
    
    def _handle_api_knowledge_extract(self, data: Dict) -> None:
        """处理知识抽取API请求"""
        if self.agent and hasattr(self.agent, "extract_knowledge_from_source"):
            source = data.get("source")
            if source:
                knowledge = self.agent.extract_knowledge_from_source(source)
                self._send_response(200, {"success": True, "knowledge_count": len(knowledge), "knowledge": knowledge})
            else:
                self._send_response(400, {"error": "No source provided"})
        else:
            self._send_response(404, {"error": "Not available"})
    
    def _send_response(self, status_code: int, data: Dict) -> None:
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        if self.agent and hasattr(self.agent, "web_config"):
            if self.agent.web_config.enable_cors:
                self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def _send_response_html(self, html: str) -> None:
        """发送HTML响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args) -> None:
        """禁用默认日志"""
        pass


class EternalAgentWebServer:
    """Web服务器主类"""
    
    def __init__(self, agent=None, config: Optional[WebServerConfig] = None):
        self.agent = agent
        self.config = config or WebServerConfig()
        self.server = None
        self.server_thread = None
        self.event_handler = WebEventHandler()
        self.running = False
        
        # 关联Agent与处理器
        EternalAgentAPIHandler.agent = agent
        EternalAgentAPIHandler.event_handler = self.event_handler
    
    def start(self) -> None:
        """启动Web服务器"""
        if self.running:
            return
        
        self.running = True
        self.server = HTTPServer((self.config.host, self.config.port), EternalAgentAPIHandler)
        
        self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
        self.server_thread.start()
        
        self.emit_event("server_started", {
            "host": self.config.host,
            "port": self.config.port
        })
        
        print(f"[Web服务] 已启动于 http://{self.config.host}:{self.config.port}")
    
    def _server_loop(self) -> None:
        """服务器主循环"""
        if self.server:
            try:
                self.server.serve_forever()
            except Exception as e:
                if self.running:
                    print(f"[Web服务] 错误: {e}")
    
    def stop(self) -> None:
        """停止Web服务器"""
        self.running = False
        if self.server:
            self.server.shutdown()
        if self.server_thread:
            self.server_thread.join(timeout=5)
        
        self.emit_event("server_stopped", {})
        print("[Web服务] 已停止")
    
    def emit_event(self, event_type: str, data: Dict) -> None:
        """发出事件"""
        if self.event_handler:
            self.event_handler.emit(event_type, data)
    
    def get_url(self) -> str:
        """获取访问URL"""
        return f"http://{self.config.host}:{self.config.port}"

