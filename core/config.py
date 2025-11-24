"""
配置管理模块
"""

import os
import json
from typing import Any


class Config:
    """配置管理类"""

    # 默认配置
    DEFAULT_CONFIG = {
        # API配置
        "api_base_url": "https://www.gdpc.gov.cn:443/bascdata",
        
        # 请求配置
        "request_delay": 2,
        "retry_delay": 5,
        "max_retries": 3,
        "rate_limit_delay": 30,
        "session_rotate_interval": 50,
        "timeout": 30,
        
        # 爬取配置
        "page_size": 20,
        "law_rule_types": [1, 2, 3],
        
        # 输出配置
        "output_dir": "crawled_data",
        "save_json": True,
        "save_markdown": True,
        "save_files": True,
        
        # 文件下载配置
        "download_docx": True,
        "download_doc": True,
        "download_pdf": False,
        "download_all_files": False,  # 下载所有形式的附件（忽略文件类型）
        
        # 代理配置
        "use_proxy": False,
        "kuaidaili_api_key": "",
        
        # 日志配置
        "log_level": "INFO",
        "log_file": "crawler.log",
        
        # GUI配置（优化后的尺寸：1200x1000，确保设置选项卡按钮可见）
        "window_width": 1200,
        "window_height": 1000,
        "theme": "light",
    }
    
    def __init__(self, config_file: str = "config.json"):
        """初始化配置
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self) -> bool:
        """从文件加载配置
        
        Returns:
            加载是否成功
        """
        if not os.path.exists(self.config_file):
            self.save()
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                self.config.update(user_config)
            return True
        except Exception as e:
            print(f"配置加载失败: {e}")
            return False
    
    def save(self) -> bool:
        """保存配置到文件
        
        Returns:
            保存是否成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"配置保存失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项
        
        Args:
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项
        
        Args:
            key: 配置键名
            value: 配置值
        """
        self.config[key] = value
    
    def reset(self) -> None:
        """重置为默认配置"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
    
    @property
    def api_base_url(self) -> str:
        return self.get("api_base_url")
    
    @property
    def output_dir(self) -> str:
        return self.get("output_dir")
    
    @property
    def request_delay(self) -> float:
        return self.get("request_delay")
    
    @property
    def max_retries(self) -> int:
        return self.get("max_retries")
    
    @property
    def use_proxy(self) -> bool:
        return self.get("use_proxy")
    
    @property
    def kuaidaili_api_key(self) -> str:
        return self.get("kuaidaili_api_key")

