import sys

try:
    import pygame
except ImportError:
    print("Pygame is not installed. Attempting to install Pygame...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        import pygame
        print("Pygame installed successfully.")
    except Exception as e:
        print(f"Error installing Pygame: {e}")
        print("Please install Pygame manually using 'pip install pygame'.")
        sys.exit()

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "My Pygame Game"

# Colors
LIGHT_BLUE = (173, 216, 230)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)

# Camera and scroll threshold
camera_x = 0
SCROLL_THRESHOLD = 200 # Pixels from edge before camera moves

# Player class
class Player:
    def __init__(self, x, y, width, height, color, platforms):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.vel_y = 0
        self.jump_strength = -15
        self.gravity = 1
        self.is_grounded = True # Assume player starts on the ground
        self.platforms = platforms

    def move(self, dx):
        # Horizontal movement and collision
        self.rect.x += dx
        # Platform collision for horizontal movement
        for platform in self.platforms:
            # Create a platform rect adjusted for camera for collision detection
            # This is important if platforms themselves don't move relative to the world
            # but the player's rect.x is world coordinate
            if self.rect.colliderect(platform):
                if dx > 0: # Moving right
                    self.rect.right = platform.left
                elif dx < 0: # Moving left
                    self.rect.left = platform.right

    def jump(self):
        if self.is_grounded:
            self.vel_y = self.jump_strength
            self.is_grounded = False

    def update(self):
        self.is_grounded = False # Assume not grounded until proven otherwise

        # Apply gravity
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # Vertical platform collision
        for platform in self.platforms:
            if self.rect.colliderect(platform) and self.vel_y > 0:
                if self.rect.bottom - self.vel_y <= platform.top + 1:
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.is_grounded = True
                    break

        # Prevent falling through the bottom of the screen (acts as ground)
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
            self.is_grounded = True

    def draw(self, surface, camera_x_offset):
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_x_offset
        pygame.draw.rect(surface, self.color, draw_rect)

# Define platforms
platforms = [
    pygame.Rect(100, SCREEN_HEIGHT - 100, 200, 20), # Platform 1
    pygame.Rect(400, SCREEN_HEIGHT - 200, 150, 20), # Platform 2
    pygame.Rect(50, SCREEN_HEIGHT - 350, 100, 20)   # Platform 3 (higher)
]

# Create player instance
player_width = 50
player_height = 50
player_x = (SCREEN_WIDTH - player_width) // 2
# Initial y position so the player starts on the "ground" or the lowest part of the screen.
player_y = SCREEN_HEIGHT - player_height
player_color = (255, 0, 0) # Red
player = Player(player_x, player_y, player_width, player_height, player_color, platforms)

# Game loop
running = True
clock = pygame.time.Clock() # To control frame rate

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()

    # Handle continuous key presses for movement
    keys = pygame.key.get_pressed()
    player_speed = 5
    if keys[pygame.K_LEFT]:
        player.move(-player_speed)
    if keys[pygame.K_RIGHT]:
        player.move(player_speed)

    # Camera scrolling logic
    # If player is near the right edge
    if player.rect.right > SCREEN_WIDTH - SCROLL_THRESHOLD:
        diff = player.rect.right - (SCREEN_WIDTH - SCROLL_THRESHOLD)
        camera_x += diff
        player.rect.x -= diff # Adjust player's world position to keep them at the threshold on screen
    # If player is near the left edge
    elif player.rect.left < SCROLL_THRESHOLD:
        diff = SCROLL_THRESHOLD - player.rect.left
        camera_x -= diff
        player.rect.x += diff # Adjust player's world position

    # Update game state (like gravity and vertical collisions)
    player.update() # Player's rect.x is already world coordinate

    # Drawing
    screen.fill(LIGHT_BLUE)
    for platform in platforms: # Draw platforms
        draw_platform_rect = platform.copy()
        draw_platform_rect.x -= camera_x
        pygame.draw.rect(screen, GREEN, draw_platform_rect)
    player.draw(screen, camera_x)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60) # Aim for 60 FPS

# Quit Pygame
pygame.quit()
sys.exit()
