import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Shooting Game")

# --- Game Settings ---
SCORE_LIMIT = 10 # First player to reach this score wins!

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
CYAN = (0, 255, 255) # Jump Pad Color
YELLOW = (255, 255, 0) # Shield Color

# Clock
clock = pygame.time.Clock()

# --- Font Setup ---
pygame.font.init()
FONT_BIG = pygame.font.SysFont(None, 72)
FONT_MEDIUM = pygame.font.SysFont(None, 36)
FONT_SMALL = pygame.font.SysFont(None, 24)

# --- Shield Constants ---
SHIELD_DURATION_MS = 1500 # Shield lasts for 1.5 seconds
SHIELD_COOLDOWN_MS = 5000 # Cooldown is 5 seconds

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
    }
}
WEAPON_ORDER = ["PISTOL", "SHOTGUN", "MACHINE_GUN"] # Used for random selection

# --- Map Data (8 Unique Obstacles and Backgrounds) ---
MAP_OBSTACLES = [
    # Map 0: Centralized Platforms
    [pygame.Rect(200, 150, 100, 30), pygame.Rect(400, 300, 200, 30), pygame.Rect(100, 450, 150, 30)],
    # Map 1: Tiered Levels
    [pygame.Rect(300, 200, 200, 30), pygame.Rect(150, 350, 100, 30), pygame.Rect(500, 450, 200, 30)],
    # Map 2: High/Low Corners
    [pygame.Rect(250, 250, 300, 30), pygame.Rect(100, 100, 150, 30), pygame.Rect(600, 400, 150, 30)],
    # Map 3: Walls and Center
    [pygame.Rect(300, 400, 200, 30), pygame.Rect(50, 250, 50, 150), pygame.Rect(700, 250, 50, 150)],
    # Map 4: The Bridge (High sides, low center)
    [pygame.Rect(50, 400, 100, 30), pygame.Rect(650, 400, 100, 30), pygame.Rect(200, 500, 400, 30)],
    # Map 5: The Pit (Center platform high, rest is open)
    [pygame.Rect(300, 150, 200, 30), pygame.Rect(100, 450, 100, 30), pygame.Rect(600, 450, 100, 30)],
    # Map 6: Vertical Chaos (Staggered small platforms)
    [pygame.Rect(100, 450, 80, 20), pygame.Rect(250, 350, 80, 20), pygame.Rect(400, 250, 80, 20), pygame.Rect(550, 150, 80, 20)],
    # Map 7: Symmetrical Arena (Mirrored opposing platforms)
    [pygame.Rect(50, 350, 150, 30), pygame.Rect(600, 350, 150, 30), pygame.Rect(50, 500, 50, 30), pygame.Rect(700, 500, 50, 30)]
]

# Background Colors corresponding to the MAP_OBSTACLES index
MAP_BACKGROUNDS = [
    {'SKY': (135, 206, 235), 'HORIZON': (173, 216, 230), 'GROUND': (50, 50, 50), 'PLATFORM': (150, 150, 150)},
    {'SKY': (75, 0, 130), 'HORIZON': (150, 110, 200), 'GROUND': (60, 40, 40), 'PLATFORM': (100, 100, 100)},
    {'SKY': (255, 69, 0), 'HORIZON': (255, 140, 0), 'GROUND': (100, 0, 0), 'PLATFORM': (200, 100, 0)},
    {'SKY': (0, 0, 20), 'HORIZON': (25, 25, 75), 'GROUND': (80, 80, 80), 'PLATFORM': (120, 120, 120)},
    {'SKY': (170, 190, 200), 'HORIZON': (230, 230, 230), 'GROUND': (50, 80, 100), 'PLATFORM': (150, 110, 80)}, 
    {'SKY': (150, 50, 50), 'HORIZON': (255, 100, 0), 'GROUND': (180, 180, 180), 'PLATFORM': (200, 200, 200)},
    {'SKY': (0, 30, 60), 'HORIZON': (0, 150, 150), 'GROUND': (0, 0, 0), 'PLATFORM': (0, 255, 255)}, 
    {'SKY': (10, 10, 10), 'HORIZON': (50, 0, 100), 'GROUND': (80, 0, 80), 'PLATFORM': (255, 0, 255)}
]

# Global variables to hold the current map and background colors
current_map_colors = MAP_BACKGROUNDS[0]
current_map_index = 0

# Function to setup the game (used for initial setup and round reset)
def setup_game():
    global current_map_rects, obstacle_group, jumppad_group, player1, player2, players_group, bullets_group, current_map_colors, current_map_index
    
    # 1. Select a random map index
    current_map_index = random.randrange(len(MAP_OBSTACLES))
    current_map_rects = MAP_OBSTACLES[current_map_index]
    current_map_colors = MAP_BACKGROUNDS[current_map_index]

    # 2. Setup Obstacles
    obstacle_group = pygame.sprite.Group()
    for rect in current_map_rects:
        obstacle = pygame.sprite.Sprite()
        obstacle.image = pygame.Surface(rect.size)
        obstacle.image.fill(current_map_colors['PLATFORM'])
        obstacle.rect = rect
        obstacle_group.add(obstacle)

    # 3. Setup Jump Pads 
    jumppad_group = pygame.sprite.Group()
    jumppad_group.add(
        JumpPad(150, HEIGHT - 80),
        JumpPad(450, 280, 80, 12, launch_strength=-30)
    )

    # 4. Setup Players
    controls_p1 = {'left': pygame.K_a, 'right': pygame.K_d,
                    'up': pygame.K_w, 'down': pygame.K_s, 
                    'shoot': pygame.K_SPACE, 'shield': pygame.K_f}
    controls_p2 = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT,
                    'up': pygame.K_UP, 'down': pygame.K_DOWN, 
                    'shoot': pygame.K_RETURN, 'shield': pygame.K_RSHIFT}

    # Store player scores so they persist across resets
    p1_score = player1.score if 'player1' in globals() else 0
    p2_score = player2.score if 'player2' in globals() else 0
    
    player1 = Player(200, 200, RED, controls_p1, None) 
    player2 = Player(600, 200, BLUE, controls_p2, None)
    
    player1.score = p1_score
    player2.score = p2_score
    
    player1.other_player = player2
    player2.other_player = player1

    # --- Random Weapon Assignment at Setup ---
    player1.assign_random_weapon()
    player2.assign_random_weapon()

    players_group = pygame.sprite.Group(player1, player2)
    bullets_group = pygame.sprite.Group()


# --- Jump Pad Class (Unchanged) ---
class JumpPad(pygame.sprite.Sprite):
    def __init__(self, x, y, width=60, height=12, launch_strength=-25):
        super().__init__()

        self.image = pygame.Surface((width, height), pygame.SRCALPHA)

        # Base
        pygame.draw.rect(self.image, CYAN, (0, 4, width, height - 4))
        pygame.draw.rect(self.image, BLACK, (0, 4, width, height - 4), 1)

        # Triangle indicator
        pygame.draw.polygon(self.image, (255, 255, 0), [
            (width//2 - 10, 4),
            (width//2 + 10, 4),
            (width//2, 0)
        ])

        self.rect = self.image.get_rect(topleft=(x, y))
        self.launch_strength = launch_strength


# Player class (Unchanged)
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, controls, other_player):
        super().__init__()
        self.image = pygame.Surface((40, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.controls = controls
        self.score = 0
        self.color = color
        
        # Physics Attributes
        self.is_jumping = True 
        self.vertical_velocity = 0
        
        self.direction = "right"
        self.other_player = other_player
        
        # Health Attributes
        self.MAX_HEALTH = 100
        self.health = self.MAX_HEALTH
        
        self.initial_pos = (x, y)
        
        # --- Shield Attributes ---
        self.is_shielded = False
        self.shield_active_time = 0
        self.shield_cooldown_time = 0

        # --- ANIMATION Attributes ---
        self.walk_frame = 0 
        self.is_moving = False

        # --- WEAPON Attributes ---
        self.current_weapon = WEAPON_ORDER[0]
        self.last_shot_time = 0 
        
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

        if keys_pressed[self.controls['up']]:
            self.jump()

        if keys_pressed[self.controls['shield']]:
            self.activate_shield()
            
        x_change = 0
        self.is_moving = False
        
        if keys_pressed[self.controls['left']]:
            x_change = -self.speed
            self.direction = "left"
            self.is_moving = True
            
        if keys_pressed[self.controls['right']]:
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
            self.shield_active_time = current_time + SHIELD_DURATION_MS
            self.shield_cooldown_time = current_time + SHIELD_COOLDOWN_MS 
    
    def draw_health_bar(self, surface):
        BAR_WIDTH = 40
        BAR_HEIGHT = 7
        x = self.rect.x
        y = self.rect.y - 10 
        fill = (self.health / self.MAX_HEALTH) * BAR_WIDTH
        outline_rect = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        pygame.draw.rect(surface, RED, outline_rect)
        pygame.draw.rect(surface, GREEN, fill_rect)
        pygame.draw.rect(surface, BLACK, outline_rect, 1)

    def draw_weapon_info(self, surface):
        weapon_text = FONT_SMALL.render(self.current_weapon, True, BLACK)
        x = self.rect.x + self.rect.width // 2 - weapon_text.get_width() // 2
        y = self.rect.y - 25
        surface.blit(weapon_text, (x, y))

    def draw(self, surface):
        cx, cy = self.rect.center
        
        # --- Draw Shield ---
        if self.is_shielded:
            alpha = 255
            elapsed = pygame.time.get_ticks() - (self.shield_active_time - SHIELD_DURATION_MS)
            if SHIELD_DURATION_MS - elapsed < 500: 
                alpha = 100 + (elapsed % 100 < 50) * 155
            
            shield_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            shield_color = YELLOW + (int(alpha),) 
            
            pygame.draw.circle(shield_surface, shield_color, (50, 50), 50, 3)
            
            surface.blit(shield_surface, (cx - 50, cy - 50))
            
        # Draw Stickman 
        pygame.draw.circle(surface, self.color, (cx, cy - 30), 10, 0) # Head
        pygame.draw.line(surface, self.color, (cx, cy - 20), (cx, cy + 20), 2) # Body
        pygame.draw.line(surface, self.color, (cx, cy - 10), (cx - 20, cy + 10), 2) # Left Arm
        pygame.draw.line(surface, self.color, (cx, cy - 10), (cx + 20, cy + 10), 2) # Right Arm
        
        # --- Legs (Walking Animation Logic) ---
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
        
        # --- Weapon (Detailed - Unchanged) ---
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
        
        for i in range(weapon['bullets']):
            if weapon['spread'] > 0:
                spread_offset = random.uniform(-weapon['spread'], weapon['spread'])
            else:
                spread_offset = 0

            bullet = Bullet(
                start_x, 
                start_y + spread_offset, 
                self.color, 
                self.direction, 
                self,
                weapon['damage'],
                weapon['size'],
                weapon['speed']
            )
            bullets_group.add(bullet)
    

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

# --- Player Reset (Used for Round Reset) ---
def reset_round_state(player):
    player.health = player.MAX_HEALTH
    player.rect.center = player.initial_pos
    player.is_jumping = True
    player.vertical_velocity = 0
    player.is_shielded = False 
    player.shield_cooldown_time = pygame.time.get_ticks()
    player.last_shot_time = 0
    
    # --- Assign random weapon on round reset ---
    player.assign_random_weapon()


# --- Menu/State Functions ---

def draw_text(text, font, color, surface, x, y, center=True):
    """Utility function to draw text, defaults to centering."""
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
    return textrect

# --- UPDATED: Function to draw static/noise effect (Default noise amount increased) ---
def draw_static(surface, noise_amount=5000):
    """Draws random gray/white pixels to simulate TV static."""
    for _ in range(noise_amount):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        
        # Random shade of gray/white for the static
        intensity = random.randint(100, 255) 
        color = (intensity, intensity, intensity)
        
        surface.set_at((x, y), color)


# --- Controls Screen (Unchanged) ---
def show_controls_screen():
    running = True
    while running:
        screen.fill(BLACK)
        
        draw_text('Controls', FONT_BIG, WHITE, screen, WIDTH // 2, 50)
        
        # Player 1 Controls
        draw_text('Player 1 (RED)', FONT_MEDIUM, RED, screen, WIDTH // 4, 150)
        draw_text('Move: W, A, D', FONT_SMALL, WHITE, screen, WIDTH // 4, 200)
        draw_text('Shoot: SPACE', FONT_SMALL, WHITE, screen, WIDTH // 4, 230)
        draw_text('Shield: F', FONT_SMALL, WHITE, screen, WIDTH // 4, 260)
        draw_text('Weapon: RANDOM per round', FONT_SMALL, YELLOW, screen, WIDTH // 4, 290)
        
        # Player 2 Controls
        draw_text('Player 2 (BLUE)', FONT_MEDIUM, BLUE, screen, 3 * WIDTH // 4, 150)
        draw_text('Move: Arrow Keys', FONT_SMALL, WHITE, screen, 3 * WIDTH // 4, 200)
        draw_text('Shoot: ENTER/RETURN', FONT_SMALL, WHITE, screen, 3 * WIDTH // 4, 230)
        draw_text('Shield: R-SHIFT', FONT_SMALL, WHITE, screen, 3 * WIDTH // 4, 260)
        draw_text('Weapon: RANDOM per round', FONT_SMALL, YELLOW, screen, 3 * WIDTH // 4, 290)
        
        draw_text('Press ESC to return to Menu', FONT_MEDIUM, YELLOW, screen, WIDTH // 2, HEIGHT - 50)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

# --- Main Menu (UPDATED: Static noise amount increased) ---
def main_menu():
    global player1, player2 
    
    # Initial player setup if they don't exist
    if 'player1' not in globals():
        dummy_controls = {'left': pygame.K_a, 'right': pygame.K_d, 'up': pygame.K_w, 'down': pygame.K_s, 'shoot': pygame.K_SPACE, 'shield': pygame.K_f}
        player1 = Player(200, 200, RED, dummy_controls, None) 
        player2 = Player(600, 200, BLUE, dummy_controls, None)

    player1.score = 0
    player2.score = 0
    setup_game() 
    
    menu_state = 'menu'
    
    while menu_state != 'start_game':
        # Draw static background - increased from 300 to 5000 
        screen.fill(BLACK)
        draw_static(screen, noise_amount=5000)
        
        if menu_state == 'menu':
            # Draw Title
            draw_text("Stickman Showdown!", FONT_BIG, RED, screen, WIDTH // 2, HEIGHT // 4)
            draw_text(f"First to {SCORE_LIMIT} Wins! (Random Weapon)", FONT_MEDIUM, WHITE, screen, WIDTH // 2, HEIGHT // 4 + 70) 
            
            # Menu Options
            start_rect = draw_text("Start Game", FONT_MEDIUM, WHITE, screen, WIDTH // 2, HEIGHT // 2)
            controls_rect = draw_text("Controls", FONT_MEDIUM, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 50)
            quit_rect = draw_text("Quit", FONT_MEDIUM, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 100)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_rect.collidepoint(event.pos):
                        menu_state = 'start_game'
                    elif controls_rect.collidepoint(event.pos):
                        menu_state = 'controls'
                    elif quit_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
            
        elif menu_state == 'controls':
            show_controls_screen()
            menu_state = 'menu' 
            
        pygame.display.flip()
        clock.tick(60) 

    setup_game()
    return 'game'

# --- Game Over Screen (UPDATED: Static noise amount increased) ---
def game_over_screen(winner_color_name, winner_color):
    running = True
    while running:
        # Draw static on game over screen - increased from 500 to 8000
        screen.fill(BLACK)
        draw_static(screen, noise_amount=8000)
        
        draw_text("GAME OVER", FONT_BIG, WHITE, screen, WIDTH // 2, HEIGHT // 3)
        draw_text(f"{winner_color_name} WINS!", FONT_BIG, winner_color, screen, WIDTH // 2, HEIGHT // 3 + 100)
        draw_text("Press SPACE to return to Menu", FONT_MEDIUM, YELLOW, screen, WIDTH // 2, HEIGHT - 100)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return 'menu'

# --- Main Game Loop (Unchanged) ---
def game_loop():
    running = True
    while running:
        keys_pressed = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                # Shooting
                if event.key == player1.controls['shoot']:
                    player1.shoot(bullets_group)
                if event.key == player2.controls['shoot']:
                    player2.shoot(bullets_group)
                
                # Check for return to menu
                if event.key == pygame.K_ESCAPE:
                    return 'menu'

        # --- Game Logic Update ---
        players_group.update(keys_pressed)
        bullets_group.update()

        pygame.sprite.groupcollide(bullets_group, obstacle_group, True, False)
        
        # Bullet collision with players
        for bullet in bullets_group:
            target = None
            if bullet.owner != player1 and bullet.rect.colliderect(player1.rect):
                target = player1
            elif bullet.owner != player2 and bullet.rect.colliderect(player2.rect):
                target = player2
            else:
                continue 
            
            if not target.is_shielded:
                target.health -= bullet.damage 
                bullet.kill()
                
                if target.health <= 0:
                    bullet.owner.score += 1
                    
                    # WIN CHECK 
                    if bullet.owner.score >= SCORE_LIMIT:
                        winner_name = "Player 1" if bullet.owner == player1 else "Player 2"
                        winner_color = RED if bullet.owner == player1 else BLUE
                        return ('game_over', winner_name, winner_color) 
                    
                    # If no win, reset the round (resets health, position, and loads new map AND assigns new random weapon)
                    setup_game() 
            else:
                bullet.kill()
                
        # --- Drawing ---
        screen.fill(current_map_colors['SKY']) 
        pygame.draw.rect(screen, current_map_colors['HORIZON'], (0, HEIGHT - 150, WIDTH, 150))
        pygame.draw.rect(screen, current_map_colors['GROUND'], (0, HEIGHT - 50, WIDTH, 50))
        
        obstacle_group.draw(screen)
        jumppad_group.draw(screen) 
        player1.draw(screen)
        player2.draw(screen)
        bullets_group.draw(screen)

        # Score display
        score_text = FONT_MEDIUM.render(f"P1: {player1.score}  P2: {player2.score}", True, BLACK)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))

        pygame.display.flip()
        clock.tick(60)
        
    return 'quit'


# --- Main Application State Machine (Unchanged) ---
if __name__ == '__main__':
    game_state = 'menu'
    winner_name = None
    winner_color = None

    while True:
        if game_state == 'menu':
            game_state = main_menu()
        elif game_state == 'game':
            result = game_loop()
            if isinstance(result, tuple) and result[0] == 'game_over':
                game_state, winner_name, winner_color = result
            elif result == 'menu':
                game_state = 'menu'
            elif result == 'quit':
                game_state = 'quit'
        elif game_state == 'game_over':
            game_state = game_over_screen(winner_name, winner_color)
        elif game_state == 'quit':
            pygame.quit()
            sys.exit()