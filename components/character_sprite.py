"""Character Sprite and Dynamic Expression Renderer for LOGIC COURTROOM.
Animates avatars with breathing idle cycles, blinking eyes, speaking mouth motion,
nervous sweat, anger marks, and thinking expressions.
"""
#pyright: ignore
import pygame
import math
import random
from typing import Tuple, Optional
from config import (
    WOOD_BROWN, DARK_BROWN, GOLD, GOLD_LIGHT, WHITE, BLACK,
    ACCENT_RED, ACCENT_BLUE, ACCENT_GREEN, MUTED_TEXT, get_font
)

class CharacterSprite:
    """Renders animated 2D character avatars with rich emotional expressions."""

    def __init__(self, character_type: str = "heir", name: str = "Unknown"):
        self.character_type = character_type
        self.name = name
        self.expression = "neutral"  # 'neutral', 'angry', 'nervous', 'surprised', 'thinking', 'satisfied', 'speaking'
        self.is_speaking = False
        self.anim_time = random.uniform(0, 10)
        self.blink_timer = random.uniform(2.0, 4.5)
        self.is_blinking = False

    def set_expression(self, expression: str, is_speaking: bool = False):
        self.expression = expression.lower()
        self.is_speaking = is_speaking

    def update(self, dt: float = 0.016):
        self.anim_time += dt
        self.blink_timer -= dt

        if self.blink_timer <= 0:
            self.is_blinking = True
            if self.blink_timer <= -0.15:
                self.is_blinking = False
                self.blink_timer = random.uniform(2.5, 5.0)

    def draw(self, surface: pygame.Surface, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], pygame.Rect):
            rect = args[0]
        elif len(args) == 4:
            rect = pygame.Rect(args[0], args[1], args[2], args[3])
        else:
            rect = kwargs.get("rect", pygame.Rect(0, 0, 90, 95))

        if "expression" in kwargs:
            self.expression = str(kwargs["expression"]).lower()
        if "role" in kwargs:
            self.character_type = str(kwargs["role"]).lower()

        self.update()

        # Outer Shadow & Border
        pygame.draw.rect(surface, (45, 25, 15), rect, border_radius=10)
        pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=10)

        cx, cy = rect.centerx, rect.centery

        # Trembling if breakdown
        if self.expression in ["breakdown", "nervous"]:
            tremble_mag = 2.5 if self.expression == "breakdown" else 0.8
            cx += random.uniform(-tremble_mag, tremble_mag)
            cy += random.uniform(-tremble_mag, tremble_mag)

        # Breathing idle animation
        breath = math.sin(self.anim_time * 2.5) * 1.5
        cy += breath

        # 1. Clothing & Shoulders
        if self.character_type in ["judge"]:
            # Judicial Robe
            pygame.draw.ellipse(surface, (20, 18, 18), (cx - 45, cy + 12, 90, 60))
            pygame.draw.polygon(surface, WHITE, [(cx - 15, cy + 15), (cx + 15, cy + 15), (cx, cy + 35)])
        elif self.character_type in ["lawyer", "counsel", "counsel_1", "heir"]:
            # Tailored Navy Coat & Tie
            pygame.draw.ellipse(surface, (30, 50, 75), (cx - 45, cy + 12, 90, 60))
            pygame.draw.polygon(surface, WHITE, [(cx - 12, cy + 15), (cx + 12, cy + 15), (cx, cy + 32)])
            pygame.draw.polygon(surface, ACCENT_RED, [(cx - 4, cy + 18), (cx + 4, cy + 18), (cx, cy + 30)])

            # Pointing arm if objection / pointing pose
            if self.expression in ["pointing", "objection"]:
                pygame.draw.polygon(surface, (30, 50, 75), [(cx + 25, cy + 15), (cx + 48, cy - 2), (cx + 45, cy + 12)])
                pygame.draw.circle(surface, (235, 195, 165), (cx + 49, cy - 2), 5)
                pygame.draw.line(surface, (235, 195, 165), (cx + 49, cy - 2), (cx + 62, cy - 10), 3)
        elif self.character_type in ["partner", "socialite", "counsel_2"]:
            # Emerald Silk Dress
            pygame.draw.ellipse(surface, (25, 70, 50), (cx - 45, cy + 12, 90, 60))
            pygame.draw.arc(surface, GOLD, (cx - 18, cy + 16, 36, 18), 0, math.pi, 2)
        elif self.character_type in ["butler", "staff", "counsel_3"]:
            # Formal Waistcoat & Bowtie
            pygame.draw.ellipse(surface, (30, 30, 35), (cx - 45, cy + 12, 90, 60))
            pygame.draw.polygon(surface, WHITE, [(cx - 14, cy + 15), (cx + 14, cy + 15), (cx, cy + 35)])
            pygame.draw.polygon(surface, BLACK, [(cx - 8, cy + 18), (cx + 8, cy + 18), (cx, cy + 22)])
        else:
            # Doctor / Executive Tweed Vest
            pygame.draw.ellipse(surface, (70, 65, 60), (cx - 45, cy + 12, 90, 60))
            pygame.draw.polygon(surface, WHITE, [(cx - 12, cy + 15), (cx + 12, cy + 15), (cx, cy + 32)])

        # 2. Head & Neck
        face_color = (235, 195, 165)
        if self.expression in ["angry", "breakdown"]:
            face_color = (245, 175, 155)  # Flushed red
        elif self.expression == "nervous":
            face_color = (225, 200, 180)  # Pale

        pygame.draw.ellipse(surface, face_color, (cx - 20, cy - 25, 40, 45))

        # 3. Hair Styles
        if self.character_type == "judge":
            wig_color = (232, 232, 238)
            pygame.draw.ellipse(surface, wig_color, (cx - 28, cy - 44, 56, 38))
            pygame.draw.circle(surface, wig_color, (cx - 26, cy - 16), 14)
            pygame.draw.circle(surface, wig_color, (cx + 26, cy - 16), 14)
        elif self.character_type in ["partner", "socialite", "counsel_2"]:
            pygame.draw.circle(surface, (165, 95, 45), (cx, cy - 30), 18)
            pygame.draw.ellipse(surface, (165, 95, 45), (cx - 24, cy - 28, 48, 26))
        elif self.character_type in ["butler", "staff"]:
            pygame.draw.ellipse(surface, (150, 150, 155), (cx - 24, cy - 28, 48, 18))
        else:
            # Slicked gentleman hair
            pygame.draw.arc(surface, (50, 30, 15), (cx - 22, cy - 35, 44, 25), 0, math.pi, 8)
            pygame.draw.circle(surface, (50, 30, 15), (cx - 18, cy - 20), 8)

        # 4. Eyebrows based on emotion
        eye_y = cy - 8
        if self.expression in ["angry", "breakdown"]:
            pygame.draw.line(surface, (70, 40, 30), (cx - 15, eye_y - 8), (cx - 4, eye_y - 4), 2)
            pygame.draw.line(surface, (70, 40, 30), (cx + 15, eye_y - 8), (cx + 4, eye_y - 4), 2)
        elif self.expression == "surprised":
            pygame.draw.arc(surface, (70, 40, 30), (cx - 16, eye_y - 14, 12, 8), 0, math.pi, 2)
            pygame.draw.arc(surface, (70, 40, 30), (cx + 4, eye_y - 14, 12, 8), 0, math.pi, 2)
        elif self.expression == "thinking":
            pygame.draw.line(surface, (70, 40, 30), (cx - 15, eye_y - 8), (cx - 5, eye_y - 8), 2)
            pygame.draw.line(surface, (70, 40, 30), (cx + 5, eye_y - 10), (cx + 15, eye_y - 6), 2)
        else:
            pygame.draw.arc(surface, (70, 40, 30), (cx - 15, eye_y - 10, 10, 6), 0, math.pi, 2)
            pygame.draw.arc(surface, (70, 40, 30), (cx + 5, eye_y - 10, 10, 6), 0, math.pi, 2)

        # 5. Eyes with blinking animation
        if self.is_blinking:
            pygame.draw.line(surface, DARK_BROWN, (cx - 13, eye_y), (cx - 5, eye_y), 2)
            pygame.draw.line(surface, DARK_BROWN, (cx + 5, eye_y), (cx + 13, eye_y), 2)
        elif self.expression in ["surprised", "breakdown"]:
            pygame.draw.circle(surface, WHITE, (cx - 9, eye_y), 6)
            pygame.draw.circle(surface, DARK_BROWN, (cx - 9, eye_y), 3)
            pygame.draw.circle(surface, WHITE, (cx + 9, eye_y), 6)
            pygame.draw.circle(surface, DARK_BROWN, (cx + 9, eye_y), 3)
        elif self.expression == "nervous":
            # Darting nervous pupils
            glance_x = math.sin(self.anim_time * 6.0) * 2
            pygame.draw.circle(surface, DARK_BROWN, (cx - 9 + int(glance_x), eye_y), 3)
            pygame.draw.circle(surface, DARK_BROWN, (cx + 9 + int(glance_x), eye_y), 3)
        else:
            pygame.draw.circle(surface, DARK_BROWN, (cx - 9, eye_y), 3)
            pygame.draw.circle(surface, DARK_BROWN, (cx + 9, eye_y), 3)

        # Spectacles if doctor or judge
        if self.character_type in ["doctor", "judge"]:
            pygame.draw.circle(surface, GOLD, (cx - 9, eye_y), 6, 1)
            pygame.draw.circle(surface, GOLD, (cx + 9, eye_y), 6, 1)
            pygame.draw.line(surface, GOLD, (cx - 3, eye_y), (cx + 3, eye_y), 1)

        # 6. Mouth animation
        mouth_y = cy + 12
        if self.is_speaking:
            mouth_h = int((math.sin(self.anim_time * 15.0) + 1.0) * 3) + 3
            pygame.draw.ellipse(surface, (90, 40, 35), (cx - 6, mouth_y - 2, 12, mouth_h))
            pygame.draw.line(surface, WHITE, (cx - 4, mouth_y), (cx + 4, mouth_y), 1)
        elif self.expression == "breakdown":
            pygame.draw.ellipse(surface, (120, 30, 25), (cx - 8, mouth_y - 2, 16, 10))
            pygame.draw.line(surface, WHITE, (cx - 5, mouth_y), (cx + 5, mouth_y), 1)
        elif self.expression == "angry":
            pygame.draw.line(surface, (120, 45, 40), (cx - 7, mouth_y + 2), (cx + 7, mouth_y + 2), 2)
        elif self.expression == "satisfied":
            pygame.draw.arc(surface, (130, 60, 50), (cx - 7, mouth_y - 4, 14, 8), math.pi, 2 * math.pi, 2)
        elif self.expression == "nervous":
            # Wobbly nervous mouth
            wobble = math.sin(self.anim_time * 10.0) * 1.5
            pygame.draw.line(surface, (130, 60, 50), (cx - 6, mouth_y + int(wobble)), (cx + 6, mouth_y - int(wobble)), 2)
        else:
            pygame.draw.line(surface, (130, 60, 50), (cx - 5, mouth_y), (cx + 5, mouth_y), 2)

        # 7. Emotional FX Overlays
        if self.expression in ["nervous", "breakdown"]:
            # Animated falling blue sweat drops
            drop_y1 = rect.y + 15 + int((self.anim_time * 35.0) % 40)
            drop_y2 = rect.y + 25 + int(((self.anim_time + 0.5) * 35.0) % 40)
            pygame.draw.circle(surface, (120, 200, 255), (rect.right - 14, drop_y1), 3)
            pygame.draw.circle(surface, (120, 200, 255), (rect.left + 14, drop_y2), 3)
        elif self.expression == "angry":
            # Anger pop mark
            pop_x, pop_y = rect.right - 16, rect.y + 14
            pygame.draw.line(surface, ACCENT_RED, (pop_x - 4, pop_y - 4), (pop_x + 4, pop_y + 4), 2)
            pygame.draw.line(surface, ACCENT_RED, (pop_x + 4, pop_y - 4), (pop_x - 4, pop_y + 4), 2)
