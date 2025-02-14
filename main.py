import pgzrun
from pygame import Rect
import random

# Constants
WIDTH = 800
HEIGHT = 600

# Game state variables
game_state = "menu"  # "menu", "playing", or "won"
music_on = True

# Game objects
hero = None
enemies = []
menu_buttons = []
enemies_jumped = 0

def draw_placeholder_sprite(sprite_name, center):
    """
    Draws a placeholder sprite using simple shapes and text.
    The sprite appearance changes based on its name.
    """
    if sprite_name.startswith("hero"):
        screen.draw.filled_circle(center, 25, "blue")
        screen.draw.text(sprite_name, center=center, fontsize=12, color="white")
    elif sprite_name.startswith("enemy"):
        # Draw a red square for enemy sprites.
        rect = Rect(center[0] - 25, center[1] - 25, 50, 50)
        screen.draw.filled_rect(rect, "red")
        screen.draw.text(sprite_name, center=center, fontsize=12, color="white")
    else:
        # Default placeholder if the name is unrecognized.
        rect = Rect(center[0] - 25, center[1] - 25, 50, 50)
        screen.draw.filled_rect(rect, "gray")
        screen.draw.text("sprite", center=center, fontsize=12, color="white")

class Button:
    """A clickable button for the menu."""
    def __init__(self, rect, text, callback):
        self.rect = rect
        self.text = text
        self.callback = callback

    def draw(self):
        screen.draw.filled_rect(self.rect, 'lightblue')
        screen.draw.rect(self.rect, 'white')
        screen.draw.text(self.text, center=self.rect.center, fontsize=30, color='black')

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()

class Character:
    """
    Base class for animated characters.
    Instead of loading image files, this version uses placeholder drawing.
    """
    def __init__(self, images, pos):
        self.images = images  # List of image names (used for animation)
        self.pos = list(pos)  # [x, y]
        self.frame_index = 0
        self.frame_counter = 0
        self.image = self.images[self.frame_index]
        self.width = 50
        self.height = 50
        self.rect = Rect(self.pos[0] - self.width // 2,
                         self.pos[1] - self.height // 2,
                         self.width, self.height)
        self.vx = 0
        self.vy = 0

    def update_animation(self):
        """Cycle through images to animate the sprite."""
        self.frame_counter += 1
        if self.frame_counter >= 10:  # Change frame every 10 updates
            self.frame_index = (self.frame_index + 1) % len(self.images)
            self.image = self.images[self.frame_index]
            self.frame_counter = 0

    def update_rect(self):
        """Update the collision rectangle to the current position."""
        self.rect.x = self.pos[0] - self.width // 2
        self.rect.y = self.pos[1] - self.height // 2

    def draw(self):
        """Draw the animated sprite at its current position."""
        screen.blit(self.image, self.rect.topleft)

class Hero(Character):
    """Hero class: controlled by the player."""
    def __init__(self, pos):
        images = ['l1.png', 'l2.png', 'r1.png', 'r2.png']  # List of hero images
        super().__init__(images, pos)
        self.speed = 3
        self.jump_strength = -15
        self.on_ground = False

    def update(self):
        # Horizontal movement via left/right arrow keys.
        if keyboard.left:
            self.vx = -self.speed
        elif keyboard.right:
            self.vx = self.speed
        else:
            self.vx = 0

        # Jumping with the up arrow key (only when on the ground).
        if keyboard.up and self.on_ground:
            self.vy = self.jump_strength
            self.on_ground = False
            # Play jump sound (if available) when music is enabled.
            if music_on:
                try:
                    sounds.jump.play()
                except Exception:
                    pass  # If sound files are missing, ignore the error.

        # Apply gravity.
        self.vy += 0.5

        # Update position.
        self.pos[0] += self.vx
        self.pos[1] += self.vy

        # Simple ground collision.
        ground_level = 500
        if self.pos[1] >= ground_level:
            self.pos[1] = ground_level
            self.vy = 0
            self.on_ground = True

        self.update_rect()
        self.update_animation()

class Enemy(Character):
    """Enemy class: moves back and forth within its territory."""
    def __init__(self, pos, left_bound, right_bound, number):
        images = [f'enemy{number}_1.png', f'enemy{number}_2.png']  # List of enemy images
        super().__init__(images, pos)
        self.speed = 2
        self.direction = 1  # 1 = moving right, -1 = moving left
        self.left_bound = left_bound
        self.right_bound = right_bound

    def update(self):
        # Patrol movement: move horizontally and reverse direction at bounds.
        self.vx = self.speed * self.direction
        self.pos[0] += self.vx

        if self.pos[0] < self.left_bound:
            self.pos[0] = self.left_bound
            self.direction = 1
        elif self.pos[0] > self.right_bound:
            self.pos[0] = self.right_bound
            self.direction = -1

        self.update_rect()
        self.update_animation()

def start_game():
    """Callback to start the game (called from the main menu)."""
    global game_state, hero, enemies, score, hero_health, enemies_jumped
    game_state = "playing"
    score = 0
    hero_health = 3
    enemies_jumped = 0
    # Initialize the hero at a starting position.
    hero = Hero([100, 500])
    # Create initial enemies.
    enemies.clear()
    for i in range(3):
        spawn_enemy()

def toggle_music():
    """Toggle background music and sound effects on/off."""
    global music_on
    music_on = not music_on
    if music_on:
        play_background_music()
    else:
        music.stop()

def play_background_music():
    """Play background music if music is enabled."""
    try:
        music.play('background')
    except Exception as e:
        print(f"Error playing background music: {e}")

def exit_game():
    """Exit the game."""
    exit()

def init_menu():
    """Initialize menu buttons with positions and callbacks."""
    global menu_buttons
    start_rect = Rect((WIDTH // 2 - 100, 200), (200, 50))
    music_rect = Rect((WIDTH // 2 - 100, 300), (200, 50))
    exit_rect = Rect((WIDTH // 2 - 100, 400), (200, 50))
    menu_buttons = [
        Button(start_rect, "Start Game", start_game),
        Button(music_rect, "Music: On/Off", toggle_music),
        Button(exit_rect, "Exit", exit_game)
    ]

def spawn_enemy():
    """Spawn a new enemy at a random position."""
    x = random.randint(300, WIDTH - 100)
    enemy = Enemy([x, 500], x - 50, x + 50, random.randint(1, 3))
    enemies.append(enemy)

# Call init_menu once at startup.
init_menu()

def update():
    """Called automatically by Pygame Zero every frame."""
    global game_state, hero, enemies, enemies_jumped
    if game_state == "playing":
        hero.update()
        for enemy in enemies:
            enemy.update()

        # Check for collisions between hero and enemies.
        buffer_distance = -15  # Adjust this value to change the hitting distance
        for enemy in enemies:
            if hero.rect.inflate(buffer_distance, buffer_distance).colliderect(enemy.rect):
                try:
                    sounds.hit.play()  # Play a collision sound if available.
                except Exception:
                    pass
                start_game()  # Restart game on hit.

        # Check if the hero has jumped over an enemy.
        for enemy in enemies:
            if hero.pos[0] > enemy.pos[0] and not hasattr(enemy, 'jumped'):
                enemies_jumped += 1
                enemy.jumped = True

        # Spawn new enemies periodically.
        if len(enemies) < 3:
            spawn_enemy()

        # Check if the hero has reached the end of the screen.
        if hero.pos[0] > WIDTH:
            game_state = "won"
            try:
                sounds.win.play()  # Play win sound if available.
            except Exception:
                pass

def draw():
    """Called automatically by Pygame Zero to redraw the screen."""
    screen.clear()
    if game_state == "menu":
        screen.fill("darkblue")
        screen.draw.text("Main Menu", center=(WIDTH // 2, 100), fontsize=60, color="white")
        for button in menu_buttons:
            button.draw()
    elif game_state == "playing":
        # Draw a simple background and ground for the platformer.
        screen.fill("skyblue")
        screen.draw.filled_rect(Rect((0, 500), (WIDTH, 100)), "green")
        hero.draw()
        for enemy in enemies:
            enemy.draw()
        # Draw the enemies jumped counter.
        screen.draw.text(f"Enemies Jumped: {enemies_jumped}", topleft=(10, 10), fontsize=30, color="white")
    elif game_state == "won":
        screen.fill("black")
        screen.draw.text("You Won!", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="white")
        screen.draw.text(f"Enemies Jumped: {enemies_jumped}", center=(WIDTH // 2, HEIGHT // 2 + 60), fontsize=30, color="white")

def on_mouse_down(pos):
    """Handle mouse clicks for the main menu buttons."""
    if game_state == "menu":
        for button in menu_buttons:
            button.check_click(pos)

# Play background music when the game starts
play_background_music()

# Start the game via pgzrun
pgzrun.go()