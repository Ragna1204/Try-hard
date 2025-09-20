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

class LevelSelect:
    def __init__(self, screen, clock, assets, sfx, max_level, shared_background=None):
        self.screen = screen
        self.clock = clock
        self.assets = assets
        self.sfx = sfx
        self.max_level = max_level
        
        # Fonts
        self.title_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 32)
        self.level_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 20)
        self.small_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 12)
        
        # Level selection
        self.selected_level = 1
        self.levels_per_row = 4
        self.level_spacing = 80
        self.level_size = 60
        
        # Animation variables
        self.title_glow = 0
        
        # Shared background
        self.shared_background = shared_background or SharedBackground(assets)
    
    def render_title(self, display):
        """Render animated title"""
        self.title_glow += 0.1
        glow_intensity = int(50 + 30 * math.sin(self.title_glow))
        
        title_text = self.title_font.render("SELECT LEVEL", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(display.get_width() // 2, 30))
        
        # Glow effect
        glow_color = (glow_intensity, glow_intensity, glow_intensity)
        glow_text = self.title_font.render("SELECT LEVEL", True, glow_color)
        
        # Draw glow behind main text
        for offset in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            display.blit(glow_text, glow_rect)
        
        # Draw main title
        display.blit(title_text, title_rect)
    
    def render_levels(self, display):
        """Render level selection grid"""
        # Calculate grid layout
        rows = (self.max_level + self.levels_per_row - 1) // self.levels_per_row
        start_x = (display.get_width() - (self.levels_per_row * self.level_spacing)) // 2 + self.level_spacing // 2
        start_y = 80
        
        for level in range(1, self.max_level + 1):
            row = (level - 1) // self.levels_per_row
            col = (level - 1) % self.levels_per_row
            
            x = start_x + col * self.level_spacing - self.level_size // 2
            y = start_y + row * (self.level_size + 20)
            
            # Selection highlight
            if level == self.selected_level:
                # Draw selection border
                selection_rect = pygame.Rect(x - 3, y - 3, self.level_size + 6, self.level_size + 6)
                pygame.draw.rect(display, (255, 255, 255), selection_rect, 2)
            
            # Level background
            level_rect = pygame.Rect(x, y, self.level_size, self.level_size)
            
            # Create level preview
            preview_surface = pygame.Surface((self.level_size, self.level_size))
            preview_surface.fill((50, 50, 50))  # Dark background
            
            # Add some simple level elements based on level number
            if level % 3 == 1:
                # Ground level
                pygame.draw.rect(preview_surface, (100, 100, 100), (5, self.level_size - 10, self.level_size - 10, 8))
            elif level % 3 == 2:
                # Platform level
                pygame.draw.rect(preview_surface, (100, 100, 100), (5, self.level_size - 10, self.level_size - 10, 8))
                pygame.draw.rect(preview_surface, (150, 150, 150), (10, self.level_size - 25, 15, 8))
            else:
                # Complex level
                pygame.draw.rect(preview_surface, (100, 100, 100), (5, self.level_size - 10, self.level_size - 10, 8))
                pygame.draw.rect(preview_surface, (150, 150, 150), (10, self.level_size - 25, 15, 8))
                pygame.draw.rect(preview_surface, (200, 200, 200), (self.level_size - 20, self.level_size - 30, 8, 15))
            
            display.blit(preview_surface, (x, y))
            
            # Draw blinking level number
            if level == self.selected_level:
                blink_intensity = int(50 + 30 * math.sin(self.title_glow))
                level_color = (blink_intensity, blink_intensity, blink_intensity)
            else:
                level_color = (255, 255, 255)
            
            level_text = self.level_font.render(str(level), True, level_color)
            level_rect = level_text.get_rect(center=(x + self.level_size // 2, y + self.level_size // 2))
            
            # Draw stroke for level text
            stroke_color = (0, 0, 0) if level_color == (255, 255, 255) else (255, 255, 255)
            stroke_level = self.level_font.render(str(level), True, stroke_color)
            for offset in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                stroke_rect = level_rect.copy()
                stroke_rect.x += offset[0]
                stroke_rect.y += offset[1]
                display.blit(stroke_level, stroke_rect)
            
            display.blit(level_text, level_rect)
    
    def render_controls(self, display):
        """Render control instructions"""
        controls_text = "Use ←→↑↓ to select, ENTER to play, ESC to back"
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
        
        # Render levels
        self.render_levels(display)
        
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
                    if self.selected_level > 1:
                        self.selected_level -= 1
                        click_sound.play()
                elif event.key == pygame.K_RIGHT:
                    if self.selected_level < self.max_level:
                        self.selected_level += 1
                        click_sound.play()
                elif event.key == pygame.K_UP:
                    # Move up a row
                    new_level = self.selected_level - self.levels_per_row
                    if new_level >= 1:
                        self.selected_level = new_level
                        click_sound.play()
                elif event.key == pygame.K_DOWN:
                    # Move down a row
                    new_level = self.selected_level + self.levels_per_row
                    if new_level <= self.max_level:
                        self.selected_level = new_level
                        click_sound.play()
                elif event.key == pygame.K_RETURN:
                    click_sound.play()
                    return self.selected_level
                elif event.key == pygame.K_ESCAPE:
                    return "back"
        
        return None
    
    def run(self):
        """Main level selection loop"""
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

def level_select(screen, clock, assets, sfx, max_level, shared_background=None):
    """Entry point for level selection"""
    level_screen = LevelSelect(screen, clock, assets, sfx, max_level, shared_background)
    return level_screen.run()
