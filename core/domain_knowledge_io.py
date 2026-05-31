
"""
领域知识导入导出与数据迁移系统 - 阶段33
支持JSON、CSV、XML等多种格式的导入导出
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import csv
import os
from pathlib import Path

from core.domain_knowledge_manager import DomainKnowledge, DomainType, KnowledgeTemplate


class ExportFormat(Enum):
    """导出格式"""
    JSON = "json"
    CSV = "csv"
    XML = "xml"


class ImportFormat(Enum):
    """导入格式"""
    JSON = "json"
    CSV = "csv"
    XML = "xml"


@dataclass
class ImportResult:
    """导入结果"""
    success_count: int = 0
    failed_count: int = 0
    errors: List[str] = field(default_factory=list)
    imported_knowledges: List[DomainKnowledge] = field(default_factory=list)


@dataclass
class ExportResult:
    """导出结果"""
    success: bool = False
    file_path: str = ""
    record_count: int = 0
    error: str = ""


class DomainKnowledgeIO:
    """领域知识导入导出管理器"""
    
    def __init__(self, domain_manager):
        self.domain_manager = domain_manager
        self.export_dir = Path("data/exports")
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.import_dir = Path("data/imports")
        self.import_dir.mkdir(parents=True, exist_ok=True)
    
    def export_knowledges(self, 
                         knowledge_ids: Optional[List[str]] = None,
                         domain_type: Optional[DomainType] = None,
                         format: ExportFormat = ExportFormat.JSON,
                         file_name: Optional[str] = None) -> ExportResult:
        """
        导出领域知识
        
        Args:
            knowledge_ids: 指定导出的知识ID列表，None则导出所有
            domain_type: 按领域类型过滤
            format: 导出格式
            file_name: 自定义文件名
        
        Returns:
            导出结果
        """
        # 获取要导出的知识
        if knowledge_ids:
            knowledges = [self.domain_manager.get_domain_knowledge(kid) 
                         for kid in knowledge_ids]
            knowledges = [k for k in knowledges if k is not None]
        elif domain_type:
            knowledges = self.domain_manager.search_domain_knowledge(
                "", domain_type=domain_type
            )
        else:
            knowledges = list(self.domain_manager.domain_knowledges.values())
        
        if not knowledges:
            return ExportResult(success=False, error="没有要导出的知识")
        
        # 生成文件名
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"domain_knowledges_{timestamp}.{format.value}"
        
        file_path = self.export_dir / file_name
        
        try:
            if format == ExportFormat.JSON:
                self._export_json(knowledges, file_path)
            elif format == ExportFormat.CSV:
                self._export_csv(knowledges, file_path)
            elif format == ExportFormat.XML:
                self._export_xml(knowledges, file_path)
            
            return ExportResult(
                success=True,
                file_path=str(file_path),
                record_count=len(knowledges)
            )
        except Exception as e:
            return ExportResult(success=False, error=str(e))
    
    def _export_json(self, knowledges: List[DomainKnowledge], file_path: Path):
        """导出为JSON格式"""
        data = {
            "export_info": {
                "version": "1.0",
                "exported_at": datetime.now().isoformat(),
                "total_count": len(knowledges)
            },
            "knowledges": []
        }
        
        for knowledge in knowledges:
            data["knowledges"].append({
                "knowledge_id": knowledge.knowledge_id,
                "domain_type": knowledge.domain_type.value,
                "name": knowledge.name,
                "content": knowledge.content,
                "confidence": knowledge.confidence,
                "tags": knowledge.tags,
                "sources": knowledge.sources,
                "created_at": knowledge.created_at,
                "updated_at": knowledge.updated_at
            })
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _export_csv(self, knowledges: List[DomainKnowledge], file_path: Path):
        """导出为CSV格式"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow([
                "knowledge_id", "domain_type", "name", "content",
                "confidence", "tags", "sources", "created_at", "updated_at"
            ])
            # 写入数据
            for knowledge in knowledges:
                writer.writerow([
                    knowledge.knowledge_id,
                    knowledge.domain_type.value,
                    knowledge.name,
                    json.dumps(knowledge.content, ensure_ascii=False),
                    knowledge.confidence,
                    "|".join(knowledge.tags),
                    "|".join(knowledge.sources),
                    knowledge.created_at,
                    knowledge.updated_at
                ])
    
    def _export_xml(self, knowledges: List[DomainKnowledge], file_path: Path):
        """导出为XML格式"""
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<domain_knowledges>',
            f'  <export_info>',
            f'    <version>1.0</version>',
            f'    <exported_at>{datetime.now().isoformat()}</exported_at>',
            f'    <total_count>{len(knowledges)}</total_count>',
            f'  </export_info>',
            '  <knowledges>'
        ]
        
        for knowledge in knowledges:
            lines.extend([
                '    <knowledge>',
                f'      <knowledge_id>{self._xml_escape(knowledge.knowledge_id)}</knowledge_id>',
                f'      <domain_type>{knowledge.domain_type.value}</domain_type>',
                f'      <name>{self._xml_escape(knowledge.name)}</name>',
                f'      <content>{self._xml_escape(json.dumps(knowledge.content, ensure_ascii=False))}</content>',
                f'      <confidence>{knowledge.confidence}</confidence>',
                f'      <tags>{self._xml_escape("|".join(knowledge.tags))}</tags>',
                f'      <sources>{self._xml_escape("|".join(knowledge.sources))}</sources>',
                f'      <created_at>{knowledge.created_at}</created_at>',
                f'      <updated_at>{knowledge.updated_at}</updated_at>',
                '    </knowledge>'
            ])
        
        lines.extend([
            '  </knowledges>',
            '</domain_knowledges>'
        ])
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def _xml_escape(self, text: str) -> str:
        """XML特殊字符转义"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    
    def import_knowledges(self, 
                         file_path: str,
                         format: Optional[ImportFormat] = None,
                         skip_existing: bool = True) -> ImportResult:
        """
        导入领域知识
        
        Args:
            file_path: 导入文件路径
            format: 导入格式，None则自动检测
            skip_existing: 是否跳过已存在的知识
        
        Returns:
            导入结果
        """
        result = ImportResult()
        
        # 自动检测格式
        if not format:
            ext = Path(file_path).suffix.lower()
            if ext == '.json':
                format = ImportFormat.JSON
            elif ext == '.csv':
                format = ImportFormat.CSV
            elif ext == '.xml':
                format = ImportFormat.XML
            else:
                result.errors.append(f"无法识别的文件格式: {ext}")
                return result
        
        try:
            if format == ImportFormat.JSON:
                knowledges = self._import_json(file_path)
            elif format == ImportFormat.CSV:
                knowledges = self._import_csv(file_path)
            elif format == ImportFormat.XML:
                knowledges = self._import_xml(file_path)
            else:
                result.errors.append(f"不支持的导入格式: {format}")
                return result
            
            # 注册导入的知识
            for knowledge in knowledges:
                if skip_existing and knowledge.knowledge_id in self.domain_manager.domain_knowledges:
                    continue
                
                success = self.domain_manager.register_domain_knowledge(knowledge)
                if success:
                    result.success_count += 1
                    result.imported_knowledges.append(knowledge)
                else:
                    result.failed_count += 1
                    result.errors.append(f"注册知识失败: {knowledge.knowledge_id}")
            
        except Exception as e:
            result.errors.append(f"导入失败: {str(e)}")
        
        return result
    
    def _import_json(self, file_path: str) -> List[DomainKnowledge]:
        """从JSON导入"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        knowledges = []
        for k_data in data.get("knowledges", []):
            try:
                domain_type = DomainType(k_data.get("domain_type", "custom"))
                knowledge = DomainKnowledge(
                    knowledge_id=k_data["knowledge_id"],
                    domain_type=domain_type,
                    name=k_data["name"],
                    content=k_data.get("content", {}),
                    confidence=k_data.get("confidence", 0.8),
                    tags=k_data.get("tags", []),
                    sources=k_data.get("sources", []),
                    created_at=k_data.get("created_at"),
                    updated_at=k_data.get("updated_at")
                )
                knowledges.append(knowledge)
            except Exception as e:
                print(f"解析知识失败: {e}")
        
        return knowledges
    
    def _import_csv(self, file_path: str) -> List[DomainKnowledge]:
        """从CSV导入"""
        knowledges = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    domain_type = DomainType(row.get("domain_type", "custom"))
                    knowledge = DomainKnowledge(
                        knowledge_id=row["knowledge_id"],
                        domain_type=domain_type,
                        name=row["name"],
                        content=json.loads(row.get("content", "{}")),
                        confidence=float(row.get("confidence", 0.8)),
                        tags=row.get("tags", "").split("|") if row.get("tags") else [],
                        sources=row.get("sources", "").split("|") if row.get("sources") else [],
                        created_at=row.get("created_at"),
                        updated_at=row.get("updated_at")
                    )
                    knowledges.append(knowledge)
                except Exception as e:
                    print(f"解析CSV行失败: {e}")
        
        return knowledges
    
    def _import_xml(self, file_path: str) -> List[DomainKnowledge]:
        """从XML导入（简化实现）"""
        # 简化实现，实际应用中应使用xml.etree.ElementTree
        knowledges = []
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简单的正则解析
        import re
        knowledge_pattern = r'<knowledge>.*?</knowledge>'
        matches = re.findall(knowledge_pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                def get_tag_value(tag_name):
                    pattern = f'<{tag_name}>(.*?)</{tag_name}>'
                    m = re.search(pattern, match, re.DOTALL)
                    return m.group(1) if m else ""
                
                domain_type = DomainType(get_tag_value("domain_type") or "custom")
                knowledge = DomainKnowledge(
                    knowledge_id=get_tag_value("knowledge_id"),
                    domain_type=domain_type,
                    name=get_tag_value("name"),
                    content=json.loads(get_tag_value("content") or "{}"),
                    confidence=float(get_tag_value("confidence") or 0.8),
                    tags=get_tag_value("tags").split("|") if get_tag_value("tags") else [],
                    sources=get_tag_value("sources").split("|") if get_tag_value("sources") else [],
                    created_at=get_tag_value("created_at") or None,
                    updated_at=get_tag_value("updated_at") or None
                )
                knowledges.append(knowledge)
            except Exception as e:
                print(f"解析XML知识失败: {e}")
        
        return knowledges
    
    def migrate_from_knowledge_graph(self) -> ImportResult:
        """
        从知识图谱迁移数据到领域知识系统
        
        Returns:
            迁移结果
        """
        result = ImportResult()
        kg = self.domain_manager.kg
        
        for node in kg.nodes.values():
            try:
                # 根据节点属性判断领域类型
                node_type = node.attr.get("type", "general")
                domain_type_map = {
                    "technology": DomainType.TECHNOLOGY,
                    "healthcare": DomainType.HEALTHCARE,
                    "education": DomainType.EDUCATION,
                    "finance": DomainType.FINANCE,
                    "legal": DomainType.LEGAL,
                    "science": DomainType.SCIENCE,
                    "language": DomainType.LANGUAGE
                }
                domain_type = domain_type_map.get(node_type, DomainType.GENERAL)
                
                knowledge = DomainKnowledge(
                    knowledge_id=f"migrated_{node.id}",
                    domain_type=domain_type,
                    name=node.name,
                    content=dict(node.attr),
                    confidence=node.attr.get("confidence", 0.8),
                    tags=node.attr.get("tags", []),
                    sources=["knowledge_graph_migration"]
                )
                
                success = self.domain_manager.register_domain_knowledge(knowledge)
                if success:
                    result.success_count += 1
                    result.imported_knowledges.append(knowledge)
                else:
                    result.failed_count += 1
            except Exception as e:
                result.failed_count += 1
                result.errors.append(f"迁移节点失败 {node.name}: {str(e)}")
        
        return result
    
    def get_export_history(self) -> List[Dict[str, Any]]:
        """获取导出历史"""
        history = []
        for file_path in self.export_dir.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                history.append({
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "format": file_path.suffix.lstrip('.')
                })
        
        return sorted(history, key=lambda x: x["created_at"], reverse=True)

