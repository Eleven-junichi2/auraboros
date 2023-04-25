# Auraboros

[英語（English）](./README.md)

自分の開発用のために作られた、pygameを核にしたゲームフレームワークです。
8trailのソースコードを流用・改変し、再利用できるようにしたものが基になっています。

## how to install

```:
pip install auraboros
```

## how to use CLI

```:
python -m auraboros 
```

## how to PyInstaller

失敗した際に
実行ファイル化時に表示されたログにLoading module hook 'hook-auraboros'の記載がない場合、
リポジトリ、またはインストールしたパッケージのフォルダ内の__pyinstallerフォルダにあるhook-auraboros.pyをsite-package内のPyInstallerのフォルダに置いてください。
