import math
import random
from typing import Any, Callable

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


def saltire_diffusion(particle: Particle) -> Particle:
    vx = random.randint(-1, 1)
    vy = random.randint(-1, 1)
    if vx == 0 and vy == 0:
        if random.getrandbits(1) > 0:
            vx = random.choice((-1, 1))
        else:
            vy = random.choice((-1, 1))
    particle.vx = vx
    particle.vy = vy
    return particle


def random_angle_diffusion(particle: Particle) -> Particle:
    angle = random.randrange(0, 360)
    speed = 1
    vx = speed * math.sin(angle)
    vy = speed * math.cos(angle)
    particle.vx = vx
    particle.vy = vy
    return particle


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
        self.particle_programs: dict[Any, Callable[[Particle], Particle]] = {
            "saltire_diffusion": saltire_diffusion,
            "random_angle_diffusion": random_angle_diffusion, }
        self.current_program_name = "random_angle_diffusion"

    def register_particle_program(
            self, program: Callable[[Particle], Particle], program_name):
        self.particle_programs[program_name] = program

    def set_current_program(self, program_name):
        self.current_program_name = program_name

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
                    particle = self.particle_programs[
                        self.current_program_name](particle)
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
