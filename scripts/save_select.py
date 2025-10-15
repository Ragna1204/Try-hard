import pygame
import sys
import math
import random
import json
import os
from scripts.shared_background import SharedBackground
from scripts.utils import resource_path

pygame.init()
pygame.mixer.init()


class SaveSelect:
    def __init__(self, screen, clock, assets, sfx, shared_background=None):
        self.screen = screen
        self.clock = clock
        self.assets = assets
        self.sfx = sfx

        self.title_font = pygame.font.Font(resource_path('data/fonts/Fruktur/Fruktur-Regular.ttf'), 32)
        self.save_font = pygame.font.Font(resource_path('data/fonts/Fruktur/Fruktur-Regular.ttf'), 16)
        self.small_font = pygame.font.Font(resource_path('data/fonts/Fruktur/Fruktur-Regular.ttf'), 12)
        self.level_font = pygame.font.Font(resource_path('data/fonts/Fruktur/Fruktur-Regular.ttf'), 24)

        self.save_slots = []
        self.selected_slot = 0
        self.selected_button = 0  # 0 for slot, 1 for delete
        self.confirming_delete = -1
        self.confirm_selection = 0  # 0 for Yes, 1 for No
        self.load_save_data()

        self.title_glow = 0
        self.shared_background = shared_background or SharedBackground(assets)

        # Create a blurred background for the slots
        self.slot_background = pygame.transform.smoothscale(assets['background_layers'][0], (140, 200))
        self.slot_background.set_alpha(100)

        self.delete_button_rects = {}
        self.confirm_yes_rect = None
        self.confirm_no_rect = None

    def load_save_data(self):
        self.save_slots = []
        for i in range(4):
            save_file = f"savefile_{i+1}.json"
            try:
                if os.path.exists(save_file):
                    with open(save_file, "r") as f:
                        data = json.load(f)
                        self.save_slots.append({
                            'exists': True,
                            'level': data.get("level", 1),
                            'max_level': data.get("max_level", 1),
                            'death_count': data.get("death_counter", 0),
                            'file_path': save_file
                        })
                else:
                    self.save_slots.append({'exists': False, 'file_path': save_file})
            except (json.JSONDecodeError, FileNotFoundError):
                self.save_slots.append({'exists': False, 'file_path': save_file})

    def render_slot(self, display, i, slot, x, y, slot_width, slot_height):
        # Selection highlight
        is_selected_slot = (i == self.selected_slot and self.selected_button == 0)
        if is_selected_slot and self.confirming_delete == -1:
            selection_rect = pygame.Rect(x - 3, y - 3, slot_width + 6, slot_height + 6)
            glow = int(128 + 127 * math.sin(self.title_glow * 2)) # Faster glow
            pygame.draw.rect(display, (glow, glow, glow), selection_rect, 2, border_radius=5)
            # Shadow
            shadow_rect = pygame.Rect(x + 2, y + 2, slot_width, slot_height)
            shadow_surface = pygame.Surface((slot_width, slot_height), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, 50))
            display.blit(shadow_surface, shadow_rect.topleft)

        # Slot background
        slot_rect = pygame.Rect(x, y, slot_width, slot_height)
        display.blit(self.slot_background, slot_rect.topleft)
        pygame.draw.rect(display, (255, 255, 255, 50), slot_rect, 1, border_radius=5)

        if slot['exists']:
            level_color = (255, 255, 255)
            if is_selected_slot:
                blink_intensity = int(128 + 127 * math.sin(self.title_glow))
                level_color = (blink_intensity, blink_intensity, blink_intensity)

            level_text = self.level_font.render(f"LEVEL {slot['level']}", True, level_color)
            level_rect = level_text.get_rect(center=(x + slot_width // 2, y + slot_height // 2))
            stroke_level = self.level_font.render(f"LEVEL {slot['level']}", True, (0, 0, 0))
            for offset in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                display.blit(stroke_level, (level_rect.x + offset[0], level_rect.y + offset[1]))
            display.blit(level_text, level_rect)

            info_text = f"Deaths: {slot['death_count']}"
            info_surface = self.small_font.render(info_text, True, (255, 255, 255))
            info_rect = info_surface.get_rect(center=(x + slot_width // 2, y + 30))
            stroke_info = self.small_font.render(info_text, True, (0,0,0))
            for offset in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                display.blit(stroke_info, (info_rect.x + offset[0], info_rect.y + offset[1]))
            display.blit(info_surface, info_rect)

            # Delete Button
            delete_button_y = y + slot_height + 10
            delete_rect = pygame.Rect(x, delete_button_y, slot_width, 30)
            self.delete_button_rects[i] = delete_rect

            is_selected_button = (i == self.selected_slot and self.selected_button == 1)
            button_color = (100, 0, 0)
            text_color = (255, 100, 100)

            if is_selected_button:
                blink_intensity = int(128 + 127 * math.sin(self.title_glow))
                button_color = (blink_intensity, 0, 0)
                text_color = (255, 255, 255)

            pygame.draw.rect(display, button_color, delete_rect, border_radius=5)
            pygame.draw.rect(display, (255, 100, 100), delete_rect, 1, border_radius=5)
            delete_text = self.save_font.render("Delete", True, text_color)
            display.blit(delete_text, delete_text.get_rect(center=delete_rect.center))
        else:
            # New Save Slot
            plus_size = 30
            plus_color = (255, 255, 255)
            if is_selected_slot:
                blink_intensity = int(128 + 127 * math.sin(self.title_glow))
                plus_color = (blink_intensity, blink_intensity, blink_intensity)
            
            pygame.draw.rect(display, plus_color, (x + slot_width // 2 - 2, y + slot_height // 2 - plus_size // 2 - 10, 4, plus_size))
            pygame.draw.rect(display, plus_color, (x + slot_width // 2 - plus_size // 2, y + slot_height // 2 - 2 - 10, plus_size, 4))

            new_save_text = self.save_font.render("NEW SAVE", True, plus_color)
            new_save_rect = new_save_text.get_rect(center=(x + slot_width // 2, y + slot_height // 2 + 20))
            stroke_new_save = self.save_font.render("NEW SAVE", True, (0,0,0))
            for offset in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                display.blit(stroke_new_save, (new_save_rect.x + offset[0], new_save_rect.y + offset[1]))
            display.blit(new_save_text, new_save_rect)

    def render(self, display, display_2):
        display.fill((0, 0, 0, 0))
        display_2.fill((0, 0, 0))

        self.shared_background.render_background(display_2)
        self.shared_background.render_particles(display)

        # Title
        self.title_glow += 0.1
        glow_intensity = int(50 + 30 * math.sin(self.title_glow))
        title_text = self.title_font.render("SELECT SAVE FILE", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(display.get_width() // 2, 40))
        stroke_title = self.title_font.render("SELECT SAVE FILE", True, (0,0,0))
        for offset in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            display.blit(stroke_title, (title_rect.x + offset[0], title_rect.y + offset[1]))
        display.blit(title_text, title_rect)

        # Slots
        slot_width = 140
        slot_height = 200
        slot_spacing = 20
        start_x = (display.get_width() - (4 * slot_width + 3 * slot_spacing)) // 2
        start_y = 120

        self.delete_button_rects = {}

        for i, slot in enumerate(self.save_slots):
            x = start_x + i * (slot_width + slot_spacing)
            y = start_y
            self.render_slot(display, i, slot, x, y, slot_width, slot_height)

            if self.confirming_delete == i:
                overlay = pygame.Surface((slot_width, slot_height + 40), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 220))
                display.blit(overlay, (x, y))

                confirm_text = self.save_font.render("Delete?", True, (255, 255, 255))
                display.blit(confirm_text, confirm_text.get_rect(center=(x + slot_width // 2, y + 40)))

                # Yes button
                yes_color = (255, 255, 255)
                if self.confirm_selection == 0:
                    blink_intensity = int(128 + 127 * math.sin(self.title_glow))
                    yes_color = (blink_intensity, blink_intensity, blink_intensity)
                yes_text = self.save_font.render("Yes", True, yes_color)
                self.confirm_yes_rect = yes_text.get_rect(center=(x + slot_width // 4 + 10, y + slot_height - 20))
                display.blit(yes_text, self.confirm_yes_rect)

                # No button
                no_color = (255, 255, 255)
                if self.confirm_selection == 1:
                    blink_intensity = int(128 + 127 * math.sin(self.title_glow))
                    no_color = (blink_intensity, blink_intensity, blink_intensity)
                no_text = self.save_font.render("No", True, no_color)
                self.confirm_no_rect = no_text.get_rect(center=(x + slot_width * 3 // 4 - 10, y + slot_height - 20))
                display.blit(no_text, self.confirm_no_rect)

        # Controls
        controls_text = "Use A/D or ←/→ to select, SPACE/ENTER to load"
        controls_surface = self.small_font.render(controls_text, True, (255, 255, 255))
        display.blit(controls_surface,
                     controls_surface.get_rect(center=(display.get_width() // 2, display.get_height() - 20)))

        display_2.blit(display, (0, 0))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            if self.confirming_delete != -1:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_a, pygame.K_LEFT]:
                        self.confirm_selection = (self.confirm_selection - 1 + 2) % 2
                        self.sfx['menu_click'].play()
                    elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                        self.confirm_selection = (self.confirm_selection + 1) % 2
                        self.sfx['menu_click'].play()
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        if self.confirm_selection == 0:  # Yes
                            try:
                                os.remove(self.save_slots[self.confirming_delete]['file_path'])
                            except OSError:
                                pass
                            self.load_save_data()
                            self.sfx['menu_click'].play()
                        self.confirming_delete = -1
                        self.confirm_selection = 0
                    elif event.key == pygame.K_ESCAPE:
                        self.confirming_delete = -1
                        self.confirm_selection = 0

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if self.confirm_yes_rect and self.confirm_yes_rect.collidepoint(mouse_x, mouse_y):
                        try:
                            os.remove(self.save_slots[self.confirming_delete]['file_path'])
                        except OSError:
                            pass
                        self.load_save_data()
                        self.sfx['menu_click'].play()
                        self.confirming_delete = -1
                        self.confirm_selection = 0
                    elif self.confirm_no_rect and self.confirm_no_rect.collidepoint(mouse_x, mouse_y):
                        self.confirming_delete = -1
                        self.confirm_selection = 0
                continue

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_a, pygame.K_LEFT]:
                    self.selected_slot = (self.selected_slot - 1 + 4) % 4
                    self.selected_button = 0
                    self.sfx['menu_click'].play()
                elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                    self.selected_slot = (self.selected_slot + 1) % 4
                    self.selected_button = 0
                    self.sfx['menu_click'].play()
                elif event.key in [pygame.K_s, pygame.K_DOWN]:
                    if self.save_slots[self.selected_slot]['exists']:
                        self.selected_button = (self.selected_button + 1) % 2
                        self.sfx['menu_click'].play()
                elif event.key in [pygame.K_w, pygame.K_UP]:
                    if self.save_slots[self.selected_slot]['exists']:
                        self.selected_button = (self.selected_button - 1 + 2) % 2
                        self.sfx['menu_click'].play()
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_button == 0:  # Slot selected
                        self.sfx['menu_click'].play()
                        return self.selected_slot
                    elif self.selected_button == 1:  # Delete button selected
                        self.confirming_delete = self.selected_slot
                        self.sfx['menu_click'].play()
                elif event.key == pygame.K_ESCAPE:
                    return "back"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in self.delete_button_rects.items():
                    if rect.collidepoint(event.pos):
                        self.confirming_delete = i
                        self.sfx['menu_click'].play()
                        return None

                slot_width = 140
                slot_height = 200
                slot_spacing = 20
                start_x = (self.screen.get_width() - (4 * slot_width + 3 * slot_spacing)) // 2
                start_y = 120
                for i in range(4):
                    slot_rect = pygame.Rect(start_x + i * (slot_width + slot_spacing), start_y, slot_width, slot_height)
                    if slot_rect.collidepoint(event.pos):
                        if self.selected_slot == i:
                            return self.selected_slot  # Double click to select
                        else:
                            self.selected_slot = i
                            self.sfx['menu_click'].play()

        return None

    def run(self):
        while True:
            action = self.handle_input()
            if action is not None:
                return action

            self.shared_background.update()

            self.render(self.screen, self.screen)

            pygame.display.flip()
            self.clock.tick(60)


def save_select(screen, clock, assets, sfx, shared_background=None):
    """Entry point for save selection"""
    save_screen = SaveSelect(screen, clock, assets, sfx, shared_background)
    return save_screen.run()
