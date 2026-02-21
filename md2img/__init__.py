"""
md2img: Markdown → HTML → 图片

推荐流程：用 Markdown 写内容，转 HTML 再通过 WeasyPrint / imgkit 转成图片。
支持小红书等平台固定尺寸，长图自动分多张。
"""

from .converter import (
    XIAOHONGSHU_1_1,
    XIAOHONGSHU_2_3,
    XIAOHONGSHU_3_4,
    XIAOHONGSHU_4_3,
    HANDWRITING_CSS,
    MUYAO_CSS,
    VIRGIL_CSS,
    OBSIDIAN_CSS,
    PARCHMENT_CSS,
    EXCALI_CSS,
    convert,
    convert_file,
    md2img,
    md_to_images,
)

__all__ = [
    "convert",
    "convert_file",
    "md2img",
    "md_to_images",
    "XIAOHONGSHU_1_1",
    "XIAOHONGSHU_2_3",
    "XIAOHONGSHU_3_4",
    "XIAOHONGSHU_4_3",
    "HANDWRITING_CSS",
    "MUYAO_CSS",
    "VIRGIL_CSS",
    "OBSIDIAN_CSS",
    "PARCHMENT_CSS",
    "EXCALI_CSS",
]
__version__ = "0.1.0"
