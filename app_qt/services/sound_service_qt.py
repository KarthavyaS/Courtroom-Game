"""Sound Effect and Background Music Manager for PySide6 LOGIC COURTROOM.
Utilizes PySide6.QtMultimedia (QSoundEffect & QMediaPlayer) with automatic WAV generation
and graceful fallbacks.
"""

import math
import struct
import wave
from pathlib import Path
from typing import Optional, Dict

from PySide6.QtCore import QObject, QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer, QSoundEffect

from app_qt.config import SOUNDS_DIR


class SoundServiceQt(QObject):
    """Singleton audio service for PySide6."""

    _instance: Optional["SoundServiceQt"] = None

    @classmethod
    def get_instance(cls) -> "SoundServiceQt":
        if cls._instance is None:
            cls._instance = SoundServiceQt()
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_muted = False
        self.sfx_volume = 0.85
        self.music_volume = 0.85
        self.sound_enabled = True
        self.music_enabled = True

        self.sounds: Dict[str, QSoundEffect] = {}
        self.music_player: Optional[QSoundEffect] = None

        self._ensure_sound_files()
        self._init_sound_effects()
        self._init_music_player()

    def _ensure_sound_files(self):
        """Ensures all standard procedural courtroom sound effects are saved as clean WAV files."""
        SOUNDS_DIR.mkdir(parents=True, exist_ok=True)

        effects = [
            ("click.wav", 600, 0.04, True, "sine"),
            ("gavel.wav", 110, 0.35, True, "gavel"),
            ("evidence.wav", 880, 0.18, True, "sine"),
            ("warning.wav", 170, 0.35, False, "saw"),
            ("type.wav", 1200, 0.02, True, "sine"),
            ("dossier.wav", 420, 0.08, True, "sine"),
            ("objection.wav", 240, 0.25, True, "saw"),
            ("verdict.wav", 523, 0.50, True, "sine")
        ]

        sample_rate = 22050
        for filename, freq, dur, decay, wave_type in effects:
            file_path = SOUNDS_DIR / filename
            if not file_path.exists():
                try:
                    num_samples = int(sample_rate * dur)
                    raw_data = bytearray()
                    for i in range(num_samples):
                        t = float(i) / sample_rate
                        env = max(0.0, 1.0 - (float(i) / num_samples)) if decay else 1.0

                        if wave_type == "gavel":
                            val = (math.sin(2 * math.pi * freq * t) * 0.7 +
                                   math.sin(2 * math.pi * (freq * 0.5) * t) * 0.3) * (env * env)
                        elif wave_type == "saw":
                            val = (2.0 * (t * freq - math.floor(0.5 + t * freq))) * 0.5 * env
                        else:
                            val = math.sin(2 * math.pi * freq * t) * env

                        sample = int(val * 16000)
                        sample = max(-32767, min(32767, sample))
                        # 16-bit signed little-endian mono
                        raw_data.extend(struct.pack("<h", sample))

                    with wave.open(str(file_path), "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(sample_rate)
                        wf.writeframes(raw_data)
                except Exception:
                    pass

    def _init_sound_effects(self):
        """Preloads QSoundEffect instances for low-latency playback."""
        sound_mappings = {
            "click": "click.wav",
            "gavel": "gavel.wav",
            "evidence": "evidence.wav",
            "warning": "warning.wav",
            "type": "type.wav",
            "typewriter": "type.wav",
            "dossier": "dossier.wav",
            "page_turn": "dossier.wav",
            "objection": "objection.wav",
            "verdict": "verdict.wav",
            "success": "verdict.wav"
        }

        for name, filename in sound_mappings.items():
            path = SOUNDS_DIR / filename
            if path.exists():
                try:
                    effect = QSoundEffect(self)
                    effect.setSource(QUrl.fromLocalFile(str(path)))
                    effect.setVolume(self.sfx_volume)
                    self.sounds[name] = effect
                except Exception:
                    pass

    def _init_music_player(self):
        """Initializes ambient background music using lightweight native QSoundEffect."""
        try:
            theme_file = SOUNDS_DIR / "thriller_horror_theme.wav"
            if theme_file.exists():
                self.music_player = QSoundEffect(self)
                self.music_player.setSource(QUrl.fromLocalFile(str(theme_file)))
                self.music_player.setLoopCount(QSoundEffect.Loop.Infinite.value)
                vol = self.music_volume if (self.music_enabled and not self.is_muted) else 0.0
                self.music_player.setVolume(vol)
                if self.music_enabled and not self.is_muted:
                    self.music_player.play()
        except Exception:
            pass

    def play(self, sound_name: str):
        """Plays a registered sound effect."""
        if self.is_muted or not self.sound_enabled:
            return
        effect = self.sounds.get(sound_name)
        if effect:
            try:
                effect.setVolume(self.sfx_volume)
                effect.play()
            except Exception:
                pass

    def set_sound_enabled(self, enabled: bool):
        self.sound_enabled = enabled

    def set_music_enabled(self, enabled: bool):
        self.music_enabled = enabled
        if self.music_player:
            if enabled and not self.is_muted:
                self.music_player.setVolume(self.music_volume)
                if not self.music_player.isPlaying():
                    self.music_player.play()
            else:
                self.music_player.stop()

    def set_volume(self, volume: float):
        vol = max(0.0, min(1.0, float(volume)))
        self.sfx_volume = vol * 0.85
        self.music_volume = vol * 0.85
        if self.music_player:
            self.music_player.setVolume(self.music_volume if (self.music_enabled and not self.is_muted) else 0.0)
        for s in self.sounds.values():
            s.setVolume(self.sfx_volume)

    def set_muted(self, muted: bool):
        self.is_muted = muted
        if self.music_player:
            self.music_player.setVolume(0.0 if muted else self.music_volume)


def get_sound_service_qt() -> SoundServiceQt:
    return SoundServiceQt.get_instance()

