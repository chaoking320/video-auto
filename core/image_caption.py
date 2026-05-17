#!/usr/bin/env python3
"""
图片文字叠加工具
在视频截图或任意图片上添加标题、副标题等文字

功能：
- 支持主标题（大字醒目）
- 支持副标题（小字红色）
- 支持自定义文字位置
- 支持文字样式（描边、阴影、渐变）
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
from typing import Tuple, List, Optional


class CaptionTool:
    """图片字幕叠加工具"""

    def __init__(self):
        self.font_cache = {}

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """获取字体，支持缓存"""
        key = f"{size}_{bold}"
        if key not in self.font_cache:
            font_paths = [
                "C:/Windows/Fonts/simhei.ttf",      # 黑体
                "C:/Windows/Fonts/simsun.ttc",      # 宋体
                "C:/Windows/Fonts/simkai.ttf",      # 楷体
                "C:/Windows/Fonts/msyh.ttc",        # 微软雅黑
                "C:/Windows/Fonts/arial.ttf",       # Arial
            ]
            font = None
            for fp in font_paths:
                try:
                    if os.path.exists(fp):
                        font = ImageFont.truetype(fp, size)
                        break
                except:
                    continue
            if font is None:
                font = ImageFont.load_default()
            self.font_cache[key] = font
        return self.font_cache[key]

    def _text_size(self, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
        """获取文字尺寸"""
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont,
                   max_width: int) -> List[str]:
        """自动换行"""
        if not text:
            return []
        lines = []
        current = ""
        for char in text:
            test = current + char
            w, h = self._text_size(test, font)
            if w > max_width and current:
                lines.append(current)
                current = char
            else:
                current = test
        if current:
            lines.append(current)
        return lines if lines else [text]

    def add_title(self, image_path: str, output_path: str,
                  title: str,
                  title_size: int = 100,
                  title_color: Tuple[int, int, int] = (255, 255, 255),
                  title_pos: str = "center",  # center, top, bottom
                  title_offset_y: int = 0,
                  stroke_color: Tuple[int, int, int] = (0, 0, 0),
                  stroke_width: int = 3,
                  shadow: bool = True,
                  shadow_offset: int = 5) -> str:
        """在图片上添加主标题

        Args:
            image_path: 输入图片路径（可以是视频截图）
            output_path: 输出图片路径
            title: 主标题文字
            title_size: 标题字体大小
            title_color: 标题颜色 (R, G, B)
            title_pos: 标题位置 (center/top/bottom)
            title_offset_y: Y轴偏移量（正值向下）
            stroke_color: 描边颜色
            stroke_width: 描边宽度
            shadow: 是否添加阴影
            shadow_offset: 阴影偏移量
        """
        # 加载图片
        img = Image.open(image_path).convert("RGB")
        W, H = img.size

        # 计算最大可用宽度（留边距）
        max_width = int(W * 0.9)

        # 缩放字体以适应图片宽度
        font_size = title_size
        font = self._get_font(font_size)
        lines = self._wrap_text(title, font, max_width)

        # 如果文字太宽，自动缩小
        while lines and self._text_size(max(lines, key=lambda x: self._text_size(x, font)[0]), font)[0] > max_width and font_size > 30:
            font_size -= 5
            font = self._get_font(font_size)
            lines = self._wrap_text(title, font, max_width)

        draw = ImageDraw.Draw(img)

        # 计算标题区域高度
        line_height = self._text_size("中", font)[1]
        total_height = len(lines) * int(line_height * 1.3)

        # 根据位置计算Y坐标
        if title_pos == "center":
            title_y = (H - total_height) // 2 + title_offset_y
        elif title_pos == "bottom":
            title_y = H - total_height - 150 + title_offset_y
        else:  # top
            title_y = 100 + title_offset_y

        # 绘制每一行
        for i, line in enumerate(lines):
            line_w, line_h = self._text_size(line, font)
            x = (W - line_w) // 2
            y = int(title_y + i * line_height * 1.3)

            # 绘制阴影
            if shadow:
                for offset in range(1, shadow_offset + 1):
                    draw.text((x + offset, y + offset), line,
                             font=font, fill=(0, 0, 0, 100))

            # 绘制描边
            if stroke_width > 0:
                for dx in range(-stroke_width, stroke_width + 1):
                    for dy in range(-stroke_width, stroke_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), line,
                                     font=font, fill=stroke_color)

            # 绘制主文字
            draw.text((x, y), line, font=font, fill=title_color)

        img.save(output_path, "JPEG", quality=95)
        print(f"[OK] 主标题已添加: {output_path}")
        return output_path

    def add_subtitle(self, image_path: str, output_path: str,
                     subtitle: str,
                     subtitle_size: int = 60,
                     subtitle_color: Tuple[int, int, int] = (220, 30, 30),
                     subtitle_pos: str = "below_title",
                     subtitle_offset_y: int = 0) -> str:
        """在图片上添加副标题

        Args:
            subtitle_pos: 位置 (below_title/center/bottom)
        """
        img = Image.open(image_path).convert("RGB")
        W, H = img.size
        draw = ImageDraw.Draw(img)

        font = self._get_font(subtitle_size)
        lines = self._wrap_text(subtitle, font, int(W * 0.9))

        line_h = self._text_size("中", font)[1]

        if subtitle_pos == "below_title":
            # 位于画面下半部分
            start_y = int(H * 0.65) + subtitle_offset_y
        elif subtitle_pos == "center":
            start_y = (H - len(lines) * line_h) // 2 + subtitle_offset_y
        else:  # bottom
            start_y = H - 200 + subtitle_offset_y

        for i, line in enumerate(lines):
            lw, lh = self._text_size(line, font)
            x = (W - lw) // 2
            y = int(start_y + i * line_h * 1.3)

            # 描边
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line,
                                 font=font, fill=(0, 0, 0))
            # 主文字
            draw.text((x, y), line, font=font, fill=subtitle_color)

        img.save(output_path, "JPEG", quality=95)
        print(f"[OK] 副标题已添加: {output_path}")
        return output_path

    def add_overlay(self, image_path: str, output_path: str,
                    title: str = "",
                    subtitle: str = "",
                    overlay_opacity: int = 100,
                    **kwargs) -> str:
        """组合封面：在图片上添加遮罩 + 主标题 + 副标题

        Args:
            image_path: 输入图片
            output_path: 输出图片
            title: 主标题
            subtitle: 副标题
            overlay_opacity: 暗化遮罩透明度 (0-255)
        """
        img = Image.open(image_path).convert("RGB")
        W, H = img.size

        # 添加暗化遮罩
        if overlay_opacity > 0:
            overlay = Image.new("RGBA", (W, H), (0, 0, 0, overlay_opacity))
            img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

        draw = ImageDraw.Draw(img)
        max_width = int(W * 0.9)

        # 绘制主标题
        if title:
            title_size = int(min(W, H) * 0.08)  # 根据图片大小自动缩放
            font = self._get_font(title_size)
            lines = self._wrap_text(title, font, max_width)

            # 缩小直到合适
            while lines and self._text_size(max(lines, key=lambda x: self._text_size(x, font)[0]), font)[0] > max_width and title_size > 30:
                title_size -= 5
                font = self._get_font(title_size)
                lines = self._wrap_text(title, font, max_width)

            line_h = self._text_size("中", font)[1]
            total_h = len(lines) * int(line_h * 1.3)
            start_y = (H - total_h) // 2 - 50

            for i, line in enumerate(lines):
                lw, lh = self._text_size(line, font)
                x = (W - lw) // 2
                y = int(start_y + i * line_h * 1.3)

                # 阴影
                for offset in range(1, 8):
                    draw.text((x + offset, y + offset), line,
                             font=font, fill=(0, 0, 0, 100))
                # 白色文字
                draw.text((x, y), line, font=font, fill=(255, 255, 255))

        # 绘制副标题
        if subtitle:
            sub_size = int(min(W, H) * 0.05)
            sub_font = self._get_font(sub_size)
            sub_lines = self._wrap_text(subtitle, sub_font, max_width)

            sub_h = self._text_size("中", sub_font)[1]
            sub_start_y = (H // 2) + 50

            for i, line in enumerate(sub_lines):
                lw, lh = self._text_size(line, sub_font)
                x = (W - lw) // 2
                y = int(sub_start_y + i * sub_h * 1.3)

                # 红色描边
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), line,
                                     font=sub_font, fill=(0, 0, 0))
                # 红色文字
                draw.text((x, y), line, font=sub_font, fill=(220, 30, 30))

        img.save(output_path, "JPEG", quality=95)
        print(f"[OK] 封面生成: {output_path}")
        return output_path


# ═══════════════════════════════════════════════════════
# 命令行入口
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="图片文字叠加工具")
    parser.add_argument("input", help="输入图片（可以是视频截图）")
    parser.add_argument("output", help="输出图片")
    parser.add_argument("--title", help="主标题")
    parser.add_argument("--subtitle", help="副标题")
    parser.add_argument("--title-size", type=int, default=100, help="标题字体大小")
    parser.add_argument("--title-color", default="255,255,255", help="标题颜色 R,G,B")
    parser.add_argument("--subtitle-color", default="220,30,30", help="副标题颜色 R,G,B")
    parser.add_argument("--title-pos", default="center", choices=["center", "top", "bottom"],
                       help="标题位置")
    parser.add_argument("--overlay", type=int, default=100, help="暗化遮罩透明度 (0-255)")

    args = parser.parse_args()

    tool = CaptionTool()

    # 解析颜色
    title_color = tuple(map(int, args.title_color.split(",")))
    subtitle_color = tuple(map(int, args.subtitle_color.split(",")))

    # 如果同时有标题和副标题，使用组合模式
    if args.title and args.subtitle:
        tool.add_overlay(
            args.input, args.output,
            title=args.title,
            subtitle=args.subtitle,
            overlay_opacity=args.overlay
        )
    elif args.title:
        tool.add_title(
            args.input, args.output,
            title=args.title,
            title_size=args.title_size,
            title_color=title_color,
            title_pos=args.title_pos
        )
    elif args.subtitle:
        tool.add_subtitle(
            args.input, args.output,
            subtitle=args.subtitle,
            subtitle_color=subtitle_color
        )
    else:
        print("请指定 --title 或 --subtitle")
