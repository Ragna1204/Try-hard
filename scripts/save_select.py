import pygame
import sys
import math
import random
import json
import os
from scripts.shared_background import SharedBackground

pygame.init()
pygame.mixer.init()


class SaveSelect:
    def __init__(self, screen, clock, assets, sfx, shared_background=None):
        self.screen = screen
        self.clock = clock
        self.assets = assets
        self.sfx = sfx
        
        self.title_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 32)
        self.save_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 16)
        self.small_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 12)
        self.level_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 24)
        
        self.save_slots = []
        self.selected_slot = 0
        self.confirming_delete = -1
        self.load_save_data()
        
        self.title_glow = 0
        self.shared_background = shared_background or SharedBackground(assets)

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

    def render(self, display, display_2):
        display.fill((0, 0, 0, 0))
        display_2.fill((0, 0, 0))
        
        self.shared_background.render_background(display_2)
        self.shared_background.render_particles(display)
        
        # Title
        self.title_glow += 0.1
        glow_intensity = int(50 + 30 * math.sin(self.title_glow))
        title_text = self.title_font.render("SELECT SAVE FILE", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(display.get_width() // 2, 30))
        glow_color = (glow_intensity, glow_intensity, glow_intensity)
        glow_text = self.title_font.render("SELECT SAVE FILE", True, glow_color)
        for offset in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            display.blit(glow_text, glow_rect)
        display.blit(title_text, title_rect)

        # Slots
        slot_width = 140
        slot_height = display.get_height() - 150
        slot_spacing = 10
        start_x = (display.get_width() - (4 * slot_width + 3 * slot_spacing)) // 2
        start_y = 80

        self.delete_button_rects = {}

        for i, slot in enumerate(self.save_slots):
            x = start_x + i * (slot_width + slot_spacing)
            y = start_y
            
            if i == self.selected_slot and self.confirming_delete == -1:
                selection_rect = pygame.Rect(x - 3, y - 3, slot_width + 6, slot_height + 6)
                pygame.draw.rect(display, (255, 255, 255), selection_rect, 2)
            
            if slot['exists']:
                preview_surface = pygame.Surface((slot_width, slot_height))
                preview_surface.fill((50, 50, 50))
                pygame.draw.rect(preview_surface, (100, 100, 100), (10, slot_height - 20, slot_width - 20, 10))
                pygame.draw.rect(preview_surface, (150, 150, 150), (20, slot_height - 30, 10, 10))
                pygame.draw.rect(preview_surface, (200, 200, 200), (slot_width - 30, slot_height - 40, 10, 20))
                display.blit(preview_surface, (x, y))

                level_color = (255, 255, 255)
                if i == self.selected_slot:
                    blink_intensity = int(50 + 30 * math.sin(self.title_glow))
                    level_color = (blink_intensity, blink_intensity, blink_intensity)
                
                level_text = self.level_font.render(f"LEVEL {slot['level']}", True, level_color)
                level_rect = level_text.get_rect(center=(x + slot_width // 2, y + slot_height // 2))
                stroke_level = self.level_font.render(f"LEVEL {slot['level']}", True, (0,0,0))
                for offset in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    display.blit(stroke_level, (level_rect.x + offset[0], level_rect.y + offset[1]))
                display.blit(level_text, level_rect)

                info_text = f"Deaths: {slot['death_count']}"
                info_surface = self.small_font.render(info_text, True, (255, 255, 255))
                info_rect = info_surface.get_rect(center=(x + slot_width // 2, y + 20))
                display.blit(info_surface, info_rect)

                delete_text_color = (200, 50, 50)
                delete_rect = pygame.Rect(x, y + slot_height + 5, slot_width, 20)
                self.delete_button_rects[i] = delete_rect
                if delete_rect.collidepoint(pygame.mouse.get_pos()):
                    delete_text_color = (255, 100, 100)
                delete_text = self.small_font.render("Delete", True, delete_text_color)
                display.blit(delete_text, delete_text.get_rect(center=delete_rect.center))
            else:
                gradient = pygame.Surface((slot_width, slot_height))
                for j in range(slot_height):
                    ratio = j / slot_height
                    color = (int(0 * (1 - ratio) + 50 * ratio),) * 3
                    pygame.draw.line(gradient, color, (0, j), (slot_width, j))
                display.blit(gradient, (x, y))
                
                plus_size = 20
                pygame.draw.rect(display, (255, 255, 255), (x + slot_width // 2 - 2, y + slot_height // 2 - plus_size // 2, 4, plus_size))
                pygame.draw.rect(display, (255, 255, 255), (x + slot_width // 2 - plus_size // 2, y + slot_height // 2 - 2, plus_size, 4))

            if self.confirming_delete == i:
                overlay = pygame.Surface((slot_width, slot_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                display.blit(overlay, (x, y))

                confirm_text = self.save_font.render("Delete?", True, (255, 255, 255))
                display.blit(confirm_text, confirm_text.get_rect(center=(x + slot_width // 2, y + slot_height // 2 - 20)))

                yes_text = self.save_font.render("Yes", True, (255, 255, 255))
                self.confirm_yes_rect = yes_text.get_rect(center=(x + slot_width // 4 + 10, y + slot_height // 2 + 20))
                display.blit(yes_text, self.confirm_yes_rect)

                no_text = self.save_font.render("No", True, (255, 255, 255))
                self.confirm_no_rect = no_text.get_rect(center=(x + slot_width * 3 // 4 - 10, y + slot_height // 2 + 20))
                display.blit(no_text, self.confirm_no_rect)

        # Controls
        controls_text = "Use A/D or ←/→ to select, SPACE/ENTER to load"
        controls_surface = self.small_font.render(controls_text, True, (255, 255, 255))
        display.blit(controls_surface, controls_surface.get_rect(center=(display.get_width() // 2, display.get_height() - 15)))
        
        display_2.blit(display, (0, 0))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            if self.confirming_delete != -1:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.confirm_yes_rect and self.confirm_yes_rect.collidepoint(event.pos):
                        try:
                            os.remove(self.save_slots[self.confirming_delete]['file_path'])
                        except OSError:
                            pass
                        self.load_save_data()
                        self.sfx['menu_click'].play()
                        self.confirming_delete = -1
                    elif self.confirm_no_rect and self.confirm_no_rect.collidepoint(event.pos):
                        self.sfx['menu_click'].play()
                        self.confirming_delete = -1
                    else:
                        self.confirming_delete = -1
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.confirming_delete = -1
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.selected_slot = (self.selected_slot - 1) % 4
                    self.sfx['menu_click'].play()
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.selected_slot = (self.selected_slot + 1) % 4
                    self.sfx['menu_click'].play()
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.sfx['menu_click'].play()
                    return self.selected_slot
                elif event.key == pygame.K_ESCAPE:
                    return "back"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in self.delete_button_rects.items():
                    if rect.collidepoint(event.pos):
                        self.confirming_delete = i
                        self.sfx['menu_click'].play()
                        return None

                slot_width = 140
                slot_height = self.screen.get_height() - 150
                slot_spacing = 10
                start_x = (self.screen.get_width() - (4 * slot_width + 3 * slot_spacing)) // 2
                start_y = 80
                for i in range(4):
                    slot_rect = pygame.Rect(start_x + i * (slot_width + slot_spacing), start_y, slot_width, slot_height)
                    if slot_rect.collidepoint(event.pos):
                        if self.selected_slot == i:
                            return self.selected_slot # Double click to select
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
