'''
Author: Hamish HD
Flappy Bird starter screen
'''
import pygame
import random
import sys
import os

pygame.init()

HIGH_SCORE_FILE = "highscore.txt"

size = width, height = 600, 800
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Flappy Bird - Background Screen")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

ground_y = int(height * 0.75)
pipe_width = 80
pipe_gap = 200
pipe_speed = 3
pipe_spawn_interval = 90
pipe_spawn_timer = 0
pipes = []
score = 0
high_score = 0
is_night = False
frame_counter = 0

bird_skins = [
    ((255, 215, 0), "Gold"),
    ((180, 180, 255), "Blue"),
    ((255, 105, 180), "Pink"),
    ((173, 255, 47), "Lime"),
    ((255, 140, 0), "Orange"),
    ((128, 0, 128), "Purple"),
]
current_skin = {"color": bird_skins[0][0], "name": bird_skins[0][1]}
selected_skin = {"color": bird_skins[0][0], "name": bird_skins[0][1]}
skin_message = ""
skin_message_timer = 0
customize_button_rect = pygame.Rect(width - 220, 20, 200, 50)
select_button_rect = pygame.Rect(width - 220, 80, 200, 50)

# Skin selection grid layout
skins_per_row = 3
skin_preview_size = 60
skin_button_height = 40
skin_spacing_x = 120
skin_spacing_y = 140
skin_grid_start_x = 40
skin_grid_start_y = 200
skin_select_buttons = []


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read())
    except:
        return 0


def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))


def create_pipe():
    gap_y = random.randint(120, ground_y - pipe_gap - 120)
    return {"x": width, "gap_y": gap_y}


def draw_pipe(surface, pipe):
    top_rect = pygame.Rect(pipe["x"], 0, pipe_width, pipe["gap_y"])
    bottom_rect = pygame.Rect(
        pipe["x"], pipe["gap_y"] + pipe_gap,
        pipe_width, ground_y - (pipe["gap_y"] + pipe_gap)
    )
    pygame.draw.rect(surface, (0, 153, 0), top_rect)
    pygame.draw.rect(surface, (0, 153, 0), bottom_rect)
    pygame.draw.rect(surface, (0, 102, 0), top_rect, 4)
    pygame.draw.rect(surface, (0, 102, 0), bottom_rect, 4)


def reset_pipes():
    global pipes, pipe_spawn_timer
    pipes = [create_pipe()]
    pipe_spawn_timer = 0


def draw_button(surface, rect, text):
    pygame.draw.rect(surface, (0, 102, 204), rect)
    pygame.draw.rect(surface, (255, 255, 255), rect, 3)
    label = font.render(text, True, (255, 255, 255))
    label_rect = label.get_rect(center=rect.center)
    surface.blit(label, label_rect)


def customize_next_skin():
    global current_skin, skin_message, skin_message_timer
    current_index = next((i for i, skin in enumerate(bird_skins) if skin[0] == current_skin["color"]), 0)
    next_index = (current_index + 1) % len(bird_skins)
    new_color, new_name = bird_skins[next_index]
    current_skin = {"color": new_color, "name": new_name}
    skin_message = f"Previewing skin: {new_name}"
    skin_message_timer = 180


def confirm_skin_selection():
    global selected_skin, current_skin, skin_message, skin_message_timer
    selected_skin = current_skin.copy()
    skin_message = f"Skin selected: {selected_skin['name']}"
    skin_message_timer = 180


def draw_background(surface):
    if is_night:
        surface.fill((25, 25, 50))
        pygame.draw.rect(surface, (30, 70, 30), (0, ground_y, width, height - ground_y))
        pygame.draw.rect(surface, (50, 100, 50), (0, ground_y, width, 40))
        cloud_color = (100, 100, 120)
    else:
        surface.fill((135, 206, 235))
        pygame.draw.rect(surface, (111, 185, 76), (0, ground_y, width, height - ground_y))
        pygame.draw.rect(surface, (179, 139, 71), (0, ground_y, width, 40))
        cloud_color = (255, 255, 255)
    
    pygame.draw.circle(surface, cloud_color, (120, 120), 30)
    pygame.draw.circle(surface, cloud_color, (150, 100), 24)
    pygame.draw.circle(surface, cloud_color, (90, 110), 22)
    pygame.draw.circle(surface, cloud_color, (420, 90), 28)
    pygame.draw.circle(surface, cloud_color, (450, 110), 24)
    pygame.draw.circle(surface, cloud_color, (390, 100), 20)


def draw_bird(surface, x, y, frame):
    bird_rect = pygame.Rect(0, 0, 54, 40)
    bird_rect.center = x, y
    pygame.draw.ellipse(surface, current_skin["color"], bird_rect)

    # Draw animated wings
    wing_color = tuple(int(c * 0.7) for c in current_skin["color"])  # Darker shade for wing
    
    # Wing animation only when bird is going up
    if bird_velocity < -1:
        wing_phase = (frame // 5) % 4  # 4-frame animation cycle
        if wing_phase == 0:
            # Wings neutral
            wing_offset = 0
        elif wing_phase == 1:
            # Wings up
            wing_offset = -8
        elif wing_phase == 2:
            # Wings neutral again
            wing_offset = 0
        else:
            # Wings down
            wing_offset = 8
    else:
        # Wings resting when not going up
        wing_offset = 5
    
    # Draw left wing
    left_wing_points = [
        (bird_rect.left + 10, bird_rect.centery),
        (bird_rect.left - 5, bird_rect.centery + wing_offset - 8),
        (bird_rect.left + 5, bird_rect.centery + wing_offset + 5),
    ]
    pygame.draw.polygon(surface, wing_color, left_wing_points)
    
    # Draw right wing
    right_wing_points = [
        (bird_rect.right - 10, bird_rect.centery),
        (bird_rect.right + 5, bird_rect.centery + wing_offset - 8),
        (bird_rect.right - 5, bird_rect.centery + wing_offset + 5),
    ]
    pygame.draw.polygon(surface, wing_color, right_wing_points)

    # Fixed eye position (doesn't move based on velocity)
    eye_pos = (bird_rect.right - 15, bird_rect.centery - 6)
    
    if bird_velocity < -1:
        beak_points = [
            (bird_rect.right, bird_rect.centery - 4),
            (bird_rect.right + 18, bird_rect.centery - 14),
            (bird_rect.right + 18, bird_rect.centery + 6),
        ]
    elif bird_velocity > 1:
        beak_points = [
            (bird_rect.right, bird_rect.centery + 4),
            (bird_rect.right + 18, bird_rect.centery - 6),
            (bird_rect.right + 18, bird_rect.centery + 14),
        ]
    else:
        beak_points = [
            (bird_rect.right, bird_rect.centery),
            (bird_rect.right + 18, bird_rect.centery - 8),
            (bird_rect.right + 18, bird_rect.centery + 8),
        ]

    pygame.draw.circle(surface, (0, 0, 0), eye_pos, 4)
    pygame.draw.polygon(surface, (255, 140, 0), beak_points)


bird_x = width // 2
bird_y = height // 2
bird_velocity = 0
gravity = 0.5
flap_strength = -10

game_state = "start"
message_text = "Press SPACE / click to start"


def reset_game():
    global bird_x, bird_y, bird_velocity, game_state, message_text, score, current_skin, skin_message, skin_message_timer, is_night, frame_counter
    bird_x = width // 4
    bird_y = height // 2
    bird_velocity = 0
    game_state = "playing"
    message_text = "Press SPACE / click to flap"
    score = 0
    current_skin = selected_skin.copy()
    skin_message = ""
    skin_message_timer = 0
    is_night = False
    frame_counter = 0
    reset_pipes()


def initialize_skin_buttons():
    """Initialize the select button rectangles for each skin"""
    global skin_select_buttons
    skin_select_buttons = []
    for i, (color, name) in enumerate(bird_skins):
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
    title_text = font.render("Select a Skin", True, (30, 30, 30))
    surface.blit(title_text, (20, 20))
    
    back_button_rect = pygame.Rect(20, 70, 100, 40)
    draw_button(surface, back_button_rect, "Back")
    
    # Draw each skin with preview and select button
    for i, (color, name) in enumerate(bird_skins):
        row = i // skins_per_row
        col = i % skins_per_row
        x = skin_grid_start_x + col * skin_spacing_x
        y = skin_grid_start_y + row * skin_spacing_y
        
        # Draw skin preview circle
        preview_circle_x = x + 40
        preview_circle_y = y + 30
        pygame.draw.circle(surface, color, (preview_circle_x, preview_circle_y), skin_preview_size // 2)
        pygame.draw.circle(surface, (0, 0, 0), (preview_circle_x, preview_circle_y), skin_preview_size // 2, 2)
        
        # Draw skin name
        skin_name_text = font.render(name, True, (30, 30, 30))
        name_rect = skin_name_text.get_rect(center=(preview_circle_x, y + skin_preview_size + 5))
        surface.blit(skin_name_text, name_rect)
        
        # Draw select button
        button = skin_select_buttons[i]
        draw_button(surface, button["rect"], "Select")


def show_start_screen(surface):
    title_text = font.render("Flappy Bird", True, (30, 30, 30))
    info_text = font.render("Press SPACE / click to start", True, (30, 30, 30))
    customize_info = font.render("Press ENTER to cycle skins", True, (30, 30, 30))
    high_score_text = font.render(f"High Score: {high_score}", True, (30, 30, 30))
    skin_text = font.render(f"Current skin: {current_skin['name']}", True, (30, 30, 30))
    surface.blit(title_text, (20, 20))
    surface.blit(info_text, (20, 60))
    surface.blit(customize_info, (20, 100))
    surface.blit(high_score_text, (20, 140))
    surface.blit(skin_text, (20, 180))
    draw_button(surface, customize_button_rect, "Customize Bird")
    if skin_message_timer > 0:
        notice_text = font.render(skin_message, True, (255, 50, 50))
        surface.blit(notice_text, (20, 220))


high_score = load_high_score()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_RETURN and game_state == "start":
                customize_next_skin()
            elif event.key in (pygame.K_SPACE, pygame.K_UP):
                if game_state == "start":
                    confirm_skin_selection()
                    reset_game()
                    bird_velocity = flap_strength
                else:
                    bird_velocity = flap_strength
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "start":
                if customize_button_rect.collidepoint(event.pos):
                    customize_next_skin()
                else:
                    confirm_skin_selection()
                    reset_game()
                    bird_velocity = flap_strength
            else:
                bird_velocity = flap_strength

    if game_state == "playing":
        bird_velocity += gravity
        bird_y += bird_velocity

        if bird_y < 20:
            bird_y = 20
            bird_velocity = 2

        pipe_spawn_timer += 1
        if pipe_spawn_timer >= pipe_spawn_interval:
            pipes.append(create_pipe())
            pipe_spawn_timer = 0

        bird_rect = pygame.Rect(0, 0, 54, 40)
        bird_rect.center = bird_x, bird_y

        for pipe in pipes[:]:
            pipe["x"] -= pipe_speed
            top_rect = pygame.Rect(pipe["x"], 0, pipe_width, pipe["gap_y"])
            bottom_rect = pygame.Rect(
                pipe["x"], pipe["gap_y"] + pipe_gap,
                pipe_width, ground_y - (pipe["gap_y"] + pipe_gap)
            )

            if pipe.get("scored") is not True and pipe["x"] + pipe_width < bird_x:
                score += 1
                pipe["scored"] = True
                is_night = (score // 15) % 2 == 1

            if pipe["x"] + pipe_width < 0:
                pipes.remove(pipe)
                continue

            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                game_state = "start"
                message_text = "You died! Press SPACE / click to restart"
                bird_x = width // 4
                bird_y = height // 2
                bird_velocity = 0
                reset_pipes()
                break

        if bird_y + 20 >= ground_y:
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            game_state = "start"
            message_text = "You died! Press SPACE / click to restart"
            bird_x = width // 4
            bird_y = height // 2
            bird_velocity = 0
            reset_pipes()

    draw_background(screen)
    if game_state == "playing":
        for pipe in pipes:
            draw_pipe(screen, pipe)
    draw_bird(screen, bird_x, bird_y, frame_counter)
    frame_counter += 1

    if game_state == "start":

        show_start_screen(screen)
    else:
        score_text = font.render(f"Score: {score}", True, (30, 30, 30))
        info_text = font.render("Press SPACE / click to flap", True, (30, 30, 30))
        screen.blit(score_text, (20, 20))
        screen.blit(info_text, (20, 60))
        if skin_message_timer > 0:
            notice_text = font.render(skin_message, True, (255, 50, 50))
            screen.blit(notice_text, (20, 100))
            skin_message_timer -= 1
        if skin_message_timer > 0:
            skin_text = font.render(skin_message, True, (255, 50, 50))
            screen.blit(skin_text, (20, 100))
            skin_message_timer -= 1

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
