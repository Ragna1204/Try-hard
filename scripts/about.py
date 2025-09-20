import pygame
import sys
import math
import random
from scripts.shared_background import SharedBackground

pygame.init()
pygame.mixer.init()

click_sound = pygame.mixer.Sound('data/menu.wav')
click_sound.set_volume(0.2)

class AboutScreen:
    def __init__(self, screen, clock, assets, sfx, shared_background=None):
        self.screen = screen
        self.clock = clock
        self.assets = assets
        self.sfx = sfx
        
        # Fonts
        self.title_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 32)
        self.subtitle_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 18)
        self.text_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 14)
        self.small_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 12)
        
        # Animation variables
        self.title_glow = 0
        self.background_animation = 0
        
        # Shared background
        self.shared_background = shared_background or SharedBackground(assets)
        
        # About content
        self.about_content = [
            "TRY-HARD",
            "",
            "A Precision Platformer",
            "",
            "Master the art of movement in this challenging",
            "ninja-themed platformer. Navigate through",
            "dangerous levels filled with enemies and obstacles.",
            "",
            "Features:",
            "• Fluid movement mechanics",
            "• Challenging level design",
            "• Multiple save slots",
            "• Progressive difficulty",
            "",
            "Controls:",
            "A/D - Move",
            "SPACE - Jump",
            "SHIFT - Dash",
            "ESC - Pause",
            "",
            "Test your skills and see how far you can go!",
            "",
            "Press ESC to return"
        ]
    
    
    def render_title(self, display):
        """Render animated title"""
        self.title_glow += 0.1
        glow_intensity = int(50 + 30 * math.sin(self.title_glow))
        
        title_text = self.title_font.render("ABOUT", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(display.get_width() // 2, 30))
        
        # Glow effect
        glow_color = (glow_intensity, glow_intensity, glow_intensity)
        glow_text = self.title_font.render("ABOUT", True, glow_color)
        
        # Draw glow behind main text
        for offset in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            display.blit(glow_text, glow_rect)
        
        # Draw main title
        display.blit(title_text, title_rect)
    
    def render_content(self, display):
        """Render about content"""
        start_y = 100  # Moved down to avoid collision with title
        line_height = 20  # Increased line height for better spacing
        padding = 20  # Add padding to text
        
        for i, line in enumerate(self.about_content):
            if line == "":
                start_y += line_height // 2
                continue
            
            # Choose font based on content
            if i == 0:  # Game title
                font = self.title_font
            elif i == 2:  # Subtitle (index 2 because of empty line)
                font = self.subtitle_font
            elif line.startswith("•") or line.startswith("Controls:") or line.startswith("Features:"):
                font = self.text_font
            else:
                font = self.text_font
            
            # Use same color for all text
            color = (255, 255, 255)
            
            # Render text with padding
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(display.get_width() // 2, start_y))
            
            # Draw stroke for better visibility
            stroke_color = (0, 0, 0)
            stroke_surface = font.render(line, True, stroke_color)
            
            # Draw stroke in all 8 directions
            for offset in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                stroke_rect = text_rect.copy()
                stroke_rect.x += offset[0]
                stroke_rect.y += offset[1]
                display.blit(stroke_surface, stroke_rect)
            
            # Draw main text
            display.blit(text_surface, text_rect)
            
            start_y += line_height
    
    def render(self, display, display_2):
        """Main render method"""
        # Clear displays
        display.fill((0, 0, 0, 0))
        display_2.fill((0, 0, 0))
        
        # Render parallax background
        self.shared_background.render_background(display_2)
        
        # Render particles using shared background
        self.shared_background.render_particles(display)
        
        # Render title
        self.render_title(display)
        
        # Render content
        self.render_content(display)
        
        # Composite displays
        display_2.blit(display, (0, 0))
    
    def handle_input(self):
        """Handle input and return selected action"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    click_sound.play()
                    return "back"
        
        return None
    
    def run(self):
        """Main about screen loop"""
        while True:
            # Handle input
            action = self.handle_input()
            if action is not None:
                return action
            
            # Render
            self.render(self.screen, self.screen)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)

def about_screen(screen, clock, assets, sfx, shared_background=None):
    """Entry point for about screen"""
    about = AboutScreen(screen, clock, assets, sfx, shared_background)
    return about.run()
