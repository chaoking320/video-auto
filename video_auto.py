#!/usr/bin/env python3
"""
video-auto: 视频自动化处理工具箱
一键完成视频预处理工作

用法:
    python video_auto.py [命令] [选项]

命令:
    info        查看视频信息
    convert     格式转换
    compress    压缩视频
    portrait    横屏转竖屏
    resize      调整尺寸
    crop        裁剪画面
    trim        截取片段
    speed       调整速度
    watermark   添加水印
    concat      拼接视频
    screenshot  截图
    preset      应用平台预设

示例:
    python video_auto.py info input.mp4
    python video_auto.py portrait input.mp4 output.mp4
    python video_auto.py preset input.mp4 output.mp4 --preset douyin
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ffmpeg_utils import FFmpegRunner


def print_usage():
    print(__doc__)
    print("\n详细命令帮助：")
    print("  python video_auto.py <command> --help")


def cmd_info(args):
    if len(args) < 1:
        print("用法: info <视频文件>")
        return

    runner = FFmpegRunner()
    info = runner.get_info(args[0])

    print("=" * 50)
    print("视频信息")
    print("=" * 50)

    format_info = info.get("format", {})
    print(f"文件名: {format_info.get('filename', 'N/A')}")
    print(f"格式: {format_info.get('format_name', 'N/A')}")
    print(f"时长: {float(format_info.get('duration', 0)):.2f} 秒")
    print(f"文件大小: {int(format_info.get('size', 0)) / (1024*1024):.2f} MB")
    print(f"码率: {int(format_info.get('bit_rate', 0)) / 1000:.0f} kbps")

    print()
    for stream in info.get("streams", []):
        codec_type = stream.get("codec_type", "unknown")
        if codec_type == "video":
            print(f"视频流:")
            print(f"  编码: {stream.get('codec_name', 'N/A')}")
            print(f"  分辨率: {stream.get('width', 0)}x{stream.get('height', 0)}")
            fps = stream.get("r_frame_rate", "0/1")
            if "/" in fps:
                num, den = fps.split("/")
                fps = float(num) / float(den) if float(den) != 0 else 0
            print(f"  帧率: {fps:.2f} fps")
            print(f"  像素格式: {stream.get('pix_fmt', 'N/A')}")
        elif codec_type == "audio":
            print(f"音频流:")
            print(f"  编码: {stream.get('codec_name', 'N/A')}")
            print(f"  采样率: {stream.get('sample_rate', 'N/A')} Hz")
            print(f"  声道: {stream.get('channels', 0)}")
            print(f"  码率: {stream.get('bit_rate', 'N/A')} bps")
    print("=" * 50)


def cmd_convert(args):
    if len(args) < 2:
        print("用法: convert <输入文件> <输出文件> [--codec copy]")
        return

    input_path, output_path = args[0], args[1]
    codec = "copy"
    if "--codec" in args:
        idx = args.index("--codec")
        if idx + 1 < len(args):
            codec = args[idx + 1]

    runner = FFmpegRunner()
    runner.convert(input_path, output_path, codec)
    print(f"转换完成: {output_path}")


def cmd_compress(args):
    if len(args) < 2:
        print("用法: compress <输入文件> <输出文件> [--crf 23] [--preset medium]")
        return

    input_path, output_path = args[0], args[1]
    crf, preset = 23, "medium"

    if "--crf" in args:
        idx = args.index("--crf")
        if idx + 1 < len(args):
            crf = int(args[idx + 1])
    if "--preset" in args:
        idx = args.index("--preset")
        if idx + 1 < len(args):
            preset = args[idx + 1]

    runner = FFmpegRunner()
    runner.compress(input_path, output_path, crf=crf, preset=preset)
    print(f"压缩完成: {output_path}")


def cmd_portrait(args):
    if len(args) < 2:
        print("用法: portrait <输入文件> <输出文件> [--w 1080] [--h 1920]")
        return

    input_path, output_path = args[0], args[1]
    w, h = 1080, 1920

    if "--w" in args:
        idx = args.index("--w")
        if idx + 1 < len(args):
            w = int(args[idx + 1])
    if "--h" in args:
        idx = args.index("--h")
        if idx + 1 < len(args):
            h = int(args[idx + 1])

    runner = FFmpegRunner()
    runner.to_portrait(input_path, output_path, target_w=w, target_h=h)
    print(f"横屏转竖屏完成: {output_path}")


def cmd_resize(args):
    if len(args) < 2:
        print("用法: resize <输入文件> <输出文件> [--w 1920] [--h 1080]")
        return

    input_path, output_path = args[0], args[1]
    w, h = None, None

    if "--w" in args:
        idx = args.index("--w")
        if idx + 1 < len(args):
            w = int(args[idx + 1])
    if "--h" in args:
        idx = args.index("--h")
        if idx + 1 < len(args):
            h = int(args[idx + 1])

    if w is None and h is None:
        print("错误: 至少指定 --w 或 --h")
        return

    runner = FFmpegRunner()
    runner.resize(input_path, output_path, width=w, height=h)
    print(f"尺寸调整完成: {output_path}")


def cmd_crop(args):
    if len(args) < 6:
        print("用法: crop <输入文件> <输出文件> <x> <y> <宽> <高>")
        print("示例: crop input.mp4 output.mp4 100 50 800 600")
        return

    input_path, output_path = args[0], args[1]
    x, y, w, h = int(args[2]), int(args[3]), int(args[4]), int(args[5])

    runner = FFmpegRunner()
    runner.crop(input_path, output_path, x, y, w, h)
    print(f"裁剪完成: {output_path}")


def cmd_trim(args):
    if len(args) < 2:
        print("用法: trim <输入文件> <输出文件> --start 00:00:10 [--duration 30|--end 00:00:40]")
        return

    input_path, output_path = args[0], args[1]
    start = "0"
    duration = None
    end = None

    if "--start" in args:
        idx = args.index("--start")
        if idx + 1 < len(args):
            start = args[idx + 1]
    if "--duration" in args:
        idx = args.index("--duration")
        if idx + 1 < len(args):
            duration = args[idx + 1]
    if "--end" in args:
        idx = args.index("--end")
        if idx + 1 < len(args):
            end = args[idx + 1]

    runner = FFmpegRunner()
    runner.trim(input_path, output_path, start=start, duration=duration, end=end)
    print(f"截取完成: {output_path}")


def cmd_speed(args):
    if len(args) < 3:
        print("用法: speed <输入文件> <输出文件> <倍数>")
        print("示例: speed input.mp4 output.mp4 2.0")
        return

    input_path, output_path = args[0], args[1]
    speed = float(args[2])

    runner = FFmpegRunner()
    runner.speed(input_path, output_path, speed=speed)
    print(f"速度调整完成: {output_path}")


def cmd_watermark(args):
    if len(args) < 3:
        print("用法: watermark <输入文件> <水印文件> <输出文件> [--position bottom-right] [--scale 1.0]")
        print("位置选项: top-left, top-right, bottom-left, bottom-right, center")
        return

    input_path, wm_path, output_path = args[0], args[1], args[2]
    position = "bottom-right"
    scale = 1.0

    if "--position" in args:
        idx = args.index("--position")
        if idx + 1 < len(args):
            position = args[idx + 1]
    if "--scale" in args:
        idx = args.index("--scale")
        if idx + 1 < len(args):
            scale = float(args[idx + 1])

    runner = FFmpegRunner()
    runner.add_watermark(input_path, wm_path, output_path, position=position, scale=scale)
    print(f"水印添加完成: {output_path}")


def cmd_concat(args):
    if len(args) < 3:
        print("用法: concat <输出文件> <视频1> <视频2> [视频3...]")
        return

    output_path = args[0]
    video_paths = args[1:]

    runner = FFmpegRunner()
    runner.concat_videos(video_paths, output_path)
    print(f"拼接完成: {output_path}")


def cmd_screenshot(args):
    if len(args) < 2:
        print("用法: screenshot <输入文件> <输出图片> [--time 00:00:01]")
        return

    input_path, output_path = args[0], args[1]
    timestamp = "00:00:01"

    if "--time" in args:
        idx = args.index("--time")
        if idx + 1 < len(args):
            timestamp = args[idx + 1]

    runner = FFmpegRunner()
    runner.screenshot(input_path, output_path, timestamp=timestamp)
    print(f"截图完成: {output_path}")


def cmd_preset(args):
    if len(args) < 3:
        print("用法: preset <输入文件> <输出文件> --preset <预设名>")
        print("可用预设: douyin, xiaohongshu, videohao")
        return

    input_path, output_path = args[0], args[1]
    preset_name = None

    if "--preset" in args:
        idx = args.index("--preset")
        if idx + 1 < len(args):
            preset_name = args[idx + 1]

    if not preset_name:
        print("错误: 必须指定 --preset")
        return

    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    preset_dir = os.path.join(script_dir, "presets")

    runner = FFmpegRunner()
    runner.apply_preset(input_path, output_path, preset_name, preset_dir=preset_dir)
    print(f"预设应用完成: {output_path}")


COMMANDS = {
    "info": cmd_info,
    "convert": cmd_convert,
    "compress": cmd_compress,
    "portrait": cmd_portrait,
    "resize": cmd_resize,
    "crop": cmd_crop,
    "trim": cmd_trim,
    "speed": cmd_speed,
    "watermark": cmd_watermark,
    "concat": cmd_concat,
    "screenshot": cmd_screenshot,
    "preset": cmd_preset,
}


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    if command in ["-h", "--help", "help"]:
        print_usage()
        return

    if command not in COMMANDS:
        print(f"未知命令: {command}")
        print("可用命令:", ", ".join(COMMANDS.keys()))
        return

    COMMANDS[command](args)


if __name__ == "__main__":
    main()
