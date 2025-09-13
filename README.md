# Fast Agent

一个基于 SmolagAgents 框架的快速 AI 智能体验证平台，提供直观的 Web 界面和可扩展的工具系统。

## 🚀 特性

- **🤖 智能对话**: 基于 OpenAI GPT-4o 模型的多步推理智能体
- **🛠️ 工具系统**: 可扩展的工具框架，支持自定义工具开发
- **💻 Web 界面**: 基于 Gradio 的现代化聊天界面
- **📁 文件上传**: 支持 PDF、DOCX、TXT 文件上传和处理
- **🔄 流式输出**: 实时显示 AI 思考和执行过程
- **📊 执行日志**: 详细的步骤追踪和性能统计
- **🎨 美观界面**: 响应式设计，支持 LaTeX 数学公式渲染

## 📦 安装

### 环境要求

- Python 3.8+
- OpenAI API 密钥

### 快速开始

1. **克隆仓库**
   ```bash
   git clone https://github.com/your-username/fast-agent.git
   cd fast-agent
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
   
   或手动安装：
   ```bash
   pip install smolagents gradio python-dotenv openai
   ```

3. **配置环境变量**
   
   创建 `.env` 文件：
   ```bash
   # OpenAI 配置
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_BASE_URL=https://api.openai.com/v1  # 可选，默认为 OpenAI 官方 API
   ```

4. **启动应用**
   ```bash
   cd fast_agent
   python main.py
   ```

5. **访问界面**
   
   启动后会自动打开浏览器，或访问控制台显示的 URL（通常是 `http://localhost:7860`）

## 🎯 使用方法

### 基本对话

在 Web 界面中直接输入问题，AI 智能体会：
1. 分析问题
2. 制定执行计划
3. 调用相应工具
4. 返回结果

### 文件处理

1. 点击"📎 Upload File"按钮
2. 选择支持的文件格式（PDF、DOCX、TXT）
3. 在对话中引用上传的文件内容

### 数学计算

内置数学工具，支持基本运算：
```
请帮我计算 25 + 37
```

## 🛠️ 工具开发

### 添加自定义工具

1. **创建工具文件**
   
   在 `fast_agent/tools/` 目录下创建新的工具文件，例如 `string_tools.py`：
   
   ```python
   from smolagents import tool
   
   @tool
   def reverse_string(text: str) -> str:
       """反转字符串
       Args:
           text: 要反转的字符串
       Returns:
           反转后的字符串
       """
       return text[::-1]
   ```

2. **注册工具**
   
   在 `fast_agent/tools/__init__.py` 中导入并添加到工具列表：
   
   ```python
   from .math_tools import add
   from .string_tools import reverse_string
   
   tools_list = [add, reverse_string]
   ```

### 工具开发规范

- 使用 `@tool` 装饰器
- 提供清晰的文档字符串
- 指定参数和返回值类型
- 处理异常情况

## 🏗️ 项目结构

```
fast-agent/
├── fast_agent/
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── ui.py               # Gradio 界面实现
│   └── tools/              # 工具模块
│       ├── __init__.py     # 工具注册
│       └── math_tools.py   # 数学工具
├── requirements.txt         # Python 依赖
├── README.md
├── LICENSE
└── .gitignore
```

## ⚙️ 配置选项

### 智能体配置

在 `main.py` 中可以调整以下参数：

```python
# 最大执行步数
agent.max_steps = 10

# 模型配置
model = OpenAIServerModel(
    model_id="gpt-4o",  # 可选: gpt-3.5-turbo, gpt-4, etc.
    api_key=os.environ.get("OPENAI_API_KEY"),
    api_base=os.environ.get("OPENAI_BASE_URL")
)

# 界面配置
GradioUI(
    agent, 
    reset_agent_memory=False,  # 是否在每次对话后重置记忆
    file_upload_folder="uploads"  # 文件上传目录
).launch(share=True)  # share=True 创建公共链接
```

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 必需 |
| `OPENAI_BASE_URL` | API 基础 URL | `https://api.openai.com/v1` |

## 🔧 高级功能

### 流式输出

智能体支持实时流式输出，用户可以看到：
- 思考过程
- 工具调用
- 执行日志
- 性能统计

### 记忆管理

- **会话记忆**: 在单次会话中保持上下文
- **重置选项**: 可配置是否在新对话时重置记忆
- **清除功能**: 界面提供清除对话历史按钮

### 文件处理

支持多种文件格式的智能处理：
- **PDF**: 文本提取和分析
- **DOCX**: Word 文档内容解析
- **TXT**: 纯文本文件处理

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [SmolagAgents](https://github.com/huggingface/smolagents) - 核心智能体框架
- [Gradio](https://gradio.app/) - Web 界面框架
- [OpenAI](https://openai.com/) - 语言模型支持

## 📞 支持

如有问题或建议，请：
- 提交 [Issue](https://github.com/your-username/fast-agent/issues)
- 发起 [Discussion](https://github.com/your-username/fast-agent/discussions)
- 联系维护者

---

**Fast Agent** - 让 AI 智能体开发更简单、更快速！ 🚀
