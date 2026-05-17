@echo off
chcp 65001 >nul
:: 一键预处理脚本
:: 用法: prepare.bat <输入视频> [平台: douyin|xiaohongshu|videohao]

set "SCRIPT_DIR=%~dp0.."
set "INPUT=%~1"
set "PLATFORM=%~2"

if "%~1"=="" (
    echo 用法: prepare.bat ^<输入视频^> [平台]
    echo 平台选项: douyin, xiaohongshu, videohao
    echo.
    echo 示例:
    echo   prepare.bat input.mp4 douyin
    exit /b 1
)

if "%~2"=="" set "PLATFORM=douyin"

echo ========================================
echo 视频自动化预处理工具
echo 输入: %INPUT%
echo 平台: %PLATFORM%
echo ========================================
echo.

:: 先查看信息
echo [1/3] 查看视频信息...
python "%SCRIPT_DIR%\video_auto.py" info "%INPUT%"

:: 应用平台预设
echo.
echo [2/3] 应用 %PLATFORM% 预设...
python "%SCRIPT_DIR%\video_auto.py" preset "%INPUT%" "%INPUT%_processed.mp4" --preset %PLATFORM%

:: 截图预览
echo.
echo [3/3] 生成封面截图...
python "%SCRIPT_DIR%\video_auto.py" screenshot "%INPUT%_processed.mp4" "%INPUT%_cover.jpg"

echo.
echo ========================================
echo 处理完成!
echo 输出文件: %INPUT%_processed.mp4
echo 封面图片: %INPUT%_cover.jpg
echo ========================================
