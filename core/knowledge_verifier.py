
import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class VerificationStatus(Enum):
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    DISPUTED = "disputed"
    REJECTED = "rejected"


class KnowledgeSource(Enum):
    USER_INPUT = "user_input"
    EXTERNAL_DATABASE = "external_database"
    WIKIPEDIA = "wikipedia"
    PLUGIN = "plugin"
    AGENT_INFERENCE = "agent_inference"
    DOCUMENT_EXTRACTION = "document_extraction"
    MANUAL_ENTRY = "manual_entry"
    CUSTOM_SOURCE = "custom_source"


@dataclass
class SourceCredibility:
    source_id: str
    source_type: KnowledgeSource
    credibility_score: float
    total_verifications: int = 0
    successful_verifications: int = 0
    failed_verifications: int = 0
    last_verified: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeConfidence:
    knowledge_id: str
    knowledge_type: str
    confidence: float
    verification_status: VerificationStatus
    source_credibility: float = 1.0
    total_verifications: int = 0
    last_verified: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeVerifier:
    def __init__(self, knowledge_graph: Any):
        self.kg = knowledge_graph
        self.source_credibilities: Dict[str, SourceCredibility] = {}
        self.knowledge_confidences: Dict[str, KnowledgeConfidence] = {}
        self.verification_logs: List[Dict[str, Any]] = []
        
        self._load_existing_confidences()
    
    def register_source(self, source_id: str, source_type: KnowledgeSource, initial_credibility: float = 0.7):
        self.source_credibilities[source_id] = SourceCredibility(
            source_id=source_id,
            source_type=source_type,
            credibility_score=initial_credibility
        )
    
    def update_source_credibility(self, source_id: str, success: bool):
        if source_id not in self.source_credibilities:
            self.register_source(source_id, KnowledgeSource.CUSTOM_SOURCE)
        
        credibility = self.source_credibilities[source_id]
        credibility.total_verifications += 1
        
        if success:
            credibility.successful_verifications += 1
        else:
            credibility.failed_verifications += 1
        
        prior = credibility.credibility_score
        weight = 1.0 / (credibility.total_verifications + 1)
        if success:
            credibility.credibility_score = prior * (1 - weight) + 1.0 * weight
        else:
            credibility.credibility_score = prior * (1 - weight)
        
        credibility.last_verified = datetime.now().isoformat()
    
    def get_source_credibility(self, source_id: str) -> float:
        if source_id in self.source_credibilities:
            return self.source_credibilities[source_id].credibility_score
        return 0.6
    
    def verify_node(self, node: Any) -> KnowledgeConfidence:
        return self._verify_knowledge(node, "node")
    
    def verify_edge(self, edge: Any) -> KnowledgeConfidence:
        return self._verify_knowledge(edge, "edge")
    
    def _verify_knowledge(self, knowledge_item: Any, knowledge_type: str) -> KnowledgeConfidence:
        knowledge_id = getattr(knowledge_item, 'id', None) or str(knowledge_item)
        
        if knowledge_id not in self.knowledge_confidences:
            self.knowledge_confidences[knowledge_id] = KnowledgeConfidence(
                knowledge_id=knowledge_id,
                knowledge_type=knowledge_type,
                confidence=0.5,
                verification_status=VerificationStatus.UNVERIFIED
            )
        
        confidence = self.knowledge_confidences[knowledge_id]
        
        validation_passed = True
        
        if hasattr(knowledge_item, 'name'):
            if len(knowledge_item.name.strip()) == 0:
                validation_passed = False
        
        if validation_passed:
            confidence.verification_status = VerificationStatus.VERIFIED
            confidence.confidence = min(1.0, confidence.confidence + 0.1)
        else:
            confidence.verification_status = VerificationStatus.DISPUTED
            confidence.confidence = max(0.0, confidence.confidence - 0.1)
        
        source_id = getattr(knowledge_item, 'attr', {}).get('source_id', 'unknown')
        confidence.source_credibility = self.get_source_credibility(source_id)
        
        base_confidence = confidence.source_credibility
        confidence.confidence = min(1.0, max(0.0, base_confidence + 0.2 - 0.1))
        
        confidence.total_verifications += 1
        confidence.last_verified = datetime.now().isoformat()
        
        return confidence
    
    def batch_verify_nodes(self, nodes: List[Any]) -> List[KnowledgeConfidence]:
        return [self.verify_node(node) for node in nodes]
    
    def batch_verify_edges(self, edges: List[Any]) -> List[KnowledgeConfidence]:
        return [self.verify_edge(edge) for edge in edges]
    
    def get_knowledge_confidence(self, knowledge_id: str) -> Optional[KnowledgeConfidence]:
        return self.knowledge_confidences.get(knowledge_id)
    
    def update_confidence(self, knowledge_id: str, new_confidence: float, reason: str):
        if knowledge_id not in self.knowledge_confidences:
            return False
        
        confidence = self.knowledge_confidences[knowledge_id]
        old_confidence = confidence.confidence
        confidence.confidence = max(0.0, min(1.0, new_confidence))
        
        log_entry = {
            "log_id": f"conf_change_{knowledge_id}_{int(datetime.now().timestamp())}",
            "knowledge_id": knowledge_id,
            "knowledge_type": confidence.knowledge_type,
            "result": True,
            "timestamp": datetime.now().isoformat(),
            "confidence_change": confidence.confidence - old_confidence,
            "details": reason
        }
        self.verification_logs.append(log_entry)
        
        return True
    
    def _load_existing_confidences(self):
        data_dir = Path("data")
        confidence_file = data_dir / "knowledge_confidences.json"
        
        if confidence_file.exists():
            try:
                with open(confidence_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for conf_data in data.get("confidences", []):
                    knowledge_id = conf_data.get("knowledge_id")
                    knowledge_type = conf_data.get("knowledge_type")
                    confidence_value = conf_data.get("confidence", 0.5)
                    status_str = conf_data.get("verification_status", "unverified")
                    status = VerificationStatus(status_str) if status_str in [s.value for s in VerificationStatus] else VerificationStatus.UNVERIFIED
                    
                    conf = KnowledgeConfidence(
                        knowledge_id=knowledge_id,
                        knowledge_type=knowledge_type,
                        confidence=confidence_value,
                        verification_status=status,
                        source_credibility=conf_data.get("source_credibility", 1.0),
                        total_verifications=conf_data.get("total_verifications", 0),
                        last_verified=conf_data.get("last_verified")
                    )
                    
                    self.knowledge_confidences[knowledge_id] = conf
            except Exception as e:
                print(f"加载置信度数据失败: {e}")
    
    def save_confidences(self):
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        confidence_file = data_dir / "knowledge_confidences.json"
        
        data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "confidences": []
        }
        
        for conf in self.knowledge_confidences.values():
            data["confidences"].append({
                "knowledge_id": conf.knowledge_id,
                "knowledge_type": conf.knowledge_type,
                "confidence": conf.confidence,
                "verification_status": conf.verification_status.value,
                "source_credibility": conf.source_credibility,
                "total_verifications": conf.total_verifications,
                "last_verified": conf.last_verified
            })
        
        try:
            with open(confidence_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存置信度数据失败: {e}")
            return False
    
    def get_verification_stats(self):
        total_nodes = 0
        total_edges = 0
        verified_count = 0
        disputed_count = 0
        rejected_count = 0
        unverified_count = 0
        
        for conf in self.knowledge_confidences.values():
            if conf.knowledge_type == "node":
                total_nodes += 1
            elif conf.knowledge_type == "edge":
                total_edges += 1
            
            if conf.verification_status == VerificationStatus.VERIFIED:
                verified_count += 1
            elif conf.verification_status == VerificationStatus.DISPUTED:
                disputed_count += 1
            elif conf.verification_status == VerificationStatus.REJECTED:
                rejected_count += 1
            else:
                unverified_count += 1
        
        avg_confidence = 0.0
        if self.knowledge_confidences:
            avg_confidence = sum(c.confidence for c in self.knowledge_confidences.values()) / len(self.knowledge_confidences)
        
        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "verified": verified_count,
            "disputed": disputed_count,
            "rejected": rejected_count,
            "unverified": unverified_count,
            "average_confidence": avg_confidence,
            "source_count": len(self.source_credibilities)
        }
