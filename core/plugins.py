
"""
插件系统 - 永动知识图谱Agent
支持动态加载和管理插件
"""

import json
import os
import importlib.util
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import time


class PluginType(Enum):
    """插件类型枚举"""
    KNOWLEDGE_EXTRACTOR = "knowledge_extractor"
    KNOWLEDGE_PROCESSOR = "knowledge_processor"
    API_EXTENSION = "api_extension"
    TASK_GENERATOR = "task_generator"
    GENERAL = "general"


class PluginStatus(Enum):
    """插件状态枚举"""
    DISABLED = "disabled"
    LOADED = "loaded"
    ACTIVE = "active"
    ERROR = "error"


@dataclass
class PluginInfo:
    """插件信息"""
    plugin_id: str
    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    status: PluginStatus = PluginStatus.DISABLED
    load_time: float = 0.0
    last_used: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)


class BasePlugin(ABC):
    """插件基类"""
    
    def __init__(self):
        self._info: Optional[PluginInfo] = None
        self._agent = None
    
    @abstractmethod
    def get_name(self) -> str:
        """获取插件名称"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """获取插件版本"""
        pass
    
    @abstractmethod
    def get_author(self) -> str:
        """获取插件作者"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取插件描述"""
        pass
    
    @abstractmethod
    def get_plugin_type(self) -> PluginType:
        """获取插件类型"""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取插件元数据"""
        return {}
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {}
    
    def initialize(self, agent, config: Optional[Dict[str, Any]] = None) -> bool:
        """初始化插件"""
        self._agent = agent
        return True
    
    def on_load(self) -> None:
        """插件加载回调"""
        pass
    
    def on_unload(self) -> None:
        """插件卸载回调"""
        pass
    
    def on_activate(self) -> None:
        """插件激活回调"""
        pass
    
    def on_deactivate(self) -> None:
        """插件停用回调"""
        pass
    
    def get_info(self) -> Optional[PluginInfo]:
        """获取插件信息"""
        return self._info
    
    def set_info(self, info: PluginInfo) -> None:
        """设置插件信息"""
        self._info = info


class KnowledgeExtractorPlugin(BasePlugin):
    """知识抽取插件基类"""
    
    @abstractmethod
    def extract(self, source: Any, **kwargs) -> List[Dict[str, Any]]:
        """
        从源中抽取知识
        
        Args:
            source: 数据源（文本、文件路径等）
            **kwargs: 额外参数
        
        Returns:
            抽取的知识节点和边列表
        """
        pass
    
    def get_plugin_type(self) -> PluginType:
        return PluginType.KNOWLEDGE_EXTRACTOR


class KnowledgeProcessorPlugin(BasePlugin):
    """知识处理插件基类"""
    
    @abstractmethod
    def process(self, knowledge_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        处理知识数据
        
        Args:
            knowledge_data: 知识数据
            **kwargs: 额外参数
        
        Returns:
            处理后的知识数据
        """
        pass
    
    def get_plugin_type(self) -> PluginType:
        return PluginType.KNOWLEDGE_PROCESSOR


class TaskGeneratorPlugin(BasePlugin):
    """任务生成插件基类"""
    
    @abstractmethod
    def generate_tasks(self, context: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """
        生成任务
        
        Args:
            context: 上下文信息
            **kwargs: 额外参数
        
        Returns:
            生成的任务列表
        """
        pass
    
    def get_plugin_type(self) -> PluginType:
        return PluginType.TASK_GENERATOR


class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dir: Optional[str] = None):
        """
        初始化插件管理器
        
        Args:
            plugin_dir: 插件目录
        """
        self.plugin_dir = plugin_dir or os.path.join(os.path.dirname(__file__), "..", "plugins")
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_infos: Dict[str, PluginInfo] = {}
        self._agent = None
        
        os.makedirs(self.plugin_dir, exist_ok=True)
    
    def set_agent(self, agent) -> None:
        """设置Agent实例"""
        self._agent = agent
    
    def load_plugin(self, plugin_path: str, plugin_id: Optional[str] = None) -> bool:
        """
        加载插件
        
        Args:
            plugin_path: 插件文件路径
            plugin_id: 插件ID（可选）
        
        Returns:
            是否加载成功
        """
        try:
            load_start = time.time()
            
            if not os.path.exists(plugin_path):
                return False
            
            module_name = f"plugin_{os.path.basename(plugin_path).replace('.py', '')}"
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if not spec or not spec.loader:
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BasePlugin) and 
                    attr != BasePlugin and 
                    attr != KnowledgeExtractorPlugin and 
                    attr != KnowledgeProcessorPlugin and 
                    attr != TaskGeneratorPlugin):
                    plugin_class = attr
                    break
            
            if not plugin_class:
                return False
            
            plugin = plugin_class()
            
            if not plugin_id:
                plugin_id = f"{plugin.get_name().lower().replace(' ', '_')}_{int(time.time())}"
            
            info = PluginInfo(
                plugin_id=plugin_id,
                name=plugin.get_name(),
                version=plugin.get_version(),
                author=plugin.get_author(),
                description=plugin.get_description(),
                plugin_type=plugin.get_plugin_type(),
                status=PluginStatus.LOADED,
                load_time=time.time() - load_start,
                metadata=plugin.get_metadata(),
                config=plugin.get_default_config()
            )
            
            plugin.set_info(info)
            self._plugins[plugin_id] = plugin
            self._plugin_infos[plugin_id] = info
            plugin.on_load()
            
            return True
            
        except Exception as e:
            if plugin_id and plugin_id in self._plugin_infos:
                self._plugin_infos[plugin_id].status = PluginStatus.ERROR
            return False
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """
        卸载插件
        
        Args:
            plugin_id: 插件ID
        
        Returns:
            是否卸载成功
        """
        if plugin_id not in self._plugins:
            return False
        
        try:
            plugin = self._plugins[plugin_id]
            plugin.on_unload()
            del self._plugins[plugin_id]
            del self._plugin_infos[plugin_id]
            return True
        except Exception:
            return False
    
    def activate_plugin(self, plugin_id: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        激活插件
        
        Args:
            plugin_id: 插件ID
            config: 配置（可选）
        
        Returns:
            是否激活成功
        """
        if plugin_id not in self._plugins:
            return False
        
        try:
            plugin = self._plugins[plugin_id]
            info = self._plugin_infos[plugin_id]
            
            if config:
                info.config.update(config)
            
            if self._agent:
                if not plugin.initialize(self._agent, info.config):
                    return False
            
            plugin.on_activate()
            info.status = PluginStatus.ACTIVE
            
            return True
        except Exception:
            if plugin_id in self._plugin_infos:
                self._plugin_infos[plugin_id].status = PluginStatus.ERROR
            return False
    
    def deactivate_plugin(self, plugin_id: str) -> bool:
        """
        停用插件
        
        Args:
            plugin_id: 插件ID
        
        Returns:
            是否停用成功
        """
        if plugin_id not in self._plugins:
            return False
        
        try:
            plugin = self._plugins[plugin_id]
            info = self._plugin_infos[plugin_id]
            plugin.on_deactivate()
            info.status = PluginStatus.LOADED
            return True
        except Exception:
            return False
    
    def get_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """
        获取插件实例
        
        Args:
            plugin_id: 插件ID
        
        Returns:
            插件实例或None
        """
        return self._plugins.get(plugin_id)
    
    def get_active_plugins(self, plugin_type: Optional[PluginType] = None) -> List[BasePlugin]:
        """
        获取活跃插件列表
        
        Args:
            plugin_type: 插件类型（可选）
        
        Returns:
            活跃插件列表
        """
        plugins = []
        for plugin_id, plugin in self._plugins.items():
            info = self._plugin_infos[plugin_id]
            if info.status == PluginStatus.ACTIVE:
                if not plugin_type or info.plugin_type == plugin_type:
                    plugins.append(plugin)
        return plugins
    
    def get_all_plugin_infos(self) -> List[PluginInfo]:
        """
        获取所有插件信息
        
        Returns:
            插件信息列表
        """
        return list(self._plugin_infos.values())
    
    def get_plugin_info(self, plugin_id: str) -> Optional[PluginInfo]:
        """
        获取插件信息
        
        Args:
            plugin_id: 插件ID
        
        Returns:
            插件信息或None
        """
        return self._plugin_infos.get(plugin_id)
    
    def update_plugin_last_used(self, plugin_id: str) -> None:
        """
        更新插件最后使用时间
        
        Args:
            plugin_id: 插件ID
        """
        if plugin_id in self._plugin_infos:
            self._plugin_infos[plugin_id].last_used = time.time()
    
    def discover_plugins(self) -> List[str]:
        """
        发现插件目录中的插件
        
        Returns:
            发现的插件文件路径列表
        """
        plugin_files = []
        if os.path.exists(self.plugin_dir):
            for filename in os.listdir(self.plugin_dir):
                if filename.endswith(".py") and not filename.startswith("_"):
                    plugin_files.append(os.path.join(self.plugin_dir, filename))
        return plugin_files
    
    def extract_knowledge(self, source: Any, **kwargs) -> List[Dict[str, Any]]:
        """
        使用活跃的知识抽取插件抽取知识
        
        Args:
            source: 数据源
            **kwargs: 额外参数
        
        Returns:
            抽取的知识列表
        """
        all_knowledge = []
        for plugin in self.get_active_plugins(PluginType.KNOWLEDGE_EXTRACTOR):
            try:
                if isinstance(plugin, KnowledgeExtractorPlugin):
                    knowledge = plugin.extract(source, **kwargs)
                    all_knowledge.extend(knowledge)
                    self.update_plugin_last_used(plugin.get_info().plugin_id)
            except Exception:
                continue
        return all_knowledge
    
    def process_knowledge(self, knowledge_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        使用活跃的知识处理插件处理知识
        
        Args:
            knowledge_data: 知识数据
            **kwargs: 额外参数
        
        Returns:
            处理后的知识数据
        """
        result = knowledge_data
        for plugin in self.get_active_plugins(PluginType.KNOWLEDGE_PROCESSOR):
            try:
                if isinstance(plugin, KnowledgeProcessorPlugin):
                    result = plugin.process(result, **kwargs)
                    self.update_plugin_last_used(plugin.get_info().plugin_id)
            except Exception:
                continue
        return result
    
    def generate_plugin_tasks(self, context: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """
        使用活跃的任务生成插件生成任务
        
        Args:
            context: 上下文
            **kwargs: 额外参数
        
        Returns:
            生成的任务列表
        """
        all_tasks = []
        for plugin in self.get_active_plugins(PluginType.TASK_GENERATOR):
            try:
                if isinstance(plugin, TaskGeneratorPlugin):
                    tasks = plugin.generate_tasks(context, **kwargs)
                    all_tasks.extend(tasks)
                    self.update_plugin_last_used(plugin.get_info().plugin_id)
            except Exception:
                continue
        return all_tasks
    
    def save_plugin_configs(self, config_path: Optional[str] = None) -> bool:
        """
        保存插件配置
        
        Args:
            config_path: 配置文件路径
        
        Returns:
            是否保存成功
        """
        try:
            if not config_path:
                config_path = os.path.join(self.plugin_dir, "plugin_configs.json")
            
            configs = {}
            for plugin_id, info in self._plugin_infos.items():
                configs[plugin_id] = {
                    "status": info.status.value,
                    "config": info.config
                }
            
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(configs, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception:
            return False
    
    def load_plugin_configs(self, config_path: Optional[str] = None) -> bool:
        """
        加载插件配置
        
        Args:
            config_path: 配置文件路径
        
        Returns:
            是否加载成功
        """
        try:
            if not config_path:
                config_path = os.path.join(self.plugin_dir, "plugin_configs.json")
            
            if not os.path.exists(config_path):
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                configs = json.load(f)
            
            for plugin_id, plugin_config in configs.items():
                if plugin_id in self._plugin_infos:
                    info = self._plugin_infos[plugin_id]
                    info.config.update(plugin_config.get("config", {}))
                    
                    if plugin_config.get("status") == "active":
                        self.activate_plugin(plugin_id, info.config)
            
            return True
        except Exception:
            return False
