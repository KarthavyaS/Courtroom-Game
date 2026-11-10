"""Sound Effect and Background Music Manager for LOGIC COURTROOM.
Plays courtroom audio effects (gavel strikes, evidence chimes, warnings) and
features a procedural Victorian courtroom ambient background music loop with safe fallbacks.
"""

#pyright: ignore
import pygame
import math
import array
from typing import Optional

class SoundService:
    """Manages audio playback, volume controls, courtroom ambient music, and procedural sound synthesis."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.is_muted = False
        self.sfx_volume = 0.85
        self.music_volume = 0.85
        self.sounds = {}
        self.mixer_available = False
        self.bg_music_sound: Optional[pygame.mixer.Sound] = None
        self.music_channel: Optional[pygame.mixer.Channel] = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.mixer_available = True
            pygame.mixer.set_num_channels(16)
            self.music_channel = pygame.mixer.Channel(0)
            self._generate_procedural_sounds()
            self._generate_procedural_music()
            self.start_background_music()
        except Exception as e:
            self.mixer_available = False

    def _generate_procedural_sounds(self):
        """Generates clean procedural courtroom sound effects using sine/square wave audio buffers."""
        if not self.mixer_available:
            return

        try:
            # 1. Click Sound (Short subtle wood tap)
            self.sounds["click"] = self._create_tone(freq=600, duration_sec=0.04, decay=True)
            # 2. Gavel Strike (Deep resonant courtroom boom)
            self.sounds["gavel"] = self._create_tone(freq=110, duration_sec=0.35, decay=True, wave_type="gavel")
            # 3. Evidence Collected Chime
            self.sounds["evidence"] = self._create_tone(freq=880, duration_sec=0.18, decay=True)
            # 4. Warning / Scold Buzz
            self.sounds["warning"] = self._create_tone(freq=170, duration_sec=0.35, decay=False, wave_type="saw")
            # 5. Typewriter Tick
            self.sounds["type"] = self._create_tone(freq=1200, duration_sec=0.02, decay=True)
            self.sounds["typewriter"] = self.sounds["type"]
            # 6. Dossier / Page Turn Sound
            self.sounds["dossier"] = self._create_tone(freq=420, duration_sec=0.08, decay=True)
            self.sounds["page_turn"] = self.sounds["dossier"]
            # 7. Objection / Drama Stinger
            self.sounds["objection"] = self._create_tone(freq=240, duration_sec=0.25, decay=True, wave_type="saw")
            # 8. Verdict Fanfare / Success
            self.sounds["verdict"] = self._create_tone(freq=523, duration_sec=0.5, decay=True)
            self.sounds["success"] = self.sounds["verdict"]
        except Exception:
            pass

    def _generate_procedural_music(self):
        """Synthesizes a Dark Thriller & Horror Investigation Theme (atmospheric spine-chilling loop)."""
        if not self.mixer_available:
            return

        import os
        from pathlib import Path
        sound_dir = Path(__file__).resolve().parent.parent / "assets" / "sounds"
        os.makedirs(sound_dir, exist_ok=True)
        horror_file = sound_dir / "thriller_horror_theme.wav"

        # If already synthesized and saved to disk, load instantly
        if horror_file.exists():
            try:
                self.bg_music_sound = pygame.mixer.Sound(str(horror_file))
                return
            except Exception:
                pass

        try:
            import wave
            sample_rate = 22050
            duration_sec = 12.0
            total_samples = int(sample_rate * duration_sec)
            buf = array.array("h")

            for i in range(total_samples):
                t = float(i) / sample_rate
                bar = int(t / 3.0) % 4
                t_in_bar = t % 3.0

                # 1. Sinister Diminished Sub-Bass Drone with Devil's Tritone
                if bar == 0:
                    f_bass, f_tri = 55.0, 77.78   # C - Eb
                elif bar == 1:
                    f_bass, f_tri = 51.91, 73.42  # G# - D
                elif bar == 2:
                    f_bass, f_tri = 46.25, 65.41  # F# - C (Tritone clash)
                else:
                    f_bass, f_tri = 61.74, 87.31  # B - F

                # Binaural anxiety pulse (1.6Hz beat frequency)
                drone = (
                    math.sin(2 * math.pi * f_bass * t) * 0.42 +
                    math.sin(2 * math.pi * (f_bass + 1.6) * t) * 0.32 +
                    math.sin(2 * math.pi * f_tri * t) * 0.28 +
                    math.sin(2 * math.pi * (f_bass * 0.5) * t) * 0.25
                )

                # 2. Dread Heartbeat (lub-dub every 1.5s)
                hb_cycle = t % 1.5
                hb_val = 0.0
                if hb_cycle < 0.22:
                    hb_env = math.exp(-22.0 * hb_cycle)
                    hb_val += math.sin(2 * math.pi * (50.0 - 15.0 * hb_cycle) * hb_cycle) * hb_env * 0.75
                elif 0.26 <= hb_cycle < 0.48:
                    dt2 = hb_cycle - 0.26
                    hb_env2 = math.exp(-26.0 * dt2)
                    hb_val += math.sin(2 * math.pi * (45.0 - 15.0 * dt2) * dt2) * hb_env2 * 0.60

                # 3. High Shivering Minor-2nd Tension Strings (Cold dread clash: 880Hz & 932Hz)
                tremolo = 1.0 + 0.35 * math.sin(2 * math.pi * 5.2 * t)
                tension = (
                    math.sin(2 * math.pi * 880.0 * t) * 0.14 +
                    math.sin(2 * math.pi * 932.33 * t) * 0.14 +
                    math.sin(2 * math.pi * 1760.0 * t) * 0.05
                ) * tremolo * (0.6 + 0.4 * math.sin(2 * math.pi * 0.33 * t))

                # 4. Ghostly Music Box / Chime Drops
                chime_val = 0.0
                chime_times = [(1.0, 622.25), (4.0, 587.33), (7.0, 739.99), (10.0, 698.46)]
                for ct, cf in chime_times:
                    if ct <= t < ct + 2.5:
                        cdt = t - ct
                        cenv = math.exp(-2.2 * cdt)
                        chime_val += (
                            math.sin(2 * math.pi * cf * cdt) * 0.30 +
                            math.sin(2 * math.pi * cf * 2.76 * cdt) * 0.12
                        ) * cenv

                raw = (drone * 0.45 + hb_val * 0.55 + tension * 0.35 + chime_val * 0.40)
                # Seamless crossfade at loop boundary
                if t < 0.25:
                    raw *= (t / 0.25)
                elif t > (duration_sec - 0.25):
                    raw *= ((duration_sec - t) / 0.25)

                # Soft saturation limiter for maximum punch without digital clipping
                compressed = math.tanh(raw * 1.3)
                sample = int(compressed * 24000)
                sample = max(-32767, min(32767, sample))
                buf.append(sample)
                buf.append(sample)

            # Save to disk for fast caching
            try:
                with wave.open(str(horror_file), "wb") as wf:
                    wf.setnchannels(2)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate)
                    wf.writeframes(buf.tobytes())
            except Exception:
                pass

            self.bg_music_sound = pygame.mixer.Sound(buffer=buf)
        except Exception:
            self.bg_music_sound = None

    def start_background_music(self):
        """Starts looping the atmospheric courtroom background music."""
        if not self.mixer_available or self.is_muted or not self.bg_music_sound:
            return
        try:
            if self.music_channel:
                self.music_channel.set_volume(self.music_volume)
                self.music_channel.play(self.bg_music_sound, loops=-1)
        except Exception:
            pass

    def stop_background_music(self):
        """Stops background music."""
        if self.music_channel:
            try:
                self.music_channel.stop()
            except Exception:
                pass

    def _create_tone(self, freq: float, duration_sec: float, decay: bool = True, wave_type: str = "sine") -> Optional[pygame.mixer.Sound]:
        try:
            sample_rate = 22050
            total_samples = int(sample_rate * duration_sec)
            buf = array.array("h")

            for i in range(total_samples):
                t = float(i) / sample_rate
                if decay:
                    env = max(0.0, 1.0 - (float(i) / total_samples))
                else:
                    env = 1.0

                if wave_type == "gavel":
                    val = math.sin(2 * math.pi * freq * t) * 0.7 + math.sin(2 * math.pi * (freq * 0.5) * t) * 0.3
                    val *= env * env
                elif wave_type == "saw":
                    val = (2.0 * (t * freq - math.floor(0.5 + t * freq))) * 0.5 * env
                else:
                    val = math.sin(2 * math.pi * freq * t) * env

                sample = int(val * 16000 * self.sfx_volume)
                buf.append(sample)
                buf.append(sample)

            return pygame.mixer.Sound(buffer=buf)
        except Exception:
            return None

    def play(self, sound_name: str):
        if self.is_muted or not self.mixer_available:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.set_volume(self.sfx_volume)
                snd.play()
            except Exception:
                pass

    def set_sound_enabled(self, enabled: bool) -> None:
        """Enables or disables sound effects playback."""
        self.sfx_volume = 0.7 if enabled else 0.0

    def set_music_enabled(self, enabled: bool) -> None:
        """Enables or disables background music loop."""
        if enabled:
            if not self.is_muted:
                self.start_background_music()
        else:
            self.stop_background_music()

    def set_volume(self, volume: float) -> None:
        """Sets master volume scale (0.0 to 1.0)."""
        vol = max(0.0, min(1.0, float(volume)))
        self.sfx_volume = vol * 0.85
        self.music_volume = vol * 0.85
        if self.music_channel:
            try:
                self.music_channel.set_volume(self.music_volume)
            except Exception:
                pass

    def toggle_mute(self) -> bool:
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.stop_background_music()
        else:
            self.start_background_music()
        return self.is_muted

_sound_service_singleton = None

def get_sound_service() -> SoundService:
    global _sound_service_singleton
    if _sound_service_singleton is None:
        _sound_service_singleton = SoundService()
    return _sound_service_singleton
