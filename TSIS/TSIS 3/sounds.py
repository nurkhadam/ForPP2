"""
sounds.py  —  TSIS 3
Loads sound effects from assets/*.wav
"""

import pygame
import os

pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=512)
pygame.mixer.init()

SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "assets")

SOUND_FILES = {
    "coin":         "coin.wav",
    "gold_coin":    "gold_coin.wav",
    "crash":        "crash.wav",
    "nitro":        "nitro.wav",
    "shield":       "shield.wav",
    "powerup":      "powerup.wav",
    "obstacle_hit": "obstacle_hit.wav",
    "engine":       "engine.wav",
}

VOLUMES = {
    "coin":         0.6,
    "gold_coin":    0.7,
    "crash":        0.9,
    "nitro":        0.7,
    "shield":       0.6,
    "powerup":      0.65,
    "obstacle_hit": 0.5,
    "engine":       0.18,
}


class SoundManager:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._engine_channel = None

        if not enabled:
            return

        for name, filename in SOUND_FILES.items():
            path = os.path.join(SOUNDS_DIR, filename)
            try:
                snd = pygame.mixer.Sound(path)
                snd.set_volume(VOLUMES.get(name, 0.5))
                self._sounds[name] = snd
            except Exception as e:
                print(f"[SoundManager] could not load {path}: {e}")

    def play(self, name: str, loops: int = 0):
        if not self.enabled:
            return
        snd = self._sounds.get(name)
        if snd:
            try:
                snd.play(loops=loops)
            except Exception:
                pass

    def start_engine(self):
        if not self.enabled:
            return
        try:
            snd = self._sounds.get("engine")
            if snd and (self._engine_channel is None or
                        not self._engine_channel.get_busy()):
                self._engine_channel = snd.play(loops=-1)
        except Exception:
            pass

    def stop_engine(self):
        if self._engine_channel:
            try:
                self._engine_channel.stop()
            except Exception:
                pass
            self._engine_channel = None

    def set_engine_pitch(self, speed: int):
        if not self.enabled:
            return
        snd = self._sounds.get("engine")
        if snd:
            vol = min(0.40, 0.12 + speed * 0.015)
            snd.set_volume(vol)

    def stop_all(self):
        if not self.enabled:
            return
        pygame.mixer.stop()
        self._engine_channel = None