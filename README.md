# Auraboros

[Japanese（日本語）](./README.jp.md)

A game framework using pygame.
(This project is made for me, reducing the burden of game dev using pygame.)

## Features

- Basic Entity Component System
- Basic UI
  - Text
  - Button
  - Flow Layout
  - Menu UI
- State Machine
- Scene management
- Custom vertex / pixel shaders
- [hook](./src/auraboros/__pyinstaller/hook-auraboros.py) for PyInstaller

## How to install

```:
pip install auraboros
```

## How to use CLI

```:
python -m auraboros

# run examples
python -m auraboros --example

# download assets
python -m auraboros --getasset
```
