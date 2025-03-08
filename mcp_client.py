#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCP 客户端
用于测试 MCP 服务器的简单客户端
"""

import os
import sys
import json
import time
import uuid
import logging
import requests
import sseclient
import threading
from typing import Dict, Any, Optional, List, Union

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_client")

class MCPClient:
    """MCP 客户端类"""
    
    def __init__(self, server_url: str = "http://127.0.0.1:12000"):
        """初始化 MCP 客户端"""
        self.server_url = server_url
        self.sse_url = f"{server_url}/sse"
        self.post_url = None  # 将由 SSE 连接提供
        self.sse_thread = None
        self.is_connected = False
        
    def connect(self):
        """连接到 MCP 服务器"""
        logger.info(f"连接到 MCP 服务器: {self.server_url}")
        
        # 启动 SSE 连接线程
        self.sse_thread = threading.Thread(target=self._sse_listener)
        self.sse_thread.daemon = True
        self.sse_thread.start()
        
        # 等待连接建立
        timeout = 10
        start_time = time.time()
        while not self.is_connected and time.time() - start_time < timeout:
            time.sleep(0.1)
        
        if not self.is_connected:
            raise ConnectionError(f"无法连接到 MCP 服务器: {self.server_url}")
        
        logger.info(f"成功连接到 MCP 服务器，API 端点: {self.post_url}")
        
        # 发送初始化请求
        return self.initialize()
    
    def _sse_listener(self):
        """SSE 连接监听器"""
        try:
            headers = {"Accept": "text/event-stream"}
            response = requests.get(self.sse_url, headers=headers, stream=True)
            response.raise_for_status()
            
            client = sseclient.SSEClient(response)
            for event in client.events():
                if event.event == "endpoint":
                    data = json.loads(event.data)
                    self.post_url = data.get("uri")
                    logger.info(f"收到端点 URI: {self.post_url}")
                    self.is_connected = True
                elif event.event == "heartbeat":
                    logger.debug("收到心跳")
                else:
                    logger.info(f"收到事件: {event.event}, 数据: {event.data}")
        except Exception as e:
            logger.exception(f"SSE 连接错误: {e}")
            self.is_connected = False
    
    def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送 JSON-RPC 请求"""
        if not self.is_connected or not self.post_url:
            raise ConnectionError("未连接到 MCP 服务器")
        
        # 构建请求
        request_id = str(uuid.uuid4())
        request_data = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method
        }
        if params:
            request_data["params"] = params
        
        # 发送请求
        logger.info(f"发送请求: {method} 到 {self.post_url}")
        try:
            response = requests.post(self.post_url, json=request_data)
            response.raise_for_status()
            
            # 解析响应
            response_data = response.json()
            
            # 检查是否有错误
            if "error" in response_data:
                error = response_data["error"]
                logger.error(f"请求错误: {error.get('message')}, 代码: {error.get('code')}")
            
            return response_data
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"响应状态码: {e.response.status_code}")
                try:
                    logger.error(f"响应内容: {e.response.text}")
                except:
                    pass
            raise
    
    def initialize(self) -> Dict[str, Any]:
        """初始化 MCP 会话"""
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "MCPTestClient",
                "version": "1.0.0"
            }
        }
        
        return self.send_request("initialize", params)
    
    def sample(self, prompt: str) -> Dict[str, Any]:
        """发送采样请求"""
        params = {
            "prompt": prompt
        }
        
        return self.send_request("sample", params)
    
    def shutdown(self) -> Dict[str, Any]:
        """关闭 MCP 会话"""
        return self.send_request("shutdown", {})


def main():
    """主函数"""
    try:
        # 从环境变量获取服务器 URL
        server_url = os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:12000")
        
        # 创建客户端
        client = MCPClient(server_url=server_url)
        
        # 连接到服务器
        init_response = client.connect()
        logger.info(f"初始化响应: {json.dumps(init_response, indent=2)}")
        
        # 发送采样请求
        sample_response = client.sample("你好，请介绍一下自己。")
        logger.info(f"采样响应: {json.dumps(sample_response, indent=2)}")
        
        # 关闭会话
        shutdown_response = client.shutdown()
        logger.info(f"关闭响应: {json.dumps(shutdown_response, indent=2)}")
        
    except Exception as e:
        logger.exception(f"客户端错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 