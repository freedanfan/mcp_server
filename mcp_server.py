#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCP 服务器实现
基于 base_router.py 实现的 MCP 服务器
"""

import os
import sys
import json
import logging
import asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

# 导入基础路由器
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from routers.base_router import MCPBaseRouter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_server")

# 加载环境变量
load_dotenv()

class MCPServer:
    """MCP 服务器类"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        """初始化 MCP 服务器"""
        self.host = host
        self.port = port
        self.app = FastAPI(title="MCP Server", description="Model Context Protocol Server")
        self.router = MCPBaseRouter()
        
        # 注册方法处理器
        self._register_methods()
        
        # 注册路由 - 修复：添加一个非空路径
        self.app.include_router(self.router.router, prefix="/api")
        
        # 添加根路径重定向
        @self.app.get("/")
        async def root():
            return {"message": "MCP Server is running", "api_endpoint": "/api"}
        
        # 添加SSE端点
        @self.app.get("/sse")
        async def sse_endpoint(request: Request):
            return await self.handle_sse_connection(request)
        
    def _register_methods(self):
        """注册方法处理器"""
        # 注册初始化方法
        self.router.register_method("initialize", self.handle_initialize)
        
        # 注册采样方法
        self.router.register_method("sample", self.handle_sample)
        
        # 注册其他方法
        self.router.register_method("shutdown", self.handle_shutdown)
    
    async def handle_sse_connection(self, request: Request):
        """处理 SSE 连接"""
        async def event_generator():
            # 发送端点信息 - 修复：返回正确的API端点
            base_url = str(request.url).split("/sse")[0]
            api_endpoint = f"{base_url}/api"
            yield f"event: endpoint\ndata: {json.dumps({'uri': api_endpoint})}\n\n"
            
            # 保持连接活跃
            while True:
                # 每 30 秒发送一次心跳
                await asyncio.sleep(30)
                yield f"event: heartbeat\ndata: {json.dumps({'timestamp': asyncio.get_event_loop().time()})}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    def handle_initialize(self, params: dict) -> dict:
        """处理初始化请求"""
        logger.info(f"收到初始化请求: {params}")
        
        # 获取协议版本
        protocol_version = params.get("protocolVersion", "2024-11-05")
        
        # 返回服务器能力
        return {
            "protocolVersion": protocol_version,
            "capabilities": {
                "logging": {},
                "prompts": {
                    "listChanged": True
                },
                "resources": {
                    "subscribe": True,
                    "listChanged": True
                },
                "tools": {
                    "listChanged": True
                }
            },
            "serverInfo": {
                "name": "MCPServer",
                "version": "1.0.0"
            }
        }
    
    async def handle_sample(self, params: dict) -> dict:
        """处理采样请求"""
        logger.info(f"收到采样请求: {params}")
        
        # 获取提示词
        prompt = params.get("prompt", "")
        
        # 模拟采样响应
        return {
            "content": f"这是对提示词 '{prompt[:30]}...' 的模拟响应。在实际实现中，这里应该调用 AI 模型 API。",
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": 50,
                "total_tokens": len(prompt.split()) + 50
            }
        }
    
    def handle_shutdown(self, params: dict) -> dict:
        """处理关闭请求"""
        logger.info(f"收到关闭请求: {params}")
        
        # 安排服务器关闭
        asyncio.create_task(self._shutdown())
        
        return {"status": "shutting_down"}
    
    async def _shutdown(self):
        """关闭服务器"""
        logger.info("服务器将在 2 秒后关闭...")
        await asyncio.sleep(2)
        os._exit(0)
    
    def run(self):
        """运行服务器"""
        logger.info(f"启动 MCP 服务器，监听 {self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port)


def main():
    """主函数"""
    try:
        # 从环境变量获取主机和端口
        host = os.environ.get("MCP_SERVER_HOST", "127.0.0.1")
        port = int(os.environ.get("MCP_SERVER_PORT", 12000))
        
        # 创建并运行服务器
        server = MCPServer(host=host, port=port)
        server.run()
    except Exception as e:
        logger.exception(f"启动服务器时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 