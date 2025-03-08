# Claude MCP (模型上下文协议)

## 概述

Claude MCP (Model Context Protocol) 是一个统一的模型上下文交互协议，用于在AI模型和开发环境之间建立标准化的上下文交互。它允许AI模型更好地理解和处理代码、文档和其他资源，提供更智能的辅助功能。

本项目提供了两种MCP服务器实现：
1. 基于Anthropic Claude API的实现
2. 基于Azure OpenAI API的实现

## 核心特性

- **多模态理解**：能够处理和理解文本、图像、代码等多种输入形式
- **任务链处理**：可以执行一系列相互关联的任务，形成完整的工作流
- **上下文感知**：在整个对话过程中保持对上下文的理解
- **工具使用能力**：能够调用和使用各种工具来完成特定任务
- **代码理解与生成**：深入理解代码结构，并能生成高质量的代码

## 应用场景

MCP可应用于多种场景，包括但不限于：

1. **软件开发辅助**：代码审查、调试、重构和生成
2. **数据分析**：处理和分析各种数据集，生成见解
3. **内容创作**：协助创建文档、报告、教程等
4. **问题解决**：分析复杂问题并提供解决方案
5. **自动化工作流**：创建和执行自动化任务序列

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
# 对于Claude API
export ANTHROPIC_API_KEY=your_api_key_here

# 对于Azure OpenAI API
export AZURE_OPENAI_API_KEY=your_api_key_here
export AZURE_OPENAI_ENDPOINT=your_endpoint_here
export AZURE_OPENAI_DEPLOYMENT_ID=your_deployment_id_here  # 例如：gpt-4
```

## 使用指南

### 使用Claude API

```python
from test_mcp_server import MCPSession

# 初始化会话
session = MCPSession()

# 发送请求
response = session.send_request(
    prompt="分析这段代码并提出改进建议",
    attachments=["path/to/code.py"]
)

# 处理响应
print(response)
```

### 使用Azure OpenAI API

```python
from use_azure_open_api_key_build_mcp_server import AzureMCPSession

# 初始化会话
session = AzureMCPSession()

# 发送请求
response = session.send_request(
    prompt="分析这段代码并提出改进建议",
    attachments=["path/to/code.py"],
    deployment_id="gpt-4"  # 指定您的部署ID
)

# 处理响应
print(response)
```

### 多步骤任务链

```python
# 使用Claude API
from test_mcp_server import MCPSession

session = MCPSession()
responses = session.start_task_chain(
    initial_prompt="创建一个简单的网站",
    steps=[
        "设计网站结构",
        "创建HTML文件",
        "添加CSS样式",
        "实现JavaScript功能"
    ]
)

# 使用Azure OpenAI API
from use_azure_open_api_key_build_mcp_server import AzureMCPSession

session = AzureMCPSession()
responses = session.start_task_chain(
    initial_prompt="创建一个简单的网站",
    steps=[
        "设计网站结构",
        "创建HTML文件",
        "添加CSS样式",
        "实现JavaScript功能"
    ],
    deployment_id="gpt-4"
)
```

## 示例脚本

本项目包含两个示例脚本：

1. `test_mcp_server.py` - 使用Anthropic Claude API的MCP服务器实现
2. `use_azure_open_api_key_build_mcp_server.py` - 使用Azure OpenAI API的MCP服务器实现

运行示例：

```bash
# 运行Claude API示例
python test_mcp_server.py

# 运行Azure OpenAI API示例
python use_azure_open_api_key_build_mcp_server.py
```

## 故障排除

### Claude API常见问题

1. **API密钥错误**：确保设置了正确的`ANTHROPIC_API_KEY`环境变量
2. **请求格式错误**：检查请求格式是否符合Claude API的要求
3. **附件处理错误**：确保附件格式正确，并且文件存在

### Azure OpenAI API常见问题

1. **API密钥或端点错误**：确保设置了正确的`AZURE_OPENAI_API_KEY`和`AZURE_OPENAI_ENDPOINT`环境变量
2. **部署ID错误**：确保使用了正确的部署ID，可以通过设置`AZURE_OPENAI_DEPLOYMENT_ID`环境变量或在代码中指定
3. **API版本问题**：如果遇到API版本相关错误，可以尝试修改`api_version`参数
4. **多模态支持**：确保您的Azure OpenAI部署支持多模态输入

## 资源

- [Claude MCP官方文档](https://www.claudemcp.com/zh)
- [Azure OpenAI API文档](https://learn.microsoft.com/zh-cn/azure/ai-services/openai/)
- [Anthropic API文档](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。 