"""
Markdown → HTML → 图片 转换核心。

优先使用 WeasyPrint（效果最好），可选 imgkit（需系统安装 wkhtmltoimage）。
支持小红书等平台固定尺寸，长图自动分页为多张。
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union

import markdown

# 小红书推荐尺寸（宽×高 px，长边≥1080）
# 3:4 竖版最优，1:1 正方形，2:3 长图
XIAOHONGSHU_3_4 = (1242, 1656)   # 推荐，竖屏占满
XIAOHONGSHU_1_1 = (1080, 1080)    # 正方形
XIAOHONGSHU_2_3 = (1080, 1620)    # 2:3 长图
XIAOHONGSHU_4_3 = (1440, 1080)    # 4:3 横版

# 默认内联 CSS：让 Markdown 渲染出来的 HTML 好看、适合截图
# 针对小红书等社交媒体优化：增大字体，提高可读性
DEFAULT_CSS = """
@page { size: 800px; margin: 24px; }
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 28px;
  line-height: 1.6;
  color: #24292e;
  max-width: 100%;
}
h1 { font-size: 2.2em; margin: 0.67em 0; border-bottom: 3px solid #eaecef; padding-bottom: 0.3em; font-weight: 700; }
h2 { font-size: 1.8em; margin: 0.75em 0; border-bottom: 2px solid #eaecef; padding-bottom: 0.3em; font-weight: 600; }
h3 { font-size: 1.5em; margin: 0.83em 0; font-weight: 600; }
h4, h5, h6 { font-size: 1.2em; margin: 1em 0; font-weight: 600; }
p { margin: 0.5em 0 1em; }
ul, ol { margin: 0.5em 0 1em; padding-left: 2em; }
li { margin: 0.3em 0; }
code { background: #f6f8fa; padding: 0.2em 0.4em; border-radius: 4px; font-size: 0.85em; }
pre { background: #f6f8fa; padding: 1em; border-radius: 6px; overflow: auto; }
pre code { background: none; padding: 0; }
blockquote { border-left: 6px solid #dfe2e5; margin: 0.5em 0 1em; padding-left: 1em; color: #6a737d; font-size: 1.1em; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #eaecef; padding: 10px 16px; text-align: left; }
th { font-weight: 600; background: #f6f8fa; }
a { color: #0366d6; text-decoration: none; }
a:hover { text-decoration: underline; }
hr { border: none; border-top: 2px solid #eaecef; margin: 1.5em 0; }
strong { font-weight: 700; }
"""

# 手写体/楷体 CSS 样式
HANDWRITING_CSS = """
@page { size: 800px; margin: 24px; }
* { box-sizing: border-box; }
body {
  font-family: "Kaiti SC", "STKaiti", "BiauKai", "Kaiti", "Apple Chancery", cursive;
  font-size: 32px;
  line-height: 1.8;
  color: #2c2c2c;
  max-width: 100%;
}
h1 { 
  font-size: 2.4em; 
  margin: 0.67em 0; 
  border-bottom: 3px solid #8b7355; 
  padding-bottom: 0.3em; 
  font-weight: 700;
  text-align: center;
}
h2 { 
  font-size: 2em; 
  margin: 0.75em 0; 
  border-bottom: 2px solid #a08060; 
  padding-bottom: 0.3em; 
  font-weight: 600; 
}
h3 { font-size: 1.6em; margin: 0.83em 0; font-weight: 600; }
h4, h5, h6 { font-size: 1.3em; margin: 1em 0; font-weight: 600; }
p { margin: 0.6em 0 1.2em; text-indent: 2em; }
"""

# 沐瑶软笔手写体 CSS 样式
MUYAO_CSS = """
@page { size: 800px; margin: 24px; }
* { box-sizing: border-box; }
body {
  font-family: "Muyao-Softbrush", "Muyao Softbrush", "沐瑶软笔手写体";
  font-size: 34px;
  line-height: 1.9;
  color: #2c2c2c;
  max-width: 100%;
}
h1 { 
  font-size: 2.6em; 
  margin: 0.67em 0; 
  border-bottom: 4px solid #e07a5f; 
  padding-bottom: 0.3em; 
  font-weight: 700;
  text-align: center;
  color: #e07a5f;
}
h2 { 
  font-size: 2.2em; 
  margin: 0.75em 0; 
  border-bottom: 3px solid #f2cc8f; 
  padding-bottom: 0.3em; 
  font-weight: 600; 
  color: #d4a373;
}
h3 { font-size: 1.8em; margin: 0.83em 0; font-weight: 600; color: #81b29a; }
h4, h5, h6 { font-size: 1.4em; margin: 1em 0; font-weight: 600; }
p { margin: 0.6em 0 1.2em; text-indent: 2em; }
ul, ol { margin: 0.5em 0 1em; padding-left: 2.5em; }
li { margin: 0.4em 0; }
code { background: #f4e9d8; padding: 0.2em 0.4em; border-radius: 4px; font-size: 0.8em; font-family: "Courier New", monospace; }
pre { background: #f4e9d8; padding: 1em; border-radius: 6px; overflow: auto; }
pre code { background: none; padding: 0; }
blockquote { 
  border-left: 6px solid #e07a5f; 
  margin: 1em 0 1.5em; 
  padding-left: 1.2em; 
  color: #7d6b5d; 
  font-size: 1.1em;
  font-style: italic;
}
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 2px solid #f2cc8f; padding: 12px 16px; text-align: left; }
th { font-weight: 600; background: #f4e9d8; color: #e07a5f; }
a { color: #e07a5f; text-decoration: none; }
a:hover { text-decoration: underline; }
hr { border: none; border-top: 3px dashed #f2cc8f; margin: 1.5em 0; }
strong { font-weight: 700; color: #e07a5f; }
"""

# Virgil 手写体 CSS 样式
VIRGIL_CSS = """
@page { size: 800px; margin: 24px; }
* { box-sizing: border-box; }
body {
  font-family: "Virgil", "FSP UppERCASE Sans", sans-serif;
  font-size: 32px;
  line-height: 1.85;
  color: #2d3436;
  max-width: 100%;
}
h1 { 
  font-size: 2.5em; 
  margin: 0.67em 0; 
  border-bottom: 4px solid #6c5ce7; 
  padding-bottom: 0.3em; 
  font-weight: 700;
  text-align: center;
  color: #6c5ce7;
}
h2 { 
  font-size: 2em; 
  margin: 0.75em 0; 
  border-bottom: 3px solid #a29bfe; 
  padding-bottom: 0.3em; 
  font-weight: 600; 
  color: #7c73e6;
}
h3 { font-size: 1.6em; margin: 0.83em 0; font-weight: 600; color: #6c5ce7; }
h4, h5, h6 { font-size: 1.3em; margin: 1em 0; font-weight: 600; }
p { margin: 0.6em 0 1.2em; text-indent: 2em; }
ul, ol { margin: 0.5em 0 1em; padding-left: 2.5em; }
li { margin: 0.4em 0; }
code { background: #e8e6ff; padding: 0.2em 0.4em; border-radius: 4px; font-size: 0.8em; font-family: "Courier New", monospace; }
pre { background: #e8e6ff; padding: 1em; border-radius: 6px; overflow: auto; }
pre code { background: none; padding: 0; }
blockquote { 
  border-left: 6px solid #6c5ce7; 
  margin: 1em 0 1.5em; 
  padding-left: 1.2em; 
  color: #5f5a7a; 
  font-size: 1.1em;
  font-style: italic;
}
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 2px solid #a29bfe; padding: 12px 16px; text-align: left; }
th { font-weight: 600; background: #e8e6ff; color: #6c5ce7; }
a { color: #6c5ce7; text-decoration: none; }
a:hover { text-decoration: underline; }
hr { border: none; border-top: 3px dashed #a29bfe; margin: 1.5em 0; }
strong { font-weight: 700; color: #6c5ce7; }
"""

# 羊皮卷风格 CSS 样式 (复古羊皮纸效果)
PARCHMENT_CSS = """
@page { size: 800px; margin: 24px; }
* { box-sizing: border-box; }
@font-face {
  font-family: "Virgil";
  src: local("Virgil"), local("FSP UppERCASE Sans");
}
body {
  font-family: "Virgil", "FSP UppERCASE Sans", "Humor Sans", sans-serif;
  font-size: 32px;
  line-height: 1.85;
  color: #1a1a1a;
  background: linear-gradient(135deg, #f4e4bc 0%, #e8d4a8 50%, #f0e2c5 100%);
  max-width: 100%;
  padding: 30px;
  box-shadow: inset 0 0 60px rgba(139, 119, 80, 0.2);
}
h1 { 
  font-size: 2.4em; 
  margin: 0.6em 0; 
  border-bottom: 3px solid #8b4513; 
  padding-bottom: 0.3em; 
  font-weight: 700;
  text-align: center;
  color: #5c3317;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}
h2 { 
  font-size: 1.9em; 
  margin: 0.7em 0; 
  border-bottom: 2px solid #a0522d; 
  padding-bottom: 0.2em; 
  font-weight: 600; 
  color: #6b3e26;
}
h3 { font-size: 1.6em; margin: 0.7em 0; font-weight: 600; color: #704214; }
h4, h5, h6 { font-size: 1.3em; margin: 0.7em 0; font-weight: 600; color: #5c3317; }
p { margin: 0.5em 0 1em; }
ul, ol { margin: 0.5em 0 1em; padding-left: 2.2em; }
li { margin: 0.3em 0; }
code { background: rgba(139, 69, 19, 0.1); padding: 0.15em 0.4em; border-radius: 3px; font-size: 0.85em; color: #5c3317; border: 1px solid #d4c4a8; }
pre { background: rgba(139, 69, 19, 0.08); padding: 1em; border-radius: 6px; overflow: auto; border: 2px solid #c4b490; }
pre code { background: none; padding: 0; color: #4a3520; }
blockquote { 
  border-left: 5px solid #8b4513; 
  margin: 0.8em 0 1em; 
  padding-left: 1em; 
  color: #6b4423; 
  font-style: italic;
  background: rgba(139, 69, 19, 0.05);
  padding: 0.8em;
  border-radius: 0 8px 8px 0;
}
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 2px solid #a0522d; padding: 10px 14px; text-align: left; }
th { font-weight: 600; background: rgba(139, 69, 19, 0.15); color: #5c3317; }
a { color: #8b4513; text-decoration: none; }
a:hover { text-decoration: underline; }
hr { border: none; border-top: 2px dashed #a0522d; margin: 1.5em 0; }
strong { font-weight: 700; color: #5c3317; }
"""

# 别名 (保留兼容性)
OBSIDIAN_CSS = PARCHMENT_CSS

# Excalifont 风格 CSS 样式 (手绘风格)
EXCALI_CSS = """
@page { size: 800px; margin: 24px; }
* { box-sizing: border-box; }
body {
  font-family: "Excalifont", "Excalifont-Regular", "Segoe Print", "Bradley Hand", cursive;
  font-size: 32px;
  line-height: 1.85;
  color: #2c3e50;
  background: linear-gradient(180deg, #faf8f5 0%, #f5f0e8 100%);
  max-width: 100%;
  padding: 25px;
  border: 3px double #5d4e37;
  border-radius: 8px;
}
h1 { 
  font-size: 2.4em; 
  margin: 0.6em 0; 
  border-bottom: 3px double #8b4513; 
  padding-bottom: 0.3em; 
  font-weight: 600;
  text-align: center;
  color: #8b4513;
  font-family: "Excalifont", "Excalifont-Regular", cursive;
}
h2 { 
  font-size: 2em; 
  margin: 0.7em 0; 
  border-bottom: 2px dashed #a0522d; 
  padding-bottom: 0.2em; 
  font-weight: 600; 
  color: #6b4423;
  font-family: "Excalifont", "Excalifont-Regular", cursive;
}
h3 { font-size: 1.7em; margin: 0.7em 0; font-weight: 600; color: #5d4037; }
h4, h5, h6 { font-size: 1.4em; margin: 0.7em 0; font-weight: 600; color: #4e342e; }
p { margin: 0.5em 0 1em; }
ul, ol { margin: 0.5em 0 1em; padding-left: 2.2em; }
li { margin: 0.3em 0; }
code { background: #f0e6d3; padding: 0.15em 0.4em; border-radius: 3px; font-size: 0.85em; color: #5d4037; border: 1px dashed #bcaaa4; font-family: monospace; }
pre { background: #f5f0e8; padding: 1em; border-radius: 6px; overflow: auto; border: 2px dashed #d7ccc8; }
pre code { background: none; padding: 0; color: #3e2723; }
blockquote { 
  border-left: 5px double #8b4513; 
  margin: 0.8em 0 1em; 
  padding-left: 1em; 
  color: #5d4037; 
  font-style: italic;
  background: rgba(139, 69, 19, 0.05);
  padding: 0.8em;
  border-radius: 4px;
}
table { border-collapse: collapse; width: 100%; margin: 1em 0; border: 2px solid #8b4513; }
th, td { border: 1px dashed #a1887f; padding: 10px 14px; text-align: left; }
th { font-weight: 600; background: #efebe9; color: #5d4037; }
a { color: #8b4513; text-decoration: none; }
a:hover { text-decoration: underline; }
hr { border: none; border-top: 3px double #a1887f; margin: 1.5em 0; }
strong { font-weight: 700; color: #5d4037; }
"""

# 别名
MUYAO_HANDWRITING_CSS = MUYAO_CSS
VIRGIL_HANDWRITING_CSS = VIRGIL_CSS
OBSIDIAN_STYLE_CSS = OBSIDIAN_CSS


def _md_to_html(md_content: str, extras: Optional[list] = None, base_css: Optional[str] = None) -> str:
    """Markdown 字符串 → 完整 HTML 文档（带默认样式）。"""
    html_body = markdown.markdown(
        md_content,
        extensions=extras or ["extra", "codehilite", "toc"],
    )
    css = base_css if base_css else DEFAULT_CSS
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Markdown Export</title>
  <style>{css}</style>
</head>
<body>
{html_body}
</body>
</html>"""


def _crop_image_to_content(image_path: Union[str, Path]) -> None:
    """裁剪图片到内容区域，去掉底部和四周的纯白空白。"""
    from PIL import Image

    path = Path(image_path)
    img = Image.open(path).convert("RGB")
    w, h = img.size
    gray = img.convert("L")
    # 非白色(255)置为 255，白色置为 0，getbbox() 即非空白区域
    thresh = 254
    mask = gray.point(lambda p: 255 if p < thresh else 0, mode="L")
    box = mask.getbbox()
    if not box:
        return
    margin = 4
    box = (
        max(0, box[0] - margin),
        max(0, box[1] - margin),
        min(w, box[2] + margin),
        min(h, box[3] + margin),
    )
    img.crop(box).save(
        str(path),
        **({"quality": 95} if path.suffix.lower() in (".jpg", ".jpeg") else {}),
    )


def _html_to_image_weasyprint(
    html: str,
    output_path: Union[str, Path],
    page_size: Optional[Tuple[int, int]] = None,
) -> List[Path]:
    """
    使用 WeasyPrint 将 HTML 转为图片。
    - page_size 为 (宽, 高) 时：按该尺寸分页，长图输出多张（如 article_1.png, article_2.png），返回路径列表。
    - page_size 为 None 时：单张长图并裁剪空白，返回单元素列表。
    """
    import tempfile
    import weasyprint

    doc = weasyprint.HTML(string=html)
    output_path = Path(output_path)
    ext = output_path.suffix.lower()
    base_dir = output_path.parent
    stem, suffix = output_path.stem, output_path.suffix

    if page_size:
        w, h = page_size
        # 固定页尺寸，多页 PDF（注入 HTML 确保覆盖默认 @page）
        from weasyprint import CSS
        page_css = CSS(string=f"@page {{ size: {w}px {h}px; margin: 28px; }}")
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name
        try:
            # 必须用 stylesheets 覆盖文档内默认 @page，且放在最后
            doc.write_pdf(pdf_path, stylesheets=[page_css])
            import fitz  # PyMuPDF
            pdf_doc = fitz.open(pdf_path)
            # 96 DPI 使输出像素与 page_size 一致（WeasyPrint px = 1/96 inch）
            dpi = 96
            out_paths: List[Path] = []
            for i in range(len(pdf_doc)):
                page = pdf_doc[i]
                pix = page.get_pixmap(dpi=dpi, alpha=False)
                p = base_dir / f"{stem}_{i + 1}{suffix}"
                if ext == ".jpg" or ext == ".jpeg":
                    pix.save(str(p), output="jpeg", quality=95)
                else:
                    pix.save(str(p))
                out_paths.append(p)
            pdf_doc.close()
            return out_paths
        finally:
            Path(pdf_path).unlink(missing_ok=True)

    # 单张长图，裁剪空白
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        pdf_path = f.name
    try:
        doc.write_pdf(pdf_path)
        import fitz  # PyMuPDF
        pdf_doc = fitz.open(pdf_path)
        page = pdf_doc[0]
        pix = page.get_pixmap(dpi=150, alpha=False)
        if ext == ".jpg" or ext == ".jpeg":
            pix.save(str(output_path), output="jpeg", quality=95)
        else:
            pix.save(str(output_path))
        pdf_doc.close()
    finally:
        Path(pdf_path).unlink(missing_ok=True)
    _crop_image_to_content(output_path)
    return [output_path]


def _html_to_image_imgkit(html: str, output_path: Union[str, Path]) -> None:
    """使用 imgkit（wkhtmltoimage）将 HTML 转为图片。"""
    import imgkit

    options = {
        "format": Path(output_path).suffix.lstrip(".") or "png",
        "quality": 95,
        "enable-local-file-access": None,
    }
    imgkit.from_string(html, str(output_path), options=options)


def convert(
    md_content: str,
    output_path: Union[str, Path],
    *,
    backend: str = "weasyprint",
    extra_css: Optional[str] = None,
    md_extras: Optional[list] = None,
    page_size: Optional[Tuple[int, int]] = None,
    style: str = "default",
) -> Union[Path, List[Path]]:
    """
    将 Markdown 字符串转为图片。

    :param md_content: Markdown 原文
    :param output_path: 输出图片路径（.png / .jpg 等）；多页时为基底名，生成 article_1.png, article_2.png ...
    :param backend: "weasyprint"（推荐）或 "imgkit"
    :param extra_css: 额外 CSS 字符串，会与默认样式合并
    :param md_extras: markdown 扩展列表，默认 ["extra", "codehilite", "toc"]
    :param page_size: 固定页尺寸 (宽, 高) px，如小红书 3:4 用 XIAOHONGSHU_3_4；长图会分多张输出
    :param style: 样式风格："default"（默认现代风格）、"handwriting"（楷体）、"muyao"（沐瑶软笔）、"virgil"（Virgil 手写体）、"parchment"（羊皮卷）或 "excali"（Excalifont 手绘风格）
    :return: 单张时为 Path，多张时为 List[Path]
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 根据 style 参数选择 CSS
    if style == "handwriting":
        base_css = HANDWRITING_CSS
    elif style == "muyao":
        base_css = MUYAO_CSS
    elif style == "virgil":
        base_css = VIRGIL_CSS
    elif style == "obsidian":
        base_css = OBSIDIAN_CSS
    elif style == "parchment":
        base_css = PARCHMENT_CSS
    elif style == "excali":
        base_css = EXCALI_CSS
    else:
        base_css = DEFAULT_CSS
    
    html = _md_to_html(md_content, extras=md_extras, base_css=base_css)
    if extra_css:
        html = html.replace("</style>", f"\n{extra_css}\n</style>")
    # 小红书等固定尺寸：把 @page 注入 HTML 末尾，覆盖默认 800px
    if page_size:
        w, h = page_size
        html = html.replace("</style>", f"\n@page {{ size: {w}px {h}px; margin: 28px; }}\n</style>")

    if backend == "weasyprint":
        paths = _html_to_image_weasyprint(html, output_path, page_size=page_size)
        return paths[0] if len(paths) == 1 else paths
    elif backend == "imgkit":
        _html_to_image_imgkit(html, output_path)
        return output_path
    else:
        raise ValueError(f'不支持的 backend: {backend!r}，请用 "weasyprint" 或 "imgkit"')


def convert_file(
    md_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    *,
    encoding: str = "utf-8",
    backend: str = "weasyprint",
    extra_css: Optional[str] = None,
    md_extras: Optional[list] = None,
    page_size: Optional[Tuple[int, int]] = None,
    style: str = "default",
) -> Union[Path, List[Path]]:
    """
    将 Markdown 文件转为图片。

    :param md_path: .md 文件路径
    :param output_path: 输出图片路径；不传则与 md 同目录、同名 .png
    :param encoding: 读取 md 文件用的编码
    :param backend: "weasyprint" 或 "imgkit"
    :param extra_css: 额外 CSS
    :param md_extras: markdown 扩展列表
    :param page_size: 固定页尺寸 (宽, 高) px，长图分多张
    :param style: 样式风格："default"（默认现代风格）或 "handwriting"（手写楷体风格）
    :return: 单张为 Path，多张为 List[Path]
    """
    md_path = Path(md_path)
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown 文件不存在: {md_path}")

    content = md_path.read_text(encoding=encoding)
    if output_path is None:
        output_path = md_path.with_suffix(".png")
    return convert(
        content,
        output_path,
        backend=backend,
        extra_css=extra_css,
        md_extras=md_extras,
        page_size=page_size,
        style=style,
    )


# 别名
def md2img(
    md_content: str,
    output_path: Union[str, Path],
    *,
    backend: str = "weasyprint",
    **kwargs,
) -> Union[Path, List[Path]]:
    """convert 的别名。"""
    return convert(md_content, output_path, backend=backend, **kwargs)


def md_to_images(
    md_content: str,
    output_path: Optional[Union[str, Path]] = None,
    *,
    output_dir: Optional[Union[str, Path]] = None,
    output_basename: str = "md2img_out",
    page_size: Optional[Tuple[int, int]] = None,
    backend: str = "weasyprint",
    extra_css: Optional[str] = None,
    md_extras: Optional[list] = None,
    style: str = "default",
) -> List[str]:
    """
    Markdown 文本转图片，返回图片的**绝对路径**列表。

    :param md_content: Markdown 原文
    :param output_path: 输出路径（可选）。不传则用 output_dir + output_basename 生成 xxx_1.png, xxx_2.png ...
    :param output_dir: 输出目录（output_path 未传时生效），默认当前目录
    :param output_basename: 输出文件名基底（output_path 未传时生效），默认 "md2img_out"
    :param page_size: 页尺寸 (宽, 高) px，默认 XIAOHONGSHU_3_4；长图自动分多张
    :param backend: "weasyprint" 或 "imgkit"
    :param extra_css: 额外 CSS
    :param md_extras: markdown 扩展列表
    :param style: 样式风格："default"（默认现代风格）或 "handwriting"（手写楷体风格）
    :return: 生成图片的绝对路径列表，如 ["/path/to/out_1.png", "/path/to/out_2.png"]
    """
    if page_size is None:
        page_size = XIAOHONGSHU_3_4
    if output_path is None:
        out_dir = Path(output_dir or ".").resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"{output_basename}.png"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    result = convert(
        md_content,
        output_path,
        backend=backend,
        extra_css=extra_css,
        md_extras=md_extras,
        page_size=page_size,
        style=style,
    )
    paths = [result] if isinstance(result, Path) else result
    return [str(p.resolve()) for p in paths]
