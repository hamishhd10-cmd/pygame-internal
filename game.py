'''
Author: Hamish HD
Flappy Bird starter screen
'''
import pygame
import sys

pygame.init()

size = width, height = 600, 800
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Flappy Bird - Background Screen")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

ground_y = int(height * 0.75)


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
    global bird_x, bird_y, bird_velocity, game_state, message_text
    bird_x = width // 4
    bird_y = height // 2
    bird_velocity = 0
    game_state = "playing"
    message_text = "Press SPACE / click to flap"


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

        if bird_y + 20 >= ground_y:
            game_state = "start"
            message_text = "You died! Press SPACE / click to restart"
            bird_x = width // 4
            bird_y = height // 2
            bird_velocity = 0

    draw_background(screen)
    draw_bird(screen, bird_x, bird_y)

    if game_state == "start":
        show_start_screen(screen)
    else:
        info_text = font.render("Press SPACE / click to flap", True, (30, 30, 30))
        screen.blit(info_text, (20, 20))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
