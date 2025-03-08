# MCP Server

[中文文档](README.zh-CN.md)

## Project Overview

Built on FastAPI and MCP (Model Context Protocol), this project enables standardized context interaction between AI models and development environments. It enhances the scalability and maintainability of AI applications by simplifying model deployment, providing efficient API endpoints, and ensuring consistency in model input and output, making it easier for developers to integrate and manage AI tasks.

MCP (Model Context Protocol) is a unified protocol for context interaction between AI models and development environments. This project provides a Python-based MCP server implementation that supports basic MCP protocol features, including initialization, sampling, and session management.

## Features

- **JSON-RPC 2.0**: Request-response communication based on standard JSON-RPC 2.0 protocol
- **SSE Connection**: Support for Server-Sent Events connections for real-time notifications
- **Modular Design**: Modular architecture for easy extension and customization
- **Asynchronous Processing**: High-performance service using FastAPI and asynchronous IO
- **Complete Client**: Includes a full test client implementation

## Project Structure

```
mcp_server/
├── mcp_server.py         # MCP server main program
├── mcp_client.py         # MCP client test program
├── routers/
│   ├── __init__.py       # Router package initialization
│   └── base_router.py    # Base router implementation
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/freedanfan/mcp_server.git
cd mcp_server
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

```bash
python mcp_server.py
```

By default, the server will start on `127.0.0.1:12000`. You can customize the host and port using environment variables:

```bash
export MCP_SERVER_HOST=0.0.0.0
export MCP_SERVER_PORT=8000
python mcp_server.py
```

### Running the Client

Run the client in another terminal:

```bash
python mcp_client.py
```

If the server is not running at the default address, you can set an environment variable:

```bash
export MCP_SERVER_URL="http://your-server-address:port"
python mcp_client.py
```

## API Endpoints

The server provides the following API endpoints:

- **Root Path** (`/`): Provides server information
- **API Endpoint** (`/api`): Handles JSON-RPC requests
- **SSE Endpoint** (`/sse`): Handles SSE connections

## MCP Protocol Implementation

### Initialization Flow

1. Client connects to the server via SSE
2. Server returns the API endpoint URI
3. Client sends an initialization request with protocol version and capabilities
4. Server responds to the initialization request, returning server capabilities

### Sampling Request

Clients can send sampling requests with prompts:

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "method": "sample",
  "params": {
    "prompt": "Hello, please introduce yourself."
  }
}
```

The server will return sampling results:

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "result": {
    "content": "This is a response to the prompt...",
    "usage": {
      "prompt_tokens": 10,
      "completion_tokens": 50,
      "total_tokens": 60
    }
  }
}
```

### Closing a Session

Clients can send a shutdown request:

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "method": "shutdown",
  "params": {}
}
```

The server will gracefully shut down:

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "result": {
    "status": "shutting_down"
  }
}
```

## Development Extensions

### Adding New Methods

To add new MCP methods, add a handler function to the `MCPServer` class and register it in the `_register_methods` method:

```python
def handle_new_method(self, params: dict) -> dict:
    """Handle new method"""
    logger.info(f"Received new method request: {params}")
    # Processing logic
    return {"result": "success"}

def _register_methods(self):
    # Register existing methods
    self.router.register_method("initialize", self.handle_initialize)
    self.router.register_method("sample", self.handle_sample)
    self.router.register_method("shutdown", self.handle_shutdown)
    # Register new method
    self.router.register_method("new_method", self.handle_new_method)
```

### Integrating AI Models

To integrate actual AI models, modify the `handle_sample` method:

```python
async def handle_sample(self, params: dict) -> dict:
    """Handle sampling request"""
    logger.info(f"Received sampling request: {params}")
    
    # Get prompt
    prompt = params.get("prompt", "")
    
    # Call AI model API
    # For example: using OpenAI API
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

## Troubleshooting

### Common Issues

1. **Connection Errors**: Ensure the server is running and the client is using the correct server URL
2. **405 Method Not Allowed**: Ensure the client is sending requests to the correct API endpoint
3. **SSE Connection Failure**: Check network connections and firewall settings

### Logging

Both server and client provide detailed logging. View logs for more information:

```bash
# Increase log level
export PYTHONPATH=.
python -m logging -v DEBUG -m mcp_server
```

## References

- [MCP Protocol Specification](https://www.claudemcp.com/specification)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [SSE Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)

## License

This project is licensed under the MIT License. See the LICENSE file for details. 