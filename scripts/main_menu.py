import pygame
import sys
import math
import random
import json

pygame.init()
pygame.mixer.init()

click_sound = pygame.mixer.Sound('data/menu.wav')
click_sound.set_volume(0.2)

class MainMenu:
    def __init__(self, screen, clock, assets, sfx):
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
        self.menu_items = ["Start Game", "Load Game", "Level Select", "Options", "About", "Exit"]
        
        # Animation variables
        self.title_glow = 0
        self.menu_animation = 0
        self.background_scroll = 0
        
        # Particle effects for menu
        self.menu_particles = []
        self.spark_effects = []
        
        # Initialize menu particles
        self.init_menu_particles()
        
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
    
    def init_menu_particles(self):
        """Initialize particle effects for the menu"""
        # Create floating particles
        for i in range(20):
            particle = {
                'pos': [random.random() * 320, random.random() * 240],
                'velocity': [random.random() * 0.5 - 0.25, random.random() * 0.5 - 0.25],
                'size': random.randint(1, 3),
                'alpha': random.randint(50, 150),
                'life': random.randint(100, 300)
            }
            self.menu_particles.append(particle)
    
    def update_particles(self):
        """Update particle effects"""
        for particle in self.menu_particles:
            particle['pos'][0] += particle['velocity'][0]
            particle['pos'][1] += particle['velocity'][1]
            particle['life'] -= 1
            
            # Wrap particles around screen
            if particle['pos'][0] < 0:
                particle['pos'][0] = 320
            elif particle['pos'][0] > 320:
                particle['pos'][0] = 0
            if particle['pos'][1] < 0:
                particle['pos'][1] = 240
            elif particle['pos'][1] > 240:
                particle['pos'][1] = 0
            
            # Respawn particles
            if particle['life'] <= 0:
                particle['pos'] = [random.random() * 320, random.random() * 240]
                particle['life'] = random.randint(100, 300)
    
    def render_background(self, display_2):
        """Render animated background with parallax effect"""
        # Animate background scroll
        self.background_scroll += 0.2
        
        # Render background layers with parallax
        parallax_factors = [0.05, 0.1, 0.2, 0.35, 0.5, 0.65]
        
        for index, layer in enumerate(self.assets['background_layers']):
            if index < len(parallax_factors):
                parallax_x = self.background_scroll * parallax_factors[index]
                
                # Get layer dimensions
                layer_width = layer.get_width()
                layer_height = layer.get_height()
                
                # Scale the background to fit screen height if needed
                screen_height = display_2.get_height()
                if layer_height < screen_height:
                    scale_factor = screen_height / layer_height
                    scaled_layer = pygame.transform.scale(layer, (int(layer_width * scale_factor), screen_height))
                    layer_width = scaled_layer.get_width()
                else:
                    scaled_layer = layer
                
                # Calculate how many horizontal tiles we need
                tiles_x = (display_2.get_width() // layer_width) + 3
                
                # Wrap the horizontal parallax offset for seamless tiling
                offset_x = -(parallax_x % layer_width)
                
                # Draw horizontally tiled background
                for tile_x in range(-1, tiles_x):
                    pos_x = offset_x + tile_x * layer_width
                    pos_y = 0
                    display_2.blit(scaled_layer, (pos_x, pos_y))
            else:
                # Fallback for extra layers
                scaled_layer = pygame.transform.scale(layer, (display_2.get_width(), display_2.get_height()))
                display_2.blit(scaled_layer, (0, 0))
    
    def render_particles(self, display):
        """Render menu particle effects"""
        for particle in self.menu_particles:
            # Create a small circle for the particle
            color = (255, 255, 255, particle['alpha'])
            pygame.draw.circle(display, color, (int(particle['pos'][0]), int(particle['pos'][1])), particle['size'])
    
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
            
            # Selection highlight
            if i == self.selected_item:
                # Animated selection glow
                glow_intensity = int(100 + 50 * math.sin(self.menu_animation * 2))
                color = (0, 0, 0)
                
                # Draw selection background
                selection_rect = pygame.Rect(display.get_width() // 2 - 80, y_pos - 5, 160, 20)
                pygame.draw.rect(display, (255, 255, 255, 100), selection_rect)
                pygame.draw.rect(display, (0, 0, 0, 150), selection_rect, 2)
            else:
                color = (0, 0, 0)
            
            # Render menu item text
            text = self.menu_font.render(item, True, color)
            text_rect = text.get_rect(center=(display.get_width() // 2, y_pos))
            display.blit(text, text_rect)
    
    def render_game_info(self, display):
        """Render current game progress information"""
        # Game progress info
        progress_text = f"Level: {self.current_level} | Max: {self.max_level} | Deaths: {self.death_count}"
        progress_surface = self.small_font.render(progress_text, True, (0, 0, 0))
        progress_rect = progress_surface.get_rect(center=(display.get_width() // 2, display.get_height() - 30))
        display.blit(progress_surface, progress_rect)
        
        # Controls hint
        controls_text = "Use ↑↓ to navigate, ENTER to select, ESC to exit"
        controls_surface = self.small_font.render(controls_text, True, (0, 0, 0))
        controls_rect = controls_surface.get_rect(center=(display.get_width() // 2, display.get_height() - 15))
        display.blit(controls_surface, controls_rect)
    
    def render(self, display, display_2):
        """Main render method"""
        # Clear displays
        display.fill((0, 0, 0, 0))
        display_2.fill((0, 0, 0))
        
        # Render background
        self.render_background(display_2)
        
        # Render particles
        self.render_particles(display)
        
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
            self.update_particles()
            
            # Render
            self.render(self.screen, self.screen)  # Using screen directly for menu
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)

def main_menu(screen, clock, assets, sfx):
    """Entry point for main menu"""
    menu = MainMenu(screen, clock, assets, sfx)
    return menu.run()
