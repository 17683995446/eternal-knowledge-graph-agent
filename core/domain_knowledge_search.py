
"""
领域知识搜索与推荐系统 - 阶段32
支持语义搜索、关键词搜索、标签推荐和知识热度排序
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
from pathlib import Path
import re
from collections import Counter
import math

from core.domain_knowledge_manager import DomainKnowledge, DomainType


class SearchType(Enum):
    """搜索类型"""
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


@dataclass
class SearchResult:
    """搜索结果"""
    knowledge: DomainKnowledge
    score: float
    match_reason: str
    rank: int = 0


@dataclass
class RecommendationResult:
    """推荐结果"""
    knowledge: DomainKnowledge
    score: float
    reason: str
    source_type: str  # "similar", "related", "trending", "recent"


@dataclass
class KnowledgeStats:
    """知识统计信息"""
    knowledge_id: str
    view_count: int = 0
    access_count: int = 0
    last_accessed: Optional[str] = None
    relevance_score: float = 0.0
    hot_score: float = 0.0


class DomainKnowledgeSearcher:
    """领域知识搜索与推荐器"""
    
    def __init__(self, domain_manager):
        self.domain_manager = domain_manager
        self.stats: Dict[str, KnowledgeStats] = {}
        self.stop_words = {"的", "是", "在", "了", "和", "有", "我", "他", "她", "这", "那", "就", "都", "而", "及", "与", "着", "或", "我们", "你们", "他们"}
        
        self.data_dir = Path("data/domains")
        self.stats_file = self.data_dir / "search_stats.json"
        
        self._load_stats()
    
    def _load_stats(self):
        """加载统计数据"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for k_id, stats_data in data.get("stats", {}).items():
                    self.stats[k_id] = KnowledgeStats(
                        knowledge_id=k_id,
                        view_count=stats_data.get("view_count", 0),
                        access_count=stats_data.get("access_count", 0),
                        last_accessed=stats_data.get("last_accessed"),
                        relevance_score=stats_data.get("relevance_score", 0.0),
                        hot_score=stats_data.get("hot_score", 0.0)
                    )
            except Exception as e:
                print(f"加载搜索统计失败: {e}")
    
    def _save_stats(self):
        """保存统计数据"""
        data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "stats": {}
        }
        
        for k_id, stats in self.stats.items():
            data["stats"][k_id] = {
                "view_count": stats.view_count,
                "access_count": stats.access_count,
                "last_accessed": stats.last_accessed,
                "relevance_score": stats.relevance_score,
                "hot_score": stats.hot_score
            }
        
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存搜索统计失败: {e}")
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 移除标点符号和特殊字符
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # 按空格分割
        tokens = text.split()
        # 对于中文文本，简单地把整个文本作为token，同时保留英文token
        # 这样可以让中文搜索工作
        all_tokens = []
        for token in tokens:
            if token and token not in self.stop_words:
                all_tokens.append(token)
        # 如果没有token，就把整个文本作为token
        if not all_tokens and text.strip():
            all_tokens.append(text.strip())
        return all_tokens
    
    def _calculate_tfidf_score(self, query_tokens: List[str], knowledge: DomainKnowledge) -> float:
        """计算TF-IDF分数"""
        content_text = f"{knowledge.name} {json.dumps(knowledge.content, ensure_ascii=False)} {' '.join(knowledge.tags)}"
        content_tokens = self._tokenize(content_text)
        
        if not query_tokens or not content_tokens:
            return 0.0
        
        # 简单的词频匹配
        match_count = 0
        for token in query_tokens:
            if token in content_tokens:
                match_count += 1
        
        # 计算匹配比例
        tf_score = match_count / max(len(query_tokens), 1)
        
        # 加上标签匹配权重
        tag_match_count = sum(1 for tag in knowledge.tags if any(token in tag.lower() for token in query_tokens))
        tag_score = tag_match_count / max(len(knowledge.tags), 1) * 0.5
        
        return tf_score * 0.7 + tag_score * 0.3
    
    def _calculate_levenshtein_distance(self, s1: str, s2: str) -> int:
        """计算编辑距离"""
        if len(s1) < len(s2):
            return self._calculate_levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _calculate_fuzzy_score(self, query: str, knowledge: DomainKnowledge) -> float:
        """计算模糊匹配分数"""
        query_lower = query.lower()
        query_tokens = self._tokenize(query)
        name_lower = knowledge.name.lower()
        
        score = 0.0
        
        # 精确匹配
        if query_lower in name_lower:
            score = 1.0
        else:
            # 编辑距离相似度
            distance = self._calculate_levenshtein_distance(query_lower, name_lower)
            max_len = max(len(query_lower), len(name_lower))
            if max_len == 0:
                similarity = 0.0
            else:
                similarity = 1 - distance / max_len
            score = similarity
        
        # 查询token匹配名称
        for token in query_tokens:
            if token in name_lower:
                score += 0.15
        
        # 内容中匹配
        content_text = json.dumps(knowledge.content, ensure_ascii=False).lower()
        for token in query_tokens:
            if token in content_text:
                score += 0.1
        
        # 标签匹配
        tag_matches = sum(1 for tag in knowledge.tags if any(token in tag.lower() for token in query_tokens))
        if tag_matches > 0:
            score += 0.2 * min(tag_matches, 3)
        
        return min(score, 1.0)
    
    def search(self, 
               query: str, 
               search_type: SearchType = SearchType.HYBRID,
               domain_type: Optional[DomainType] = None,
               tags: Optional[List[str]] = None,
               limit: int = 10,
               min_score: float = 0.1) -> List[SearchResult]:
        """
        搜索领域知识
        
        Args:
            query: 搜索关键词
            search_type: 搜索类型
            domain_type: 领域过滤
            tags: 标签过滤
            limit: 返回结果数量
            min_score: 最低匹配分数
        
        Returns:
            排序后的搜索结果列表
        """
        query_tokens = self._tokenize(query)
        results = []
        
        all_knowledges = list(self.domain_manager.domain_knowledges.values())
        
        for knowledge in all_knowledges:
            # 应用领域过滤
            if domain_type and knowledge.domain_type != domain_type:
                continue
            
            # 应用标签过滤
            if tags:
                has_tag = any(tag in knowledge.tags for tag in tags)
                if not has_tag:
                    continue
            
            # 计算匹配分数
            if search_type == SearchType.KEYWORD:
                score = self._calculate_tfidf_score(query_tokens, knowledge)
                match_reason = "关键词匹配"
            elif search_type == SearchType.SEMANTIC:
                score = self._calculate_fuzzy_score(query, knowledge)
                match_reason = "语义匹配"
            else:  # HYBRID
                tfidf_score = self._calculate_tfidf_score(query_tokens, knowledge)
                fuzzy_score = self._calculate_fuzzy_score(query, knowledge)
                score = tfidf_score * 0.6 + fuzzy_score * 0.4
                match_reason = "混合匹配"
            
            if score >= min_score:
                results.append(SearchResult(
                    knowledge=knowledge,
                    score=score,
                    match_reason=match_reason
                ))
        
        # 排序
        results.sort(key=lambda x: x.score, reverse=True)
        
        # 限制数量并设置排名
        results = results[:limit]
        for i, result in enumerate(results, 1):
            result.rank = i
        
        return results
    
    def record_view(self, knowledge_id: str):
        """记录知识浏览"""
        if knowledge_id not in self.stats:
            self.stats[knowledge_id] = KnowledgeStats(knowledge_id=knowledge_id)
        
        stats = self.stats[knowledge_id]
        stats.view_count += 1
        stats.access_count += 1
        stats.last_accessed = datetime.now().isoformat()
        stats.relevance_score = min(stats.relevance_score + 0.1, 1.0)
        
        self._update_hot_score(knowledge_id)
        self._save_stats()
    
    def _update_hot_score(self, knowledge_id: str):
        """更新热度分数"""
        if knowledge_id not in self.stats:
            return
        
        stats = self.stats[knowledge_id]
        
        # 热度 = 访问频率 + 最近访问 + 相关度
        access_score = min(stats.access_count / 100.0, 0.5)
        
        # 最近访问衰减
        if stats.last_accessed:
            last_time = datetime.fromisoformat(stats.last_accessed)
            days_ago = (datetime.now() - last_time).days
            recency_score = max(0.5 - days_ago * 0.05, 0)
        else:
            recency_score = 0
        
        stats.hot_score = access_score * 0.4 + recency_score * 0.4 + stats.relevance_score * 0.2
    
    def get_recommendations(self,
                           source_knowledge_id: Optional[str] = None,
                           source_tags: Optional[List[str]] = None,
                           limit: int = 5,
                           recommend_types: Optional[List[str]] = None) -> List[RecommendationResult]:
        """
        获取知识推荐
        
        Args:
            source_knowledge_id: 源知识ID（用于相似推荐）
            source_tags: 源标签列表（用于相关推荐）
            limit: 推荐数量
            recommend_types: 推荐类型 ["similar", "related", "trending", "recent"]
        
        Returns:
            推荐结果列表
        """
        if recommend_types is None:
            recommend_types = ["similar", "related", "trending", "recent"]
        
        all_recommendations: List[RecommendationResult] = []
        
        # 1. 相似知识推荐（基于标签和内容）
        if "similar" in recommend_types and source_knowledge_id:
            similar = self._get_similar_recommendations(source_knowledge_id, limit // 2)
            all_recommendations.extend(similar)
        
        # 2. 相关知识推荐（基于标签）
        if "related" in recommend_types and source_tags:
            related = self._get_tag_based_recommendations(source_tags, limit // 2)
            all_recommendations.extend(related)
        
        # 3. 热门知识推荐
        if "trending" in recommend_types:
            trending = self._get_trending_recommendations(limit // 2)
            all_recommendations.extend(trending)
        
        # 4. 最近知识推荐
        if "recent" in recommend_types:
            recent = self._get_recent_recommendations(limit // 2)
            all_recommendations.extend(recent)
        
        # 去重并排序
        seen_ids = set()
        unique_recommendations = []
        for rec in all_recommendations:
            if rec.knowledge.knowledge_id not in seen_ids:
                seen_ids.add(rec.knowledge.knowledge_id)
                unique_recommendations.append(rec)
        
        unique_recommendations.sort(key=lambda x: x.score, reverse=True)
        return unique_recommendations[:limit]
    
    def _get_similar_recommendations(self, knowledge_id: str, limit: int) -> List[RecommendationResult]:
        """获取相似知识推荐"""
        source = self.domain_manager.get_domain_knowledge(knowledge_id)
        if not source:
            return []
        
        recommendations = []
        
        for knowledge in self.domain_manager.domain_knowledges.values():
            if knowledge.knowledge_id == knowledge_id:
                continue
            
            # 基于标签相似度
            source_tags = set(source.tags)
            target_tags = set(knowledge.tags)
            
            if source_tags and target_tags:
                intersection = source_tags & target_tags
                union = source_tags | target_tags
                jaccard = len(intersection) / len(union)
            else:
                jaccard = 0.0
            
            # 基于领域相似度
            domain_bonus = 1.0 if knowledge.domain_type == source.domain_type else 0.5
            
            score = jaccard * 0.7 + domain_bonus * 0.3
            
            if score > 0:
                recommendations.append(RecommendationResult(
                    knowledge=knowledge,
                    score=score,
                    reason=f"标签相似: {', '.join(intersection) if intersection else '同领域'}",
                    source_type="similar"
                ))
        
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]
    
    def _get_tag_based_recommendations(self, tags: List[str], limit: int) -> List[RecommendationResult]:
        """基于标签的推荐"""
        tag_set = set(tags)
        recommendations = []
        
        for knowledge in self.domain_manager.domain_knowledges.values():
            knowledge_tags = set(knowledge.tags)
            match_count = len(tag_set & knowledge_tags)
            
            if match_count > 0:
                score = match_count / max(len(tags), 1)
                matching_tags = list(tag_set & knowledge_tags)
                recommendations.append(RecommendationResult(
                    knowledge=knowledge,
                    score=score,
                    reason=f"标签匹配: {', '.join(matching_tags)}",
                    source_type="related"
                ))
        
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]
    
    def _get_trending_recommendations(self, limit: int) -> List[RecommendationResult]:
        """获取热门推荐"""
        # 确保所有知识都有统计
        for k_id in self.domain_manager.domain_knowledges:
            if k_id not in self.stats:
                self.stats[k_id] = KnowledgeStats(knowledge_id=k_id)
            self._update_hot_score(k_id)
        
        sorted_knowledges = sorted(
            self.domain_manager.domain_knowledges.values(),
            key=lambda k: self.stats.get(k.knowledge_id, KnowledgeStats(knowledge_id=k.knowledge_id)).hot_score,
            reverse=True
        )
        
        recommendations = []
        for knowledge in sorted_knowledges[:limit]:
            stats = self.stats.get(knowledge.knowledge_id, KnowledgeStats(knowledge_id=knowledge.knowledge_id))
            recommendations.append(RecommendationResult(
                knowledge=knowledge,
                score=stats.hot_score,
                reason=f"热度评分: {stats.hot_score:.2f} (访问: {stats.access_count})",
                source_type="trending"
            ))
        
        return recommendations
    
    def _get_recent_recommendations(self, limit: int) -> List[RecommendationResult]:
        """获取最近知识推荐"""
        sorted_knowledges = sorted(
            self.domain_manager.domain_knowledges.values(),
            key=lambda k: k.created_at,
            reverse=True
        )
        
        recommendations = []
        for i, knowledge in enumerate(sorted_knowledges[:limit]):
            score = 1.0 - (i / limit) * 0.5
            recommendations.append(RecommendationResult(
                knowledge=knowledge,
                score=score,
                reason=f"创建于: {knowledge.created_at[:19]}",
                source_type="recent"
            ))
        
        return recommendations
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """获取搜索统计信息"""
        total_views = sum(s.view_count for s in self.stats.values())
        total_accesses = sum(s.access_count for s in self.stats.values())
        
        # 标签统计
        all_tags = []
        for knowledge in self.domain_manager.domain_knowledges.values():
            all_tags.extend(knowledge.tags)
        tag_counts = Counter(all_tags)
        
        return {
            "total_knowledges": len(self.domain_manager.domain_knowledges),
            "total_views": total_views,
            "total_accesses": total_accesses,
            "top_tags": tag_counts.most_common(10),
            "stats_count": len(self.stats)
        }

