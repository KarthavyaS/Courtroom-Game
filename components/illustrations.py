"""Procedural Graphic Illustration Helpers and Animation Systems for LOGIC COURTROOM.
Features animated courtroom atmosphere particles, interactive Judge expressions,
speaking mouth animations, animated gavel slams, and forensic iconography.
"""
#pyright: ignore
import pygame
import math
import random
from typing import Tuple, List, Optional
from config import (
    WOOD_BROWN, DARK_BROWN, GOLD, GOLD_LIGHT, GOLD_DARK, LIGHT_PARCHMENT,
    WHITE, BLACK, ACCENT_RED, ACCENT_BLUE, ACCENT_GREEN, MUTED_TEXT, SCREEN_WIDTH, SCREEN_HEIGHT
)

class AmbientParticleSystem:
    """Creates floating ambient dust motes / gold sparks for vintage courtroom ambiance."""

    def __init__(self, count: int = 35):
        self.particles = []
        for _ in range(count):
            self.particles.append({
                "x": random.uniform(0, SCREEN_WIDTH),
                "y": random.uniform(0, SCREEN_HEIGHT),
                "speed_x": random.uniform(-0.3, 0.3),
                "speed_y": random.uniform(-0.4, -0.1),
                "radius": random.uniform(1.2, 3.2),
                "alpha": random.uniform(30, 90),
                "color": random.choice([GOLD_LIGHT, (250, 240, 210), GOLD])
            })

    def update(self):
        for p in self.particles:
            p["x"] += p["speed_x"]
            p["y"] += p["speed_y"]
            if p["y"] < 0:
                p["y"] = SCREEN_HEIGHT + 5
                p["x"] = random.uniform(0, SCREEN_WIDTH)
            if p["x"] < 0:
                p["x"] = SCREEN_WIDTH
            elif p["x"] > SCREEN_WIDTH:
                p["x"] = 0

    def draw(self, surface: pygame.Surface):
        for p in self.particles:
            alpha_surf = pygame.Surface((int(p["radius"] * 4), int(p["radius"] * 4)), pygame.SRCALPHA)
            col = (*p["color"][:3], int(p["alpha"]))
            pygame.draw.circle(alpha_surf, col, (int(p["radius"] * 2), int(p["radius"] * 2)), int(p["radius"]))
            surface.blit(alpha_surf, (int(p["x"]), int(p["y"])))


def draw_animated_judge(
    surface: pygame.Surface,
    rect: pygame.Rect,
    tick: int = 0,
    mood: str = "neutral",
    is_speaking: bool = False,
    gavel_strike_anim: int = 0
) -> None:
    """Draws an animated Victorian Judge with blinking, breathing, mouth movement, and gavel strikes."""
    # Background oval with gold trim
    pygame.draw.ellipse(surface, (45, 25, 15), rect)
    pygame.draw.ellipse(surface, GOLD, rect, 3)

    cx, cy = rect.centerx, rect.centery

    # Breathing head/torso bobbing
    breath = math.sin(tick * 0.05) * 1.5
    cy += breath

    # Judicial Robe
    robe_rect = pygame.Rect(cx - 50, cy + 12, 100, 65)
    pygame.draw.ellipse(surface, (20, 18, 18), robe_rect)
    # White Collar Jabot
    pygame.draw.polygon(surface, WHITE, [(cx - 16, cy + 16), (cx + 16, cy + 16), (cx, cy + 38)])
    pygame.draw.polygon(surface, (190, 190, 195), [(cx - 8, cy + 24), (cx + 8, cy + 24), (cx, cy + 40)], 1)

    # Face base
    face_color = (235, 195, 165)
    pygame.draw.ellipse(surface, face_color, (cx - 22, cy - 26, 44, 48))

    # Traditional Powdered Wig
    wig_color = (232, 232, 238)
    pygame.draw.ellipse(surface, wig_color, (cx - 28, cy - 44, 56, 38))
    # Wig side curls
    pygame.draw.circle(surface, wig_color, (cx - 26, cy - 16), 14)
    pygame.draw.circle(surface, wig_color, (cx + 26, cy - 16), 14)
    pygame.draw.circle(surface, wig_color, (cx - 28, cy + 4), 12)
    pygame.draw.circle(surface, wig_color, (cx + 28, cy + 4), 12)

    # Eyebrows
    eye_y = cy - 10
    if mood in ["stern", "displeased"]:
        pygame.draw.line(surface, (80, 50, 40), (cx - 16, eye_y - 9), (cx - 4, eye_y - 5), 3)
        pygame.draw.line(surface, (80, 50, 40), (cx + 16, eye_y - 9), (cx + 4, eye_y - 5), 3)
    elif mood == "satisfied":
        pygame.draw.arc(surface, (80, 50, 40), (cx - 16, eye_y - 12, 12, 8), 0, math.pi, 2)
        pygame.draw.arc(surface, (80, 50, 40), (cx + 4, eye_y - 12, 12, 8), 0, math.pi, 2)
    else:
        pygame.draw.arc(surface, (80, 50, 40), (cx - 16, eye_y - 10, 12, 8), 0, math.pi, 2)
        pygame.draw.arc(surface, (80, 50, 40), (cx + 4, eye_y - 10, 12, 8), 0, math.pi, 2)

    # Eyes with periodic blinking animation
    is_blinking = (tick % 160) > 152
    if is_blinking:
        pygame.draw.line(surface, DARK_BROWN, (cx - 14, eye_y), (cx - 6, eye_y), 2)
        pygame.draw.line(surface, DARK_BROWN, (cx + 6, eye_y), (cx + 14, eye_y), 2)
    else:
        # Pupil & highlight
        pygame.draw.circle(surface, DARK_BROWN, (cx - 10, eye_y), 4)
        pygame.draw.circle(surface, WHITE, (cx - 11, eye_y - 1), 1)
        pygame.draw.circle(surface, DARK_BROWN, (cx + 10, eye_y), 4)
        pygame.draw.circle(surface, WHITE, (cx + 9, eye_y - 1), 1)

    # Gold Spectacles
    pygame.draw.circle(surface, GOLD, (cx - 10, eye_y), 7, 2)
    pygame.draw.circle(surface, GOLD, (cx + 10, eye_y), 7, 2)
    pygame.draw.line(surface, GOLD, (cx - 3, eye_y), (cx + 3, eye_y), 2)

    # Nose
    pygame.draw.line(surface, (190, 150, 120), (cx, eye_y + 2), (cx - 2, eye_y + 11), 2)
    pygame.draw.line(surface, (190, 150, 120), (cx - 2, eye_y + 11), (cx + 3, eye_y + 11), 2)

    # Mouth with speaking animation
    mouth_y = cy + 14
    if is_speaking:
        mouth_open = (math.sin(tick * 0.4) + 1.0) * 3
        pygame.draw.ellipse(surface, (90, 35, 30), (cx - 7, mouth_y - 2, 14, int(4 + mouth_open)))
        pygame.draw.line(surface, WHITE, (cx - 5, mouth_y), (cx + 5, mouth_y), 1)
    elif mood == "satisfied":
        pygame.draw.arc(surface, (130, 60, 50), (cx - 8, mouth_y - 4, 16, 10), math.pi, 2 * math.pi, 2)
    elif mood == "stern":
        pygame.draw.line(surface, (120, 50, 40), (cx - 8, mouth_y + 2), (cx + 8, mouth_y + 2), 2)
    else:
        pygame.draw.line(surface, (130, 60, 50), (cx - 6, mouth_y), (cx + 6, mouth_y), 2)

    # Animated Gavel Strike
    if gavel_strike_anim > 0:
        gavel_angle = math.sin(gavel_strike_anim * 0.3) * 25
        gx = cx + 60
        gy = cy + 10
        # Gavel head
        pygame.draw.rect(surface, (130, 75, 40), (gx - 15, gy - 8, 30, 16), border_radius=4)
        pygame.draw.rect(surface, GOLD, (gx - 15, gy - 8, 30, 16), width=2, border_radius=4)
        # Gavel handle
        pygame.draw.line(surface, (100, 55, 30), (gx, gy), (gx + 30, gy + 25), 4)

        # Impact shockwave ring
        ring_r = (20 - gavel_strike_anim) * 3
        if ring_r > 0:
            pygame.draw.circle(surface, GOLD_LIGHT, (gx, gy + 15), ring_r, 2)


def draw_animated_scales(surface: pygame.Surface, center: Tuple[int, int], tick: int = 0) -> None:
    """Draws balanced / swaying golden Scales of Justice."""
    cx, cy = center
    sway = math.sin(tick * 0.03) * 6

    # Center pillar & apex
    pygame.draw.line(surface, GOLD_LIGHT, (cx, cy - 25), (cx, cy + 30), 4)
    pygame.draw.circle(surface, GOLD_LIGHT, (cx, cy - 25), 5)
    pygame.draw.rect(surface, GOLD_DARK, (cx - 20, cy + 28, 40, 8), border_radius=3)

    # Beam with dynamic tilt
    p1 = (cx - 45, cy - 10 + sway)
    p2 = (cx + 45, cy - 10 - sway)
    pygame.draw.line(surface, GOLD_LIGHT, p1, p2, 3)

    # Left pan
    pygame.draw.line(surface, GOLD, p1, (p1[0] - 12, p1[1] + 25), 1)
    pygame.draw.line(surface, GOLD, p1, (p1[0] + 12, p1[1] + 25), 1)
    pygame.draw.polygon(surface, GOLD, [
        (p1[0] - 16, p1[1] + 25),
        (p1[0] + 16, p1[1] + 25),
        (p1[0], p1[1] + 32)
    ])

    # Right pan
    pygame.draw.line(surface, GOLD, p2, (p2[0] - 12, p2[1] + 25), 1)
    pygame.draw.line(surface, GOLD, p2, (p2[0] + 12, p2[1] + 25), 1)
    pygame.draw.polygon(surface, GOLD, [
        (p2[0] - 16, p2[1] + 25),
        (p2[0] + 16, p2[1] + 25),
        (p2[0], p2[1] + 32)
    ])


def draw_suspect_portrait(surface: pygame.Surface, rect: pygame.Rect, avatar_type: str = "heir") -> None:
    """Draws custom vintage illustrated character avatars."""
    # Frame
    pygame.draw.rect(surface, (60, 35, 20), rect, border_radius=10)
    pygame.draw.rect(surface, GOLD, rect, 2, border_radius=10)

    cx, cy = rect.centerx, rect.centery

    # Clothes base
    if avatar_type in ["heir", "executive", "counsel_1"]:
        pygame.draw.ellipse(surface, (35, 55, 75), (cx - 45, cy + 12, 90, 60))
        pygame.draw.polygon(surface, WHITE, [(cx - 12, cy + 15), (cx + 12, cy + 15), (cx, cy + 32)])
        pygame.draw.polygon(surface, ACCENT_RED, [(cx - 4, cy + 18), (cx + 4, cy + 18), (cx, cy + 30)])
    elif avatar_type in ["partner", "socialite", "counsel_2"]:
        pygame.draw.ellipse(surface, (25, 70, 50), (cx - 45, cy + 12, 90, 60))
        pygame.draw.arc(surface, GOLD, (cx - 18, cy + 16, 36, 18), 0, math.pi, 2)
    elif avatar_type in ["butler", "counsel_3"]:
        pygame.draw.ellipse(surface, (30, 30, 35), (cx - 45, cy + 12, 90, 60))
        pygame.draw.polygon(surface, WHITE, [(cx - 14, cy + 15), (cx + 14, cy + 15), (cx, cy + 35)])
        pygame.draw.polygon(surface, BLACK, [(cx - 8, cy + 18), (cx + 8, cy + 18), (cx, cy + 22)])
    else:
        pygame.draw.ellipse(surface, (80, 80, 85), (cx - 45, cy + 12, 90, 60))
        pygame.draw.polygon(surface, WHITE, [(cx - 12, cy + 15), (cx + 12, cy + 15), (cx, cy + 32)])

    # Head & Face
    face_color = (235, 195, 165)
    pygame.draw.ellipse(surface, face_color, (cx - 20, cy - 25, 40, 45))

    # Hair style
    if avatar_type in ["heir", "executive", "counsel_1"]:
        pygame.draw.arc(surface, (50, 30, 15), (cx - 22, cy - 35, 44, 25), 0, math.pi, 8)
        pygame.draw.circle(surface, (50, 30, 15), (cx - 18, cy - 20), 8)
        pygame.draw.line(surface, (50, 30, 15), (cx - 8, cy + 8), (cx + 8, cy + 8), 2)
    elif avatar_type in ["partner", "socialite", "counsel_2"]:
        pygame.draw.circle(surface, (165, 95, 45), (cx, cy - 30), 18)
        pygame.draw.ellipse(surface, (165, 95, 45), (cx - 24, cy - 28, 48, 26))
    elif avatar_type in ["butler", "counsel_3"]:
        pygame.draw.ellipse(surface, (150, 150, 155), (cx - 24, cy - 28, 48, 18))
        pygame.draw.circle(surface, (150, 150, 155), (cx - 20, cy - 15), 6)
        pygame.draw.circle(surface, (150, 150, 155), (cx + 20, cy - 15), 6)
    else:
        pygame.draw.ellipse(surface, (70, 45, 25), (cx - 22, cy - 32, 44, 20))
        pygame.draw.circle(surface, GOLD, (cx - 8, cy - 8), 5, 1)
        pygame.draw.circle(surface, GOLD, (cx + 8, cy - 8), 5, 1)
        pygame.draw.line(surface, GOLD, (cx - 3, cy - 8), (cx + 3, cy - 8), 1)

    # Eyes & details
    pygame.draw.circle(surface, DARK_BROWN, (cx - 9, cy - 8), 3)
    pygame.draw.circle(surface, DARK_BROWN, (cx + 9, cy - 8), 3)
    pygame.draw.line(surface, (190, 140, 110), (cx, cy - 6), (cx, cy + 3), 2)
    pygame.draw.line(surface, (150, 80, 70), (cx - 6, cy + 12), (cx + 6, cy + 12), 2)


def draw_evidence_icon(surface: pygame.Surface, *args, **kwargs) -> None:
    """Draws clear forensic iconography for evidence tokens and crime scene hotspots."""
    if len(args) == 2:
        # Signature: (surface, rect, icon_type) or (surface, icon_type, rect)
        if isinstance(args[0], pygame.Rect):
            rect, icon_type = args[0], args[1]
        elif isinstance(args[1], pygame.Rect):
            icon_type, rect = args[0], args[1]
        else:
            rect = pygame.Rect(args[0])
            icon_type = str(args[1])
    elif len(args) == 5:
        # Signature: (surface, icon_type, x, y, w, h)
        icon_type = str(args[0])
        rect = pygame.Rect(args[1], args[2], args[3], args[4])
    else:
        rect = kwargs.get("rect", pygame.Rect(0, 0, 40, 40))
        icon_type = kwargs.get("icon_type", "generic")

    cx, cy = rect.centerx, rect.centery

    if icon_type == "body":
        pygame.draw.circle(surface, WHITE, (cx, cy - 12), 8, 2)
        pygame.draw.line(surface, WHITE, (cx, cy - 4), (cx, cy + 14), 2)
        pygame.draw.line(surface, WHITE, (cx - 14, cy), (cx + 14, cy), 2)
        pygame.draw.line(surface, WHITE, (cx, cy + 14), (cx - 10, cy + 24), 2)
        pygame.draw.line(surface, WHITE, (cx, cy + 14), (cx + 10, cy + 24), 2)

    elif icon_type == "knife":
        pygame.draw.polygon(surface, (210, 215, 225), [(cx - 15, cy - 12), (cx + 8, cy + 5), (cx + 14, cy + 2)])
        pygame.draw.line(surface, (120, 60, 30), (cx - 14, cy - 11), (cx - 22, cy - 18), 5)
        pygame.draw.circle(surface, ACCENT_RED, (cx + 11, cy + 4), 3)

    elif icon_type == "fingerprint":
        for r in [4, 8, 12, 16]:
            pygame.draw.ellipse(surface, GOLD, (cx - r, cy - int(r*1.2), r*2, int(r*2.4)), 1)

    elif icon_type == "glass":
        pygame.draw.polygon(surface, (180, 220, 240), [(cx - 12, cy + 10), (cx - 2, cy - 12), (cx + 4, cy + 4)], 1)
        pygame.draw.polygon(surface, (200, 235, 255), [(cx + 2, cy - 10), (cx + 14, cy - 6), (cx + 6, cy + 12)], 1)

    elif icon_type == "phone":
        pygame.draw.rect(surface, (30, 30, 35), (cx - 12, cy - 18, 24, 36), border_radius=4)
        pygame.draw.rect(surface, (70, 130, 180), (cx - 9, cy - 14, 18, 24))
        pygame.draw.circle(surface, GOLD, (cx, cy + 13), 2)

    elif icon_type == "cctv":
        pygame.draw.polygon(surface, (60, 65, 75), [(cx - 14, cy - 8), (cx + 10, cy - 12), (cx + 10, cy + 8), (cx - 14, cy + 4)])
        pygame.draw.circle(surface, ACCENT_RED, (cx + 8, cy - 2), 3)
        pygame.draw.line(surface, (40, 40, 45), (cx - 14, cy), (cx - 20, cy + 10), 3)

    elif icon_type == "safe":
        pygame.draw.rect(surface, (50, 55, 60), (cx - 16, cy - 16, 32, 32), border_radius=4)
        pygame.draw.circle(surface, GOLD, (cx, cy), 7, 2)
        pygame.draw.line(surface, GOLD, (cx, cy - 7), (cx, cy + 7), 2)

    elif icon_type == "blood":
        pygame.draw.circle(surface, ACCENT_RED, (cx, cy + 2), 8)
        pygame.draw.circle(surface, ACCENT_RED, (cx - 6, cy - 4), 4)
        pygame.draw.circle(surface, ACCENT_RED, (cx + 8, cy + 6), 3)

    else:
        pygame.draw.circle(surface, GOLD, (cx - 4, cy - 4), 10, 2)
        pygame.draw.line(surface, (130, 80, 40), (cx + 4, cy + 4), (cx + 14, cy + 14), 4)
