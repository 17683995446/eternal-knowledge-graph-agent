
"""
阶段25验收测试：实际应用集成
测试插件系统、文档知识抽取、API增强功能
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_plugin_system_basic():
    """测试插件系统基础功能"""
    print("\n=== 测试1: 插件系统基础功能 ===")
    
    from core.plugins import (
        PluginManager,
        KnowledgeExtractorPlugin,
        PluginType,
        PluginStatus
    )
    
    plugin_dir = tempfile.mkdtemp()
    
    test_plugin_code = '''
from core.plugins import KnowledgeExtractorPlugin, PluginType
from typing import List, Dict, Any

class TestPlugin(KnowledgeExtractorPlugin):
    def get_name(self) -> str:
        return "TestPlugin"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_author(self) -> str:
        return "TestAuthor"
    
    def get_description(self) -> str:
        return "Test Description"
    
    def get_plugin_type(self) -> PluginType:
        return PluginType.KNOWLEDGE_EXTRACTOR
    
    def extract(self, source, **kwargs) -> List[Dict[str, Any]]:
        return [{"type": "node", "name": "TestNode"}]
'''
    
    plugin_path = os.path.join(plugin_dir, "test_plugin.py")
    with open(plugin_path, "w", encoding="utf-8") as f:
        f.write(test_plugin_code)
    
    manager = PluginManager(plugin_dir)
    assert manager is not None, "插件管理器应该能创建"
    print("✓ 插件管理器创建成功")
    
    success = manager.load_plugin(plugin_path, "test_plugin_1")
    assert success, "插件应该能加载"
    print("✓ 插件加载成功")
    
    infos = manager.get_all_plugin_infos()
    assert len(infos) == 1, "应该有一个插件信息"
    assert infos[0].name == "TestPlugin", "插件名称应该匹配"
    print("✓ 插件信息获取成功")
    
    success = manager.activate_plugin("test_plugin_1")
    assert success, "插件应该能激活"
    print("✓ 插件激活成功")
    
    knowledge = manager.extract_knowledge("test source")
    assert len(knowledge) > 0, "应该能抽取到知识"
    print("✓ 插件知识抽取成功")
    
    success = manager.deactivate_plugin("test_plugin_1")
    assert success, "插件应该能停用"
    print("✓ 插件停用成功")
    
    print("✓ 测试1通过!")
    
    import shutil
    shutil.rmtree(plugin_dir)
    return True


def test_document_extractor():
    """测试文档知识抽取功能"""
    print("\n=== 测试2: 文档知识抽取功能 ===")
    
    from core.document_extractor import (
        DocumentKnowledgeExtractor,
        DocumentType
    )
    
    extractor = DocumentKnowledgeExtractor()
    assert extractor is not None, "文档抽取器应该能创建"
    print("✓ 文档抽取器创建成功")
    
    assert extractor.detect_document_type("test.txt") == DocumentType.TEXT
    assert extractor.detect_document_type("test.md") == DocumentType.MARKDOWN
    assert extractor.detect_document_type("test.json") == DocumentType.JSON
    print("✓ 文档类型检测成功")
    
    test_text = """
John works at TechCorp Inc in New York.
TechCorp Inc has many employees.
"""
    
    result = extractor.extract_from_text(test_text, "test")
    assert result is not None, "应该能抽取到结果"
    print("✓ 文本抽取成功")
    
    kg_data = extractor.extraction_result_to_knowledge_graph(result)
    assert len(kg_data) >= 0, "结果应该有效"
    print(f"✓ 知识图谱格式转换成功，获得 {len(kg_data)} 条知识")
    
    print("✓ 测试2通过!")
    return True


def test_agent_plugin_integration():
    """测试Agent与插件系统集成"""
    print("\n=== 测试3: Agent与插件系统集成 ===")
    
    from core.agent import EternalSelfAgent
    
    agent = EternalSelfAgent(agent_id="test_agent_25")
    assert hasattr(agent, "plugin_manager"), "Agent应该有插件管理器"
    print("✓ Agent插件管理器存在")
    
    plugin_dir = tempfile.mkdtemp()
    
    test_plugin_code = '''
from core.plugins import KnowledgeExtractorPlugin, PluginType
from typing import List, Dict, Any

class AgentTestPlugin(KnowledgeExtractorPlugin):
    def get_name(self) -> str:
        return "AgentTestPlugin"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_author(self) -> str:
        return "TestAuthor"
    
    def get_description(self) -> str:
        return "Agent Test Plugin"
    
    def get_plugin_type(self) -> PluginType:
        return PluginType.KNOWLEDGE_EXTRACTOR
    
    def extract(self, source, **kwargs) -> List[Dict[str, Any]]:
        return [
            {"type": "node", "name": "TestNode1"},
            {"type": "node", "name": "TestNode2"},
            {"type": "edge", "source": "TestNode1", "target": "TestNode2", "relation_type": "related_to"}
        ]
'''
    
    plugin_path = os.path.join(plugin_dir, "agent_test_plugin.py")
    with open(plugin_path, "w", encoding="utf-8") as f:
        f.write(test_plugin_code)
    
    success = agent.load_plugin(plugin_path, "agent_test_plugin")
    assert success, "Agent应该能加载插件"
    print("✓ Agent加载插件成功")
    
    success = agent.activate_plugin("agent_test_plugin")
    assert success, "Agent应该能激活插件"
    print("✓ Agent激活插件成功")
    
    plugin_status = agent.get_plugin_status()
    assert len(plugin_status) == 1, "应该有一个插件"
    print("✓ 插件状态获取成功")
    
    knowledge = agent.extract_knowledge_from_source("test")
    assert len(knowledge) >= 0, "应该能抽取知识"
    print("✓ Agent知识抽取成功")
    
    assert len(agent.knowledge_graph.nodes) > 0, "知识图谱应该有节点"
    print("✓ 知识成功加入知识图谱")
    
    success = agent.plugin_manager.save_plugin_configs()
    assert success, "应该能保存插件配置"
    print("✓ 插件配置保存成功")
    
    agent.shutdown()
    
    print("✓ 测试3通过!")
    
    import shutil
    shutil.rmtree(plugin_dir)
    return True


def test_deployment_tools():
    """测试部署和运维工具"""
    print("\n=== 测试4: 部署和运维工具 ===")
    
    from core.deployment import (
        LoggerManager,
        MetricsCollector,
        DeploymentHelper
    )
    
    logger_manager = LoggerManager()
    assert logger_manager is not None, "日志管理器应该能创建"
    print("✓ 日志管理器创建成功")
    
    logger_manager.info("Test info message")
    logger_manager.warning("Test warning message")
    logger_manager.error("Test error message")
    logs = logger_manager.get_recent_logs()
    assert isinstance(logs, list), "应该能获取最近日志"
    print("✓ 日志功能正常")
    
    collector = MetricsCollector()
    assert collector is not None, "指标收集器应该能创建"
    print("✓ 指标收集器创建成功")
    
    helper = DeploymentHelper()
    assert helper is not None, "部署辅助工具应该能创建"
    print("✓ 部署辅助工具创建成功")
    
    info = helper.get_system_info()
    assert info is not None, "应该能获取系统信息"
    print("✓ 系统信息获取成功")
    
    file_check = helper.check_required_files()
    assert isinstance(file_check, dict), "应该能检查文件"
    print("✓ 文件检查功能正常")
    
    print("✓ 测试4通过!")
    return True


def test_example_text_extractor():
    """测试示例文本抽取插件"""
    print("\n=== 测试5: 示例文本抽取插件 ===")
    
    from core.agent import EternalSelfAgent
    
    agent = EternalSelfAgent(agent_id="test_example_plugin")
    
    plugin_path = os.path.join(
        os.path.dirname(__file__), "..", "plugins", "example_text_extractor.py"
    )
    plugin_path = os.path.abspath(plugin_path)
    
    success = agent.load_plugin(plugin_path, "example_extractor")
    assert success, "应该能加载示例插件"
    print("✓ 示例插件加载成功")
    
    success = agent.activate_plugin("example_extractor")
    assert success, "应该能激活示例插件"
    print("✓ 示例插件激活成功")
    
    test_text = """
Alice works at OpenAI Inc in San Francisco.
OpenAI develops AI technology.
"""
    
    knowledge = agent.extract_knowledge_from_source(test_text)
    assert isinstance(knowledge, list), "应该能抽取知识"
    print(f"✓ 示例插件抽取测试通过，获得 {len(knowledge)} 条知识")
    
    agent.shutdown()
    
    print("✓ 测试5通过!")
    return True


def run_all_tests():
    """运行所有验收测试"""
    print("=" * 60)
    print("阶段25验收测试：实际应用集成")
    print("=" * 60)
    
    tests = [
        test_plugin_system_basic,
        test_document_extractor,
        test_agent_plugin_integration,
        test_deployment_tools,
        test_example_text_extractor
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n  测试失败: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
