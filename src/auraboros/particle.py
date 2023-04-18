import abc
import math
import random

import pygame

from .schedule import Stopwatch


class Particle:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 1
        self.vy = 1
        self.lifetime = 2000  # -1 means endless lifetime.
        self.size = 3
        self.color = (255, 255, 255)
        self.is_moving = False
        self._lifetimer = Stopwatch()

    def let_move(self):
        if not self.is_moving:
            self._lifetimer.start()
        self.is_moving = True

    def let_freeze(self):
        if self.is_moving:
            self._lifetimer.stop()
        self.is_moving = False

    def reset_life(self):
        self._lifetimer.reset()

    def update(self):
        if self.is_moving:
            if not self.is_lifetime_end() or self.lifetime < 0:
                self.x += self.vx
                self.y += self.vy

    def is_lifetime_end(self) -> bool:
        return self._lifetimer.read() >= self.lifetime

    def draw(self, surface):
        pygame.draw.circle(surface, self.color,
                           (int(self.x), int(self.y)), self.size)


class ParticleProgram(metaclass=abc.ABCMeta):

    @classmethod
    def __init__(cls, particle: Particle) -> "program":
        cls.particle = particle

    @classmethod
    @abc.abstractmethod
    def program(cls, particle: Particle):
        raise NotImplementedError()

    @classmethod
    def run(cls):
        cls.program()
        return cls.particle


class SaltireDiffusion(ParticleProgram):
    @classmethod
    def program(cls):
        vx = random.randint(-1, 1)
        vy = random.randint(-1, 1)
        if vx == 0 and vy == 0:
            if random.getrandbits(1) > 0:
                vx = random.choice((-1, 1))
            else:
                vy = random.choice((-1, 1))
        cls.particle.vx = vx
        cls.particle.vy = vy


class Emitter:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.lifetime = 2000  # -1 means endless lifetime.
        self.particles: list[Particle] = []
        self.how_many_emit = -1  # -1 means endless during lifetime.
        self.emitted_counter = 0
        self.is_emitting = False
        self._lifetimer = Stopwatch()

    def let_emit(self):
        if not self.is_emitting:
            self._lifetimer.start()
        self.is_emitting = True

    def let_freeze(self):
        if self.is_emitting:
            self._lifetimer.stop()
        self.is_emitting = False

    def reset(self):
        self.particles.clear()
        self.emitted_counter = 0
        self._lifetimer.reset()

    def reset_lifetime_count(self):
        self._lifetimer.reset()

    def erase_finished_particles(self):
        for i, particle in enumerate(self.particles):
            if particle.is_lifetime_end():
                del self.particles[i]

    def update(self):
        if self.is_emitting:
            if not self.is_lifetime_end() or self.lifetime < 0:
                if self.emitted_counter < self.how_many_emit or \
                        self.how_many_emit < 0:
                    particle = Particle()
                    particle.x = self.x
                    particle.y = self.y
                    particle = SaltireDiffusion(particle).run()
                    particle.let_move()
                    self.particles.append(particle)
                    self.emitted_counter += 1
        if self.particles:
            for particle in self.particles:
                particle.update()

    def is_lifetime_end(self) -> bool:
        return self._lifetimer.read() >= self.lifetime

    def is_particles_lifetime_end(self) -> bool:
        is_end = []
        for particle in self.particles:
            if particle.is_lifetime_end():
                is_end.append(True)
            else:
                is_end.append(False)
        if all(is_end):
            return True
        else:
            return False

    def draw(self, screen: pygame.surface.Surface):
        for particle in self.particles:
            particle.draw(screen)

    # def let_emit(self):
    #     self.is_emitting = True
    #     self.is_pausing = False

    # def let_pause(self):
    #     self.is_emitting = False
    #     self.is_pausing = True

    # def is_lifetime_end(self):
    #     if self._spawn_time:
    #         _current_time = pygame.time.get_ticks()
    #         return _current_time - self._spawn_time >= self.lifetime
    #     else:
    #         return False

    # def respawn(self):
    #     self._spawn_time = pygame.time.get_ticks()
    #     self.emitted_counter = 0

    # def update(self):
    #     _current_time = pygame.time.get_ticks()
    #     if self.is_emitting:
    #         if self._spawn_time is None:
    #             self.respawn()
    #         if not _current_time - self._spawn_time >= self.lifetime:
    #             if self.emitted_counter < self.how_many_emit or \
    #                     self.how_many_emit < 0:
    #                 particle = Particle()
    #                 particle.x = self.x
    #                 particle.y = self.y
    #                 speed = 1
    #                 angle = random.uniform(0, 360)
    #                 particle.vx = speed * math.cos(math.radians(angle))
    #                 particle.vy = speed * math.sin(math.radians(angle))
    #                 self.particles.append(particle)
    #                 self.emitted_counter += 1
    #         else:
    #             self.is_emitting = False
    #     if not self.is_pausing:
    #         for particle in self.particles:
    #             particle.update()
    #             if _current_time - particle._spawn_time >= particle.lifetime:
    #                 self.particles.remove(particle)

    # def draw(self, screen: pygame.surface.Surface):
    #     for particle in self.particles:
    #         particle.draw(screen)


class OldParticle:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 1
        self.vy = 1
        self.lifetime = 2000
        self.size = 3
        self.color = (255, 255, 255)
        self._spawn_time = None
        # self.size

    def update(self):
        if self._spawn_time is None:
            self._spawn_time = pygame.time.get_ticks()
        _current_time = pygame.time.get_ticks()
        if not _current_time - self._spawn_time >= self.lifetime:
            self.x += self.vx
            self.y += self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, self.color,
                           (int(self.x), int(self.y)), self.size)


class OldEmitter:
    def __init__(self):
        self.x = 0
        self.y = 0
        # self.rate = rate
        self.lifetime = 1000
        self.particles: list[Particle] = []
        self.how_many_emit = -1  # -1 means endless during lifetime.
        self.emitted_counter = 0
        self._spawn_time = None
        self.is_emitting = False
        self.is_pausing = False

    def let_emit(self):
        self.is_emitting = True
        self.is_pausing = False

    def let_pause(self):
        self.is_emitting = False
        self.is_pausing = True

    def is_lifetime_end(self):
        if self._spawn_time:
            _current_time = pygame.time.get_ticks()
            return _current_time - self._spawn_time >= self.lifetime
        else:
            return False

    def respawn(self):
        self._spawn_time = pygame.time.get_ticks()
        self.emitted_counter = 0

    def update(self):
        _current_time = pygame.time.get_ticks()
        if self.is_emitting:
            if self._spawn_time is None:
                self.respawn()
            if not _current_time - self._spawn_time >= self.lifetime:
                if self.emitted_counter < self.how_many_emit or \
                        self.how_many_emit < 0:
                    particle = Particle()
                    particle.x = self.x
                    particle.y = self.y
                    speed = 1
                    angle = random.uniform(0, 360)
                    particle.vx = speed * math.cos(math.radians(angle))
                    particle.vy = speed * math.sin(math.radians(angle))
                    self.particles.append(particle)
                    self.emitted_counter += 1
            else:
                self.is_emitting = False
        if not self.is_pausing:
            for particle in self.particles:
                particle.update()
                if _current_time - particle._spawn_time >= particle.lifetime:
                    self.particles.remove(particle)

    def draw(self, screen: pygame.surface.Surface):
        for particle in self.particles:
            particle.draw(screen)
