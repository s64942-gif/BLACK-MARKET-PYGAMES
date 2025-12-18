import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# --- Screen setup (virtual 1920x1080, scaled to fit actual window) ---
WIDTH, HEIGHT = 1920, 1080  # keep ALL game logic in this coordinate space

info = pygame.display.Info()
WINDOW_W = min(info.current_w, WIDTH)
WINDOW_H = min(int(info.current_h * 0.95), HEIGHT)  # margin so it won't clip under taskbar

window = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)
pygame.display.set_caption("Stickman Shooting Game")

# Draw everything here, then scale it into the real window
screen = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()

# --- Scaling helpers ---
_scale = 1.0
_offset_x = 0
_offset_y = 0
_scaled_size = (WINDOW_W, WINDOW_H)

def _recalc_view():
    global _scale, _offset_x, _offset_y, _scaled_size
    ww, wh = window.get_size()
    _scale = min(ww / WIDTH, wh / HEIGHT)
    _scaled_size = (max(1, int(WIDTH * _scale)), max(1, int(HEIGHT * _scale)))
    _offset_x = (ww - _scaled_size[0]) // 2
    _offset_y = (wh - _scaled_size[1]) // 2

def _handle_resize(event):
    global window
    window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
    _recalc_view()

def to_virtual(pos):
    # Convert real-window mouse coords -> virtual 1920x1080 coords
    x, y = pos
    x = (x - _offset_x) / _scale
    y = (y - _offset_y) / _scale
    return (int(x), int(y))

def present():
    # Scale the virtual screen into the real window and flip
    window.fill((0, 0, 0))
    scaled = pygame.transform.smoothscale(screen, _scaled_size)
    window.blit(scaled, (_offset_x, _offset_y))
    pygame.display.flip()

_recalc_view()

# --- Game Settings ---
SCORE_LIMIT = 10  # First player to reach this score wins!
CURRENT_GAME_MODE = None  # Global: To store the selected mode

# --- NEW Custom Battle Globals ---
P1_SELECTED_WEAPON = "PISTOL"
P2_SELECTED_WEAPON = "PISTOL"
SELECTED_MAP_INDEX = 0

# --- NEW: Character selections for Custom Battle ---
P1_SELECTED_CHARACTER = "DEFAULT"
P2_SELECTED_CHARACTER = "DEFAULT"

# --- Mode Definitions ---
GAME_MODES = {
    "CLASSIC_DEATHMATCH": {
        "name": "Classic Deathmatch",
        "description": f"First to {SCORE_LIMIT} kills. New map & random weapon per round.",
        "function": 'game'
    },
    "CUSTOM_BATTLE": {
        "name": "Custom Battle",
        "description": "Select the map, starting weapon, and character for each player.",
        "function": 'custom_setup'
    },
    "SINGLE_PLAYER_AI": {
        "name": "Single Player (vs AI)",
        "description": f"Battle against a tactical AI. First to {SCORE_LIMIT} kills wins!",
        "function": 'game'
    },
    "COOP_SURVIVAL": {
        "name": "Co-op Survival",
        "description": "Team up to survive waves of enemies and defeat the boss!",
        "function": 'survival_game'
    }
}

# Physics Constants
GRAVITY = 1
JUMP_STRENGTH = -15

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)  # Jump Pad Color
YELLOW = (255, 255, 0)  # Shield Color
BRIGHT_BLUE = (100, 100, 255)
BRIGHT_RED = (255, 100, 100)

# Clock
clock = pygame.time.Clock()

# --- Font Setup (scaled) ---
pygame.font.init()
FONT_BIG = pygame.font.SysFont(None, 120)
FONT_MEDIUM = pygame.font.SysFont(None, 60)
FONT_SMALL = pygame.font.SysFont(None, 36)

# --- Shield Constants ---
SHIELD_DURATION_MS = 1500
SHIELD_COOLDOWN_MS = 5000

# --- WEAPON CONFIGURATION ---
WEAPON_DATA = {
    "PISTOL": {
        "damage": 20, "speed": 8, "size": (10, 10),
        "cooldown": 500, "bullets": 1, "spread": 0
    },
    "SHOTGUN": {
        "damage": 15, "speed": 6, "size": (8, 8),
        "cooldown": 1200, "bullets": 5, "spread": 10
    },
    "MACHINE_GUN": {
        "damage": 10, "speed": 10, "size": (6, 6),
        "cooldown": 100, "bullets": 1, "spread": 0
    },
    "ROCKET_LAUNCHER": {
        "damage": 50, "speed": 12, "size": (14, 14),
        "cooldown": 2000, "bullets": 1, "spread": 0
    }
}
WEAPON_ORDER = ["PISTOL", "SHOTGUN", "MACHINE_GUN", "ROCKET_LAUNCHER"]

# --- Character Configuration ---
CHARACTERS = {
    "DEFAULT": {
        "name": "Default",
        "color": (0, 0, 0),
        "health": 100,
        "speed": 5,
        "special": None
    },
    "TANK": {
        "name": "Tank",
        "color": (100, 50, 50),
        "health": 150,
        "speed": 3,
        "special": "shield_boost"
    },
    "NINJA": {
        "name": "Ninja",
        "color": (50, 50, 100),
        "health": 80,
        "speed": 7,
        "special": "double_jump"
    },
    "SNIPER": {
        "name": "Sniper",
        "color": (0, 100, 0),
        "health": 90,
        "speed": 5,
        "special": "extra_range"
    }
}

# --- Map Data (scaled for 1920x1080) ---
MAP_OBSTACLES = [
    # Map 0: Centralized Platforms
    [pygame.Rect(600, 300, 300, 50), pygame.Rect(900, 600, 400, 50), pygame.Rect(300, 900, 250, 50)],
    # Map 1: Tiered Levels
    [pygame.Rect(900, 360, 300, 50), pygame.Rect(450, 630, 200, 50), pygame.Rect(1500, 810, 300, 50)],
    # Map 2: High/Low Corners
    [pygame.Rect(750, 450, 450, 50), pygame.Rect(300, 180, 250, 50), pygame.Rect(1800, 720, 250, 50)],
    # Map 3: Walls and Center
    [pygame.Rect(900, 720, 300, 50), pygame.Rect(150, 450, 100, 270), pygame.Rect(1800, 450, 100, 270)],
    # Map 4: The Bridge (High sides, low center)
    [pygame.Rect(150, 720, 200, 50), pygame.Rect(1750, 720, 200, 50), pygame.Rect(600, 900, 800, 50)],
    # Map 5: The Pit (Center platform high, rest is open)
    [pygame.Rect(900, 270, 300, 50), pygame.Rect(300, 810, 200, 50), pygame.Rect(1600, 810, 200, 50)],
    # Map 6: Vertical Chaos (Staggered small platforms)
    [pygame.Rect(300, 810, 120, 30), pygame.Rect(750, 630, 120, 30), pygame.Rect(1200, 450, 120, 30), pygame.Rect(1650, 270, 120, 30)],
    # Map 7: Symmetrical Arena (Mirrored opposing platforms)
    [pygame.Rect(150, 630, 250, 50), pygame.Rect(1650, 630, 250, 50), pygame.Rect(150, 900, 100, 50), pygame.Rect(1750, 900, 100, 50)]
]

# Background Colors corresponding to the MAP_OBSTACLES index
MAP_BACKGROUNDS = [
    {'SKY': (135, 206, 235), 'HORIZON': (173, 216, 230), 'GROUND': (50, 50, 50), 'PLATFORM': (150, 150, 150)},  # 0: Blue Sky
    {'SKY': (75, 0, 130), 'HORIZON': (150, 110, 200), 'GROUND': (60, 40, 40), 'PLATFORM': (100, 100, 100)},      # 1: Deep Purple
    {'SKY': (255, 69, 0), 'HORIZON': (255, 140, 0), 'GROUND': (100, 0, 0), 'PLATFORM': (200, 100, 0)},           # 2: Sunset/Orange
    {'SKY': (0, 0, 20), 'HORIZON': (25, 25, 75), 'GROUND': (80, 80, 80), 'PLATFORM': (120, 120, 120)},           # 3: Night
    {'SKY': (170, 190, 200), 'HORIZON': (230, 230, 230), 'GROUND': (50, 80, 100), 'PLATFORM': (150, 110, 80)},   # 4: Foggy
    {'SKY': (150, 50, 50), 'HORIZON': (255, 100, 0), 'GROUND': (180, 180, 180), 'PLATFORM': (200, 200, 200)},    # 5: Martian
    {'SKY': (0, 30, 60), 'HORIZON': (0, 150, 150), 'GROUND': (0, 0, 0), 'PLATFORM': (0, 255, 255)},              # 6: Aqua
    {'SKY': (10, 10, 10), 'HORIZON': (50, 0, 100), 'GROUND': (80, 0, 80), 'PLATFORM': (255, 0, 255)}             # 7: Neon Pink/Dark
]

current_map_colors = MAP_BACKGROUNDS[0]
current_map_index = 0

# --- Utility: draw text/static ---
def draw_text(text, font, color, surface, x, y, center=True):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
    return textrect

def draw_static(surface, noise_amount=20000):
    for _ in range(noise_amount):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        intensity = random.randint(100, 255)
        color = (intensity, intensity, intensity)
        surface.set_at((x, y), color)

# Background band sizes adapted to resolution
HORIZON_HEIGHT = int(HEIGHT * 0.18)
GROUND_HEIGHT = int(HEIGHT * 0.08)

# --- Jump Pad Class ---
class JumpPad(pygame.sprite.Sprite):
    def __init__(self, x, y, width=80, height=16, launch_strength=-28):
        super().__init__()

        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, CYAN, (0, 4, width, height - 4))
        pygame.draw.rect(self.image, BLACK, (0, 4, width, height - 4), 1)
        pygame.draw.polygon(self.image, (255, 255, 0), [
            (width//2 - 10, 4),
            (width//2 + 10, 4),
            (width//2, 0)
        ])
        self.rect = self.image.get_rect(topleft=(x, y))
        self.launch_strength = launch_strength

# --- Helper: collect all valid targets for rockets ---
def get_all_targets():
    targets = []
    if 'player1' in globals() and player1: targets.append(player1)
    if 'player2' in globals() and player2: targets.append(player2)
    if 'enemies_group' in globals():
        targets.extend(list(enemies_group))
    return targets

# --- Bullet & Rocket Classes ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, color, direction, owner, damage, size, speed):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.direction = direction
        self.owner = owner
        self.damage = damage

    def update(self):
        if self.direction == "left":
            self.rect.x -= self.speed
        elif self.direction == "right":
            self.rect.x += self.speed
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

class Rocket(Bullet):
    def __init__(self, x, y, color, direction, owner, damage, size, speed):
        super().__init__(x, y, color, direction, owner, damage, size, speed)
        self.image.fill((255, 120, 0))
        self.exploding = False
        self.explosion_start = 0
        self.explosion_radius = 0
        self.explosion_center = self.rect.center

    def explode(self):
        if self.exploding:
            return
        self.exploding = True
        self.explosion_start = pygame.time.get_ticks()
        self.explosion_center = self.rect.center

        aoe_rect = pygame.Rect(0, 0, 160, 160)
        aoe_rect.center = self.explosion_center

        for target in get_all_targets():
            if target != self.owner and aoe_rect.colliderect(target.rect):
                target.health -= self.damage

    def update(self):
        if not self.exploding:
            if self.direction == "left":
                self.rect.x -= self.speed
            elif self.direction == "right":
                self.rect.x += self.speed

            if not screen.get_rect().colliderect(self.rect):
                self.kill()
                return

            if 'obstacle_group' in globals() and pygame.sprite.spritecollide(self, obstacle_group, False):
                self.explode()

            for target in get_all_targets():
                if target != self.owner and self.rect.colliderect(target.rect):
                    self.explode()
                    break
        else:
            elapsed = pygame.time.get_ticks() - self.explosion_start
            self.explosion_radius = min(60, elapsed // 2)
            if elapsed > 500:
                self.kill()

    def draw_explosion(self, surface):
        if self.exploding:
            pygame.draw.circle(surface, (255, 180, 0), self.explosion_center, max(1, self.explosion_radius // 2), 2)
            pygame.draw.circle(surface, (255, 80, 0), self.explosion_center, self.explosion_radius, 3)

# --- Helper: Line of Sight ---
def has_line_of_sight(rect_a, rect_b, obstacles):
    ax, ay = rect_a.center
    bx, by = rect_b.center
    if abs(ay - by) > 80:
        return False
    left = min(ax, bx)
    right = max(ax, bx)
    mid_y = (ay + by) // 2
    ray = pygame.Rect(left, mid_y - 5, right - left, 10)
    for o in obstacles:
        if ray.colliderect(o.rect):
            return False
    return True

# --- Player class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, controls, other_player):
        super().__init__()
        self.image = pygame.Surface((40, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.controls = controls
        self.score = 0
        self.color = color

        self.is_jumping = True
        self.vertical_velocity = 0

        self.direction = "right"
        self.other_player = other_player

        self.MAX_HEALTH = 100
        self.health = self.MAX_HEALTH

        self.initial_pos = (x, y)

        self.is_shielded = False
        self.shield_active_time = 0
        self.shield_cooldown_time = 0

        self.walk_frame = 0
        self.is_moving = False

        self.current_weapon = WEAPON_ORDER[0]
        self.last_shot_time = 0

        self.special = None

    def assign_random_weapon(self):
        self.current_weapon = random.choice(WEAPON_ORDER)
        self.last_shot_time = 0

    def jump(self):
        temp_y = self.rect.y
        self.rect.y += 2
        hit_list = pygame.sprite.spritecollide(self, obstacle_group, False)
        self.rect.y = temp_y

        if self.rect.bottom >= HEIGHT or len(hit_list) > 0:
            self.vertical_velocity = JUMP_STRENGTH
            self.is_jumping = True

    def update(self, keys_pressed):
        current_time = pygame.time.get_ticks()

        if self.is_shielded and current_time > self.shield_active_time:
            self.is_shielded = False

        if keys_pressed:
            if self.controls.get('up') and keys_pressed[self.controls['up']]:
                if self.special == "double_jump" and not self.is_jumping:
                    self.jump()
                self.jump()

            if self.controls.get('shield') and keys_pressed[self.controls['shield']]:
                self.activate_shield()

        x_change = 0
        self.is_moving = False

        if keys_pressed and self.controls.get('left') and keys_pressed[self.controls['left']]:
            x_change = -self.speed
            self.direction = "left"
            self.is_moving = True

        if keys_pressed and self.controls.get('right') and keys_pressed[self.controls['right']]:
            x_change = self.speed
            self.direction = "right"
            self.is_moving = True

        if self.is_moving and not self.is_jumping:
            if pygame.time.get_ticks() % 5 == 0:
                self.walk_frame = (self.walk_frame + 1) % 3
        else:
            self.walk_frame = 0

        self.rect.x += x_change

        hit_list_h = pygame.sprite.spritecollide(self, obstacle_group, False)
        for platform in hit_list_h:
            if x_change > 0:
                self.rect.right = platform.rect.left
            elif x_change < 0:
                self.rect.left = platform.rect.right

        old_y = self.rect.y

        self.vertical_velocity += GRAVITY
        if self.vertical_velocity > 15:
            self.vertical_velocity = 15

        self.rect.y += self.vertical_velocity

        jumppad_hits = pygame.sprite.spritecollide(self, jumppad_group, False)
        jumped_from_pad = False
        for pad in jumppad_hits:
            if old_y + self.rect.height <= pad.rect.top and self.vertical_velocity >= 0:
                self.rect.bottom = pad.rect.top
                self.vertical_velocity = pad.launch_strength
                self.is_jumping = True
                jumped_from_pad = True
                break

        if not jumped_from_pad:
            hit_list_v = pygame.sprite.spritecollide(self, obstacle_group, False)
            for platform in hit_list_v:
                if self.vertical_velocity > 0:
                    if old_y + self.rect.height <= platform.rect.top:
                        self.rect.bottom = platform.rect.top
                        self.is_jumping = False
                        self.vertical_velocity = 0
                elif self.vertical_velocity < 0:
                    if old_y >= platform.rect.bottom:
                        self.rect.top = platform.rect.bottom
                        self.vertical_velocity = 0

        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.is_jumping = False
            self.vertical_velocity = 0

        self.rect.clamp_ip(screen.get_rect())

    def activate_shield(self):
        current_time = pygame.time.get_ticks()
        if not self.is_shielded and current_time > self.shield_cooldown_time:
            self.is_shielded = True
            duration = SHIELD_DURATION_MS + (1000 if self.special == "shield_boost" else 0)
            self.shield_active_time = current_time + duration
            self.shield_cooldown_time = current_time + SHIELD_COOLDOWN_MS

    def draw_health_bar(self, surface):
        BAR_WIDTH = 50
        BAR_HEIGHT = 9
        x = self.rect.x
        y = self.rect.y - 14
        fill = (self.health / self.MAX_HEALTH) * BAR_WIDTH
        outline_rect = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        pygame.draw.rect(surface, RED, outline_rect)
        pygame.draw.rect(surface, GREEN, fill_rect)
        pygame.draw.rect(surface, BLACK, outline_rect, 1)

    def draw_weapon_info(self, surface):
        weapon_text = FONT_SMALL.render(self.current_weapon, True, BLACK)
        x = self.rect.x + self.rect.width // 2 - weapon_text.get_width() // 2
        y = self.rect.y - 35
        surface.blit(weapon_text, (x, y))

    def draw(self, surface):
        cx, cy = self.rect.center

        if self.is_shielded:
            alpha = 255
            elapsed = pygame.time.get_ticks() - (self.shield_active_time - SHIELD_DURATION_MS)
            if SHIELD_DURATION_MS - elapsed < 500:
                alpha = 100 + (elapsed % 100 < 50) * 155

            shield_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            shield_color = YELLOW + (int(alpha),)
            pygame.draw.circle(shield_surface, shield_color, (60, 60), 60, 3)
            surface.blit(shield_surface, (cx - 60, cy - 60))

        pygame.draw.circle(surface, self.color, (cx, cy - 30), 10, 0)  # Head
        pygame.draw.line(surface, self.color, (cx, cy - 20), (cx, cy + 20), 2)  # Body
        pygame.draw.line(surface, self.color, (cx, cy - 10), (cx - 20, cy + 10), 2)  # Left Arm
        pygame.draw.line(surface, self.color, (cx, cy - 10), (cx + 20, cy + 10), 2)  # Right Arm

        leg_start_y = cy + 20
        leg_end_y = cy + 40

        if self.is_jumping:
            pygame.draw.line(surface, self.color, (cx, leg_start_y), (cx - 10, cy + 30), 2)
            pygame.draw.line(surface, self.color, (cx, leg_start_y), (cx + 10, cy + 30), 2)
        elif self.walk_frame == 0:
            pygame.draw.line(surface, self.color, (cx - 2, leg_start_y), (cx - 2, leg_end_y), 2)
            pygame.draw.line(surface, self.color, (cx + 2, leg_start_y), (cx + 2, leg_end_y), 2)
        elif self.walk_frame == 1:
            pygame.draw.line(surface, self.color, (cx, leg_start_y), (cx + 15, leg_end_y), 2)
            pygame.draw.line(surface, self.color, (cx, leg_start_y), (cx - 5, cy + 30), 2)
        elif self.walk_frame == 2:
            pygame.draw.line(surface, self.color, (cx, leg_start_y), (cx - 15, leg_end_y), 2)
            pygame.draw.line(surface, self.color, (cx, leg_start_y), (cx + 5, cy + 30), 2)

        gun_color = BLACK
        gun_width = 5
        barrel_length = 20
        handle_offset = 10

        gun_start_x = cx
        gun_start_y = cy - 20

        if self.direction == "left":
            gun_end_x = cx - barrel_length
            pygame.draw.line(surface, gun_color, (gun_start_x, gun_start_y), (gun_end_x, gun_start_y), gun_width)
            pygame.draw.rect(surface, (50, 50, 50), (gun_end_x - 3, gun_start_y - gun_width//2, 3, gun_width))
            pygame.draw.line(surface, gun_color, (gun_start_x - handle_offset, gun_start_y),
                             (gun_start_x - handle_offset, gun_start_y + 5), 2)
        elif self.direction == "right":
            gun_end_x = cx + barrel_length
            pygame.draw.line(surface, gun_color, (gun_start_x, gun_start_y), (gun_end_x, gun_start_y), gun_width)
            pygame.draw.rect(surface, (50, 50, 50), (gun_end_x, gun_start_y - gun_width//2, 3, gun_width))
            pygame.draw.line(surface, gun_color, (gun_start_x + handle_offset, gun_start_y),
                             (gun_start_x + handle_offset, gun_start_y + 5), 2)

        if self.special == "shield_boost":  # Tank
            pygame.draw.rect(surface, (80, 40, 40), (cx - 12, cy - 42, 24, 8))
        elif self.special == "double_jump":  # Ninja
            pygame.draw.rect(surface, (200, 0, 0), (cx - 12, cy - 36, 24, 4))
            pygame.draw.line(surface, (200, 0, 0), (cx + 12, cy - 34), (cx + 22, cy - 44), 3)
        elif self.special == "extra_range":  # Sniper
            if self.direction == "right":
                pygame.draw.circle(surface, (0, 100, 0), (cx + 25, cy - 20), 4)
            else:
                pygame.draw.circle(surface, (0, 100, 0), (cx - 25, cy - 20), 4)

        self.draw_health_bar(surface)
        self.draw_weapon_info(surface)

    def shoot(self, bullets_group):
        current_time = pygame.time.get_ticks()
        weapon = WEAPON_DATA[self.current_weapon]

        if current_time - self.last_shot_time < weapon['cooldown']:
            return

        self.last_shot_time = current_time

        start_x = self.rect.centerx
        start_y = self.rect.centery - 20

        if self.direction == "left":
            start_x -= 23
        elif self.direction == "right":
            start_x += 23

        speed_boost = 2 if self.special == "extra_range" else 0

        for i in range(weapon['bullets']):
            spread_offset = random.uniform(-weapon['spread'], weapon['spread']) if weapon['spread'] > 0 else 0
            proj_speed = weapon['speed'] + speed_boost

            if self.current_weapon == "ROCKET_LAUNCHER":
                bullet = Rocket(
                    start_x,
                    start_y + spread_offset,
                    self.color,
                    self.direction,
                    self,
                    weapon['damage'],
                    weapon['size'],
                    proj_speed
                )
            else:
                bullet = Bullet(
                    start_x,
                    start_y + spread_offset,
                    self.color,
                    self.direction,
                    self,
                    weapon['damage'],
                    weapon['size'],
                    proj_speed
                )
            bullets_group.add(bullet)

    def death_animation(self, surface):
        cx, cy = self.rect.center
        if self.special == "shield_boost":
            pygame.draw.rect(surface, (80, 40, 40), (cx - 12, cy - 42 + (pygame.time.get_ticks() % 20), 24, 8))
        elif self.special == "double_jump":
            for _ in range(6):
                ox = random.randint(-20, 20)
                oy = random.randint(-20, 20)
                pygame.draw.circle(surface, (120, 120, 120), (cx + ox, cy + oy), random.randint(5, 12))
        elif self.special == "extra_range":
            pygame.draw.circle(surface, (0, 100, 0), (cx, cy + 30), 6)
        else:
            pygame.draw.line(surface, self.color, (cx, cy - 20), (cx, cy + 40), 3)

# --- Tactical AI Player ---
class AIPlayer(Player):
    def __init__(self, x, y, color, controls, other_player):
        super().__init__(x, y, color, controls, other_player)
        self.strafe_dir = random.choice([-1, 1])
        self.strafe_timer = 0
        self.retarget_timer = 0

    def desired_range(self):
        if self.current_weapon == "SHOTGUN":
            return 80
        if self.current_weapon == "MACHINE_GUN":
            return 180
        if self.current_weapon == "ROCKET_LAUNCHER":
            return 260
        return 150

    def incoming_threat_close(self):
        for b in bullets_group:
            if b.owner == self:
                continue
            dx = b.rect.centerx - self.rect.centerx
            dy = b.rect.centery - self.rect.centery
            if abs(dy) < 60 and abs(dx) < 180:
                if (dx < 0 and b.direction == "right") or (dx > 0 and b.direction == "left"):
                    return True
        return False

    def rocket_nearby(self):
        for b in bullets_group:
            if isinstance(b, Rocket) and not b.exploding:
                if abs(b.rect.centerx - self.rect.centerx) < 140 and abs(b.rect.centery - self.rect.centery) < 120:
                    return True
        return False

    def update(self, keys_pressed=None):
        target = self.other_player
        if not target:
            super().update(None)
            return

        desired = self.desired_range()
        if self.health < 35:
            desired += 120

        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        horizontal_distance = abs(dx)

        self.direction = "right" if dx > 0 else "left"

        if self.incoming_threat_close():
            self.activate_shield()

        if self.rocket_nearby():
            self.rect.x += -self.speed if self.direction == "right" else self.speed

        x_change = 0
        if horizontal_distance > desired + 20:
            x_change = self.speed if dx > 0 else -self.speed
        elif horizontal_distance < desired - 20:
            x_change = -self.speed if dx > 0 else self.speed
        else:
            if self.strafe_timer <= 0:
                self.strafe_dir = random.choice([-1, 1])
                self.strafe_timer = random.randint(20, 60)
            x_change = self.strafe_dir * (self.speed - 2)
            self.strafe_timer -= 1

        jump_request = False
        if dy < -50 and not self.is_jumping and random.random() < 0.05:
            jump_request = True

        for pad in jumppad_group:
            nearby = abs(pad.rect.centerx - self.rect.centerx) < 30 and (self.rect.bottom <= pad.rect.bottom)
            if nearby and random.random() < 0.15:
                jump_request = True

        can_shoot = has_line_of_sight(self.rect, target.rect, obstacle_group)
        if can_shoot and random.random() < (0.14 if self.current_weapon == "MACHINE_GUN" else 0.08):
            self.shoot(bullets_group)

        current_time = pygame.time.get_ticks()
        if self.is_shielded and current_time > self.shield_active_time:
            self.is_shielded = False

        if jump_request:
            self.jump()

        self.is_moving = x_change != 0
        if self.is_moving and not self.is_jumping:
            if pygame.time.get_ticks() % 5 == 0:
                self.walk_frame = (self.walk_frame + 1) % 3
        else:
            self.walk_frame = 0

        self.rect.x += x_change
        hit_list_h = pygame.sprite.spritecollide(self, obstacle_group, False)
        for platform in hit_list_h:
            if x_change > 0:
                self.rect.right = platform.rect.left
            elif x_change < 0:
                self.rect.left = platform.rect.right

        old_y = self.rect.y
        self.vertical_velocity += GRAVITY
        if self.vertical_velocity > 15:
            self.vertical_velocity = 15

        self.rect.y += self.vertical_velocity

        jumppad_hits = pygame.sprite.spritecollide(self, jumppad_group, False)
        jumped_from_pad = False
        for pad in jumppad_hits:
            if old_y + self.rect.height <= pad.rect.top and self.vertical_velocity >= 0:
                self.rect.bottom = pad.rect.top
                self.vertical_velocity = pad.launch_strength
                self.is_jumping = True
                jumped_from_pad = True
                break

        if not jumped_from_pad:
            hit_list_v = pygame.sprite.spritecollide(self, obstacle_group, False)
            for platform in hit_list_v:
                if self.vertical_velocity > 0:
                    if old_y + self.rect.height <= platform.rect.top:
                        self.rect.bottom = platform.rect.top
                        self.is_jumping = False
                        self.vertical_velocity = 0
                elif self.vertical_velocity < 0:
                    if old_y >= platform.rect.bottom:
                        self.rect.top = platform.rect.bottom
                        self.vertical_velocity = 0

        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.is_jumping = False
            self.vertical_velocity = 0

        self.rect.clamp_ip(screen.get_rect())

# --- Enemy & Boss for Survival Mode ---
class Enemy(Player):
    def __init__(self, x, y, color, target_players):
        super().__init__(x, y, color, {}, None)
        self.target_players = target_players
        self.speed = 3
        self.assign_random_weapon()

    def update(self, keys_pressed=None):
        target = min(self.target_players, key=lambda p: abs(p.rect.centerx - self.rect.centerx))
        dx = target.rect.centerx - self.rect.centerx
        self.direction = "right" if dx > 0 else "left"
        self.rect.x += self.speed if dx > 0 else -self.speed

        if random.random() < 0.01:
            self.jump()
        if has_line_of_sight(self.rect, target.rect, obstacle_group) and random.random() < 0.05:
            self.shoot(bullets_group)

        super().update(None)

class Boss(Enemy):
    def __init__(self, x, y, target_players):
        super().__init__(x, y, (150, 0, 150), target_players)
        self.MAX_HEALTH = 500
        self.health = self.MAX_HEALTH
        self.speed = 4
        self.current_weapon = "ROCKET_LAUNCHER"

    def update(self, keys_pressed=None):
        super().update(None)
        if random.random() < 0.02:
            self.shoot(bullets_group)
            self.shoot(bullets_group)

# --- Player Reset (Used for Round Reset) ---
def reset_round_state(player):
    if CURRENT_GAME_MODE == "CUSTOM_BATTLE":
        char_key = P1_SELECTED_CHARACTER if player == player1 else P2_SELECTED_CHARACTER
        char = CHARACTERS[char_key]
        player.MAX_HEALTH = char["health"]
        player.health = char["health"]
        player.speed = char["speed"]
        player.special = char["special"]
        player.color = char["color"]

    player.rect.center = player.initial_pos
    player.is_jumping = True
    player.vertical_velocity = 0
    player.is_shielded = False
    player.shield_cooldown_time = pygame.time.get_ticks()
    player.last_shot_time = 0

    if CURRENT_GAME_MODE == "CLASSIC_DEATHMATCH":
        player.assign_random_weapon()
    elif CURRENT_GAME_MODE == "CUSTOM_BATTLE":
        if player == player1:
            player.current_weapon = P1_SELECTED_WEAPON
        else:
            player.current_weapon = P2_SELECTED_WEAPON
    elif CURRENT_GAME_MODE in ("SINGLE_PLAYER_AI", "COOP_SURVIVAL"):
        player.assign_random_weapon()

# --- Custom Battle Setup Screen ---
def custom_battle_setup_screen():
    global P1_SELECTED_WEAPON, P2_SELECTED_WEAPON, SELECTED_MAP_INDEX, current_map_colors
    global P1_SELECTED_CHARACTER, P2_SELECTED_CHARACTER
    running = True

    weapon_keys = WEAPON_ORDER
    map_max_index = len(MAP_OBSTACLES) - 1

    p1_weapon_index = weapon_keys.index(P1_SELECTED_WEAPON)
    p2_weapon_index = weapon_keys.index(P2_SELECTED_WEAPON)
    map_index = SELECTED_MAP_INDEX

    character_keys = list(CHARACTERS.keys())
    p1_char_index = character_keys.index(P1_SELECTED_CHARACTER)
    p2_char_index = character_keys.index(P2_SELECTED_CHARACTER)

    current_map_colors = MAP_BACKGROUNDS[map_index]

    while running:
        screen.fill(BLACK)
        draw_text("CUSTOM BATTLE SETUP", FONT_BIG, WHITE, screen, WIDTH // 2, 120)
        draw_text(f"First to {SCORE_LIMIT} Kills", FONT_MEDIUM, YELLOW, screen, WIDTH // 2, 200)

        draw_text("Player 1 Weapon (W/S)", FONT_MEDIUM, RED, screen, WIDTH // 4, 280)
        draw_text(f"<< {weapon_keys[p1_weapon_index]} >>", FONT_BIG, BRIGHT_RED, screen, WIDTH // 4, 340)

        draw_text("Player 1 Character (Q/E)", FONT_MEDIUM, RED, screen, WIDTH // 4, 420)
        draw_text(f"<< {CHARACTERS[character_keys[p1_char_index]]['name']} >>", FONT_MEDIUM, WHITE, screen, WIDTH // 4, 470)

        draw_text("Player 2 Weapon (UP/DOWN)", FONT_MEDIUM, BLUE, screen, 3 * WIDTH // 4, 280)
        draw_text(f"<< {weapon_keys[p2_weapon_index]} >>", FONT_BIG, BRIGHT_BLUE, screen, 3 * WIDTH // 4, 340)

        draw_text("Player 2 Character (I/K)", FONT_MEDIUM, BLUE, screen, 3 * WIDTH // 4, 420)
        draw_text(f"<< {CHARACTERS[character_keys[p2_char_index]]['name']} >>", FONT_MEDIUM, WHITE, screen, 3 * WIDTH // 4, 470)

        draw_text(f"Map Selection (A/D or Left/Right): {map_index + 1} of {map_max_index + 1}", FONT_MEDIUM, WHITE, screen, WIDTH // 2, 560)
        draw_text(f"<< Arena {map_index} >>", FONT_BIG, current_map_colors['HORIZON'], screen, WIDTH // 2, 620)

        draw_text("Press SPACE to Start", FONT_MEDIUM, GREEN, screen, WIDTH // 2, HEIGHT - 140)
        draw_text("Press ESC to return to Mode Select", FONT_SMALL, GRAY, screen, WIDTH // 2, HEIGHT - 90)

        present()

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                _handle_resize(event)

            if event.type == pygame.QUIT:
                return 'quit'

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'mode_select'

                if event.key == pygame.K_SPACE:
                    P1_SELECTED_WEAPON = weapon_keys[p1_weapon_index]
                    P2_SELECTED_WEAPON = weapon_keys[p2_weapon_index]
                    P1_SELECTED_CHARACTER = character_keys[p1_char_index]
                    P2_SELECTED_CHARACTER = character_keys[p2_char_index]
                    SELECTED_MAP_INDEX = map_index
                    return 'game'

                if event.key == pygame.K_w:
                    p1_weapon_index = (p1_weapon_index - 1) % len(weapon_keys)
                if event.key == pygame.K_s:
                    p1_weapon_index = (p1_weapon_index + 1) % len(weapon_keys)
                if event.key == pygame.K_q:
                    p1_char_index = (p1_char_index - 1) % len(character_keys)
                if event.key == pygame.K_e:
                    p1_char_index = (p1_char_index + 1) % len(character_keys)

                if event.key == pygame.K_UP:
                    p2_weapon_index = (p2_weapon_index - 1) % len(weapon_keys)
                if event.key == pygame.K_DOWN:
                    p2_weapon_index = (p2_weapon_index + 1) % len(weapon_keys)
                if event.key == pygame.K_i:
                    p2_char_index = (p2_char_index - 1) % len(character_keys)
                if event.key == pygame.K_k:
                    p2_char_index = (p2_char_index + 1) % len(character_keys)

                if event.key in (pygame.K_a, pygame.K_LEFT):
                    map_index = (map_index - 1) % (map_max_index + 1)
                if event.key in (pygame.K_d, pygame.K_RIGHT):
                    map_index = (map_index + 1) % (map_max_index + 1)

                current_map_colors = MAP_BACKGROUNDS[map_index]

        clock.tick(60)

# --- Mode Select Screen ---
def mode_select_screen():
    global CURRENT_GAME_MODE
    running = True
    menu_options = list(GAME_MODES.keys())
    option_rects = []

    while running:
        screen.fill(BLACK)
        draw_static(screen, noise_amount=20000)

        draw_text("SELECT MODE", FONT_BIG, WHITE, screen, WIDTH // 2, 160)
        y_pos = HEIGHT // 3

        option_rects.clear()
        for i, mode_key in enumerate(menu_options):
            mode_data = GAME_MODES[mode_key]
            text_color = WHITE

            mx, my = to_virtual(pygame.mouse.get_pos())
            mouse_y = my

            row_y = y_pos + i * 120
            if mode_key == CURRENT_GAME_MODE or mouse_y in range(row_y - 30, row_y + 30):
                text_color = YELLOW
            rect = draw_text(mode_data["name"], FONT_MEDIUM, text_color, screen, WIDTH // 2, row_y)
            option_rects.append((mode_key, rect))
            draw_text(mode_data["description"], FONT_SMALL, GRAY, screen, WIDTH // 2, row_y + 40)

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                _handle_resize(event)

            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'menu'
            if event.type == pygame.MOUSEBUTTONDOWN:
                for mode_key, rect in option_rects:
                    if rect.collidepoint(to_virtual(event.pos)):
                        CURRENT_GAME_MODE = mode_key
                        return GAME_MODES[mode_key]['function']

        present()
        clock.tick(60)

# --- Function to setup the game ---
def setup_game():
    global current_map_rects, obstacle_group, jumppad_group, player1, player2, players_group, bullets_group, current_map_colors, current_map_index, CURRENT_GAME_MODE, P1_SELECTED_WEAPON, P2_SELECTED_WEAPON, SELECTED_MAP_INDEX

    if CURRENT_GAME_MODE == "CUSTOM_BATTLE":
        current_map_index = SELECTED_MAP_INDEX
    else:
        current_map_index = random.randrange(len(MAP_OBSTACLES))

    current_map_rects = MAP_OBSTACLES[current_map_index]
    current_map_colors = MAP_BACKGROUNDS[current_map_index]

    obstacle_group = pygame.sprite.Group()
    for rect in current_map_rects:
        obstacle = pygame.sprite.Sprite()
        obstacle.image = pygame.Surface(rect.size)
        obstacle.image.fill(current_map_colors['PLATFORM'])
        obstacle.rect = rect
        obstacle_group.add(obstacle)

    jumppad_group = pygame.sprite.Group()
    # Scaled jump pads for larger maps
    jumppad_group.add(
        JumpPad(300, HEIGHT - GROUND_HEIGHT - 120, 100, 18, launch_strength=-32),
        JumpPad(900, 520, 120, 16, launch_strength=-30)
    )

    controls_p1 = {'left': pygame.K_a, 'right': pygame.K_d,
                    'up': pygame.K_w, 'down': pygame.K_s,
                    'shoot': pygame.K_SPACE, 'shield': pygame.K_f}
    controls_p2 = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT,
                    'up': pygame.K_UP, 'down': pygame.K_DOWN,
                    'shoot': pygame.K_RETURN, 'shield': pygame.K_RSHIFT}

    p1_score = player1.score if 'player1' in globals() else 0
    p2_score = player2.score if 'player2' in globals() else 0

    # Spawn positions adapted to larger canvas
    spawn_p1 = (int(WIDTH * 0.2), int(HEIGHT * 0.3))
    spawn_p2 = (int(WIDTH * 0.8), int(HEIGHT * 0.3))

    if CURRENT_GAME_MODE == "SINGLE_PLAYER_AI":
        player1 = Player(spawn_p1[0], spawn_p1[1], RED, controls_p1, None)
        player2 = AIPlayer(spawn_p2[0], spawn_p2[1], BLUE, {}, player1)
        player1.other_player = player2
    elif CURRENT_GAME_MODE == "CUSTOM_BATTLE":
        char1 = CHARACTERS[P1_SELECTED_CHARACTER]
        char2 = CHARACTERS[P2_SELECTED_CHARACTER]

        player1 = Player(spawn_p1[0], spawn_p1[1], char1["color"], controls_p1, None)
        player1.MAX_HEALTH = char1["health"]
        player1.health = char1["health"]
        player1.speed = char1["speed"]
        player1.special = char1["special"]

        player2 = Player(spawn_p2[0], spawn_p2[1], char2["color"], controls_p2, None)
        player2.MAX_HEALTH = char2["health"]
        player2.health = char2["health"]
        player2.speed = char2["speed"]
        player2.special = char2["special"]

        player1.other_player = player2
        player2.other_player = player1
    else:
        player1 = Player(spawn_p1[0], spawn_p1[1], RED, controls_p1, None)
        player2 = Player(spawn_p2[0], spawn_p2[1], BLUE, controls_p2, None)
        player1.other_player = player2
        player2.other_player = player1

    player1.score = p1_score
    player2.score = p2_score

    if CURRENT_GAME_MODE == "CUSTOM_BATTLE":
        player1.current_weapon = P1_SELECTED_WEAPON
        player2.current_weapon = P2_SELECTED_WEAPON
    else:
        player1.assign_random_weapon()
        player2.assign_random_weapon()

    players_group = pygame.sprite.Group(player1, player2)
    bullets_group = pygame.sprite.Group()

# --- Main Menu ---
def main_menu():
    global player1, player2

    if 'player1' not in globals():
        dummy_controls = {'left': pygame.K_a, 'right': pygame.K_d, 'up': pygame.K_w, 'down': pygame.K_s, 'shoot': pygame.K_SPACE, 'shield': pygame.K_f}
        player1 = Player(int(WIDTH * 0.2), int(HEIGHT * 0.3), RED, dummy_controls, None)
        player2 = Player(int(WIDTH * 0.8), int(HEIGHT * 0.3), BLUE, dummy_controls, None)

    player1.score = 0
    player2.score = 0
    setup_game()

    menu_state = 'menu'

    while menu_state not in ['mode_select', 'quit']:
        screen.fill(BLACK)
        draw_static(screen, noise_amount=20000)

        if menu_state == 'menu':
            draw_text("Stickman Showdown!", FONT_BIG, RED, screen, WIDTH // 2, HEIGHT // 4)
            draw_text(f"First to {SCORE_LIMIT} Wins!", FONT_MEDIUM, WHITE, screen, WIDTH // 2, HEIGHT // 4 + 100)

            start_rect = draw_text("Start Game", FONT_MEDIUM, WHITE, screen, WIDTH // 2, HEIGHT // 2)
            controls_rect = draw_text("Controls", FONT_MEDIUM, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 80)
            quit_rect = draw_text("Quit", FONT_MEDIUM, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 160)

            for event in pygame.event.get():
                if event.type == pygame.VIDEORESIZE:
                    _handle_resize(event)

                if event.type == pygame.QUIT:
                    menu_state = 'quit'
                if event.type == pygame.MOUSEBUTTONDOWN:
                    vpos = to_virtual(event.pos)
                    if start_rect.collidepoint(vpos):
                        menu_state = 'mode_select'
                    elif controls_rect.collidepoint(vpos):
                        menu_state = 'controls'
                    elif quit_rect.collidepoint(vpos):
                        menu_state = 'quit'

        elif menu_state == 'controls':
            show_controls_screen()
            menu_state = 'menu'

        present()
        clock.tick(60)

    return menu_state

# --- Controls Screen ---
def show_controls_screen():
    running = True
    while running:
        screen.fill(BLACK)

        draw_text('Controls', FONT_BIG, WHITE, screen, WIDTH // 2, 120)

        draw_text('Player 1 (RED)', FONT_MEDIUM, RED, screen, WIDTH // 4, 300)
        draw_text('Move: W, A, D', FONT_SMALL, WHITE, screen, WIDTH // 4, 360)
        draw_text('Shoot: SPACE', FONT_SMALL, WHITE, screen, WIDTH // 4, 400)
        draw_text('Shield: F', FONT_SMALL, WHITE, screen, WIDTH // 4, 440)
        draw_text('Weapon: RANDOM per round (Classic)', FONT_SMALL, YELLOW, screen, WIDTH // 4, 480)

        draw_text('Player 2 (BLUE)', FONT_MEDIUM, BLUE, screen, 3 * WIDTH // 4, 300)
        draw_text('Move: Arrow Keys', FONT_SMALL, WHITE, screen, 3 * WIDTH // 4, 360)
        draw_text('Shoot: ENTER/RETURN', FONT_SMALL, WHITE, screen, 3 * WIDTH // 4, 400)
        draw_text('Shield: R-SHIFT', FONT_SMALL, WHITE, screen, 3 * WIDTH // 4, 440)
        draw_text('Weapon: RANDOM per round (Classic)', FONT_SMALL, YELLOW, screen, 3 * WIDTH // 4, 480)

        draw_text('Single Player (vs AI): Blue is AI-controlled', FONT_SMALL, GREEN, screen, WIDTH // 2, 560)
        draw_text('Co-op Survival: Fight waves and a boss together', FONT_SMALL, GREEN, screen, WIDTH // 2, 600)

        draw_text('Press ESC to return to Menu', FONT_MEDIUM, YELLOW, screen, WIDTH // 2, HEIGHT - 140)

        present()

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                _handle_resize(event)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

# --- Game Over Screen ---
def game_over_screen(winner_color_name, winner_color):
    running = True
    while running:
        screen.fill(BLACK)
        draw_static(screen, noise_amount=24000)

        draw_text("GAME OVER", FONT_BIG, WHITE, screen, WIDTH // 2, HEIGHT // 3)
        draw_text(f"{winner_color_name} WINS!", FONT_BIG, winner_color, screen, WIDTH // 2, HEIGHT // 3 + 140)
        draw_text("Press SPACE to return to Menu", FONT_MEDIUM, YELLOW, screen, WIDTH // 2, HEIGHT - 140)

        present()

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                _handle_resize(event)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return 'menu'

# --- Helper: Resolve kill/score and round reset ---
def resolve_kill_if_dead(victim, attacker):
    if victim.health <= 0:
        death_start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - death_start < 1000:
            for event in pygame.event.get():
                if event.type == pygame.VIDEORESIZE:
                    _handle_resize(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Draw background bands with scaled heights
            screen.fill(current_map_colors['SKY'])
            pygame.draw.rect(screen, current_map_colors['HORIZON'], (0, HEIGHT - (HORIZON_HEIGHT + GROUND_HEIGHT), WIDTH, HORIZON_HEIGHT))
            pygame.draw.rect(screen, current_map_colors['GROUND'], (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
            obstacle_group.draw(screen)
            jumppad_group.draw(screen)

            other = player2 if victim == player1 else player1
            other.draw(screen)

            for bullet in bullets_group:
                if isinstance(bullet, Rocket):
                    bullet.draw_explosion(screen)

            victim.death_animation(screen)
            present()
            clock.tick(60)

        attacker.score += 1
        if attacker.score >= SCORE_LIMIT:
            winner_name = "Player 1" if attacker == player1 else "Player 2"
            winner_color = RED if attacker == player1 else BLUE
            return ('game_over', winner_name, winner_color)
        setup_game()
    return None

# --- Main Game Loop ---
def game_loop():
    running = True
    while running:
        keys_pressed = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                _handle_resize(event)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == player1.controls['shoot']:
                    player1.shoot(bullets_group)
                if 'shoot' in player2.controls and event.key == player2.controls.get('shoot', -1):
                    player2.shoot(bullets_group)
                if event.key == pygame.K_ESCAPE:
                    return 'menu'

        for p in players_group:
            if isinstance(p, AIPlayer):
                p.update(None)
            else:
                p.update(keys_pressed)

        bullets_group.update()

        for bullet in list(bullets_group):
            if pygame.sprite.spritecollide(bullet, obstacle_group, False):
                if isinstance(bullet, Rocket):
                    bullet.explode()
                else:
                    bullet.kill()

        for bullet in list(bullets_group):
            target = None
            if bullet.owner != player1 and bullet.rect.colliderect(player1.rect):
                target = player1
            elif bullet.owner != player2 and bullet.rect.colliderect(player2.rect):
                target = player2
            else:
                continue

            if isinstance(bullet, Rocket):
                bullet.explode()
                res1 = resolve_kill_if_dead(player1, bullet.owner)
                if res1:
                    return res1
                res2 = resolve_kill_if_dead(player2, bullet.owner)
                if res2:
                    return res2
            else:
                if not target.is_shielded:
                    target.health -= bullet.damage
                    bullet.kill()
                    result = resolve_kill_if_dead(target, bullet.owner)
                    if result:
                        return result
                else:
                    bullet.kill()

        # --- Drawing (scaled background bands) ---
        screen.fill(current_map_colors['SKY'])
        pygame.draw.rect(screen, current_map_colors['HORIZON'], (0, HEIGHT - (HORIZON_HEIGHT + GROUND_HEIGHT), WIDTH, HORIZON_HEIGHT))
        pygame.draw.rect(screen, current_map_colors['GROUND'], (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))

        obstacle_group.draw(screen)
        jumppad_group.draw(screen)
        player1.draw(screen)
        player2.draw(screen)
        bullets_group.draw(screen)

        for bullet in bullets_group:
            if isinstance(bullet, Rocket):
                bullet.draw_explosion(screen)

        score_text = FONT_MEDIUM.render(f"P1: {player1.score}  P2: {player2.score}", True, BLACK)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 40))

        present()
        clock.tick(60)

    return 'quit'

# --- Survival Mode: Wave System & Loop ---
current_wave = 1
enemies_group = pygame.sprite.Group()

def spawn_wave():
    global current_wave
    enemies_group.empty()
    num_enemies = 2 + current_wave
    for i in range(num_enemies):
        enemy = Enemy(random.randint(80, WIDTH-80), 200, (0, 200, 0), [player1, player2])
        enemies_group.add(enemy)
    current_wave += 1

def survival_game():
    global current_wave
    setup_game()
    current_wave = 1
    spawn_wave()
    boss_spawned = False

    while True:
        keys_pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                _handle_resize(event)

            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == player1.controls['shoot']:
                    player1.shoot(bullets_group)
                if 'shoot' in player2.controls and event.key == player2.controls.get('shoot', -1):
                    player2.shoot(bullets_group)
                if event.key == pygame.K_ESCAPE:
                    return 'menu'

        player1.update(keys_pressed)
        player2.update(keys_pressed)

        for enemy in enemies_group:
            enemy.update(None)

        bullets_group.update()

        for bullet in list(bullets_group):
            if pygame.sprite.spritecollide(bullet, obstacle_group, False):
                if isinstance(bullet, Rocket):
                    bullet.explode()
                else:
                    bullet.kill()

        for bullet in list(bullets_group):
            if isinstance(bullet.owner, Enemy):
                if bullet.rect.colliderect(player1.rect):
                    if not player1.is_shielded:
                        player1.health -= bullet.damage
                    bullet.kill()
                elif bullet.rect.colliderect(player2.rect):
                    if not player2.is_shielded:
                        player2.health -= bullet.damage
                    bullet.kill()
            elif bullet.owner in [player1, player2]:
                for enemy in list(enemies_group):
                    if bullet.rect.colliderect(enemy.rect):
                        if isinstance(bullet, Rocket):
                            bullet.explode()
                        else:
                            enemy.health -= bullet.damage
                            bullet.kill()

        for enemy in list(enemies_group):
            if enemy.health <= 0:
                enemy.kill()

        if player1.health <= 0 and player2.health <= 0:
            return ('game_over', "Enemies", (0, 200, 0))

        if len(enemies_group) == 0:
            if current_wave < 5:
                spawn_wave()
            elif not boss_spawned:
                boss = Boss(WIDTH//2, 220, [player1, player2])
                enemies_group.add(boss)
                boss_spawned = True
            else:
                return ('game_over', "Players", GREEN)

        # --- Drawing (scaled bands) ---
        screen.fill(current_map_colors['SKY'])
        pygame.draw.rect(screen, current_map_colors['HORIZON'], (0, HEIGHT - (HORIZON_HEIGHT + GROUND_HEIGHT), WIDTH, HORIZON_HEIGHT))
        pygame.draw.rect(screen, current_map_colors['GROUND'], (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))

        obstacle_group.draw(screen)
        jumppad_group.draw(screen)

        for enemy in enemies_group:
            enemy.draw(screen)

        player1.draw(screen)
        player2.draw(screen)
        bullets_group.draw(screen)

        hud_text = FONT_MEDIUM.render(f"Wave: {min(current_wave, 5)}  P1 HP: {player1.health}  P2 HP: {player2.health}", True, BLACK)
        screen.blit(hud_text, (WIDTH//2 - hud_text.get_width()//2, 40))

        for bullet in bullets_group:
            if isinstance(bullet, Rocket):
                bullet.draw_explosion(screen)

        present()
        clock.tick(60)

# --- Main Application State Machine ---
if __name__ == '__main__':
    game_state = 'menu'
    winner_name = None
    winner_color = None

    dummy_controls = {'left': pygame.K_a, 'right': pygame.K_d, 'up': pygame.K_w, 'down': pygame.K_s, 'shoot': pygame.K_SPACE, 'shield': pygame.K_f}
    player1 = Player(int(WIDTH * 0.2), int(HEIGHT * 0.3), RED, dummy_controls, None)
    player2 = Player(int(WIDTH * 0.8), int(HEIGHT * 0.3), BLUE, dummy_controls, None)

    while True:
        if game_state == 'menu':
            game_state = main_menu()
        elif game_state == 'mode_select':
            game_state = mode_select_screen()
        elif game_state == 'custom_setup':
            game_state = custom_battle_setup_screen()
        elif game_state == 'game':
            setup_game()
            result = game_loop()
            if isinstance(result, tuple) and result[0] == 'game_over':
                game_state, winner_name, winner_color = result
            elif result == 'menu':
                game_state = 'menu'
            elif result == 'quit':
                game_state = 'quit'
        elif game_state == 'survival_game':
            result = survival_game()
            if isinstance(result, tuple) and result[0] == 'game_over':
                winner_name = result[1]
                winner_color = result[2]
                game_state = 'game_over'
            elif result == 'menu':
                game_state = 'menu'
            elif result == 'quit':
                game_state = 'quit'
        elif game_state == 'game_over':
            game_state = game_over_screen(winner_name, winner_color)
        elif game_state == 'quit':
            pygame.quit()
            sys.exit()
