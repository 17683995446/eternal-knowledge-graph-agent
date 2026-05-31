"""
基于第一性原理，轻量化永动知识图谱智能体 - 异常基类

所有异常类都从基类继承，确保统一的异常处理接口。
"""


class AgentException(Exception):
    """
    智能体异常基类

    所有自定义异常都继承自此类，提供统一的接口和元数据。
    符合存续公理：异常不应导致系统崩溃，而应被隔离和处理。
    """

    def __init__(self, message: str, recoverable: bool = True):
        """
        初始化异常

        Args:
            message: 异常消息
            recoverable: 该异常是否可恢复（默认：True）
        """
        self.message = message
        self.recoverable = recoverable
        super().__init__(self.message)

    def __str__(self) -> str:
        """返回异常的字符串表示"""
        return f"{self.__class__.__name__}: {self.message} (recoverable: {self.recoverable})"


class KnowledgeGraphException(AgentException):
    """
    知识图谱相关异常

    用于表示知识图谱操作时出现的错误，包括数据损坏、
    序列化失败、无效节点等。
    """

    pass


class TaskExecutionException(AgentException):
    """
    任务执行异常

    用于表示任务执行过程中出现的错误。
    """

    pass


class ResourceExhaustedException(AgentException):
    """
    资源耗尽异常

    用于表示系统资源（内存、任务队列空间等）耗尽的情况。
    符合存续公理：资源耗尽时应熔断而不是崩溃。
    """

    def __init__(self, message: str):
        # 资源耗尽通常是可恢复的（例如通过清理或等待）
        super().__init__(message, recoverable=True)
