<div align="center">

# Mahiro icons

IMAGE PLACEHOLDER

LANGUAGE PLACEHOLDER

</div>

绪山真寻主题的图标库。

# 下载与使用

欢迎前往网站[PLACEHOLDER]下载各种格式的图标，您也可以直接在Github网站中下载您需要的图标。

# 贡献

欢迎提交图标，提交方式为：
fork 本仓库，添加图标后提交 pull request。
图标应当放置在icons目录下，需要有xml、svg、ico、jpg、png五种格式
svg格式必须为800x800的大小，如果图标本身不是正方形的，请将图标放置在一个800x800的画布上，图标居中。
创建图标时可以先创建xml或svg后使用updater文件夹内的icon_converter.py自动生成其他的格式。

```Python
pip install -r requirements.txt
python icon_converter.py
```