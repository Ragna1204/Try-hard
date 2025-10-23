import pygame
import sys
import math
import random
import json
from scripts.shared_background import SharedBackground
from scripts.utils import resource_path

pygame.init()
pygame.mixer.init()

class MainMenu:
    def __init__(self, screen, clock, assets, sfx, shared_background=None):
        self.screen = screen
        self.clock = clock
        self.assets = assets
        self.sfx = sfx
        
        # Fonts
        self.title_font = pygame.font.Font(resource_path('data/fonts/ninjaline/NinjaLine.ttf'), 48) # Keep NinjaLine for title
        self.subtitle_font = pygame.font.Font(resource_path('data/fonts/AmaticSC/AmaticSC-Regular.ttf'), 24)
        self.menu_font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 32) # Use Protest_Revolution for menu options
        self.item_height = 35  # Adjust spacing for Protest_Revolution font
        self.small_font = pygame.font.Font(resource_path('data/fonts/AmaticSC/AmaticSC-Regular.ttf'), 16)
        
        # Menu state
        self.selected_item = 0
        self.hovered_item = None
        self.last_hovered_item = None  # Track previous hover for sound logic
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
            with open("saves/savefile.json", "r") as save_file:
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
        item_height = self.item_height  # Use adjusted spacing for Protest_Revolution font
        for i, item in enumerate(self.menu_items):
            y_pos = start_y + i * item_height
            base_y_pos = y_pos

            # Check for hover effect
            mouse_x, mouse_y = pygame.mouse.get_pos()
            item_rect = pygame.Rect(display.get_width() // 2 - 100, y_pos - 10, 200, 20)
            is_hovered = item_rect.collidepoint(mouse_x, mouse_y) and display.get_rect().collidepoint(mouse_x, mouse_y)

            # Update hover state
            prev_hovered = self.hovered_item
            if is_hovered:
                self.hovered_item = i
            elif self.hovered_item == i:
                self.hovered_item = None

            # Play sound only when moving to a NEW hovered item (not from intermediate states)
            if prev_hovered != self.hovered_item and self.hovered_item is not None and prev_hovered is None:
                self.sfx['menu_click'].play()

            # Selection highlight - unified hover/selection with priority to hover
            if i == self.hovered_item:
                # Hover takes priority - blink effect for consistency
                blink_intensity = int(50 + 30 * math.sin(self.title_glow))
                color = (blink_intensity, blink_intensity, blink_intensity)
                self.selected_item = i  # Update selection to hovered item
            elif i == self.selected_item:
                # Use the same blinking pattern as the title for keyboard selection
                blink_intensity = int(50 + 30 * math.sin(self.title_glow))
                color = (blink_intensity, blink_intensity, blink_intensity)
            else:
                color = (0, 0, 0)

            # Render menu item text - simplified, no outline for cleaner look
            text = self.menu_font.render(item, True, color)
            text_rect = text.get_rect(center=(display.get_width() // 2, y_pos))

            # Draw main text directly
            display.blit(text, text_rect)
    
    def render_game_info(self, display):
        """Render current game progress information - removed as requested"""
        # All game progress info removed - looking bad according to user feedback
        pass
    
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
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                    self.sfx['menu_click'].play()
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                    self.sfx['menu_click'].play()
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.sfx['menu_click'].play()
                    return self.menu_items[self.selected_item].lower().replace(" ", "_")
                elif event.key == pygame.K_ESCAPE:
                    return "exit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    start_y = 110
                    item_height = self.item_height  # Match Protest_Revolution spacing
                    for i, item in enumerate(self.menu_items):
                        y_pos = start_y + i * item_height
                        item_rect = pygame.Rect(self.screen.get_width() // 2 - 100, y_pos - 10, 200, 20)
                        if item_rect.collidepoint(mouse_x, mouse_y):
                            self.selected_item = i
                            self.sfx['menu_click'].play()
                            return self.menu_items[i].lower().replace(" ", "_")

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

def confirmation_dialog(screen, clock, message, assets=None, sfx=None, shared_background=None):
    """
    Generic confirmation dialog with Yes/No options.
    Returns True for Yes, False for No
    Use the optimized confirmation dialog - calls the main implementation from pause.py
    """
    # Import and use the optimized dialog from pause.py
    import scripts.pause
    return scripts.pause.confirmation_dialog(screen, clock, message, assets, sfx, shared_background)


def main_menu(screen, clock, assets, sfx, shared_background=None):
    """Entry point for main menu"""
    menu = MainMenu(screen, clock, assets, sfx, shared_background)
    while True:
        action = menu.run()
        if action == "exit":
            confirmed = confirmation_dialog(screen, clock, "Exit the game?", assets, sfx, shared_background)
            if confirmed:
                return action
            # If not confirmed, continue the menu loop
        else:
            return action
