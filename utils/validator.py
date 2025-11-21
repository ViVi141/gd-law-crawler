"""
数据验证工具
"""

import re
from typing import Any


class Validator:
    """数据验证器"""
    
    @staticmethod
    def is_valid_policy_id(policy_id: str) -> bool:
        """验证政策ID格式
        
        Args:
            policy_id: 政策ID
            
        Returns:
            是否有效
        """
        if not policy_id:
            return False
        
        # UUID格式: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        return bool(re.match(pattern, policy_id, re.IGNORECASE))
    
    @staticmethod
    def is_valid_law_rule_type(law_rule_type: Any) -> bool:
        """验证政策类型
        
        Args:
            law_rule_type: 政策类型
            
        Returns:
            是否有效
        """
        try:
            return int(law_rule_type) in [1, 2, 3]
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """验证日期格式
        
        Args:
            date_str: 日期字符串
            
        Returns:
            是否有效
        """
        if not date_str:
            return False
        
        # YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS
        patterns = [
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
        ]
        
        return any(bool(re.match(p, date_str)) for p in patterns)
    
    @staticmethod
    def clean_html_entities(text: str) -> str:
        """清理HTML实体
        
        Args:
            text: 输入文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        replacements = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&nbsp;': ' ',
            '&#39;': "'",
            '&quot;': '"',
        }
        
        for entity, char in replacements.items():
            text = text.replace(entity, char)
        
        return text
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """净化文件名（移除非法字符）
        
        Args:
            filename: 文件名
            
        Returns:
            净化后的文件名
        """
        if not filename:
            return "untitled"
        
        # 移除Windows文件名非法字符
        illegal_chars = r'<>:"/\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        
        # 只保留字母、数字、空格、下划线、连字符、点
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
        
        # 移除前后空格
        filename = filename.strip()
        
        # 如果净化后为空，使用默认名称
        if not filename:
            filename = "untitled"
        
        return filename
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """验证URL格式
        
        Args:
            url: URL字符串
            
        Returns:
            是否有效
        """
        if not url:
            return False
        
        pattern = r'^https?://[\w\-]+(\.[\w\-]+)+[/#?]?.*$'
        return bool(re.match(pattern, url))

