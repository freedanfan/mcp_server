#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCP 提示词管理路由器
处理提示词相关的 MCP 请求
"""

import logging
from typing import Dict, Any, Optional, List

from .base_router import MCPBaseRouter

logger = logging.getLogger("prompt_router")

class PromptRouter(MCPBaseRouter):
    """提示词管理路由器"""
    
    def __init__(self):
        """初始化路由器"""
        super().__init__()
        self.prompts = {}
        self._register_methods()
        self._register_prompts()
        
    def _register_methods(self):
        """注册方法处理器"""
        self.register_method("prompts/list", self.handle_list_prompts)
        self.register_method("prompts/get", self.handle_get_prompt)
        self.register_method("prompts/create", self.handle_create_prompt)
        self.register_method("prompts/update", self.handle_update_prompt)
        self.register_method("prompts/delete", self.handle_delete_prompt)
        
    def _register_prompts(self):
        """注册示例提示词"""
        self.prompts["code_review"] = {
            "id": "code_review",
            "name": "代码审查",
            "description": "用于代码审查的提示词模板",
            "content": "你是一个专业的代码审查者。请审查以下代码并提供改进建议：\n\n{{code}}"
        }
        
        self.prompts["documentation"] = {
            "id": "documentation",
            "name": "文档生成",
            "description": "用于生成代码文档的提示词模板",
            "content": "请为以下代码生成详细的文档，包括函数说明、参数描述和使用示例：\n\n{{code}}"
        }
    
    def handle_list_prompts(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理提示词列表请求"""
        logger.info("处理提示词列表请求")
        
        # 构建提示词列表
        prompts_list = list(self.prompts.values())
        
        return {
            "prompts": prompts_list
        }
    
    def handle_get_prompt(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理获取提示词请求"""
        if not params or "id" not in params:
            raise ValueError("缺少提示词 ID 参数")
        
        prompt_id = params["id"]
        logger.info(f"处理获取提示词请求，提示词 ID: {prompt_id}")
        
        # 查找提示词
        if prompt_id not in self.prompts:
            raise ValueError(f"提示词 ID '{prompt_id}' 不存在")
        
        return self.prompts[prompt_id]
    
    async def handle_create_prompt(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理创建提示词请求（异步）"""
        if not params or "id" not in params or "content" not in params:
            raise ValueError("缺少必要参数")
        
        prompt_id = params["id"]
        logger.info(f"处理创建提示词请求，提示词 ID: {prompt_id}")
        
        # 检查是否已存在
        if prompt_id in self.prompts:
            raise ValueError(f"提示词 ID '{prompt_id}' 已存在")
        
        # 创建提示词
        self.prompts[prompt_id] = {
            "id": prompt_id,
            "name": params.get("name", prompt_id),
            "description": params.get("description", ""),
            "content": params["content"]
        }
        
        return self.prompts[prompt_id]
    
    def handle_update_prompt(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理更新提示词请求"""
        if not params or "id" not in params:
            raise ValueError("缺少提示词 ID 参数")
        
        prompt_id = params["id"]
        logger.info(f"处理更新提示词请求，提示词 ID: {prompt_id}")
        
        # 检查是否存在
        if prompt_id not in self.prompts:
            raise ValueError(f"提示词 ID '{prompt_id}' 不存在")
        
        # 更新提示词
        prompt = self.prompts[prompt_id]
        if "name" in params:
            prompt["name"] = params["name"]
        if "description" in params:
            prompt["description"] = params["description"]
        if "content" in params:
            prompt["content"] = params["content"]
        
        return prompt
    
    def handle_delete_prompt(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理删除提示词请求"""
        if not params or "id" not in params:
            raise ValueError("缺少提示词 ID 参数")
        
        prompt_id = params["id"]
        logger.info(f"处理删除提示词请求，提示词 ID: {prompt_id}")
        
        # 检查是否存在
        if prompt_id not in self.prompts:
            raise ValueError(f"提示词 ID '{prompt_id}' 不存在")
        
        # 删除提示词
        prompt = self.prompts.pop(prompt_id)
        
        return {
            "id": prompt_id,
            "deleted": True
        }