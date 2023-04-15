import math
import random

import pygame


class Particle:

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


class Emitter:
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
