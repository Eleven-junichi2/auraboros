from pathlib import Path
import json
import sys


class AssetFilePath:
    root_dir_path: Path

    @classmethod
    def set_root_dir(cls, root_dir_path: str | Path):
        """
        Args:
            root_dir_path (str | Path): A path to the directory to store asset files.
        Raises:
            ValueError: Raise it if root_dir_path is not a Path or str object.
        """
        if isinstance(root_dir_path, (str, Path)):
            cls.root_dir_path = Path(root_dir_path)
        else:
            raise ValueError("argument `root_dir_path` must be str or Path")

    @classmethod
    def get_asset(
        cls, filepath_relative_to_rootdir: Path | str, return_Path_object_else_str=True
    ) -> Path | str:
        """
        Examples:
            >>> get_asset("example_asset.png")
            >>> Path({root_dir_path}/example_asset.png)
            >>> get_asset("sounds_dir/example_sound.wav")
            >>> Path({root_dir_path}/sounds_dir/example_sound.wav)
        """
        path = cls.root_dir_path / Path(filepath_relative_to_rootdir)
        if not return_Path_object_else_str:
            path = str(path)
        return path


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
