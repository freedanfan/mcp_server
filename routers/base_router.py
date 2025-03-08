#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCP 服务基础路由器
提供处理 MCP 协议请求的基础类
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Callable

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

logger = logging.getLogger("mcp_router")

class MCPRequest(BaseModel):
    """MCP 请求模型"""
    jsonrpc: str = Field("2.0", description="JSON-RPC 版本")
    id: Optional[Union[str, int]] = Field(None, description="请求 ID")
    method: str = Field(..., description="方法名称")
    params: Optional[Dict[str, Any]] = Field(None, description="参数")

class MCPError(BaseModel):
    """MCP 错误模型"""
    code: int = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    data: Optional[Any] = Field(None, description="错误数据")

class MCPResponse(BaseModel):
    """MCP 响应模型"""
    jsonrpc: str = Field("2.0", description="JSON-RPC 版本")
    id: Optional[Union[str, int]] = Field(None, description="请求 ID")
    result: Optional[Any] = Field(None, description="结果")
    error: Optional[MCPError] = Field(None, description="错误")

class MCPNotification(BaseModel):
    """MCP 通知模型"""
    jsonrpc: str = Field("2.0", description="JSON-RPC 版本")
    method: str = Field(..., description="方法名称")
    params: Optional[Dict[str, Any]] = Field(None, description="参数")

class MCPBaseRouter:
    """MCP 基础路由器类"""
    
    def __init__(self):
        """初始化路由器"""
        self.router = APIRouter()
        self.methods = {}
        self._register_routes()
        
    def _register_routes(self):
        """注册路由"""
        # 处理 JSON-RPC 请求的路由 - 修复：使用非空路径
        self.router.post("/")(self.handle_request)
        
        # 注意：SSE路由将在主应用中注册，这里不再注册
        
    def register_method(self, method_name: str, handler: Callable):
        """注册方法处理器"""
        self.methods[method_name] = handler
        
    async def handle_request(self, request: Request) -> JSONResponse:
        """处理 MCP 请求"""
        try:
            # 解析请求体
            body = await request.json()
            
            # 验证是否为有效的 JSON-RPC 请求
            if not isinstance(body, dict) or body.get("jsonrpc") != "2.0":
                return self._create_error_response(
                    None, -32600, "无效的请求", "请求不符合 JSON-RPC 2.0 规范"
                )
            
            # 解析请求
            mcp_request = MCPRequest(**body)
            
            # 检查是否为通知（没有 ID）
            is_notification = mcp_request.id is None
            
            # 查找方法处理器
            method_name = mcp_request.method
            handler = self.methods.get(method_name)
            
            if not handler:
                if is_notification:
                    return JSONResponse(content={})
                return self._create_error_response(
                    mcp_request.id, -32601, "方法不存在", f"方法 '{method_name}' 不存在"
                )
            
            # 调用方法处理器
            try:
                result = await handler(mcp_request.params) if asyncio.iscoroutinefunction(handler) else handler(mcp_request.params)
                
                # 如果是通知，不需要返回结果
                if is_notification:
                    return JSONResponse(content={})
                
                # 返回成功响应
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": mcp_request.id,
                    "result": result
                })
            except Exception as e:
                logger.exception(f"处理方法 '{method_name}' 时出错")
                if is_notification:
                    return JSONResponse(content={})
                return self._create_error_response(
                    mcp_request.id, -32603, "内部错误", str(e)
                )
                
        except Exception as e:
            logger.exception("处理请求时出错")
            return self._create_error_response(
                None, -32700, "解析错误", str(e)
            )
    
    async def handle_sse_connection(self, request: Request):
        """处理 SSE 连接"""
        async def event_generator():
            # 发送端点信息
            endpoint = str(request.url).replace("/sse", "")
            yield f"event: endpoint\ndata: {json.dumps({'uri': endpoint})}\n\n"
            
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
    
    def _create_error_response(self, id: Optional[Union[str, int]], code: int, message: str, data: Any = None) -> JSONResponse:
        """创建错误响应"""
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": id,
            "error": {
                "code": code,
                "message": message,
                "data": data
            }
        })
    
    def create_notification(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """创建通知"""
        notification = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params:
            notification["params"] = params
        return notification
    
    # 同步方法示例
    def handle_sync_method(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理同步方法示例"""
        logger.info(f"同步处理方法，参数: {params}")
        return {"status": "success", "message": "同步方法处理成功", "params": params}
    
    # 异步方法示例
    async def handle_async_method(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理异步方法示例"""
        logger.info(f"异步处理方法，参数: {params}")
        # 模拟异步操作
        await asyncio.sleep(0.1)
        return {"status": "success", "message": "异步方法处理成功", "params": params}