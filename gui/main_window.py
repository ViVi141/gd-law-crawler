"""
主窗口模块
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import threading
from typing import Optional

from core import Config, PolicyCrawler, CrawlProgress
from .crawl_tab import CrawlTab
from .progress_tab import ProgressTab
from .settings_tab import SettingsTab


class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        self.root = tk.Tk()
        self.root.title("GD Law Crawler (广东省法规爬虫工具) v1.0")
        
        # 加载配置
        self.config = Config()
        
        # 设置窗口大小和位置（基于黄金比例和常见分辨率优化）
        # 默认尺寸：1200x1000 (1.2:1，增加高度确保设置选项卡按钮可见)
        window_width = self.config.get("window_width", 1200)
        window_height = self.config.get("window_height", 1000)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 确保窗口不超过屏幕的80%
        max_width = int(screen_width * 0.8)
        max_height = int(screen_height * 0.8)
        window_width = min(window_width, max_width)
        window_height = min(window_height, max_height)
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置最小尺寸（保持比例，增加高度确保按钮可见）
        self.root.minsize(960, 800)
        
        # 设置系统内置字体（Windows）
        if sys.platform == 'win32':
            default_font = ("Microsoft YaHei UI", 10)
            self.root.option_add("*Font", default_font)
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 爬虫实例
        self.crawler: Optional[PolicyCrawler] = None
        self.crawl_thread: Optional[threading.Thread] = None
        self.is_crawling = False
        
        # 创建界面
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 创建主框架（统一间距：12px）
        main_frame = ttk.Frame(self.root, padding="12")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 配置网格权重（优化比例：选项卡区域占75%，日志区域占25%）
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=3)  # 选项卡区域（75%）
        main_frame.rowconfigure(1, weight=1)  # 日志区域（25%）
        main_frame.columnconfigure(0, weight=1)
        
        # 创建顶部选项卡区域（统一间距：8px）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # 创建各个选项卡
        self.crawl_tab = CrawlTab(self.notebook, self.config, self._on_start_crawl, self._on_stop_crawl)
        self.progress_tab = ProgressTab(self.notebook, self.config)
        self.settings_tab = SettingsTab(self.notebook, self.config)
        
        self.notebook.add(self.crawl_tab.frame, text="  爬取配置  ")
        self.notebook.add(self.progress_tab.frame, text="  爬取进度  ")
        self.notebook.add(self.settings_tab.frame, text="  设置  ")
        
        # 创建底部日志区域（统一间距：8px）
        log_frame = ttk.LabelFrame(main_frame, text="日志输出", padding="8")
        log_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=(8, 0))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            wrap=tk.WORD,
            font=("Consolas", 9) if sys.platform == 'win32' else ("Courier", 9),
            bg="#f8f8f8",
            relief=tk.FLAT,
            borderwidth=1
        )
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # 添加清空日志按钮（统一按钮宽度：12字符）
        clear_button = ttk.Button(log_frame, text="清空日志", command=self._clear_log, width=12)
        clear_button.grid(row=1, column=0, sticky="e", padx=4, pady=4)
        
        # 重定向标准输出到日志窗口
        sys.stdout = TextRedirector(self.log_text, sys.__stdout__)
        
        print("欢迎使用 GD Law Crawler (广东省法规爬虫工具) v1.0")
        print("请在\"爬取配置\"选项卡中设置参数，然后点击\"开始爬取\"按钮")
    
    def _on_start_crawl(self, crawl_type: str, **kwargs):
        """开始爬取回调
        
        Args:
            crawl_type: 爬取类型 ('single' 或 'batch')
            **kwargs: 爬取参数
        """
        if self.is_crawling:
            messagebox.showwarning("警告", "爬取任务正在进行中，请等待完成")
            return
        
        # 切换到进度选项卡
        self.notebook.select(1)
        
        # 应用配置
        for key, value in kwargs.items():
            if value is not None:
                self.config.set(key, value)
        
        # 创建爬虫实例
        self.crawler = PolicyCrawler(self.config, progress_callback=self._update_progress)
        
        # 在新线程中运行爬取任务
        self.is_crawling = True
        self.crawl_thread = threading.Thread(
            target=self._run_crawl,
            args=(crawl_type,),
            daemon=True
        )
        self.crawl_thread.start()
    
    def _run_crawl(self, crawl_type: str):
        """运行爬取任务（在后台线程中执行）
        
        Args:
            crawl_type: 爬取类型
        """
        try:
            if crawl_type == 'single':
                # 爬取单个政策（只搜索第一页）
                law_rule_type = self.config.get("law_rule_types", [1])[0]
                
                print("\n[测试模式] 获取第一页政策列表...")
                result = self.crawler.api_client.search_policies(law_rule_type, page_num=1, page_size=20)
                
                if result and result.get('data', {}).get('rows'):
                    # 转换为Policy对象
                    from core import Policy
                    rows = result['data']['rows']
                    policies = [Policy.from_dict(row) for row in rows]
                    
                    print(f"获取到 {len(policies)} 条政策")
                    
                    policy = policies[0]
                    print(f"\n选择政策: {policy.title}")
                    success = self.crawler.crawl_single_policy(policy)
                    
                    if success:
                        self._show_completion("爬取完成", "单个政策爬取成功！")
                    else:
                        self._show_error("爬取失败", "政策爬取失败，请查看日志")
                else:
                    self._show_error("未找到政策", "没有找到符合条件的政策")
            
            elif crawl_type == 'batch':
                # 批量爬取
                law_rule_types = self.config.get("law_rule_types", [1, 2, 3])
                self.crawler.crawl_batch(law_rule_types)
                self._show_completion("爬取完成", f"批量爬取完成！\n成功: {self.crawler.progress.completed_count}\n失败: {self.crawler.progress.failed_count}")
        
        except Exception as e:
            self._show_error("错误", f"爬取过程中发生错误:\n{str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.is_crawling = False
            if self.crawler:
                self.crawler.close()
    
    def _on_stop_crawl(self):
        """停止爬取回调"""
        if not self.is_crawling:
            messagebox.showinfo("提示", "当前没有正在进行的爬取任务")
            return
        
        confirm = messagebox.askyesno("确认", "确定要停止当前爬取任务吗？")
        if confirm:
            self.is_crawling = False
            print("\n用户请求停止爬取任务...")
            
            # 通知爬虫停止
            if self.crawler:
                self.crawler.request_stop()
            
            messagebox.showinfo("提示", "已发送停止信号，等待任务结束...")
    
    def _update_progress(self, progress: CrawlProgress):
        """更新进度（从后台线程调用）
        
        Args:
            progress: 进度对象
        """
        # 使用after方法在主线程中更新UI
        self.root.after(0, self.progress_tab.update_progress, progress)
    
    def _show_completion(self, title: str, message: str):
        """显示完成消息（线程安全）"""
        self.root.after(0, messagebox.showinfo, title, message)
    
    def _show_error(self, title: str, message: str):
        """显示错误消息（线程安全）"""
        self.root.after(0, messagebox.showerror, title, message)
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        print("日志已清空")
    
    def _on_closing(self):
        """窗口关闭事件"""
        if self.is_crawling:
            confirm = messagebox.askyesno(
                "确认退出",
                "爬取任务正在进行中，确定要退出吗？"
            )
            if not confirm:
                return
        
        # 恢复标准输出
        sys.stdout = sys.__stdout__
        
        # 关闭爬虫
        if self.crawler:
            self.crawler.close()
        
        # 销毁窗口
        self.root.destroy()
    
    def run(self):
        """运行主窗口"""
        self.root.mainloop()


class TextRedirector:
    """文本重定向器 - 将print输出重定向到Text widget"""
    
    def __init__(self, text_widget, original_stdout):
        """初始化
        
        Args:
            text_widget: Text widget
            original_stdout: 原始标准输出
        """
        self.text_widget = text_widget
        self.original_stdout = original_stdout
    
    def write(self, text):
        """写入文本"""
        # 同时输出到Text widget和原始stdout
        if text.strip():
            self.text_widget.insert(tk.END, text)
            self.text_widget.see(tk.END)
            self.text_widget.update_idletasks()
        
        # 同时输出到控制台（方便调试）
        self.original_stdout.write(text)
        self.original_stdout.flush()
    
    def flush(self):
        """刷新"""
        self.original_stdout.flush()

