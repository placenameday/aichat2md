# ChatGPT 对话转 Markdown 工具设计方案

**设计日期**: 2024-02-02
**目标**: 创建标准化脚本工具，自动将 ChatGPT 分享链接转换为结构化 Markdown 文档

---

## 1. 核心目标

### 1.1 主要优势
- **减少 Token 浪费**: 通过预处理文本提取，只在结构化阶段使用 AI
- **标准化流程**: 固定的工具替代每次手动调用 AI
- **自动化程度高**: 一键输入 URL 或文件，自动输出 Markdown

### 1.2 使用场景
- 专门处理 ChatGPT 分享链接（`chatgpt.com/share/` 格式）
- 提取对话内容并重组为知识文档
- 支持 URL 和 Safari webarchive 两种输入

---

## 2. 技术架构

### 2.1 项目结构
```
chatgpt2md/
├── chatgpt2md.py                    # 主脚本
├── config.json                      # 配置文件
├── extractors/
│   ├── playwright_extractor.py      # URL 提取器（无需 AI）
│   └── webarchive_extractor.py      # .webarchive 提取器
├── structurizer.py                  # AI 结构化模块
├── prompt_template.py               # DeepSeek 提示词
├── requirements.txt                 # 依赖列表
└── output/                          # 输出目录（可配置）
```

### 2.2 核心依赖
```txt
playwright>=1.40.0    # 浏览器自动化，渲染 JS
requests>=2.31.0      # HTTP 请求，调用 DeepSeek API
```

### 2.3 工作流程
```
输入: URL 或 .webarchive
  ↓
[阶段 1: 文本提取 - 无 AI]
  ├─ URL → Playwright 渲染 → 纯文本
  └─ webarchive → plistlib 解析 → 纯文本
  ↓
[阶段 2: AI 结构化 - DeepSeek API]
  提取文本 → DeepSeek API → 结构化 Markdown
  ↓
输出: Markdown 文档
```

---

## 3. 文本提取实现

### 3.1 Playwright 提取器
**功能**: 从 ChatGPT 分享 URL 提取对话文本

**实现要点**:
```python
def extract_from_url(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until='networkidle')

        # 等待对话加载完成
        page.wait_for_selector('[data-testid*="conversation"]')

        # 提取纯文本
        content = page.inner_text('body')
        browser.close()

        return content
```

**关键点**:
- 等待 JS 渲染完成（`networkidle`）
- 提取纯文本而非 HTML，减少噪音
- 无需 MCP，使用原生 Playwright Python 库

### 3.2 Webarchive 提取器
**功能**: 从 Safari 保存的 .webarchive 文件提取内容

**实现要点**:
```python
def extract_from_webarchive(filepath: str) -> str:
    import plistlib
    from html.parser import HTMLParser

    with open(filepath, 'rb') as f:
        plist = plistlib.load(f)

    html_data = plist['WebMainResource']['WebResourceData']
    html = html_data.decode('utf-8')

    # HTMLParser 清洗 HTML → 纯文本
    parser = CleanHTMLParser()
    parser.feed(html)

    return parser.get_text()
```

**关键点**:
- 使用 Python 标准库 `plistlib`
- 去除 `<script>` 和 `<style>` 标签
- 返回纯文本格式

---

## 4. AI 结构化模块

### 4.1 DeepSeek API 调用
**优先使用 DeepSeek**: 性价比极高，质量可靠

```python
def structurize_content(raw_text: str, config: dict) -> str:
    response = requests.post(
        'https://api.deepseek.com/v1/chat/completions',
        headers={'Authorization': f'Bearer {config["deepseek_api_key"]}'},
        json={
            'model': config['model'],
            'messages': [
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': raw_text}
            ],
            'max_tokens': config['max_tokens'],
            'temperature': config['temperature']
        }
    )

    return response.json()['choices'][0]['message']['content']
```

### 4.2 提示词设计
```python
SYSTEM_PROMPT = """你是一个专业的知识文档编辑器。

输入：ChatGPT 对话的原始文本
输出：结构化的 Markdown 文档

要求：
1. 识别对话主题，生成简洁的文档标题
2. 提取技术标签（如 [Python, API, Web]）
3. 写一段摘要（2-3 句话概括核心内容）
4. 将对话重组为知识章节，使用合理的标题层级
5. 过滤无用的对话废话（"好的"、"让我想想"等）
6. 提取代码块单独呈现
7. 不要保留对话轮次格式（User/Assistant）

输出格式：
---
技术标签: [标签1, 标签2]
日期: 2024-02-02
来源: https://chatgpt.com/share/xxx
---

# 文档标题

## 摘要
[2-3 句话概括核心内容]

## 关键主题
- 主题 1
- 主题 2

## [知识点章节标题 1]
[重组后的说明性内容，非对话格式]

## [知识点章节标题 2]
...

## 代码示例
```python
# 提取的完整代码
```
"""
```

**关键设计**:
- **不保留对话格式**: 重组为连贯知识文档
- **自动识别主题**: AI 生成合理的章节结构
- **过滤废话**: 去除"好的"、"谢谢"等对话冗余
- **代码单独提取**: 便于复用

### 4.3 文本处理策略
- **直接全文发送**: 对话废话占用 token 极少，无需预清洗
- **无分块处理**: 假设单次对话不会超限，遇到超长时再处理
- **简单可靠**: 避免过早优化

---

## 5. 配置和输出

### 5.1 配置文件（config.json）
```json
{
  "deepseek_api_key": "sk-xxx",
  "output_dir": "~/Downloads",
  "model": "deepseek-chat",
  "max_tokens": 4000,
  "temperature": 0.7
}
```

**配置说明**:
- `deepseek_api_key`: DeepSeek API 密钥（必填）
- `output_dir`: URL 输入时的输出目录（默认系统下载目录）
- `model`: DeepSeek 模型名称
- `max_tokens`: 最大生成长度
- `temperature`: 生成随机性（0.7 平衡创造性和准确性）

**初始化**: 运行 `--setup` 自动生成配置文件

### 5.2 输出路径规则
| 输入类型 | 输出位置 | 示例 |
|---------|---------|------|
| .webarchive 文件 | 文件所在目录 | `~/Downloads/chat.webarchive` → `~/Downloads/chat.md` |
| URL | `config.json` 中的 `output_dir` | `https://...` → `~/Downloads/2024-02-02-标题.md` |

### 5.3 文件命名规则
- **webarchive 输入**: 保持原文件名，改扩展名 `.md`
- **URL 输入**: `日期-AI生成的标题.md`
  - 日期格式: `YYYY-MM-DD`
  - 标题自动截断到 50 字符
  - 非法字符替换为 `-`

---

## 6. 主脚本逻辑

### 6.1 命令行接口
```python
def main():
    parser = argparse.ArgumentParser(description='ChatGPT 对话转 Markdown')
    parser.add_argument('input', nargs='?', help='URL 或 .webarchive 文件路径')
    parser.add_argument('--setup', action='store_true', help='初始化配置')
    args = parser.parse_args()

    # 初始化配置
    if args.setup:
        setup_config()
        return

    # 加载配置
    config = load_config()

    # 判断输入类型并提取
    if args.input.startswith('http'):
        text = extract_from_url(args.input)
        output_path = Path(config['output_dir']) / generate_filename()
    else:
        text = extract_from_webarchive(args.input)
        output_path = Path(args.input).with_suffix('.md')

    # AI 结构化
    markdown = structurize_content(text, config)

    # 保存文件
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding='utf-8')
    print(f'✓ 已保存到: {output_path}')
```

### 6.2 执行流程
1. 解析命令行参数
2. 检查配置文件存在性
3. 自动识别输入类型（URL vs 文件）
4. 调用对应提取器
5. 调用 DeepSeek API 结构化
6. 保存到指定路径
7. 输出成功消息

---

## 7. 错误处理

### 7.1 异常场景和处理

| 异常类型 | 场景 | 处理方式 |
|---------|------|---------|
| 配置缺失 | `config.json` 不存在 | 提示运行 `--setup` |
| API key 空 | 未填写密钥 | 提示填写配置 |
| URL 无法访问 | 网络问题 | 提示检查网络或 URL |
| Playwright 超时 | 页面加载失败 | 提示页面加载超时 |
| webarchive 格式错误 | 文件损坏 | 提示文件损坏 |
| API 401 | API key 无效 | 提示重新配置 |
| API 超限 | Token 限制 | 提示对话过长 |
| 输出目录不存在 | 路径错误 | 自动创建目录 |
| 文件名冲突 | 重复文件名 | 添加序号后缀 |

### 7.2 实现示例
```python
try:
    # 核心逻辑
except PlaywrightTimeoutError:
    print("✗ 页面加载超时，请检查 URL")
    sys.exit(1)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("✗ API key 无效，请运行 --setup 重新配置")
    else:
        print(f"✗ API 调用失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ 未知错误: {e}")
    sys.exit(1)
```

---

## 8. 使用流程

### 8.1 首次安装
```bash
# 1. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 2. 初始化配置
python chatgpt2md.py --setup
# 输入 DeepSeek API key
# 自动生成 config.json
```

### 8.2 日常使用
```bash
# URL 方式（需联网）
python chatgpt2md.py https://chatgpt.com/share/xxx

# webarchive 方式（离线可用）
python chatgpt2md.py ~/Downloads/chat.webarchive
```

### 8.3 输出示例
```markdown
---
技术标签: [Python, Requests, API]
日期: 2024-02-02
来源: https://chatgpt.com/share/xxx
---

# Python Requests 库使用指南

## 摘要
介绍 Requests 库的安装、基础使用和异常处理最佳实践，适合 Python 开发者快速上手 HTTP 请求。

## 关键主题
- HTTP 请求方法（GET/POST）
- 异常处理策略
- 实际应用示例

## 安装和配置
通过 pip 安装：
```bash
pip install requests
```

基础导入：
```python
import requests
```

## 发送 HTTP 请求

### GET 请求
使用 `requests.get()` 方法获取数据...

### POST 请求
使用 `requests.post()` 发送表单或 JSON 数据...

## 异常处理
常见异常类型：
- `ConnectionError`: 网络连接失败
- `Timeout`: 请求超时
- `HTTPError`: HTTP 状态码错误

处理策略：
```python
try:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
```

## 代码示例
```python
import requests

def fetch_data(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# 使用示例
data = fetch_data('https://api.example.com/data')
print(data)
```
```

---

## 9. 设计优势总结

1. **Token 优化**: 文本提取阶段完全不使用 AI，只在结构化时调用
2. **简单可靠**: 单一脚本，配置简单，依赖少
3. **灵活输入**: 支持 URL 和 webarchive 两种方式
4. **智能输出**: AI 自动识别主题并生成合理结构
5. **跨平台**: Python 实现，支持 macOS/Windows/Linux
6. **可扩展**: 配置文件支持切换 AI 模型，预留接口

---

## 10. 后续扩展可能

- 支持批量处理（文件夹中多个 webarchive）
- 添加 GUI 界面
- 支持其他 AI 后端（Claude、GPT-4 等）
- 自定义输出模板
- 导出为 PDF/HTML 格式
