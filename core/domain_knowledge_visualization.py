
"""
领域知识可视化与图谱展示系统 - 阶段35
支持知识图谱可视化、统计图表、关系网络展示
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
from collections import Counter

from core.domain_knowledge_manager import DomainKnowledge, DomainType


@dataclass
class VisualizationNode:
    """可视化节点"""
    id: str
    label: str
    domain_type: str
    size: int = 10
    color: str = "#4CAF50"
    x: float = 0.0
    y: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VisualizationEdge:
    """可视化边"""
    source: str
    target: str
    label: str = ""
    weight: float = 1.0
    color: str = "#999999"


@dataclass
class VisualizationGraph:
    """可视化图谱"""
    nodes: List[VisualizationNode] = field(default_factory=list)
    edges: List[VisualizationEdge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DomainKnowledgeVisualization:
    """领域知识可视化管理器"""
    
    # 领域类型颜色映射
    DOMAIN_COLORS = {
        DomainType.GENERAL: "#9E9E9E",
        DomainType.TECHNOLOGY: "#2196F3",
        DomainType.HEALTHCARE: "#F44336",
        DomainType.EDUCATION: "#FF9800",
        DomainType.FINANCE: "#4CAF50",
        DomainType.LEGAL: "#673AB7",
        DomainType.SCIENCE: "#00BCD4",
        DomainType.LANGUAGE: "#E91E63",
        DomainType.CUSTOM: "#795548"
    }
    
    def __init__(self, domain_manager):
        self.domain_manager = domain_manager
        self.export_dir = Path("data/visualizations")
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_domain_graph(self, 
                             domain_type: Optional[DomainType] = None,
                             include_relations: bool = True) -> VisualizationGraph:
        """
        生成领域知识图谱
        
        Args:
            domain_type: 指定领域类型，None则包含所有
            include_relations: 是否包含关系边
        
        Returns:
            可视化图谱
        """
        graph = VisualizationGraph()
        
        # 获取知识
        if domain_type:
            knowledges = self.domain_manager.search_domain_knowledge(
                "", domain_type=domain_type
            )
        else:
            knowledges = list(self.domain_manager.domain_knowledges.values())
        
        # 创建节点
        for i, knowledge in enumerate(knowledges):
            color = self.DOMAIN_COLORS.get(knowledge.domain_type, "#9E9E9E")
            # 根据置信度调整大小
            size = 10 + int(knowledge.confidence * 20)
            
            node = VisualizationNode(
                id=knowledge.knowledge_id,
                label=knowledge.name,
                domain_type=knowledge.domain_type.value,
                size=size,
                color=color,
                x=i * 50,
                y=i * 30,
                metadata={
                    "confidence": knowledge.confidence,
                    "tags": knowledge.tags,
                    "sources": knowledge.sources
                }
            )
            graph.nodes.append(node)
        
        # 创建边（基于标签相似度）
        if include_relations:
            for i, k1 in enumerate(knowledges):
                for j, k2 in enumerate(knowledges[i+1:], i+1):
                    # 计算标签交集
                    tags1 = set(k1.tags)
                    tags2 = set(k2.tags)
                    common_tags = tags1 & tags2
                    
                    if common_tags:
                        weight = len(common_tags) / max(len(tags1), len(tags2))
                        edge = VisualizationEdge(
                            source=k1.knowledge_id,
                            target=k2.knowledge_id,
                            label=",".join(common_tags),
                            weight=weight,
                            color="#CCCCCC"
                        )
                        graph.edges.append(edge)
        
        graph.metadata = {
            "generated_at": datetime.now().isoformat(),
            "total_nodes": len(graph.nodes),
            "total_edges": len(graph.edges),
            "domain_type": domain_type.value if domain_type else "all"
        }
        
        return graph
    
    def generate_domain_distribution(self) -> Dict[str, Any]:
        """生成领域分布统计"""
        domain_counts = Counter()
        domain_confidences = {}
        
        for knowledge in self.domain_manager.domain_knowledges.values():
            domain = knowledge.domain_type.value
            domain_counts[domain] += 1
            
            if domain not in domain_confidences:
                domain_confidences[domain] = []
            domain_confidences[domain].append(knowledge.confidence)
        
        distribution = []
        for domain, count in domain_counts.most_common():
            avg_confidence = sum(domain_confidences[domain]) / len(domain_confidences[domain])
            color = self.DOMAIN_COLORS.get(
                DomainType(domain), "#9E9E9E"
            )
            distribution.append({
                "domain": domain,
                "count": count,
                "avg_confidence": round(avg_confidence, 2),
                "color": color,
                "percentage": round(count / len(self.domain_manager.domain_knowledges) * 100, 1)
            })
        
        return {
            "total": len(self.domain_manager.domain_knowledges),
            "distribution": distribution
        }
    
    def generate_tag_cloud(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """生成标签云"""
        tag_counts = Counter()
        tag_domains = {}
        
        for knowledge in self.domain_manager.domain_knowledges.values():
            for tag in knowledge.tags:
                tag_counts[tag] += 1
                if tag not in tag_domains:
                    tag_domains[tag] = set()
                tag_domains[tag].add(knowledge.domain_type.value)
        
        max_count = max(tag_counts.values()) if tag_counts else 1
        
        tags = []
        for tag, count in tag_counts.most_common(top_n):
            size = 10 + int((count / max_count) * 30)
            tags.append({
                "text": tag,
                "size": size,
                "count": count,
                "domains": list(tag_domains[tag])
            })
        
        return tags
    
    def generate_confidence_chart(self) -> Dict[str, Any]:
        """生成置信度分布图"""
        ranges = {
            "0.0-0.2": 0,
            "0.2-0.4": 0,
            "0.4-0.6": 0,
            "0.6-0.8": 0,
            "0.8-1.0": 0
        }
        
        for knowledge in self.domain_manager.domain_knowledges.values():
            conf = knowledge.confidence
            if conf < 0.2:
                ranges["0.0-0.2"] += 1
            elif conf < 0.4:
                ranges["0.2-0.4"] += 1
            elif conf < 0.6:
                ranges["0.4-0.6"] += 1
            elif conf < 0.8:
                ranges["0.6-0.8"] += 1
            else:
                ranges["0.8-1.0"] += 1
        
        return {
            "title": "知识置信度分布",
            "ranges": list(ranges.keys()),
            "values": list(ranges.values())
        }
    
    def export_to_json(self, graph: VisualizationGraph, file_name: Optional[str] = None) -> str:
        """导出图谱为JSON"""
        if not file_name:
            file_name = f"graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        file_path = self.export_dir / file_name
        
        data = {
            "nodes": [
                {
                    "id": n.id,
                    "label": n.label,
                    "domain_type": n.domain_type,
                    "size": n.size,
                    "color": n.color,
                    "x": n.x,
                    "y": n.y,
                    "metadata": n.metadata
                }
                for n in graph.nodes
            ],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "label": e.label,
                    "weight": e.weight,
                    "color": e.color
                }
                for e in graph.edges
            ],
            "metadata": graph.metadata
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return str(file_path)
    
    def export_to_html(self, graph: VisualizationGraph, file_name: Optional[str] = None) -> str:
        """导出为交互式HTML"""
        if not file_name:
            file_name = f"graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        file_path = self.export_dir / file_name
        
        # 生成简单的HTML可视化
        nodes_json = json.dumps([
            {"id": n.id, "label": n.label, "color": n.color, "size": n.size}
            for n in graph.nodes
        ], ensure_ascii=False)
        
        edges_json = json.dumps([
            {"source": e.source, "target": e.target, "label": e.label}
            for e in graph.edges
        ], ensure_ascii=False)
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>领域知识图谱</title>
    <style>
        body {{ margin: 0; font-family: Arial, sans-serif; }}
        #graph {{ width: 100vw; height: 100vh; background: #f5f5f5; }}
        .node {{ cursor: pointer; }}
        .node text {{ font-size: 12px; pointer-events: none; }}
        .edge {{ stroke-opacity: 0.6; }}
        #info {{ position: absolute; top: 10px; left: 10px; background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div id="info">
        <h3>领域知识图谱</h3>
        <p>节点数: {len(graph.nodes)}</p>
        <p>边数: {len(graph.edges)}</p>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    <svg id="graph"></svg>
    <script>
        const nodes = {nodes_json};
        const edges = {edges_json};
        
        const svg = document.getElementById('graph');
        const width = window.innerWidth;
        const height = window.innerHeight;
        svg.setAttribute('width', width);
        svg.setAttribute('height', height);
        
        // 简单的力导向布局
        const nodeMap = {{}};
        nodes.forEach((n, i) => {{
            n.x = width/2 + Math.cos(i * 2 * Math.PI / nodes.length) * 200;
            n.y = height/2 + Math.sin(i * 2 * Math.PI / nodes.length) * 200;
            nodeMap[n.id] = n;
        }});
        
        // 绘制边
        edges.forEach(e => {{
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', nodeMap[e.source].x);
            line.setAttribute('y1', nodeMap[e.source].y);
            line.setAttribute('x2', nodeMap[e.target].x);
            line.setAttribute('y2', nodeMap[e.target].y);
            line.setAttribute('stroke', '#999');
            line.setAttribute('stroke-width', '1');
            line.classList.add('edge');
            svg.appendChild(line);
        }});
        
        // 绘制节点
        nodes.forEach(n => {{
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.classList.add('node');
            g.setAttribute('transform', `translate(${{n.x}}, ${{n.y}})`);
            
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('r', n.size);
            circle.setAttribute('fill', n.color);
            g.appendChild(circle);
            
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('dy', n.size + 15);
            text.textContent = n.label;
            g.appendChild(text);
            
            svg.appendChild(g);
        }});
    </script>
</body>
</html>"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(file_path)
    
    def get_visualization_summary(self) -> Dict[str, Any]:
        """获取可视化摘要"""
        return {
            "total_knowledges": len(self.domain_manager.domain_knowledges),
            "domain_distribution": self.generate_domain_distribution(),
            "tag_cloud": self.generate_tag_cloud(10),
            "confidence_chart": self.generate_confidence_chart(),
            "export_dir": str(self.export_dir)
        }

