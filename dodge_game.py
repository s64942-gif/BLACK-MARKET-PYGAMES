import pygame
import random
import sys
# Initialize pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dodge the Falling Blocks")
# Set up fonts
font = pygame.font.SysFont("arialblack", 40)
fontsmall = pygame.font.SysFont("arialblack", 20)
small_font = pygame.font.Font(None, 30)
#MENU ITEMS button first
def draw_button(text, x, y, width, height, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, width, height))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))

    text_surf = small_font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=((x + (width / 2)), (y + (height / 2))))
    screen.blit(text_surf, text_rect)
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def game_mode_easy():
    print("Loading Easy Mode!")
    # Your easy mode game loop and logic goes here
    # For demonstration, we'll just return to the menu after a delay
    pygame.time.delay(2000)
    main_menu()

def game_mode_hard():
    print("Loading Hard Mode!")
    # Your hard mode game loop and logic goes here
    pygame.time.delay(2000)
    main_menu()

def game_mode_EXTREME():
    print("Loading IMPOSSIBLE Mode!")
    # Your extreme mode game loop and logic goes here
    pygame.time.delay(2000)
    main_menu()

def quit_game():
    pygame.quit()
    sys.exit()

def reset_game():
    global player_x, player_y, score, block_speed, blocks, green_blocks, counter

    player_x = screen_width // 2 - player_width // 2
    player_y = screen_height - player_height - 10

    score = 5
    block_speed = 1
    counter = 0

    blocks = []
    green_blocks = []

def main_menu():
    menu_running = True
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

        screen.fill(BLACK)
        
        title_text = font.render("Select Game Mode", True, WHITE)
        title_rect = title_text.get_rect(center=(screen_width / 2, 100))
        screen.blit(title_text, title_rect)
        title_text = fontsmall.render("Dodge red blocks and collect green ones to win!", True, WHITE)
        title_rect = title_text.get_rect(center=(screen_width / 2, 350))
        screen.blit(title_text, title_rect)

        draw_button("Easy", 100, 250, 200, 80, GREEN, WHITE, game_loop)
        draw_button("Hard", 300, 250, 200, 80, RED, WHITE, game_mode_hard)
        draw_button("Extreme", 500, 250, 200, 80, PINK, WHITE, game_mode_EXTREME)
        draw_button("Quit", 300, 450, 200, 80, BLUE, WHITE, quit_game)
        
        pygame.display.update()

pygame.display.update()

pygame.time.wait(1000)  # Show game over screen for 2 seconds
# Set up colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
TEXT_COL = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
PINK = (170, 51, 106)
GOLD = (212, 175, 55)
#draw_text("Loading", font, TEXT_COL, 160, 250)
#pygame.display.update()
#pygame.time.wait(2000)
# Set up player and block properties
player_width = 40
player_height = 40
block_width = 50
block_height = 50
player_x = screen_width // 2 - player_width // 2
player_y = screen_height - player_height - 10
counter = 0
player_speed = 6
# Game variables
blocks = []
green_blocks = []
gold_blocks = []
block_speed = 1
score = 0
block_type = 0

# Game clock
clock = pygame.time.Clock()

# Function to display score
def display_score(score):
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

# Function to draw the player
def draw_player(x, y):
    pygame.draw.rect(screen, BLUE, (x, y, player_width, player_height))

# Function to create new falling blocks
def create_block():
    block_x = random.randint(0, screen_width - block_width)
    block_y = -block_height  # Start above the screen
    block_type = 1
    return [block_x, block_y, block_type]

def spawn_block():
    block_x = -block_height  # to the left of the screen 
    block_y = random.randint(0, screen_width - block_width)
    block_type = 2
    return [block_x, block_y, block_type]  
def Right_spawn_block():
    block_x = screen_width  # spawn just outside right edge
    block_y = random.randint(0, screen_height - block_height)
    block_type = 5
    return [block_x, block_y, block_type]
def create_blockgreen():
    block_x = random.randint(0, screen_width - block_width)
    block_y = -block_height  # Start above the screen
    block_type = 3
    return [block_x, block_y, block_type]
def spawn_blockgreen():
    block_y = random.randint(0, screen_width - block_width)
    block_x = -block_height  # Start above the screen
    block_type = 4
    return [block_x, block_y, block_type]
def spawn_blockgreen_left():
    block_x = screen_width  # spawn just outside right edge
    block_y = random.randint(0, screen_height - block_height)
    block_type = 6
    return [block_x, block_y, block_type]

# Main game loop and difficulties
def game_loop():
    global player_x, score, block_speed, player_y, block_height, counter
    draw_text("", font, TEXT_COL, 140, 320)
    draw_text("", font, TEXT_COL, 140, 370)
    pygame.display.update()
    pygame.time.wait(2000)
    running = True
    while running:
        screen.fill((0, 0, 0))  # Fill the scrwefieen with black
        display_score(score)  # Display the score
        player_speed = 6
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Get the keys pressed for player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d] and player_x < screen_width - player_width:
            player_x += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w] and player_y < screen_height - player_height:
            player_y -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s] and player_y < screen_height - player_height:
            player_y += player_speed

        # Create new blocks and move them down
        if random.randint(1, 50) == 1:  # Randomly create blocks, higher the range slower block spawn
            blocks.append(create_block())
            counter += 1
        #if random.randint(5, 100) == 5:  # Randomly create blocks, higher the range slower block spawn
        #    blocks.append(spawn_block())
        #   counter += 1
        if random.randint(3, 500) == 3:  # Randomly create blocks, higher the range slower block spawn but these are green
            green_blocks.append(create_blockgreen())
        if random.randint(2, 500) == 2:  # Randomly create blocks, higher the range slower block spawn safe blocks
            green_blocks.append(spawn_blockgreen())
        if random.randint(8, 3000) == 8:  # Randomly create blocks, higher the range slower block spawn safe blocks
            green_blocks.append(spawn_blockgreen_left())       
        # Move the blocks and check for collisions
        for block in blocks[:]:
            if block[2] == 1: #checking if its a create block
                block[1] += block_speed  # Move the block down
                if block[1] > screen_height:  # Remove blocks that fall off screen
                    blocks.remove(block)
                    score += 1  # Increase score for surviving
                if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                    running = False
                    # End game if collision occurs
            #else if spawn block
            #elif block[2] == 2: #check if spawn block
            #    block[0] += block_speed  # Move the block to right
            #    if block[0] > screen_width:  # Remove blocks that fall off right side screen
            #        blocks.remove(block)
            #        score += 2  # Increase score for surviving
            #    if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
            #        running = False  # End game if collision occurs
            # Draw the falling blocks
            pygame.draw.rect(screen, RED, (block[0], block[1], block_width, block_height))
                #if counter % 7 == 0:
                    # GREEN BLOCKS SPAWN
        for block in green_blocks[:]:
                        if block[2] == 3: #checking if its a create greenblock
                            block[1] += block_speed  # Move the greenblock down
                        if block[1] > screen_height:  # Remove greenblocks that fall off screen
                            green_blocks.remove(block)
                            score -= 0
                        if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                            score += 10  # Increase score for hitting green blocks
                            green_blocks.remove(block)
                    #else if spawn block
                    #    elif block[2] == 4: #check if spawn greenblock
                    #        block[0] += block_speed  # Move the green lock to right
                    #        if block[0] > screen_width:  # Remove greenblocks that fall off right side screen
                    #            green_blocks.remove(block)
                    #           score -= 0  # Increase score for surviving
                    #        if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                    #            score += 10  # Increase score for hitting green blocks
                                
            # Draw the falling blocks
                        pygame.draw.rect(screen, GREEN, (block[0], block[1], block_width, block_height))
        for block in green_blocks[:]:
                if block[2] == 6: #check if right spawn block
                        block[0] -= block_speed  # Move the block to right
                if  block[0] > screen_width:  # Remove blocks that fall off right side screen
                        green_blocks.remove(block)
                        score -= 0  # Increase score for surviving
                if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                        score += 20  # GIVE MASSIVE AMOUNT if collision occurs
                # Draw the falling blocks
                if block[2] == 6:
                    pygame.draw.rect(screen, GOLD, (block[0], block[1], block_width, block_height))
                else:
                    pygame.draw.rect(screen, GREEN, (block[0], block[1], block_width, block_height))
        # Draw the player
        draw_player(player_x, player_y)

        # Update the display
        pygame.display.update()

        # Increase the speed of the falling blocks over time
        if score > 20:
            block_speed =1
        if score > 50:
            block_speed = 3
        if score > 70:
            block_speed = 3
        if score > 100:
            block_speed = 4
        if score > 200:
            block_speed = 6
        if score > 300:

            game_over_text = font.render("YOU WON", True, WHITE)
            screen.fill((0, 0, 0))
            screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - 50))
            pygame.display.update()
            pygame.time.wait(2000)  # Show game over screen for 2 seconds
            reset_game()
            main_menu()
            return
        clock.tick(60)  # Limit the frame rate to 60 FPS

    # Game over screen
    game_over_text = font.render("GAME OVER", True, WHITE)
    final_score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.fill((0, 0, 0))
    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - 50))
    screen.blit(final_score_text, (screen_width // 2 - final_score_text.get_width() // 2, screen_height // 2 + 10))
    pygame.display.update()
    pygame.time.wait(2000)  # Show game over screen for 2 seconds
    reset_game()
    main_menu()
    return
def game_mode_hard():
    global player_x, score, block_speed, player_y, block_height, counter
    draw_text("", font, TEXT_COL, 140, 320)
    draw_text("", font, TEXT_COL, 140, 370)
    pygame.display.update()
    pygame.time.wait(2000)
    running = True
    while running:
        screen.fill((0, 0, 0))  # Fill the scrwefieen with black
        display_score(score)  # Display the score
        player_speed = 6
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Get the keys pressed for player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d] and player_x < screen_width - player_width:
            player_x += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w] and player_y < screen_height - player_height:
            player_y -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s] and player_y < screen_height - player_height:
            player_y += player_speed

        # Create new blocks and move them down
        if random.randint(1, 80) == 1:  # Randomly create blocks, higher the range slower block spawn
            blocks.append(create_block())
            counter += 1
        if random.randint(5, 80) == 5:  # Randomly create blocks, higher the range slower block spawn
            blocks.append(spawn_block())
            counter += 1
        if random.randint(3, 500) == 3:  # Randomly create blocks, higher the range slower block spawn but these are green
            green_blocks.append(create_blockgreen())
        if random.randint(2, 500) == 2:  # Randomly create blocks, higher the range slower block spawn safe blocks
            green_blocks.append(spawn_blockgreen())
        if random.randint(8, 3000) == 8:  # Randomly create blocks, higher the range slower block spawn safe blocks
            green_blocks.append(spawn_blockgreen_left())   
        # Move the blocks and check for collisions
        for block in blocks[:]:
            if block[2] == 1: #checking if its a create block
                block[1] += block_speed  # Move the block down
                if block[1] > screen_height:  # Remove blocks that fall off screen
                    blocks.remove(block)
                    score += 1  # Increase score for surviving
                if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                    running = False  # End game if collision occurs
            #else if spawn block
            elif block[2] == 2: #check if spawn block
                block[0] += block_speed  # Move the block to right
                if block[0] > screen_width:  # Remove blocks that fall off right side screen
                    blocks.remove(block)
                    score += 1  # Increase score for surviving
                if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                    running = False  # End game if collision occurs
            # Draw the falling blocks
            pygame.draw.rect(screen, RED, (block[0], block[1], block_width, block_height))
                #if counter % 7 == 0:
                    # GREEN BLOCKS SPAWN
        for block in green_blocks[:]:
                        if block[2] == 3: #checking if its a create greenblock
                            block[1] += block_speed  # Move the greenblock down
                        if block[1] > screen_height:  # Remove greenblocks that fall off screen
                            green_blocks.remove(block)
                            score -= 5
                        if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                            score += 10  # Increase score for hitting green blocks
                            green_blocks.remove(block)
                    #else if spawn block
                        elif block[2] == 4: #check if spawn greenblock
                            block[0] += block_speed  # Move the greenblock to right
                            if block[0] > screen_width:  # Remove greenblocks that fall off right side screen
                                green_blocks.remove(block)
                                score -= 5  # Increase score for surviving
                            if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                                score += 10  # Increase score for hitting green blocks
                                
            # Draw the falling blocks
                        pygame.draw.rect(screen, GREEN, (block[0], block[1], block_width, block_height))
        for block in green_blocks[:]:
                if block[2] == 6: #check if right spawn block
                        block[0] -= block_speed  # Move the block to right
                if  block[0] > screen_width:  # Remove blocks that fall off right side screen
                        green_blocks.remove(block)
                        score -= 0  # Increase score for surviving
                if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                        score += 20  # GIVE MASSIVE AMOUNT if collision occurs
                # Draw the falling blocks
                if block[2] == 6:
                    pygame.draw.rect(screen, GOLD, (block[0], block[1], block_width, block_height))
                else:
                    pygame.draw.rect(screen, GREEN, (block[0], block[1], block_width, block_height))
        # Draw the player
        draw_player(player_x, player_y)

        # Update the display
        pygame.display.update()

        # Increase the speed of the falling blocks over time
        if score < -30:
            game_over_text = font.render("YOU LOST, STAY IN THE BOUNDARY", True, WHITE)
            screen.fill((0, 0, 0))
            screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - 50))
            pygame.display.update()
            pygame.time.wait(2000)  # Show game over screen for 2 seconds
            reset_game()
            main_menu()
            return
        if score > 20:
            block_speed =1
        if score > 50:
            block_speed = 3
        if score > 70:
            block_speed = 4
        if score > 100:
            block_speed = 6
        if score > 200:
            block_speed = 10
        if score > 300:
            game_over_text = font.render("YOU WON", True, WHITE)
            screen.fill((0, 0, 0))
            screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - 50))
            pygame.display.update()
            pygame.time.wait(2000)  # Show game over screen for 2 seconds
            reset_game()
            main_menu()
            return
        clock.tick(60)  # Limit the frame rate to 60 FPS

    # Game over screen
    game_over_text = font.render("GAME OVER", True, WHITE)
    final_score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.fill((0, 0, 0))
    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - 50))
    screen.blit(final_score_text, (screen_width // 2 - final_score_text.get_width() // 2, screen_height // 2 + 10))
    pygame.display.update()
    pygame.time.wait(2000)  # Show game over screen for 2 seconds
    reset_game()
    main_menu()
    return
def game_mode_EXTREME():
    global player_x, score, block_speed, player_y, block_height, counter
    draw_text("", font, TEXT_COL, 140, 320)
    draw_text("", font, TEXT_COL, 140, 370)
    pygame.display.update()
    pygame.time.wait(2000)
    running = True
    while running:
        screen.fill((0, 0, 0))  # Fill the scrwefieen with black
        display_score(score)  # Display the score
        player_speed = 8
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Get the keys pressed for player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d] and player_x < screen_width - player_width:
            player_x += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w] and player_y < screen_height - player_height:
            player_y -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s] and player_y < screen_height - player_height:
            player_y += player_speed

        # Create new blocks and move them down
        if random.randint(1, 50) == 1:  # Randomly create blocks, higher the range slower block spawn
            blocks.append(create_block())
            counter += 1
        if random.randint(5, 60) == 5:  # Randomly create blocks, higher the range slower block spawn
            blocks.append(spawn_block())
            counter += 1
        if random.randint(6, 60) == 6:  # Randomly create blocks, higher the range slower block spawn
            blocks.append(Right_spawn_block())
            counter += 1    
        if random.randint(3, 400) == 3:  # Randomly create blocks, higher the range slower block spawn but these are green
            green_blocks.append(create_blockgreen())
        if random.randint(2, 500) == 2:  # Randomly create blocks, higher the range slower block spawn safe blocks
            green_blocks.append(spawn_blockgreen())
        if random.randint(8, 2000) == 8:  # Randomly create blocks, higher the range slower block spawn safe blocks
            green_blocks.append(spawn_blockgreen_left())  
        # Move the blocks and check for collisions  
        # Move the blocks and check for collisions
        for block in blocks[:]:
            if block[2] == 1: #checking if its a create block
                block[1] += block_speed  # Move the block down
                if block[1] > screen_height:  # Remove blocks that fall off screen
                    blocks.remove(block)
                    score += 0  # Increase score for surviving
                if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                    running = False  # End game if collision occurs
            #else if spawn block
            elif block[2] == 2: #check if spawn block
                block[0] += block_speed  # Move the block to right
                if block[0] > screen_width:  # Remove blocks that fall off right side screen
                    blocks.remove(block)
                    score += 1  # Increase score for surviving
                if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                    running = False  # End game if collision occurs
            #else if right spawn block
            elif block[2] == 5: #check if right spawn block
                block[0] -= block_speed  # Move the block to right
                if block[0] > screen_width:  # Remove blocks that fall off right side screen
                    blocks.remove(block)
                    score += 0  # Increase score for surviving
                if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                    running = False  # End game if collision occurs
            # Draw the falling blocks
            pygame.draw.rect(screen, RED, (block[0], block[1], block_width, block_height))
                #if counter % 7 == 0:
                    # GREEN BLOCKS SPAWN
        for block in green_blocks[:]:
                        if block[2] == 3: #checking if its a create greenblock
                            block[1] += block_speed  # Move the greenblock down
                        if block[1] > screen_height:  # Remove greenblocks that fall off screen
                            green_blocks.remove(block)
                            score -= 5
                        if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                            score += 5  # Increase score for hitting green blocks
                            green_blocks.remove(block)
                    #else if spawn block
                        elif block[2] == 4: #check if spawn greenblock
                            block[0] += block_speed  # Move the greenblock to right
                            if block[0] > screen_width:  # Remove greenblocks that fall off right side screen
                                green_blocks.remove(block)
                                score -= 5  # Increase score for surviving
                            if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                                score += 5  # Increase score for hitting green blocks     
                    # Draw the falling blocks
                            pygame.draw.rect(screen, GREEN, (block[0], block[1], block_width, block_height))
        for block in green_blocks[:]:
                if block[2] == 6: #check if right spawn block
                        block[0] -= block_speed  # Move the block to right
                if  block[0] > screen_width:  # Remove blocks that fall off right side screen
                        green_blocks.remove(block)
                        score -= 0  # Increase score for surviving
                if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(pygame.Rect(block[0], block[1], block_width, block_height)):
                        score += 20  # GIVE MASSIVE AMOUNT if collision occurs
                # Draw the falling blocks
                if block[2] == 6:
                    pygame.draw.rect(screen, GOLD, (block[0], block[1], block_width, block_height))
                else:
                    pygame.draw.rect(screen, GREEN, (block[0], block[1], block_width, block_height))
        # Draw the player
        draw_player(player_x, player_y)

        # Update the display
        pygame.display.update()

        # Increase the speed of the falling blocks over time
        if score < -10:
            game_over_text = font.render("YOU LOST, STAY IN THE BOUNDARY", True, WHITE)
            screen.fill((0, 0, 0))
            screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - 50))
            pygame.display.update()
            pygame.time.wait(2000)  # Show game over screen for 2 seconds
            reset_game()
            main_menu()
            return
        if score > 0:
            block_speed =1
        if score > 50:
            block_speed = 5
        if score > 70:
            block_speed = 10
        if score > 100:
            block_speed = 15
        if score > 200:
            block_speed = 20
        if score > 300:
            game_over_text = font.render("YOU WON", True, WHITE)
            screen.fill((0, 0, 0))
            screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - 50))
            pygame.display.update()
            pygame.time.wait(2000)  # Show game over screen for 2 seconds
            reset_game()
            main_menu()
            return
        clock.tick(60)  # Limit the frame rate to 60 FPS
    # Game over screen
    game_over_text = font.render("GAME OVER", True, WHITE)
    final_score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.fill((0, 0, 0))
    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - 50))
    screen.blit(final_score_text, (screen_width // 2 - final_score_text.get_width() // 2, screen_height // 2 + 10))
    pygame.display.update()
    pygame.time.wait(2000)  # Show game over screen for 2 seconds
    reset_game()
    main_menu()
    return
# Run the game
main_menu()