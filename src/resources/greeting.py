"""
问候相关的资源
"""

from mcp.server.fastmcp import FastMCP
import datetime


def register_greeting_resources(mcp: FastMCP):
    """注册问候相关的资源到 MCP 服务器"""
    
    @mcp.resource("greeting://{name}")
    def get_greeting(name: str) -> str:
        """获取个性化问候语"""
        current_time = datetime.datetime.now()
        hour = current_time.hour
        
        if 5 <= hour < 12:
            time_greeting = "早上好"
        elif 12 <= hour < 18:
            time_greeting = "下午好"
        else:
            time_greeting = "晚上好"
        
        return f"{time_greeting}, {name}! 现在是 {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    @mcp.resource("quote://daily")
    def get_daily_quote() -> str:
        """获取每日名言"""
        quotes = [
            "今天是新的一天，充满无限可能。",
            "成功不是终点，失败不是致命的，重要的是继续前进的勇气。",
            "学习是一辈子的事业。",
            "每一次挫折都是成长的机会。",
            "保持好奇心，世界会变得更有趣。"
        ]
        
        # 根据日期选择名言，确保每天都是同一句
        day_of_year = datetime.datetime.now().timetuple().tm_yday
        quote_index = day_of_year % len(quotes)
        
        return f"📝 每日名言：{quotes[quote_index]}" 