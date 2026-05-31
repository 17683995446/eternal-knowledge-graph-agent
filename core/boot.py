"""
基于第一性原理，轻量化永动知识图谱智能体 - 启动引导模块
系统初始化与启动流程
"""

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from core.agent import EternalSelfAgent

from core.constants import KG_SAVE_PATH


class BootStrapper:
    """系统启动引导器"""

    def __init__(self):
        self.checks = []
        self.errors = []

    def run_preflight_checks(self) -> bool:
        """运行启动前检查"""
        self._check_python_version()
        self._check_data_directory()
        self._check_disk_space()
        self._check_file_permissions()

        if self.errors:
            print("[启动检查] 发现以下问题:")
            for error in self.errors:
                print(f"  - {error}")
            return False

        print("[启动检查] 所有检查通过")
        return True

    def _check_python_version(self):
        """检查Python版本"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.errors.append(f"Python版本过低: {version.major}.{version.minor} (需要3.8+)")

    def _check_data_directory(self):
        """检查数据目录"""
        data_dir = Path(KG_SAVE_PATH).parent

        if not data_dir.exists():
            try:
                data_dir.mkdir(parents=True, exist_ok=True)
                print(f"[目录创建] {data_dir}")
            except Exception as e:
                self.errors.append(f"无法创建数据目录: {e}")

    def _check_disk_space(self):
        """检查磁盘空间（至少需要10MB）"""
        try:
            import shutil
            stat = shutil.disk_usage("/")
            free_mb = stat.free / (1024 * 1024)
            if free_mb < 10:
                self.errors.append(f"磁盘空间不足: {free_mb:.1f}MB (需要至少10MB)")
        except Exception as e:
            self.errors.append(f"无法检查磁盘空间: {e}")

    def _check_file_permissions(self):
        """检查文件权限"""
        data_dir = Path(KG_SAVE_PATH).parent

        if not os.access(data_dir, os.W_OK):
            self.errors.append(f"数据目录不可写: {data_dir}")

    def initialize_system(self) -> "EternalSelfAgent":
        """初始化系统"""
        from core.agent import EternalSelfAgent

        print("[初始化] 开始系统初始化...")

        # 1. 预检查
        if not self.run_preflight_checks():
            print("[初始化] 启动前检查失败，系统无法启动")
            sys.exit(1)

        # 2. 创建智能体实例
        print("[初始化] 创建智能体实例...")
        agent = EternalSelfAgent()

        # 3. 注入初始根认知任务
        print("[初始化] 注入初始任务...")
        self._inject_initial_tasks(agent)

        # 4. 执行首次知识进化
        print("[初始化] 执行首次知识进化...")
        agent.evolution_layer.evolve()

        print("[初始化] 系统初始化完成")

        return agent

    def _inject_initial_tasks(self, agent: "EternalSelfAgent"):
        """注入初始任务"""
        initial_tasks = [
            "系统初始认知迭代",
            "探索知识图谱基本结构",
            "建立首个认知节点",
            "测试任务执行流程"
        ]

        for task in initial_tasks:
            agent.task_queue.add(task)

        print(f"[初始任务] 已注入 {len(initial_tasks)} 个初始任务")
