import pygame
import random
pygame.init()

WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FPS = 60

PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 15

FONT = pygame.font.Font(None, 50)
BIG_FONT = pygame.font.Font(None, 80)


# ------------------------------------------------------
#              MAKE RANDOM MIXED OBSTACLES
# ------------------------------------------------------
def make_obstacles():
    obstacles = []
    
    count = random.randint(1, 7)  # Random amount up to 7
    
    for _ in range(count):
        obstacle_type = random.choice(["vertical", "horizontal", "box"])
        
        if obstacle_type == "vertical":
            width = 20
            height = random.randint(80, 180)
        
        elif obstacle_type == "horizontal":
            width = random.randint(80, 180)
            height = 20
        
        else:
            size = random.randint(40, 80)
            width = size
            height = size
        
        x = random.randint(250, WIDTH - 250)
        y = random.randint(80, HEIGHT - 80)
        
        obstacles.append(pygame.Rect(x, y, width, height))
    
    return obstacles


# ------------------------------------------------------
#                         GAME LOOP
# ------------------------------------------------------
def game_loop(speed, random_mode=False):
    left_score = 0
    right_score = 0

    paddle_speed = 11   # <<--- FASTER PADDLES HERE

    ball_speed = speed

    left_paddle = pygame.Rect(20, HEIGHT//2 - 50, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(WIDTH - 30, HEIGHT//2 - 50, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH//2, HEIGHT//2, BALL_SIZE, BALL_SIZE)

    ball_vel_x = random.choice([-ball_speed, ball_speed])
    ball_vel_y = random.choice([-ball_speed, ball_speed])

    obstacles = make_obstacles() if random_mode else []

    clock = pygame.time.Clock()
    wait_timer = 0

    run = True
    while run:
        clock.tick(FPS)
        WIN.fill(BLACK)

        if wait_timer > 0:
            text = FONT.render(f"Get Ready! {wait_timer//FPS}", True, WHITE)
            WIN.blit(text, (WIDTH//2 - 100, HEIGHT//2 - 20))
            wait_timer -= 1
            pygame.display.update()
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # PADDLE MOVEMENT
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and left_paddle.top > 0:
            left_paddle.y -= paddle_speed
        if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
            left_paddle.y += paddle_speed
        if keys[pygame.K_UP] and right_paddle.top > 0:
            right_paddle.y -= paddle_speed
        if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
            right_paddle.y += paddle_speed

        # BALL MOVEMENT
        ball.x += ball_vel_x
        ball.y += ball_vel_y

        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_vel_y *= -1

        if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
            ball_vel_x *= -1.1
            ball_vel_y *= 1.1

        # OBSTACLE COLLISION
        if random_mode:
            for obs in obstacles:
                if ball.colliderect(obs):
                    if abs(ball.centerx - obs.centerx) > abs(ball.centery - obs.centery):
                        ball_vel_x *= -1
                    else:
                        ball_vel_y *= -1

        # SCORING
        if ball.left <= 0:
            right_score += 1
            ball.center = (WIDTH//2, HEIGHT//2)
            ball_vel_x = random.choice([-ball_speed, ball_speed])
            ball_vel_y = random.choice([-ball_speed, ball_speed])
            if random_mode:
                obstacles = make_obstacles()
            wait_timer = 3 * FPS

        if ball.right >= WIDTH:
            left_score += 1
            ball.center = (WIDTH//2, HEIGHT//2)
            ball_vel_x = random.choice([-ball_speed, ball_speed])
            ball_vel_y = random.choice([-ball_speed, ball_speed])
            if random_mode:
                obstacles = make_obstacles()
            wait_timer = 3 * FPS

        # DRAWING
        pygame.draw.rect(WIN, WHITE, left_paddle)
        pygame.draw.rect(WIN, WHITE, right_paddle)
        pygame.draw.ellipse(WIN, WHITE, ball)

        if random_mode:
            for obs in obstacles:
                pygame.draw.rect(WIN, WHITE, obs)

        score_text = FONT.render(f"{left_score}  |  {right_score}", True, WHITE)
        WIN.blit(score_text, (WIDTH//2 - 60, 20))

        pygame.display.update()

    pygame.quit()


# ------------------------------------------------------
#                    MAIN MENU
# ------------------------------------------------------
def menu():
    clock = pygame.time.Clock()

    while True:
        WIN.fill(BLACK)
        title = BIG_FONT.render("PONG MENU", True, WHITE)
        WIN.blit(title, (WIDTH//2 - 180, 80))

        easy = FONT.render("1 - Easy", True, WHITE)
        medium = FONT.render("2 - Medium", True, WHITE)
        hard = FONT.render("3 - Hard", True, WHITE)
        random_mode = FONT.render("4 - Random Mode", True, WHITE)
        quit_game = FONT.render("5 - Quit", True, WHITE)

        WIN.blit(easy, (WIDTH//2 - 100, 200))
        WIN.blit(medium, (WIDTH//2 - 100, 260))
        WIN.blit(hard, (WIDTH//2 - 100, 320))
        WIN.blit(random_mode, (WIDTH//2 - 100, 380))
        WIN.blit(quit_game, (WIDTH//2 - 100, 440))

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_loop(5)
                if event.key == pygame.K_2:
                    game_loop(7)
                if event.key == pygame.K_3:
                    game_loop(10)
                if event.key == pygame.K_4:
                    game_loop(7, random_mode=True)
                if event.key == pygame.K_5:
                    return


menu()

