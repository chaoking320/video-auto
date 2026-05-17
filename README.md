# video-auto - 视频自动化处理工具箱

帮老婆大人做的视频剪辑自动化工具，把机械重复工作自动化，创意工作留给剪映。

## 功能清单

| 功能 | 命令 | 说明 |
|------|------|------|
| 查看信息 | `info` | 查看视频分辨率、码率、时长等 |
| 格式转换 | `convert` | MOV/MKV 转 MP4 |
| 压缩优化 | `compress` | 减小文件体积 |
| 横竖屏转换 | `portrait` | 横屏转 9:16 竖屏 |
| 尺寸调整 | `resize` | 任意尺寸缩放 |
| 裁剪 | `crop` | 画面局部裁剪 |
| 截取片段 | `trim` | 提取视频片段 |
| 调速 | `speed` | 加速/减速 |
| 加水印 | `watermark` | 添加 Logo |
| 拼接 | `concat` | 多个视频合并 |
| 截图 | `screenshot` | 截取封面 |
| 平台预设 | `preset` | 一键适配抖音/小红书/视频号 |

## 快速开始

### 1. 查看视频信息
```bash
python video_auto.py info 原片.mp4
```

### 2. 横屏转竖屏（最常用！）
```bash
python video_auto.py portrait 横屏原片.mp4 竖屏输出.mp4
```

### 3. 应用平台预设（一键搞定）
```bash
# 抖音 9:16
python video_auto.py preset 原片.mp4 抖音版.mp4 --preset douyin

# 小红书 3:4
python video_auto.py preset 原片.mp4 小红书版.mp4 --preset xiaohongshu

# 视频号 9:16
python video_auto.py preset 原片.mp4 视频号版.mp4 --preset videohao
```

### 4. 一键预处理（懒人模式）
```bash
# Windows
bin\prepare.bat 原片.mp4 douyin
```
会自动：查看信息 → 应用预设 → 生成封面截图

### 5. 更多用法

**压缩视频**
```bash
python video_auto.py compress 原片.mp4 压缩版.mp4 --crf 23
```

**截取片段**
```bash
python video_auto.py trim 原片.mp4 片段.mp4 --start 00:00:10 --duration 00:00:30
```

**添加水印**
```bash
python video_auto.py watermark 原片.mp4 logo.png 带水印.mp4 --position bottom-right
```

## 平台参数说明

| 平台 | 分辨率 | 比例 | 码率建议 |
|------|--------|------|----------|
| 抖音 | 1080x1920 | 9:16 | ≤512MB |
| 小红书 | 1080x1440 | 3:4 | ≤5GB |
| 视频号 | 1080x1920 | 9:16 | ≤1GB |

## 项目结构

```
video-auto/
├── video_auto.py          # 主程序入口
├── core/
│   └── ffmpeg_utils.py    # FFmpeg 核心封装
├── presets/
│   ├── douyin.json        # 抖音预设
│   ├── xiaohongshu.json   # 小红书预设
│   └── videohao.json      # 视频号预设
├── templates/
│   ├── intros/            # 片头模板（备用）
│   └── outros/            # 片尾模板（备用）
├── bin/
│   └── prepare.bat        # Windows一键脚本
└── README.md              # 本文件
```

## 技术栈

- **FFmpeg** - 视频处理引擎（必须安装）
- **Python 3** - 脚本层封装
- **JSON** - 预设配置文件

## 注意事项

1. 确保 FFmpeg 已添加到系统 PATH
2. 拼接视频时，各视频格式必须一致
3. 字幕烧录支持 SRT 格式
4. 水印支持 PNG 透明图片

## 后续扩展

- [ ] AI 字幕自动生成（Whisper）
- [ ] 内容感知特效（人脸追踪）
- [ ] 批量处理队列
- [ ] 图形界面（GUI）
- [ ] 更多平台预设
