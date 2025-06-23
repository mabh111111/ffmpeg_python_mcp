"""
数学相关的工具函数
"""

from mcp.server.fastmcp import FastMCP


def register_math_tools(mcp: FastMCP):
    """注册数学相关的工具到 MCP 服务器"""
    
    @mcp.tool()
    def add(a: int = 0, b: int = 0) -> int:
        """将两个数字相加"""
        try:
            return int(a) + int(b)
        except Exception as e:
            raise ValueError(f"参数错误: {e}")
    
    @mcp.tool()
    def subtract(a: int = 0, b: int = 0) -> int:
        """计算两个数字的差"""
        try:
            return int(a) - int(b)
        except Exception as e:
            raise ValueError(f"参数错误: {e}")
    
    @mcp.tool()
    def multiply(a: int = 1, b: int = 1) -> int:
        """计算两个数字的乘积"""
        try:
            return int(a) * int(b)
        except Exception as e:
            raise ValueError(f"参数错误: {e}")
    
    @mcp.tool()
    def divide(a: float, b: float) -> float:
        """计算两个数字的商"""
        try:
            if b == 0:
                raise ValueError("除数不能为零")
            return float(a) / float(b)
        except Exception as e:
            raise ValueError(f"参数错误: {e}") 