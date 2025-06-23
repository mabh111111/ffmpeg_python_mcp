"""
服务器配置类
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ServerConfig:
    """MCP 服务器配置"""
    
    # 服务器基本信息
    name: str = "MCP Demo Server"
    version: str = "1.0.0"
    description: str = "一个模块化的 MCP 服务器示例"
    
    # 服务器行为配置
    enable_logging: bool = True
    log_level: str = "INFO"
    
    # 功能开关
    enable_math_tools: bool = True
    enable_greeting_resources: bool = True
    
    # 运行时配置
    host: str = "localhost"
    port: Optional[int] = None  # stdio 模式下不需要端口
    
    @classmethod
    def get_default_config(cls) -> "ServerConfig":
        """获取默认配置"""
        return cls()
    
    @classmethod
    def get_development_config(cls) -> "ServerConfig":
        """获取开发环境配置"""
        return cls(
            name="MCP Demo Server (Dev)",
            enable_logging=True,
            log_level="DEBUG"
        )
    
    @classmethod
    def get_production_config(cls) -> "ServerConfig":
        """获取生产环境配置"""
        return cls(
            name="MCP Demo Server (Prod)",
            enable_logging=True,
            log_level="WARNING"
        ) 