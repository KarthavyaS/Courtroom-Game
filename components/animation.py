"""Delta-Time Based Animation System, Easing Functions, and Screen Transitions for LOGIC COURTROOM.
"""

import pygame
import math
import random
from typing import Callable, List, Dict, Any, Optional, Tuple

# Easing Functions
def ease_linear(t: float) -> float:
    return t

def ease_in_quad(t: float) -> float:
    return t * t

def ease_out_quad(t: float) -> float:
    return t * (2.0 - t)

def ease_in_out_quad(t: float) -> float:
    return 2.0 * t * t if t < 0.5 else -1.0 + (4.0 - 2.0 * t) * t

def ease_out_back(t: float, overshoot: float = 1.70158) -> float:
    t = t - 1.0
    return t * t * ((overshoot + 1.0) * t + overshoot) + 1.0

def ease_out_bounce(t: float) -> float:
    if t < (1.0 / 2.75):
        return 7.5625 * t * t
    elif t < (2.0 / 2.75):
        t -= (1.5 / 2.75)
        return 7.5625 * t * t + 0.75
    elif t < (2.5 / 2.75):
        t -= (2.25 / 2.75)
        return 7.5625 * t * t + 0.9375
    else:
        t -= (2.625 / 2.75)
        return 7.5625 * t * t + 0.984375


class ScreenTransition:
    """Manages smooth cinematic transitions with shutter wipes, gold accent beams, and particle sweeps."""

    def __init__(self, duration: float = 0.28):
        self.duration = max(0.05, duration)
        self.time = 0.0
        self.state = "NONE"  # 'FADE_IN', 'FADE_OUT', 'NONE'
        self.on_midpoint_callback: Optional[Callable[[], None]] = None
        self.surface: Optional[pygame.Surface] = None
        self.transition_style = "CURTAIN"  # 'CURTAIN', 'BEAM', 'VIGNETTE'

    def start_transition(self, on_midpoint: Callable[[], None], style: str = "CURTAIN"):
        self.time = 0.0
        self.state = "FADE_OUT"
        self.transition_style = style
        self.on_midpoint_callback = on_midpoint

    def update(self, dt: float) -> bool:
        """Updates transition state. Returns True if transition is actively running."""
        if self.state == "NONE":
            return False

        self.time += dt
        progress = min(1.0, self.time / self.duration)

        if self.state == "FADE_OUT":
            if progress >= 1.0:
                if self.on_midpoint_callback:
                    self.on_midpoint_callback()
                    self.on_midpoint_callback = None
                self.state = "FADE_IN"
                self.time = 0.0
        elif self.state == "FADE_IN":
            if progress >= 1.0:
                self.state = "NONE"
                self.time = 0.0

        return True

    def draw(self, surface: pygame.Surface):
        if self.state == "NONE":
            return

        w, h = surface.get_size()
        progress = min(1.0, self.time / self.duration)

        if self.state == "FADE_OUT":
            e_prog = ease_in_out_quad(progress)
            curtain_w = int((w / 2) * e_prog)
            alpha = int(e_prog * 255)
        else:
            e_prog = 1.0 - ease_out_quad(progress)
            curtain_w = int((w / 2) * e_prog)
            alpha = int(e_prog * 255)

        # 1. Shutter Panels (Left & Right with gold trim)
        if curtain_w > 0:
            left_rect = pygame.Rect(0, 0, curtain_w, h)
            right_rect = pygame.Rect(w - curtain_w, 0, curtain_w, h)
            
            # Rich dark panel background
            pygame.draw.rect(surface, (18, 12, 9), left_rect)
            pygame.draw.rect(surface, (18, 12, 9), right_rect)

            # Luminous Gold Trim Lines
            if curtain_w < (w / 2):
                pygame.draw.line(surface, (255, 215, 65), (curtain_w, 0), (curtain_w, h), 3)
                pygame.draw.line(surface, (255, 235, 130), (curtain_w - 1, 0), (curtain_w - 1, h), 1)
                pygame.draw.line(surface, (255, 215, 65), (w - curtain_w, 0), (w - curtain_w, h), 3)
                pygame.draw.line(surface, (255, 235, 130), (w - curtain_w + 1, 0), (w - curtain_w + 1, h), 1)

        # 2. Ambient Overlay Tint
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((15, 10, 8, max(0, min(240, int(alpha * 0.75)))))
        surface.blit(overlay, (0, 0))

        # 3. Dynamic Center Beam / Lens Flare Sweep
        if self.state == "FADE_OUT":
            beam_y = int(progress * h)
            beam_surf = pygame.Surface((w, 8), pygame.SRCALPHA)
            beam_surf.fill((255, 225, 110, int(180 * (1.0 - abs(progress - 0.5) * 2))))
            surface.blit(beam_surf, (0, beam_y - 4))



class ParticleSystem:
    """Reusable visual particle generator for courtroom dust, shockwaves, and sparks."""

    def __init__(self, max_particles: int = 40):
        self.max_particles = max_particles
        self.particles: List[Dict[str, Any]] = []

    def emit(self, x: float, y: float, count: int = 5, color: Tuple[int, int, int] = (215, 175, 105), speed_mult: float = 1.0, shape: str = "circle"):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.0, 4.0) * speed_mult
            self.particles.append({
                "x": x,
                "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": 1.0,
                "decay": random.uniform(1.2, 2.5),
                "radius": random.uniform(2.0, 5.0),
                "color": color,
                "shape": shape
            })

    def emit_shockwave(self, x: float, y: float, color: Tuple[int, int, int] = (215, 175, 105)):
        self.particles.append({
            "x": x,
            "y": y,
            "vx": 0,
            "vy": 0,
            "life": 1.0,
            "decay": 2.0,
            "radius": 5.0,
            "max_radius": 65.0,
            "color": color,
            "shape": "ring"
        })

    def update(self, dt: float):
        surviving = []
        for p in self.particles:
            p["life"] -= p["decay"] * dt
            if p["life"] > 0:
                p["x"] += p["vx"] * (dt * 60.0)
                p["y"] += p["vy"] * (dt * 60.0)
                if p["shape"] == "ring":
                    p["radius"] += (p["max_radius"] - p["radius"]) * 6.0 * dt
                surviving.append(p)
        self.particles = surviving

    def draw(self, surface: pygame.Surface):
        for p in self.particles:
            alpha = max(0, min(255, int(p["life"] * 255)))
            col = (*p["color"][:3], alpha)

            if p["shape"] == "ring":
                r = int(p["radius"])
                if r > 2:
                    ring_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
                    pygame.draw.circle(ring_surf, col, (r + 2, r + 2), r, width=3)
                    surface.blit(ring_surf, (int(p["x"] - r - 2), int(p["y"] - r - 2)))
            else:
                r = int(p["radius"] * p["life"])
                if r > 0:
                    dot_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
                    pygame.draw.circle(dot_surf, col, (r + 1, r + 1), r)
                    surface.blit(dot_surf, (int(p["x"] - r - 1), int(p["y"] - r - 1)))


class ScreenShake:
    """Manages dramatic camera screenshake on gavel impacts, objections, and shocks."""
    def __init__(self):
        self.duration = 0.0
        self.intensity = 0.0
        self.offset_x = 0
        self.offset_y = 0

    def trigger(self, duration: float = 0.4, intensity: float = 8.0):
        self.duration = duration
        self.intensity = intensity

    def update(self, dt: float):
        if self.duration > 0:
            self.duration -= dt
            self.offset_x = random.uniform(-self.intensity, self.intensity)
            self.offset_y = random.uniform(-self.intensity, self.intensity)
            self.intensity = max(0.0, self.intensity - (dt * 15.0))
        else:
            self.offset_x = 0
            self.offset_y = 0

    def get_offset(self) -> Tuple[int, int]:
        return int(self.offset_x), int(self.offset_y)


class ObjectionBanner:
    """Renders high-impact dramatic interjection banners ('OBJECTION!', 'HOLD IT!', 'TAKE THAT!')."""
    def __init__(self):
        self.active = False
        self.timer = 0.0
        self.duration = 1.2
        self.text = "OBJECTION!"
        self.speaker = "Defense Counsel"
        self.scale = 2.5
        self.particles = ParticleSystem(max_particles=30)

    def trigger(self, text: str = "OBJECTION!", speaker: str = "Defense Counsel"):
        self.active = True
        self.timer = 0.0
        self.text = text
        self.speaker = speaker
        self.scale = 2.8
        self.particles.emit(550, 340, count=25, color=(255, 215, 80), speed_mult=3.0)
        self.particles.emit_shockwave(550, 340, color=(255, 100, 80))

    def update(self, dt: float):
        if not self.active:
            return
        self.timer += dt
        self.particles.update(dt)
        # Slam scale down to 1.0 with overshoot
        if self.timer < 0.25:
            t = self.timer / 0.25
            self.scale = 2.8 - ease_out_back(t) * 1.8
        else:
            self.scale = 1.0

        if self.timer >= self.duration:
            self.active = False

    def draw(self, surface: pygame.Surface, font_func: Any):
        if not self.active:
            return

        w, h = surface.get_size()
        # Dark dramatic letterbox backdrop with red streak
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        alpha = int(min(180, (1.0 - (self.timer / self.duration) ** 2) * 220))
        overlay.fill((15, 8, 8, alpha))

        # Dynamic red banner stripe across screen
        stripe_h = 130
        stripe_rect = pygame.Rect(0, (h - stripe_h) // 2 - 20, w, stripe_h)
        pygame.draw.rect(overlay, (180, 25, 20, min(240, alpha + 30)), stripe_rect)
        pygame.draw.line(overlay, (255, 215, 90), (0, stripe_rect.y), (w, stripe_rect.y), 3)
        pygame.draw.line(overlay, (255, 215, 90), (0, stripe_rect.bottom), (w, stripe_rect.bottom), 3)

        # Starburst / Speedlines
        for i in range(16):
            ang = (i / 16.0) * math.pi * 2 + (self.timer * 4.0)
            lx = 550 + math.cos(ang) * 450
            ly = 320 + math.sin(ang) * 200
            pygame.draw.line(overlay, (255, 240, 150, min(140, alpha)), (550, 320), (lx, ly), 2)

        surface.blit(overlay, (0, 0))
        self.particles.draw(surface)

        # Scaled Text rendering
        base_font = font_func(int(42 * max(0.5, self.scale)), bold=True)
        t_surf = base_font.render(f"★ {self.text} ★", True, (255, 235, 120))
        t_shadow = base_font.render(f"★ {self.text} ★", True, (40, 0, 0))

        tx = (w - t_surf.get_width()) // 2
        ty = (h - t_surf.get_height()) // 2 - 25
        surface.blit(t_shadow, (tx + 4, ty + 4))
        surface.blit(t_surf, (tx, ty))

        # Subtitle speaker tag
        sub_font = font_func(14, bold=True)
        s_surf = sub_font.render(f"— {self.speaker.upper()} INTERJECTS —", True, (255, 255, 255))
        surface.blit(s_surf, ((w - s_surf.get_width()) // 2, ty + t_surf.get_height() + 8))


class WaxSealStamp:
    """Renders an authentic royal courtroom wax seal stamp animation for verdicts."""
    def __init__(self):
        self.active = False
        self.timer = 0.0
        self.duration = 2.0
        self.text = "GUILTY BEYOND DOUBT"
        self.is_won = True
        self.y_pos = -150.0
        self.particles = ParticleSystem(max_particles=40)

    def trigger(self, text: str = "GUILT PROVEN", is_won: bool = True):
        self.active = True
        self.timer = 0.0
        self.text = text
        self.is_won = is_won
        self.y_pos = -120.0

    def update(self, dt: float):
        if not self.active:
            return
        self.timer += dt
        self.particles.update(dt)

        # Fall and slam stamp onto paper
        if self.timer < 0.4:
            t = self.timer / 0.4
            self.y_pos = -120.0 + ease_out_bounce(t) * 220.0
            if t >= 0.95 and len(self.particles.particles) == 0:
                self.particles.emit(550, int(self.y_pos), count=30, color=(255, 215, 100), speed_mult=2.5)
                self.particles.emit_shockwave(550, int(self.y_pos), color=(220, 50, 40) if self.is_won else (180, 140, 50))
        else:
            self.y_pos = 100.0

    def draw(self, surface: pygame.Surface, font_func: Any):
        if not self.active:
            return

        cx, cy = 550, int(self.y_pos)
        self.particles.draw(surface)

        # Wax Stamp Circle Body
        radius = 65
        seal_color = (175, 30, 25) if self.is_won else (150, 105, 35)
        pygame.draw.circle(surface, seal_color, (cx, cy), radius)
        pygame.draw.circle(surface, (255, 215, 90), (cx, cy), radius - 4, width=2)
        pygame.draw.circle(surface, (255, 235, 130), (cx, cy), radius - 10, width=1)

        f_seal = font_func(14, bold=True)
        txt = "PROVEN" if self.is_won else "DISMISSED"
        t_surf = f_seal.render(txt, True, (255, 240, 180))
        surface.blit(t_surf, t_surf.get_rect(center=(cx, cy)))


class VolumetricLightRays:
    """Renders atmospheric sunbeams / light rays drifting through courtroom stained glass."""
    def __init__(self):
        self.time = 0.0

    def update(self, dt: float):
        self.time += dt

    def draw(self, surface: pygame.Surface):
        w, h = surface.get_size()
        ray_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # 3 soft animated light rays
        rays = [
            (180, 0, 120, 0.4),
            (550, 0, 160, 0.6),
            (880, 0, 130, 0.5)
        ]
        for start_x, start_y, beam_w, speed in rays:
            sway = math.sin(self.time * speed) * 35.0
            alpha = int(18 + math.sin(self.time * (speed * 1.5)) * 10)
            
            # Polygon beam points
            p1 = (start_x - 30, start_y)
            p2 = (start_x + 30, start_y)
            p3 = (start_x + beam_w + int(sway) + 140, h)
            p4 = (start_x + int(sway) - 80, h)
            
            pygame.draw.polygon(ray_surf, (255, 235, 170, alpha), [p1, p2, p3, p4])

        surface.blit(ray_surf, (0, 0))


class ScalesOfJustice:
    """Renders dynamic animated golden Scales of Justice tilting based on jury persuasion."""
    def __init__(self, x: int = 550, y: int = 48):
        self.x = x
        self.y = y
        self.current_tilt = 0.0
        self.time = 0.0

    def update(self, dt: float, jury_persuasion: float):
        self.time += dt
        # -1.0 (suspect favored) to +1.0 (lawyer/guilt proven)
        target_tilt = (jury_persuasion - 50.0) / 50.0
        self.current_tilt += (target_tilt - self.current_tilt) * min(1.0, 5.0 * dt)

    def draw(self, surface: pygame.Surface):
        t = self.time
        cx, cy = self.x, self.y
        tilt_angle = self.current_tilt * 0.28 + math.sin(t * 1.5) * 0.03
        bar_len = 65

        # Central Golden Stand
        pygame.draw.line(surface, (180, 140, 50), (cx, cy), (cx, cy + 50), 3)
        pygame.draw.circle(surface, (255, 215, 70), (cx, cy), 6)

        # Tilting Crossbar
        dx = math.cos(tilt_angle) * bar_len
        dy = math.sin(tilt_angle) * bar_len
        left_end = (cx - dx, cy - dy)
        right_end = (cx + dx, cy + dy)
        pygame.draw.line(surface, (255, 215, 70), left_end, right_end, 3)

        # Hanging scale pans
        for px, py, is_left in [(left_end[0], left_end[1], True), (right_end[0], right_end[1], False)]:
            pan_drop = 30 + math.sin(t * 2.0 + (0 if is_left else math.pi)) * 3
            pan_bottom = (px, py + pan_drop)
            # Strings
            pygame.draw.line(surface, (200, 165, 80), (px, py), (px - 14, py + pan_drop), 1)
            pygame.draw.line(surface, (200, 165, 80), (px, py), (px + 14, py + pan_drop), 1)
            # Pan curve
            pan_rect = pygame.Rect(px - 16, py + pan_drop - 3, 32, 10)
            pygame.draw.arc(surface, (255, 225, 90), pan_rect, 0, math.pi, 2)


class CourtroomChandelier:
    """Animated ornate Victorian brass chandeliers that gently sway from the ceiling casting warm light."""
    def __init__(self, x: int, y: int = 0, length: int = 60, swing_speed: float = 1.2, phase: float = 0.0):
        self.x = x
        self.y = y
        self.length = length
        self.swing_speed = swing_speed
        self.phase = phase
        self.time = 0.0

    def update(self, dt: float):
        self.time += dt

    def draw(self, surface: pygame.Surface):
        t = self.time * self.swing_speed + self.phase
        angle = math.sin(t) * 0.08  # subtle pendulum sway
        
        # Pendulum rod end
        end_x = self.x + math.sin(angle) * self.length
        end_y = self.y + math.cos(angle) * self.length

        # Brass hanging chain
        pygame.draw.line(surface, (140, 105, 45), (self.x, self.y), (end_x, end_y), 2)

        # Chandelier Tier Ring
        ring_w = 42
        ring_h = 10
        ring_rect = pygame.Rect(end_x - ring_w // 2, end_y - ring_h // 2, ring_w, ring_h)
        pygame.draw.ellipse(surface, (190, 145, 55), ring_rect, width=2)
        pygame.draw.ellipse(surface, (255, 215, 80), ring_rect.inflate(-4, -4), width=1)

        # 3 Candle Flames with warm flickering glow
        flame_offsets = [-14, 0, 14]
        for off in flame_offsets:
            fx = end_x + off
            fy = end_y - 6
            flicker = math.sin(self.time * 8.0 + off) * 2.0
            
            # Candle Stick
            pygame.draw.line(surface, (230, 220, 200), (fx, fy), (fx, fy + 6), 2)
            # Flame core
            pygame.draw.circle(surface, (255, 240, 140), (fx, fy - 2 + flicker * 0.5), 3)
            pygame.draw.circle(surface, (255, 120, 40), (fx, fy - 4 + flicker * 0.5), 2)

        # Soft Ambient Downward Illumination Cone
        cone_surf = pygame.Surface((180, 220), pygame.SRCALPHA)
        cone_pts = [
            (90, 0),
            (0, 220),
            (180, 220)
        ]
        alpha = int(14 + math.sin(t * 2.0) * 4)
        pygame.draw.polygon(cone_surf, (255, 235, 140, alpha), cone_pts)
        surface.blit(cone_surf, (end_x - 90, end_y))


class CourtroomGallery:
    """Animated Victorian Juror & Spectator Silhouettes in the upper gallery with bobbing heads and murmurs."""
    def __init__(self, start_x: int = 50, start_y: int = 68, count: int = 7):
        self.start_x = start_x
        self.start_y = start_y
        self.count = count
        self.time = 0.0

    def update(self, dt: float):
        self.time += dt

    def draw(self, surface: pygame.Surface):
        # Render a subtle wooden gallery balustrade
        gal_rect = pygame.Rect(self.start_x, self.start_y + 16, 200, 10)
        pygame.draw.rect(surface, (45, 30, 22), gal_rect, border_radius=3)
        pygame.draw.line(surface, (120, 85, 45), (self.start_x, self.start_y + 16), (self.start_x + 200, self.start_y + 16), 1)

        # Draw Spectator Silhouettes with gentle bobbing
        for i in range(self.count):
            bob = math.sin(self.time * 2.0 + i * 1.2) * 2.0
            sx = self.start_x + 12 + i * 26
            sy = self.start_y + 8 + bob

            # Head
            pygame.draw.circle(surface, (70, 50, 40), (sx, sy), 7)
            # Shoulders / Torso
            pygame.draw.ellipse(surface, (40, 28, 22), (sx - 9, sy + 5, 18, 12))
            # Hair / Hat on some
            if i % 2 == 0:
                pygame.draw.rect(surface, (25, 18, 14), (sx - 8, sy - 8, 16, 5), border_radius=2)


class CredibilityHeartbeatGauge:
    """Animated pulsating ECG Heartbeat credibility meter for high-stakes courtroom tension."""
    def __init__(self, x: int = 895, y: int = 58, width: int = 155, height: int = 48):
        self.rect = pygame.Rect(x, y, width, height)
        self.time = 0.0
        self.pulse_phase = 0.0

    def update(self, dt: float, credibility_pct: float = 100.0):
        self.time += dt
        speed = 2.0 + (1.0 - (credibility_pct / 100.0)) * 4.0
        self.pulse_phase = (self.pulse_phase + dt * speed) % 1.0

    def draw(self, surface: pygame.Surface, font_func: Any, strikes: int = 0):
        from components.ui_shapes import draw_chamfered_rect
        r = self.rect
        is_danger = strikes >= 2
        b_col = (235, 55, 50) if is_danger else (255, 215, 65)
        
        draw_chamfered_rect(surface, r, (28, 16, 14), b_col, cut=6, border_width=1, corner_brackets=True)

        # Header
        f = font_func(12, bold=True)
        lbl_col = (255, 120, 100) if is_danger else (255, 235, 130)
        surface.blit(f.render("COURT DISCIPLINE", True, lbl_col), (r.x + 10, r.y + 4))

        # Animated ECG Pulse Waveform in center
        ecg_surf = pygame.Surface((r.width - 20, 12), pygame.SRCALPHA)
        ecg_pts = []
        wave_w = ecg_surf.get_width()
        for i in range(0, wave_w, 4):
            rel_x = i / float(wave_w)
            # Pulse spike around pulse_phase
            dist = abs(rel_x - self.pulse_phase)
            if dist < 0.08:
                spike = math.sin((dist / 0.08) * math.pi) * 5.0
            else:
                spike = math.sin(self.time * 6.0 + i) * 1.0
            ecg_pts.append((i, 6 - spike))
            
        if len(ecg_pts) > 1:
            pygame.draw.lines(ecg_surf, (255, 80, 70) if is_danger else (100, 220, 120), False, ecg_pts, 2)
        surface.blit(ecg_surf, (r.x + 10, r.y + 19))

        # 3 Warning Strike Pips
        for i in range(3):
            pip_x = r.x + 16 + i * 44
            pip_y = r.y + 32
            is_struck = (i < strikes)
            pip_col = (235, 55, 50) if is_struck else (60, 45, 35)
            pygame.draw.circle(surface, pip_col, (pip_x, pip_y), 6)
            pygame.draw.circle(surface, (255, 215, 65) if not is_struck else (255, 120, 120), (pip_x, pip_y), 6, width=1)
            p_lbl = font_func(10, bold=True).render("!" if is_struck else f"#{i+1}", True, (255, 255, 255) if is_struck else (180, 170, 160))
            surface.blit(p_lbl, p_lbl.get_rect(center=(pip_x, pip_y)))


class CrowdMurmur:
    """Floating comic-style juror and gallery murmur thought bubbles."""
    def __init__(self):
        self.bubbles: List[Dict[str, Any]] = []
        self.spawn_timer = 2.0

    def trigger_reaction(self, text: str, x: int, y: int, color: Tuple[int, int, int] = (255, 235, 140)):
        self.bubbles.append({
            "text": text,
            "x": float(x),
            "y": float(y),
            "orig_y": float(y),
            "life": 1.8,
            "color": color
        })

    def update(self, dt: float):
        surviving = []
        for b in self.bubbles:
            b["life"] -= dt
            b["y"] -= dt * 25.0
            if b["life"] > 0:
                surviving.append(b)
        self.bubbles = surviving

    def draw(self, surface: pygame.Surface, font_func: Any):
        for b in self.bubbles:
            alpha = max(0, min(255, int((b["life"] / 1.8) * 255)))
            f = font_func(12, bold=True)
            txt_surf = f.render(b["text"], True, b["color"])
            
            # Bubble pill backdrop
            bw = txt_surf.get_width() + 18
            bh = txt_surf.get_height() + 10
            bx = int(b["x"] - bw // 2)
            by = int(b["y"] - bh // 2)
            
            bubble_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
            pygame.draw.rect(bubble_surf, (20, 14, 10, min(220, alpha)), (0, 0, bw, bh), border_radius=6)
            pygame.draw.rect(bubble_surf, (255, 215, 80, alpha), (0, 0, bw, bh), width=1, border_radius=6)
            surface.blit(bubble_surf, (bx, by))
            
            txt_surf.set_alpha(alpha)
            surface.blit(txt_surf, (bx + 9, by + 5))




