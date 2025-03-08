# MCP 服务器

[English](README.md)

## 项目概述

基于 FastAPI 和 MCP（模型上下文协议），实现 AI 模型与开发环境 之间的标准化上下文交互，提升 AI 应用的可扩展性和可维护性。该项目旨在简化模型部署，提供高效的 API 接口，并确保模型输入输出的一致性，以便开发者能够更方便地集成和管理 AI 任务。

MCP（Model Context Protocol）是一个统一的模型上下文交互协议，用于在AI模型和开发环境之间建立标准化的上下文交互。本项目提供了一个基于Python的MCP服务器实现，支持基本的MCP协议功能，包括初始化、采样和会话管理。

## 功能特性

- **JSON-RPC 2.0**: 基于标准JSON-RPC 2.0协议实现请求-响应通信
- **SSE连接**: 支持服务器发送事件（Server-Sent Events）连接，用于实时通知
- **模块化设计**: 采用模块化设计，易于扩展和定制
- **异步处理**: 使用FastAPI和异步IO实现高性能服务
- **完整的客户端**: 提供完整的测试客户端实现

## 项目结构

```
mcp_server/
├── mcp_server.py         # MCP服务器主程序
├── mcp_client.py         # MCP客户端测试程序
├── routers/
│   ├── __init__.py       # 路由器包初始化
│   └── base_router.py    # 基础路由器实现
├── requirements.txt      # 项目依赖
└── README.md             # 项目说明文档
```

## 安装

1. 克隆项目仓库：

```bash
git clone https://github.com/freedanfan/mcp_server.git
cd mcp_server
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 启动服务器

```bash
python mcp_server.py
```

默认情况下，服务器将在`127.0.0.1:12000`上启动。您可以通过环境变量自定义主机和端口：

```bash
export MCP_SERVER_HOST=0.0.0.0
export MCP_SERVER_PORT=8000
python mcp_server.py
```

### 运行客户端

在另一个终端中运行客户端：

```bash
python mcp_client.py
```

如果服务器不在默认地址运行，可以设置环境变量：

```bash
export MCP_SERVER_URL="http://your-server-address:port"
python mcp_client.py
```

## API端点

服务器提供以下API端点：

- **根路径** (`/`): 提供服务器信息
- **API端点** (`/api`): 处理JSON-RPC请求
- **SSE端点** (`/sse`): 处理SSE连接

## MCP协议实现

### 初始化流程

1. 客户端通过SSE连接到服务器
2. 服务器返回API端点URI
3. 客户端发送初始化请求，包含协议版本和能力
4. 服务器响应初始化请求，返回服务器能力

### 采样请求

客户端可以发送采样请求，包含提示词：

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "method": "sample",
  "params": {
    "prompt": "你好，请介绍一下自己。"
  }
}
```

服务器将返回采样结果：

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "result": {
    "content": "这是对提示词的响应...",
    "usage": {
      "prompt_tokens": 10,
      "completion_tokens": 50,
      "total_tokens": 60
    }
  }
}
```

### 关闭会话

客户端可以发送关闭请求：

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "method": "shutdown",
  "params": {}
}
```

服务器将优雅地关闭：

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "result": {
    "status": "shutting_down"
  }
}
```

## 扩展开发

### 添加新方法

要添加新的MCP方法，请在`MCPServer`类中添加处理函数，并在`_register_methods`方法中注册：

```python
def handle_new_method(self, params: dict) -> dict:
    """处理新方法"""
    logger.info(f"收到新方法请求: {params}")
    # 处理逻辑
    return {"result": "success"}

def _register_methods(self):
    # 注册现有方法
    self.router.register_method("initialize", self.handle_initialize)
    self.router.register_method("sample", self.handle_sample)
    self.router.register_method("shutdown", self.handle_shutdown)
    # 注册新方法
    self.router.register_method("new_method", self.handle_new_method)
```

### 集成AI模型

要集成实际的AI模型，请修改`handle_sample`方法：

```python
async def handle_sample(self, params: dict) -> dict:
    """处理采样请求"""
    logger.info(f"收到采样请求: {params}")
    
    # 获取提示词
    prompt = params.get("prompt", "")
    
    # 调用AI模型API
    # 例如：使用OpenAI API
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    content = response.choices[0].message.content
    usage = response.usage
    
    return {
        "content": content,
        "usage": {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens
        }
    }
```

## 故障排除

### 常见问题

1. **连接错误**：确保服务器正在运行，并且客户端使用正确的服务器URL
2. **405 Method Not Allowed**：确保客户端发送请求到正确的API端点
3. **SSE连接失败**：检查网络连接和防火墙设置

### 日志记录

服务器和客户端都提供详细的日志记录。查看日志以获取更多信息：

```bash
# 增加日志级别
export PYTHONPATH=.
python -m logging -v DEBUG -m mcp_server
```

## 参考资料

- [MCP协议规范](https://www.claudemcp.com/zh/specification)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [JSON-RPC 2.0规范](https://www.jsonrpc.org/specification)
- [SSE规范](https://html.spec.whatwg.org/multipage/server-sent-events.html)

## 许可证

本项目采用MIT许可证。详情请参阅LICENSE文件。 