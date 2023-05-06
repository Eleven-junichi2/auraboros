=================================
Auraboros Tutorials - Hello world
=================================

このチュートリアルは、Pygame初心者（Pygameを公式ドキュメント(https://www.pygame.org/docs/)のクイックスタートを動かせる程度だけ触ったことがある人）
の方も対象に意識して書いていますが、不備・不足があれば遠慮なくご指摘ください。

Pygameの基礎知識
------------------------------------

ゲームをプログラムするのに、最低限やりたいことは**描画**です。
**Pygameは、pygame.surface.Surfaceで描画を表現する** これを理解していれば、Pygameを使ったゲームプログラムは書けます。

そして、PygameはSDLのラップです。本家SDLのドキュメントや情報源からヒントを得られる部分があります。
行き詰まったらそちらでも調べてみるのが良いでしょう。

公式のhttp://www.pygame.org/docs/tut/newbieguide.html はPygameの本質を理解できる素晴らしいドキュメントです。
（日本語版:https://www.unixuser.org/~euske/doc/pygame/newbieguide-j.html）

helloworld.py
-------------

