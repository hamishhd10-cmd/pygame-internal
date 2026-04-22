"""
Flappy Bird Game

A simple Flappy Bird clone implemented in Pygame.
The player controls a bird that must navigate through pipes without colliding.
Features include skin customization, scoring, and high score tracking.

Author: Hamish HD
"""

import pygame
import random
import sys
import os
import json

# Initialize Pygame modules
pygame.init()

# Constants for file paths and game settings
LEADERBOARD_FILE = "leaderboard.txt"

# Screen dimensions
size = width, height = 600, 800
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Flappy Bird - Background Screen")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Game environment constants
ground_y = int(height * 0.75)  # Y position of the ground
pipe_width = 80  # Width of pipes
pipe_gap = 200  # Gap between top and bottom pipes
pipe_speed = 3  # Speed at which pipes move left
pipe_spawn_interval = 90  # Frames between pipe spawns
pipe_spawn_timer = 0  # Timer for pipe spawning
pipes = []  # List of active pipes
score = 0  # Current game score
leaderboard = [0, 0, 0, 0, 0]  # Top 5 scores
is_night = False  # Flag for night mode (changes background)
frame_counter = 0  # Counter for animation frames

# Bird skin options: list of (color, name) tuples
bird_skins = [
    ((255, 215, 0), "Gold"),
    ((180, 180, 255), "Blue"),
    ((255, 105, 180), "Pink"),
    ((173, 255, 47), "Lime"),
    ((255, 140, 0), "Orange"),
    ((128, 0, 128), "Purple"),
]
# Current skin being previewed
current_skin = {"color": bird_skins[0][0], "name": bird_skins[0][1]}
# Selected skin for gameplay
selected_skin = {"color": bird_skins[0][0], "name": bird_skins[0][1]}
skin_message = ""  # Message for skin changes
skin_message_timer = 0  # Timer for displaying skin messages
# Button rectangles for customization
customize_button_rect = pygame.Rect(width - 220, 20, 200, 50)
select_button_rect = pygame.Rect(width - 220, 80, 200, 50)

# Skin selection grid layout constants
skins_per_row = 3  # Number of skins per row in grid
skin_preview_size = 60  # Size of skin preview circles
skin_button_height = 40  # Height of select buttons
skin_spacing_x = 120  # Horizontal spacing between skins
skin_spacing_y = 140  # Vertical spacing between skins
skin_grid_start_x = 40  # Starting X position for skin grid
skin_grid_start_y = 200  # Starting Y position for skin grid
skin_select_buttons = []  # List of button dictionaries for skin selection

def load_leaderboard():
    """
    Load the leaderboard from the leaderboard file.

    Returns:
        list: A list of top 5 scores, default [0,0,0,0,0] if file doesn't exist or is invalid.
    """
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) == 5:
                return data
            else:
                return [0, 0, 0, 0, 0]
    except:
        return [0, 0, 0, 0, 0]

def save_leaderboard(leaderboard):
    """
    Save the leaderboard to the file.

    Args:
        leaderboard (list): The list of top 5 scores to save.
    """
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f)

def create_pipe():
    """
    Create a new pipe with a random gap position.

    Returns:
        dict: A dictionary containing 'x' (starting position) and 'gap_y' (gap top position).
    """
    gap_y = random.randint(120, ground_y - pipe_gap - 120)
    return {"x": width, "gap_y": gap_y}

def draw_pipe(surface, pipe):
    """
    Draw a pipe on the given surface.

    Args:
        surface (pygame.Surface): The surface to draw on.
        pipe (dict): The pipe data with 'x' and 'gap_y'.
    """
    # Define top and bottom pipe rectangles
    top_rect = pygame.Rect(pipe["x"], 0, pipe_width, pipe["gap_y"])
    bottom_rect = pygame.Rect(
        pipe["x"], pipe["gap_y"] + pipe_gap,
        pipe_width, ground_y - (pipe["gap_y"] + pipe_gap)
    )
    # Draw pipe bodies
    pygame.draw.rect(surface, (0, 153, 0), top_rect)
    pygame.draw.rect(surface, (0, 153, 0), bottom_rect)
    # Draw pipe outlines
    pygame.draw.rect(surface, (0, 102, 0), top_rect, 4)
    pygame.draw.rect(surface, (0, 102, 0), bottom_rect, 4)

def reset_pipes():
    """
    Reset the pipes list and spawn timer for a new game.
    """
    global pipes, pipe_spawn_timer
    pipes = [create_pipe()]
    pipe_spawn_timer = 0

def draw_button(surface, rect, text):
    """
    Draw a button with text on the given surface.

    Args:
        surface (pygame.Surface): The surface to draw on.
        rect (pygame.Rect): The rectangle for the button.
        text (str): The text to display on the button.
    """
    # Draw button background and border
    pygame.draw.rect(surface, (0, 102, 204), rect)
    pygame.draw.rect(surface, (255, 255, 255), rect, 3)
    # Render and center the text
    label = font.render(text, True, (255, 255, 255))
    label_rect = label.get_rect(center=rect.center)
    surface.blit(label, label_rect)

def customize_next_skin():
    """
    Cycle to the next bird skin for preview.
    """
    global current_skin, skin_message, skin_message_timer
    # Find current skin index
    current_index = next((i for i, skin in enumerate(bird_skins) if skin[0] == current_skin["color"]), 0)
    # Get next skin (wrap around)
    next_index = (current_index + 1) % len(bird_skins)
    new_color, new_name = bird_skins[next_index]
    current_skin = {"color": new_color, "name": new_name}
    skin_message = f"Previewing skin: {new_name}"
    skin_message_timer = 180  # Display for 3 seconds at 60 FPS

def confirm_skin_selection():
    """
    Confirm the current previewed skin as the selected skin.
    """
    global selected_skin, current_skin, skin_message, skin_message_timer
    selected_skin = current_skin.copy()
    skin_message = f"Skin selected: {selected_skin['name']}"
    skin_message_timer = 180  # Display for 3 seconds at 60 FPS

def draw_background(surface):
    """
    Draw the background including sky, ground, and clouds.

    Args:
        surface (pygame.Surface): The surface to draw on.
    """
    if is_night:
        # Night mode colors
        surface.fill((25, 25, 50))
        pygame.draw.rect(surface, (30, 70, 30), (0, ground_y, width, height - ground_y))
        pygame.draw.rect(surface, (50, 100, 50), (0, ground_y, width, 40))
        cloud_color = (100, 100, 120)
    else:
        # Day mode colors
        surface.fill((135, 206, 235))
        pygame.draw.rect(surface, (111, 185, 76), (0, ground_y, width, height - ground_y))
        pygame.draw.rect(surface, (179, 139, 71), (0, ground_y, width, 40))
        cloud_color = (255, 255, 255)
    
    # Draw clouds as circles
    pygame.draw.circle(surface, cloud_color, (120, 120), 30)
    pygame.draw.circle(surface, cloud_color, (150, 100), 24)
    pygame.draw.circle(surface, cloud_color, (90, 110), 22)
    pygame.draw.circle(surface, cloud_color, (420, 90), 28)
    pygame.draw.circle(surface, cloud_color, (450, 110), 24)
    pygame.draw.circle(surface, cloud_color, (390, 100), 20)

def draw_bird(surface, x, y, frame):
    """
    Draw the bird with animation based on velocity.

    Args:
        surface (pygame.Surface): The surface to draw on.
        x (int): X position of the bird.
        y (int): Y position of the bird.
        frame (int): Current frame counter for animation.
    """
    # Bird body as ellipse
    bird_rect = pygame.Rect(0, 0, 54, 40)
    bird_rect.center = x, y
    pygame.draw.ellipse(surface, current_skin["color"], bird_rect)

    # Wing color is darker shade of skin color
    wing_color = tuple(int(c * 0.7) for c in current_skin["color"])
    
    # Wing animation logic: only animate when bird is going up (negative velocity)
    if bird_velocity < -1:
        # 4-frame animation cycle
        wing_phase = (frame // 5) % 4
        if wing_phase == 0:
            wing_offset = 0  # Neutral
        elif wing_phase == 1:
            wing_offset = -8  # Up
        elif wing_phase == 2:
            wing_offset = 0  # Neutral
        else:
            wing_offset = 8  # Down
    else:
        # Resting position when not flapping up
        wing_offset = 5
    
    # Draw left wing as polygon
    left_wing_points = [
        (bird_rect.left + 10, bird_rect.centery),
        (bird_rect.left - 5, bird_rect.centery + wing_offset - 8),
        (bird_rect.left + 5, bird_rect.centery + wing_offset + 5),
    ]
    pygame.draw.polygon(surface, wing_color, left_wing_points)
    
    # Draw right wing as polygon
    right_wing_points = [
        (bird_rect.right - 10, bird_rect.centery),
        (bird_rect.right + 5, bird_rect.centery + wing_offset - 8),
        (bird_rect.right - 5, bird_rect.centery + wing_offset + 5),
    ]
    pygame.draw.polygon(surface, wing_color, right_wing_points)

    # Eye position (fixed relative to body)
    eye_pos = (bird_rect.right - 15, bird_rect.centery - 6)
    
    # Beak position changes based on velocity for animation
    if bird_velocity < -1:
        # Bird going up: beak up
        beak_points = [
            (bird_rect.right, bird_rect.centery - 4),
            (bird_rect.right + 18, bird_rect.centery - 14),
            (bird_rect.right + 18, bird_rect.centery + 6),
        ]
    elif bird_velocity > 1:
        # Bird going down: beak down
        beak_points = [
            (bird_rect.right, bird_rect.centery + 4),
            (bird_rect.right + 18, bird_rect.centery - 6),
            (bird_rect.right + 18, bird_rect.centery + 14),
        ]
    else:
        # Neutral: beak straight
        beak_points = [
            (bird_rect.right, bird_rect.centery),
            (bird_rect.right + 18, bird_rect.centery - 8),
            (bird_rect.right + 18, bird_rect.centery + 8),
        ]

    # Draw eye and beak
    pygame.draw.circle(surface, (0, 0, 0), eye_pos, 4)
    pygame.draw.polygon(surface, (255, 140, 0), beak_points)

# Bird position and physics
bird_x = width // 2  # Initial X position (changes to width//4 on reset)
bird_y = height // 2  # Initial Y position
bird_velocity = 0  # Vertical velocity
gravity = 0.5  # Gravity acceleration
flap_strength = -10  # Upward velocity on flap

# Game state variables
game_state = "start"  # "start" or "playing"
message_text = "Press SPACE / click to start"

def reset_game():
    """
    Reset all game variables for a new game session.
    """
    global bird_x, bird_y, bird_velocity, game_state, message_text, score, current_skin, skin_message, skin_message_timer, is_night, frame_counter
    bird_x = width // 4  # Move bird to left side
    bird_y = height // 2
    bird_velocity = 0
    game_state = "playing"
    message_text = "Press SPACE / click to flap"
    score = 0
    current_skin = selected_skin.copy()  # Use selected skin
    skin_message = ""
    skin_message_timer = 0
    is_night = False
    frame_counter = 0
    reset_pipes()  # Reset pipe system

def initialize_skin_buttons():
    """Initialize the select button rectangles for each skin"""
    global skin_select_buttons
    skin_select_buttons = []
    for i, (color, name) in enumerate(bird_skins):
        # Calculate grid position
        row = i // skins_per_row
        col = i % skins_per_row
        x = skin_grid_start_x + col * skin_spacing_x
        y = skin_grid_start_y + row * skin_spacing_y + skin_preview_size + 10
        button_rect = pygame.Rect(x, y, 80, skin_button_height)
        skin_select_buttons.append({
            "rect": button_rect,
            "color": color,
            "name": name,
            "index": i
        })

def draw_skin_selection_screen(surface):
    """Draw the skin selection screen with all skins and select buttons"""
    # Title
    title_text = font.render("Select a Skin", True, (30, 30, 30))
    surface.blit(title_text, (20, 20))
    
    # Back button
    back_button_rect = pygame.Rect(20, 70, 100, 40)
    draw_button(surface, back_button_rect, "Back")
    
    # Draw each skin preview and button
    for i, (color, name) in enumerate(bird_skins):
        row = i // skins_per_row
        col = i % skins_per_row
        x = skin_grid_start_x + col * skin_spacing_x
        y = skin_grid_start_y + row * skin_spacing_y
        
        # Skin preview circle
        preview_circle_x = x + 40
        preview_circle_y = y + 30
        pygame.draw.circle(surface, color, (preview_circle_x, preview_circle_y), skin_preview_size // 2)
        pygame.draw.circle(surface, (0, 0, 0), (preview_circle_x, preview_circle_y), skin_preview_size // 2, 2)
        
        # Skin name text
        skin_name_text = font.render(name, True, (30, 30, 30))
        name_rect = skin_name_text.get_rect(center=(preview_circle_x, y + skin_preview_size + 5))
        surface.blit(skin_name_text, name_rect)
        
        # Select button
        button = skin_select_buttons[i]
        draw_button(surface, button["rect"], "Select")

def show_start_screen(surface):
    """
    Draw the start screen with title, instructions, leaderboard, and skin info.

    Args:
        surface (pygame.Surface): The surface to draw on.
    """
    # Render text elements
    title_text = font.render("Flappy Bird", True, (30, 30, 30))
    info_text = font.render("Press SPACE / click to start", True, (30, 30, 30))
    customize_info = font.render("Press ENTER to cycle skins", True, (30, 30, 30))
    leaderboard_title = font.render("Leaderboard:", True, (30, 30, 30))
    skin_text = font.render(f"Current skin: {current_skin['name']}", True, (30, 30, 30))
    # Blit text to screen
    surface.blit(title_text, (20, 20))
    surface.blit(info_text, (20, 60))
    surface.blit(customize_info, (20, 100))
    surface.blit(leaderboard_title, (20, 140))
    # Display top 5 scores
    for i in range(5):
        lb_text = font.render(f"{i+1}. {leaderboard[i]}", True, (30, 30, 30))
        surface.blit(lb_text, (20, 160 + i * 20))
    surface.blit(skin_text, (20, 280))
    # Draw customize button
    draw_button(surface, customize_button_rect, "Customize Bird")
    # Show skin message if active
    if skin_message_timer > 0:
        notice_text = font.render(skin_message, True, (255, 50, 50))
        surface.blit(notice_text, (20, 320))

# Load high score at startup
leaderboard = load_leaderboard()
running = True

# Main game loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_RETURN and game_state == "start":
                customize_next_skin()  # Cycle skin on Enter
            elif event.key in (pygame.K_SPACE, pygame.K_UP):
                if game_state == "start":
                    confirm_skin_selection()  # Confirm skin and start game
                    reset_game()
                    bird_velocity = flap_strength
                else:
                    bird_velocity = flap_strength  # Flap during gameplay
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "start":
                if customize_button_rect.collidepoint(event.pos):
                    customize_next_skin()  # Customize button clicked
                else:
                    confirm_skin_selection()  # Start game on other clicks
                    reset_game()
                    bird_velocity = flap_strength
            else:
                bird_velocity = flap_strength  # Flap on click during gameplay

    # Game logic when playing
    if game_state == "playing":
        # Apply gravity and update bird position
        bird_velocity += gravity
        bird_y += bird_velocity

        # Prevent bird from going too high
        if bird_y < 20:
            bird_y = 20
            bird_velocity = 2  # Bounce down slightly

        # Spawn new pipes periodically
        pipe_spawn_timer += 1
        if pipe_spawn_timer >= pipe_spawn_interval:
            pipes.append(create_pipe())
            pipe_spawn_timer = 0

        # Bird collision rectangle
        bird_rect = pygame.Rect(0, 0, 54, 40)
        bird_rect.center = bird_x, bird_y

        # Update pipes and check collisions/scoring
        for pipe in pipes[:]:
            pipe["x"] -= pipe_speed  # Move pipe left
            # Define pipe rectangles
            top_rect = pygame.Rect(pipe["x"], 0, pipe_width, pipe["gap_y"])
            bottom_rect = pygame.Rect(
                pipe["x"], pipe["gap_y"] + pipe_gap,
                pipe_width, ground_y - (pipe["gap_y"] + pipe_gap)
            )

            # Score when passing pipe
            if pipe.get("scored") is not True and pipe["x"] + pipe_width < bird_x:
                score += 1
                pipe["scored"] = True
                # Toggle night mode every 15 points
                is_night = (score // 15) % 2 == 1

            # Remove off-screen pipes
            if pipe["x"] + pipe_width < 0:
                pipes.remove(pipe)
                continue

            # Check for pipe collisions
            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                # Game over: update leaderboard
                global leaderboard
                leaderboard.append(score)
                leaderboard.sort(reverse=True)
                leaderboard = leaderboard[:5]
                save_leaderboard(leaderboard)
                game_state = "start"
                message_text = "You died! Press SPACE / click to restart"
                # Reset bird position
                bird_x = width // 4
                bird_y = height // 2
                bird_velocity = 0
                reset_pipes()
                break

        # Check ground collision
        if bird_y + 20 >= ground_y:
            # Game over: update leaderboard
            global leaderboard
            leaderboard.append(score)
            leaderboard.sort(reverse=True)
            leaderboard = leaderboard[:5]
            save_leaderboard(leaderboard)
            game_state = "start"
            message_text = "You died! Press SPACE / click to restart"
            # Reset bird position
            bird_x = width // 4
            bird_y = height // 2
            bird_velocity = 0
            reset_pipes()

    # Drawing phase
    draw_background(screen)
    if game_state == "playing":
        for pipe in pipes:
            draw_pipe(screen, pipe)
    draw_bird(screen, bird_x, bird_y, frame_counter)
    frame_counter += 1

    # UI based on game state
    if game_state == "start":
        show_start_screen(screen)
    else:
        # Show score and flap instruction
        score_text = font.render(f"Score: {score}", True, (30, 30, 30))
        info_text = font.render("Press SPACE / click to flap", True, (30, 30, 30))
        screen.blit(score_text, (20, 20))
        screen.blit(info_text, (20, 60))
        # Show skin message if active
        if skin_message_timer > 0:
            notice_text = font.render(skin_message, True, (255, 50, 50))
            screen.blit(notice_text, (20, 100))
            skin_message_timer -= 1
        # Note: Duplicate skin message drawing removed in original, but kept as is

    # Update display and cap frame rate
    pygame.display.update()
    clock.tick(60)

# Clean exit
pygame.quit()
sys.exit()
