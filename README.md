# GalMC_API_UIEditor
为开发者或者玩家们提供一种更加简单的方式在Minecraft中制作GalGame Provide developers or players with a simpler way to create GalGames in Minecraft.

## 依赖要求

- Python 3.10 及以上（项目代码使用了 `match-case` 语法）。
- PyQt5（用于图形化界面）。
- mutagen（用于读取 `.ogg` 音频时长）。

可使用如下命令安装依赖：

```bash
pip install PyQt5 mutagen
```

## 用法

1. 准备一个项目目录，并确保目录结构包含 `assets/galmc_api/...` 相关资源路径。
2. 在仓库根目录运行编辑器：

```bash
python test1.py
```

3. 在界面中选择/创建项目资源后进行编辑。
4. 程序会通过 `res_manager.py` 自动扫描资源，并生成 `assets/galmc_api/sound.json`。
