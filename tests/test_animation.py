from pygame.surface import Surface
from src.auraboros.animation import AnimationImage


def test_anim_frames():
    animation = AnimationImage()
    animation.anim_frames = [
        Surface((32, 32)),
        Surface((32, 32)),
        Surface((32, 32))
    ]
    assert len(animation.anim_frames) == 3


def test_anim_interval():
    animation = AnimationImage()
    animation.anim_interval = 500
    assert animation.anim_interval == 500


def test_is_all_loop_finished():
    animation = AnimationImage()
    animation.loop_count = 2
    animation.loop_counter = 2
    assert animation.is_all_loop_finished()


def test_let_play():
    animation = AnimationImage()
    animation.is_playing = False
    animation.loop_count = 1
    animation.loop_counter = 1
    animation.let_play()
    assert animation.is_playing
    assert animation.loop_counter == 0


def test_let_stop():
    animation = AnimationImage()
    animation.is_playing = True
    animation.let_stop()
    assert not animation.is_playing


def test_seek():
    animation = AnimationImage()
    animation.anim_frames = [
        Surface((32, 32)),
        Surface((32, 32)),
        Surface((32, 32))
    ]
    animation.seek(1)
    assert animation.anim_frame_id == 1


def test_reset_current_loop():
    animation = AnimationImage()
    animation.anim_frames = [
        Surface((32, 32)),
        Surface((32, 32)),
        Surface((32, 32))
    ]
    animation.anim_frame_id = 2
    animation.reset_current_loop()
    assert animation.anim_frame_id == 0


def test_reset_animation():
    animation = AnimationImage()
    animation.anim_frames = [
        Surface((32, 32)),
        Surface((32, 32)),
        Surface((32, 32))
    ]
    animation.anim_frame_id = 2
    animation.loop_count = 1
    animation.loop_counter = 1
    animation.reset_animation()
    assert animation.anim_frame_id == 0
    assert animation.loop_counter == 0


def test_update_animation():
    animation = AnimationImage()
    animation.anim_frames = [
        Surface((32, 32)),
        Surface((32, 32)),
        Surface((32, 32))
    ]
    animation.anim_interval = 500
    animation.is_playing = True
    animation.loop_count = 1
    animation.update_animation()
    assert animation.anim_frame_id == 1
    animation.update_animation()
    assert animation.anim_frame_id == 2
    animation.update_animation()
    assert animation.anim_frame_id == 0
    assert not animation.is_playing
