# GD Law Crawler (广东省法规爬虫工具) v1.1

> **GUI和命令行二合一**的现代化政策爬虫工具

**English**: GD Law Crawler | **中文**: 广东省法规爬虫工具

[![GitHub](https://img.shields.io/badge/GitHub-ViVi141-blue?style=flat-square&logo=github)](https://github.com/ViVi141)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-1.1.0-green?style=flat-square)](https://github.com/ViVi141/gd-law-crawler/releases)

**项目地址**: [https://github.com/ViVi141/gd-law-crawler](https://github.com/ViVi141/gd-law-crawler)

## ✨ 特性

- 🖥️ **双模式支持**：支持GUI图形界面和CLI命令行两种模式
- 🎯 **智能爬取**：自动识别并爬取地方性法规、政府规章、规范性文件
- 📄 **文档转换**：自动将DOCX/DOC/PDF转换为Markdown格式
- 🤖 **RAG知识库**：生成适合RAG系统的结构化Markdown文件
- 🛡️ **反爬虫对抗**：User-Agent轮换、会话管理、代理IP支持
- 💾 **多格式保存**：同时保存JSON、Markdown和原始文件
- 📊 **实时进度**：实时显示爬取进度和统计信息
- ⚙️ **灵活配置**：支持GUI设置和配置文件两种方式

## 📦 项目结构

```
gd-law-crawler/
├── core/                      # 核心业务逻辑
│   ├── __init__.py
│   ├── config.py             # 配置管理
│   ├── models.py             # 数据模型
│   ├── api_client.py         # API客户端
│   ├── converter.py          # 文档转换
│   └── crawler.py            # 爬虫核心
├── gui/                       # GUI界面
│   ├── __init__.py
│   ├── main_window.py        # 主窗口
│   ├── crawl_tab.py          # 爬取配置标签
│   ├── progress_tab.py       # 进度显示标签
│   └── settings_tab.py       # 设置标签
├── cli/                       # 命令行界面
│   ├── __init__.py
│   └── commands.py           # CLI命令
├── utils/                     # 工具函数
│   ├── __init__.py
│   ├── logger.py             # 日志管理
│   ├── file_handler.py       # 文件处理
│   └── validator.py          # 数据验证
├── main.py                    # 统一入口
├── config.json                # 配置文件（首次运行自动创建）
├── config.json.example        # 配置文件模板
├── requirements.txt           # 依赖清单
├── .gitignore                 # Git忽略文件
├── build_exe.py               # 打包脚本（GUI版本）
└── README.md                  # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置设置（可选）

首次运行程序会自动创建 `config.json` 配置文件。如果需要自定义配置，可以：

```bash
# 复制配置模板
cp config.json.example config.json

# 然后编辑 config.json 文件，设置你的参数
```

**注意**：`config.json` 文件可能包含敏感信息（如API密钥），已添加到 `.gitignore` 中，不会被提交到Git仓库。

### 3. 打包成exe（可选）

打包成Windows可执行文件。

**快速打包**：
```bash
python build_exe.py
```

### 4. 运行程序

#### GUI模式（图形界面）

```bash
python main.py
```

直接双击 `main.py` 也可以启动GUI模式。

#### CLI模式（命令行）

```bash
# 查看帮助
python main.py --help

# 爬取单个政策
python main.py crawl --type 1

# 批量爬取
python main.py batch --types 1,2,3

# 查看版本
python main.py version
```

## 📖 使用指南

### GUI模式

1. **启动程序**：运行 `python main.py`
2. **配置参数**：在"爬取配置"选项卡中设置参数
3. **开始爬取**：点击"开始爬取"按钮
4. **查看进度**：自动切换到"爬取进度"选项卡查看实时进度
5. **调整设置**：在"设置"选项卡中调整高级参数

#### 界面截图

![GD Law Crawler GUI](https://www.vivi141.com/upload/gd-law-crawler.png)

**主要功能**：
- 🎯 **爬取配置**：选择爬取模式（单个/批量）、政策类型、输出目录
- 📊 **爬取进度**：实时显示进度、统计信息、失败列表
- ⚙️ **设置**：配置请求参数、输出选项、日志级别
- 📝 **日志输出**：实时显示爬取日志，支持自动换行

### CLI模式

#### 命令列表

| 命令 | 说明 | 示例 |
|------|------|------|
| `crawl` | 爬取单个政策 | `python main.py crawl --type 1` |
| `batch` | 批量爬取 | `python main.py batch --types 1,2,3` |
| `config` | 配置管理 | `python main.py config --show` |
| `version` | 版本信息 | `python main.py version` |

#### crawl命令

```bash
# 爬取地方性法规（默认）
python main.py crawl

# 爬取政府规章
python main.py crawl --type 2

# 爬取规范性文件
python main.py crawl --type 3

# 指定输出目录
python main.py crawl --output my_data

# 使用代理
python main.py crawl --proxy --kuaidaili-key "key:secret"
```

#### batch命令

```bash
# 爬取所有类型（默认）
python main.py batch

# 只爬取地方性法规和政府规章
python main.py batch --types 1,2

# 限制数量（测试用）
python main.py batch --limit 10

# 使用代理批量爬取
python main.py batch --proxy --kuaidaili-key "key:secret"
```

#### config命令

```bash
# 查看当前配置
python main.py config --show

# 修改配置
python main.py config --set request_delay=3
python main.py config --set page_size=50

# 重置为默认配置
python main.py config --reset
```

## ⚙️ 配置说明

配置文件：`config.json`

### 核心配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `api_base_url` | API基础URL | `https://www.gdpc.gov.cn:443/bascdata` |
| `output_dir` | 输出目录 | `crawled_data` |
| `law_rule_types` | 政策类型列表 | `[1, 2, 3]` |

### 请求配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `request_delay` | 请求间隔（秒） | `2` |
| `retry_delay` | 重试延迟（秒） | `5` |
| `max_retries` | 最大重试次数 | `3` |
| `rate_limit_delay` | 限流延迟（秒） | `30` |
| `timeout` | 超时时间（秒） | `30` |

### 输出配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `save_json` | 保存JSON数据 | `true` |
| `save_markdown` | 保存Markdown | `true` |
| `save_files` | 保存附件文件 | `true` |
| `download_docx` | 下载DOCX | `true` |
| `download_doc` | 下载DOC | `true` |
| `download_pdf` | 下载PDF | `false` |

### 代理配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `use_proxy` | 启用代理 | `false` |
| `kuaidaili_api_key` | 快代理API密钥 | `""` |

## 📂 输出结构

```
crawled_data/
├── json/                          # JSON数据文件
│   ├── policy_{id}.json          # 基础数据
│   └── policy_{id}_complete.json # 完整数据
├── files/                         # 原始附件文件
│   └── {id}_{filename}.{ext}     # 下载的附件
└── markdown/                      # RAG格式Markdown
    └── {编号}_{政策名称}.md       # RAG知识库文件
```

### Markdown文件格式

```yaml
---
title: "政策标题"
policy_id: "政策ID"
law_rule_type: "1"
office: "制定机关"
pass_date: "2024-01-01"
effective_date: "2024-01-01"
keywords: ["关键词1", "关键词2"]
tags: ["标签1", "标签2"]
source_url: "https://..."
crawl_time: "2024-01-01 12:00:00"
---

# 政策标题

## 基本信息

- **制定机关**: ...
- **通过日期**: ...
- **时效性**: 有效
- **来源链接**: [查看原文](...)

## 关键词

关键词1, 关键词2, ...

## 正文内容

（文档转换后的内容）
```

## 🔧 高级功能

### 1. 代理IP支持

支持使用快代理SDK进行IP轮换：

```bash
# 安装快代理SDK
pip install kdl

# 使用代理
python main.py batch --proxy --kuaidaili-key "secret_id:secret_key"
```

### 2. 文档转换增强

支持多种文档格式转换：

- **DOCX**：使用 python-docx 直接转换
- **DOC**：尝试多种方案（LibreOffice、poword、antiword）
- **PDF**：使用 pypdf 提取文本（仅支持文本型PDF）

### 3. 自定义User-Agent

程序内置12种User-Agent，自动轮换：

- Chrome (Windows/macOS/Linux)
- Firefox (Windows/macOS)
- Edge (Windows)
- Safari (macOS)

### 4. 会话管理

每50个请求自动轮换会话，清除Cookie，避免被识别。

## 🐛 常见问题

### Q1: 启动GUI时报错 "GUI模块加载失败"

**A**: 确保安装了所有依赖：

```bash
pip install -r requirements.txt
```

tkinter是Python内置库，如果缺失需要重新安装Python（勾选tcl/tk组件）。

### Q2: DOC文件转换失败

**A**: DOC格式需要额外工具支持：

1. **推荐**：安装LibreOffice（https://www.libreoffice.org/）
2. **可选**：安装poword库（`pip install poword`）
3. **Linux**：安装antiword（`sudo apt install antiword`）

### Q3: 爬取时遇到限流（429错误）

**A**: 调整请求延迟或使用代理：

```bash
# 方法1：增加延迟
python main.py config --set request_delay=5

# 方法2：使用代理
python main.py batch --proxy --kuaidaili-key "your_key"
```

### Q4: PDF无法提取文本

**A**: 可能是扫描版PDF，需要OCR功能（暂未实现）。建议：

1. 访问来源链接在线查看
2. 使用专业OCR工具处理
3. 手动复制文本内容

### Q5: 如何只爬取特定政策？

**A**: 修改源码或使用API客户端：

```python
from core import Config, PolicyCrawler, Policy

config = Config()
crawler = PolicyCrawler(config)

# 手动创建Policy对象并爬取
policy = Policy(
    id="your-policy-id",
    title="政策标题",
    office="制定机关",
    pass_date="2024-01-01",
    law_rule_type=1
)

crawler.crawl_single_policy(policy)
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/ViVi141/gd-law-crawler.git
cd gd-law-crawler

# 安装依赖
pip install -r requirements.txt

# 运行测试
python main.py crawl --type 1
```

### 代码风格

- 遵循Google Python Style Guide
- 使用UTF-8编码
- 添加适当的类型注解
- 编写清晰的docstring

## 📄 许可证

本项目采用 **Apache License 2.0** 开源许可证。

**Apache License 2.0 特点**：

✅ **允许**：
- 商业使用
- 修改和分发
- 专利使用
- 私有使用
- 重新发布（需保留版权声明和许可证）

📋 **要求**：
- 必须保留版权声明
- 必须包含许可证文件
- 修改的文件必须注明变更
- 如果包含 NOTICE 文件，必须保留

**完整许可证条款**：请查看 [LICENSE](LICENSE) 文件

**许可证链接**：https://www.apache.org/licenses/LICENSE-2.0

## 👥 作者

**ViVi141**

- **GitHub**: [@ViVi141](https://github.com/ViVi141)
- **邮箱**: 747384120@qq.com

**项目名称**: gd-law-crawler  
**英文全称**: GD Law Crawler  
**中文名称**: 广东省法规爬虫工具

## 🙏 致谢
- 广东省人大常委会法工委（数据来源）
- [快代理](https://www.kuaidaili.com/)（代理IP服务）
- Python社区（优秀的开源库，如requests用于HTTP请求和会话管理、python-docx用于DOCX文档转换、tkinter用于GUI界面构建，以及众多其他开源贡献者提供的稳定工具和库，支持整个项目的开发和运行）

---

## 💝 赞助支持
如果您觉得这个项目对您有帮助，欢迎通过以下方式赞助，支持项目的持续开发和维护！

### 微信赞助
![微信收款二维码](https://www.vivi141.com/upload/mm_facetoface_collect_qrcode_1726138034524.png)

### 支付宝赞助
![支付宝收款二维码](https://www.vivi141.com/upload/1726138087557.jpg)

**感谢您的支持！** 您的赞助将用于服务器费用、工具订阅和项目优化。任何金额的赞助都将激励我提供更好的功能和文档。

---

## 📦 现成数据集
如果您需要现成的全量 Markdown 文件数据集（12,293 个文件，约 341 MB），可以访问我的私人店铺 [https://store.vivi141.com/](https://store.vivi141.com/) 购买，售价仅 5 元人民币。我为此数据集投入了约 80 元代理 IP 服务费用，以及 48 小时不间断采集时间，确保数据完整和最新。

## 未来计划 🚀

### v1.2 计划功能

#### 1. 多线程爬取与转换
- **爬取线程池**: 使用线程池并行爬取多个政策，显著提升爬取速度
- **转换线程池**: 将文档格式转换（DOCX/PDF → Markdown）与爬取分离，异步处理
- **智能队列管理**: 实现生产者-消费者模式，平衡爬取与转换速度
- **进度追踪**: 实时显示各线程工作状态

#### 2. 多IP代理池并行爬取
- **代理池管理**: 支持配置多个快代理API密钥或自定义代理列表
- **智能轮询**: 自动轮换多个IP地址，避免单IP限流
- **并发控制**: 每个IP独立线程，实现真正的并行爬取
- **健康检查**: 实时检测代理可用性，自动剔除失效代理
- **负载均衡**: 智能分配任务到不同IP，优化整体效率

#### 3. 性能优化
- **断点续爬**: 支持中断后从上次位置继续
- **增量更新**: 只爬取新增或更新的政策
- **缓存机制**: 缓存已爬取的列表数据，减少重复请求

#### 4. 功能增强
- **导出Excel**: 支持将政策信息导出为Excel表格
- **全文搜索**: 在已爬取的Markdown文件中进行全文搜索
- **定时任务**: 支持定时自动爬取，保持数据最新

### 贡献代码

欢迎提交 Pull Request 或提出 Issue！

---

## 版本历史 📋

### v1.1.0 (2025-11-21)
- ✨ 优化日志系统，使用标准logging模块
- ✨ GUI日志支持字符级自动换行
- ✨ 优化日志输出格式，清晰区分"获取列表"和"爬取详细内容"
- ✨ 实时用时显示，独立定时器自动更新
- ✨ 优化进度统计显示
- 🐛 修复批量爬取时进度更新问题
- 🐛 修复按钮状态管理问题

### v1.0.0 (2025-11-21)
- 🎉 首次发布
- ✨ GUI和命令行二合一
- ✨ 支持批量爬取和单个测试
- ✨ 自动转换DOCX/DOC/PDF为Markdown
- ✨ 生成RAG友好的格式
- ✨ 支持快代理SDK
- ✨ 完整的进度追踪和错误处理

---

**版本**: 1.1.0  
**最后更新**: 2025-11-21  
**项目主页**: https://github.com/ViVi141/gd-law-crawler  
**项目名称**: GD Law Crawler (gd-law-crawler)  
**作者**: ViVi141  
**联系方式**: 747384120@qq.com

**如有问题，欢迎提Issue或联系我们！** 📧

