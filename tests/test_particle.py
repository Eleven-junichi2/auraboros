import pytest

from src.auraboros.particle import Particle, Emitter


class TestParticle:
    particle: Particle

    @classmethod
    def setup_class(cls):
        cls.particle = Particle()

    @pytest.mark.run(order=1)
    def test_let_move(self):
        self.particle.let_move()
        assert self.particle.is_moving

    @pytest.mark.run(order=2)
    def test_let_freeze(self):
        self.particle.let_freeze()
        assert not self.particle.is_moving


class TestEmitter:
    emitter: Emitter

    @classmethod
    def setup_class(cls):
        cls.emitter = Emitter()

    @pytest.mark.run(order=1)
    def test_let_move(self):
        self.emitter.let_emit()
        assert self.emitter.is_emitting

    @pytest.mark.run(order=2)
    def test_let_freeze(self):
        self.emitter.let_freeze()
        assert not self.emitter.is_emitting
