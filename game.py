'''
Author: Hamish HD
Flappy Bird starter screen
'''
import pygame
import random
import sys

pygame.init()

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


def draw_background(surface):
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


def draw_bird(surface, x, y):
    bird_rect = pygame.Rect(0, 0, 54, 40)
    bird_rect.center = x, y
    pygame.draw.ellipse(surface, (255, 215, 0), bird_rect)
    pygame.draw.circle(surface, (0, 0, 0), (bird_rect.right - 15, bird_rect.centery - 6), 4)
    pygame.draw.polygon(surface, (255, 140, 0), [
        (bird_rect.right, bird_rect.centery),
        (bird_rect.right + 18, bird_rect.centery - 8),
        (bird_rect.right + 18, bird_rect.centery + 8),
    ])


bird_x = width // 4
bird_y = height // 2
bird_velocity = 0
gravity = 0.5
flap_strength = -10

game_state = "start"
message_text = "Press SPACE / click to start"


def reset_game():
    global bird_x, bird_y, bird_velocity, game_state, message_text, score
    bird_x = width // 4
    bird_y = height // 2
    bird_velocity = 0
    game_state = "playing"
    message_text = "Press SPACE / click to flap"
    score = 0
    reset_pipes()


def show_start_screen(surface):
    title_text = font.render("Flappy Bird", True, (30, 30, 30))
    info_text = font.render(message_text, True, (30, 30, 30))
    surface.blit(title_text, (20, 20))
    surface.blit(info_text, (20, 60))


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key in (pygame.K_SPACE, pygame.K_UP):
                if game_state == "start":
                    reset_game()
                else:
                    bird_velocity = flap_strength
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "start":
                reset_game()
            else:
                bird_velocity = flap_strength

    if game_state == "playing":
        bird_velocity += gravity
        bird_y += bird_velocity

        if bird_y < 20:
            bird_y = 20
            bird_velocity = 0

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

            if pipe["x"] + pipe_width < 0:
                pipes.remove(pipe)
                continue

            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                game_state = "start"
                message_text = "You died! Press SPACE / click to restart"
                bird_x = width // 4
                bird_y = height // 2
                bird_velocity = 0
                reset_pipes()
                break

        if bird_y + 20 >= ground_y:
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
    draw_bird(screen, bird_x, bird_y)

    if game_state == "start":
        show_start_screen(screen)
    else:
        score_text = font.render(f"Score: {score}", True, (30, 30, 30))
        info_text = font.render("Press SPACE / click to flap", True, (30, 30, 30))
        screen.blit(score_text, (20, 20))
        screen.blit(info_text, (20, 60))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
