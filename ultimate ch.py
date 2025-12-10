import pygame
import random
import time

pygame.init()
WIDTH, HEIGHT = 900, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Chicken Horse - Python Edition")

FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 80, 80)
GREEN = (80, 255, 80)
BLUE  = (80, 80, 255)
GREY  = (200, 200, 200)

PLAYER_SIZE = 30
GRAVITY = 0.5
WINNING_SCORE = 15
FONT = pygame.font.Font(None, 40)

# ---------------------------------------------------------
# PROJECTILE CLASS (for shooting traps)
# ---------------------------------------------------------
class Projectile:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 12, 6)
        self.speed = 7 * direction

    def update(self):
        self.rect.x += self.speed

    def draw(self):
        pygame.draw.rect(WIN, RED, self.rect)


# ---------------------------------------------------------
# PLAYER CLASS
# ---------------------------------------------------------
class Player:
    def __init__(self, x, y, color, name):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.color = color
        self.vel_y = 0
        self.on_ground = False
        self.alive = True
        self.finished = False
        self.score = 0
        self.name = name

    def update(self, platforms, traps, projectiles):
        if not self.alive or self.finished:
            return

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.on_ground = False

        # Platform/wall collision
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vel_y > 0:
                    self.rect.bottom = p.top
                    self.vel_y = 0
                    self.on_ground = True

        # Trap collision
        for t in traps:
            if self.rect.colliderect(t):
                self.alive = False

        # Projectile collision
        for proj in projectiles:
            if self.rect.colliderect(proj.rect):
                self.alive = False

        # Fall off map
        if self.rect.top > HEIGHT:
            self.alive = False

    def move(self, keys, left_key, right_key, jump_key):
        if not self.alive or self.finished:
            return
        if keys[left_key]:
            self.rect.x -= 5
        if keys[right_key]:
            self.rect.x += 5
        if keys[jump_key] and self.on_ground:
            self.vel_y = -10

    def draw(self):
        pygame.draw.rect(WIN, self.color, self.rect)


# ---------------------------------------------------------
# BUILD PHASE
# ---------------------------------------------------------
def build_phase(placeables, placed_data):
    clock = pygame.time.Clock()
    selected = 0  # which item is selected

    while True:
        clock.tick(FPS)
        WIN.fill(GREY)
        mx, my = pygame.mouse.get_pos()

        obj_type, rect = placeables[selected]

        # Move preview object
        preview = rect.copy()
        preview.x = mx - preview.width//2
        preview.y = my - preview.height//2
        
        color = BLUE if obj_type != "trap_shooter" else RED
        pygame.draw.rect(WIN, color, preview, 2)

        # Draw placed structures
        for p in placed_data["platforms"]:
            pygame.draw.rect(WIN, BLACK, p)
        for w in placed_data["walls"]:
            pygame.draw.rect(WIN, BLACK, w)
        for t in placed_data["traps"]:
            pygame.draw.rect(WIN, RED, t)
        for s in placed_data["shooters"]:
            pygame.draw.rect(WIN, BLUE, s)

        # Selector UI
        pygame.draw.rect(WIN, WHITE, (20, 520, 350, 70))
        label = obj_type.replace("_", " ").title()
        txt = FONT.render(f"Selected: {label}", True, BLACK)
        WIN.blit(txt, (30, 540))

        instruction = FONT.render("BUILD - Click to place | Q/E to change | ENTER to start", True, BLACK)
        WIN.blit(instruction, (20, 20))

        pygame.display.update()

        # -------------------- EVENTS --------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                if event.key == pygame.K_q:
                    selected = (selected - 1) % len(placeables)
                if event.key == pygame.K_e:
                    selected = (selected + 1) % len(placeables)

            if event.type == pygame.MOUSEBUTTONDOWN:
                new_obj = rect.copy()
                new_obj.x = mx - new_obj.width//2
                new_obj.y = my - new_obj.height//2

                if obj_type == "platform":
                    placed_data["platforms"].append(new_obj)
                elif obj_type == "wall":
                    placed_data["walls"].append(new_obj)
                elif obj_type == "trap":
                    placed_data["traps"].append(new_obj)
                elif obj_type == "trap_shooter":
                    placed_data["shooters"].append(new_obj)


# ---------------------------------------------------------
# RUN PHASE
# ---------------------------------------------------------
def run_phase(players, placed_data, goal):
    clock = pygame.time.Clock()

    projectiles = []
    last_shot_time = time.time()

    while True:
        clock.tick(FPS)
        WIN.fill(WHITE)
        keys = pygame.key.get_pressed()

        # Movement
        players[0].move(keys, pygame.K_a, pygame.K_d, pygame.K_w)
        players[1].move(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)

        # Update players
        for p in players:
            p.update(
                placed_data["platforms"] + placed_data["walls"],
                placed_data["traps"],
                projectiles
            )

            if p.rect.colliderect(goal) and not p.finished:
                p.finished = True
                p.score += 1

        # SHOOTER LOGIC
        if time.time() - last_shot_time >= 1:
            last_shot_time = time.time()
            for shooter in placed_data["shooters"]:
                direction = -1  # left
                proj = Projectile(shooter.right, shooter.centery, direction)
                projectiles.append(proj)

        # Update projectiles
        for proj in projectiles[:]:
            proj.update()
            if proj.rect.right < 0 or proj.rect.left > WIDTH:
                projectiles.remove(proj)

        # DRAW everything
        for p in placed_data["platforms"]:
            pygame.draw.rect(WIN, BLACK, p)
        for w in placed_data["walls"]:
            pygame.draw.rect(WIN, BLACK, w)
        for t in placed_data["traps"]:
            pygame.draw.rect(WIN, RED, t)
        for s in placed_data["shooters"]:
            pygame.draw.rect(WIN, BLUE, s)
        for proj in projectiles:
            proj.draw()

        pygame.draw.rect(WIN, GREEN, goal)

        for p in players:
            p.draw()

        # Scoreboard
        score_text = FONT.render(
            f"{players[0].name}: {players[0].score}   |   {players[1].name}: {players[1].score}",
            True, BLACK
        )
        WIN.blit(score_text, (20, 20))

        pygame.display.update()

        # End round when all players are done
        if all(not p.alive or p.finished for p in players):
            pygame.time.delay(1000)
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return


# ---------------------------------------------------------
# MAIN GAME LOOP
# ---------------------------------------------------------
def main():
    # ALL placeable object types
    placeables = [
        ("platform", pygame.Rect(0, 0, 120, 25)),
        ("wall", pygame.Rect(0, 0, 30, 120)),
        ("wall", pygame.Rect(0, 0, 120, 30)),
        ("trap", pygame.Rect(0, 0, 40, 40)),
        ("trap_shooter", pygame.Rect(0, 0, 40, 40))
    ]

    # Stored objects
    placed_data = {
        "platforms": [pygame.Rect(0, HEIGHT - 40, WIDTH, 40)],
        "walls": [],
        "traps": [],
        "shooters": []
    }

    players = [
        Player(50, HEIGHT - 100, BLUE, "P1"),
        Player(100, HEIGHT - 100, GREEN, "P2")
    ]

    goal = pygame.Rect(WIDTH - 80, HEIGHT - 120, 60, 80)

    while True:
        # Win check
        for p in players:
            if p.score >= WINNING_SCORE:
                WIN.fill(WHITE)
                msg = FONT.render(f"{p.name} WINS!", True, BLACK)
                WIN.blit(msg, (WIDTH // 2 - 100, HEIGHT // 2))
                pygame.display.update()
                pygame.time.delay(3000)
                return

        # Reset players
        for p in players:
            p.rect.x, p.rect.y = 50, HEIGHT - 100
            p.vel_y = 0
            p.alive = True
            p.finished = False

        # BUILD phase
        if not build_phase(placeables, placed_data):
            break

        # RUN phase
        run_phase(players, placed_data, goal)


main()
