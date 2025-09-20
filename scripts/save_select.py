import pygame
import sys
import math
import random
import json
import os
from scripts.shared_background import SharedBackground

pygame.init()
pygame.mixer.init()

click_sound = pygame.mixer.Sound('data/menu.wav')
click_sound.set_volume(0.2)

class SaveSelect:
    def __init__(self, screen, clock, assets, sfx, shared_background=None):
        self.screen = screen
        self.clock = clock
        self.assets = assets
        self.sfx = sfx
        
        # Fonts
        self.title_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 32)
        self.save_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 16)
        self.small_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 12)
        self.level_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 24)
        
        # Save slots
        self.save_slots = []
        self.selected_slot = 0
        self.load_save_data()
        
        # Animation variables
        self.title_glow = 0
        
        # Shared background
        self.shared_background = shared_background or SharedBackground(assets)
    
    def load_save_data(self):
        """Load save data for all 4 slots"""
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
                    self.save_slots.append({
                        'exists': False,
                        'level': 1,
                        'max_level': 1,
                        'death_count': 0,
                        'file_path': save_file
                    })
            except (json.JSONDecodeError, FileNotFoundError):
                self.save_slots.append({
                    'exists': False,
                    'level': 1,
                    'max_level': 1,
                    'death_count': 0,
                    'file_path': save_file
                })
    
    
    def render_title(self, display):
        """Render animated title"""
        self.title_glow += 0.1
        glow_intensity = int(50 + 30 * math.sin(self.title_glow))
        
        title_text = self.title_font.render("SELECT SAVE FILE", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(display.get_width() // 2, 30))
        
        # Glow effect
        glow_color = (glow_intensity, glow_intensity, glow_intensity)
        glow_text = self.title_font.render("SELECT SAVE FILE", True, glow_color)
        
        # Draw glow behind main text
        for offset in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            display.blit(glow_text, glow_rect)
        
        # Draw main title
        display.blit(title_text, title_rect)
    
    def create_gradient_surface(self, width, height, start_color, end_color):
        """Create a gradient surface from start_color to end_color"""
        surface = pygame.Surface((width, height))
        for y in range(height):
            ratio = y / height
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        return surface
    
    def render_save_slots(self, display):
        """Render the 4 save slots"""
        slot_width = 140
        slot_height = display.get_height() - 120  # Elongate to bottom, leaving space for controls
        slot_spacing = 10
        start_x = (display.get_width() - (4 * slot_width + 3 * slot_spacing)) // 2
        start_y = 80
        
        for i, slot in enumerate(self.save_slots):
            x = start_x + i * (slot_width + slot_spacing)
            y = start_y
            
            # Selection highlight
            if i == self.selected_slot:
                # Draw selection border
                selection_rect = pygame.Rect(x - 3, y - 3, slot_width + 6, slot_height + 6)
                pygame.draw.rect(display, (255, 255, 255), selection_rect, 2)
            
            # Save slot background
            slot_rect = pygame.Rect(x, y, slot_width, slot_height)
            
            if slot['exists']:
                # Existing save - show level preview
                preview_surface = pygame.Surface((slot_width, slot_height))
                preview_surface.fill((50, 50, 50))  # Dark background
                
                # Add some simple level elements
                pygame.draw.rect(preview_surface, (100, 100, 100), (10, slot_height - 20, slot_width - 20, 10))  # Ground
                pygame.draw.rect(preview_surface, (150, 150, 150), (20, slot_height - 30, 10, 10))  # Platform
                pygame.draw.rect(preview_surface, (200, 200, 200), (slot_width - 30, slot_height - 40, 10, 20))  # Wall
                
                display.blit(preview_surface, (x, y))
                
                # Draw blinking level number in the center
                if i == self.selected_slot:
                    blink_intensity = int(50 + 30 * math.sin(self.title_glow))
                    level_color = (blink_intensity, blink_intensity, blink_intensity)
                else:
                    level_color = (255, 255, 255)
                
                level_text = self.level_font.render(f"LEVEL {slot['level']}", True, level_color)
                level_rect = level_text.get_rect(center=(x + slot_width // 2, y + slot_height // 2))
                
                # Draw stroke for level text
                stroke_color = (0, 0, 0) if level_color == (255, 255, 255) else (255, 255, 255)
                stroke_level = self.level_font.render(f"LEVEL {slot['level']}", True, stroke_color)
                for offset in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                    stroke_rect = level_rect.copy()
                    stroke_rect.x += offset[0]
                    stroke_rect.y += offset[1]
                    display.blit(stroke_level, stroke_rect)
                
                display.blit(level_text, level_rect)
            else:
                # Empty save - gradient background
                gradient = self.create_gradient_surface(slot_width, slot_height, (0, 0, 0), (50, 50, 50))
                display.blit(gradient, (x, y))
                
                # Draw + icon
                plus_size = 20
                plus_x = x + slot_width // 2 - plus_size // 2
                plus_y = y + slot_height // 2 - plus_size // 2 - 10
                
                # Draw + symbol
                pygame.draw.rect(display, (255, 255, 255), (plus_x + plus_size // 2 - 2, plus_y, 4, plus_size))
                pygame.draw.rect(display, (255, 255, 255), (plus_x, plus_y + plus_size // 2 - 2, plus_size, 4))
                
                # Draw "NEW SAVE" text with blinking effect if selected
                if i == self.selected_slot:
                    blink_intensity = int(50 + 30 * math.sin(self.title_glow))
                    new_save_color = (blink_intensity, blink_intensity, blink_intensity)
                else:
                    new_save_color = (255, 255, 255)
                
                new_save_text = self.small_font.render("NEW SAVE", True, new_save_color)
                new_save_rect = new_save_text.get_rect(center=(x + slot_width // 2, y + slot_height // 2 + 15))
                
                # Draw stroke for new save text
                stroke_color = (0, 0, 0) if new_save_color == (255, 255, 255) else (255, 255, 255)
                stroke_new_save = self.small_font.render("NEW SAVE", True, stroke_color)
                for offset in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                    stroke_rect = new_save_rect.copy()
                    stroke_rect.x += offset[0]
                    stroke_rect.y += offset[1]
                    display.blit(stroke_new_save, stroke_rect)
                
                display.blit(new_save_text, new_save_rect)
            
            # Draw save info at the top
            if slot['exists']:
                info_text = f"Level: {slot['level']} | Deaths: {slot['death_count']}"
                info_surface = self.small_font.render(info_text, True, (255, 255, 255))
                info_rect = info_surface.get_rect(center=(x + slot_width // 2, y - 20))
                
                # Draw stroke for info text
                stroke_info = self.small_font.render(info_text, True, (0, 0, 0))
                for offset in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                    stroke_rect = info_rect.copy()
                    stroke_rect.x += offset[0]
                    stroke_rect.y += offset[1]
                    display.blit(stroke_info, stroke_rect)
                
                display.blit(info_surface, info_rect)
    
    def render_controls(self, display):
        """Render control instructions"""
        controls_text = "Use ←→ to select, ENTER to load, ESC to back"
        controls_surface = self.small_font.render(controls_text, True, (0, 0, 0))
        controls_rect = controls_surface.get_rect(center=(display.get_width() // 2, display.get_height() - 15))
        
        # Draw stroke for controls text
        stroke_controls = self.small_font.render(controls_text, True, (255, 255, 255))
        for offset in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            stroke_rect = controls_rect.copy()
            stroke_rect.x += offset[0]
            stroke_rect.y += offset[1]
            display.blit(stroke_controls, stroke_rect)
        
        display.blit(controls_surface, controls_rect)
    
    def render(self, display, display_2):
        """Main render method"""
        # Clear displays
        display.fill((0, 0, 0, 0))
        display_2.fill((0, 0, 0))
        
        # Render background using shared background
        self.shared_background.render_background(display_2)
        
        # Render particles using shared background
        self.shared_background.render_particles(display)
        
        # Render title
        self.render_title(display)
        
        # Render save slots
        self.render_save_slots(display)
        
        # Render controls
        self.render_controls(display)
        
        # Composite displays
        display_2.blit(display, (0, 0))
    
    def handle_input(self):
        """Handle input and return selected action"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.selected_slot = (self.selected_slot - 1) % 4
                    click_sound.play()
                elif event.key == pygame.K_RIGHT:
                    self.selected_slot = (self.selected_slot + 1) % 4
                    click_sound.play()
                elif event.key == pygame.K_RETURN:
                    click_sound.play()
                    return self.selected_slot
                elif event.key == pygame.K_ESCAPE:
                    return "back"
        
        return None
    
    def run(self):
        """Main save selection loop"""
        while True:
            # Handle input
            action = self.handle_input()
            if action is not None:
                return action
            
            # Update animations
            self.shared_background.update()
            
            # Render
            self.render(self.screen, self.screen)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)

def save_select(screen, clock, assets, sfx, shared_background=None):
    """Entry point for save selection"""
    save_screen = SaveSelect(screen, clock, assets, sfx, shared_background)
    return save_screen.run()
