import httpx
import os
import subprocess
import asyncio
from pathlib import Path
from typing import Optional, List
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("视频音频处理器")


async def run_ffmpeg_command(cmd: List[str]):
    """运行FFmpeg命令的异步辅助函数"""
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return type('Result', (), {
        'returncode': process.returncode,
        'stdout': stdout.decode() if stdout else '',
        'stderr': stderr.decode() if stderr else ''
    })()


async def check_qsv_support():
    """检查系统是否支持Intel QSV硬件加速"""
    try:
        # 检查FFmpeg是否编译了QSV支持
        cmd = ["ffmpeg", "-hide_banner", "-encoders"]
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            qsv_encoders = []
            for line in result.stdout.split('\n'):
                if 'qsv' in line.lower():
                    qsv_encoders.append(line.strip())
            
            return len(qsv_encoders) > 0, qsv_encoders
        return False, []
    except Exception:
        return False, []


@mcp.tool()
async def check_hardware_acceleration() -> str:
    """
    检查系统支持的硬件加速选项
    
    Returns:
        硬件加速支持情况报告
    """
    try:
        # 检查QSV支持
        qsv_supported, qsv_encoders = await check_qsv_support()
        
        # 检查其他硬件加速
        cmd = ["ffmpeg", "-hide_banner", "-hwaccels"]
        result = await run_ffmpeg_command(cmd)
        
        report = "硬件加速支持情况：\n\n"
        
        if result.returncode == 0:
            hwaccels = result.stdout.strip().split('\n')[1:]  # 跳过标题行
            report += "可用的硬件加速器:\n"
            for hwaccel in hwaccels:
                if hwaccel.strip():
                    report += f"  - {hwaccel.strip()}\n"
        
        report += f"\nIntel QSV支持: {'✓ 支持' if qsv_supported else '✗ 不支持'}\n"
        
        if qsv_supported:
            report += "QSV编码器:\n"
            for encoder in qsv_encoders[:5]:  # 只显示前5个
                report += f"  - {encoder}\n"
            if len(qsv_encoders) > 5:
                report += f"  ... 以及其他 {len(qsv_encoders) - 5} 个编码器\n"
        
        # 检查NVIDIA NVENC支持
        cmd_nvenc = ["ffmpeg", "-hide_banner", "-encoders"]
        result_nvenc = await run_ffmpeg_command(cmd_nvenc)
        nvenc_supported = False
        if result_nvenc.returncode == 0:
            nvenc_supported = 'nvenc' in result_nvenc.stdout.lower()
        
        report += f"NVIDIA NVENC支持: {'✓ 支持' if nvenc_supported else '✗ 不支持'}\n"
        
        return report
        
    except Exception as e:
        return f"检查硬件加速时发生错误：{str(e)}"


@mcp.tool()
async def convert_video_with_qsv(
    input_path: str,
    output_path: Optional[str] = None,
    output_format: str = "mp4",
    qsv_encoder: str = "h264_qsv",
    quality: str = "medium",
    qsv_preset: str = "medium"
) -> str:
    """
    使用Intel QSV硬件加速转换视频
    
    Args:
        input_path: 输入视频文件路径
        output_path: 输出视频文件路径（可选）
        output_format: 输出格式（mp4, mkv, avi等）
        qsv_encoder: QSV编码器（h264_qsv, hevc_qsv, av1_qsv等）
        quality: 质量设置（high, medium, low）
        qsv_preset: QSV预设（veryfast, faster, fast, medium, slow, slower, veryslow）
    
    Returns:
        转换结果信息
    """
    try:
        if not os.path.exists(input_path):
            return f"错误：输入文件不存在 - {input_path}"
        
        # 检查QSV支持
        qsv_supported, _ = await check_qsv_support()
        if not qsv_supported:
            return "错误：系统不支持Intel QSV硬件加速"
        
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_qsv.{output_format}")
        
        # 质量设置映射
        quality_map = {
            "high": "18",
            "medium": "23",
            "low": "28"
        }
        global_quality = quality_map.get(quality, "23")
        
        cmd = [
            "ffmpeg",
            "-hwaccel", "qsv",  # 硬件解码加速
            "-i", input_path,
            "-c:v", qsv_encoder,
            "-preset", qsv_preset,
            "-global_quality", global_quality,
            "-c:a", "aac",
            "-y",
            output_path
        ]
        
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            return f"成功使用QSV加速转换视频！\n输入文件: {input_path}\n输出文件: {output_path}\n编码器: {qsv_encoder}\n质量: {quality}\n预设: {qsv_preset}"
        else:
            return f"QSV转换失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def compress_video_with_qsv(
    input_path: str,
    output_path: Optional[str] = None,
    quality: str = "medium",
    qsv_encoder: str = "h264_qsv",
    target_bitrate: Optional[str] = None
) -> str:
    """
    使用Intel QSV硬件加速压缩视频
    
    Args:
        input_path: 输入视频文件路径
        output_path: 输出视频文件路径（可选）
        quality: 压缩质量（high, medium, low）
        qsv_encoder: QSV编码器（h264_qsv, hevc_qsv等）
        target_bitrate: 目标比特率（如"2M", "1000k"）
    
    Returns:
        压缩结果信息
    """
    try:
        if not os.path.exists(input_path):
            return f"错误：输入文件不存在 - {input_path}"
        
        # 检查QSV支持
        qsv_supported, _ = await check_qsv_support()
        if not qsv_supported:
            return "错误：系统不支持Intel QSV硬件加速"
        
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_qsv_compressed.{input_file.suffix[1:]}")
        
        # 获取原文件大小
        original_size_mb = os.path.getsize(input_path) / (1024 * 1024)
        
        cmd = [
            "ffmpeg",
            "-hwaccel", "qsv",
            "-i", input_path,
            "-c:v", qsv_encoder,
            "-preset", "medium"
        ]
        
        if target_bitrate:
            cmd.extend(["-b:v", target_bitrate])
        else:
            # 使用质量设置
            quality_map = {
                "high": "20",
                "medium": "25", 
                "low": "30"
            }
            global_quality = quality_map.get(quality, "25")
            cmd.extend(["-global_quality", global_quality])
        
        cmd.extend([
            "-c:a", "aac",
            "-b:a", "128k",
            "-y",
            output_path
        ])
        
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            # 获取压缩后文件大小
            compressed_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            compression_ratio = (1 - compressed_size_mb / original_size_mb) * 100
            
            return f"成功使用QSV加速压缩视频！\n输入文件: {input_path}\n输出文件: {output_path}\n编码器: {qsv_encoder}\n原始大小: {original_size_mb:.1f}MB\n压缩后大小: {compressed_size_mb:.1f}MB\n压缩率: {compression_ratio:.1f}%\n质量设置: {quality}"
        else:
            return f"QSV压缩失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def extract_audio_from_video(
    video_path: str, 
    output_path: Optional[str] = None,
    audio_format: str = "mp3",
    audio_quality: str = "192k"
) -> str:
    """
    从视频文件中提取音频
    
    Args:
        video_path: 输入视频文件路径
        output_path: 输出音频文件路径（可选，默认与视频同目录）
        audio_format: 音频格式（mp3, wav, aac, flac等）
        audio_quality: 音频质量（如192k, 320k等）
    
    Returns:
        提取结果信息
    """
    try:
        # 检查输入文件是否存在
        if not os.path.exists(video_path):
            return f"错误：视频文件不存在 - {video_path}"
        
        # 生成输出文件路径
        if output_path is None:
            video_file = Path(video_path)
            output_path = str(video_file.parent / f"{video_file.stem}.{audio_format}")
        
        # 构建FFmpeg命令
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vn",  # 不处理视频流
            "-acodec", "libmp3lame" if audio_format == "mp3" else "copy",
            "-ab", audio_quality,
            "-y",  # 覆盖输出文件
            output_path
        ]
        
        # 执行FFmpeg命令
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            return f"成功提取音频！\n输入文件: {video_path}\n输出文件: {output_path}\n格式: {audio_format}\n质量: {audio_quality}"
        else:
            return f"提取失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def get_video_info(video_path: str) -> str:
    """
    获取视频文件信息
    
    Args:
        video_path: 视频文件路径
    
    Returns:
        视频文件详细信息
    """
    try:
        if not os.path.exists(video_path):
            return f"错误：视频文件不存在 - {video_path}"
        
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            return f"视频信息获取成功：\n{result.stdout}"
        else:
            return f"获取视频信息失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def extract_audio_segment(
    video_path: str,
    start_time: str,
    duration: str,
    output_path: Optional[str] = None,
    audio_format: str = "mp3"
) -> str:
    """
    从视频中提取指定时间段的音频
    
    Args:
        video_path: 输入视频文件路径
        start_time: 开始时间（格式：HH:MM:SS）
        duration: 持续时间（格式：HH:MM:SS）
        output_path: 输出音频文件路径（可选）
        audio_format: 音频格式
    
    Returns:
        提取结果信息
    """
    try:
        if not os.path.exists(video_path):
            return f"错误：视频文件不存在 - {video_path}"
        
        if output_path is None:
            video_file = Path(video_path)
            output_path = str(video_file.parent / f"{video_file.stem}_segment.{audio_format}")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-ss", start_time,
            "-t", duration,
            "-vn",
            "-acodec", "libmp3lame" if audio_format == "mp3" else "copy",
            "-y",
            output_path
        ]
        
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            return f"成功提取音频片段！\n输入文件: {video_path}\n输出文件: {output_path}\n开始时间: {start_time}\n持续时间: {duration}"
        else:
            return f"提取失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def convert_video_format(
    input_path: str,
    output_path: Optional[str] = None,
    output_format: str = "mp4",
    video_codec: str = "libx264",
    audio_codec: str = "aac",
    quality: str = "medium",
    use_hardware_acceleration: bool = False,
    hwaccel_type: str = "qsv"
) -> str:
    """
    转换视频格式
    
    Args:
        input_path: 输入视频文件路径
        output_path: 输出视频文件路径（可选）
        output_format: 输出格式（mp4, avi, mov, mkv, flv等）
        video_codec: 视频编码器（libx264, libx265, libvpx, h264_qsv, hevc_qsv等）
        audio_codec: 音频编码器（aac, mp3, ac3等）
        quality: 质量设置（high, medium, low）
        use_hardware_acceleration: 是否使用硬件加速
        hwaccel_type: 硬件加速类型（qsv, nvenc, vaapi等）
    
    Returns:
        转换结果信息
    """
    try:
        if not os.path.exists(input_path):
            return f"错误：输入文件不存在 - {input_path}"
        
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_converted.{output_format}")
        
        cmd = ["ffmpeg"]
        
        # 添加硬件加速
        if use_hardware_acceleration:
            if hwaccel_type == "qsv":
                # 检查QSV支持
                qsv_supported, _ = await check_qsv_support()
                if not qsv_supported:
                    return "错误：系统不支持Intel QSV硬件加速"
                cmd.extend(["-hwaccel", "qsv"])
                # 如果使用软件编码器但启用了硬件加速，自动切换到QSV编码器
                if video_codec == "libx264":
                    video_codec = "h264_qsv"
                elif video_codec == "libx265":
                    video_codec = "hevc_qsv"
            elif hwaccel_type == "nvenc":
                cmd.extend(["-hwaccel", "cuda"])
                if video_codec == "libx264":
                    video_codec = "h264_nvenc"
                elif video_codec == "libx265":
                    video_codec = "hevc_nvenc"
        
        cmd.extend(["-i", input_path, "-c:v", video_codec])
        
        # 质量设置
        if "qsv" in video_codec:
            # QSV编码器使用global_quality
            quality_map = {
                "high": "18",
                "medium": "23", 
                "low": "28"
            }
            global_quality = quality_map.get(quality, "23")
            cmd.extend(["-global_quality", global_quality])
        elif "nvenc" in video_codec:
            # NVENC编码器使用cq
            quality_map = {
                "high": "18",
                "medium": "23", 
                "low": "28"
            }
            cq_value = quality_map.get(quality, "23")
            cmd.extend(["-cq", cq_value])
        else:
            # 软件编码器使用crf
            quality_map = {
                "high": "18",
                "medium": "23", 
                "low": "28"
            }
            crf_value = quality_map.get(quality, "23")
            cmd.extend(["-crf", crf_value])
        
        cmd.extend(["-c:a", audio_codec, "-y", output_path])
        
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            accel_info = f"\n硬件加速: {hwaccel_type.upper()}" if use_hardware_acceleration else ""
            return f"成功转换视频格式！\n输入文件: {input_path}\n输出文件: {output_path}\n格式: {output_format}\n编码器: {video_codec}\n质量: {quality}{accel_info}"
        else:
            return f"转换失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def convert_audio_format(
    input_path: str,
    output_path: Optional[str] = None,
    output_format: str = "mp3",
    audio_codec: str = "libmp3lame",
    bitrate: str = "192k"
) -> str:
    """
    转换音频格式
    
    Args:
        input_path: 输入音频文件路径
        output_path: 输出音频文件路径（可选）
        output_format: 输出格式（mp3, wav, aac, flac, ogg等）
        audio_codec: 音频编码器（libmp3lame, aac, flac等）
        bitrate: 音频码率（128k, 192k, 320k等）
    
    Returns:
        转换结果信息
    """
    try:
        if not os.path.exists(input_path):
            return f"错误：输入文件不存在 - {input_path}"
        
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_converted.{output_format}")
        
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-c:a", audio_codec,
            "-b:a", bitrate,
            "-y",
            output_path
        ]
        
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            return f"成功转换音频格式！\n输入文件: {input_path}\n输出文件: {output_path}\n格式: {output_format}\n码率: {bitrate}"
        else:
            return f"转换失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def merge_m3u8_to_mp4(
    m3u8_url: str,
    output_path: str,
    headers: Optional[str] = None
) -> str:
    """
    合并M3U8流为MP4文件
    
    Args:
        m3u8_url: M3U8播放列表URL
        output_path: 输出MP4文件路径
        headers: 可选的HTTP头部信息（格式：key1:value1,key2:value2）
    
    Returns:
        合并结果信息
    """
    try:
        cmd = ["ffmpeg", "-i", m3u8_url]
        
        # 如果提供了headers，添加到命令中
        if headers:
            header_pairs = headers.split(",")
            for header_pair in header_pairs:
                if ":" in header_pair:
                    cmd.extend(["-headers", header_pair.strip()])
        
        cmd.extend([
            "-c", "copy",
            "-bsf:a", "aac_adtstoasc",
            "-y",
            output_path
        ])
        
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            return f"成功合并M3U8流！\nM3U8 URL: {m3u8_url}\n输出文件: {output_path}"
        else:
            return f"合并失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def cut_video_segment(
    input_path: str,
    start_time: str,
    end_time: Optional[str] = None,
    duration: Optional[str] = None,
    output_path: Optional[str] = None,
    use_hardware_acceleration: bool = False,
    hwaccel_type: str = "qsv",
    precise_cut: bool = False
) -> str:
    """
    切割视频片段
    
    Args:
        input_path: 输入视频文件路径
        start_time: 开始时间（格式：HH:MM:SS）
        end_time: 结束时间（格式：HH:MM:SS，与duration二选一）
        duration: 持续时间（格式：HH:MM:SS，与end_time二选一）
        output_path: 输出视频文件路径（可选）
        use_hardware_acceleration: 是否使用硬件加速（需要重新编码）
        hwaccel_type: 硬件加速类型（qsv, nvenc, vaapi等）
        precise_cut: 是否精确切割（重新编码，速度较慢但更精确）
    
    Returns:
        切割结果信息
    """
    try:
        if not os.path.exists(input_path):
            return f"错误：输入文件不存在 - {input_path}"
        
        if not end_time and not duration:
            return "错误：必须提供end_time或duration中的一个"
        
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_cut.{input_file.suffix[1:]}")
        
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-ss", start_time
        ]
        
        if duration:
            cmd.extend(["-t", duration])
        elif end_time:
            cmd.extend(["-to", end_time])
        
        cmd.extend([
            "-c", "copy",
            "-y",
            output_path
        ])
        
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            time_info = f"开始时间: {start_time}"
            if duration:
                time_info += f", 持续时间: {duration}"
            elif end_time:
                time_info += f", 结束时间: {end_time}"
            
            return f"成功切割视频！\n输入文件: {input_path}\n输出文件: {output_path}\n{time_info}"
        else:
            return f"切割失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def cut_audio_segment(
    input_path: str,
    start_time: str,
    end_time: Optional[str] = None,
    duration: Optional[str] = None,
    output_path: Optional[str] = None
) -> str:
    """
    切割音频片段
    
    Args:
        input_path: 输入音频文件路径
        start_time: 开始时间（格式：HH:MM:SS）
        end_time: 结束时间（格式：HH:MM:SS，与duration二选一）
        duration: 持续时间（格式：HH:MM:SS，与end_time二选一）
        output_path: 输出音频文件路径（可选）
    
    Returns:
        切割结果信息
    """
    try:
        if not os.path.exists(input_path):
            return f"错误：输入文件不存在 - {input_path}"
        
        if not end_time and not duration:
            return "错误：必须提供end_time或duration中的一个"
        
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_cut.{input_file.suffix[1:]}")
        
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-ss", start_time
        ]
        
        if duration:
            cmd.extend(["-t", duration])
        elif end_time:
            cmd.extend(["-to", end_time])
        
        cmd.extend([
            "-c", "copy",
            "-y",
            output_path
        ])
        
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            time_info = f"开始时间: {start_time}"
            if duration:
                time_info += f", 持续时间: {duration}"
            elif end_time:
                time_info += f", 结束时间: {end_time}"
            
            return f"成功切割音频！\n输入文件: {input_path}\n输出文件: {output_path}\n{time_info}"
        else:
            return f"切割失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def merge_videos(
    video_paths: str,
    output_path: Optional[str] = None,
    merge_method: str = "concat"
) -> str:
    """
    合并多个视频文件
    
    Args:
        video_paths: 视频文件路径列表，用逗号分隔
        output_path: 输出视频文件路径（可选）
        merge_method: 合并方式（concat：简单拼接，filter：滤镜合并）
    
    Returns:
        合并结果信息
    """
    try:
        paths = [path.strip() for path in video_paths.split(",")]
        
        # 检查所有输入文件是否存在
        for path in paths:
            if not os.path.exists(path):
                return f"错误：视频文件不存在 - {path}"
        
        if len(paths) < 2:
            return "错误：至少需要两个视频文件进行合并"
        
        if output_path is None:
            first_file = Path(paths[0])
            output_path = str(first_file.parent / f"merged_video.{first_file.suffix[1:]}")
        
        if merge_method == "concat":
            # 创建临时文件列表
            list_file = Path(output_path).parent / "video_list.txt"
            with open(list_file, "w") as f:
                for path in paths:
                    f.write(f"file '{path}'\n")
            
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_file),
                "-c", "copy",
                "-y",
                output_path
            ]
            
            result = await run_ffmpeg_command(cmd)
            
            # 清理临时文件
            list_file.unlink()
            
        else:  # filter方法
            # 构建复杂的filter命令
            inputs = []
            for path in paths:
                inputs.extend(["-i", path])
            
            filter_complex = ""
            for i in range(len(paths)):
                filter_complex += f"[{i}:v][{i}:a]"
            filter_complex += f"concat=n={len(paths)}:v=1:a=1[outv][outa]"
            
            cmd = [
                "ffmpeg"
            ] + inputs + [
                "-filter_complex", filter_complex,
                "-map", "[outv]",
                "-map", "[outa]",
                "-y",
                output_path
            ]
            
            result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            return f"成功合并视频！\n输入文件: {', '.join(paths)}\n输出文件: {output_path}\n合并方式: {merge_method}"
        else:
            return f"合并失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def merge_audios(
    audio_paths: str,
    output_path: Optional[str] = None,
    merge_method: str = "concat"
) -> str:
    """
    合并多个音频文件
    
    Args:
        audio_paths: 音频文件路径列表，用逗号分隔
        output_path: 输出音频文件路径（可选）
        merge_method: 合并方式（concat：拼接，mix：混音）
    
    Returns:
        合并结果信息
    """
    try:
        paths = [path.strip() for path in audio_paths.split(",")]
        
        # 检查所有输入文件是否存在
        for path in paths:
            if not os.path.exists(path):
                return f"错误：音频文件不存在 - {path}"
        
        if len(paths) < 2:
            return "错误：至少需要两个音频文件进行合并"
        
        if output_path is None:
            first_file = Path(paths[0])
            output_path = str(first_file.parent / f"merged_audio.{first_file.suffix[1:]}")
        
        if merge_method == "concat":
            # 创建临时文件列表
            list_file = Path(output_path).parent / "audio_list.txt"
            with open(list_file, "w") as f:
                for path in paths:
                    f.write(f"file '{path}'\n")
            
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_file),
                "-c", "copy",
                "-y",
                output_path
            ]
            
            result = await run_ffmpeg_command(cmd)
            
            # 清理临时文件
            list_file.unlink()
            
        else:  # mix方法
            inputs = []
            for path in paths:
                inputs.extend(["-i", path])
            
            filter_complex = f"amix=inputs={len(paths)}:duration=longest"
            
            cmd = [
                "ffmpeg"
            ] + inputs + [
                "-filter_complex", filter_complex,
                "-y",
                output_path
            ]
            
            result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            return f"成功合并音频！\n输入文件: {', '.join(paths)}\n输出文件: {output_path}\n合并方式: {merge_method}"
        else:
            return f"合并失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def video_to_gif(
    input_path: str,
    output_path: Optional[str] = None,
    start_time: Optional[str] = None,
    duration: Optional[str] = None,
    width: int = 480,
    fps: int = 10,
    quality: str = "medium"
) -> str:
    """
    视频转GIF动图
    
    Args:
        input_path: 输入视频文件路径
        output_path: 输出GIF文件路径（可选）
        start_time: 开始时间（格式：HH:MM:SS，可选）
        duration: 持续时间（格式：HH:MM:SS，可选）
        width: GIF宽度像素（高度自动按比例缩放）
        fps: 帧率（建议5-15）
        quality: 质量设置（high, medium, low）
    
    Returns:
        转换结果信息
    """
    try:
        if not os.path.exists(input_path):
            return f"错误：输入文件不存在 - {input_path}"
        
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}.gif")
        
        # 构建基础命令
        cmd = ["ffmpeg", "-i", input_path]
        
        # 添加时间参数
        if start_time:
            cmd.extend(["-ss", start_time])
        if duration:
            cmd.extend(["-t", duration])
        
        # 质量设置映射
        quality_settings = {
            "high": {"colors": "256", "dither": "bayer:bayer_scale=5"},
            "medium": {"colors": "128", "dither": "bayer:bayer_scale=3"},
            "low": {"colors": "64", "dither": "bayer:bayer_scale=1"}
        }
        
        settings = quality_settings.get(quality, quality_settings["medium"])
        
        # 构建滤镜链
        filter_complex = f"fps={fps},scale={width}:-1:flags=lanczos,palettegen=max_colors={settings['colors']}"
        
        # 第一步：生成调色板
        palette_path = str(Path(output_path).parent / "palette.png")
        cmd_palette = cmd + [
            "-vf", filter_complex,
            "-y", palette_path
        ]
        
        result = await run_ffmpeg_command(cmd_palette)
        if result.returncode != 0:
            return f"调色板生成失败：{result.stderr}"
        
        # 第二步：使用调色板生成GIF
        filter_gif = f"fps={fps},scale={width}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither={settings['dither']}"
        
        cmd_gif = cmd + [
            "-i", palette_path,
            "-filter_complex", filter_gif,
            "-y", output_path
        ]
        
        result = await run_ffmpeg_command(cmd_gif)
        
        # 清理临时调色板文件
        if os.path.exists(palette_path):
            os.remove(palette_path)
        
        if result.returncode == 0:
            time_info = ""
            if start_time or duration:
                time_info = f"\n时间范围: {start_time or '开始'} - {duration or '结束'}"
            
            return f"成功转换为GIF！\n输入文件: {input_path}\n输出文件: {output_path}\n尺寸: {width}px宽\n帧率: {fps}fps\n质量: {quality}{time_info}"
        else:
            return f"GIF转换失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def resize_video(
    input_path: str,
    width: int,
    height: int,
    output_path: Optional[str] = None,
    keep_aspect_ratio: bool = True
) -> str:
    """
    调整视频分辨率
    
    Args:
        input_path: 输入视频文件路径
        width: 目标宽度
        height: 目标高度
        output_path: 输出视频文件路径（可选）
        keep_aspect_ratio: 是否保持宽高比
    
    Returns:
        调整结果信息
    """
    try:
        if not os.path.exists(input_path):
            return f"错误：输入文件不存在 - {input_path}"
        
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_resized.{input_file.suffix[1:]}")
        
        # 构建缩放参数
        if keep_aspect_ratio:
            scale_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease"
        else:
            scale_filter = f"scale={width}:{height}"
        
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vf", scale_filter,
            "-c:a", "copy",
            "-y",
            output_path
        ]
        
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            aspect_info = "（保持宽高比）" if keep_aspect_ratio else "（拉伸填充）"
            return f"成功调整视频分辨率！\n输入文件: {input_path}\n输出文件: {output_path}\n分辨率: {width}x{height}{aspect_info}"
        else:
            return f"分辨率调整失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def add_watermark(
    input_path: str,
    watermark_path: str,
    output_path: Optional[str] = None,
    position: str = "bottom-right",
    opacity: float = 0.8,
    margin: int = 10
) -> str:
    """
    为视频添加水印
    
    Args:
        input_path: 输入视频文件路径
        watermark_path: 水印图片路径
        output_path: 输出视频文件路径（可选）
        position: 水印位置（top-left, top-right, bottom-left, bottom-right, center）
        opacity: 水印透明度（0.0-1.0）
        margin: 水印边距像素
    
    Returns:
        添加结果信息
    """
    try:
        if not os.path.exists(input_path):
            return f"错误：输入视频文件不存在 - {input_path}"
        
        if not os.path.exists(watermark_path):
            return f"错误：水印文件不存在 - {watermark_path}"
        
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_watermarked.{input_file.suffix[1:]}")
        
        # 位置映射
        position_map = {
            "top-left": f"{margin}:{margin}",
            "top-right": f"W-w-{margin}:{margin}",
            "bottom-left": f"{margin}:H-h-{margin}",
            "bottom-right": f"W-w-{margin}:H-h-{margin}",
            "center": "(W-w)/2:(H-h)/2"
        }
        
        overlay_pos = position_map.get(position, position_map["bottom-right"])
        
        # 构建滤镜
        filter_complex = f"[1:v]format=rgba,colorchannelmixer=aa={opacity}[watermark];[0:v][watermark]overlay={overlay_pos}"
        
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-i", watermark_path,
            "-filter_complex", filter_complex,
            "-c:a", "copy",
            "-y",
            output_path
        ]
        
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            return f"成功添加水印！\n输入文件: {input_path}\n水印文件: {watermark_path}\n输出文件: {output_path}\n位置: {position}\n透明度: {opacity}"
        else:
            return f"水印添加失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def extract_frames(
    input_path: str,
    output_dir: Optional[str] = None,
    fps: Optional[float] = None,
    start_time: Optional[str] = None,
    duration: Optional[str] = None,
    image_format: str = "jpg"
) -> str:
    """
    从视频中提取帧图片
    
    Args:
        input_path: 输入视频文件路径
        output_dir: 输出图片目录（可选）
        fps: 提取帧率（如1表示每秒1帧，0.5表示2秒1帧）
        start_time: 开始时间（格式：HH:MM:SS）
        duration: 持续时间（格式：HH:MM:SS）
        image_format: 图片格式（jpg, png, bmp）
    
    Returns:
        提取结果信息
    """
    try:
        if not os.path.exists(input_path):
            return f"错误：输入文件不存在 - {input_path}"
        
        if output_dir is None:
            input_file = Path(input_path)
            output_dir = str(input_file.parent / f"{input_file.stem}_frames")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 构建命令
        cmd = ["ffmpeg", "-i", input_path]
        
        if start_time:
            cmd.extend(["-ss", start_time])
        if duration:
            cmd.extend(["-t", duration])
        
        if fps:
            cmd.extend(["-vf", f"fps={fps}"])
        
        output_pattern = os.path.join(output_dir, f"frame_%04d.{image_format}")
        cmd.extend(["-y", output_pattern])
        
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            # 统计生成的图片数量
            frame_count = len([f for f in os.listdir(output_dir) if f.endswith(f".{image_format}")])
            
            time_info = ""
            if start_time or duration:
                time_info = f"\n时间范围: {start_time or '开始'} - {duration or '结束'}"
            
            fps_info = f"\n提取帧率: {fps}fps" if fps else ""
            
            return f"成功提取视频帧！\n输入文件: {input_path}\n输出目录: {output_dir}\n图片格式: {image_format}\n帧数量: {frame_count}{time_info}{fps_info}"
        else:
            return f"帧提取失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def change_video_speed(
    input_path: str,
    speed: float,
    output_path: Optional[str] = None,
    keep_audio_pitch: bool = True
) -> str:
    """
    改变视频播放速度
    
    Args:
        input_path: 输入视频文件路径
        speed: 播放速度倍数（0.5=半速，1.0=原速，2.0=两倍速）
        output_path: 输出视频文件路径（可选）
        keep_audio_pitch: 是否保持音频音调不变
    
    Returns:
        速度调整结果信息
    """
    try:
        if not os.path.exists(input_path):
            return f"错误：输入文件不存在 - {input_path}"
        
        if speed <= 0:
            return "错误：速度倍数必须大于0"
        
        if output_path is None:
            input_file = Path(input_path)
            speed_str = f"{speed:.1f}x".replace(".", "_")
            output_path = str(input_file.parent / f"{input_file.stem}_speed_{speed_str}.{input_file.suffix[1:]}")
        
        # 构建滤镜
        video_filter = f"setpts={1/speed}*PTS"
        
        if keep_audio_pitch:
            # 使用atempo保持音调，但atempo只支持0.5-100的范围
            if 0.5 <= speed <= 2.0:
                audio_filter = f"atempo={speed}"
            else:
                # 对于极端速度，使用多个atempo串联
                audio_filter = "atempo=2.0" if speed > 2.0 else "atempo=0.5"
                remaining_speed = speed / 2.0 if speed > 2.0 else speed / 0.5
                while remaining_speed > 2.0 or remaining_speed < 0.5:
                    if remaining_speed > 2.0:
                        audio_filter += ",atempo=2.0"
                        remaining_speed /= 2.0
                    else:
                        audio_filter += ",atempo=0.5"
                        remaining_speed /= 0.5
                if remaining_speed != 1.0:
                    audio_filter += f",atempo={remaining_speed}"
        else:
            # 简单的音频速度调整
            audio_filter = f"atempo={speed}"
        
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-filter_complex", f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
            "-map", "[v]",
            "-map", "[a]",
            "-y",
            output_path
        ]
        
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            speed_desc = "加速" if speed > 1.0 else "减速" if speed < 1.0 else "原速"
            pitch_info = "（保持音调）" if keep_audio_pitch else "（音调跟随变化）"
            
            return f"成功调整视频速度！\n输入文件: {input_path}\n输出文件: {output_path}\n速度: {speed}倍 {speed_desc}{pitch_info}"
        else:
            return f"速度调整失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


@mcp.tool()
async def compress_video(
    input_path: str,
    output_path: Optional[str] = None,
    quality: str = "medium",
    target_size_mb: Optional[int] = None,
    use_hardware_acceleration: bool = False,
    hwaccel_type: str = "qsv"
) -> str:
    """
    压缩视频文件
    
    Args:
        input_path: 输入视频文件路径
        output_path: 输出视频文件路径（可选）
        quality: 压缩质量（high, medium, low）
        target_size_mb: 目标文件大小（MB，可选）
        use_hardware_acceleration: 是否使用硬件加速
        hwaccel_type: 硬件加速类型（qsv, nvenc, vaapi等）
    
    Returns:
        压缩结果信息
    """
    try:
        if not os.path.exists(input_path):
            return f"错误：输入文件不存在 - {input_path}"
        
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_compressed.{input_file.suffix[1:]}")
        
        # 获取原文件大小
        original_size_mb = os.path.getsize(input_path) / (1024 * 1024)
        
        cmd = ["ffmpeg"]
        video_codec = "libx264"
        
        # 添加硬件加速
        if use_hardware_acceleration:
            if hwaccel_type == "qsv":
                # 检查QSV支持
                qsv_supported, _ = await check_qsv_support()
                if not qsv_supported:
                    return "错误：系统不支持Intel QSV硬件加速"
                cmd.extend(["-hwaccel", "qsv"])
                video_codec = "h264_qsv"
            elif hwaccel_type == "nvenc":
                cmd.extend(["-hwaccel", "cuda"])
                video_codec = "h264_nvenc"
        
        cmd.extend(["-i", input_path, "-c:v", video_codec, "-preset", "medium"])
        
        if target_size_mb:
            # 根据目标大小计算比特率
            # 获取视频时长
            duration_cmd = [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "csv=p=0", input_path
            ]
            duration_result = await run_ffmpeg_command(duration_cmd)
            
            if duration_result.returncode == 0:
                duration = float(duration_result.stdout.strip())
                target_bitrate = int((target_size_mb * 8 * 1024) / duration)  # kbps
                cmd.extend(["-b:v", f"{target_bitrate}k"])
            else:
                return f"无法获取视频时长：{duration_result.stderr}"
        else:
            # 使用质量设置
            if "qsv" in video_codec:
                # QSV编码器使用global_quality
                quality_map = {
                    "high": "20",
                    "medium": "25",
                    "low": "30"
                }
                global_quality = quality_map.get(quality, "25")
                cmd.extend(["-global_quality", global_quality])
            elif "nvenc" in video_codec:
                # NVENC编码器使用cq
                quality_map = {
                    "high": "20",
                    "medium": "25",
                    "low": "30"
                }
                cq_value = quality_map.get(quality, "25")
                cmd.extend(["-cq", cq_value])
            else:
                # 软件编码器使用crf
                quality_map = {
                    "high": "20",
                    "medium": "25",
                    "low": "30"
                }
                crf_value = quality_map.get(quality, "25")
                cmd.extend(["-crf", crf_value])
        
        cmd.extend(["-c:a", "aac", "-b:a", "128k", "-y", output_path])
        
        result = await run_ffmpeg_command(cmd)
        
        if result.returncode == 0:
            # 获取压缩后文件大小
            compressed_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            compression_ratio = (1 - compressed_size_mb / original_size_mb) * 100
            
            accel_info = f"\n硬件加速: {hwaccel_type.upper()}" if use_hardware_acceleration else ""
            return f"成功压缩视频！\n输入文件: {input_path}\n输出文件: {output_path}\n编码器: {video_codec}\n原始大小: {original_size_mb:.1f}MB\n压缩后大小: {compressed_size_mb:.1f}MB\n压缩率: {compression_ratio:.1f}%\n质量设置: {quality}{accel_info}"
        else:
            return f"视频压缩失败：{result.stderr}"
            
    except Exception as e:
        return f"发生错误：{str(e)}"


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
