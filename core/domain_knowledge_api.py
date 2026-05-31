
"""
领域知识API接口与外部集成 - 阶段39
提供RESTful API接口和外部系统集成能力
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from core.domain_knowledge_manager import DomainKnowledge, DomainType


@dataclass
class APIResponse:
    """API响应"""
    success: bool
    data: Any = None
    message: str = ""
    error_code: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class DomainKnowledgeAPI:
    """领域知识API管理器"""
    
    def __init__(self, agent):
        self.agent = agent
    
    def get_all_knowledges(self, 
                          domain_type: Optional[str] = None,
                          tags: Optional[List[str]] = None,
                          limit: int = 100,
                          offset: int = 0) -> APIResponse:
        """获取所有知识"""
        try:
            dt = DomainType(domain_type) if domain_type else None
            
            if dt or tags:
                results = self.agent.search_domain_knowledge(
                    "", domain_type=dt, tags=tags, limit=limit
                )
                knowledges = [r.knowledge for r in results]
            else:
                knowledges = list(self.agent.domain_knowledge_manager.domain_knowledges.values())
                knowledges = knowledges[offset:offset+limit]
            
            data = {
                "total": len(self.agent.domain_knowledge_manager.domain_knowledges),
                "limit": limit,
                "offset": offset,
                "knowledges": [self._knowledge_to_dict(k) for k in knowledges]
            }
            
            return APIResponse(success=True, data=data)
        except Exception as e:
            return APIResponse(success=False, message=str(e), error_code="FETCH_ERROR")
    
    def get_knowledge(self, knowledge_id: str) -> APIResponse:
        """获取单条知识"""
        try:
            knowledge = self.agent.get_domain_knowledge(knowledge_id)
            if knowledge:
                return APIResponse(success=True, data=self._knowledge_to_dict(knowledge))
            else:
                return APIResponse(success=False, message="知识不存在", error_code="NOT_FOUND")
        except Exception as e:
            return APIResponse(success=False, message=str(e), error_code="FETCH_ERROR")
    
    def create_knowledge(self, 
                        template_id: str,
                        name: str,
                        content: Dict[str, Any],
                        tags: Optional[List[str]] = None,
                        sources: Optional[List[str]] = None) -> APIResponse:
        """创建知识"""
        try:
            knowledge = self.agent.create_domain_knowledge(
                template_id, name, content, tags, sources
            )
            if knowledge:
                return APIResponse(
                    success=True,
                    data=self._knowledge_to_dict(knowledge),
                    message="知识创建成功"
                )
            else:
                return APIResponse(success=False, message="创建失败", error_code="CREATE_ERROR")
        except Exception as e:
            return APIResponse(success=False, message=str(e), error_code="CREATE_ERROR")
    
    def update_knowledge(self, 
                        knowledge_id: str,
                        content_updates: Dict[str, Any]) -> APIResponse:
        """更新知识"""
        try:
            success = self.agent.update_domain_knowledge(knowledge_id, content_updates)
            if success:
                return APIResponse(success=True, message="更新成功")
            else:
                return APIResponse(success=False, message="更新失败", error_code="UPDATE_ERROR")
        except Exception as e:
            return APIResponse(success=False, message=str(e), error_code="UPDATE_ERROR")
    
    def delete_knowledge(self, knowledge_id: str) -> APIResponse:
        """删除知识"""
        try:
            success = self.agent.delete_domain_knowledge(knowledge_id)
            if success:
                return APIResponse(success=True, message="删除成功")
            else:
                return APIResponse(success=False, message="删除失败", error_code="DELETE_ERROR")
        except Exception as e:
            return APIResponse(success=False, message=str(e), error_code="DELETE_ERROR")
    
    def search_knowledges(self, 
                         query: str,
                         search_type: str = "hybrid",
                         domain_type: Optional[str] = None,
                         limit: int = 10) -> APIResponse:
        """搜索知识"""
        try:
            results = self.agent.search_domain_knowledge(
                query=query,
                search_type=search_type,
                domain_type=DomainType(domain_type) if domain_type else None,
                limit=limit
            )
            
            data = {
                "query": query,
                "total": len(results),
                "results": [
                    {
                        "knowledge": self._knowledge_to_dict(r.knowledge),
                        "score": r.score,
                        "match_reason": r.match_reason,
                        "rank": r.rank
                    }
                    for r in results
                ]
            }
            
            return APIResponse(success=True, data=data)
        except Exception as e:
            return APIResponse(success=False, message=str(e), error_code="SEARCH_ERROR")
    
    def get_recommendations(self,
                           source_knowledge_id: Optional[str] = None,
                           source_tags: Optional[List[str]] = None,
                           limit: int = 5) -> APIResponse:
        """获取推荐"""
        try:
            results = self.agent.get_domain_recommendations(
                source_knowledge_id=source_knowledge_id,
                source_tags=source_tags,
                limit=limit
            )
            
            data = {
                "total": len(results),
                "recommendations": [
                    {
                        "knowledge": self._knowledge_to_dict(r.knowledge),
                        "score": r.score,
                        "reason": r.reason,
                        "source_type": r.source_type
                    }
                    for r in results
                ]
            }
            
            return APIResponse(success=True, data=data)
        except Exception as e:
            return APIResponse(success=False, message=str(e), error_code="RECOMMEND_ERROR")
    
    def ask_question(self, 
                    question: str,
                    session_id: str = "default",
                    domain_type: Optional[str] = None) -> APIResponse:
        """问答"""
        try:
            answer = self.agent.ask_domain_question(
                question=question,
                session_id=session_id,
                domain_type=domain_type
            )
            
            data = {
                "question": answer.question,
                "answer": answer.answer_text,
                "confidence": answer.confidence,
                "question_type": answer.question_type.value,
                "sources": [self._knowledge_to_dict(k) for k in answer.sources],
                "related_questions": answer.related_questions
            }
            
            return APIResponse(success=True, data=data)
        except Exception as e:
            return APIResponse(success=False, message=str(e), error_code="QA_ERROR")
    
    def get_domain_stats(self) -> APIResponse:
        """获取领域统计"""
        try:
            stats = self.agent.get_domain_stats()
            return APIResponse(success=True, data=stats)
        except Exception as e:
            return APIResponse(success=False, message=str(e), error_code="STATS_ERROR")
    
    def get_visualization_data(self, 
                              viz_type: str = "distribution") -> APIResponse:
        """获取可视化数据"""
        try:
            if viz_type == "distribution":
                data = self.agent.generate_domain_distribution()
            elif viz_type == "tag_cloud":
                data = self.agent.generate_tag_cloud()
            elif viz_type == "confidence":
                data = self.agent.generate_confidence_chart()
            else:
                return APIResponse(success=False, message="未知的可视化类型", error_code="INVALID_TYPE")
            
            return APIResponse(success=True, data=data)
        except Exception as e:
            return APIResponse(success=False, message=str(e), error_code="VIZ_ERROR")
    
    def export_knowledges(self,
                         format: str = "json",
                         domain_type: Optional[str] = None) -> APIResponse:
        """导出知识"""
        try:
            dt = DomainType(domain_type) if domain_type else None
            result = self.agent.export_domain_knowledges(
                format=format,
                domain_type=dt
            )
            
            if result.success:
                return APIResponse(
                    success=True,
                    data={
                        "file_path": result.file_path,
                        "record_count": result.record_count
                    },
                    message="导出成功"
                )
            else:
                return APIResponse(success=False, message=result.error, error_code="EXPORT_ERROR")
        except Exception as e:
            return APIResponse(success=False, message=str(e), error_code="EXPORT_ERROR")
    
    def get_quality_report(self, knowledge_id: Optional[str] = None) -> APIResponse:
        """获取质量报告"""
        try:
            if knowledge_id:
                report = self.agent.get_quality_report(knowledge_id)
                if report:
                    data = {
                        "knowledge_id": report.knowledge_id,
                        "overall_score": report.overall_score,
                        "quality_level": report.quality_level.value,
                        "completeness_score": report.completeness_score,
                        "accuracy_score": report.accuracy_score,
                        "consistency_score": report.consistency_score,
                        "freshness_score": report.freshness_score,
                        "issues": report.issues,
                        "suggestions": report.suggestions
                    }
                    return APIResponse(success=True, data=data)
                else:
                    return APIResponse(success=False, message="报告不存在", error_code="NOT_FOUND")
            else:
                metrics = self.agent.batch_evaluate_quality()
                data = {
                    "total_knowledges": metrics.total_knowledges,
                    "avg_quality_score": metrics.avg_quality_score,
                    "quality_distribution": metrics.quality_distribution,
                    "completeness_avg": metrics.completeness_avg,
                    "accuracy_avg": metrics.accuracy_avg,
                    "consistency_avg": metrics.consistency_avg,
                    "freshness_avg": metrics.freshness_avg,
                    "top_issues": metrics.top_issues
                }
                return APIResponse(success=True, data=data)
        except Exception as e:
            return APIResponse(success=False, message=str(e), error_code="QUALITY_ERROR")
    
    def _knowledge_to_dict(self, knowledge: DomainKnowledge) -> Dict[str, Any]:
        """将知识转换为字典"""
        return {
            "knowledge_id": knowledge.knowledge_id,
            "domain_type": knowledge.domain_type.value,
            "name": knowledge.name,
            "content": knowledge.content,
            "confidence": knowledge.confidence,
            "tags": knowledge.tags,
            "sources": knowledge.sources,
            "created_at": knowledge.created_at,
            "updated_at": knowledge.updated_at
        }
    
    def get_api_documentation(self) -> Dict[str, Any]:
        """获取API文档"""
        return {
            "api_version": "1.0",
            "base_url": "/api/v1",
            "endpoints": [
                {
                    "path": "/knowledges",
                    "method": "GET",
                    "description": "获取知识列表",
                    "parameters": ["domain_type", "tags", "limit", "offset"]
                },
                {
                    "path": "/knowledges/{id}",
                    "method": "GET",
                    "description": "获取单条知识"
                },
                {
                    "path": "/knowledges",
                    "method": "POST",
                    "description": "创建知识",
                    "parameters": ["template_id", "name", "content", "tags", "sources"]
                },
                {
                    "path": "/knowledges/{id}",
                    "method": "PUT",
                    "description": "更新知识",
                    "parameters": ["content_updates"]
                },
                {
                    "path": "/knowledges/{id}",
                    "method": "DELETE",
                    "description": "删除知识"
                },
                {
                    "path": "/search",
                    "method": "GET",
                    "description": "搜索知识",
                    "parameters": ["query", "search_type", "domain_type", "limit"]
                },
                {
                    "path": "/recommendations",
                    "method": "GET",
                    "description": "获取推荐",
                    "parameters": ["source_knowledge_id", "source_tags", "limit"]
                },
                {
                    "path": "/qa",
                    "method": "POST",
                    "description": "问答",
                    "parameters": ["question", "session_id", "domain_type"]
                },
                {
                    "path": "/stats",
                    "method": "GET",
                    "description": "获取统计"
                },
                {
                    "path": "/visualization",
                    "method": "GET",
                    "description": "获取可视化数据",
                    "parameters": ["viz_type"]
                },
                {
                    "path": "/export",
                    "method": "POST",
                    "description": "导出知识",
                    "parameters": ["format", "domain_type"]
                },
                {
                    "path": "/quality",
                    "method": "GET",
                    "description": "获取质量报告",
                    "parameters": ["knowledge_id"]
                }
            ]
        }

