"""
爬取配置选项卡
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Callable

from core import Config


class CrawlTab:
    """爬取配置选项卡"""
    
    def __init__(
        self,
        parent,
        config: Config,
        start_callback: Callable,
        stop_callback: Callable
    ):
        """初始化
        
        Args:
            parent: 父窗口
            config: 配置对象
            start_callback: 开始爬取回调
            stop_callback: 停止爬取回调
        """
        self.config = config
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        
        # 创建主框架（统一间距：12px）
        self.frame = ttk.Frame(parent, padding="12")
        
        # 创建界面
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 爬取模式选择（统一间距：组件间距8px，内部padding 10px）
        mode_frame = ttk.LabelFrame(self.frame, text="爬取模式", padding="10")
        mode_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        self.crawl_mode = tk.StringVar(value="single")
        
        ttk.Radiobutton(
            mode_frame,
            text="爬取单个政策（测试）",
            variable=self.crawl_mode,
            value="single",
            command=self._on_mode_change
        ).grid(row=0, column=0, sticky="w", padx=5)
        
        ttk.Radiobutton(
            mode_frame,
            text="批量爬取所有政策",
            variable=self.crawl_mode,
            value="batch",
            command=self._on_mode_change
        ).grid(row=0, column=1, sticky="w", padx=5)
        
        # 政策类型选择
        type_frame = ttk.LabelFrame(self.frame, text="政策类型", padding="10")
        type_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        self.type_vars = {
            1: tk.BooleanVar(value=True),
            2: tk.BooleanVar(value=True),
            3: tk.BooleanVar(value=True)
        }
        
        ttk.Checkbutton(
            type_frame,
            text="地方性法规",
            variable=self.type_vars[1]
        ).grid(row=0, column=0, sticky="w", padx=5)
        
        ttk.Checkbutton(
            type_frame,
            text="政府规章",
            variable=self.type_vars[2]
        ).grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Checkbutton(
            type_frame,
            text="规范性文件",
            variable=self.type_vars[3]
        ).grid(row=0, column=2, sticky="w", padx=5)
        
        # 输出设置（优化输入框宽度：50字符）
        output_frame = ttk.LabelFrame(self.frame, text="输出设置", padding="10")
        output_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        ttk.Label(output_frame, text="输出目录:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        
        self.output_dir = tk.StringVar(value=self.config.get("output_dir", "crawled_data"))
        
        ttk.Entry(
            output_frame,
            textvariable=self.output_dir,
            width=50
        ).grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        
        ttk.Button(
            output_frame,
            text="浏览...",
            command=self._browse_output_dir,
            width=12
        ).grid(row=0, column=2, padx=(6, 0), pady=6)
        
        output_frame.columnconfigure(1, weight=1)
        
        # 文件下载选项
        download_frame = ttk.LabelFrame(self.frame, text="文件下载选项", padding="10")
        download_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        self.download_docx = tk.BooleanVar(value=self.config.get("download_docx", True))
        self.download_doc = tk.BooleanVar(value=self.config.get("download_doc", True))
        self.download_pdf = tk.BooleanVar(value=self.config.get("download_pdf", False))
        self.download_all_files = tk.BooleanVar(value=self.config.get("download_all_files", False))
        
        self.download_docx_check = ttk.Checkbutton(
            download_frame,
            text="下载DOCX文件",
            variable=self.download_docx,
            command=self._on_download_option_change
        )
        self.download_docx_check.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.download_doc_check = ttk.Checkbutton(
            download_frame,
            text="下载DOC文件",
            variable=self.download_doc,
            command=self._on_download_option_change
        )
        self.download_doc_check.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        self.download_pdf_check = ttk.Checkbutton(
            download_frame,
            text="下载PDF文件",
            variable=self.download_pdf,
            command=self._on_download_option_change
        )
        self.download_pdf_check.grid(row=0, column=2, sticky="w", padx=5, pady=2)
        
        self.download_all_files_check = ttk.Checkbutton(
            download_frame,
            text="下载所有形式的附件",
            variable=self.download_all_files,
            command=self._on_download_all_change
        )
        self.download_all_files_check.grid(row=1, column=0, columnspan=3, sticky="w", padx=5, pady=(8, 2))
        
        # 初始化时检查状态，如果启用了"下载所有文件"，禁用其他选项
        if self.download_all_files.get():
            self._on_download_all_change()
        
        # 代理设置（优化输入框宽度：50字符）
        proxy_frame = ttk.LabelFrame(self.frame, text="代理设置（可选）", padding="10")
        proxy_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        self.use_proxy = tk.BooleanVar(value=self.config.get("use_proxy", False))
        
        ttk.Checkbutton(
            proxy_frame,
            text="启用代理IP（快代理）",
            variable=self.use_proxy,
            command=self._on_proxy_toggle
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Secret ID（统一间距：标签-输入框间距6px）
        ttk.Label(proxy_frame, text="Secret ID:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        
        kuaidaili_key = self.config.get("kuaidaili_api_key", "")
        secret_id = ""
        secret_key = ""
        if kuaidaili_key and ":" in kuaidaili_key:
            parts = kuaidaili_key.split(":", 1)
            secret_id = parts[0] if len(parts) > 0 else ""
            secret_key = parts[1] if len(parts) > 1 else ""
        
        self.kuaidaili_secret_id = tk.StringVar(value=secret_id)
        
        self.secret_id_entry = ttk.Entry(
            proxy_frame,
            textvariable=self.kuaidaili_secret_id,
            width=50
        )
        self.secret_id_entry.grid(row=1, column=1, sticky="ew", padx=6, pady=4)
        self.secret_id_entry.config(state="disabled" if not self.use_proxy.get() else "normal")
        
        # Secret Key
        ttk.Label(proxy_frame, text="Secret Key:").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        
        self.kuaidaili_secret_key = tk.StringVar(value=secret_key)
        
        self.secret_key_entry = ttk.Entry(
            proxy_frame,
            textvariable=self.kuaidaili_secret_key,
            width=50,
            show="*"
        )
        self.secret_key_entry.grid(row=2, column=1, sticky="ew", padx=6, pady=4)
        self.secret_key_entry.config(state="disabled" if not self.use_proxy.get() else "normal")
        
        proxy_frame.columnconfigure(1, weight=1)
        
        # 按钮区域
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        # 按钮（统一宽度：14字符，统一间距：12px）
        self.start_button = ttk.Button(
            button_frame,
            text="开始爬取",
            command=self._on_start,
            width=14
        )
        self.start_button.grid(row=0, column=0, padx=(0, 12))
        
        self.stop_button = ttk.Button(
            button_frame,
            text="停止爬取",
            command=self._on_stop,
            width=14,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=0)
        
        # 配置网格权重
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
    
    def _on_mode_change(self):
        """爬取模式改变事件"""
        mode = self.crawl_mode.get()
        if mode == "single":
            # 单个模式：只选择一个类型
            selected_count = sum(1 for var in self.type_vars.values() if var.get())
            if selected_count != 1:
                # 重置为只选择第一个
                self.type_vars[1].set(True)
                self.type_vars[2].set(False)
                self.type_vars[3].set(False)
    
    def _on_proxy_toggle(self):
        """代理开关切换事件"""
        if self.use_proxy.get():
            self.secret_id_entry.config(state="normal")
            self.secret_key_entry.config(state="normal")
        else:
            self.secret_id_entry.config(state="disabled")
            self.secret_key_entry.config(state="disabled")
    
    def _on_download_all_change(self):
        """下载所有文件选项改变事件"""
        if self.download_all_files.get():
            # 如果选择了"下载所有文件"，禁用其他选项
            self.download_docx_check.config(state="disabled")
            self.download_doc_check.config(state="disabled")
            self.download_pdf_check.config(state="disabled")
        else:
            # 如果取消选择，启用其他选项
            self.download_docx_check.config(state="normal")
            self.download_doc_check.config(state="normal")
            self.download_pdf_check.config(state="normal")
    
    def _on_download_option_change(self):
        """文件类型选项改变事件"""
        # 如果选择了任何特定文件类型，取消"下载所有文件"选项
        if self.download_docx.get() or self.download_doc.get() or self.download_pdf.get():
            if self.download_all_files.get():
                self.download_all_files.set(False)
                self._on_download_all_change()
    
    def _browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=self.output_dir.get()
        )
        if directory:
            self.output_dir.set(directory)
    
    def _on_start(self):
        """开始爬取按钮点击事件"""
        # 获取选择的类型
        selected_types = [t for t, var in self.type_vars.items() if var.get()]
        
        if not selected_types:
            tk.messagebox.showwarning("警告", "请至少选择一种政策类型")
            return
        
        # 准备参数
        crawl_type = self.crawl_mode.get()
        
        # 组合快代理的ID和Key
        kuaidaili_api_key = ""
        if self.use_proxy.get():
            secret_id = self.kuaidaili_secret_id.get().strip()
            secret_key = self.kuaidaili_secret_key.get().strip()
            if secret_id and secret_key:
                kuaidaili_api_key = f"{secret_id}:{secret_key}"
        
        kwargs = {
            "output_dir": self.output_dir.get(),
            "law_rule_types": selected_types,
            "download_docx": self.download_docx.get(),
            "download_doc": self.download_doc.get(),
            "download_pdf": self.download_pdf.get(),
            "download_all_files": self.download_all_files.get(),
            "use_proxy": self.use_proxy.get(),
            "kuaidaili_api_key": kuaidaili_api_key
        }
        
        # 禁用开始按钮，启用停止按钮
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # 调用回调
        self.start_callback(crawl_type, **kwargs)
    
    def _on_stop(self):
        """停止爬取按钮点击事件"""
        self.stop_callback()
        
        # 恢复按钮状态
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

