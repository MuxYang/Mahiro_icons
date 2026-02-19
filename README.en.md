<div align="center">

# Mahiro icons

[![Logo](res/Logo.png)](https://mahiroicon.muxyang.com/)

[简体中文](README.md) | [English](README.en.md)

An icon library themed and colored around Mahiro Shioyama.

</div>

# Download

Welcome to visit [mahiroicon.muxyang.com](https://mahiroicon.muxyang.com/) to download icons in various formats. You can also directly download the icons you need from the Github repository.

# Contributing

We welcome icon submissions! To contribute:

1. Fork this repository
2. Add your icons and submit a pull request

## Icon Requirements

- Icons should be placed in the `icons` directory
- Each icon must have five formats: xml, svg, ico, jpg, and png
- SVG format **must be 800x800** in size
  - If your icon is not square or is too large/small, please scale it proportionally to 800x800
- You can create the icon in xml or svg format first, then use `icon_converter.py` in the `updater` folder to automatically generate other formats

## Updating Existing Icons

If you modify an icon file, create a marker file in the same directory as the icon's svg:

- `.updatexml` - Delete xml and regenerate
- `.updatesvg` - Delete svg and regenerate

**Note:** The icon must already be listed in the `.converted` file for the update to take effect.

## Auto-generation Steps

```bash
cd updater
pip install -r requirements.txt
python icon_converter.py
```

The script will:
- Check if the SVG is 800x800
- Generate px files in different sizes
- Create ico, jpg, and png files
- Handle icon updates automatically
