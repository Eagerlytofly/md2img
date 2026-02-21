---
name: md2img
version: 1.0.0
description: Markdown 转图片工具，支持小红书等社交媒体图文生成
homepage: https://github.com/openclaw/openclaw
metadata:
  {
    "openclaw":
      {
        "emoji": "🖼️",
        "requires": { "python": ">=3.9" },
        "install":
          [
            {
              "id": "pip",
              "kind": "pip",
              "packages": ["weasyprint", "PyMuPDF", "markdown", "Pillow"],
              "label": "Install Python dependencies"
            }
          ],
      },
  }
---

# md2img 🖼️

将 Markdown 文本转换为图片，支持小红书等社交媒体平台的图文生成。

## 功能特性

- 📝 **Markdown 渲染**：支持标准 Markdown 语法（标题、列表、表格、代码块等）
- 📐 **多平台尺寸**：内置小红书 3:4/1:1/2:3、横版 4:3 等常用尺寸
- 🎨 **自定义样式**：支持自定义 CSS 样式
- 📄 **分页支持**：长文自动分页为多张图片
- 🖨️ **高质量输出**：使用 WeasyPrint 引擎，输出清晰美观

## 前置要求

### 系统依赖（macOS）

```bash
# 安装 WeasyPrint 所需的系统库
brew install pango cairo gdk-pixbuf libffi
```

### Python 依赖

```bash
pip install weasyprint PyMuPDF markdown Pillow
```

## 使用方法

### 命令行

```bash
# 基础用法 - 从 stdin 读取 Markdown
echo "# 标题\n内容" | md2img

# 从文件读取
md2img input.md

# 指定输出目录和文件名
md2img input.md -o ./output -b myimage

# 指定尺寸（小红书 3:4 竖版）
md2img input.md --size 3:4

# 小红书 1:1 正方形
md2img input.md --size 1:1

# 自定义尺寸
md2img input.md --width 1200 --height 1600
```

### Python API

```python
from md2img import md_to_images

# 基础用法
paths = md_to_images("# 标题\n内容")
print(paths)  # ["/path/to/md2img_out_1.png"]

# 指定尺寸和输出目录
paths = md_to_images(
    md_content="# 小红书笔记\n\n今天分享...",
    output_dir="/tmp",
    output_basename="xiaohongshu_post",
    page_size=(1242, 1656)  # 小红书 3:4
)
```

## 参数说明

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | Markdown 文件路径，不传或 `-` 表示从 stdin 读取 | `-` |
| `-o, --output-dir` | 输出目录 | 当前目录 |
| `-b, --basename` | 输出文件名基底 | `md2img_out` |
| `--size` | 预设尺寸：`3:4`, `1:1`, `2:3`, `4:3` | `3:4` |
| `--width` | 自定义宽度（像素） | - |
| `--height` | 自定义高度（像素） | - |
| `--css` | 自定义 CSS 文件路径 | - |
| `--style` | 样式风格：`default`（默认现代风）或 `handwriting`（手写楷体） | `default` |

### Python API 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `md_content` | str | Markdown 原文 |
| `output_dir` | str/Path | 输出目录 |
| `output_basename` | str | 文件名基底 |
| `page_size` | tuple | 页尺寸 (宽, 高) 像素，默认 `(1242, 1656)` |
| `backend` | str | 渲染引擎：`weasyprint`（默认）或 `imgkit` |
| `extra_css` | str | 额外 CSS 样式字符串 |
| `md_extras` | list | markdown 扩展列表 |
| `style` | str | 样式风格：`default` 或 `handwriting`（手写楷体） |

## 预设尺寸

| 尺寸 | 分辨率 | 适用场景 |
|------|--------|----------|
| `3:4` | 1242×1656 | 小红书竖版（推荐） |
| `1:1` | 1080×1080 | 小红书/Instagram 正方形 |
| `2:3` | 1080×1620 | 小红书长图 |
| `4:3` | 1440×1080 | 横版 |

### 样式风格

支持两种样式风格：

```python
from md2img import md_to_images

# 默认现代风格
paths = md_to_images("# 标题\n内容", style="default")

# 手写楷体风格
paths = md_to_images("# 标题\n内容", style="handwriting")
```

**手写体风格特点：**
- 使用楷体字体（Kaiti SC / STKaiti）
- 更大的行距和字体
- 暖色调配色（米色背景、棕色边框）
- 段落首行缩进
- 虚线分隔线

## 使用示例

### 生成小红书笔记图片

```bash
# 创建 Markdown 文件
cat > note.md << 'EOF'
# 🌸 今日份美好

今天发现了一家超棒的咖啡店！

## 环境
- 装修风格：日式原木风
- 座位舒适度：⭐⭐⭐⭐⭐
- 音乐氛围：轻爵士

## 推荐
1. 手冲埃塞俄比亚
2. 抹茶巴斯克蛋糕

> 生活不止眼前的苟且，还有咖啡和远方 ☕
EOF

# 生成图片
md2img note.md --size 3:4 -o ./output -b coffee_note
```

### 在 Python 脚本中使用

```python
from md2img import md_to_images

content = """
# AI Agent 今日热点

## 🤖 OpenClaw
- 24/7 运行在你的电脑上
- 支持浏览器自动化
- 开源免费

## 💡 关键洞察
AI Agent 正从**工具**转变为**实体**
"""

paths = md_to_images(
    md_content=content,
    output_dir="/Users/wangzhenbo/Desktop",
    output_basename="twitter_summary",
    page_size=(1242, 1656)
)

print(f"生成 {len(paths)} 张图片:")
for p in paths:
    print(f"  - {p}")
```

## 自定义样式

通过 `--css` 参数传入自定义 CSS 文件：

```css
/* custom.css */
body {
  font-family: "PingFang SC", sans-serif;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
h1 {
  color: #ff6b6b;
  text-align: center;
}
```

## 故障排除

### WeasyPrint 导入错误

```bash
# macOS 解决方案
brew install pango cairo gdk-pixbuf libffi
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
```

### 中文字体显示问题

确保系统安装了中文字体：
- macOS: 默认已安装 "PingFang SC"
- Linux: 安装 `fonts-noto-cjk`

### 图片裁剪问题

如果生成的图片有白边，会自动裁剪到内容区域。如需禁用，修改 `DEFAULT_CSS` 中的 margin 设置。

## 相关链接

- [WeasyPrint 文档](https://doc.courtbouillon.org/weasyprint/)
- [Markdown 语法](https://www.markdownguide.org/)
