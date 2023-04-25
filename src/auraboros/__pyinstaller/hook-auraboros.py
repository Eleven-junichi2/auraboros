from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('auraboros', excludes=[
                           '__pyinstaller', 'debugs', 'getasset_order.json'])
