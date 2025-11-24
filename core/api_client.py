"""
API客户端模块 - 处理所有HTTP请求
"""

import requests
import time
import random
import warnings
from typing import Dict, Optional, Any
from urllib.parse import quote

# 禁用 urllib3 的 HeaderParsingError 警告（服务器响应头格式不完全标准，但不影响功能）
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.HeaderParsingError)
except (ImportError, AttributeError):
    pass

from .config import Config


# User-Agent列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
]


class APIClient:
    """API客户端类"""
    
    def __init__(self, config: Config):
        """初始化API客户端
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.session = self._create_session()
        self.request_count = 0
        self.current_proxy = None
        self.q_token = ""
        
        # 初始化代理（如果启用）
        self._init_proxy()
    
    def _create_session(self) -> requests.Session:
        """创建新的会话"""
        session = requests.Session()
        
        # 随机选择User-Agent
        user_agent = random.choice(USER_AGENTS)
        
        # 设置请求头
        session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.gdpc.gov.cn/',
            'Origin': 'https://www.gdpc.gov.cn',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })
        
        return session
    
    def _init_proxy(self):
        """初始化代理"""
        if not self.config.use_proxy:
            return
        
        api_key = self.config.kuaidaili_api_key
        if not api_key:
            return
        
        try:
            # 尝试导入快代理SDK
            import kdl
            
            if ':' in api_key:
                secret_id, secret_key = api_key.split(':', 1)
                auth = kdl.Auth(secret_id, secret_key)
                self.kuaidaili_client = kdl.Client(auth, timeout=(8, 12), max_retries=3)
                print("[信息] 快代理已启用")
            else:
                print("[警告] 快代理API密钥格式错误，需要 secret_id:secret_key")
        except ImportError:
            print("[警告] 快代理SDK未安装: pip install kdl")
        except Exception as e:
            print(f"[警告] 快代理初始化失败: {e}")
    
    def _get_proxy(self, force_new: bool = False) -> Optional[Dict[str, str]]:
        """获取代理IP
        
        Args:
            force_new: 是否强制获取新代理
            
        Returns:
            代理配置字典
        """
        if not self.config.use_proxy:
            return None
        
        if force_new or self.current_proxy is None:
            try:
                if hasattr(self, 'kuaidaili_client'):
                    proxy_list = self.kuaidaili_client.get_dps(1, format='json')
                    if proxy_list and len(proxy_list) > 0:
                        self.current_proxy = proxy_list[0]
                        print(f"  [代理] 获取新代理: {self.current_proxy[:50]}...")
            except Exception as e:
                if force_new:
                    print(f"  [警告] 获取代理失败: {e}")
                self.current_proxy = None
        
        if self.current_proxy:
            return {
                'http': f'http://{self.current_proxy}',
                'https': f'http://{self.current_proxy}',
            }
        
        return None
    
    def _rotate_session(self):
        """轮换会话"""
        if hasattr(self.session, 'close'):
            try:
                self.session.close()
            except Exception:
                pass
        
        self.session = self._create_session()
        self.request_count = 0
        print("  [会话轮换] 已创建新会话")
    
    def _check_and_rotate_session(self):
        """检查并轮换会话"""
        self.request_count += 1
        if self.request_count >= self.config.get("session_rotate_interval", 50):
            self._rotate_session()
    
    def search_policies(
        self,
        law_rule_type: int,
        page_num: int = 1,
        page_size: int = 20
    ) -> Optional[Dict[str, Any]]:
        """搜索政策列表
        
        Args:
            law_rule_type: 政策类型 (1/2/3)
            page_num: 页码
            page_size: 每页数量
            
        Returns:
            搜索结果
        """
        url = f"{self.config.api_base_url}/nfrr/law-rule!noSession_es_regulation_search.gx"
        
        params = {
            "pageNum": page_num,
            "pageSize": page_size,
            "lawRuleType": law_rule_type,
            "orderByColumn": "passDate"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Q-Token': self.q_token
        }
        
        self._check_and_rotate_session()
        
        for retry in range(self.config.max_retries):
            try:
                proxies = self._get_proxy(force_new=(retry > 0))
                response = self.session.post(
                    url,
                    json=params,
                    headers=headers,
                    timeout=self.config.get("timeout", 30),
                    proxies=proxies
                )
                response.raise_for_status()
                result = response.json()
                
                # 更新Q-Token
                if 'msg' in result:
                    self.q_token = result['msg']
                
                if result.get('code') == 200:
                    return result
                else:
                    error_msg = result.get('msg', '未知错误')
                    print(f"[X] 搜索失败: {error_msg}")
                    
                    # 检查是否限流
                    if "Too many requests" in str(error_msg) or "rate limit" in str(error_msg).lower():
                        if retry < self.config.max_retries - 1:
                            wait_time = self.config.get("rate_limit_delay", 30) * (retry + 1)
                            print(f"  [限流] 等待 {wait_time} 秒...")
                            time.sleep(wait_time)
                            continue
                    
                    return None
                    
            except Exception as e:
                print(f"[X] 请求异常: {e}")
                
                if retry < self.config.max_retries - 1:
                    wait_time = self.config.get("retry_delay", 5) * (retry + 1)
                    print(f"  [重试 {retry + 1}/{self.config.max_retries}] 等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                else:
                    return None
        
        return None
    
    def get_policy_detail(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """获取政策详情
        
        Args:
            policy_id: 政策ID
            
        Returns:
            政策详情
        """
        url = f"{self.config.api_base_url}/nfrr/law-rule!noSession_getById.gx"
        data = {'id': policy_id}
        
        self._check_and_rotate_session()
        
        for retry in range(self.config.max_retries):
            try:
                proxies = self._get_proxy(force_new=(retry > 0))
                response = self.session.post(
                    url,
                    data=data,
                    timeout=self.config.get("timeout", 30),
                    proxies=proxies
                )
                response.raise_for_status()
                result = response.json()
                
                if result and ('lawRule' in result or 'list' in result):
                    return result
                else:
                    print("[X] 详情数据格式异常")
                    if retry < self.config.max_retries - 1:
                        wait_time = self.config.get("retry_delay", 5) * (retry + 1)
                        time.sleep(wait_time)
                        continue
                    return None
                    
            except Exception as e:
                print(f"[X] 获取详情失败: {e}")
                
                if retry < self.config.max_retries - 1:
                    wait_time = self.config.get("retry_delay", 5) * (retry + 1)
                    time.sleep(wait_time)
                else:
                    return None
        
        return None
    
    def download_file(
        self,
        file_path: str,
        save_path: str,
        chunk_size: int = 8192
    ) -> bool:
        """下载文件
        
        Args:
            file_path: 文件路径（服务器端）
            save_path: 保存路径（本地）
            chunk_size: 分块大小
            
        Returns:
            是否下载成功
        """
        # 处理文件路径特殊字符
        processed_path = file_path.replace('(', 'left').replace(')', 'right')
        processed_path = processed_path.replace('（', 'zLeft').replace('）', 'zRight')
        processed_path = processed_path.replace('[', 'lBracket').replace(']', 'rBracket')
        
        url = f"{self.config.api_base_url}/downloadFile?fileFolder={quote(processed_path, safe='')}"
        
        self._check_and_rotate_session()
        
        for retry in range(self.config.max_retries):
            try:
                proxies = self._get_proxy(force_new=(retry > 0))
                
                # 禁用 urllib3 的 HeaderParsingError 警告
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    try:
                        import urllib3
                        urllib3.disable_warnings(urllib3.exceptions.HeaderParsingError)
                    except (ImportError, AttributeError):
                        pass
                    
                    response = self.session.get(
                        url,
                        stream=True,
                        timeout=60,
                        proxies=proxies
                    )
                    response.raise_for_status()
                
                # 下载文件
                import os
                try:
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                    
                    # 检查文件是否成功下载
                    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                        return True
                    else:
                        print("  [X] 下载失败：文件为空或不存在")
                        return False
                        
                except Exception as download_error:
                    # 即使下载过程中出错，也检查文件是否已部分下载
                    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                        # 文件已部分下载，可能是 HeaderParsingError 导致的
                        error_str = str(download_error)
                        if 'HeaderParsingError' in error_str or 'NoBoundaryInMultipartDefect' in error_str:
                            # 忽略这个解析错误，文件已成功下载
                            return True
                    raise  # 重新抛出异常
                
            except Exception as e:
                # 检查是否是 HeaderParsingError（文件可能已成功下载）
                import os
                error_str = str(e)
                error_type = type(e).__name__
                
                if 'HeaderParsingError' in error_type or 'NoBoundaryInMultipartDefect' in error_str:
                    # 检查文件是否已成功下载
                    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                        # 文件已成功下载，忽略这个解析错误
                        return True
                
                print(f"  [X] 下载失败: {e}")
                
                if retry < self.config.max_retries - 1:
                    wait_time = self.config.get("retry_delay", 5) * (retry + 1)
                    print(f"  [重试 {retry + 1}/{self.config.max_retries}] 等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                else:
                    return False
        
        return False
    
    def close(self):
        """关闭客户端"""
        if hasattr(self.session, 'close'):
            try:
                self.session.close()
            except Exception:
                pass

