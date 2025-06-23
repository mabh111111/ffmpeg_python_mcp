# FFmpeg Python MCP 服务器

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green.svg)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Powered-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 📋 项目简介

这是一个基于 **Model Context Protocol (MCP)** 的 FFmpeg 视频音频处理服务器。该项目为 AI 助手提供了强大的视频和音频处理能力，包括格式转换、切割合并、特效添加等功能，支持硬件加速处理。

### 🌟 主要特性

- 🎬 **完整的视频音频处理功能** - 转换、切割、合并、压缩等
- ⚡ **硬件加速支持** - Intel QSV、NVIDIA NVENC 等
- 🔄 **异步并发处理** - 支持多任务并行执行
- 🌐 **流媒体支持** - M3U8 合并、直播流处理
- 🎨 **视频特效** - 水印、GIF转换、变速等
- 🤖 **AI友好接口** - 标准 MCP 协议，易于集成

## 🚀 快速开始

### 前置要求

1. **Python 3.12+**
2. **FFmpeg** - 请先安装 FFmpeg：
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg
   
   # Windows
   # 从 https://ffmpeg.org/download.html 下载
   ```
3. **uv** 包管理器：
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

### 安装和运行

1. **克隆项目**
   ```bash
   git clone https://github.com/mabh111111/ffmpeg_python_mcp.git
   cd ffmpeg_python_mcp
   ```

2. **安装依赖**
   ```bash
   uv sync
   ```

3. **运行 MCP 服务器**
   ```bash
   # 开发模式（推荐用于测试）
   uv run mcp dev main.py
   
   # 或直接运行
   uv run python main.py
   ```

## 🔧 MCP 配置和使用

### 什么是 MCP？

Model Context Protocol (MCP) 是一个标准化协议，允许 AI 助手（如 Claude、ChatGPT 等）安全地访问外部工具和资源。

### 在 AI 客户端中配置

#### 配置 Claude Desktop

1. 打开 Claude Desktop 配置文件：
   ```bash
   # macOS
   ~/Library/Application Support/Claude/claude_desktop_config.json
   
   # Windows
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. 添加 MCP 服务器配置：
   ```json
   {
     "mcpServers": {
       "ffmpeg-processor": {
         "command": "uv",
         "args": ["run", "python", "/path/to/ffmpeg_python_mcp/main.py"],
         "cwd": "/path/to/ffmpeg_python_mcp"
       }
     }
   }
   ```

3. 重启 Claude Desktop

#### 配置其他 MCP 客户端

对于支持 MCP 的其他客户端，使用以下连接信息：
- **命令**: `uv run python main.py`
- **工作目录**: 项目根目录
- **协议**: stdio

### 验证连接

运行服务器后，你应该能在 AI 助手中看到以下可用工具：

- 视频音频提取和转换工具
- 切割和合并功能
- 硬件加速处理
- 视频特效和压缩

## 🛠️ 主要功能

### 📤 音频提取
```python
# 从视频提取音频
extract_audio_from_video(video_path, output_path?, audio_format?, audio_quality?)

# 提取音频片段
extract_audio_segment(video_path, start_time, duration, output_path?, audio_format?)
```

### 🔄 格式转换
```python
# 视频格式转换
convert_video_format(input_path, output_path?, output_format?, video_codec?, audio_codec?, quality?)

# 音频格式转换  
convert_audio_format(input_path, output_path?, output_format?, audio_codec?, bitrate?)
```

### ✂️ 切割合并
```python
# 视频切割
cut_video_segment(input_path, start_time, end_time?|duration?, output_path?)

# 视频合并
merge_videos(video_paths, output_path?, merge_method?)
```

### 🎨 视频特效
```python
# 转换为GIF
video_to_gif(input_path, output_path?, start_time?, duration?, width?, fps?, quality?)

# 添加水印
add_watermark(input_path, watermark_path, output_path?, position?, opacity?, margin?)

# 调整分辨率
resize_video(input_path, width, height, output_path?, keep_aspect_ratio?)
```

### 🚀 硬件加速
```python
# 检查硬件加速支持
check_hardware_acceleration()

# QSV硬件加速转换
convert_video_with_qsv(input_path, output_path?, output_format?, qsv_encoder?, quality?)
```

### 🌐 流媒体处理
```python
# M3U8合并
merge_m3u8_to_mp4(m3u8_url, output_path, headers?)
```

## ⚡ 性能特性

### 异步并发处理
- 所有处理函数支持异步执行
- AI 可同时调用多个工具进行并行处理
- 批量处理性能提升 3-5 倍

### 硬件加速
- **Intel QSV**: 处理速度提升 3-10 倍
- **NVIDIA NVENC**: GPU 硬件编码
- **自动检测**: 智能选择最佳加速方案

## 📁 项目结构
```
ffmpeg_python_mcp/
├── main.py                     # MCP 服务器入口
├── src/                        # 源代码模块
│   ├── tools/
│   │   └── math_tools.py       # 数学工具（示例）
│   ├── resources/
│   │   └── greeting.py         # 问候资源（示例）
│   └── config/
│       └── server_config.py    # 配置管理
├── pyproject.toml              # 项目配置
├── uv.lock                     # 依赖锁定
└── README.md                   # 项目文档
```

## 🔧 开发指南

### 添加新工具

1. 在相应模块中定义工具函数
2. 使用 `@server.tool` 装饰器注册
3. 添加完整的参数类型和文档字符串

```python
@server.tool()
async def my_new_tool(input_path: str, option: str = "default") -> str:
    """
    工具描述
    
    Args:
        input_path: 输入文件路径
        option: 可选参数
        
    Returns:
        处理结果
    """
    # 实现逻辑
    return result
```

### 运行测试

```bash
# 检查代码格式
uv run ruff check

# 运行开发模式
uv run mcp dev main.py
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 支持

- **GitHub Issues**: [提交问题](https://github.com/mabh111111/ffmpeg_python_mcp/issues)
- **讨论**: [GitHub Discussions](https://github.com/mabh111111/ffmpeg_python_mcp/discussions)

## 🔗 相关链接

- [Model Context Protocol 官方文档](https://modelcontextprotocol.io/)
- [FFmpeg 官方网站](https://ffmpeg.org/)
- [Claude Desktop](https://claude.ai/desktop)

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
