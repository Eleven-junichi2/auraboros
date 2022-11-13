from eightrail import eightrail
from eightrail.utilities import AssetFilePath

eightrail.init(pixel_scale=2, icon_filepath=AssetFilePath.img("icon.ico"))

if __name__ == "__main__":
    eightrail.run(60)
