import pygame
import random
import time
import webbrowser
import os
import sys

# Initialize Pygame
pygame.init()

# Initialize the mixer module
pygame.mixer.init(buffer=8192)
pygame.mixer.music.set_volume(0.5)

# Set up some constants
WIDTH = 1280
HEIGHT = 1024
GRAVITY_MAGNITUDE = 1   # Gravitation magnitude
GRAVITY_ACC = GRAVITY_MAGNITUDE / (HEIGHT // 100)  # Gravitational acceleration
BALL_SPEED = 5
BALL_SIZE = 32
MENU, PLAYING, GAME_OVER = 0, 1, 2

# Set up some variables
clock = pygame.time.Clock()
paddle_width = 300
paddle_height = 25
fps = 120
game_state = PLAYING
running = True
shades_y = -300
exit_delay = -1

# Create the window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooting Star")
SCORE_FONT = pygame.font.SysFont("Arial", 24)

# Support loading resources from working directory or pyinstaller bundled exe
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller. """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Load the images
background_image = pygame.image.load(resource_path("background.webp"))
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
ball_image = pygame.image.load(resource_path("star.png"))
ball_image = pygame.transform.scale(ball_image, (BALL_SIZE, BALL_SIZE))
paddle_image = pygame.image.load(resource_path("wand.png"))
paddle_image = pygame.transform.scale(paddle_image, (paddle_width, paddle_height))
shades = pygame.image.load(resource_path("sunglasses.png"))
shades = pygame.transform.scale(shades, (WIDTH // 4, 200))
winning_image = pygame.image.load(resource_path("winning.png"))
winning_image = pygame.transform.scale(winning_image, (WIDTH, HEIGHT))
sparkle_image = pygame.image.load(resource_path("sparkle.png"))
sparkle_image = pygame.transform.scale(sparkle_image, (ball_image.get_width() // 2, ball_image.get_height() // 2))

# Load and play the music
pygame.mixer.music.load(resource_path('music.mp3'))
pygame.mixer.music.play(-1)  # The -1 makes the music loop indefinitely

# Load sounds
zero_score_sound = pygame.mixer.Sound(resource_path("you-suck-ass.wav"))
low_score_sound = pygame.mixer.Sound(resource_path("you-suck.wav"))
mid_score_sound = pygame.mixer.Sound(resource_path("not-bad.wav"))
good_score_sound = pygame.mixer.Sound(resource_path("pretty-good.wav"))
winning_score_sound = pygame.mixer.Sound(resource_path("rockstar-from-mars.wav"))

# List to store sparkles
sparkles = []

# Set up the player and ball objects
player_x = WIDTH // 2 - 50
player_y = HEIGHT - 50
ball_x = random.randint(0, WIDTH)
ball_y = random.randint(0, HEIGHT // 3)

player_speed = 10

ball_speed_y = BALL_SPEED
ball_speed_x = random.randint(-2 * BALL_SPEED, 2 * BALL_SPEED)
# Ensure ball doesn't drop too vertically
if ball_speed_x < 0:
    ball_speed_x = min(ball_speed_x, -BALL_SPEED)
else:
    ball_speed_x = max(ball_speed_x, BALL_SPEED)

score = 0
ran_once = False

def reset_ball():
    global ball_x, ball_y, ball_speed_y
    ball_x = random.randint(BALL_SIZE, WIDTH - BALL_SIZE)
    ball_y = random.randint(BALL_SIZE, HEIGHT // 3)
    ball_speed_y = BALL_SPEED
reset_ball()

def run_end_game():
    global running, score, shades_y, ran_once, shades, winning_image, fps, exit_delay
    global zero_score_sound, low_score_sound, mid_score_sound, good_score_sound, winning_score_sound

    shades_x        = 300
    shades_y_max    = 190

    if not ran_once:
        fps = 120
        pygame.mixer.music.stop()

    winning = False
    if score < 5:
        message = "Wow, you really suck ass!"
        if not ran_once:
            zero_score_sound.play()
    elif score < 20:
        message = "You suck!"
        if not ran_once:
            low_score_sound.play()
    elif score < 30:
        if not ran_once:
            mid_score_sound.play()
        message = "Not bad."
    elif score < 50:
        if not ran_once:
            good_score_sound.play()
        message = "Pretty good!"
    else:
        if not ran_once:
            winning_score_sound.play()
        message = ""
        window.blit(winning_image, (0, 0))
        winning = True
    if message:
        text = SCORE_FONT.render(message, True, (255, 255, 255))
        x = WIDTH // 2 - text.get_width() // 2
        y = HEIGHT // 2 - text.get_height() // 2
        window.blit(text, (x, y))
        pygame.display.flip()
        if not ran_once:
            exit_delay = fps * 3
    if winning:
        if not ran_once:
            webbrowser.open("https://www.youtube.com/watch?v=9QS0q3mGPGg")
            exit_delay = fps * 120
        window.blit(shades, (shades_x, shades_y))
        shades_y += 1
        shades_y = min(shades_y, shades_y_max)
    if exit_delay > -1:
        if exit_delay == 0:
            running = False
        else:
            exit_delay -= 1

    pygame.display.flip()
    ran_once = True

def run_playing():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, paddle_image, player_x, score, paddle_width, paddle_height, fps, game_state
    global sparkles

    # Check for left boundary collision
    if ball_x <= BALL_SIZE:
        ball_speed_x = -ball_speed_x
    
    # Check for right boundary collision
    if ball_x >= WIDTH - BALL_SIZE:
        ball_speed_x = -ball_speed_x

    # Check if ball crosses the bottom boundary
    if ball_y > HEIGHT - 30:
        game_state = GAME_OVER

    # Apply gravity
    ball_acceleration_y = GRAVITY_ACC

    # Update Y position with acceleration
    ball_speed_y += ball_acceleration_y
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Add a new sparkle at the center of the ball's position
    center_x = ball_x + BALL_SIZE // 2 - BALL_SIZE // 4
    center_y = ball_y + BALL_SIZE // 2 - BALL_SIZE // 4
    variation = 10
    sparkles.append((random.gauss(center_x, 5), random.gauss(center_y, 5)))

    # Limit the number of sparkles
    if len(sparkles) > 20:
        sparkles.pop(0)

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    elif keys[pygame.K_RIGHT] and player_x < WIDTH - paddle_width:
        player_x += player_speed
    
    # Clear the window
    window.fill((0, 0, 0))

    # Draw the background image
    window.blit(background_image, (0, 0))

    # Draw the sparkles
    for sparkle in sparkles:
        window.blit(sparkle_image, sparkle)

    # Draw the player and ball
    window.blit(paddle_image, (player_x, player_y))
    window.blit(ball_image, (ball_x, ball_y))

    # Show the score
    score_text = SCORE_FONT.render(str(score), True, (255, 255, 255))
    window.blit(score_text, (10, HEIGHT - 30))

    # Define a rectangle for the paddle
    paddle_rect = pygame.Rect(player_x, player_y, paddle_width, paddle_height)
    ball_rect = pygame.Rect(ball_x - BALL_SIZE, ball_y - BALL_SIZE, BALL_SIZE * 2, BALL_SIZE * 2)

    # Check for collision between the ball and the paddle
    if paddle_rect.colliderect(ball_rect):
        score += 1
        # Ensure the ball doesn't get stuck in the paddle
        if ball_speed_y > 0:  # Ball moving down
            ball_y = player_y - BALL_SIZE * 2
        else:  # Ball moving up
            ball_y = player_y + 10
        # Make the ball bounce vertically
        ball_speed_y *= -1
        # Optionally add a slight random variation to the horizontal speed to vary the bounce angle
        ball_speed_x *= random.uniform(0.80, 1.20)
        # Slightly reduce y speed
        ball_speed_y *= 0.98
        # Make the game get harder over time
        paddle_width *= 0.98
        paddle_width = max(paddle_width, 60)
        paddle_height *= 0.98
        paddle_height = max(paddle_height, 15)
        paddle_image = pygame.transform.scale(paddle_image, (paddle_width, paddle_height))
        fps *= 1.012


# Main game loop
while running:
    clock.tick(fps)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if game_state == PLAYING:
        run_playing()
    elif game_state == GAME_OVER:
        run_end_game()

    # Update the window
    pygame.display.flip()

# Quit Pygame
pygame.quit()