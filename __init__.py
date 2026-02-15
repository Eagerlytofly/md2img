"""
md2img - Markdown 转图片 Skill

提供 Markdown 到图片的转换功能，支持小红书等社交媒体平台。

基本用法:
    from md2img import md_to_images
    
    paths = md_to_images("# 标题\n内容")
    print(paths)  # ["/path/to/output_1.png"]

完整参数:
    paths = md_to_images(
        md_content="# 标题\n内容",
        output_dir="./output",
        output_basename="myimage",
        page_size=(1242, 1656),  # 小红书 3:4
        extra_css="body { background: #fff; }",
    )
"""

import sys
from pathlib import Path

# 添加原始项目路径
TXT2IMG_ROOT = Path("/Users/wangzhenbo/code/cursor/txt2img")
if str(TXT2IMG_ROOT) not in sys.path:
    sys.path.insert(0, str(TXT2IMG_ROOT))

# 从原始项目导入所有公开 API
try:
    from md2img import (
        md_to_images,
        convert,
        convert_file,
        md2img,
        XIAOHONGSHU_1_1,
        XIAOHONGSHU_2_3,
        XIAOHONGSHU_3_4,
        XIAOHONGSHU_4_3,
    )
    
    __all__ = [
        "md_to_images",
        "convert",
        "convert_file",
        "md2img",
        "XIAOHONGSHU_1_1",
        "XIAOHONGSHU_2_3",
        "XIAONGSHU_3_4",
        "XIAOHONGSHU_4_3",
    ]
    
except ImportError as e:
    import warnings
    warnings.warn(f"md2img 依赖未安装: {e}. 请运行: pip install weasyprint PyMuPDF markdown Pillow")
    
    # 提供占位符函数
    def md_to_images(*args, **kwargs):
        raise ImportError("md2img 依赖未安装。请运行: pip install weasyprint PyMuPDF markdown Pillow")
    
    __all__ = ["md_to_images"]

__version__ = "1.0.0"
