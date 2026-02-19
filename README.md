<div align="center">

# Mahiro icons

[![Logo](res/Logo.png)](https://mahiroicon.muxyang.com/)

[简体中文](README.md) | [English](README.en.md)

绪山真寻主题配色的图标库。

</div>

# 下载

欢迎前往网站 [mahiroicon.muxyang.com](https://mahiroicon.muxyang.com/) 下载各种格式的图标，您也可以直接在 Github 网站中下载您需要的图标。

# 贡献

欢迎提交图标，提交方式为：
fork 本仓库，添加图标后提交 pull request。
图标应当放置在`icons`目录下，需要有xml、svg、ico、jpg、png五种格式
svg格式必须为**800x800**的大小，如果图标本身不是正方形的或图标过大/过小，请将图标调整为等比缩放到**800x800**大小。
创建图标时可以先创建xml或svg后使用`updater`文件夹内的`icon_converter.py`自动生成其他的格式。
如果您对图标文件进行了更改，请在该图标svg同级目录下创建标识文件，
标识文件为`.updatexml`与`.updatesvg`，前者为删除xml重新生成；后者为删除svg重新生成。

```Python
pip install -r requirements.txt
python icon_converter.py
```

该脚本将会:
- 检查相关设置是否符合要求
- 创建相关尺寸的图片