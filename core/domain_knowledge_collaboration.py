
"""
领域知识协作与共享系统 - 阶段34
支持知识共享、协作编辑、权限管理和版本合并
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path

from core.domain_knowledge_manager import DomainKnowledge, DomainType


class PermissionLevel(Enum):
    """权限级别"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class ShareStatus(Enum):
    """共享状态"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class ShareConfig:
    """共享配置"""
    share_id: str
    knowledge_id: str
    shared_by: str
    shared_with: Optional[str] = None  # None表示公开
    permission: PermissionLevel = PermissionLevel.READ
    expires_at: Optional[str] = None
    status: ShareStatus = ShareStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CollaborationRecord:
    """协作记录"""
    record_id: str
    knowledge_id: str
    user_id: str
    action: str  # "edit", "comment", "review"
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class KnowledgeFork:
    """知识分支"""
    fork_id: str
    original_knowledge_id: str
    forked_by: str
    forked_knowledge: DomainKnowledge
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    merge_status: str = "open"  # "open", "merged", "closed"


class DomainKnowledgeCollaboration:
    """领域知识协作管理器"""
    
    def __init__(self, domain_manager):
        self.domain_manager = domain_manager
        self.shares: Dict[str, ShareConfig] = {}
        self.collaborations: Dict[str, List[CollaborationRecord]] = {}
        self.forks: Dict[str, KnowledgeFork] = {}
        
        self.data_dir = Path("data/collaboration")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self._load_data()
    
    def _load_data(self):
        """加载协作数据"""
        shares_file = self.data_dir / "shares.json"
        if shares_file.exists():
            try:
                with open(shares_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for s_data in data.get("shares", []):
                    share = ShareConfig(
                        share_id=s_data["share_id"],
                        knowledge_id=s_data["knowledge_id"],
                        shared_by=s_data["shared_by"],
                        shared_with=s_data.get("shared_with"),
                        permission=PermissionLevel(s_data.get("permission", "read")),
                        expires_at=s_data.get("expires_at"),
                        status=ShareStatus(s_data.get("status", "active")),
                        created_at=s_data.get("created_at")
                    )
                    self.shares[share.share_id] = share
            except Exception as e:
                print(f"加载共享数据失败: {e}")
    
    def _save_data(self):
        """保存协作数据"""
        shares_file = self.data_dir / "shares.json"
        data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "shares": []
        }
        for share in self.shares.values():
            data["shares"].append({
                "share_id": share.share_id,
                "knowledge_id": share.knowledge_id,
                "shared_by": share.shared_by,
                "shared_with": share.shared_with,
                "permission": share.permission.value,
                "expires_at": share.expires_at,
                "status": share.status.value,
                "created_at": share.created_at
            })
        try:
            with open(shares_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存共享数据失败: {e}")
    
    def share_knowledge(self, 
                       knowledge_id: str,
                       shared_by: str,
                       shared_with: Optional[str] = None,
                       permission: str = "read",
                       expires_at: Optional[str] = None) -> Optional[ShareConfig]:
        """
        共享知识
        
        Args:
            knowledge_id: 知识ID
            shared_by: 分享者
            shared_with: 接收者，None表示公开
            permission: 权限级别
            expires_at: 过期时间
        
        Returns:
            共享配置
        """
        knowledge = self.domain_manager.get_domain_knowledge(knowledge_id)
        if not knowledge:
            print(f"知识 {knowledge_id} 不存在")
            return None
        
        share_id = f"share_{knowledge_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        share = ShareConfig(
            share_id=share_id,
            knowledge_id=knowledge_id,
            shared_by=shared_by,
            shared_with=shared_with,
            permission=PermissionLevel(permission),
            expires_at=expires_at
        )
        
        self.shares[share_id] = share
        self._save_data()
        
        print(f"共享知识: {knowledge.name} -> {shared_with or '公开'}")
        return share
    
    def revoke_share(self, share_id: str) -> bool:
        """撤销共享"""
        if share_id not in self.shares:
            return False
        
        self.shares[share_id].status = ShareStatus.REVOKED
        self._save_data()
        
        print(f"撤销共享: {share_id}")
        return True
    
    def check_permission(self, knowledge_id: str, user_id: str, required_permission: PermissionLevel) -> bool:
        """检查权限"""
        # 检查是否是知识所有者
        knowledge = self.domain_manager.get_domain_knowledge(knowledge_id)
        if knowledge and hasattr(knowledge, 'owner') and knowledge.owner == user_id:
            return True
        
        # 检查共享权限
        for share in self.shares.values():
            if share.knowledge_id == knowledge_id and share.status == ShareStatus.ACTIVE:
                # 检查是否过期
                if share.expires_at:
                    expires = datetime.fromisoformat(share.expires_at)
                    if datetime.now() > expires:
                        share.status = ShareStatus.EXPIRED
                        continue
                
                # 检查用户匹配
                if share.shared_with is None or share.shared_with == user_id:
                    perm_levels = {
                        PermissionLevel.READ: 1,
                        PermissionLevel.WRITE: 2,
                        PermissionLevel.ADMIN: 3
                    }
                    if perm_levels.get(share.permission, 0) >= perm_levels.get(required_permission, 0):
                        return True
        
        return False
    
    def get_shared_knowledges(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户可访问的共享知识"""
        results = []
        
        for share in self.shares.values():
            if share.status != ShareStatus.ACTIVE:
                continue
            
            # 检查过期
            if share.expires_at:
                expires = datetime.fromisoformat(share.expires_at)
                if datetime.now() > expires:
                    share.status = ShareStatus.EXPIRED
                    continue
            
            # 检查权限
            if share.shared_with is None or share.shared_with == user_id:
                knowledge = self.domain_manager.get_domain_knowledge(share.knowledge_id)
                if knowledge:
                    results.append({
                        "knowledge": knowledge,
                        "share": share,
                        "permission": share.permission.value
                    })
        
        return results
    
    def record_collaboration(self, 
                            knowledge_id: str,
                            user_id: str,
                            action: str,
                            content: Dict[str, Any]) -> bool:
        """记录协作行为"""
        if knowledge_id not in self.collaborations:
            self.collaborations[knowledge_id] = []
        
        record = CollaborationRecord(
            record_id=f"collab_{knowledge_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            knowledge_id=knowledge_id,
            user_id=user_id,
            action=action,
            content=content
        )
        
        self.collaborations[knowledge_id].append(record)
        
        print(f"记录协作: {user_id} {action} {knowledge_id}")
        return True
    
    def get_collaboration_history(self, knowledge_id: str) -> List[CollaborationRecord]:
        """获取协作历史"""
        return self.collaborations.get(knowledge_id, [])
    
    def fork_knowledge(self, knowledge_id: str, forked_by: str) -> Optional[KnowledgeFork]:
        """创建知识分支"""
        knowledge = self.domain_manager.get_domain_knowledge(knowledge_id)
        if not knowledge:
            print(f"知识 {knowledge_id} 不存在")
            return None
        
        # 创建副本
        from copy import deepcopy
        forked_knowledge = deepcopy(knowledge)
        forked_knowledge.knowledge_id = f"fork_{knowledge_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        forked_knowledge.name = f"[分支] {knowledge.name}"
        
        fork = KnowledgeFork(
            fork_id=f"fork_{knowledge_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            original_knowledge_id=knowledge_id,
            forked_by=forked_by,
            forked_knowledge=forked_knowledge
        )
        
        self.forks[fork.fork_id] = fork
        
        # 注册分支知识
        self.domain_manager.register_domain_knowledge(forked_knowledge)
        
        print(f"创建分支: {forked_knowledge.name}")
        return fork
    
    def merge_fork(self, fork_id: str) -> bool:
        """合并分支到原知识"""
        if fork_id not in self.forks:
            return False
        
        fork = self.forks[fork_id]
        if fork.merge_status != "open":
            print(f"分支 {fork_id} 状态不允许合并")
            return False
        
        original = self.domain_manager.get_domain_knowledge(fork.original_knowledge_id)
        if not original:
            return False
        
        # 合并内容
        original.content.update(fork.forked_knowledge.content)
        original.updated_at = datetime.now().isoformat()
        
        fork.merge_status = "merged"
        
        # 保存
        self.domain_manager._save_knowledge()
        
        print(f"合并分支: {fork_id} -> {fork.original_knowledge_id}")
        return True
    
    def get_collaboration_stats(self) -> Dict[str, Any]:
        """获取协作统计"""
        return {
            "total_shares": len(self.shares),
            "active_shares": sum(1 for s in self.shares.values() if s.status == ShareStatus.ACTIVE),
            "total_forks": len(self.forks),
            "merged_forks": sum(1 for f in self.forks.values() if f.merge_status == "merged"),
            "total_collaborations": sum(len(records) for records in self.collaborations.values())
        }

