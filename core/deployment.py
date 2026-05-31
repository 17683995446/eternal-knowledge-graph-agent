
"""
部署和运维工具
提供系统监控、日志管理和部署辅助功能
"""
import os
import sys
import time
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: float
    node_count: int
    edge_count: int
    task_queue_size: int
    plugin_count: int
    active_plugins: int


class LoggerManager:
    """日志管理器"""
    
    def __init__(self, log_dir: Optional[str] = None):
        self.log_dir = log_dir or os.path.join(os.path.dirname(__file__), "..", "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 设置日志
        self.logger = logging.getLogger("EternalAgent")
        self.logger.setLevel(logging.INFO)
        
        # 文件处理器
        log_file = os.path.join(self.log_dir, f"agent_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """记录信息"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误"""
        self.logger.error(message)
    
    def get_recent_logs(self, limit: int = 100) -> List[str]:
        """获取最近的日志"""
        logs = []
        log_file = os.path.join(self.log_dir, f"agent_{datetime.now().strftime('%Y%m%d')}.log")
        
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    logs = lines[-limit:]
            except Exception:
                pass
        
        return logs


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.metrics_file = os.path.join(self.data_dir, "metrics.json")
        self.metrics_history: List[SystemMetrics] = []
    
    def collect_metrics(self, agent) -> SystemMetrics:
        """收集系统指标"""
        status = agent.get_status()
        
        metrics = SystemMetrics(
            timestamp=time.time(),
            node_count=status.get("knowledge_nodes", 0),
            edge_count=status.get("knowledge_edges", 0),
            task_queue_size=status.get("task_queue_size", 0),
            plugin_count=len(agent.get_plugin_status()),
            active_plugins=len([p for p in agent.get_plugin_status() if p.get("status") == "active"])
        )
        
        self.metrics_history.append(metrics)
        
        # 保留最近1000条
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics
    
    def save_metrics(self):
        """保存指标到文件"""
        try:
            metrics_data = [asdict(m) for m in self.metrics_history]
            with open(self.metrics_file, "w", encoding="utf-8") as f:
                json.dump(metrics_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def load_metrics(self) -> List[SystemMetrics]:
        """从文件加载指标"""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, "r", encoding="utf-8") as f:
                    metrics_data = json.load(f)
                    self.metrics_history = [
                        SystemMetrics(**m) for m in metrics_data
                    ]
            except Exception:
                pass
        return self.metrics_history
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        if not self.metrics_history:
            return {}
        
        latest = self.metrics_history[-1]
        
        return {
            "latest": asdict(latest),
            "history_count": len(self.metrics_history),
            "avg_node_count": sum(m.node_count for m in self.metrics_history) / len(self.metrics_history)
        }


class DeploymentHelper:
    """部署辅助工具"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "python_version": sys.version,
            "platform": sys.platform,
            "base_dir": self.base_dir,
            "timestamp": datetime.now().isoformat()
        }
    
    def check_required_files(self) -> Dict[str, bool]:
        """检查必要文件"""
        required_files = [
            "core/agent.py",
            "core/knowledge_graph.py",
            "core/plugins.py",
            "core/document_extractor.py",
            "core/web_service.py"
        ]
        
        results = {}
        for file_path in required_files:
            full_path = os.path.join(self.base_dir, file_path)
            results[file_path] = os.path.exists(full_path)
        
        return results
    
    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """创建数据备份"""
        backup_name = backup_name or f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir = os.path.join(self.base_dir, "backups", backup_name)
        os.makedirs(backup_dir, exist_ok=True)
        
        # 备份数据目录
        data_dir = os.path.join(self.base_dir, "data")
        if os.path.exists(data_dir):
            import shutil
            shutil.copytree(data_dir, os.path.join(backup_dir, "data"))
        
        return backup_dir
    
    def export_knowledge(self, output_file: str) -> bool:
        """导出知识"""
        # 这个函数需要与实际的Agent实例配合使用
        return True


def create_quick_start_script():
    """创建快速启动脚本"""
    script_content = '''#!/usr/bin/env python3
"""
快速启动脚本
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent import EternalSelfAgent

def main():
    print("=" * 60)
    print("永动知识图谱智能体 - 快速启动")
    print("=" * 60)
    
    # 创建Agent
    agent = EternalSelfAgent(agent_id="quick_start_agent")
    
    # 发现并加载插件
    plugins = agent.discover_plugins()
    print(f"\\n发现 {len(plugins)} 个插件:")
    for i, plugin in enumerate(plugins):
        print(f"  {i+1}. {os.path.basename(plugin)}")
    
    # 启动Web界面
    print("\\n启动Web界面...")
    agent.enable_web_interface(port=8080)
    print("Web界面已启动: http://127.0.0.1:8080")
    
    # 添加初始任务
    agent.add_initial_tasks([
        "探索新知识",
        "知识图谱梳理"
    ])
    
    print("\\n系统已就绪！按 Ctrl+C 停止")
    print("=" * 60)
    
    try:
        agent.eternal_loop()
    except KeyboardInterrupt:
        print("\\n正在停止...")
        agent.shutdown()

if __name__ == "__main__":
    main()
'''
    
    script_path = os.path.join(os.path.dirname(__file__), "..", "quick_start.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # 添加执行权限
    os.chmod(script_path, 0o755)
    
    return script_path

