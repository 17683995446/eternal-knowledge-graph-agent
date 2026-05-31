"""
基于第一性原理，轻量化永动知识图谱智能体 - 语义增强模块
实现知识向量嵌入、相似度计算和语义检索功能
"""
import math
import hashlib
import json
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
from core.knowledge_graph import KnowledgeGraph


class VectorEmbedding:
    """
    知识向量嵌入 - 将节点和关系转换为向量表示
    采用轻量化方法，不依赖外部大型模型
    """
    
    def __init__(self, vector_dim: int = 128):
        self.vector_dim = vector_dim
        self.word_hash_cache = {}  # 词 -> 向量缓存
        
    def _text_to_hash(self, text: str) -> int:
        """将文本转换为稳定的哈希值"""
        return int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
        
    def embed_text(self, text: str) -> List[float]:
        """
        基于文本内容生成向量嵌入
        使用哈希方法，无外部依赖
        """
        if text in self.word_hash_cache:
            return self.word_hash_cache[text]
        
        # 初始化向量
        vector = [0.0] * self.vector_dim
        
        # 分解文本为词级单元
        words = self._tokenize(text)
        
        # 为每个词生成向量并累加
        for word in words:
            word_hash = self._text_to_hash(word)
            for i in range(self.vector_dim):
                # 使用位运算生成伪随机但确定性的值
                bit_val = (word_hash >> (i % 60)) & 1
                sign = 1 if bit_val else -1
                vector[i] += sign * (1.0 / math.sqrt(len(words)))
        
        # 归一化向量
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        
        self.word_hash_cache[text] = vector
        return vector
    
    def _tokenize(self, text: str) -> List[str]:
        """简单的文本分词（支持中英文）"""
        # 简单实现：按空格和标点符号分割
        tokens = []
        current_token = []
        
        for char in text:
            if char.isalnum() or char in ['_', '-']:
                current_token.append(char)
            else:
                if current_token:
                    tokens.append(''.join(current_token))
                    current_token = []
                # 单个字符作为token（针对中文等）
                if not char.isspace():
                    tokens.append(char)
        
        if current_token:
            tokens.append(''.join(current_token))
        
        return tokens if tokens else [text]
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


class SemanticSearch:
    """
    语义检索功能 - 超越简单关键词匹配
    支持语义相似度、关联搜索等
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
        self.embedding = VectorEmbedding()
        self.node_vectors = {}  # node_id -> vector
        self._build_index()
        
    def _build_index(self):
        """构建索引：为现有节点生成向量"""
        for node_id, node in self.kg.nodes.items():
            # 结合节点名称和属性生成向量
            text_repr = node.name
            if node.attr:
                text_repr += ' ' + json.dumps(node.attr, ensure_ascii=False)
            self.node_vectors[node_id] = self.embedding.embed_text(text_repr)
    
    def add_node_vector(self, node_id: str, node_name: str, node_attr: Optional[Dict] = None):
        """添加新节点的向量表示"""
        text_repr = node_name
        if node_attr:
            text_repr += ' ' + json.dumps(node_attr, ensure_ascii=False)
        self.node_vectors[node_id] = self.embedding.embed_text(text_repr)
    
    def semantic_search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        语义搜索：查找与查询语义相似的节点
        返回: [(node_name, similarity_score), ...]
        """
        query_vector = self.embedding.embed_text(query)
        scores = []
        
        for node_id, node_vector in self.node_vectors.items():
            node = self.kg.nodes.get(node_id)
            if node and node.valid:
                similarity = self.embedding.cosine_similarity(query_vector, node_vector)
                scores.append((node.name, similarity))
        
        # 按相似度排序并返回前K个
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def find_similar_nodes(self, node_name: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """查找与指定节点相似的其他节点"""
        node = self.kg._get_node_by_name(node_name)
        if not node or node.id not in self.node_vectors:
            return []
        
        target_vector = self.node_vectors[node.id]
        scores = []
        
        for other_id, other_vector in self.node_vectors.items():
            if other_id != node.id:
                other_node = self.kg.nodes.get(other_id)
                if other_node and other_node.valid:
                    similarity = self.embedding.cosine_similarity(target_vector, other_vector)
                    scores.append((other_node.name, similarity))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


class KnowledgeExporter:
    """
    知识图谱导出 - 支持多种标准格式
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
    
    def export_json_ld(self) -> Dict[str, Any]:
        """
        导出为JSON-LD格式
        JSON-LD是W3C推荐的知识图谱标准格式
        """
        # 构建上下文
        context = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "name": "rdfs:label",
            "type": "rdf:type",
            "relatedTo": "rdfs:seeAlso"
        }
        
        # 构建节点
        entities = []
        for node_id, node in self.kg.nodes.items():
            if node.valid:
                entity = {
                    "@id": f"urn:node:{node_id}",
                    "@type": ["Entity"],
                    "name": node.name,
                    "createdAt": node.created_at
                }
                # 添加自定义属性
                if node.attr:
                    entity.update(node.attr)
                entities.append(entity)
        
        # 构建边
        relations = []
        for edge in self.kg.edges:
            # 查找源和目标节点ID
            source_node = self.kg._get_node_by_name(edge.source)
            target_node = self.kg._get_node_by_name(edge.target)
            
            if source_node and target_node and source_node.valid and target_node.valid:
                relation = {
                    "@id": f"urn:edge:{hash(edge.source + edge.target + edge.relation)}",
                    "@type": ["Relation"],
                    "source": {"@id": f"urn:node:{source_node.id}"},
                    "target": {"@id": f"urn:node:{target_node.id}"},
                    "relation": edge.relation,
                    "weight": edge.weight,
                    "createdAt": edge.created_at
                }
                relations.append(relation)
        
        return {
            "@context": context,
            "@graph": entities + relations
        }
    
    def export_turtle(self) -> str:
        """
        导出为Turtle格式（RDF的简洁表示）
        Turtle是一种常用的RDF序列化格式
        """
        lines = []
        
        # 前缀声明
        lines.append("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
        lines.append("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
        lines.append("@prefix ex: <urn:eternal-agent:> .")
        lines.append("")
        
        # 输出节点
        for node_id, node in self.kg.nodes.items():
            if node.valid:
                node_uri = f"ex:node-{node_id}"
                # 转义特殊字符
                safe_name = node.name.replace('"', '\\"')
                lines.append(f'{node_uri} rdf:type ex:Entity .')
                lines.append(f'{node_uri} rdfs:label "{safe_name}" .')
                
                if node.attr:
                    for key, value in node.attr.items():
                        safe_value = str(value).replace('"', '\\"')
                        lines.append(f'{node_uri} ex:{key} "{safe_value}" .')
                lines.append("")
        
        # 输出边
        for edge in self.kg.edges:
            source_node = self.kg._get_node_by_name(edge.source)
            target_node = self.kg._get_node_by_name(edge.target)
            
            if source_node and target_node and source_node.valid and target_node.valid:
                source_uri = f"ex:node-{source_node.id}"
                target_uri = f"ex:node-{target_node.id}"
                
                # 关系URI安全处理
                relation_safe = edge.relation.replace(" ", "_")
                lines.append(f'{source_uri} ex:{relation_safe} {target_uri} .')
                lines.append(f'{source_uri} ex:weight "{edge.weight}"^^xsd:decimal .')
                lines.append("")
        
        return "\n".join(lines)
    
    def export_graphviz(self) -> str:
        """
        导出为Graphviz格式，用于可视化
        可以通过Graphviz工具渲染为图片
        """
        lines = []
        lines.append("digraph KnowledgeGraph {")
        lines.append("    rankdir=LR;")
        lines.append("    node [shape=ellipse, style=filled, fillcolor=lightblue];")
        lines.append("")
        
        # 添加节点
        for node_id, node in self.kg.nodes.items():
            if node.valid:
                # 转义特殊字符
                safe_name = node.name.replace('"', '\\"').replace('\n', ' ')
                lines.append(f'    "{node_id}" [label="{safe_name}"];')
        
        lines.append("")
        
        # 添加边
        for edge in self.kg.edges:
            source_node = self.kg._get_node_by_name(edge.source)
            target_node = self.kg._get_node_by_name(edge.target)
            
            if source_node and target_node and source_node.valid and target_node.valid:
                # 根据权重设置边的粗细
                penwidth = max(1, int(edge.weight * 5))
                safe_label = edge.relation.replace('"', '\\"')
                
                lines.append(
                    f'    "{source_node.id}" -> "{target_node.id}" '
                    f'[label="{safe_label}", penwidth={penwidth}, tooltip="weight={edge.weight:.2f}"];'
                )
        
        lines.append("}")
        return "\n".join(lines)
    
    def export_markdown(self) -> str:
        """
        导出为Markdown格式，便于阅读
        """
        lines = []
        lines.append("# 知识图谱导出\n")
        lines.append(f"> 导出时间: {self.kg._timestamp()}\n")
        
        # 统计信息
        lines.append("## 统计信息\n")
        lines.append(f"- 节点总数: {len([n for n in self.kg.nodes.values() if n.valid])}\n")
        lines.append(f"- 关系总数: {len(self.kg.edges)}\n\n")
        
        # 节点列表
        lines.append("## 节点列表\n")
        for node_id, node in self.kg.nodes.items():
            if node.valid:
                lines.append(f"### {node.name}\n")
                lines.append(f"- ID: {node.id}\n")
                lines.append(f"- 创建时间: {node.created_at}\n")
                if node.attr:
                    lines.append("- 属性:\n")
                    for key, value in node.attr.items():
                        lines.append(f"  - {key}: {value}\n")
                lines.append("\n")
        
        # 关系列表
        lines.append("## 关系列表\n")
        for edge in self.kg.edges:
            lines.append(f"- **{edge.source}** → **{edge.target}** ({edge.relation}), 权重: {edge.weight:.2f}\n")
        
        return "".join(lines)
