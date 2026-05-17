#!/usr/bin/env python3
"""
封面生成器
支持多种封面模板，一键生成带文字效果的专业封面

模板系统：
- 模板1: 口播/对话类（醒目大标题）
- 模板2: IP/教程类（质感渐变+人物）
- 模板3: 极简风（纯色背景+居中文字）
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
import json
from typing import Dict, Optional, Tuple, List
from pathlib import Path


class CoverGenerator:
    """封面生成器"""

    def __init__(self, templates_dir: str = "templates/covers"):
        self.templates_dir = templates_dir
        self.default_font = "arial.ttf"
        self.font_cache = {}

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """获取字体，支持缓存"""
        key = f"{size}_{bold}"
        if key not in self.font_cache:
            # 尝试常见的中文字体
            font_paths = [
                "C:/Windows/Fonts/simhei.ttf",      # 黑体
                "C:/Windows/Fonts/simsun.ttc",      # 宋体
                "C:/Windows/Fonts/simkai.ttf",      # 楷体
                "C:/Windows/Fonts/arial.ttf",        # Arial
                "C:/Windows/Fonts/msyh.ttc",         # 微软雅黑
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

    def _draw_text_with_outline(self, draw: ImageDraw.Draw,
                                text: str, pos: Tuple[int, int],
                                font: ImageFont.FreeTypeFont,
                                fill: Tuple[int, int, int],
                                outline_color: Tuple[int, int, int] = (0, 0, 0),
                                outline_width: int = 3):
        """绘制带描边的文字"""
        x, y = pos
        # 描边
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        # 主文字
        draw.text(pos, text, font=font, fill=fill)

    def _draw_text_with_shadow(self, draw: ImageDraw.Draw,
                               text: str, pos: Tuple[int, int],
                               font: ImageFont.FreeTypeFont,
                               fill: Tuple[int, int, int],
                               shadow_color: Tuple[int, int, int] = (0, 0, 0),
                               shadow_offset: Tuple[int, int] = (3, 3),
                               shadow_blur: int = 5):
        """绘制带阴影的文字"""
        x, y = pos
        sx, sy = shadow_offset
        # 阴影
        for i in range(shadow_blur):
            alpha = int(255 * (1 - i / shadow_blur) * 0.5)
            draw.text((x + sx + i, y + sy + i), text,
                      font=font, fill=shadow_color + (alpha,))
        # 主文字
        draw.text(pos, text, font=font, fill=fill)

    def _create_gradient(self, size: Tuple[int, int],
                         colors: List[Tuple[int, int, int]],
                         direction: str = "vertical") -> Image.Image:
        """创建渐变背景"""
        w, h = size
        base = Image.new("RGB", size, colors[0])
        
        for i, color in enumerate(colors):
            if i == 0:
                continue
            for row in range(h):
                ratio = row / h
                r = int(colors[0][0] * (1 - ratio) + colors[-1][0] * ratio)
                g = int(colors[0][1] * (1 - ratio) + colors[-1][1] * ratio)
                b = int(colors[0][2] * (1 - ratio) + colors[-1][2] * ratio)
                for col in range(w):
                    base.putpixel((col, row), (r, g, b))
            break  # 简化：只处理双色渐变
        return base

    # ═══════════════════════════════════════════════════════
    # 模板1：口播/对话类（醒目大标题）
    # ═══════════════════════════════════════════════════════
    def template_broadcast(self, output_path: str,
                           bg_path: str = "",
                           quote: str = "",
                           title: str = "标题文字",
                           subtitle: str = "",
                           duration: str = "",
                           likes: str = "",
                           **kwargs) -> str:
        """口播类封面模板
        
        布局:
            顶部: 引用语(小字白色)
            中间: 主标题(超大白色粗体,黑影)
            底部: 副标题(红色粗体)
            右下角: 时长 + 点赞
        """
        # 加载背景图
        if bg_path and os.path.exists(bg_path):
            bg = Image.open(bg_path).convert("RGB")
            bg = bg.resize((1080, 1920), Image.LANCZOS)
        else:
            # 纯灰色背景
            bg = Image.new("RGB", (1080, 1920), (50, 50, 50))
        
        # 添加暗化遮罩
        overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 100))
        bg = Image.alpha_composite(bg.convert("RGBA"), overlay)
        
        draw = ImageDraw.Draw(bg)
        
        # 1. 顶部引用语
        if quote:
            quote_font = self._get_font(36)
            quote_w, quote_h = self._text_size(quote, quote_font)
            quote_x = (1080 - quote_w) // 2
            quote_y = 120
            self._draw_text_with_outline(draw, quote, (quote_x, quote_y),
                                        quote_font, fill=(255, 255, 255),
                                        outline_color=(0, 0, 0), outline_width=2)
        
        # 2. 主标题（超大白色，带黑色投影）
        title_font = self._get_font(160)
        # 自动换行处理
        lines = self._wrap_text(title, title_font, 1000)
        
        total_height = len(lines) * 200
        start_y = (1920 - total_height) // 2 - 100
        
        for i, line in enumerate(lines):
            tw, th = self._text_size(line, title_font)
            tx = (1080 - tw) // 2
            ty = start_y + i * 200
            
            # 画黑色投影（多层）
            for offset in range(1, 8):
                draw.text((tx + offset, ty + offset), line,
                         font=title_font, fill=(0, 0, 0, 150))
            # 白色主文字
            draw.text((tx, ty), line, font=title_font, fill=(255, 255, 255))
        
        # 3. 副标题（红色，带黑色描边）
        if subtitle:
            sub_font = self._get_font(180)
            sub_w, sub_h = self._text_size(subtitle, sub_font)
            sub_x = (1080 - sub_w) // 2
            sub_y = start_y + len(lines) * 200 + 20
            self._draw_text_with_outline(draw, subtitle, (sub_x, sub_y),
                                        sub_font, fill=(220, 20, 20),
                                        outline_color=(0, 0, 0), outline_width=4)
        
        # 4. 右下角信息
        info_parts = []
        if duration:
            info_parts.append(duration)
        if likes:
            info_parts.append(f"{likes}")
        
        if info_parts:
            info_text = "    ".join(info_parts)
            info_font = self._get_font(36)
            info_w, info_h = self._text_size(info_text, info_font)
            info_x = 1080 - info_w - 40
            info_y = 1920 - 80
            draw.text((info_x, info_y), info_text, font=info_font, fill=(255, 255, 255))
        
        # 保存
        bg.convert("RGB").save(output_path, "JPEG", quality=95)
        print(f"[OK] 口播类封面生成: {output_path}")
        return output_path

    # ═══════════════════════════════════════════════════════
    # 模板2：IP/教程类（质感渐变+人物）
    # ═══════════════════════════════════════════════════════
    def template_ip(self, output_path: str,
                    person_image: str = "",
                    name: str = "",
                    name_en: str = "",
                    title1: str = "",
                    title2: str = "",
                    title3: str = "",
                    desc_lines: List[str] = None,
                    stats: str = "",
                    gradient_colors: List[Tuple[int, int, int]] = None,
                    **kwargs) -> str:
        """IP类封面模板
        
        布局:
            背景: 渐变 + 横纹
            左上角: 人名 + 英文水印
            左侧: 大标题1+2+3
            左下: 描述文字(多行)
            右下: 统计数据
            右侧: 人物照片
        """
        W, H = 1080, 1920
        
        # 创建渐变背景
        if gradient_colors is None:
            gradient_colors = [(60, 30, 20), (120, 70, 40)]
        
        bg = self._create_gradient((W, H), gradient_colors)
        
        # 添加横纹纹理
        draw = ImageDraw.Draw(bg)
        for i in range(0, H, 4):
            alpha = 20 if i % 8 == 0 else 10
            overlay_color = tuple(min(255, c + alpha) for c in gradient_colors[0])
            draw.line([(0, i), (W, i)], fill=overlay_color, width=1)
        
        # 绘制人物照片（右侧，裁剪为竖向）
        if person_image and os.path.exists(person_image):
            person = Image.open(person_image).convert("RGBA")
            # 裁剪为正方形并缩放
            pw, ph = person.size
            size = min(pw, ph)
            left = (pw - size) // 2
            top = (ph - size) // 2
            person = person.crop((left, top, left + size, top + size))
            person = person.resize((900, 900), Image.LANCZOS)
            
            # 添加淡入边缘（右侧）
            mask = Image.new("L", person.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            for x in range(900):
                for y in range(900):
                    # 左侧渐变透明
                    alpha = int(255 * min(1, x / 400))
                    mask.putpixel((x, y), alpha)
            
            # 放到右侧底部
            pos_x = W - 800
            pos_y = H - 950
            bg.paste(person, (pos_x, pos_y), mask)
        
        # 重新获取 draw
        draw = ImageDraw.Draw(bg)
        
        # 1. 人名（白色大字+金色英文水印）
        name_y = 120
        if name:
            name_font = self._get_font(120)
            # 先画金色底（偏移2px）
            draw.text((52, name_y + 2), name, font=name_font, fill=(180, 140, 80))
            # 白色主文字
            draw.text((50, name_y), name, font=name_font, fill=(255, 255, 255))
            
            # 英文水印
            if name_en:
                en_font = self._get_font(60)
                en_w, en_h = self._text_size(name_en, en_font)
                # 斜体效果（手动偏移）
                for i, ch in enumerate(name_en):
                    draw.text((280 + i * 50, name_y + 20 + i * 5), ch,
                             font=en_font, fill=(180, 140, 80, 150))
        
        # 2. 标题区域（左侧）
        title_y = 320
        title_x = 60
        
        if title1:
            t1_font = self._get_font(80)
            draw.text((title_x, title_y), title1, font=t1_font, fill=(255, 255, 255))
            title_y += 120
        
        if title2:
            t2_font = self._get_font(80)
            # 描边效果
            for offset in range(-2, 3):
                for oy in range(-2, 3):
                    if offset != 0 or oy != 0:
                        draw.text((title_x + offset, title_y + oy), title2,
                                 font=t2_font, fill=(180, 140, 80))
            draw.text((title_x, title_y), title2, font=t2_font, fill=(255, 255, 255))
            title_y += 120
        
        if title3:
            t3_font = self._get_font(80)
            draw.text((title_x, title_y), title3, font=t3_font, fill=(255, 255, 255))
            title_y += 150
        
        # 分隔线
        draw.rectangle([(title_x, title_y), (title_x + 200, title_y + 3)],
                      fill=(180, 140, 80))
        title_y += 30
        
        # 3. 描述文字（多行）
        if desc_lines:
            desc_font = self._get_font(28)
            for line in desc_lines:
                draw.text((title_x, title_y), line, font=desc_font, fill=(200, 180, 160))
                title_y += 50
        
        # 4. 统计数据
        if stats:
            stats_font = self._get_font(24)
            draw.text((title_x, title_y + 20), stats, font=stats_font, fill=(180, 140, 80))
        
        # 5. 引号装饰
        quote_font = self._get_font(80)
        draw.text((title_x, H - 200), "\u201c", font=quote_font, fill=(180, 140, 80))
        
        # 保存
        bg.save(output_path, "JPEG", quality=95)
        print(f"[OK] IP类封面生成: {output_path}")
        return output_path

    # ═══════════════════════════════════════════════════════
    # 模板3：极简风（纯色背景+居中文字）
    # ═══════════════════════════════════════════════════════
    def template_minimal(self, output_path: str,
                         bg_color: Tuple[int, int, int] = (240, 84, 84),
                         title: str = "标题",
                         subtitle: str = "",
                         tag: str = "",
                         text_color: Tuple[int, int, int] = (255, 255, 255),
                         **kwargs) -> str:
        """极简风封面模板
        
        布局:
            纯色背景
            居中大字
            标签
        """
        W, H = 1080, 1920
        bg = Image.new("RGB", (W, H), bg_color)
        draw = ImageDraw.Draw(bg)
        
        # 主标题（居中）
        title_font = self._get_font(120)
        tw, th = self._text_size(title, title_font)
        tx = (W - tw) // 2
        ty = (H - th) // 2 - 100
        
        # 白色文字带轻微阴影
        draw.text((tx + 3, ty + 3), title, font=title_font, fill=(0, 0, 0, 50))
        draw.text((tx, ty), title, font=title_font, fill=text_color)
        
        # 副标题
        if subtitle:
            sub_font = self._get_font(50)
            sw, sh = self._text_size(subtitle, sub_font)
            sx = (W - sw) // 2
            sy = ty + th + 40
            draw.text((sx, sy), subtitle, font=sub_font, fill=text_color)
        
        # 标签（底部）
        if tag:
            tag_font = self._get_font(36)
            # 圆角标签背景
            tag_w, tag_h = self._text_size(tag, tag_font)
            tag_pad = 20
            tag_rect = [
                (W - tag_w) // 2 - tag_pad,
                H - 200,
                (W + tag_w) // 2 + tag_pad,
                H - 200 + tag_h + tag_pad * 2
            ]
            draw.rounded_rectangle(tag_rect, radius=30, fill=(255, 255, 255, 80),
                                   outline=text_color, width=2)
            draw.text(((W - tag_w) // 2, H - 200 + tag_pad), tag,
                     font=tag_font, fill=text_color)
        
        bg.save(output_path, "JPEG", quality=95)
        print(f"[OK] 极简风封面生成: {output_path}")
        return output_path

    # ═══════════════════════════════════════════════════════
    # 辅助方法
    # ═══════════════════════════════════════════════════════
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont,
                   max_width: int) -> List[str]:
        """自动换行"""
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

    def generate(self, template_id: int, output_path: str, **kwargs) -> str:
        """根据模板ID生成封面
        
        Args:
            template_id: 1=口播类, 2=IP类, 3=极简风
            output_path: 输出路径
            **kwargs: 模板参数
        """
        templates = {
            1: self.template_broadcast,
            2: self.template_ip,
            3: self.template_minimal,
        }
        
        if template_id not in templates:
            raise ValueError(f"未知模板: {template_id}，可用: 1, 2, 3")
        
        return templates[template_id](output_path=output_path, **kwargs)


# ═══════════════════════════════════════════════════════
# 命令行入口
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="封面生成器")
    parser.add_argument("template", type=int, choices=[1, 2, 3], help="模板编号")
    parser.add_argument("output", help="输出路径")
    parser.add_argument("--bg", help="背景图路径（模板1用）")
    parser.add_argument("--quote", help="引用语")
    parser.add_argument("--title", help="主标题")
    parser.add_argument("--subtitle", help="副标题")
    parser.add_argument("--name", help="人名（模板2用）")
    parser.add_argument("--name-en", help="英文名")
    parser.add_argument("--person", help="人物照片路径")
    parser.add_argument("--desc", nargs="+", help="描述文字（多行）")
    parser.add_argument("--stats", help="统计数据")
    parser.add_argument("--tag", help="标签")
    parser.add_argument("--color", help="背景色(R,G,B)")
    
    args = parser.parse_args()
    
    gen = CoverGenerator()
    params = {}
    
    # 收集参数
    if args.bg:
        params["bg_path"] = args.bg
    if args.quote:
        params["quote"] = args.quote
    if args.title:
        params["title"] = args.title
    if args.subtitle:
        params["subtitle"] = args.subtitle
    if args.name:
        params["name"] = args.name
    if args.name_en:
        params["name_en"] = args.name_en
    if args.person:
        params["person_image"] = args.person
    if args.desc:
        params["desc_lines"] = args.desc
    if args.stats:
        params["stats"] = args.stats
    if args.tag:
        params["tag"] = args.tag
    if args.color:
        params["bg_color"] = tuple(map(int, args.color.split(",")))
    
    gen.generate(args.template, args.output, **params)
