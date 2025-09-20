import pygame
import sys
import math
import random
import json
from scripts.shared_background import SharedBackground

pygame.init()
pygame.mixer.init()

click_sound = pygame.mixer.Sound('data/menu.wav')
click_sound.set_volume(0.2)

class MainMenu:
    def __init__(self, screen, clock, assets, sfx, shared_background=None):
        self.screen = screen
        self.clock = clock
        self.assets = assets
        self.sfx = sfx
        
        # Fonts
        self.title_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 48)
        self.subtitle_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 24)
        self.menu_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 20)
        self.small_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 16)
        
        # Menu state
        self.selected_item = 0
        self.menu_items = ["Start Game", "Options", "About", "Exit"]
        
        # Animation variables
        self.title_glow = 0
        self.menu_animation = 0
        
        # Shared background
        self.shared_background = shared_background or SharedBackground(assets)
        
        # Load game state for display
        self.load_game_state()
    
    def load_game_state(self):
        """Load game state to display current progress"""
        try:
            with open("savefile.json", "r") as save_file:
                state = json.load(save_file)
                self.current_level = state.get("level", 1)
                self.max_level = state.get("max_level", 1)
                self.death_count = state.get("death_counter", 0)
        except (json.JSONDecodeError, FileNotFoundError):
            self.current_level = 1
            self.max_level = 1
            self.death_count = 0
    
    
    def render_title(self, display):
        """Render animated game title"""
        # Animate title glow
        self.title_glow += 0.1
        glow_intensity = int(50 + 30 * math.sin(self.title_glow))
        
        # Main title
        title_text = self.title_font.render("TRY-HARD", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(display.get_width() // 2, 50))
        
        # Glow effect
        glow_color = (glow_intensity, glow_intensity, glow_intensity)
        glow_text = self.title_font.render("TRY-HARD", True, glow_color)
        
        # Draw glow behind main text
        for offset in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            display.blit(glow_text, glow_rect)
        
        # Draw main title
        display.blit(title_text, title_rect)
        
        # Subtitle
        # subtitle_text = self.subtitle_font.render("The Ultimate Ninja Challenge", True, (0, 0, 0))
        # subtitle_rect = subtitle_text.get_rect(center=(display.get_width() // 2, 80))
        # display.blit(subtitle_text, subtitle_rect)
    
    def render_menu_items(self, display):
        """Render menu items with selection highlighting"""
        # Animate menu
        self.menu_animation += 0.05
        
        start_y = 110
        for i, item in enumerate(self.menu_items):
            y_pos = start_y + i * 25
            
            # Selection highlight - blinking effect like the title
            if i == self.selected_item:
                # Use the same blinking pattern as the title
                blink_intensity = int(50 + 30 * math.sin(self.title_glow))
                color = (blink_intensity, blink_intensity, blink_intensity)
            else:
                color = (0, 0, 0)
            
            # Render menu item text with stroke
            text = self.menu_font.render(item, True, color)
            text_rect = text.get_rect(center=(display.get_width() // 2, y_pos))
            
            # Draw stroke (outline) behind the text
            stroke_color = (255, 255, 255) if color == (0, 0, 0) else (0, 0, 0)
            stroke_text = self.menu_font.render(item, True, stroke_color)
            
            # Draw stroke in all 8 directions around the text
            for offset in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                stroke_rect = text_rect.copy()
                stroke_rect.x += offset[0]
                stroke_rect.y += offset[1]
                display.blit(stroke_text, stroke_rect)
            
            # Draw main text on top
            display.blit(text, text_rect)
    
    def render_game_info(self, display):
        """Render current game progress information"""
        # Use the same blinking pattern as the title for bottom text
        blink_intensity = int(50 + 30 * math.sin(self.title_glow))
        blink_color = (blink_intensity, blink_intensity, blink_intensity)
        
        # Game progress info
        progress_text = f"Level: {self.current_level} | Max: {self.max_level} | Deaths: {self.death_count}"
        progress_surface = self.small_font.render(progress_text, True, blink_color)
        progress_rect = progress_surface.get_rect(center=(display.get_width() // 2, display.get_height() - 30))
        
        # Draw stroke for progress text
        stroke_color = (255, 255, 255) if blink_intensity < 128 else (0, 0, 0)
        stroke_progress = self.small_font.render(progress_text, True, stroke_color)
        
        # Draw stroke in all 8 directions around the progress text
        for offset in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            stroke_rect = progress_rect.copy()
            stroke_rect.x += offset[0]
            stroke_rect.y += offset[1]
            display.blit(stroke_progress, stroke_rect)
        
        # Draw main progress text on top
        display.blit(progress_surface, progress_rect)
        
        # Controls hint
        controls_text = "Use ↑↓ to navigate, ENTER to select, ESC to exit"
        controls_surface = self.small_font.render(controls_text, True, blink_color)
        controls_rect = controls_surface.get_rect(center=(display.get_width() // 2, display.get_height() - 15))
        
        # Draw stroke for controls text
        stroke_controls = self.small_font.render(controls_text, True, stroke_color)
        
        # Draw stroke in all 8 directions around the controls text
        for offset in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            stroke_rect = controls_rect.copy()
            stroke_rect.x += offset[0]
            stroke_rect.y += offset[1]
            display.blit(stroke_controls, stroke_rect)
        
        # Draw main controls text on top
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
        
        # Render menu items
        self.render_menu_items(display)
        
        # Render game info
        self.render_game_info(display)
        
        # Composite displays
        display_2.blit(display, (0, 0))
    
    def handle_input(self):
        """Handle menu input and return selected action"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                    click_sound.play()
                elif event.key == pygame.K_UP:
                    self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                    click_sound.play()
                elif event.key == pygame.K_RETURN:
                    click_sound.play()
                    return self.menu_items[self.selected_item].lower().replace(" ", "_")
                elif event.key == pygame.K_ESCAPE:
                    return "exit"
        
        return None
    
    def run(self):
        """Main menu loop"""
        while True:
            # Handle input
            action = self.handle_input()
            if action:
                return action
            
            # Update animations
            self.shared_background.update()
            
            # Render
            self.render(self.screen, self.screen)  # Using screen directly for menu
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)

def main_menu(screen, clock, assets, sfx, shared_background=None):
    """Entry point for main menu"""
    menu = MainMenu(screen, clock, assets, sfx, shared_background)
    return menu.run()
