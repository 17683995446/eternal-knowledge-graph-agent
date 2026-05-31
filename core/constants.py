"""
三大公理固化为常量：
- LOOP_DELAY: 存续公理 - 主循环节拍控制
- EVOLVE_STEP: 自驱公理 - 进化触发周期
- KG_SAVE_PATH: 记忆公理 - 唯一持久化路径
- TASK_QUEUE_MAX: 资源守恒 - 任务池上限
- WEIGHT_THRESHOLD: 知识质量阈值
"""

LOOP_DELAY = 0.3
EVOLVE_STEP = 50
KG_SAVE_PATH = "data/knowledge_graph.json"
TASK_QUEUE_MAX = 200
WEIGHT_HIGH = 0.2   # 高价值关联阈值
WEIGHT_TRIM = 0.1   # 淘汰边界阈值
