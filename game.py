import pygame
import random
import sys
import os
from bosses.cave_guardians import CaveGuardians
from bosses.lava_elemental import LavaElemental
from bosses.roshan import Roshan


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


pygame.mixer.pre_init(44100, -16, 2, 128)

pygame.init()

pygame.mixer.init()

WIDTH, HEIGHT = 1100, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rune Catcher")

clock = pygame.time.Clock()
# General font
font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont("timesnewroman", 80, bold=True)

# Story font
story_font = pygame.font.SysFont("georgia", 28)
hero_story_font = pygame.font.SysFont("garamond", 18)

hero_select = pygame.image.load(resource_path("pics/hero_select_background.png"))
hero_select = pygame.transform.scale(hero_select, (WIDTH, HEIGHT))

main_menu_bg = pygame.image.load(resource_path("pics/main_menu.png")).convert()
main_menu_bg = pygame.transform.scale(main_menu_bg, (WIDTH, HEIGHT))

how_to_play_bg = pygame.image.load(resource_path("pics/how_to_play.png")).convert()
how_to_play_bg = pygame.transform.scale(how_to_play_bg, (WIDTH, HEIGHT))

story_begin = pygame.image.load(resource_path("pics/story_begin.png")).convert()
story_begin = pygame.transform.scale(story_begin, (WIDTH, HEIGHT))

menu_overlay = pygame.Surface((WIDTH, HEIGHT))
menu_overlay.fill((0, 0, 0))
menu_overlay.set_alpha(90)

damage_flash = pygame.Surface((WIDTH, HEIGHT))
damage_flash.fill((180, 0, 0))
damage_flash_alpha = 0
damage_flash.set_alpha(damage_flash_alpha)

# --- States ---
MAIN_MENU = 0
HERO_SELECT = 1
HERO_STORY = 2
PLAYING = 3
ENDLESS = 4
HOW_TO_PLAY = 5
STORY = 6
GAME_OVER = 7
BOSS_FIGHT = 8
game_state = MAIN_MENU

story_lines = [
"For centuries the runes of power flowed freely across the land.",
"",
"Gold, Haste, Regeneration... fragments of ancient magic.",
"",
"But something has changed.",
"",
"The legendary Golden Rune has been stolen.",
"",
"Without it the rune cycle is broken.",
"",
"Magic spills uncontrollably across the world.",
"",
"Deep within a forgotten cave, creatures guard the stolen power.",
"",
"Heroes have begun the hunt.",
"",
"You are one of them."
]

# hero stories
hero_stories = {
    "Drow Ranger": [
        "Dwelling deep within the forest and above the Glacier",
        "few have ever caught a glimpse of the solitary and impossibly beautiful Drow Ranger.",
        "Her presence was known only from the chill of frost arrows, driving deep into her enemies hearts.",
        "Named and raised by the sympathetic Drow, Traxex draws on her heritage to deal with assailants who venture too close.",
        "Honing her skill to peerless precision, the ranger's legendary marksmanship only improves with each passing skirmish."
    ],
    "Bristleback": [
        "The enforcer at a local pub, Rigwarl's never failed to collect a tab.",
        "His thorny back deters attacks while peppering foes with constant barrages of quill sprays.",
        "When it comes to a fight, he really puts his back into it."''
        "With every volley Rigwarl works himself into a fury, adding rage to each blow"
    ],
    "Dawnbreaker": [
        "To those who dared organize defiance, the Children of Light would dispatch Valora "
        "and her hammer to show a measure of their power.",
        "Dawnbreaker shines Luminosity in the heart of battle",
        "happily shattering her enemies with her celestial hammer, the Brightmaul."
        "Always waiting to tap her true cosmic power she is eager to rout her enemies on the battlefield no matter where they are."
    ],
    "Night Stalker": [
        "The beast of bedtime tales, Balanar is the primal terror that every child knows to fear.",
        "Once the sun goes down, Night Stalker's hunt begins.",
        "Charging through the shadowy forests, he snares his prey, forcing all who see him to flee,",
        "arms withering and spells fizzling as their hearts are stricken with Crippling Fear."
    ],
    "Sniper": [
        "With a single bullet, Kardel Sharpeye pierced the steep-stalker's central eye from the valley floor,",
        "an ominous act that resulted in his ritual exile. He would win acclaim on a field of battle, or never return.",
        "Like his mountain kin, the Sniper is one with his firearm.",
        "No enemy is safe within the range of the Sniper's scope.",
        "As he pauses to line up his cross-hairs, compensating for every variable before he Assassinates his mark in one fatal shot."
    ],
    "Undying": [
        "Consumed by the chorus of the unending, Dirge, the Undying one marches across the land, rallying the dead to rise against the living.",
        "He saps the strength from his enemies, and rip the souls from all close-by beings.",
        "Monstrous and truly horrifying, Undying finds great pleasure in keeping himself alive and vital, while his adversaries suffer as he delivers death to the field."
    ],
    "Viper": [
        "It was foolhardy to try and tame a Netherdrake, a lesson the old wizard learned in death.",
        "Freed from his captor, Viper spread his wings and went forth to explore the surface world.",
        "With his poison attacks imbued with virulent liquid, he is causing joints to harden, crippling foes whether they choose to flee or fight.",
        "The Viper strike signals the beginning of the end. The afflicted victim staggers to a crawl, barely able to take its next step.",
        "If the Netherdrake doesn't finish his targets off, the venom in their veins will."
    ],
    "Ancient Apparition": [
        "Projected from the cold, infinite void, the Ancient Apparition known as Kaldr is but a faint image of his true self.",
        "Nevertheless, his chilling touch is more than enough to make heroes quickly get cold feet",
        "and before they know it, find themselves frozen in place.",
        "All enemies have no choice but to retreat before their brittle bodies shatter to pieces..."
    ],
    "Crystal Maiden": [
        "Wherever Rylai went, the cold went with her.",
        "Fields and orchards withered in her wake, leaving her parents no choice but to pack her off to Icewrack, a realm in the frigid north.",
        "Under the tutelage of a hermit wizard, Rylai learned to imprison her enemies with a thick block of ice, holding them in place as she freezes the ground.",
        "In the heat of battle, Rylai keeps a cool head. Channeling her elemental talents, the Crystal Maiden obliterates all foes foolish enough to remain in her freezing field."
    ],
    "Dazzle": [
        "A journey to the Nothl Realm changes all its visitors, not least of which Dazzle, a young acolyte of the Dezun Order.",
        "Consecrated as a Shadow Priest, Dazzle sends outs shadow waves to mend and maim.",
        "Foes are crippled by his paralytic enchantment while allies are blessed, cheating death no matter how severe their injuries.",
        "Enemies within earshot of his incantations feel their bodies weaken, for those who cross Dazzle are invariably afflicted with an eternity of suffering."
    ],
    "Jakiro": [
        "Most Pyrexae Dragons are hatched with one head, attuned to either ice or fire.",
        "Then there was Jakiro, an accident of nature.",
        "Possessing the might of both elements, the twin-headed dragon's dual breath freezes and burns simultaneously.",
        "Gobs of liquid frost or liquid fire adhere to armor and walls, melting down steel and stone alike."
    ],
    "Lich": [
        "Resurrected by a curious geomancer, Ethreain bewitched his savior with a sinister gaze, then promptly made the man his newest sacrifice.",
        "Finally freed from the depths of the Black Pool, the Lich returns to wreak icy destruction on the world.",
        "Ethreain floats across the battlefield to blast any who cross him."
    ],
    "Lina": [
        "Like her younger sister, Lina's elemental affinity was the source of many headaches.",
        "Sent south to live with a patient aunt, she learned to master her fiery soul in the blazing Desert of Misrule.",
        "Attuned to fire, Lina ignites the ground, incinerating foes in a column of flame."
    ],
    "Warlock": [
        "In the endless pursuit of rare texts, Demnok Lannik found it necessary to learn the magics",
        "that would help him reach the most inaccessible tomes.",
        "In short time, his obsessive study made him the most powerful Warlock in the academy.",
        "He brings a chaotic offering and eldritch imps to every fight.",
        "Not even an army can hold long against his dark spells and immolated golems."
    ],
    "Witch Doctor": [
        "A bizarre figure shambles across the land, searching for any opportunity to apply the morbid arts of Prefectura Island.",
        "To his allies, Zharvakko is a fountain of health, while to his foes he is the source of illness.",
        "Notoriously known for cursing his adversaries and forcing them to relive the agony they will inevitably receive"
    ],
    "Zeus": [
        "Charged with godly might emanating from his lightning hands Zeus calls down lightning bolts to smite his enemies.",
        "None can hide from Zeus, pointing his arms skyward to bring divine punishment down on each and every foe.",
        "Wherever they may be, none shall stand against the Thundergod's wrath."
    ]

}

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

hero_backgrounds = {}

for name in HEROES:
    filename = name.lower().replace(" ", "_") + "_background.png"
    path = f"pics/{filename}"

    try:
        bg = pygame.image.load(resource_path(path))
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

        dim = pygame.Surface((WIDTH, HEIGHT))
        dim.fill((0, 0, 0))
        dim.set_alpha(140)

        bg.blit(dim, (0, 0))

        hero_backgrounds[name] = bg
    except:
        hero_backgrounds[name] = None

# Pre-load icons (small) and full-size (large) images
hero_icons = {}
hero_full = {}
for name, path in HEROES.items():
    try:
        img = pygame.image.load(resource_path(path))
        hero_icons[name] = pygame.transform.scale(img, (40, 40))
        hero_full[name] = pygame.transform.scale(img, (190, 190))
    except:
        hero_icons[name] = pygame.Surface((40, 40))
        hero_full[name] = pygame.Surface((190, 190))

player_image = None
original_player_img = None

# --- Asset loading ---
frog_img = pygame.transform.scale(pygame.image.load(resource_path("pics/frog.png")), (150, 150))
heart_img = pygame.transform.scale(pygame.image.load(resource_path("pics/heart.png")), (40, 40))

rune_images = {
    "normal": pygame.transform.scale(pygame.image.load(resource_path("pics/runе.png")), (60, 60)),
    "dd": pygame.transform.scale(pygame.image.load(resource_path("pics/dd.png")), (60, 60)),
    "haste": pygame.transform.scale(pygame.image.load(resource_path("pics/haste.png")), (60, 60)),
    "regen": pygame.transform.scale(pygame.image.load(resource_path("pics/regen.png")), (60, 60)),
    "creep": pygame.transform.scale(pygame.image.load(resource_path("pics/creep.png")), (80, 80)),
    "hex": pygame.transform.scale(pygame.image.load(resource_path("pics/hex.png")), (60, 60)),
    "shield": pygame.transform.scale(pygame.image.load(resource_path("pics/shield.png")), (60, 60)),
    "water": pygame.transform.scale(pygame.image.load(resource_path("pics/water.png")), (60, 60)),
    "invisible": pygame.transform.scale(pygame.image.load(resource_path("pics/invisible.png")), (60, 60))
}

rune_data = {
    "normal": """Gold rune: +50 gold if you catch it, or -1hp if you dont
    During boss fight: -1hp to the boss""",
    "dd": """Double Damage rune: +100 gold if you catch it, or -1hp if you dont
    During boss fight: -1hp to the boss""",
    "haste": "Haste rune: double movement speed",
    "regen": "Regeneration rune: restore up to 3HP",
    "creep": "Enemy creep: damages you",
    "hex": "Hex rune: turns you into slow frog",
    "shield": "Shield rune: blocks next hit",
    "water": "Water rune: +1 HP",
    "invisible": "Invisibility rune: you become invisible"
}

# Sounds

sounds = {
    "pickup": pygame.mixer.Sound(resource_path("sounds/pickup.wav")),
    "damage": pygame.mixer.Sound(resource_path("sounds/damage.ogg")),
    "button_hover": pygame.mixer.Sound(resource_path("sounds/button_hover.ogg")),
    "hero_select": pygame.mixer.Sound(resource_path("sounds/hero_select.wav")),
    "water": pygame.mixer.Sound(resource_path("sounds/water.wav")),
    "game_over": pygame.mixer.Sound(resource_path("sounds/game_over.wav")),
    "miss": pygame.mixer.Sound(resource_path("sounds/miss.wav")),
    "shield": pygame.mixer.Sound(resource_path("sounds/shield.wav")),
    "regen": pygame.mixer.Sound(resource_path("sounds/regen.aif")),
    "block": pygame.mixer.Sound(resource_path("sounds/block.ogg")),
    "hex": pygame.mixer.Sound(resource_path("sounds/hex.wav")),
    "haste": pygame.mixer.Sound(resource_path("sounds/haste.ogg")),
    "invisible": pygame.mixer.Sound(resource_path("sounds/invisible.ogg")),
    "main_menu": pygame.mixer.Sound(resource_path("sounds/main_menu.ogg")),
    "cave_entrance_guardian": pygame.mixer.Sound(resource_path("sounds/cave_entrance_guardian.ogg")),
    "boss_win": pygame.mixer.Sound(resource_path("sounds/boss_win.wav")),
    "cave_entrance_intro": pygame.mixer.Sound(resource_path("sounds/cave_entrance_intro.mp3")),
    "roshan_intro": pygame.mixer.Sound(resource_path("sounds/roshan_intro.wav")),
    "lava_elemental_intro": pygame.mixer.Sound(resource_path("sounds/lava_elemental_intro.mp3"))
}

for s in sounds.values():
    s.set_volume(0.35)

# --- Game Variables ---
player = pygame.Rect(WIDTH // 2, HEIGHT - 190, 190, 190)
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
selected_hero = None
rune_speed = 3
embers = []
shake_timer = 0
shake_strength = 0
multiplier = 1
consecutive_runes = 0
last_hovered_hero = None
game_over_played = False
last_hovered_button = None
player_mask = None
current_boss = None
endless_mode = False
aegis = False

# boss defeated status
boss_defeated = {
    "cave_guardians": False,
    "lava_elemental": False,
    "roshan": False,
}

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

status_font = pygame.font.SysFont(None, 20)

# --- Buttons ---
retry_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 20, 240, 60)
menu_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 100, 240, 60)

how_to_play_btn = pygame.Rect(60, HEIGHT - 90, 260, 55)
choose_hero_btn = pygame.Rect(WIDTH - 320, HEIGHT - 90, 260, 55)

back_btn = pygame.Rect(40, 40, 120, 50)

hero_story_back_btn = pygame.Rect(WIDTH // 2 - 130, HEIGHT - 80, 260, 45)
hero_story_play_btn = pygame.Rect(WIDTH - 300, HEIGHT - 80, 260, 45)
hero_story_endless_btn = pygame.Rect(40, HEIGHT - 80, 260, 45)


def play_music(file):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(resource_path(file))
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)

def update_multiplier():
    global multiplier

    if consecutive_runes >= 18:
        multiplier = 10
    elif consecutive_runes >= 14:
        multiplier = 5
    elif consecutive_runes >= 10:
        multiplier = 4
    elif consecutive_runes >= 7:
        multiplier = 3
    elif consecutive_runes >= 4:
        multiplier = 2
    else:
        multiplier = 1


def spawn_ember():
    embers.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(-50, -10),
        "speed": random.uniform(1, 3),
        "size": random.randint(2, 4)
    })


def add_floating_text(text, x, y, color=(255, 255, 0)):
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
    image = rune_images[rtype]
    mask = pygame.mask.from_surface(image)

    return {
        "type": rtype,
        "rect": rect,
        "mask": mask
    }


def reset_game(to_menu=False):
    global gold, lives, rune_speed, base_speed, player_speed, max_runes, runes, player_image, game_state, shield, \
        invisible, multiplier, consecutive_runes, game_over_played
    gold = 0
    lives = 10
    rune_speed = 3
    base_speed = 6
    player_speed = 6
    max_runes = 1
    shield = invisible = False
    player.x = WIDTH // 2
    runes = [spawn_rune()]
    multiplier = 1
    consecutive_runes = 0
    game_over_played = False
    if to_menu:
        game_state = HERO_SELECT
    else:
        player_image = original_player_img
        game_state = PLAYING


def draw_gold_button(rect, text):
    global last_hovered_button

    if rect.collidepoint((mx, my)):
        if last_hovered_button != text:
            sounds["button_hover"].play()
            last_hovered_button = text
    else:
        if last_hovered_button == text:
            last_hovered_button = None

    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    if rect.collidepoint((mx, my)):
        panel.fill((120, 70, 20, 200))

        pygame.draw.rect(panel, (255, 170, 80), panel.get_rect(), 2, border_radius=6)

        glow = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
        pygame.draw.rect(glow, (255, 120, 40, 80), glow.get_rect(), border_radius=8)
        screen.blit(glow, (rect.x - 4, rect.y - 4))

    else:
        panel.fill((30, 20, 10, 200))
        pygame.draw.rect(panel, (200, 150, 80), panel.get_rect(), 2, border_radius=6)

    screen.blit(panel, rect.topleft)

    txt = font.render(text, True, (255,255,255))
    screen.blit(txt, (rect.centerx - txt.get_width()//2,
                      rect.centery - txt.get_height()//2))


def draw_text_outline(surface, text, font, x, y, text_color, outline_color=(0,0,0)):
    base = font.render(text, True, text_color)
    outline = font.render(text, True, outline_color)

    for dx in (-2, -1, 1, 2):
        for dy in (-2, -1, 1, 2):
            surface.blit(outline, (x + dx, y + dy))

    surface.blit(base, (x, y))


def draw_hero_story():

    lines = hero_stories.get(selected_hero, ["No story yet."])

    panel_x = 20
    panel_width = 380
    start_y = 40
    line_height = 30

    y = start_y

    for line in lines:

        words = line.split(" ")
        current_line = ""

        for word in words:

            test_line = current_line + word + " "
            test_surface = story_font.render(test_line, True, (255, 255, 255))

            if test_surface.get_width() > panel_width:

                draw_text_outline(
                    screen,
                    current_line,
                    story_font,
                    panel_x,
                    y,
                    (230, 220, 180),
                    (0, 0, 0)
                )

                y += line_height
                current_line = word + " "

            else:
                current_line = test_line

        draw_text_outline(
            screen,
            current_line,
            story_font,
            panel_x,
            y,
            (230, 220, 180),
            (0, 0, 0)
        )

        y += line_height


running = True

play_music("sounds/main_menu.ogg")

while running:

    mx, my = pygame.mouse.get_pos()

    #FPS
    fps = int(clock.get_fps())
    screen.blit(font.render(f"FPS: {fps}", True, (255, 255, 255)), (10, 70))

    if game_state == MAIN_MENU:
        screen.blit(main_menu_bg, (0, 0))

        draw_gold_button(how_to_play_btn, "HOW TO PLAY")
        draw_gold_button(choose_hero_btn, "CHOOSE HERO")

    if game_state == HOW_TO_PLAY:

        start_x = 60
        start_y = 130
        line_gap = 60
        icon_size = 48

        screen.blit(how_to_play_bg, (0, 0))

        back_btn_top = pygame.Rect(40, 40, 120, 45)
        draw_gold_button(back_btn_top, "BACK")

        y = start_y

        for rtype, text in rune_data.items():
            icon = rune_images[rtype]

            icon_scaled = pygame.transform.smoothscale(icon, (icon_size, icon_size))
            screen.blit(icon_scaled, (start_x, y))

            draw_text_outline(
                screen,
                text,
                font,
                start_x + icon_size + 15,
                y + 10,
                (240, 240, 240)
            )

            y += line_gap

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == STORY and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                reset_game(False)

        if event.type == pygame.MOUSEBUTTONDOWN:

            if game_state == MAIN_MENU:

                if how_to_play_btn.collidepoint(event.pos):
                    game_state = HOW_TO_PLAY
                    play_music("sounds/main_menu.ogg")

                if choose_hero_btn.collidepoint(event.pos):
                    game_state = HERO_SELECT
                    play_music("sounds/hero_select.wav")

            if game_state == HOW_TO_PLAY:
                screen.blit(how_to_play_bg, (0, 0))

                pygame.draw.rect(screen, (50, 50, 50), back_btn, border_radius=8)
                screen.blit(font.render("Back", True, (255, 255, 255)), (back_btn.x + 25, back_btn.y + 12))


            if game_state == HOW_TO_PLAY and event.type == pygame.MOUSEBUTTONDOWN:

                if back_btn.collidepoint(event.pos):
                    game_state = MAIN_MENU
                    play_music("sounds/main_menu.ogg")


        if game_state == HERO_SELECT and event.type == pygame.MOUSEBUTTONDOWN:

            back_btn_bottom = pygame.Rect(WIDTH // 2 - 130, HEIGHT - 80, 260, 45)

            if back_btn_bottom.collidepoint(event.pos):
                game_state = MAIN_MENU
                play_music("sounds/main_menu.ogg")

            cols = 3

            for i, name in enumerate(HEROES.keys()):
                col, row = i % cols, i // cols
                rect = pygame.Rect(100 + (col * 280), 140 + (row * 55), 260, 45)
                if rect.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    sounds["hero_select"].play()
                    original_player_img = hero_full[name]
                    player_image = original_player_img

                    player = player_image.get_rect()
                    player.centerx = WIDTH // 2
                    player.bottom = HEIGHT - 10

                    player_mask = pygame.mask.from_surface(player_image)

                    selected_hero = name
                    hero_story_bg = pygame.image.load(
                        resource_path(f"pics/{name.lower().replace(' ', '_')}_story.png")
                    ).convert()

                    hero_story_bg = pygame.transform.scale(hero_story_bg, (WIDTH, HEIGHT))

                    game_state = HERO_STORY

        if game_state == HERO_STORY and event.type == pygame.MOUSEBUTTONDOWN:

            if hero_story_back_btn.collidepoint(event.pos):
                game_state = HERO_SELECT

            elif hero_story_play_btn.collidepoint(event.pos):
                endless_mode = False
                game_state = PLAYING

            elif hero_story_endless_btn.collidepoint(event.pos):
                endless_mode = True
                game_state = PLAYING

        if game_state == GAME_OVER and event.type == pygame.MOUSEBUTTONDOWN:
            if retry_btn.collidepoint(event.pos): reset_game(False)
            if menu_btn.collidepoint(event.pos): reset_game(True)

    if game_state == HERO_SELECT:
        screen.blit(hero_select, (0, 0))
        screen.blit(menu_overlay, (0, 0))
        title = title_font.render("CHOOSE YOUR HERO", True, (255, 180, 60))
        shadow = title_font.render("CHOOSE YOUR HERO", True, (0, 0, 0))

        screen.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 4, 44))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        cols = 3

        if random.random() < 0.2:
            spawn_ember()

        for e in embers[:]:
            e["y"] += e["speed"]

            if e["y"] > HEIGHT:
                embers.remove(e)

        for i, name in enumerate(HEROES.keys()):
            col, row = i % cols, i // cols
            btn_rect = pygame.Rect(100 + (col * 280), 140 + (row * 55), 260, 45)

            # Hero select buttons
            panel = pygame.Surface((btn_rect.width, btn_rect.height), pygame.SRCALPHA)

            if btn_rect.collidepoint((mx, my)):
                panel.fill((120, 70, 20, 200))

                if last_hovered_hero != name:
                    sounds["button_hover"].play()
                    last_hovered_hero = name
            else:
                panel.fill((20, 20, 20, 180))
                if last_hovered_hero == name:
                    last_hovered_hero = None

            screen.blit(panel, btn_rect.topleft)

            pygame.draw.rect(screen, (200, 150, 80), btn_rect, 2, border_radius=6)

            if btn_rect.collidepoint((mx, my)):
                glow = pygame.Surface((btn_rect.width + 8, btn_rect.height + 8), pygame.SRCALPHA)
                pygame.draw.rect(glow, (255, 120, 40, 80), glow.get_rect(), border_radius=8)
                screen.blit(glow, (btn_rect.x - 4, btn_rect.y - 4))

            # Draw Preview Icon
            screen.blit(hero_icons[name], (btn_rect.x + 5, btn_rect.y + 2))
            # Draw Name
            txt = font.render(name, True, (255, 255, 255))
            screen.blit(txt, (btn_rect.x + 55, btn_rect.centery - txt.get_height() // 2))

            for e in embers:
                pygame.draw.circle(screen, (255, 120, 40), (int(e["x"]), int(e["y"])), e["size"])

        back_btn_bottom = pygame.Rect(WIDTH // 2 - 130, HEIGHT - 80, 260, 45)
        draw_gold_button(back_btn_bottom, "BACK")

    if game_state == HERO_STORY:

        screen.blit(hero_story_bg, (0, 0))

        title = title_font.render(selected_hero, True, (255, 180, 60))

        draw_text_outline(
            screen,
            selected_hero,
            title_font,
            420,
            10,
            (255, 180, 60),
            (0, 0, 0)
        )

        draw_hero_story()

        hero_story_back_btn = pygame.Rect(WIDTH // 2 - 130, HEIGHT - 80, 260, 45)
        hero_story_play_btn = pygame.Rect(WIDTH - 300, HEIGHT - 80, 260, 45)
        hero_story_endless_btn = pygame.Rect(40, HEIGHT - 80, 260, 45)

        draw_gold_button(hero_story_back_btn, "BACK")
        draw_gold_button(hero_story_play_btn, "PLAY")
        draw_gold_button(hero_story_endless_btn, "ENDLESS")




    elif game_state in [PLAYING, GAME_OVER]:
        # --- Gameplay Logic ---
        if game_state == PLAYING:
            sounds["hero_select"].stop()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player.left > 0: player.x -= player_speed
            if keys[pygame.K_RIGHT] and player.right < WIDTH: player.x += player_speed

            hero_bg = hero_backgrounds.get(selected_hero)

            # boss spawn logic
            if gold >= 12000 and not current_boss and not endless_mode:

                if not boss_defeated["cave_guardians"]:
                    boss = CaveGuardians
                elif not boss_defeated["lava_elemental"]:
                    boss = LavaElemental
                elif not boss_defeated["roshan"]:
                    boss = Roshan

                else:
                    boss = None

                if boss:
                    player_speed = base_speed
                    lives = max_lives
                    current_boss = boss(screen, resource_path, rune_images, sounds, player, player_mask, player_image)
                    game_state = BOSS_FIGHT

            if hero_bg:
                screen.blit(hero_bg, (0, 0))
            else:
                screen.fill((30, 30, 40))

            for rune in runes: rune["rect"].y += rune_speed
            for rune in runes[:]:
                offset = (rune["rect"].x - player.x, rune["rect"].y - player.y)

                if player.colliderect(rune["rect"]):
                    if player_mask.overlap(rune["mask"], offset):
                        rtype = rune["type"]

                        if rtype == "normal":
                            gold += 50 * multiplier
                            sounds["pickup"].play()
                            consecutive_runes += 1
                            update_multiplier()
                            if multiplier == 1:
                                add_floating_text("+50", rune["rect"].centerx, rune["rect"].centery)
                            else:
                                add_floating_text(f"+{50 * multiplier}", rune["rect"].centerx, rune["rect"].centery)
                                add_floating_text(f"x{multiplier}!!!", player.x, HEIGHT - 120, (220, 220, 220))

                        elif rtype == "dd":
                            gold += 100 * multiplier
                            sounds["pickup"].play()
                            consecutive_runes += 1
                            update_multiplier()
                            if multiplier == 1:
                                add_floating_text("+100", rune["rect"].centerx, rune["rect"].centery)
                            else:
                                add_floating_text(f"+{100 * multiplier}", rune["rect"].centerx, rune["rect"].centery)
                                add_floating_text(f"x{multiplier}!!!", player.x, HEIGHT - 120, (220, 220, 220))

                        elif rtype == "haste":
                            sounds["haste"].play()
                            player_speed = base_speed * 2
                            haste_timer = pygame.time.get_ticks()

                        elif rtype == "regen":
                            if lives < max_lives:
                                if lives + 3 <= max_lives:
                                    sounds["regen"].play()
                                    lives += 3
                                    add_floating_text(f"+3 HP", rune["rect"].centerx, rune["rect"].centery, (80, 255, 120))
                                else:
                                    missing_lives = max_lives - lives
                                    lives = max_lives
                                    sounds["regen"].play()
                                    add_floating_text(f"+{missing_lives} HP", rune["rect"].centerx, rune["rect"].centery,
                                                      (80, 255, 120))
                            else:
                                sounds["miss"].play()


                        elif rtype == "creep":
                            if shield:
                                sounds["block"].play()
                                shield = False
                            else:
                                lives -= 1
                                sounds["damage"].play()
                                damage_flash_alpha = 150
                                consecutive_runes = 0
                                update_multiplier()
                                shake_timer = 10
                                shake_strength = 6
                                add_floating_text("-1 HP", rune["rect"].centerx, rune["rect"].centery, (255, 80, 80))

                        elif rtype == "hex":
                            sounds["hex"].play()
                            consecutive_runes = 0
                            update_multiplier()
                            player_speed = base_speed // 2
                            player_image = frog_img
                            hex_timer = pygame.time.get_ticks()

                        elif rtype == "water":
                            if lives < max_lives:
                                lives += 1
                                sounds["water"].play()
                                add_floating_text("+1 HP", rune["rect"].centerx, rune["rect"].centery, (80, 200, 255))
                            else:
                                sounds["miss"].play()

                        elif rtype == "shield":
                            sounds["shield"].play()
                            shield = True

                        elif rtype == "invisible":
                            sounds["invisible"].play()
                            consecutive_runes = 0
                            update_multiplier()
                            invisible = True
                            invisible_timer = pygame.time.get_ticks()

                        runes.remove(rune)
                        continue

                if rune["rect"].top > HEIGHT:

                    if rune["type"] in ["normal", "dd"]:
                        if shield:
                            sounds["block"].play()
                            shield = False
                        else:
                            lives -= 1
                            sounds["damage"].play()
                            damage_flash_alpha = 150
                            consecutive_runes = 0
                            update_multiplier()
                            shake_timer = 10
                            shake_strength = 6
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

                if gold >= 3000:
                    max_runes = 3

                if gold >= 6000:
                    max_runes = 4

                if gold >= 300 and rune_speed == 3:
                    rune_speed += 1
                    base_speed += 1
                    player_speed = base_speed

                if gold >= 700 and rune_speed == 4:
                    rune_speed += 1
                    base_speed += 1
                    player_speed = base_speed

                if gold >= 1500 and rune_speed == 5:
                    rune_speed += 1
                    base_speed += 1
                    player_speed = base_speed

                if gold >= 4000 and rune_speed == 6:
                    rune_speed += 1
                    base_speed += 1
                    player_speed = base_speed

                if gold >= 7000 and rune_speed == 7:
                    rune_speed += 1
                    base_speed += 1
                    player_speed = base_speed

                if gold >= 10000 and rune_speed == 8:
                    rune_speed += 1

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

            if lives <= 0:
                if aegis:
                    aegis = False
                    lives = max_lives
                else:
                    game_state = GAME_OVER

            if damage_flash_alpha > 0:
                damage_flash_alpha -= 15
                damage_flash.set_alpha(damage_flash_alpha)

        # --- Rendering ---

        offset_x = offset_y = 0

        for r in runes:
            screen.blit(rune_images[r["type"]], r["rect"])

        if shake_timer > 0:
            offset_x = random.randint(-shake_strength, shake_strength)
            offset_y = random.randint(-shake_strength, shake_strength)
            shake_timer -= 1

        for ft in floating_texts:
            text_surface = font.render(ft["text"], True, ft["color"])
            screen.blit(text_surface, (ft["x"], ft["y"]))

        # UI

        #FPS
        fps = int(clock.get_fps())
        screen.blit(font.render(f"FPS: {fps}", True, (255, 255, 255)), (10, 70))

        screen.blit(font.render(f"Gold: {gold}", True, (255, 255, 0)), (10, 10))
        screen.blit(heart_img, (WIDTH - 120, 10))
        pygame.draw.line(screen, (120, 120, 120), (WIDTH - 260, 55), (WIDTH - 0, 55), 1)
        screen.blit(font.render(str(lives), True, (255, 255, 255)), (WIDTH - 70, 18))

        screen.blit(font.render(f"Combo: {consecutive_runes}", True, (180, 180, 180)), (10, 40))

        if not invisible:
            screen.blit(player_image, (player.x + offset_x, player.y + offset_y))

        if damage_flash_alpha > 0:
            screen.blit(damage_flash, (0, 0))

        statuses = [
            ("SHIELD", shield, None, 0),
            ("INVIS", invisible, invisible_timer, INVISIBLE_DURATION),
            ("HASTED", haste_timer != 0, haste_timer, 5000),
            ("HEXED", hex_timer != 0, hex_timer, 5000)
        ]

        start_x = WIDTH - 260
        y = 60

        for name, active, timer, duration in statuses:

            color = (220, 220, 220) if active else (90, 90, 90)

            text = status_font.render(name, True, color)
            screen.blit(text, (start_x, y))

            if active and timer:
                remaining = max(0, duration - (pygame.time.get_ticks() - timer))
                seconds = int(remaining / 1000)

                timer_text = status_font.render(str(seconds), True, (255, 200, 120))
                screen.blit(timer_text, (start_x + 10, y + 18))

                glow = status_font.render(name, True, (255, 180, 80))
                screen.blit(glow, (start_x, y))

            start_x += 70

        if game_state == GAME_OVER:

            if not game_over_played:
                sounds["game_over"].play()
                game_over_played = True

            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))
            msg = title_font.render("GAME OVER", True, (255, 50, 50))
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 100))

            for btn, label in [(retry_btn, "RETRY"), (menu_btn, "CHANGE HERO")]:
                pygame.draw.rect(screen, (80, 80, 80), btn, border_radius=5)
                pygame.draw.rect(screen, (200, 200, 200), btn, 2, border_radius=5)
                l_txt = font.render(label, True, (255, 255, 255))
                screen.blit(l_txt, (btn.centerx - l_txt.get_width() // 2, btn.centery - l_txt.get_height() // 2))


    elif game_state == BOSS_FIGHT:

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

        if lives <= 0:
            if aegis:
                aegis = False
                lives = max_lives
            else:
                game_state = GAME_OVER

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= player_speed

        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += player_speed

        result = current_boss.update()

        screen.blit(font.render(f"Gold: {gold}", True, (255, 255, 0)), (10, 10))
        screen.blit(heart_img, (WIDTH - 120, 10))
        pygame.draw.line(screen, (120, 120, 120), (WIDTH - 260, 55), (WIDTH - 0, 55), 1)
        screen.blit(font.render(str(lives), True, (255, 255, 255)), (WIDTH - 70, 18))

        screen.blit(font.render(f"Combo: {consecutive_runes}", True, (180, 180, 180)), (10, 40))

        if not invisible:
            screen.blit(player_image, (player.x + offset_x, player.y + offset_y))

        if damage_flash_alpha > 0:
            screen.blit(damage_flash, (0, 0))

        statuses = [
            ("SHIELD", shield, None, 0),
            ("INVIS", invisible, invisible_timer, INVISIBLE_DURATION),
            ("HASTED", haste_timer != 0, haste_timer, 5000),
            ("HEXED", hex_timer != 0, hex_timer, 5000)
        ]

        start_x = WIDTH - 260
        y = 60

        for name, active, timer, duration in statuses:

            color = (220, 220, 220) if active else (90, 90, 90)

            text = status_font.render(name, True, color)
            screen.blit(text, (start_x, y))

            if active and timer:
                remaining = max(0, duration - (pygame.time.get_ticks() - timer))
                seconds = int(remaining / 1000)

                timer_text = status_font.render(str(seconds), True, (255, 200, 120))
                screen.blit(timer_text, (start_x + 10, y + 18))

                glow = status_font.render(name, True, (255, 180, 80))
                screen.blit(glow, (start_x, y))

            start_x += 70

        if game_state == GAME_OVER:

            if not game_over_played:
                sounds["game_over"].play()
                game_over_played = True

            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))
            msg = title_font.render("GAME OVER", True, (255, 50, 50))
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 100))

            for btn, label in [(retry_btn, "RETRY"), (menu_btn, "CHANGE HERO")]:
                pygame.draw.rect(screen, (80, 80, 80), btn, border_radius=5)
                pygame.draw.rect(screen, (200, 200, 200), btn, 2, border_radius=5)
                l_txt = font.render(label, True, (255, 255, 255))
                screen.blit(l_txt, (btn.centerx - l_txt.get_width() // 2, btn.centery - l_txt.get_height() // 2))

        if isinstance(result, dict):
            if result["damage"] > 0:
                if shield:
                    shield = False
                    sounds["block"].play()
                else:
                    lives -= result["damage"]
                    damage_flash_alpha = 150
                    sounds["damage"].play()

            if result["heal"] > 0:
                lives = min(max_lives, lives + result["heal"])

            if result["haste"]:
                player_speed = base_speed * 2
                haste_timer = pygame.time.get_ticks()

            if result["shield"]: shield = True

            if result["hex"]:
                player_speed = base_speed // 2
                player_image = frog_img
                hex_timer = pygame.time.get_ticks()

            if result["invis"]:
                invisible = True
                invisible_timer = pygame.time.get_ticks()



        elif result == "win":
            defeated_boss = current_boss.name
            reset_game(False)
            boss_defeated[defeated_boss] = True

            # boss bonuses
            if defeated_boss == "cave_guardians":
                base_speed += 1
                player_speed = base_speed
            elif defeated_boss == "lava_elemental":
                max_lives += 2
            elif defeated_boss == "roshan":
                aegis = True

            current_boss = None
            game_state = PLAYING

    elif game_state == STORY:

        screen.blit(story_begin, (0, 0))

        line_height = 25
        total_height = len(story_lines) * line_height
        y = HEIGHT // 2 - total_height // 2

        for line in story_lines:
            if line.strip() == "":
                y += line_height
                continue

            temp_surface = story_font.render(line, True, (0, 0, 0))
            text_x = WIDTH // 2 - temp_surface.get_width() // 2

            draw_text_outline(
                screen,
                line,
                story_font,
                text_x,
                y,
                (240, 240, 240),
                (0, 0, 0),
            )

            y += line_height

        hint_text = "Press SPACE to begin the hunt"
        hint_x = WIDTH // 2 - font.render(hint_text, True, (0, 0, 0)).get_width() // 2
        draw_text_outline(screen, hint_text, font, hint_x, HEIGHT - 80, (180, 180, 180), (0, 0, 0))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()