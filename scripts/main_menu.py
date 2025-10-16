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
    """
    # Use the optimized confirmation dialog from pause.py
    def confirmation_dialog_internal(screen, clock, message, assets=None, sfx=None, shared_background=None):
        """
        Generic confirmation dialog with Yes/No options.
        Returns True for Yes, False for No
        """
        font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 24)
        title_font = pygame.font.Font(resource_path('data/fonts/ninjaline/NinjaLine.ttf'), 32)
        dialog_width = 450
        dialog_height = 220
        dialog_x = (screen.get_width() - dialog_width) // 2
        dialog_y = (screen.get_height() - dialog_height) // 2

        options = ["Yes", "No"]
        selected_item = 1  # Start with No selected for safety
        hovered_item = None
        title_glow = 0

        # Create shared background if not provided
        if not shared_background and assets:
            shared_background = SharedBackground(assets)

        # Pre-calculate static effects to eliminate per-frame lag
        # Create vignette surface once
        vignette = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        center_x, center_y = screen.get_width() // 2, screen.get_height() // 2
        max_distance = math.sqrt(center_x**2 + center_y**2)

        # Optimized vignette creation using circular gradients
        for radius in range(0, int(max_distance), 2):
            alpha = int(100 * (radius / max_distance))
            if alpha > 255:
                alpha = 255
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (center_x, center_y), radius, 2)

        # Pre-calculate dialog background gradient
        dialog_bg = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        for i in range(dialog_height):
            alpha = int(220 + 35 * math.sin(i * math.pi / dialog_height))
            red_intensity = int(20 + 25 * math.sin(i * math.pi / dialog_height))
            pygame.draw.line(dialog_bg, (red_intensity, 0, 0, alpha), (0, i), (dialog_width, i))

        # Pre-calculate border glow
        border_glow = pygame.Surface((dialog_width + 8, dialog_height + 8), pygame.SRCALPHA)
        pygame.draw.rect(border_glow, (255, 50, 50, 100),
                        (0, 0, dialog_width + 8, dialog_height + 8), 0, border_radius=12)

        # Pre-calculate inner shadow
        inner_shadow = pygame.Surface((dialog_width - 8, dialog_height - 8), pygame.SRCALPHA)
        for i in range(dialog_height - 8):
            alpha = max(0, int(35 * (1 - i / (dialog_height - 8))))
            pygame.draw.line(inner_shadow, (0, 0, 0, alpha), (0, i), (dialog_width - 8, i))

        while True:
            title_glow += 0.1

            # Clear screen
            screen.fill((0, 0, 0))

            # Render parallax background if available
            if shared_background:
                shared_background.render_background(screen)
                shared_background.render_particles(screen)
                shared_background.update()

            # Create elegant semi-transparent overlay (simplified)
            overlay = pygame.Surface(screen.get_size())
            overlay.fill((0, 0, 0))
            overlay.set_alpha(160)
            screen.blit(overlay, (0, 0))

            # Blit pre-calculated vignette
            screen.blit(vignette, (0, 0))

            # Blit pre-calculated effects
            screen.blit(border_glow, (dialog_x - 4, dialog_y - 4))
            screen.blit(dialog_bg, (dialog_x, dialog_y))
            screen.blit(inner_shadow, (dialog_x + 4, dialog_y + 4))

            # Draw red border with rounded corners
            border_color = (200, 50, 50)  # Dark red border
            pygame.draw.rect(screen, border_color, (dialog_x, dialog_y, dialog_width, dialog_height), 2, border_radius=8)

            # Draw centered warning/exclamation icon at top with red glow
            icon_text = title_font.render("!", True, (255, 100, 100))  # Red exclamation
            icon_rect = icon_text.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 15 + 12))
            screen.blit(icon_text, icon_rect)

            # Draw message with better spacing
            message_lines = message.split('\n')
            y_offset = dialog_y + 50
            for line in message_lines:
                msg_text = font.render(line, True, (240, 240, 250))
                msg_rect = msg_text.get_rect(center=(screen.get_width() // 2, y_offset))
                screen.blit(msg_text, msg_rect)
                y_offset += 32

            # Draw elegant option buttons
            start_y = dialog_y + 160
            item_spacing = 100
            button_width = 80
            button_height = 32

            for i, option in enumerate(options):
                x_pos = dialog_x + dialog_width // 2 + (i - 0.5) * item_spacing

                # Create button background
                button_rect = pygame.Rect(x_pos - button_width // 2, start_y - button_height // 2, button_width, button_height)
                is_hovered = button_rect.collidepoint(pygame.mouse.get_pos())

                # Update hover state immediately (no prev_hovered tracking for performance)
                prev_hovered = hovered_item
                hovered_item = i if is_hovered else hovered_item if hovered_item == i else None

                # Play sound only when entering a new hover (simplified for performance)
                if prev_hovered != hovered_item and hovered_item is not None and prev_hovered is None:
                    if sfx:
                        sfx['menu_click'].play()

                # Update selection to hovered item immediately
                if hovered_item is not None:
                    selected_item = hovered_item

                # Red/black button styling
                if i == selected_item or i == hovered_item:
                    if selected_item == i and hovered_item == i:
                        # Both selected and hovered - brightest red
                        button_color = (180, 60, 60, 240)
                        glow_color = (255, 100, 100, 120)
                    elif selected_item == i:
                        # Selected only
                        button_color = (140, 40, 40, 230)
                        glow_color = (220, 80, 80, 100)
                    else:
                        # Hovered only
                        button_color = (160, 50, 50, 235)
                        glow_color = (240, 90, 90, 110)
                else:
                    button_color = (60, 20, 20, 220)
                    glow_color = (0, 0, 0, 0)

                # Draw button glow (simplified)
                if glow_color[3] > 0:
                    pygame.draw.rect(screen, glow_color, button_rect.inflate(6, 6), border_radius=8)

                # Draw button background
                pygame.draw.rect(screen, button_color, button_rect, border_radius=6)

                # Draw red/black button border
                border_color = (255, 150, 150) if i == selected_item else (150, 50, 50)
                pygame.draw.rect(screen, border_color, button_rect, 1, border_radius=6)

                # Draw option text
                text_color = (255, 255, 255) if i == selected_item or i == hovered_item else (220, 220, 230)
                option_text = font.render(option, True, text_color)
                option_rect = option_text.get_rect(center=(x_pos, start_y))
                screen.blit(option_text, option_rect)

            pygame.display.flip()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False  # Treat quit as No
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        selected_item = (selected_item - 1) % len(options)
                        hovered_item = None  # Reset hover when using keyboard
                        if sfx:
                            sfx['menu_click'].play()
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        selected_item = (selected_item + 1) % len(options)
                        hovered_item = None  # Reset hover when using keyboard
                        if sfx:
                            sfx['menu_click'].play()
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        if sfx:
                            sfx['menu_click'].play()
                        return selected_item == 0  # Yes = True, No = False
                    elif event.key == pygame.K_ESCAPE:
                        return False  # ESC = No

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_x, mouse_y = event.pos
                        for i, option in enumerate(options):
                            x_pos = dialog_x + dialog_width // 2 + (i - 0.5) * item_spacing
                            button_rect = pygame.Rect(x_pos - button_width // 2, start_y - button_height // 2, button_width, button_height)
                            if button_rect.collidepoint(mouse_x, mouse_y):
                                if sfx:
                                    sfx['menu_click'].play()
                                return i == 0  # Yes = True, No = False

            clock.tick(60)

    return confirmation_dialog_internal(screen, clock, message, assets, sfx, shared_background)


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
