import pygame
import random
import sys

pygame.init()

width = 1000
height = 700
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Rune Snatch")

player_image = pygame.image.load("pics/Zeus.png")
player_image = pygame.transform.smoothscale(player_image, (200,200))
players_size = player_image.get_rect().size
player_x = width // 2 - players_size[0] // 2
player_y = height - players_size[1] - 10
player_speed = 5

item_image = pygame.image.load("pics/rune.png")
item_image = pygame.transform.smoothscale(item_image, (80, 80))
item_size = item_image.get_rect().size
item_x = random.randint(0, width - item_size[0])
item_y= -item_size[1]
item_speed = 3

score = 0
update = 0
font = pygame.font.Font(None, 36)

game_over_font = pygame.font.Font(None, 72)
game_over_text = game_over_font.render("GAME OVER", True, (0, 0, 255))
game_over_text_pos = (width // 2 - game_over_text.get_width() // 2, height // 2 - game_over_text.get_height() // 2)

button_font = pygame.font.Font(None, 36)
button_text = button_font.render("New game", True, (255, 255, 255))
button_text_pos = (width // 2 - button_text.get_width() // 2, height // 2 + button_text.get_height() // 2)
button_rect = pygame.Rect(button_text_pos[0], button_text_pos[1], button_text.get_width(), button_text.get_height())

STATE_PLAYING = 1
STATE_GAME_OVER = 2
state = STATE_PLAYING

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if state == STATE_GAME_OVER and button_rect.collidepoint(event.pos):
                state = STATE_PLAYING
                score = 0
                item_speed = 3
                player_x = width // 2 - players_size[0] // 2
                item_x = random.randint(0, width - item_size[0])
                item_y = -item_size[1]

    if state == STATE_PLAYING:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < width - players_size[0]:
            player_x += player_speed

        item_y += item_speed

        player_rect = pygame.Rect(player_x, player_y, players_size[0], players_size[1])
        item_rect = pygame.Rect(item_x, item_y, item_size[0], item_size[1])

        if player_rect.colliderect(item_rect):
            score += 50
            update += 1
            item_x = random.randint(0, width - item_size[0])
            item_y = -item_size[1]

            if update % 5 == 0:
                item_speed += 1

        if item_y > height:
            state = STATE_GAME_OVER

    window.fill((30, 30, 40))

    window.blit(player_image, (player_x, player_y))

    window.blit(item_image, (item_x, item_y))

    score_text = font.render("You got: " + str(score) + "gold", True, (255, 255, 255))
    window.blit(score_text, (10, 10))

    if state == STATE_GAME_OVER:
        window.blit(game_over_text, game_over_text_pos)

        pygame.draw.rect(window, (0, 0, 255), button_rect)
        window.blit(button_text, button_text_pos)

    pygame.display.update()

    clock.tick(60)

pygame.quit()
sys.exit()
