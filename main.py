#! /usr/bin/env python3

# Simple pygame program

# Import the pygame module
import pygame
import random

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

# Setup for sounds. Defaults are good.
pygame.mixer.init()

# Load and play background music
# Sound source: http://ccmixter.org/files/Apoxode/59262
# License: https://creativecommons.org/licenses/by/3.0/
pygame.mixer.music.load("Apoxode_-_Electric_1.mp3")
pygame.mixer.music.play(loops=-1)

# Load all sound files
# Sound sources: Jon Fincher
move_up_sound = pygame.mixer.Sound("Rising_putter.ogg")
move_down_sound = pygame.mixer.Sound("Falling_putter.ogg")
collision_sound = pygame.mixer.Sound("Collision.ogg")

# Initialize pygame
pygame.init()

# Define constants for the screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

max_score = 0
score = 0
tick = 0

# Define a Player object by extending pygame.sprite.Sprite
# The surface drawn on the screen is now an attribute of 'player'
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.num_frame = 4
        self.current_frame = 0
        self.load_image()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        )

    def load_image(self):
        self.surf = pygame.image.load(f'jet-{self.current_frame}.png').convert()
        self.current_frame = self.current_frame + 1
        if self.current_frame >= self.num_frame:
            self.current_frame = 0


    def move(self, dx, dy):
        cx = self.rect.centerx + dx
        cy = self.rect.centery + dy
        self.move_to((cx, cy))

    def move_to(self, center):
        self.rect.center = center

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT



    # Move the sprite based on user keypresses
    def update(self, pressed_keys):
        self.load_image()
        if pressed_keys[K_UP]:
            self.move(0, -5)
            move_up_sound.play()
        if pressed_keys[K_DOWN]:
            self.move(0, 5)
            move_down_sound.play()
        if pressed_keys[K_LEFT]:
            self.move(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.move(5, 0)


# Define the enemy object by extending pygame.sprite.Sprite
# The surface you draw on the screen is now an attribute of 'enemy'
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(5 + score, 20 + score)

    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


# Define the cloud object by extending pygame.sprite.Sprite
# Use an image for a better-looking sprite
class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super(Cloud, self).__init__()
        self.surf = pygame.image.load("cloud.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        # The starting position is randomly generated
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

    # Move the cloud based on a constant speed
    # Remove the cloud when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-5 - score, 0)
        if self.rect.right < 0:
            self.kill()


# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Jet Fight')

# Setup the clock for a decent framerate
clock = pygame.time.Clock()

# Create custom events for adding a new enemy and a cloud
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)
ADDCLOUD = pygame.USEREVENT + 2
pygame.time.set_timer(ADDCLOUD, 1000)

# Instantiate player. Right now, this is just a rectangle.
player = Player()

# Create groups to hold enemy sprites, cloud sprites, and all sprites
# - enemies is used for collision detection and position updates
# - clouds is used for position updates
# - all_sprites is used for rendering
enemies = pygame.sprite.Group()
clouds = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)


# Run until the user asks to quit
running = True
while running:
    # Look at every event in the queue
    for event in pygame.event.get():
        # Did the user hit a key?
        if event.type == KEYDOWN:
            # Was it the Escape key? If so, stop the loop.
            if event.key == K_ESCAPE:
                running = False

        # Did the user click the window close button? If so, stop the loop.
        elif event.type == QUIT:
            running = False

        # Add a new enemy?
        elif event.type == ADDENEMY:
            # Create the new enemy and add it to sprite groups
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

        # Add a new cloud?
        elif event.type == ADDCLOUD:
            # Create the new cloud and add it to sprite groups
            new_cloud = Cloud()
            clouds.add(new_cloud)
            all_sprites.add(new_cloud)

    # Fill the screen with black
    screen.fill((255, 255, 255))

    # Get all the keys currently pressed
    pressed_keys = pygame.key.get_pressed()

    # Update the player sprite based on user keypresses
    player.update(pressed_keys)

    # Update the position of enemies and clouds
    enemies.update()
    clouds.update()

    # Draw all sprites
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    # Check if any enemies have collided with the player
    if pygame.sprite.spritecollideany(player, enemies):
        # Stop any moving sounds and play the collision sound
        move_up_sound.stop()
        move_down_sound.stop()
        collision_sound.play()

        player.move_to((SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        score -= 5
        # If so, then remove the player and stop the loop
        if score < 0:
            score = 0
            player.kill()
            running = False

    tick += 1
    if tick % 30 == 0:
        score += 1
        if score > max_score:
            max_score = score

    font = pygame.font.SysFont("montserrat", 25)
    score_text = font.render(f'Score = {score}', True, (198,30,74))
    screen.blit(score_text, (10, 10))

    # Flip the display
    pygame.display.flip()

    # Ensure program maintains a rate of 30 frames per second
    clock.tick(30)

screen.fill((255, 255, 255))
font = pygame.font.SysFont("montserrat", 40)
text = font.render('Game Over', True, (198,30,74))
screen.blit(text, ((SCREEN_WIDTH - text.get_width())/2, (SCREEN_HEIGHT - text.get_height())/2))
max_score_text = font.render(f'Score: {max_score}', True, (198,30,74))
screen.blit(max_score_text, ((SCREEN_WIDTH - max_score_text.get_width())/2, (SCREEN_HEIGHT + text.get_height())/2 + 10))

pygame.display.flip()

pygame.event.clear()
running = True
while running:
    for event in pygame.event.get():
        # Did the user hit a key?
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            running = False

# All done! Stop and quit the mixer.
pygame.mixer.music.stop()
pygame.mixer.quit()


# Done! Time to quit.
pygame.quit()
