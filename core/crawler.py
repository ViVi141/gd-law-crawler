"""
爬虫核心模块 - 政策爬取主逻辑
"""

import os
import json
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime

from .config import Config
from .api_client import APIClient
from .converter import DocumentConverter
from .models import Policy, PolicyDetail, FileAttachment, CrawlProgress


class PolicyCrawler:
    """政策爬虫核心类"""
    
    def __init__(self, config: Config, progress_callback: Optional[Callable] = None):
        """初始化爬虫
        
        Args:
            config: 配置对象
            progress_callback: 进度回调函数 (progress: CrawlProgress) -> None
        """
        self.config = config
        self.api_client = APIClient(config)
        self.converter = DocumentConverter()
        self.progress_callback = progress_callback
        self.stop_requested = False  # 停止标志
        self.progress = CrawlProgress()
        
        # 创建输出目录
        self._create_output_dirs()
    
    def _create_output_dirs(self):
        """创建输出目录"""
        output_dir = self.config.output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/json", exist_ok=True)
        os.makedirs(f"{output_dir}/files", exist_ok=True)
        os.makedirs(f"{output_dir}/markdown", exist_ok=True)
    
    def request_stop(self):
        """请求停止爬取"""
        self.stop_requested = True
        print("\n[停止] 收到停止请求，正在停止...")
    
    def _update_progress(self, **kwargs):
        """更新进度并触发回调"""
        for key, value in kwargs.items():
            setattr(self.progress, key, value)
        
        if self.progress_callback:
            self.progress_callback(self.progress)
    
    def search_all_policies(self, law_rule_type: int) -> List[Policy]:
        """搜索所有政策
        
        Args:
            law_rule_type: 政策类型
            
        Returns:
            政策列表
        """
        policies = []
        page_num = 1
        page_size = self.config.get("page_size", 20)
        
        type_names = {1: "地方性法规", 2: "政府规章", 3: "规范性文件"}
        type_name = type_names.get(law_rule_type, f"类型{law_rule_type}")
        
        print(f"\n搜索 {type_name} 列表...")
        
        while True:
            # 检查停止标志
            if self.stop_requested:
                print(f"[停止] 停止搜索 {type_name} 列表")
                break
            
            result = self.api_client.search_policies(law_rule_type, page_num, page_size)
            
            if not result:
                break
            
            data = result.get('data', {}) or {}
            rows = data.get('rows') or []
            total = data.get('total', 0)
            
            if not rows:
                break
            
            # 转换为Policy对象
            for row in rows:
                policy = Policy.from_dict(row)
                policies.append(policy)
            
            print(f"  第 {page_num} 页: 获取 {len(rows)} 条，累计 {len(policies)}/{total} 条")
            
            # 如果已获取所有数据，退出
            if len(rows) < page_size or len(policies) >= total:
                break
            
            page_num += 1
            time.sleep(self.config.request_delay)
        
        print(f"[OK] {type_name} 共获取 {len(policies)} 条政策")
        return policies
    
    def crawl_single_policy(self, policy: Policy) -> bool:
        """爬取单个政策
        
        Args:
            policy: 政策对象
            
        Returns:
            是否成功
        """
        self._update_progress(
            current_policy_id=policy.id,
            current_policy_title=policy.title
        )
        
        print(f"\n爬取政策: {policy.title}")
        print(f"ID: {policy.id}")
        print("=" * 60)
        
        # 1. 获取详情
        detail_data = self.api_client.get_policy_detail(policy.id)
        if not detail_data:
            print("[X] 获取详情失败")
            return False
        
        law_rule = detail_data.get('lawRule', {})
        file_list = detail_data.get('list', [])
        
        # 转换附件列表
        attachments = [FileAttachment.from_dict(f) for f in file_list]
        
        # 创建PolicyDetail对象
        detail = PolicyDetail(
            policy=policy,
            law_rule=law_rule,
            attachments=attachments,
            keywords=law_rule.get('keywords', ''),
            effective_date=law_rule.get('effectiveDate', ''),
            associate_id=law_rule.get('associate', '')
        )
        
        # 2. 保存JSON数据
        if self.config.get("save_json", True):
            self._save_json(policy.id, detail.to_dict())
        
        # 3. 下载并转换附件
        markdown_content = self._download_and_convert_files(policy, attachments)
        
        # 4. 生成RAG Markdown
        if self.config.get("save_markdown", True):
            self._generate_rag_markdown(policy, detail, markdown_content)
        
        print("[OK] 政策爬取完成")
        return True
    
    def _download_and_convert_files(
        self,
        policy: Policy,
        attachments: List[FileAttachment]
    ) -> Optional[str]:
        """下载并转换附件文件
        
        Args:
            policy: 政策对象
            attachments: 附件列表
            
        Returns:
            转换后的Markdown内容
        """
        if not attachments:
            return None
        
        # 筛选需要下载的文件
        target_files = []
        for att in attachments:
            ext = att.file_ext.lower()
            if (self.config.get("download_docx", True) and 'docx' in ext) or \
               (self.config.get("download_doc", True) and 'doc' in ext and 'docx' not in ext) or \
               (self.config.get("download_pdf", False) and 'pdf' in ext):
                target_files.append(att)
        
        if not target_files:
            return None
        
        print(f"\n从 {len(attachments)} 个附件中筛选出 {len(target_files)} 个文件")
        
        markdown_parts = []
        
        for i, att in enumerate(target_files, 1):
            print(f"\n  [{i}/{len(target_files)}] 处理: {att.file_name}")
            
            # 下载文件
            safe_name = "".join(c for c in att.file_name if c.isalnum() or c in (' ', '-', '_', '.')).strip()
            ext = os.path.splitext(att.file_name)[1] or f'.{att.file_ext}'
            save_path = f"{self.config.output_dir}/files/{policy.id}_{safe_name}{ext}"
            
            if self.api_client.download_file(att.file_path, save_path):
                print(f"    [OK] 下载成功: {save_path}")
                
                # 转换为Markdown
                print("    转换为Markdown...")
                content = self.converter.convert(save_path)
                
                if content:
                    markdown_parts.append(f"\n\n## {att.file_name}\n\n")
                    markdown_parts.append(content)
                
                # 文件间延迟
                if i < len(target_files):
                    time.sleep(0.3)
            else:
                print("    [X] 下载失败")
        
        if markdown_parts:
            result = '\n'.join(markdown_parts)
            print(f"\n  [OK] 已合并 {len(target_files)} 个文件的内容")
            return result
        
        return None
    
    def _save_json(self, policy_id: str, data: Dict):
        """保存JSON数据"""
        filepath = f"{self.config.output_dir}/json/policy_{policy_id}.json"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[OK] JSON已保存: {filepath}")
        except Exception as e:
            print(f"[X] JSON保存失败: {e}")
    
    def _generate_rag_markdown(
        self,
        policy: Policy,
        detail: PolicyDetail,
        markdown_content: Optional[str]
    ):
        """生成RAG格式的Markdown文件"""
        try:
            md_lines = []
            
            # YAML Front Matter
            md_lines.append('---')
            md_lines.append(f'title: "{policy.title}"')
            md_lines.append(f'policy_id: "{policy.id}"')
            md_lines.append(f'law_rule_type: "{policy.law_rule_type}"')
            md_lines.append(f'office: "{policy.office}"')
            md_lines.append(f'pass_date: "{policy.pass_date[:10]}"')
            md_lines.append(f'effective_date: "{detail.effective_date[:10] if detail.effective_date else ""}"')
            md_lines.append(f'file_type: "{policy.file_type}"')
            md_lines.append(f'timeliness: "{policy.timeliness}"')
            md_lines.append(f'formulate_mode: "{policy.formulate_mode}"')
            
            # 关键词
            if detail.keywords:
                keywords_list = [k.strip() for k in detail.keywords.split(',') if k.strip()]
                md_lines.append(f'keywords: {json.dumps(keywords_list, ensure_ascii=False)}')
            
            # 标签
            if policy.tag_names:
                tags_list = [t.strip() for t in policy.tag_names.split('、') if t.strip()]
                md_lines.append(f'tags: {json.dumps(tags_list, ensure_ascii=False)}')
            
            # 来源链接
            detail_url = f"https://www.gdpc.gov.cn:443/bascdata/securityJsp/nfrr_inner/internet/lawRule/lawRuleDetail.jsp?id={policy.id}&lawRuleType={policy.law_rule_type}"
            md_lines.append(f'source_url: "{detail_url}"')
            md_lines.append(f'crawl_time: "{time.strftime("%Y-%m-%d %H:%M:%S")}"')
            md_lines.append('---')
            md_lines.append('')
            
            # 标题
            md_lines.append(f'# {policy.title}')
            md_lines.append('')
            
            # 基本信息
            md_lines.append('## 基本信息')
            md_lines.append('')
            md_lines.append(f'- **制定机关**: {policy.office}')
            md_lines.append(f'- **通过日期**: {policy.pass_date[:10]}')
            if detail.effective_date:
                md_lines.append(f'- **生效日期**: {detail.effective_date[:10]}')
            md_lines.append(f'- **时效性**: {policy.timeliness}')
            md_lines.append(f'- **制定形式**: {policy.formulate_mode}')
            md_lines.append(f'- **来源链接**: [查看原文]({detail_url})')
            md_lines.append('')
            
            # 关键词
            if detail.keywords:
                md_lines.append('## 关键词')
                md_lines.append('')
                keywords_list = [k.strip() for k in detail.keywords.split(',') if k.strip()][:20]
                md_lines.append(', '.join(keywords_list))
                md_lines.append('')
            
            # 正文内容
            if markdown_content:
                md_lines.append('---')
                md_lines.append('')
                md_lines.append('## 正文内容')
                md_lines.append('')
                md_lines.append(markdown_content)
            else:
                md_lines.append('---')
                md_lines.append('')
                md_lines.append('## 正文内容')
                md_lines.append('')
                md_lines.append('> **注意**: 该政策的附件文件无法自动转换为文本格式。')
                md_lines.append('> ')
                md_lines.append('> 请访问[来源链接](#基本信息)查看完整文档内容。')
            
            # 保存文件
            file_number = self._get_next_file_number()
            safe_title = "".join(c for c in policy.title if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_title:
                safe_title = f"政策_{policy.id[:8]}"
            
            md_filename = f"{file_number:04d}_{safe_title}.md"
            md_filepath = f"{self.config.output_dir}/markdown/{md_filename}"
            
            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_lines))
            
            print(f"[OK] Markdown已保存: {md_filepath}")
            
        except Exception as e:
            print(f"[X] Markdown生成失败: {e}")
    
    def _get_next_file_number(self) -> int:
        """获取下一个文件编号"""
        markdown_dir = f"{self.config.output_dir}/markdown"
        
        if not os.path.exists(markdown_dir):
            return 1
        
        existing_files = [f for f in os.listdir(markdown_dir) if f.endswith('.md')]
        
        if not existing_files:
            return 1
        
        numbers = []
        for filename in existing_files:
            parts = filename.split('_', 1)
            if parts and len(parts) >= 2 and parts[0].isdigit():
                numbers.append(int(parts[0]))
        
        if not numbers:
            return 1
        
        return max(numbers) + 1
    
    def crawl_batch(self, law_rule_types: List[int] = [1, 2, 3]) -> CrawlProgress:
        """批量爬取
        
        Args:
            law_rule_types: 政策类型列表
            
        Returns:
            爬取进度
        """
        self.progress = CrawlProgress()
        self.progress.start_time = datetime.now()
        
        all_policies = []
        
        # 获取所有政策
        for law_rule_type in law_rule_types:
            # 检查停止标志
            if self.stop_requested:
                print("[停止] 停止获取政策列表")
                break
            
            policies = self.search_all_policies(law_rule_type)
            all_policies.extend(policies)
        
        # 如果已停止，返回当前进度
        if self.stop_requested:
            self.progress.end_time = datetime.now()
            return self.progress
        
        self.progress.total_count = len(all_policies)
        self._update_progress()
        
        print(f"\n开始爬取，共 {len(all_policies)} 条政策")
        print("=" * 60)
        
        # 爬取每个政策
        for i, policy in enumerate(all_policies, 1):
            # 检查停止标志
            if self.stop_requested:
                print("[停止] 停止爬取政策")
                break
            
            print(f"\n进度: [{i}/{len(all_policies)}]")
            
            success = self.crawl_single_policy(policy)
            
            if success:
                self.progress.completed_count += 1
                self.progress.completed_policies.append(policy.id)
            else:
                self.progress.failed_count += 1
                self.progress.failed_policies.append({
                    'id': policy.id,
                    'title': policy.title,
                    'reason': '爬取失败'
                })
            
            self._update_progress()
            
            # 请求间隔
            time.sleep(self.config.request_delay)
        
        self.progress.end_time = datetime.now()
        self._update_progress()
        
        # 输出统计
        print("\n" + "=" * 60)
        print("爬取完成")
        print("=" * 60)
        print(f"总计: {self.progress.total_count} 条")
        print(f"成功: {self.progress.completed_count} 条")
        print(f"失败: {self.progress.failed_count} 条")
        print(f"成功率: {self.progress.success_rate:.2f}%")
        
        return self.progress
    
    def close(self):
        """关闭爬虫"""
        if hasattr(self.api_client, 'close'):
            self.api_client.close()

