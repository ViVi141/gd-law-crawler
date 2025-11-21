"""
爬取进度选项卡
"""

import tkinter as tk
from tkinter import ttk

from core import Config, CrawlProgress


class ProgressTab:
    """爬取进度选项卡"""
    
    def __init__(self, parent, config: Config):
        """初始化
        
        Args:
            parent: 父窗口
            config: 配置对象
        """
        self.config = config
        self.parent = parent
        self.current_progress = None  # 保存当前进度对象
        self.timer_id = None  # 定时器ID
        
        # 创建主框架（统一间距：12px）
        self.frame = ttk.Frame(parent, padding="12")
        
        # 创建界面
        self._create_widgets()
        
        # 初始化进度显示
        from core import CrawlProgress
        initial_progress = CrawlProgress()
        self.update_progress(initial_progress)
        
        # 启动定时器自动更新用时
        self._start_time_update_timer()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 总体进度（统一间距：组件间距8px，内部padding 10px）
        overall_frame = ttk.LabelFrame(self.frame, text="总体进度", padding="10")
        overall_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        overall_frame.columnconfigure(1, weight=1)
        
        # 进度条（统一间距：6px）
        ttk.Label(overall_frame, text="完成进度:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        
        self.progress_bar = ttk.Progressbar(
            overall_frame,
            mode="determinate",
            maximum=100,
            length=400
        )
        self.progress_bar.grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        
        self.progress_label = ttk.Label(overall_frame, text="0%", font=("", 10, "bold"), width=6)
        self.progress_label.grid(row=0, column=2, padx=6, pady=6)
        
        # 添加状态提示
        self.status_label = ttk.Label(
            overall_frame,
            text="等待开始爬取...",
            font=("", 9),
            foreground="gray"
        )
        self.status_label.grid(row=1, column=0, columnspan=3, sticky="w", padx=6, pady=(0, 0))
        
        # 统计信息
        stats_frame = ttk.LabelFrame(self.frame, text="统计信息", padding="10")
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        
        # 使用Grid布局统计信息
        row = 0
        
        # 总数
        ttk.Label(stats_frame, text="总数:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.total_label = ttk.Label(stats_frame, text="0", font=("", 10, "bold"))
        self.total_label.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        # 成功数
        ttk.Label(stats_frame, text="成功:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.success_label = ttk.Label(stats_frame, text="0", foreground="green", font=("", 10, "bold"))
        self.success_label.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        # 失败数
        ttk.Label(stats_frame, text="失败:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.failed_label = ttk.Label(stats_frame, text="0", foreground="red", font=("", 10, "bold"))
        self.failed_label.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        # 成功率
        ttk.Label(stats_frame, text="成功率:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.rate_label = ttk.Label(stats_frame, text="0.00%", font=("", 10, "bold"))
        self.rate_label.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        # 用时
        ttk.Label(stats_frame, text="用时:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.time_label = ttk.Label(stats_frame, text="0秒", font=("", 10))
        self.time_label.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        
        # 当前政策信息
        current_frame = ttk.LabelFrame(self.frame, text="当前政策", padding="10")
        current_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        current_frame.columnconfigure(1, weight=1)
        
        ttk.Label(current_frame, text="政策ID:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.current_id_label = ttk.Label(current_frame, text="-", font=("Consolas", 9))
        self.current_id_label.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        
        ttk.Label(current_frame, text="政策标题:").grid(row=1, column=0, sticky="nw", padx=6, pady=4)
        self.current_title_label = ttk.Label(current_frame, text="-", font=("", 9), wraplength=600, justify="left")
        self.current_title_label.grid(row=1, column=1, sticky="ew", padx=6, pady=4)
        
        # 失败列表（如果有）（优化表格列宽比例：基于内容重要性）
        failed_frame = ttk.LabelFrame(self.frame, text="失败政策列表", padding="10")
        failed_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 0))
        failed_frame.rowconfigure(0, weight=1)
        failed_frame.columnconfigure(0, weight=1)
        
        # 创建Treeview显示失败列表（优化行数：6行，减少高度）
        self.failed_tree = ttk.Treeview(
            failed_frame,
            columns=("id", "title", "reason"),
            show="headings",
            height=6
        )
        
        self.failed_tree.heading("id", text="政策ID")
        self.failed_tree.heading("title", text="政策标题")
        self.failed_tree.heading("reason", text="失败原因")
        
        # 优化列宽比例：ID占25%，标题占60%，原因占15%（基于内容重要性）
        self.failed_tree.column("id", width=220, minwidth=180, stretch=tk.NO)
        self.failed_tree.column("title", width=480, minwidth=300, stretch=tk.YES)
        self.failed_tree.column("reason", width=140, minwidth=120, stretch=tk.NO)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(failed_frame, orient="vertical", command=self.failed_tree.yview)
        self.failed_tree.configure(yscrollcommand=scrollbar.set)
        
        self.failed_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 配置网格权重
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(3, weight=1)
    
    def update_progress(self, progress: CrawlProgress):
        """更新进度显示
        
        Args:
            progress: 进度对象
        """
        # 更新进度条
        percentage = progress.progress_percentage
        self.progress_bar["value"] = percentage
        self.progress_label.config(text=f"{percentage:.1f}%")
        
        # 更新状态提示
        if progress.total_count == 0:
            self.status_label.config(text="等待开始爬取...", foreground="gray")
        elif progress.end_time is not None:
            self.status_label.config(text="爬取已完成", foreground="green")
        else:
            self.status_label.config(text="正在爬取中...", foreground="blue")
        
        # 更新统计信息
        self.total_label.config(text=str(progress.total_count))
        self.success_label.config(text=str(progress.completed_count))
        self.failed_label.config(text=str(progress.failed_count))
        self.rate_label.config(text=f"{progress.success_rate:.2f}%")
        
        # 保存当前进度对象（用于定时器自动更新用时）
        self.current_progress = progress
        
        # 更新用时（由定时器自动更新，这里不再更新）
        
        # 更新当前政策信息
        self.current_id_label.config(text=progress.current_policy_id or "-")
        self.current_title_label.config(text=progress.current_policy_title or "-")
        
        # 更新失败列表
        # 清空现有项
        for item in self.failed_tree.get_children():
            self.failed_tree.delete(item)
        
        # 如果有失败的政策，添加新项
        if progress.failed_policies:
            for failed in progress.failed_policies:
                self.failed_tree.insert("", "end", values=(
                    failed.get("id", ""),
                    failed.get("title", ""),
                    failed.get("reason", "")
                ))
        else:
            # 如果没有失败项，显示提示信息
            self.failed_tree.insert("", "end", values=("", "暂无失败记录", ""))
    
    def _start_time_update_timer(self):
        """启动定时器，每秒自动更新用时显示"""
        self._update_elapsed_time()
    
    def _update_elapsed_time(self):
        """定时更新用时显示"""
        if self.current_progress and self.current_progress.start_time is not None:
            elapsed_time = self.current_progress.elapsed_time
            if elapsed_time is not None:
                # 确保elapsed_time是非负数
                elapsed_time = max(0.0, elapsed_time)
                elapsed = int(elapsed_time)
                hours = elapsed // 3600
                minutes = (elapsed % 3600) // 60
                seconds = elapsed % 60
                
                if hours > 0:
                    time_str = f"{hours}小时{minutes}分{seconds}秒"
                elif minutes > 0:
                    time_str = f"{minutes}分{seconds}秒"
                else:
                    time_str = f"{seconds}秒"
                
                self.time_label.config(text=time_str)
            else:
                self.time_label.config(text="0秒")
        else:
            self.time_label.config(text="0秒")
        
        # 每1000毫秒（1秒）调用一次
        self.timer_id = self.frame.after(1000, self._update_elapsed_time)
    
    def stop_timer(self):
        """停止定时器"""
        if self.timer_id:
            self.frame.after_cancel(self.timer_id)
            self.timer_id = None

