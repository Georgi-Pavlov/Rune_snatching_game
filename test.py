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
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 90)

# --- States ---
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# --- Hero Data ---
HEROES = {
    "Zeus": "pics/Zeus.png",
    "Crystal Maiden": "pics/crystal_maiden.png",
    "CM Persona": "pics/crystal_maiden_persona.png",
    "Ancient Apparition": "pics/apparition.png",
    "Bristleback": "pics/bristleback.png",
    "Dawnbreaker": "pics/dawnbreaker.png",
    "Dazzle": "pics/dazzle.png",
    "Drow Ranger": "pics/drow_ranger.png",
    "Jakiro": "pics/jakiro.png",
    "Lich": "pics/lich.png",
    "Lina": "pics/lina.png",
    "Night Stalker": "pics/night_stalker.png",
    "Sniper": "pics/sniper.png",
    "Undying": "pics/undying.png",
    "Viper": "pics/viper.png",
    "Warlock": "pics/warlock.png",
    "Witch Doctor": "pics/witch_doctor.png"
}

# Pre-load icons (small) and full-size (large) images
hero_icons = {}
hero_full = {}
for name, path in HEROES.items():
    try:
        img = pygame.image.load(resource_path(path))
        hero_icons[name] = pygame.transform.scale(img, (40, 40))
        hero_full[name] = pygame.transform.scale(img, (200, 200))
    except:
        hero_icons[name] = pygame.Surface((40, 40))
        hero_full[name] = pygame.Surface((200, 200))

player_image = None
original_player_img = None

# --- Asset loading ---
frog_img = pygame.transform.scale(pygame.image.load(resource_path("pics/frog.png")), (150, 150))
heart_img = pygame.transform.scale(pygame.image.load(resource_path("pics/heart.png")), (40, 40))

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

# --- Game Variables ---
player = pygame.Rect(WIDTH // 2, HEIGHT - 190, 200, 200)
player_speed = base_speed = 6
gold = 0
lives = 10
max_lives = 10
max_runes = 1
runes = []
floating_texts = []
haste_timer = hex_timer = invisible_timer = 0
invisible = shield = False
INVISIBLE_DURATION = 3000

rune_speed = 3

rune_weights = {"normal": 40,
                "dd": 15,
                "creep": 25,
                "regen": 3,
                "water": 4,
                "haste": 3,
                "hex": 3,
                "shield": 4,
                "invisible": 2
                }

# --- Buttons ---
retry_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 20, 240, 60)
menu_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 100, 240, 60)


def add_floating_text(text, x, y, color=(255,255,0)):
    floating_texts.append({
        "text": text,
        "x": x,
        "y": y,
        "timer": 60,
        "color": color
    })


def spawn_rune():
    rtype = random.choices(list(rune_weights.keys()), weights=rune_weights.values())[0]
    rect = rune_images[rtype].get_rect()
    rect.x, rect.y = random.randint(0, WIDTH - rect.width), -rect.height
    return {"type": rtype, "rect": rect}


def reset_game(to_menu=False):
    global gold, lives, rune_speed, base_speed, player_speed, max_runes, runes, player_image, game_state, shield, invisible
    gold, lives, rune_speed, base_speed, player_speed, max_runes = 0, 10, 3, 6, 6, 1
    shield = invisible = False
    player.x = WIDTH // 2
    runes = [spawn_rune()]
    if to_menu:
        game_state = MENU
    else:
        player_image = original_player_img
        game_state = PLAYING


running = True
while running:
    screen.fill((30, 30, 40))
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == MENU and event.type == pygame.MOUSEBUTTONDOWN:
            cols = 3
            for i, name in enumerate(HEROES.keys()):
                col, row = i % cols, i // cols
                rect = pygame.Rect(100 + (col * 280), 140 + (row * 55), 260, 45)
                if rect.collidepoint(event.pos):
                    original_player_img = hero_full[name]
                    player_image = original_player_img
                    reset_game(False)

        if game_state == GAME_OVER and event.type == pygame.MOUSEBUTTONDOWN:
            if retry_btn.collidepoint(event.pos): reset_game(False)
            if menu_btn.collidepoint(event.pos): reset_game(True)

    if game_state == MENU:
        title = big_font.render("SELECT YOUR HERO", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        cols = 3
        for i, name in enumerate(HEROES.keys()):
            col, row = i % cols, i // cols
            btn_rect = pygame.Rect(100 + (col * 280), 140 + (row * 55), 260, 45)

            # Hover effect
            color = (70, 180, 70) if btn_rect.collidepoint((mx, my)) else (50, 130, 50)
            pygame.draw.rect(screen, color, btn_rect, border_radius=8)

            # Draw Preview Icon
            screen.blit(hero_icons[name], (btn_rect.x + 5, btn_rect.y + 2))
            # Draw Name
            txt = font.render(name, True, (255, 255, 255))
            screen.blit(txt, (btn_rect.x + 55, btn_rect.centery - txt.get_height() // 2))

    elif game_state in [PLAYING, GAME_OVER]:
        # --- Gameplay Logic ---
        if game_state == PLAYING:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player.left > 0: player.x -= player_speed
            if keys[pygame.K_RIGHT] and player.right < WIDTH: player.x += player_speed

            for rune in runes: rune["rect"].y += rune_speed
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
                    rune_speed += 2
                    base_speed += 1.5
                    player_speed = base_speed

                if gold >= 1500 and rune_speed == 5:
                    rune_speed += 2
                    base_speed += 1.5
                    player_speed = base_speed

                if gold >= 3000 and rune_speed == 7:
                    rune_speed += 2
                    base_speed += 1.5
                    player_speed = base_speed

            # Timers
            if haste_timer:
                if pygame.time.get_ticks() - haste_timer > 5000:
                    player_speed = base_speed
                    haste_timer = 0

            if hex_timer:
                if pygame.time.get_ticks() - hex_timer > 5000:
                    player_speed = base_speed
                    player_image = original_player_img
                    hex_timer = 0

            if invisible and pygame.time.get_ticks() - invisible_timer > INVISIBLE_DURATION:
                invisible = False

            if lives <= 0: game_state = GAME_OVER

        # --- Rendering ---
        if not invisible:
            screen.blit(player_image, player)

        for r in runes:
            screen.blit(rune_images[r["type"]], r["rect"])

        for ft in floating_texts:
            text_surface = font.render(ft["text"], True, ft["color"])
            screen.blit(text_surface, (ft["x"], ft["y"]))

        # UI
        screen.blit(font.render(f"Gold: {gold}", True, (255, 255, 0)), (10, 10))
        screen.blit(heart_img, (WIDTH - 120, 10))
        screen.blit(font.render(str(lives), True, (255, 255, 255)), (WIDTH - 70, 18))

        if invisible:
            inv_text = font.render("INVISIBLE", True, (150, 150, 255))
            screen.blit(inv_text, (WIDTH - 220, 50))

        if shield:
            inv_text = font.render("SHIELD", True, (150, 150, 255))
            screen.blit(inv_text, (WIDTH - 220, 50))

        if game_state == GAME_OVER:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))
            msg = big_font.render("GAME OVER", True, (255, 50, 50))
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 100))

            for btn, label in [(retry_btn, "RETRY"), (menu_btn, "CHANGE HERO")]:
                pygame.draw.rect(screen, (80, 80, 80), btn, border_radius=5)
                pygame.draw.rect(screen, (200, 200, 200), btn, 2, border_radius=5)
                l_txt = font.render(label, True, (255, 255, 255))
                screen.blit(l_txt, (btn.centerx - l_txt.get_width() // 2, btn.centery - l_txt.get_height() // 2))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()