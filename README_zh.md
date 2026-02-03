# aichat2md

将 AI 聊天对话转换为结构化 Markdown 文档。

## 特性

- 🌐 **从 URL 提取** - 支持 ChatGPT、Gemini、豆包分享链接（通过 Playwright 渲染 JS）
- 📄 **从 webarchive 提取** - Safari .webarchive 文件（离线模式）
- 🤖 **多 AI 后端** - DeepSeek、OpenAI、Groq 或任何兼容 OpenAI 的 API
- 🌍 **双语支持** - 英文/中文提示词
- 📝 **清晰输出** - 知识文档格式，非聊天记录
- ⚡ **简单 CLI** - pip 安装，一次配置

## 快速开始

```bash
# 安装
pip install aichat2md

# 配置（首次使用）
aichat2md --setup

# 转换 ChatGPT 分享链接
aichat2md https://chatgpt.com/share/xxx

# 转换 webarchive 文件
aichat2md ~/Downloads/chat.webarchive
```

## 支持的平台

- **ChatGPT** - chatgpt.com 分享链接
- **Gemini** - gemini.google.com 或 g.co 分享链接
- **豆包** - doubao.com 分享链接
- **Webarchive** - Safari 导出的 .webarchive 文件（支持所有平台）

### 使用示例

```bash
# ChatGPT
aichat2md https://chatgpt.com/share/xxx

# Gemini（支持长短链接）
aichat2md https://gemini.google.com/share/xxx
aichat2md https://g.co/gemini/share/xxx

# 豆包
aichat2md https://www.doubao.com/thread/xxx

# Webarchive 文件
aichat2md ~/Downloads/conversation.webarchive
```

## 支持的 AI 后端

- **DeepSeek**（默认）- 性价比高，国内服务
- **OpenAI** - GPT-4o-mini、GPT-4
- **Groq** - 快速推理的 Llama 模型
- **自定义** - 任何兼容 OpenAI 的 API

## 安装

### 前置要求

- Python 3.8 或更高版本
- Playwright（自动安装，但需要手动安装浏览器）

### 从 PyPI 安装

```bash
pip install aichat2md
```

### 安装 Playwright 浏览器

```bash
playwright install chromium
```

### 首次配置

```bash
aichat2md --setup
```

你将被提示：
1. 选择 AI 提供商（DeepSeek、OpenAI、Groq 或自定义）
2. 输入 API 密钥
3. 选择提示词语言（英文或中文）
4. 设置输出目录（默认：~/Downloads）

## 使用方法

### 基本用法

```bash
# 从 URL 转换（使用配置的输出目录）
aichat2md https://chatgpt.com/share/xxx

# 从 webarchive 转换（输出到输入文件同目录）
aichat2md ~/Downloads/chat.webarchive
```

### 覆盖语言

```bash
# 使用中文提示词（即使配置了英文）
aichat2md <url> --lang zh

# 使用英文提示词
aichat2md <url> --lang en
```

### 自定义输出路径

```bash
# 指定输出文件
aichat2md <url> -o ~/Documents/my-notes.md
aichat2md <url> --output ~/Documents/my-notes.md
```

### 覆盖模型

```bash
# 使用不同于配置的模型
aichat2md <url> --model gpt-4o
aichat2md <url> --model deepseek-chat
```

### 版本信息

```bash
aichat2md --version
```

## 配置

配置文件存储在 `~/.config/aichat2md/config.json`（跨平台）。

### 配置示例

```json
{
  "api_key": "sk-your-api-key",
  "api_base_url": "https://api.deepseek.com",
  "model": "deepseek-chat",
  "language": "zh",
  "output_dir": "/Users/you/Downloads",
  "max_tokens": 4000,
  "temperature": 0.7
}
```

### 重新配置

```bash
aichat2md --setup
```

## 输出格式

工具将聊天对话转换为结构化 Markdown，包括：

- **元信息** - 标签、日期、来源
- **摘要** - 2-3 句话概述
- **关键主题** - 要点列表
- **知识章节** - 重组后的内容，带逻辑标题
- **代码示例** - 提取的代码块及注释

### 输出示例

```markdown
---
技术标签: [Python, API, Web]
日期: 2026-02-02
来源: https://chatgpt.com/share/xxx
---

# 使用 FastAPI 构建 REST API

## 摘要
本文档介绍如何使用 FastAPI 构建生产级 REST API...

## 关键主题
- API 设计模式
- 请求验证
- 错误处理

## API 设计原则
...

## 代码示例
\```python
from fastapi import FastAPI
app = FastAPI()
...
\```
```

## 工作原理

1. **提取** - Playwright（URL）或 plistlib（webarchive）提取原始文本
2. **结构化** - AI API 重组为知识文档
3. **保存** - 自动生成文件名或指定路径

### 为什么分两阶段处理？

- **阶段 1（提取）** - 不使用 AI token，仅 HTML 解析
- **阶段 2（结构化）** - AI 高效组织内容

这节省成本并允许本地缓存提取内容。

## 开发

### 本地安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/aichat2md.git
cd aichat2md

# 可编辑模式安装
pip install -e .

# 安装 Playwright
playwright install chromium
```

### 运行测试

```bash
pip install pytest
pytest tests/
```

### 构建包

```bash
pip install build
python -m build
```

## 故障排除

### "Configuration file not found"

运行 `aichat2md --setup` 创建配置文件。

### "API authentication failed"

检查 `~/.config/aichat2md/config.json` 中的 API 密钥。

### Playwright 错误

安装浏览器：`playwright install chromium`

### 输出为空

对话可能太短或 AI 响应失败。检查错误消息。

## 贡献

欢迎贡献！请：

1. Fork 仓库
2. 创建功能分支
3. 为新功能添加测试
4. 提交 pull request

## 许可证

MIT 许可证 - 见 [LICENSE](LICENSE) 文件。

## 链接

- [GitHub 仓库](https://github.com/yourusername/aichat2md)
- [问题跟踪](https://github.com/yourusername/aichat2md/issues)
- [English Documentation](README.md)

## 致谢

- [Playwright](https://playwright.dev/) - Web 自动化
- [DeepSeek](https://www.deepseek.com/) - 性价比高的 AI API
- [OpenAI](https://openai.com/) - API 兼容标准
