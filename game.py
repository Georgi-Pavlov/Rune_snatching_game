import pygame
import random
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rune Catcher")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 90)

PLAYING = 1
GAME_OVER = 2
game_state = PLAYING


# --- images ---
player_img = pygame.image.load(resource_path("pics/Zeus.png"))
frog_img = pygame.image.load(resource_path("pics/frog.png"))
player_img = pygame.transform.scale(player_img, (200, 200))
frog_img = pygame.transform.scale(frog_img, (150, 150))

heart_img = pygame.image.load(resource_path("pics/heart.png"))
heart_img = pygame.transform.scale(heart_img, (40, 40))


rune_images = {
    "normal": pygame.transform.scale(pygame.image.load(resource_path("pics/rune.png")), (70, 70)),
    "dd": pygame.transform.scale(pygame.image.load(resource_path("pics/dd.png")), (70, 70)),
    "haste": pygame.transform.scale(pygame.image.load(resource_path("pics/haste.png")), (70, 70)),
    "regen": pygame.transform.scale(pygame.image.load(resource_path("pics/regen.png")), (70, 70)),
    "creep": pygame.transform.scale(pygame.image.load(resource_path("pics/creep.png")), (85, 85)),
    "hex": pygame.transform.scale(pygame.image.load(resource_path("pics/hex.png")), (70, 70)),
    "shield": pygame.transform.scale(pygame.image.load(resource_path("pics/shield.png")), (70, 70)),
    "water": pygame.transform.scale(pygame.image.load(resource_path("pics/water.png")), (70, 70)),
    "invisible": pygame.transform.scale(pygame.image.load(resource_path("pics/invisible.png")), (70, 70)),
}


# --- player ---
player = pygame.Rect(WIDTH // 2, HEIGHT - 190, 200, 200)
player_speed = 6
base_speed = 6
player_image = player_img


# --- stats ---
gold = 0
lives = 10
max_lives = 10
max_runes = 1
floating_texts = []


# --- effects ---
haste_timer = 0
hex_timer = 0


invisible = False
shield = False
invisible_timer = 0
INVISIBLE_DURATION = 3000

# --- rune ---
rune_speed = 3

rune_weights = {
    "normal": 40,
    "dd": 15,
    "creep": 25,
    "regen": 3,
    "water": 4,
    "haste": 3,
    "hex": 3,
    "shield": 4,
    "invisible": 2
}


def add_floating_text(text, x, y, color=(255,255,0)):
    floating_texts.append({
        "text": text,
        "x": x,
        "y": y,
        "timer": 60,
        "color": color
    })


def spawn_rune():
    rtype = random.choices(
        list(rune_weights.keys()),
        weights=rune_weights.values()
    )[0]

    img = rune_images[rtype]
    rect = img.get_rect()
    rect.x = random.randint(0, WIDTH - rect.width)
    rect.y = -rect.height
    return {"type": rtype, "rect": rect}


def reset_game():
    global gold, lives, rune_speed, base_speed, player_speed, max_runes
    global runes, player, player_image, haste_timer, hex_timer, game_state

    gold = 0
    lives = 10
    rune_speed = 3
    base_speed = 6
    player_speed = 6
    max_runes = 1

    player.x = WIDTH // 2
    player_image = player_img

    haste_timer = 0
    hex_timer = 0

    runes = [spawn_rune()]
    game_state = PLAYING


runes = [spawn_rune()]

button_rect = pygame.Rect(WIDTH//2-120, HEIGHT//2+50, 240, 70)

running = True

while running:

    dt = clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if game_state == GAME_OVER:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    reset_game()


    keys = pygame.key.get_pressed()

    if game_state == PLAYING:

        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += player_speed


        # rune falling
        for rune in runes:
            rune["rect"].y += rune_speed


        for rune in runes[:]:

            if player.colliderect(rune["rect"]):

                rtype = rune["type"]

                if rtype == "normal":
                    gold += 50
                    add_floating_text("+50", rune["rect"].centerx, rune["rect"].centery)

                elif rtype == "dd":
                    gold += 100
                    add_floating_text("+100", rune["rect"].centerx, rune["rect"].centery)

                elif rtype == "haste":
                    player_speed = base_speed * 2
                    haste_timer = pygame.time.get_ticks()

                elif rtype == "regen":
                    if lives < max_lives:
                        if lives + 3 <= max_lives:
                            lives += 3
                            add_floating_text(f"+3 HP", rune["rect"].centerx, rune["rect"].centery, (80, 255, 120))
                        else:
                            lives = max_lives


                elif rtype == "creep":
                    if shield:
                        shield = False
                    else:
                        lives -= 1
                        add_floating_text("-1 HP", rune["rect"].centerx, rune["rect"].centery, (255, 80, 80))


                elif rtype == "hex":
                    player_speed = base_speed // 2
                    player_image = frog_img
                    hex_timer = pygame.time.get_ticks()

                elif rtype == "water":
                    if lives < max_lives:
                        if lives + 1 <= max_lives:
                            lives += 1
                            add_floating_text("+1 HP", rune["rect"].centerx, rune["rect"].centery, (80, 200, 255))
                        else:
                            lives = max_lives


                elif rtype == "shield":
                    shield = True

                elif rtype == "invisible":
                    invisible = True
                    invisible_timer = pygame.time.get_ticks()

                runes.remove(rune)
                continue


            if rune["rect"].top > HEIGHT:

                if rune["type"] in ["normal", "dd"]:
                    if shield:
                        shield = False
                    else:
                        lives -= 1
                        add_floating_text("-1 HP", rune["rect"].centerx, HEIGHT - 120, (255, 80, 80))

                runes.remove(rune)

        for ft in floating_texts[:]:
            ft["y"] -= 1
            ft["timer"] -= 1

            if ft["timer"] <= 0:
                floating_texts.remove(ft)


        while len(runes) < max_runes:
            runes.append(spawn_rune())


        if gold >= 1000:
            max_runes = 2

        if gold >= 2500:
            max_runes = 3

        if gold >= 5000:
            max_runes = 4


        if gold >= 500 and rune_speed == 3:
            rune_speed = 5
            base_speed += 1
            player_speed = base_speed

        if gold >= 1500 and rune_speed == 5:
            rune_speed = 7
            base_speed += 1
            player_speed = base_speed

        if gold >= 3000 and rune_speed == 7:
            rune_speed = 9
            base_speed += 1
            player_speed = base_speed


        if haste_timer:
            if pygame.time.get_ticks() - haste_timer > 5000:
                player_speed = base_speed
                haste_timer = 0


        if hex_timer:
            if pygame.time.get_ticks() - hex_timer > 5000:
                player_speed = base_speed
                player_image = player_img
                hex_timer = 0

        if invisible and pygame.time.get_ticks() - invisible_timer > INVISIBLE_DURATION:
            invisible = False

        if lives <= 0:
            game_state = GAME_OVER


    screen.fill((30, 30, 40))

    if not invisible:
        screen.blit(player_image, player)

    for rune in runes:
        screen.blit(rune_images[rune["type"]], rune["rect"])

    for ft in floating_texts:
        text_surface = font.render(ft["text"], True, ft["color"])
        screen.blit(text_surface, (ft["x"], ft["y"]))

    gold_text = font.render(f"Gold: {gold}", True, (255,255,0))
    screen.blit(gold_text, (10,10))

    screen.blit(heart_img, (WIDTH-120, 10))
    lives_text = font.render(str(lives), True, (255,255,255))
    screen.blit(lives_text, (WIDTH-70, 15))

    if invisible:
        inv_text = font.render("INVISIBLE", True, (150, 150, 255))
        screen.blit(inv_text, (WIDTH - 220, 50))

    if shield:
        inv_text = font.render("SHIELD", True, (150, 150, 255))
        screen.blit(inv_text, (WIDTH - 220, 50))


    if game_state == GAME_OVER:

        text = big_font.render("GAME OVER", True, (220,50,50))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 120))

        pygame.draw.rect(screen, (70,70,70), button_rect)
        pygame.draw.rect(screen, (200,200,200), button_rect, 3)

        play_text = font.render("PLAY AGAIN", True, (255,255,255))
        screen.blit(
            play_text,
            (
                button_rect.centerx - play_text.get_width()//2,
                button_rect.centery - play_text.get_height()//2
            )
        )


    pygame.display.flip()

pygame.quit()