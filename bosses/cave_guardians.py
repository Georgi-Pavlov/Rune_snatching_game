import pygame
import random

# States
INTRO = 0
FIGHT = 1
OUTRO = 2
DONE = 3


class CaveGuardians:
    def __init__(self, screen, resource_path, rune_images, sounds, player, player_mask, player_img, overlay):
        self.screen = screen
        self.resource_path = resource_path
        self.rune_images = rune_images
        self.sounds = sounds
        self.player = player
        self.player_mask = player_mask
        self.player_img = player_img

        self.WIDTH = 1100
        self.HEIGHT = 750

        self.overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 120))

        # Assets
        self.cave_bg = pygame.image.load(resource_path("pics/cave_entrance_background.png")).convert()
        self.cave_bg = pygame.transform.scale(self.cave_bg, (self.WIDTH, self.HEIGHT))

        self.guardian1_img = pygame.transform.scale(
            pygame.image.load(resource_path("pics/cave_entrance_guardian_1.png")), (190, 190))
        self.guardian2_img = pygame.transform.scale(
            pygame.image.load(resource_path("pics/cave_entrance_guardian_2.png")), (190, 190))

        self.guardian1_rect = self.guardian1_img.get_rect(midtop=(self.WIDTH // 2 - 150, 40))
        self.guardian2_rect = self.guardian2_img.get_rect(midtop=(self.WIDTH // 2 + 150, 40))

        # Stats
        self.guardian1_hp = 20
        self.guardian2_hp = 12
        self.runes = []
        self.runes_caught_for_attack = 0
        self.rune_speed = 7
        self.state = INTRO
        self.timer = pygame.time.get_ticks()
        self.font = pygame.font.SysFont(None, 36)

        # Attack Logic Variables
        self.last_attack_time = pygame.time.get_ticks()
        self.attack_interval = 3000  # Attacks every 3 seconds
        self.attacker_turn = 1  # 1 for Guardian 1, 2 for Guardian 2

        # Animation Variables
        self.g1_offset_y = 0
        self.g2_offset_y = 0

        # UI
        self.floating_texts = []


    def add_floating_text(self, text, x, y, color=(255, 255, 0)):
        self.floating_texts.append({
            "text": text,
            "x": x,
            "y": y,
            "timer": 60,
            "color": color
        })


    def spawn_rune(self):
        types = list(self.rune_images.keys())
        rtype = random.choice(types)
        rect = self.rune_images[rtype].get_rect()
        rect.x = random.randint(0, self.WIDTH - rect.width)
        rect.y = -rect.height
        mask = pygame.mask.from_surface(self.rune_images[rtype])
        return {"type": rtype, "rect": rect, "mask": mask}

    def draw_hp_bar(self, x, y, hp, max_hp):
        width = 120
        pygame.draw.rect(self.screen, (60, 0, 0), (x, y, width, 12))
        if hp > 0:
            fill_width = width * (hp / max_hp)
            pygame.draw.rect(self.screen, (220, 0, 0), (x, y, fill_width, 12))

    def update(self):
        """Returns a dictionary of events to the main game loop."""
        if self.state == INTRO:
            return self.update_intro()
        if self.state == FIGHT:
            return self.fight()
        if self.state == OUTRO:
            return self.update_outro()
        if self.state == DONE:
            return "win"
        return None


    def draw_local_outline(self, text, x, y):
        """Helper to ensure we see text if main function isn't in scope"""
        outline_color = (0, 0, 0)
        main_color = (255, 200, 80)  # Nice gold color for boss intro
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            surf = self.font.render(text, True, outline_color)
            self.screen.blit(surf, (x + dx, y + dy))
        main_surf = self.font.render(text, True, main_color)
        self.screen.blit(main_surf, (x, y))


    def update_intro(self):

        self.screen.blit(self.cave_bg, (0, 0))
        self.screen.blit(self.overlay, (0, 0))

        lines = [
            "The entrance to the cave stands before you.",
            "For centuries the Golden Rune has been hidden here.",
            "Two ancient guardians protect it.",
            "They will not step aside willingly."
        ]

        start_y = self.HEIGHT // 2 - 80
        for i, text in enumerate(lines):
            line_surface = self.font.render(text, True, (0, 0, 0))
            text_x = self.WIDTH // 2 - line_surface.get_width() // 2
            text_y = start_y + (i * 50)

            self.draw_local_outline(text, text_x, text_y)

        if pygame.time.get_ticks() - self.timer > 4000:  # Increased to 4s so player can actually read it!
            self.state = FIGHT
            self.last_attack_time = pygame.time.get_ticks()
        return None


    def fight(self):
        # Dictionary to send updates back to game.py
        events = {"damage": 0, "heal": 0, "haste": False, "shield": False, "hex": False, "invis": False}

        self.screen.blit(self.cave_bg, (0, 0))

        current_time = pygame.time.get_ticks()

        # --- Attack Timer Logic ---
        if current_time - self.last_attack_time > self.attack_interval:
            self.last_attack_time = current_time

            if self.attacker_turn == 1:
                if self.guardian1_hp > 0:
                    events["damage"] = 1
                    self.g1_offset_y = 50  # Lunging down
                self.attacker_turn = 2  # Switch turn
            else:
                if self.guardian2_hp > 0:
                    events["damage"] = 2
                    self.g2_offset_y = 50  # Lunging down
                self.attacker_turn = 1  # Switch turn

        # Smoothly return Guardians to original position (Animation)
        if self.g1_offset_y > 0: self.g1_offset_y -= 2
        if self.g2_offset_y > 0: self.g2_offset_y -= 2

        # Handle Runes
        for rune in self.runes:
            rune["rect"].y += self.rune_speed

        for rune in self.runes[:]:
            offset = (rune["rect"].x - self.player.x, rune["rect"].y - self.player.y)

            if self.player_mask.overlap(rune["mask"], offset):
                rtype = rune["type"]

                # Attack Logic
                if rtype in ["normal", "dd"]:
                    self.sounds["pickup"].play()
                    self.runes_caught_for_attack += 1

                    if self.runes_caught_for_attack % 4 == 0:
                        dmg = 3
                        # Add floating damage text over the boss
                        dmg_text = f"-{dmg} HP"
                        # Target Guardian 1 if he's alive, otherwise Guardian 2
                        target_x = self.guardian1_rect.centerx if self.guardian1_hp > 0 else self.guardian2_rect.centerx
                        self.add_floating_text(dmg_text, target_x, 100, (255, 100, 100))
                    else:
                        dmg = 1
                        # Add floating damage text over the boss
                        dmg_text = f"-{dmg} HP"
                        # Target Guardian 1 if he's alive, otherwise Guardian 2
                        target_x = self.guardian1_rect.centerx if self.guardian1_hp > 0 else self.guardian2_rect.centerx
                        self.add_floating_text(dmg_text, target_x, 100, (255, 100, 100))

                    if self.guardian1_hp > 0:
                        self.guardian1_hp -= dmg
                    else:
                        self.guardian2_hp -= dmg

                # Player Status Effects (Sent to game.py)
                elif rtype == "haste":
                    events["haste"] = True
                    self.sounds["haste"].play()
                elif rtype == "regen":
                    events["heal"] = 3
                    self.add_floating_text("+3 HP", self.player.x, self.player.y - 40, (80, 255, 120))
                    self.sounds["regen"].play()
                elif rtype == "water":
                    events["heal"] = 1
                    self.add_floating_text("+1 HP", self.player.x, self.player.y - 40, (80, 200, 255))
                    self.sounds["water"].play()
                elif rtype == "shield":
                    events["shield"] = True
                    self.sounds["shield"].play()
                elif rtype == "hex":
                    events["hex"] = True
                    self.sounds["hex"].play()
                    self.runes_caught_for_attack = 0
                elif rtype == "invisible":
                    events["invis"] = True
                    self.sounds["invisible"].play()
                    self.runes_caught_for_attack = 0
                elif rtype == "creep":
                    events["damage"] = 1
                    self.add_floating_text("-1 HP", self.player.x, self.player.y - 40, (255, 50, 50))
                    self.sounds["damage"].play()
                    self.runes_caught_for_attack = 0

                self.runes.remove(rune)

            elif rune["rect"].top > self.HEIGHT:
                if rune["type"] in ["normal", "dd"]:
                    events["damage"] = 1
                    self.add_floating_text("-1 HP", self.player.x, self.player.y - 40, (255, 50, 50))
                    self.sounds["damage"].play()
                    self.runes_caught_for_attack = 0
                self.runes.remove(rune)

        while len(self.runes) < 4:
            self.runes.append(self.spawn_rune())

        # Draw Bosses
        if self.guardian1_hp > 0:
            # Use a temporary position for the attack lunging animation
            g1_pos = (self.guardian1_rect.x, self.guardian1_rect.y + self.g1_offset_y)
            self.screen.blit(self.guardian1_img, g1_pos)
            # Move the HP bar with the boss so it doesn't look detached
            self.draw_hp_bar(self.guardian1_rect.x, self.guardian1_rect.bottom + self.g1_offset_y + 5,
                             self.guardian1_hp, 20)

        if self.guardian2_hp > 0:
            # Same here for Guardian 2
            g2_pos = (self.guardian2_rect.x, self.guardian2_rect.y + self.g2_offset_y)
            self.screen.blit(self.guardian2_img, g2_pos)
            self.draw_hp_bar(self.guardian2_rect.x, self.guardian2_rect.bottom + self.g2_offset_y + 5,
                             self.guardian2_hp, 12)

        # Draw Runes
        for r in self.runes:
            self.screen.blit(self.rune_images[r["type"]], r["rect"])

        if self.guardian1_hp <= 0 and self.guardian2_hp <= 0:
            self.state = OUTRO
            self.timer = pygame.time.get_ticks()

        for ft in self.floating_texts[:]:
            ft["y"] -= 1
            ft["timer"] -= 1

            # Draw the text
            text_surf = self.font.render(ft["text"], True, ft["color"])
            self.screen.blit(text_surf, (ft["x"], ft["y"]))

            if ft["timer"] <= 0:
                self.floating_texts.remove(ft)

        return events

    def update_outro(self):
        self.screen.blit(self.cave_bg, (0, 0))

        t1 = self.font.render("The guardians fall.", True, (200, 200, 200))
        t2 = self.font.render("The path into the cave is now open.", True, (200, 200, 200))
        t3 = self.font.render("You feel the adrenaline rush from the battle.", True, (200, 200, 200))
        t4 = self.font.render("You are now alert for any danger! (+1 speed)", True, (200, 200, 200))

        # Calculate positions (Centered X, incremented Y)
        center_x = self.WIDTH // 2
        start_y = self.HEIGHT // 2 - 80  # starting point

        self.screen.blit(t1, (center_x - t1.get_width() // 2, start_y))
        self.screen.blit(t2, (center_x - t2.get_width() // 2, start_y + 50))
        self.screen.blit(t3, (center_x - t3.get_width() // 2, start_y + 100))
        self.screen.blit(t4, (center_x - t4.get_width() // 2, start_y + 150))

        if pygame.time.get_ticks() - self.timer > 3000:
            self.state = DONE
        return None