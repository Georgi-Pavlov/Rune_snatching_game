import pygame
import random

# States
INTRO = 0
FIGHT = 1
OUTRO = 2
DONE = 3


class CaveGuardians:
    def __init__(self, screen, resource_path, rune_images, sounds, player, player_mask, player_img, hero_stats):
        self.screen = screen
        self.resource_path = resource_path
        self.rune_images = rune_images
        self.sounds = sounds
        self.player = player
        self.player_mask = player_mask
        self.player_img = player_img
        self.name = "cave_guardians"

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
        self.rune_speed = 7
        self.state = INTRO
        self.timer = pygame.time.get_ticks()
        self.font = pygame.font.SysFont(None, 36)

        # Attack Logic Variables
        self.last_attack_time = pygame.time.get_ticks()
        self.attack_interval = self.base_attack_interval = 3000  # Attacks every 3 seconds
        self.attacker_turn = 1  # 1 for Guardian 1, 2 for Guardian 2

        # Animation Variables
        self.g1_offset_y = 0
        self.g2_offset_y = 0

        # UI
        self.floating_texts = []

        # music
        self.intro_music_played = False
        self.outro_music_played = False

        # hero stats
        self.hero_stats = hero_stats
        self.game_state = {
            "effects": [],
            "player_buffs": [],
            "ultimate_charges": 0
        }
        self.player_rune_shield = False


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
        """Helper to ensure text is visible"""
        outline_color = (0, 0, 0)
        main_color = (255, 200, 80)  # Nice gold color for boss intro
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            surf = self.font.render(text, True, outline_color)
            self.screen.blit(surf, (x + dx, y + dy))
        main_surf = self.font.render(text, True, main_color)
        self.screen.blit(main_surf, (x, y))


    def get_player_damage(self):
        dmg_config = self.hero_stats.get("dmg_vs_boss", {"type": "hit", "value": 1})

        if dmg_config["type"] == "hit":
            dmg = dmg_config["value"]

        elif dmg_config["type"] == "crit":
            import random
            if random.random() < dmg_config["chance"]:
                dmg = dmg_config["crit"]
            else:
                dmg = dmg_config["base"]

        else:
            dmg = 1

        # buffs от ultimate
        for buff in self.game_state["player_buffs"][:]:
            if buff["type"] == "attack_buff":
                dmg += buff["bonus_damage"]
                buff["attacks"] -= 1

                if buff["attacks"] <= 0:
                    self.game_state["player_buffs"].remove(buff)

        for effect in self.game_state["effects"]:
            if effect["type"] == "damage_amp":
                dmg += effect["bonus"]

        return dmg

    def get_ultimate_damage(self, dmg_cfg):
        if dmg_cfg["type"] == "hit":
            return dmg_cfg["value"]
        return 0


    def activate_ultimate(self):
        ult = self.hero_stats.get("on_ultimate")

        if not ult:
            return

        # DAMAGE
        dmg_cfg = ult.get("damage")
        if dmg_cfg:
            dmg = self.get_ultimate_damage(dmg_cfg)
            self.apply_damage_to_boss(dmg)

        # EFFECT
        effect = ult.get("effect")
        if effect:
            e = effect.copy()
            now = pygame.time.get_ticks()
            e["expires_at"] = now + effect.get("duration", 0)
            e["last_tick"] = now

            if e["type"] in ["attack_buff"]:
                self.game_state["player_buffs"].append(e)
            elif effect["type"] == "heal":
                self.add_floating_text(f"+{effect['value']} HP", self.player.x, self.player.y - 40, (80, 255, 120))
                return {"heal": effect["value"]}
            else:
                self.game_state["effects"].append(e)

    def apply_damage_to_boss(self, dmg):
        target_x = self.guardian1_rect.centerx if self.guardian1_hp > 0 else self.guardian2_rect.centerx

        self.add_floating_text(f"-{dmg} HP", target_x, 100, (255, 100, 100))

        if self.guardian1_hp > 0:
            self.guardian1_hp -= dmg
        else:
            self.guardian2_hp -= dmg


    def update_effects(self):
        target_x = self.guardian1_rect.centerx if self.guardian1_hp > 0 else self.guardian2_rect.centerx
        current_time = pygame.time.get_ticks()

        for effect in self.game_state["effects"][:]:
            etype = effect["type"]

            # --- DAMAGE OVER TIME ---
            if etype == "dot":
                subtype = effect.get("subtype", "default")
                if current_time - effect.get("last_tick", 0) > 1000:
                    self.apply_damage_to_boss(effect["tick_damage"])

                    if subtype == "poison":
                        self.add_floating_text("Poison!", target_x, 120, (100, 255, 100))
                    elif subtype == "burn":
                        self.add_floating_text("Burning!", target_x, 120, (255, 80, 50))
                    elif subtype == "curse":
                        self.add_floating_text("Cursed!", target_x, 120, (180, 80, 255))
                    else:
                        self.add_floating_text(f"-{effect['tick_damage']}", target_x, 120)

                    effect["last_tick"] = current_time

            # SHIELD
            elif etype == "shield":
                if not effect.get("applied"):
                    effect["applied"] = True
                    self.add_floating_text("Shield Up!", self.player.x, self.player.y - 40, (100, 200, 255))

            # IMMUNE
            elif etype == "creep_immunity":
                if not effect.get("applied"):
                    effect["applied"] = True
                    self.add_floating_text("Immune!", self.player.x, self.player.y - 40, (200, 200, 255))

            # LIFEDRAIN
            elif etype == "lifedrain":
                if current_time - effect.get("last_tick", 0) > 1000:
                    effect["last_tick"] = current_time

                    # heal player
                    self.add_floating_text("+1 HP", self.player.x, self.player.y - 40, (100, 255, 100))

                    # damage boss
                    self.apply_damage_to_boss(1)

            # --- FREEZE ---
            elif etype == "freeze":
                if not effect.get("applied"):
                    effect["applied"] = True
                    self.add_floating_text("Frozen!", target_x, 60, (150, 200, 255))

            # --- SLOW ---
            elif etype == "boss_slow":
                if not effect.get("applied"):
                    total_slow = sum(e["attack_delay"] for e in self.game_state["effects"] if e["type"] == "boss_slow")
                    self.attack_interval = self.base_attack_interval + total_slow
                    effect["applied"] = True
                    self.add_floating_text("Slowed!", target_x, 60, (150, 200, 255))

            # --- EXPIRE ---
            if current_time >= effect["expires_at"]:
                if etype == "boss_slow":
                    self.attack_interval -= effect["attack_delay"]
                self.game_state["effects"].remove(effect)


    def update_intro(self):

        self.screen.blit(self.cave_bg, (0, 0))
        self.screen.blit(self.overlay, (0, 0))

        if not self.intro_music_played:
            self.sounds["cave_entrance_intro"].play()
            self.intro_music_played = True

        lines = [
            "The entrance to the cave stands before you.",
            "For centuries the Golden Rune has been hidden here.",
            "Two ancient guardians protect it.",
            "They will not step aside willingly."
        ]

        start_y = self.HEIGHT // 2 - 140
        line_spacing = 50
        elapsed = pygame.time.get_ticks() - self.timer
        for i, text in enumerate(lines):
            if elapsed > i * 900:
                line_surface = self.font.render(text, True, (255, 220, 150))
                text_x = self.WIDTH // 2 - line_surface.get_width() // 2
                text_y = start_y + (i * line_spacing)

                self.draw_local_outline(text, text_x, text_y)


        if pygame.time.get_ticks() - self.timer > 4500:  # Increased to 4s so player can actually read it!
            self.sounds["cave_entrance_intro"].stop()
            self.state = FIGHT
            self.last_attack_time = pygame.time.get_ticks()
        return None


    def fight(self):
        # Dictionary to send updates back to game.py
        events = {"damage": 0, "heal": 0, "haste": False, "shield": False, "hex": False, "invis": False}

        self.update_effects()

        self.screen.blit(self.cave_bg, (0, 0))

        current_time = pygame.time.get_ticks()

        # --- Attack Timer Logic ---
        is_frozen = any(e["type"] == "freeze" for e in self.game_state["effects"])
        if not is_frozen and current_time - self.last_attack_time > self.attack_interval:
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

        # boss attack nerf and dmg return
        for effect in self.game_state["effects"][:]:
            if effect["type"] == "boss_attack_nerf":
                events["damage"] *= effect["damage_multiplier"]

                effect["attacks"] -= 1
                if effect.get("reflect_damage", 0):
                    self.apply_damage_to_boss(effect["reflect_damage"])

                if effect["attacks"] <= 0:
                    self.game_state["effects"].remove(effect)

        # Handle Runes
        for rune in self.runes:
            rune["rect"].y += self.rune_speed

        for rune in self.runes[:]:
            offset = (rune["rect"].x - self.player.x, rune["rect"].y - self.player.y)

            if self.player_mask.overlap(rune["mask"], offset):
                rtype = rune["type"]

                # Attack Logic
                if rtype in ["normal", "dd"]:
                    self.sounds["cave_entrance_guardian"].play()
                    self.game_state["ultimate_charges"] += 1

                    if "ultimate_cost" in self.hero_stats and \
                            self.game_state["ultimate_charges"] >= self.hero_stats["ultimate_cost"]:
                        self.activate_ultimate()
                        self.game_state["ultimate_charges"] = 0

                    base_damage = self.get_player_damage()
                    dmg = base_damage

                    self.apply_damage_to_boss(dmg)

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
                    self.player_rune_shield = True
                    self.sounds["shield"].play()
                elif rtype == "hex":
                    events["hex"] = True
                    self.sounds["hex"].play()

                elif rtype == "invisible":
                    events["invis"] = True
                    self.sounds["invisible"].play()

                elif rtype == "creep":
                    timed_shield = next((e for e in self.game_state["effects"]
                                         if e["type"] == "shield" and e.get("subtype") == "timed"), None)

                    if any(e["type"] == "creep_immunity" for e in self.game_state["effects"]):
                        pass

                    elif timed_shield:
                        self.add_floating_text("Shielded!", self.player.x, self.player.y - 40, (100, 200, 255))
                        # dont remove shield


                    elif self.player_rune_shield:
                        self.player_rune_shield = False
                        self.add_floating_text("Blocked!", self.player.x, self.player.y - 40, (100, 200, 255))
                    else:
                        events["damage"] = 1
                        self.add_floating_text("-1 HP", self.player.x, self.player.y - 40, (255, 50, 50))
                        self.sounds["damage"].play()

                self.runes.remove(rune)

            elif rune["rect"].top > self.HEIGHT:
                if rune["type"] in ["normal", "dd"]:
                    events["damage"] = 1
                    self.add_floating_text("-1 HP", self.player.x, self.player.y - 40, (255, 50, 50))
                    self.sounds["damage"].play()

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
        self.screen.blit(self.overlay, (0, 0))

        if not self.outro_music_played:
            self.sounds["boss_win"].play()
            self.outro_music_played = True

        lines = [
            "The guardians fall.",
            "The path into the cave is now open.",
            "You feel the adrenaline rush from the battle.",
            "You are now alert for any danger! (+1 speed)"
        ]

        start_y = self.HEIGHT // 2 - 100
        line_spacing = 60
        elapsed = pygame.time.get_ticks() - self.timer
        for i, text in enumerate(lines):
            if elapsed > i * 900:
                line_surface = self.font.render(text, True, (255, 220, 150))
                text_x = self.WIDTH // 2 - line_surface.get_width() // 2
                text_y = start_y + (i * line_spacing)

                self.draw_local_outline(text, text_x, text_y)


        if pygame.time.get_ticks() - self.timer > 4500:
            self.sounds["boss_win"].stop()
            self.state = DONE
        return None