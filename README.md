# md2img Skill

Markdown 转图片工具 Skill，基于 txt2img 项目封装。

## 快速开始

```bash
# 基础用法
echo "# 标题\n内容" | md2img

# 指定尺寸（小红书 3:4）
md2img --size 3:4 input.md

# 完整示例
echo "# 小红书笔记\n\n今天分享..." | md2img --size 3:4 -o ./output -b mypost
```

## 文件结构

```
md2img/
├── SKILL.md           # 详细文档
├── README.md          # 本文件
├── config.json        # Skill 配置
├── __init__.py        # Python 模块入口
└── bin/
    ├── md2img         # 主 CLI 脚本
    └── md2img-wrapper # macOS 环境包装器
```

## 依赖

- Python 3.9+
- WeasyPrint
- PyMuPDF
- markdown
- Pillow

macOS 还需安装系统库：
```bash
brew install pango cairo gdk-pixbuf libffi
```

## 使用场景

- 生成小红书图文笔记
- 将 Markdown 文档转为图片分享
- 社交媒体内容制作

## 链接

- 
