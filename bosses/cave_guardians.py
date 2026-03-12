import pygame
import random

class CaveGuardians:

    def __init__(self, game):

        self.game = game

        self.guardian1_hp = 10
        self.guardian2_hp = 7

        self.guardian1_rect = game.guardian1_rect
        self.guardian2_rect = game.guardian2_rect

        self.runes_caught_for_attack = 0
        self.guardian_attack_counter = 0
        self.guardian_turn = 0


    def add_floating_text(text, x, y, color=(255, 255, 0)):
        floating_texts.append({
            "text": text,
            "x": x,
            "y": y,
            "timer": 60,
            "color": color
        })


    def update(self):
        game = self.game

        for rune in game.runes:
            rune["rect"].y += 6

            if rune["rect"].top > HEIGHT:
                runes.remove(rune)

            offset = (rune["rect"].x - player.x, rune["rect"].y - player.y)

            if player_mask.overlap(rune["mask"], offset):

                rtype = rune["type"]

                # --- ATTACK RUNES ---
                if rtype in ["normal", "dd"]:

                    runes_caught_for_attack += 1
                    guardian_attack_counter += 1

                    damage = 1

                    if runes_caught_for_attack == 5:
                        damage = 4
                        runes_caught_for_attack = 0
                        add_floating_text("ULTIMATE!", player.x + 40, player.y - 30, (255, 180, 80))

                    if guardian1_hp > 0:
                        guardian1_hp -= damage
                    else:
                        guardian2_hp -= damage


                # --- HASTE ---
                elif rtype == "haste":
                    sounds["haste"].play()
                    player_speed = base_speed * 2
                    haste_timer = pygame.time.get_ticks()


                # --- REGEN ---
                elif rtype == "regen":

                    if lives < max_lives:
                        heal = min(3, max_lives - lives)
                        lives += heal
                        sounds["regen"].play()
                        add_floating_text(f"+{heal} HP", rune["rect"].centerx, rune["rect"].centery, (80, 255, 120))
                    else:
                        sounds["miss"].play()


                # --- WATER ---
                elif rtype == "water":

                    if lives < max_lives:
                        lives += 1
                        sounds["water"].play()
                        add_floating_text("+1 HP", rune["rect"].centerx, rune["rect"].centery, (80, 200, 255))
                    else:
                        sounds["miss"].play()


                # --- SHIELD ---
                elif rtype == "shield":
                    sounds["shield"].play()
                    shield = True


                # --- HEX ---
                elif rtype == "hex":
                    sounds["hex"].play()
                    player_speed = base_speed // 2
                    player_image = frog_img
                    hex_timer = pygame.time.get_ticks()


                # --- INVIS ---
                elif rtype == "invisible":
                    sounds["invisible"].play()
                    invisible = True
                    invisible_timer = pygame.time.get_ticks()


                # --- CREEP ---
                elif rtype == "creep":

                    if shield:
                        sounds["block"].play()
                        shield = False
                    else:
                        lives -= 1
                        sounds["damage"].play()
                        damage_flash_alpha = 150
                        shake_timer = 10
                        shake_strength = 6
                        add_floating_text("-1 HP", rune["rect"].centerx, rune["rect"].centery, (255, 80, 80))

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

            for ft in floating_texts[:]:
                ft["y"] -= 1
                ft["timer"] -= 1

                if ft["timer"] <= 0:
                    floating_texts.remove(ft)

        if guardian_attack_counter >= 3:

            guardian_attack_counter = 0
            guardian_turn += 1

            if guardian_turn % 2 == 1:
                dmg = 1
            else:
                dmg = 2

            if shield:
                sounds["block"].play()
                shield = False
            else:
                lives -= dmg
                sounds["damage"].play()
                add_floating_text(f"-{dmg} HP", player.x + 40, player.y, (255, 80, 80))

        while len(runes) < 2:
            runes.append(spawn_rune())

        for r in runes:
            screen.blit(rune_images[r["type"]], r["rect"])

    def draw(self):

        game = self.game
        screen = game.screen

        screen.blit(game.cave_bg, (0, 0))

        screen.blit(game.guardian1_img, self.guardian1_rect)
        screen.blit(game.guardian2_img, self.guardian2_rect)

        game.draw_hp_bar(self.guardian1_rect.x,
                         self.guardian1_rect.bottom + 5,
                         self.guardian1_hp, 10)

        game.draw_hp_bar(self.guardian2_rect.x,
                         self.guardian2_rect.bottom + 5,
                         self.guardian2_hp, 7)