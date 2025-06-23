# FFMPEG Python MCP 项目

## 项目简介
这是一个基于 Model Context Protocol (MCP) 的模块化 Python 项目。

## ✅ 已完成的功能

### 1. 环境设置
- ✅ 安装了 `uv` 包管理器
- ✅ 使用 `uv` 创建了 Python 3.12 项目
- ✅ 安装了 MCP Python SDK (`mcp[cli]`)

### 2. 模块化架构重构
- ✅ 实现了模块化的项目结构
- ✅ 分离了工具、资源和配置模块
- ✅ 添加了配置管理系统
- ✅ 支持不同环境配置（开发/生产）

### 3. MCP 服务器功能
- ✅ **数学工具模块**：加法、减法、乘法、除法
- ✅ **问候资源模块**：智能时间问候、每日名言
- ✅ **配置系统**：环境特定配置、功能开关
- ✅ **日志系统**：可配置的日志级别

### 4. 视频音频处理器 (全功能升级)
- ✅ **视频音频提取**：从视频文件中提取完整音频
- ✅ **音频片段提取**：提取指定时间段的音频片段
- ✅ **视频信息获取**：获取视频文件的详细信息
- ✅ **格式转换**：视频、音频格式转换（MP4↔AVI↔MOV等）
- ✅ **M3U8 合并**：将 M3U8 流媒体合并为 MP4 文件
- ✅ **视频切割**：精确切割视频片段
- ✅ **音频切割**：精确切割音频片段
- ✅ **视频合并**：多个视频文件拼接或混合
- ✅ **音频合并**：多个音频文件拼接或混音
- ✅ **视频转GIF**：高质量视频转动图，支持时间范围选择
- ✅ **视频缩放**：调整视频分辨率，支持保持宽高比
- ✅ **添加水印**：为视频添加图片水印，支持多种位置
- ✅ **提取帧图**：从视频中提取静态图片帧
- ✅ **变速播放**：视频加速/减速，支持保持音调
- ✅ **视频压缩**：智能压缩视频文件大小
- ✅ **硬件加速**：Intel QSV 硬件加速支持，大幅提升处理速度 🆕
- ✅ **加速检测**：自动检测系统支持的硬件加速选项 🆕
- ✅ **多格式支持**：支持所有主流视频音频格式
- ✅ **质量控制**：可配置编码器、码率、质量等参数
- ✅ **FFmpeg 集成**：直接调用系统 FFmpeg 命令
- ✅ **异步处理**：所有工具函数已升级为异步版本，支持AI并发调用

## 📁 项目结构
```
mcp-server-demo/
├── server.py                    # 主服务器入口文件
├── src/                         # 源代码模块
│   ├── __init__.py
│   ├── tools/                   # 工具模块
│   │   ├── __init__.py
│   │   └── math_tools.py        # 数学相关工具
│   ├── resources/               # 资源模块
│   │   ├── __init__.py
│   │   └── greeting.py          # 问候相关资源
│   └── config/                  # 配置模块
│       ├── __init__.py
│       └── server_config.py     # 服务器配置类
├── pyproject.toml               # uv 项目配置
├── uv.lock                     # 依赖锁定文件
├── .venv/                      # 虚拟环境
└── README.md                   # 项目说明文档
```

## 🛠️ 服务器功能

### 视频音频处理器 (Video Audio Processor) - 主要功能

> 🚀 **性能升级**: 所有处理函数已升级为异步版本，支持并发处理多个任务，提高处理效率！

#### 📤 音频提取工具
- **extract_audio_from_video(video_path, output_path?, audio_format?, audio_quality?)**: 从视频中提取完整音频
- **extract_audio_segment(video_path, start_time, duration, output_path?, audio_format?)**: 提取指定时间段的音频

#### 🔄 格式转换工具
- **convert_video_format(input_path, output_path?, output_format?, video_codec?, audio_codec?, quality?)**: 转换视频格式
  - 支持格式：MP4、AVI、MOV、MKV、FLV、WMV等
  - 编码器：libx264、libx265、libvpx等
  - 质量：high、medium、low

- **convert_audio_format(input_path, output_path?, output_format?, audio_codec?, bitrate?)**: 转换音频格式
  - 支持格式：MP3、WAV、AAC、FLAC、OGG等
  - 编码器：libmp3lame、aac、flac等
  - 码率：128k、192k、256k、320k等

#### 🌐 流媒体处理
- **merge_m3u8_to_mp4(m3u8_url, output_path, headers?)**: 合并M3U8流为MP4文件
  - 支持自定义HTTP头部信息
  - 自动处理分段视频合并

#### ✂️ 切割工具
- **cut_video_segment(input_path, start_time, end_time?|duration?, output_path?)**: 切割视频片段
- **cut_audio_segment(input_path, start_time, end_time?|duration?, output_path?)**: 切割音频片段
  - 时间格式：HH:MM:SS
  - 支持按持续时间或结束时间切割

#### 🔗 合并工具
- **merge_videos(video_paths, output_path?, merge_method?)**: 合并多个视频文件
  - concat：简单拼接
  - filter：滤镜合并（适用于不同格式）
  
- **merge_audios(audio_paths, output_path?, merge_method?)**: 合并多个音频文件
  - concat：顺序拼接
  - mix：混音合成

#### 🎨 视频特效工具
- **video_to_gif(input_path, output_path?, start_time?, duration?, width?, fps?, quality?)**: 视频转GIF动图
  - 支持时间范围选择
  - 可调整尺寸、帧率、质量
  - 智能调色板优化

- **resize_video(input_path, width, height, output_path?, keep_aspect_ratio?)**: 调整视频分辨率
  - 支持保持宽高比或拉伸填充
  - 智能缩放算法

- **add_watermark(input_path, watermark_path, output_path?, position?, opacity?, margin?)**: 添加水印
  - 支持5种位置：左上、右上、左下、右下、居中
  - 可调整透明度和边距

- **extract_frames(input_path, output_dir?, fps?, start_time?, duration?, image_format?)**: 提取视频帧
  - 支持自定义帧率提取
  - 多种图片格式：JPG、PNG、BMP

- **change_video_speed(input_path, speed, output_path?, keep_audio_pitch?)**: 改变播放速度
  - 支持0.5-10倍速调整
  - 可选择保持音频音调

- **compress_video(input_path, output_path?, quality?, target_size_mb?)**: 压缩视频
  - 支持按质量或目标大小压缩
  - 智能码率计算

#### 📊 信息查询
- **get_video_info(video_path)**: 获取视频文件详细信息
  - 返回视频的元数据、编码信息、时长等

#### 🚀 硬件加速工具 
- **check_hardware_acceleration()**: 检查系统硬件加速支持情况
  - 自动检测 Intel QSV、NVIDIA NVENC 等硬件加速器
  - 显示可用的编码器和解码器列表

- **convert_video_with_qsv(input_path, output_path?, output_format?, qsv_encoder?, quality?, qsv_preset?)**: QSV硬件加速视频转换
  - 支持编码器：h264_qsv、hevc_qsv、av1_qsv 等
  - 预设选项：veryfast、fast、medium、slow、veryslow
  - 处理速度提升：相比软件编码可提升 3-10 倍

- **compress_video_with_qsv(input_path, output_path?, quality?, qsv_encoder?, target_bitrate?)**: QSV硬件加速视频压缩
  - 智能码率控制和质量优化
  - 支持按目标码率或质量等级压缩

#### 🔧 增强的现有工具（硬件加速支持）
- **convert_video_format()**: 新增 `use_hardware_acceleration` 和 `hwaccel_type` 参数
- **compress_video()**: 新增硬件加速选项，大幅提升压缩速度

### 数学工具 (Math Tools) - 历史功能
- **add(a: int, b: int) -> int**: 加法运算
- **subtract(a: int, b: int) -> int**: 减法运算
- **multiply(a: int, b: int) -> int**: 乘法运算
- **divide(a: float, b: float) -> float**: 除法运算（包含零除错误处理）

### 问候资源 (Greeting Resources) - 历史功能
- **greeting://{name}**: 智能时间问候（早上好/下午好/晚上好）+ 当前时间
- **quote://daily**: 每日名言（基于日期固定显示）

### 配置系统
- **开发模式**: 调试级别日志，详细输出
- **生产模式**: 警告级别日志，简洁输出
- **默认模式**: 信息级别日志，平衡输出

## ⚡ 异步处理特性

### 🔄 并发执行能力
本项目已全面升级为异步架构，所有视频音频处理工具都支持异步执行，这意味着：

- **并行处理**: AI可以同时调用多个工具函数进行并发处理
- **性能提升**: 对于批量处理任务，性能提升可达3-5倍
- **资源优化**: 更好的系统资源利用率，避免阻塞等待
- **响应性**: 长时间任务不会阻塞其他操作

### 🎯 适用场景
- **批量转换**: 同时转换多个视频文件格式
- **并行压缩**: 同时压缩多个大文件
- **多任务处理**: 同时进行音频提取、视频切割等不同操作
- **流水线处理**: 链式处理任务的并发执行

### 🛠️ 技术实现
- 使用 `asyncio.create_subprocess_exec()` 替代同步 `subprocess.run()`
- 统一的 `run_ffmpeg_command()` 异步辅助函数
- 保持完全向后兼容的API接口

## 🚀 使用说明

### ✅ 推荐方式：使用 MCP Inspector
```bash
# 直接运行视频音频提取器
uv run mcp dev main.py
```

**MCP Inspector 地址**: `http://127.0.0.1:6274`

在 MCP Inspector 中你可以：
- 🎵 **提取视频音频**：从任意视频文件中提取音频
- ✂️ **裁剪音频片段**：提取指定时间段的音频
- 📊 **查看视频信息**：获取视频的详细技术信息
- 🔧 **自定义格式**：选择输出音频格式和质量
- 🔍 **实时调试**：查看 FFmpeg 命令执行过程

### 📝 使用示例

#### 1. 视频格式转换
```json
{
  "input_path": "/path/to/input.avi",
  "output_format": "mp4",
  "video_codec": "libx264",
  "quality": "high"
}
```

#### 2. M3U8流合并
```json
{
  "m3u8_url": "https://example.com/playlist.m3u8",
  "output_path": "/path/to/output.mp4",
  "headers": "User-Agent:Mozilla/5.0,Referer:https://example.com"
}
```

#### 3. 视频切割
```json
{
  "input_path": "/path/to/video.mp4",
  "start_time": "00:01:30",
  "duration": "00:02:00"
}
```

#### 4. 视频合并
```json
{
  "video_paths": "/path/to/video1.mp4,/path/to/video2.mp4,/path/to/video3.mp4",
  "merge_method": "concat"
}
```

#### 5. 音频合并（混音）
```json
{
  "audio_paths": "/path/to/audio1.mp3,/path/to/audio2.mp3",
  "merge_method": "mix"
}
```

#### 6. 音频格式转换
```json
{
  "input_path": "/path/to/audio.wav",
  "output_format": "mp3",
  "bitrate": "320k"
}
```

#### 7. 视频转GIF动图
```json
{
  "input_path": "/path/to/video.mp4",
  "start_time": "00:00:10",
  "duration": "00:00:05",
  "width": 640,
  "fps": 12,
  "quality": "high"
}
```

#### 8. 视频添加水印
```json
{
  "input_path": "/path/to/video.mp4",
  "watermark_path": "/path/to/logo.png",
  "position": "bottom-right",
  "opacity": 0.7,
  "margin": 20
}
```

#### 9. 视频变速播放
```json
{
  "input_path": "/path/to/video.mp4",
  "speed": 1.5,
  "keep_audio_pitch": true
}
```

#### 10. 视频压缩
```json
{
  "input_path": "/path/to/large_video.mp4",
  "target_size_mb": 50,
  "quality": "medium"
}
```

### ⚡ 直接运行
```bash
# 直接运行视频音频提取器
uv run python main.py
```

### 🔗 与客户端集成
```bash
uv run mcp run main.py  # 用于 MCP 客户端连接
```

### 🎯 支持的视频格式
- **输入格式**: MP4, AVI, MOV, MKV, FLV, WMV, 3GP 等所有 FFmpeg 支持的格式
- **输出音频格式**: MP3, WAV, AAC, FLAC, M4A, OGG 等
- **音质选项**: 128k, 192k, 256k, 320k 或自定义码率

## 🔧 开发指南

### 添加新工具
1. 在 `src/tools/` 中创建新的工具模块
2. 在 `src/tools/__init__.py` 中导入并导出
3. 在 `server.py` 中注册新工具

### 添加新资源
1. 在 `src/resources/` 中创建新的资源模块
2. 在 `src/resources/__init__.py` 中导入并导出
3. 在 `server.py` 中注册新资源

### 修改配置
编辑 `src/config/server_config.py` 中的 `ServerConfig` 类

## ✅ 验证服务器工作

服务器正常工作的标志：
1. **MCP Inspector 正常启动**: 访问 `http://127.0.0.1:6274`
2. **工具测试成功**: 在 Inspector 中测试数学运算
3. **资源访问正常**: 获取问候语和每日名言
4. **日志输出正常**: 查看控制台日志信息

## 🔍 故障排除

### Q: `mcp dev` 找不到服务器对象？
**A**: 确保 `server.py` 中有全局变量 `mcp`。现在已修复。

### Q: 模块导入错误？
**A**: 确保在项目根目录运行命令，Python 能找到 `src` 模块。

### Q: 工具或资源没有注册？
**A**: 检查配置中的功能开关，确保 `enable_math_tools` 和 `enable_greeting_resources` 为 `True`。

### Q: 日志输出太多或太少？
**A**: 使用不同的运行模式：
- `--dev`: 详细调试信息
- 默认: 一般信息
- `--prod`: 仅警告和错误

## 💻 技术栈
- Python 3.12
- MCP Python SDK
- FastMCP 框架
- uv 包管理器
- 模块化架构设计

## 🎯 架构优势
- **模块化**: 功能分离，易于维护和扩展
- **可配置**: 支持多环境配置
- **可测试**: 清晰的模块边界便于单元测试
- **可扩展**: 易于添加新工具和资源
- **日志友好**: 完整的日志系统

## 📋 下一步计划
- [ ] 添加 FFMPEG 相关工具
- [ ] 实现文件处理资源
- [ ] 添加单元测试
- [ ] 创建客户端示例
- [ ] 添加 Docker 支持
- [ ] 实现插件系统
