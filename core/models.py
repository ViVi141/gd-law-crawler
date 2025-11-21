"""
数据模型定义
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class Policy:
    """政策基本信息"""
    id: str
    title: str
    office: str
    pass_date: str
    law_rule_type: int
    formulate_mode: str = ""
    timeliness: str = ""
    file_type: str = ""
    tag_names: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "office": self.office,
            "pass_date": self.pass_date,
            "law_rule_type": self.law_rule_type,
            "formulate_mode": self.formulate_mode,
            "timeliness": self.timeliness,
            "file_type": self.file_type,
            "tag_names": self.tag_names,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Policy":
        """从字典创建"""
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            office=data.get("officeVo", {}).get("groupName", ""),
            pass_date=data.get("passDate", ""),
            law_rule_type=data.get("lawRuleType", 0),
            formulate_mode=data.get("formulateMode", ""),
            timeliness=data.get("timeliness", ""),
            file_type=data.get("fileType", ""),
            tag_names=data.get("tagNames", ""),
        )


@dataclass
class FileAttachment:
    """附件信息"""
    id: str
    file_name: str
    file_path: str
    file_ext: str
    file_class: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_ext": self.file_ext,
            "file_class": self.file_class,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileAttachment":
        """从字典创建"""
        return cls(
            id=data.get("id", ""),
            file_name=data.get("fileName", ""),
            file_path=data.get("filePath", ""),
            file_ext=data.get("fileExt", ""),
            file_class=data.get("fileClass", ""),
        )


@dataclass
class PolicyDetail:
    """政策详细信息"""
    policy: Policy
    law_rule: Dict[str, Any]
    attachments: List[FileAttachment] = field(default_factory=list)
    keywords: str = ""
    effective_date: str = ""
    associate_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "policy": self.policy.to_dict(),
            "law_rule": self.law_rule,
            "attachments": [att.to_dict() for att in self.attachments],
            "keywords": self.keywords,
            "effective_date": self.effective_date,
            "associate_id": self.associate_id,
        }


@dataclass
class CrawlProgress:
    """爬取进度"""
    total_count: int = 0
    completed_count: int = 0
    failed_count: int = 0
    current_policy_id: str = ""
    current_policy_title: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    completed_policies: List[str] = field(default_factory=list)
    failed_policies: List[Dict[str, str]] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_count == 0:
            return 0.0
        return (self.completed_count / self.total_count) * 100
    
    @property
    def progress_percentage(self) -> float:
        """进度百分比"""
        if self.total_count == 0:
            return 0.0
        return ((self.completed_count + self.failed_count) / self.total_count) * 100
    
    @property
    def elapsed_time(self) -> Optional[float]:
        """已用时间（秒）"""
        if not self.start_time:
            return None
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_count": self.total_count,
            "completed_count": self.completed_count,
            "failed_count": self.failed_count,
            "current_policy_id": self.current_policy_id,
            "current_policy_title": self.current_policy_title,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "completed_policies": self.completed_policies,
            "failed_policies": self.failed_policies,
            "success_rate": self.success_rate,
            "progress_percentage": self.progress_percentage,
            "elapsed_time": self.elapsed_time,
        }

