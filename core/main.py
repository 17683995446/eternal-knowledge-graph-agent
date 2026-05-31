"""
基于第一性原理，轻量化永动知识图谱智能体 - 系统入口
系统唯一启动入口
"""


def main():
    """系统唯一启动入口"""
    print("=" * 50)
    print("永动知识图谱智能体 (Eternal Knowledge Graph Agent)")
    print("=" * 50)

    # 启动引导
    from core.boot import BootStrapper
    bootstrapper = BootStrapper()

    # 初始化系统
    agent = bootstrapper.initialize_system()

    # 启动永动循环
    print("\n[启动] 开始永动循环...")
    print("-" * 50)

    try:
        agent.eternal_loop()
    except KeyboardInterrupt:
        print("\n[中断] 收到中断信号，正在关闭...")
        agent.shutdown()
    except Exception as e:
        print(f"\n[致命错误] {e}")
        agent.shutdown()
        raise


if __name__ == "__main__":
    main()
