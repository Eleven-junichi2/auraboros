from pathlib import Path
import json
import sys


class AssetFilePath:
    root_dirname = "assets"
    root_dir_parent = Path(sys.argv[0]).parent
    __root = root_dir_parent / root_dirname
    root = Path(__root)
    img_dirname = "imgs"
    font_dirname = "fonts"
    sound_dirname = "sounds"

    @classmethod
    def pyinstaller_path(cls, filepath):
        try:
            # PyInstaller creates a temp folder
            # and stores the programs in _MEIPASS
            path = Path(sys._MEIPASS) / cls.root_dirname / filepath
            # path will be such as: "sys._MEIPASS/assets/imgs/example.png"
        except AttributeError:
            path = cls.root / filepath
        return path

    @classmethod
    def img(cls, filename):
        return cls.pyinstaller_path(Path(cls.img_dirname) / filename)

    @classmethod
    def font(cls, filename):
        return cls.pyinstaller_path(Path(cls.font_dirname) / filename)

    @classmethod
    def sound(cls, filename):
        return cls.pyinstaller_path(Path(cls.sound_dirname) / filename)

    @classmethod
    def set_asset_root(cls, root_dir_path: str):
        cls.__root = root_dir_path
        cls.root = Path(cls.__root)
        cls.root_dir_parent = Path(root_dir_path).parent
        cls.root_dirname = Path(root_dir_path).name


def open_json_file(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


def path_pyinstllr(path):
    """
    Convert the given path with the sys._MEIPASS directory as its
    parent if the app is running with PyInstaller.

    Bootloader of PyInstalle creates a temp folder "sys._MEIPASS"
    and stores programs and files in it.
    """
    try:
        # PyInstaller creates a temp folder
        # and stores the programs in _MEIPASS
        path = Path(sys._MEIPASS) / path
        # path will be such as: "sys._MEIPASS/assets/imgs/example.png"
    except AttributeError:
        path = path
    return path
