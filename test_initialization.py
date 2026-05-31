"""
快速测试初始化
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.main import main_entry

# 这里我们不运行完整循环，只测试初始化
if __name__ == "__main__":
    from core.agent import EternalSelfAgent
    print("=== 测试初始化 ===")
    agent = EternalSelfAgent()
    print("✅ 智能体初始化成功！")
    print(f"   - 节点数量: {len(agent.knowledge_graph.nodes)}")
    print(f"   - 边数量: {len(agent.knowledge_graph.edges)}")
