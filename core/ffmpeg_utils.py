"""
FFmpeg 核心工具封装
封装常用的视频处理命令，提供简单易用的 Python API
"""

import subprocess
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any


class FFmpegRunner:
    """FFmpeg 命令执行器"""

    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe"):
        self.ffmpeg = ffmpeg_path
        self.ffprobe = ffprobe_path

    def _run(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """执行 FFmpeg 命令"""
        cmd = [self.ffmpeg] + args
        print(f"[CMD] {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if check and result.returncode != 0:
            print(f"[ERROR] {result.stderr}")
            raise RuntimeError(f"FFmpeg 执行失败: {result.stderr[:200]}")
        return result

    def get_info(self, input_path: str) -> Dict[str, Any]:
        """获取视频信息"""
        cmd = [
            self.ffprobe,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            input_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            raise RuntimeError(f"无法读取视频信息: {result.stderr}")
        return json.loads(result.stdout)

    def convert(self, input_path: str, output_path: str, codec: str = "copy") -> str:
        """格式转换"""
        args = ["-i", input_path, "-c", codec]
        if codec == "copy":
            # 保持原始编码，仅封装格式改变
            args += ["-y", output_path]
        else:
            args += ["-y", output_path]
        self._run(args)
        return output_path

    def compress(self, input_path: str, output_path: str,
                 crf: int = 23, preset: str = "medium") -> str:
        """压缩视频

        参数:
            crf: 质量 (0-51, 越小越好, 默认23)
            preset: 编码速度 (ultrafast~veryslow, 默认medium)
        """
        args = [
            "-i", input_path,
            "-c:v", "libx264",
            "-crf", str(crf),
            "-preset", preset,
            "-c:a", "aac",
            "-b:a", "128k",
            "-y", output_path
        ]
        self._run(args)
        return output_path

    def resize(self, input_path: str, output_path: str,
               width: Optional[int] = None, height: Optional[int] = None) -> str:
        """调整尺寸

        如果只给宽或高，会自动按比例缩放
        """
        if width and height:
            scale = f"scale={width}:{height}"
        elif width:
            scale = f"scale={width}:-2"
        elif height:
            scale = f"scale=-2:{height}"
        else:
            raise ValueError("至少指定 width 或 height")

        args = [
            "-i", input_path,
            "-vf", scale,
            "-c:a", "copy",
            "-y", output_path
        ]
        self._run(args)
        return output_path

    def to_portrait(self, input_path: str, output_path: str,
                    target_w: int = 1080, target_h: int = 1920) -> str:
        """横屏转竖屏 (9:16)

        自动缩放并填充黑边（或裁剪）
        """
        # scale: 等比缩放，保持原始宽高比，不裁剪
        # pad: 如果缩放后不够目标尺寸，填充黑色
        vf = (
            f"scale={target_w}:{target_h}:"
            f"force_original_aspect_ratio=decrease,"
            f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2"
        )
        args = [
            "-i", input_path,
            "-vf", vf,
            "-c:a", "copy",
            "-y", output_path
        ]
        self._run(args)
        return output_path

    def crop(self, input_path: str, output_path: str,
             x: int, y: int, w: int, h: int) -> str:
        """裁剪视频"""
        args = [
            "-i", input_path,
            "-vf", f"crop={w}:{h}:{x}:{y}",
            "-c:a", "copy",
            "-y", output_path
        ]
        self._run(args)
        return output_path

    def trim(self, input_path: str, output_path: str,
             start: str = "0", duration: Optional[str] = None,
             end: Optional[str] = None) -> str:
        """截取片段

        参数:
            start: 开始时间 (如 "00:00:10" 或 "10")
            duration: 持续时长 (如 "00:00:30" 或 "30")
            end: 结束时间（二选一）
        """
        args = ["-ss", start, "-i", input_path]
        if duration:
            args += ["-t", duration]
        elif end:
            args += ["-to", end]
        args += ["-c", "copy", "-y", output_path]
        self._run(args)
        return output_path

    def speed(self, input_path: str, output_path: str,
              speed: float = 1.0) -> str:
        """调整速度

        speed > 1: 加速（如 2.0 表示2倍速）
        speed < 1: 减速（如 0.5 表示0.5倍速）
        """
        if speed <= 0:
            raise ValueError("speed 必须大于0")
        pts = 1.0 / speed
        atempo = speed
        args = [
            "-i", input_path,
            "-vf", f"setpts={pts}*PTS",
            "-af", f"atempo={atempo}",
            "-y", output_path
        ]
        self._run(args)
        return output_path

    def add_watermark(self, input_path: str, watermark_path: str,
                      output_path: str,
                      position: str = "bottom-right",
                      scale: float = 1.0) -> str:
        """添加水印

        position: top-left, top-right, bottom-left, bottom-right, center
        """
        positions = {
            "top-left": "10:10",
            "top-right": "W-w-10:10",
            "bottom-left": "10:H-h-10",
            "bottom-right": "W-w-10:H-h-10",
            "center": "(W-w)/2:(H-h)/2"
        }
        overlay = positions.get(position, positions["bottom-right"])
        vf = f"[1:v]scale=iw*{scale}:ih*{scale}[wm];[0:v][wm]overlay={overlay}"
        args = [
            "-i", input_path,
            "-i", watermark_path,
            "-filter_complex", vf,
            "-c:a", "copy",
            "-y", output_path
        ]
        self._run(args)
        return output_path

    def concat_videos(self, video_paths: List[str], output_path: str) -> str:
        """拼接多个视频（视频格式必须相同）"""
        # 创建临时文件列表
        list_file = output_path + ".concat_list.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for path in video_paths:
                f.write(f"file '{os.path.abspath(path)}'\n")

        try:
            args = [
                "-f", "concat",
                "-safe", "0",
                "-i", list_file,
                "-c", "copy",
                "-y", output_path
            ]
            self._run(args)
        finally:
            if os.path.exists(list_file):
                os.remove(list_file)

        return output_path

    def add_subtitle(self, input_path: str, subtitle_path: str,
                     output_path: str) -> str:
        """烧录字幕到视频"""
        # Windows 路径需要处理反斜杠
        sub_path = subtitle_path.replace("\\", "/").replace(":", "\\:")
        args = [
            "-i", input_path,
            "-vf", f"subtitles='{sub_path}'",
            "-c:a", "copy",
            "-y", output_path
        ]
        self._run(args)
        return output_path

    def screenshot(self, input_path: str, output_path: str,
                   timestamp: str = "00:00:01") -> str:
        """截取视频某一帧"""
        args = [
            "-ss", timestamp,
            "-i", input_path,
            "-vframes", "1",
            "-q:v", "2",
            "-y", output_path
        ]
        self._run(args)
        return output_path

    def apply_preset(self, input_path: str, output_path: str,
                     preset_name: str, preset_dir: str = "presets") -> str:
        """应用平台预设"""
        preset_file = os.path.join(preset_dir, f"{preset_name}.json")
        if not os.path.exists(preset_file):
            raise FileNotFoundError(f"预设不存在: {preset_file}")

        with open(preset_file, "r", encoding="utf-8") as f:
            preset = json.load(f)

        args = ["-i", input_path]

        # 视频编码参数
        video = preset.get("video", {})
        if video.get("codec"):
            args += ["-c:v", video["codec"]]
        if video.get("crf"):
            args += ["-crf", str(video["crf"])]
        if video.get("preset"):
            args += ["-preset", video["preset"]]

        # 分辨率
        if video.get("width") and video.get("height"):
            w, h = video["width"], video["height"]
            vf = (
                f"scale={w}:{h}:"
                f"force_original_aspect_ratio=decrease,"
                f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"
            )
            args += ["-vf", vf]

        # 音频编码
        audio = preset.get("audio", {})
        if audio.get("codec"):
            args += ["-c:a", audio["codec"]]
        if audio.get("bitrate"):
            args += ["-b:a", audio["bitrate"]]

        # 帧率
        if video.get("fps"):
            args += ["-r", str(video["fps"])]

        args += ["-y", output_path]
        self._run(args)
        return output_path
