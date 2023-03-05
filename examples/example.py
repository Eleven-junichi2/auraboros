from src import eightrail
from src.utilities import AssetFilePath

eightrail.init(pixel_scale=2, caption="test",
               icon_filepath=AssetFilePath.img("icon.ico"))

if __name__ == "__main__":
    eightrail.run(60)
