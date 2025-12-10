import pygame
import random
import math
import time

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 900, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Fortnite Style Game")

# Colors
WHITE  = (255, 255, 255)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLUE   = (0, 120, 255)
GOLD   = (255, 215, 0)
BLACK  = (0, 0, 0)
PURPLE = (180, 0, 180)
BG     = (40, 40, 45)

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- Player ---
player = pygame.Rect(WIDTH // 2 - 20, HEIGHT // 2 - 30, 40, 60)
player_speed = 6
sprint_speed = 10
PLAYER_MAX_HEALTH = 100
player_health = PLAYER_MAX_HEALTH

# --- Bullets [rect, vx, vy, distance_traveled, max_distance, damage] ---
bullets = []
bullet_speed = 12

# --- Score ---
score = 0

# --- Weapons ---
current_weapon = None
last_shot_time = 0
sniper_delay = 0.8
shotgun_range = 220
weapon_damage = {
    "Shotgun": 20,
    "AR": 25,
    "Sniper": 100
}

# ---------------------------------------------------------
# NEW: Spawning helpers
# ---------------------------------------------------------
def spawn_far_from_player(min_distance=250):
    """Return an (x, y) location far enough away from the player."""
    while True:
        x = random.randint(0, WIDTH - 60)
        y = random.randint(0, HEIGHT - 80)
        dx = x - player.x
        dy = y - player.y
        if math.hypot(dx, dy) >= min_distance:
            return x, y

# --- Normal bot ---
def spawn_bot():
    x, y = spawn_far_from_player()
    return pygame.Rect(x, y, 40, 60)

bot = spawn_bot()
bot_health = 100
bot_speed = 2

# --- Golden bot ---
golden_bot = None
golden_bot_health = 0
golden_bot_speed = 2

def spawn_golden_bot():
    x, y = spawn_far_from_player()
    return pygame.Rect(x, y, 40, 60)

# --- Boss ---
boss = None
boss_health = 0
boss_max_health = 0
boss_speed = 1.2
last_boss_score = 0
boss_spawn_count = 0

def spawn_boss():
    x, y = spawn_far_from_player(min_distance=350)
    return pygame.Rect(x, y, 100, 140)

# --- Reset ---
def reset_game_state():
    global player_health, score, bullets
    global bot, bot_health, golden_bot, golden_bot_health
    global boss, boss_health, boss_max_health, last_boss_score, boss_spawn_count
    global current_weapon, last_shot_time

    player_health = PLAYER_MAX_HEALTH
    score = 0
    bullets.clear()

    bot = spawn_bot()
    bot_health = 100

    golden_bot = None
    golden_bot_health = 0

    boss = None
    boss_health = 0
    boss_max_health = 0
    last_boss_score = 0
    boss_spawn_count = 0

    current_weapon = None
    last_shot_time = 0

    player.x = WIDTH // 2 - player.width // 2
    player.y = HEIGHT // 2 - player.height // 2

# --- Draw ---
def draw():
    WIN.fill(BG)
    pygame.draw.rect(WIN, BLUE, player)

    if bot_health > 0:
        pygame.draw.rect(WIN, RED, bot)
    if golden_bot_health > 0:
        pygame.draw.rect(WIN, GOLD, golden_bot)
    if boss_health > 0:
        pygame.draw.rect(WIN, PURPLE, boss)

    for rect, vx, vy, dist, max_dist, dmg in bullets:
        pygame.draw.rect(WIN, WHITE, rect)

    # HUD
    health_bar_w = int((player_health / PLAYER_MAX_HEALTH) * 200)
    pygame.draw.rect(WIN, GREEN, (20, 20, max(0, health_bar_w), 20))
    WIN.blit(font.render(f"Health: {int(player_health)}", True, WHITE), (230, 18))
    WIN.blit(font.render(f"Score: {score}", True, WHITE), (20, 50))

    weap = current_weapon if current_weapon else "None"
    WIN.blit(font.render(f"Weapon: {weap}", True, WHITE), (20, 80))

    if boss_health > 0 and boss_max_health > 0:
        bar_w = int((boss_health / boss_max_health) * (WIDTH - 40))
        pygame.draw.rect(WIN, PURPLE, (20, 120, max(0, bar_w), 16))
        WIN.blit(font.render(f"Boss HP: {boss_health}", True, WHITE), (20, 140))

    pygame.display.update()

# --- Movement ---
def move_bot():
    global bot_health, player_health
    if bot_health <= 0 or boss_health > 0:
        return
    dx = player.x - bot.x
    dy = player.y - bot.y
    dist = math.hypot(dx, dy)
    if dist != 0:
        bot.x += bot_speed * dx / dist
        bot.y += bot_speed * dy / dist
    if bot.colliderect(player):
        player_health -= 10
        bot_health = 0

def move_golden_bot():
    global golden_bot_health, player_health
    if golden_bot_health <= 0 or boss_health > 0:
        return
    dx = player.x - golden_bot.x
    dy = player.y - golden_bot.y
    dist = math.hypot(dx, dy)
    if dist != 0:
        golden_bot.x += golden_bot_speed * dx / dist
        golden_bot.y += golden_bot_speed * dy / dist
    if golden_bot.colliderect(player):
        player_health -= 10
        golden_bot_health = 0

def move_boss():
    global boss_health, player_health
    if boss_health <= 0:
        return
    dx = player.x - boss.x
    dy = player.y - boss.y
    dist = math.hypot(dx, dy)
    if dist != 0:
        boss.x += boss_speed * dx / dist
        boss.y += boss_speed * dy / dist
    if boss.colliderect(player):
        player_health -= 20

# --- Bullets ---
def handle_bullets():
    global bot_health, bot, score, golden_bot_health, golden_bot
    global boss_health, boss, last_boss_score
    for b in bullets[:]:
        rect, vx, vy, dist, max_dist, dmg = b
        rect.x += vx
        rect.y += vy
        dist += math.hypot(vx, vy)
        b[3] = dist

        if rect.x < -30 or rect.x > WIDTH + 30 or rect.y < -30 or rect.y > HEIGHT + 30 or dist > max_dist:
            bullets.remove(b)
            continue

        if boss_health > 0 and rect.colliderect(boss):
            boss_health -= dmg
            if boss_health <= 0:
                score += 10
                boss = None
                last_boss_score = score
            bullets.remove(b)
            continue

        if boss_health <= 0 and bot_health > 0 and rect.colliderect(bot):
            bot_health -= dmg
            if bot_health <= 0:
                score += 1
                if random.randint(1, 10) == 1 and golden_bot_health <= 0:
                    golden_bot = spawn_golden_bot()
                    golden_bot_health = 100
            bullets.remove(b)
            continue

        if boss_health <= 0 and golden_bot_health > 0 and rect.colliderect(golden_bot):
            golden_bot_health -= dmg
            if golden_bot_health <= 0:
                score += 10
            bullets.remove(b)
            continue

# --- Spawns ---
def check_bot_respawn():
    global bot, bot_health
    if boss_health > 0:
        return
    if bot_health <= 0:
        bot = spawn_bot()
        bot_health = 100

def check_boss_spawn():
    global boss, boss_health, boss_max_health, last_boss_score, boss_spawn_count
    if boss_health <= 0 and score >= last_boss_score + 50:
        boss = spawn_boss()
        boss_max_health = 500 + boss_spawn_count * 1000
        boss_health = boss_max_health
        boss_spawn_count += 1
        last_boss_score = score

# --- Shooting ---
def shoot(mx, my):
    global last_shot_time
    if current_weapon is None:
        return
    bx = player.x + player.width // 2
    by = player.y + player.height // 2
    dx = mx - bx
    dy = my - by
    dist = math.hypot(dx, dy) or 1
    vel_x = bullet_speed * (dx / dist)
    vel_y = bullet_speed * (dy / dist)

    if current_weapon == "AR":
        bullet_rect = pygame.Rect(bx, by, 10, 5)
        bullets.append([bullet_rect, vel_x, vel_y, 0, 1000, weapon_damage["AR"]])

    elif current_weapon == "Sniper":
        now = time.time()
        if now - last_shot_time >= sniper_delay:
            bullet_rect = pygame.Rect(bx, by, 12, 6)
            bullets.append([bullet_rect, vel_x, vel_y, 0, 1500, weapon_damage["Sniper"]])
            last_shot_time = now

    elif current_weapon == "Shotgun":
        spread_angles = [-0.25, -0.12, 0, 0.12, 0.25]
        angle = math.atan2(dy, dx)
        for offset in spread_angles:
            vx = bullet_speed * math.cos(angle + offset)
            vy = bullet_speed * math.sin(angle + offset)
            bullet_rect = pygame.Rect(bx, by, 8, 4)
            bullets.append([bullet_rect, vx, vy, 0, shotgun_range, weapon_damage["Shotgun"]])

# --- Menu ---
def menu():
    global current_weapon
    reset_game_state()
    current_weapon = None
    run = True
    while run:
        WIN.fill(BLACK)
        title = font.render("Choose Your Weapon", True, WHITE)
        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 170))

        option1 = font.render(f"1 - Shotgun (spread, short range)  Damage: {weapon_damage['Shotgun']} per pellet", True, WHITE)
        option2 = font.render(f"2 - AR (normal fire)  Damage: {weapon_damage['AR']}", True, WHITE)
        option3 = font.render(f"3 - Sniper (slow rate, long range)  Damage: {weapon_damage['Sniper']}", True, WHITE)
        boss_info = font.render("Boss spawns at each +50 score; +1000 HP each spawn; bots pause during boss.", True, PURPLE)
        hint     = font.render("Press 1, 2, or 3 to start", True, GOLD)

        WIN.blit(option1, (WIDTH // 2 - option1.get_width() // 2, HEIGHT // 2 - 60))
        WIN.blit(option2, (WIDTH // 2 - option2.get_width() // 2, HEIGHT // 2 - 20))
        WIN.blit(option3, (WIDTH // 2 - option3.get_width() // 2, HEIGHT // 2 + 20))
        WIN.blit(boss_info, (WIDTH // 2 - boss_info.get_width() // 2, HEIGHT // 2 + 70))
        WIN.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 120))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_weapon = "Shotgun"
                    run = False
                elif event.key == pygame.K_2:
                    current_weapon = "AR"
                    run = False
                elif event.key == pygame.K_3:
                    current_weapon = "Sniper"
                    run = False
    return True

# --- Main loop ---
def main():
    global player_health, bot_health, golden_bot_health
    if not menu():
        return

    run = True
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                shoot(mx, my)

        # Movement + Sprint
        keys = pygame.key.get_pressed()
        speed = sprint_speed if keys[pygame.K_LSHIFT] else player_speed
        if keys[pygame.K_a] and player.x > 0:
            player.x -= speed
        if keys[pygame.K_d] and player.x < WIDTH - player.width:
            player.x += speed
        if keys[pygame.K_w] and player.y > 0:
            player.y -= speed
        if keys[pygame.K_s] and player.y < HEIGHT - player.height:
            player.y += speed

        move_boss()
        move_bot()
        move_golden_bot()
        handle_bullets()
        check_boss_spawn()
        check_bot_respawn()
        draw()

        if player_health <= 0:
            print(f"GAME OVER — Final Score: {score}")
            pygame.time.delay(1200)
            if not menu():
                run = False

    pygame.quit()

if __name__ == "__main__":
    main()
