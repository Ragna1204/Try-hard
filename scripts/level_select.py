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

class LevelSelect:
    def __init__(self, screen, clock, assets, sfx, max_level, shared_background=None):
        self.screen = screen
        self.clock = clock
        self.assets = assets
        self.sfx = sfx
        self.max_level = max_level
        
        # Fonts
        self.title_font = pygame.font.Font(resource_path('data/fonts/ninjaline/NinjaLine.ttf'), 32)
        self.level_font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 20)
        self.small_font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 12)
        
        # Level selection
        self.selected_level = 1
        self.hovered_level = None
        self.levels_per_row = 4
        self.level_spacing = 80
        self.level_size = 60

        # Animation variables
        self.title_glow = 0
        self.animation_time = 0

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
        """Render level selection grid with ninja-themed design"""
        self.animation_time += 0.05

        # Calculate grid layout
        rows = (self.max_level + self.levels_per_row - 1) // self.levels_per_row
        start_x = (display.get_width() - (self.levels_per_row * self.level_spacing)) // 2 + self.level_spacing // 2
        start_y = 80

        for level in range(1, self.max_level + 1):
            row = (level - 1) // self.levels_per_row
            col = (level - 1) % self.levels_per_row

            base_x = start_x + col * self.level_spacing - self.level_size // 2
            base_y = start_y + row * (self.level_size + 20)

            # Mouse hover detection (prioritize this first)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            level_rect = pygame.Rect(base_x, base_y, self.level_size, self.level_size)
            is_hovered = level_rect.collidepoint(mouse_x, mouse_y)

            # Update hover state and play sound
            prev_hovered = self.hovered_level
            if is_hovered:
                self.hovered_level = level
                self.selected_level = level  # Hover immediately updates selection
            elif self.hovered_level == level:
                self.hovered_level = None

            # Play sound only when entering a new hover
            if prev_hovered != self.hovered_level and prev_hovered is None and self.hovered_level is not None:
                self.sfx['menu_click'].play()

            # Determine state
            is_selected = (level == self.selected_level)
            is_active = is_selected or is_hovered

            x = base_x
            y = base_y

            # Subtle floating motion like a ninja in shadow
            float_offset = int(3 * math.sin(self.animation_time + level * 0.7))
            y += float_offset

            # Ninja-themed selection highlight
            if is_active:
                # Crimson energy outline (ninja blood/chi energy)
                glow_intensity = int(180 + 75 * math.sin(self.animation_time * 5))
                energy_color = (glow_intensity, 30, 30)  # Deep crimson red
                pygame.draw.rect(display, energy_color, (x - 4, y - 4, self.level_size + 8, self.level_size + 8), 2)

                # Secondary shadow aura
                shadow_color = (glow_intensity//3, 10, 10)
                pygame.draw.rect(display, shadow_color, (x - 6, y - 6, self.level_size + 12, self.level_size + 12), 1)
            else:
                # Subtle dark border
                pygame.draw.rect(display, (40, 40, 40), (x - 1, y - 1, self.level_size + 2, self.level_size + 2), 1)

            # Dark ninja background
            if is_active:
                bg_color = (45, 15, 15)  # Dark crimson for active
                parchment_color = (90, 40, 40)
            else:
                bg_color = (30, 10, 10)  # Deeper crimson for inactive
                parchment_color = (60, 25, 25)

            # Main background (blood-stained parchment look)
            pygame.draw.rect(display, bg_color, (x, y, self.level_size, self.level_size))

            # Parchment texture pattern
            for px in range(x, x + self.level_size, 6):
                for py in range(y, y + self.level_size, 6):
                    if (px + py) % 12 == 0:
                        pygame.draw.rect(display, parchment_color, (px, py, 3, 3))

            # Ninja-themed level icons with crimson accents
            icon_color = (120, 50, 50) if not is_active else (200, 80, 80)

            # Ninja symbols based on level type
            if level % 4 == 1:  # Shadow/Sneak training (Kunai)
                # Draw kunai (dagger)
                pygame.draw.polygon(display, icon_color, [
                    (x + self.level_size//2, y + self.level_size - 5),  # Point
                    (x + self.level_size//2 - 3, y + self.level_size - 12),  # Left up
                    (x + self.level_size//2 - 1, y + self.level_size - 8),   # Left down
                    (x + self.level_size//2, y + self.level_size - 5),      # Point
                    (x + self.level_size//2 + 1, y + self.level_size - 8),   # Right down
                    (x + self.level_size//2 + 3, y + self.level_size - 12)   # Right up
                ])
                # Handle
                pygame.draw.rect(display, icon_color, (x + self.level_size//2 - 1, y + self.level_size - 8, 2, 6))

            elif level % 4 == 2:  # Combat training (Shuriken)
                # Draw shuriken (throwing star)
                center_x, center_y = x + self.level_size//2, y + self.level_size//2
                radius = 8
                points = []
                for i in range(8):
                    angle = (math.pi / 4) * i
                    if i % 2 == 0:  # Points
                        r = radius
                    else:  # Inner points
                        r = radius * 0.6
                    px = center_x + r * math.cos(angle)
                    py = center_y + r * math.sin(angle)
                    points.append((int(px), int(py)))

                pygame.draw.polygon(display, icon_color, points)

            elif level % 4 == 3:  # Precision/Moving targets (Bow)
                # Draw ninja bow silhouette
                bow_x = x + self.level_size//2 - 8
                bow_y = y + self.level_size//2 - 15
                # Bow curve (top half)
                for i in range(17):
                    angle = math.pi * (i / 16)
                    px = int(bow_x + 8 + 8 * math.sin(angle))
                    py = int(bow_y + 15 - 8 * math.cos(angle))
                    if 0 < px < x + self.level_size and 0 < py < y + self.level_size:
                        pygame.draw.rect(display, icon_color, (px, py, 1, 1))
                # Bowstring
                pygame.draw.line(display, icon_color, (bow_x + 8, bow_y + 15), (bow_x + 8, bow_y + 7), 1)

            else:  # Stealth/Master challenges (Full Moon/Scroll)
                if level % 8 == 0:  # Master levels - Moon symbol
                    center_x, center_y = int(x + self.level_size//2), int(y + self.level_size//2)
                    # Moon crescent
                    pygame.draw.circle(display, icon_color, (center_x + 3, center_y), 10)
                    pygame.draw.circle(display, bg_color, (center_x - 2, center_y - 2), 8)
                else:  # Regular challenge levels - Scroll
                    scroll_x = x + 8
                    scroll_y = y + self.level_size//2 - 8
                    # Scroll paper
                    pygame.draw.rect(display, icon_color, (scroll_x, scroll_y, 12, 16))
                    pygame.draw.rect(display, icon_color, (scroll_x + 1, scroll_y + 1, 10, 14))
                    # Winders at top and bottom
                    pygame.draw.circle(display, icon_color, (scroll_x + 6, scroll_y), 2)
                    pygame.draw.circle(display, icon_color, (scroll_x + 6, scroll_y + 15), 2)

            # Ninja-themed level number with crimson glow
            if is_active:
                text_intensity = int(200 + 55 * math.sin(self.animation_time * 4))
                level_color = (text_intensity, 80, 80)  # Crimson glow
            else:
                level_color = (255, 200, 200)  # Subtle crimson

            level_text = self.level_font.render(str(level), True, level_color)
            level_rect = level_text.get_rect(center=(x + self.level_size // 2, y + self.level_size // 2))

            # Crimson energy glow for active levels
            if is_active:
                # Layered crimson glow
                for glow_layer in [(-3, -3), (3, -3), (-3, 3), (3, 3), (-2, 0), (2, 0), (0, -2), (0, 2)]:
                    glow_surface = self.level_font.render(str(level), True, (100, 30, 30))
                    display.blit(glow_surface, (level_rect.x + glow_layer[0], level_rect.y + glow_layer[1]))

            # Text border
            border_color = (0, 0, 0) if level_color == (255, 255, 255) else (40, 10, 10)
            border_text = self.level_font.render(str(level), True, border_color)
            for offset in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                border_rect = level_rect.copy()
                border_rect.x += offset[0]
                border_rect.y += offset[1]
                display.blit(border_text, border_rect)

            # Main text
            display.blit(level_text, level_rect)
    
    def render_controls(self, display):
        """Render control instructions with mouse support"""
        controls_text = "Use WASD/←→↑↓ to select, SPACE/ENTER/Click to play"
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
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    if self.selected_level > 1:
                        self.selected_level -= 1
                        self.sfx['menu_click'].play()
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    if self.selected_level < self.max_level:
                        self.selected_level += 1
                        self.sfx['menu_click'].play()
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    # Move up a row
                    new_level = self.selected_level - self.levels_per_row
                    if new_level >= 1:
                        self.selected_level = new_level
                        self.sfx['menu_click'].play()
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    # Move down a row
                    new_level = self.selected_level + self.levels_per_row
                    if new_level <= self.max_level:
                        self.selected_level = new_level
                        self.sfx['menu_click'].play()
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.sfx['menu_click'].play()
                    return self.selected_level
                elif event.key == pygame.K_ESCAPE:
                    return "back"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    for level in range(1, self.max_level + 1):
                        row = (level - 1) // self.levels_per_row
                        col = (level - 1) % self.levels_per_row
                        x = ((self.screen.get_width() - (self.levels_per_row * self.level_spacing)) // 2 +
                             self.level_spacing // 2 + col * self.level_spacing - self.level_size // 2)
                        y = (80 + row * (self.level_size + 20))
                        level_rect = pygame.Rect(x, y, self.level_size, self.level_size)
                        if level_rect.collidepoint(mouse_x, mouse_y):
                            self.selected_level = level
                            self.sfx['menu_click'].play()
                            return level

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
