import pygame
import sys
import math
from scripts.shared_background import SharedBackground
from scripts.utils import resource_path

pygame.init()
pygame.mixer.init()

click_sound = pygame.mixer.Sound(resource_path('data/menu.wav'))
click_sound.set_volume(0.2)

class AboutScreen:
    def __init__(self, screen, clock, assets, sfx, shared_background=None):
        self.screen = screen
        self.clock = clock
        self.assets = assets
        self.sfx = sfx
        
        # Fonts
        self.title_font = pygame.font.Font(resource_path('data/fonts/ninjaline/NinjaLine.ttf'), 32)
        self.subtitle_font = pygame.font.Font(resource_path('data/fonts/ninjaline/NinjaLine.ttf'), 18)
        self.text_font = pygame.font.Font(resource_path('data/fonts/ninjaline/NinjaLine.ttf'), 14)
        
        # Animation and scroll variables
        self.title_glow = 0
        self.scroll_y = 0
        self.scroll_speed = 0
        self.scroll_momentum = 0
        
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
            "Press SPACE or ESC to return"
        ]
        
        # Calculate content height
        self.content_height = self.calculate_content_height()

    def calculate_content_height(self):
        height = 0
        line_height = 28 # Updated line height
        for i, line in enumerate(self.about_content):
            if line == "":
                height += line_height // 2
            else:
                height += line_height
        return height

    def render_title(self, display):
        self.title_glow += 0.1
        glow_intensity = int(50 + 30 * math.sin(self.title_glow))
        
        title_text = self.title_font.render("ABOUT", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(display.get_width() // 2, 40))
        
        glow_color = (glow_intensity, glow_intensity, glow_intensity)
        glow_text = self.title_font.render("ABOUT", True, glow_color)
        
        for offset in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            display.blit(glow_text, glow_rect)
        
        display.blit(title_text, title_rect)

    def render_content(self, display):
        content_area_rect = pygame.Rect(50, 100, display.get_width() - 100, 300) # x, y, width, height
        
        # Create a subsurface for the content area with transparency
        content_surface = pygame.Surface(content_area_rect.size, pygame.SRCALPHA)
        content_surface.fill((0, 0, 0, 128)) # Semi-transparent black background

        # Calculate the actual rendering start_y within the content_surface
        internal_start_y = 20 - self.scroll_y # Padding from top of content_surface
        line_height = 28 # Increased line height
        
        for i, line in enumerate(self.about_content):
            if line == "":
                internal_start_y += line_height // 2
                continue
            
            font = self.text_font
            if i == 0:
                font = self.title_font
            elif i == 2:
                font = self.subtitle_font

            text_surface = font.render(line, True, (255, 255, 255))
            
            # Center text horizontally within the content_surface
            text_rect = text_surface.get_rect(center=(content_area_rect.width // 2, internal_start_y))
            
            # Draw only if within the visible part of the content_surface, with extra buffer for fade
            if -line_height < text_rect.y < content_area_rect.height - line_height:
                content_surface.blit(text_surface, text_rect)

            internal_start_y += line_height
        
        # Blit the content_surface onto the main display
        display.blit(content_surface, content_area_rect.topleft)

        # Render fade effect at top and bottom of the scrollable area
        # Top fade
        fade_surface_top = pygame.Surface((content_area_rect.width, 30), pygame.SRCALPHA)
        for y in range(30):
            alpha = int(255 * (y / 30))
            pygame.draw.line(fade_surface_top, (0, 0, 0, alpha), (0, y), (content_area_rect.width, y))
        display.blit(fade_surface_top, content_area_rect.topleft)

        # Bottom fade
        fade_surface_bottom = pygame.Surface((content_area_rect.width, 30), pygame.SRCALPHA)
        for y in range(30):
            alpha = int(255 * (1 - (y / 30)))
            pygame.draw.line(fade_surface_bottom, (0, 0, 0, alpha), (0, y), (content_area_rect.width, y))
        display.blit(fade_surface_bottom, (content_area_rect.x, content_area_rect.y + content_area_rect.height - 30))

    def render_scroll_indicator(self, display):
        content_area_rect = pygame.Rect(50, 100, display.get_width() - 100, 300)
        max_scroll = self.content_height - content_area_rect.height + 40 # Add some buffer for padding
        if max_scroll <= 0:
            return

        scroll_bar_height = content_area_rect.height
        indicator_height = max(20, scroll_bar_height * (content_area_rect.height / self.content_height))
        
        scroll_percentage = self.scroll_y / max_scroll
        indicator_y = content_area_rect.y + (scroll_bar_height - indicator_height) * scroll_percentage
        
        # Draw scrollbar background
        pygame.draw.rect(display, (100, 100, 100, 128), (content_area_rect.right - 25, content_area_rect.y, 10, scroll_bar_height), 0, 5)
        # Draw scrollbar indicator
        pygame.draw.rect(display, (200, 200, 200, 200), (content_area_rect.right - 25, indicator_y, 10, indicator_height), 0, 5)

    def render(self, display, display_2):
        display.fill((0, 0, 0, 0))
        display_2.fill((0, 0, 0))
        
        self.shared_background.render_background(display_2)
        self.shared_background.render_particles(display)
        
        self.render_title(display)
        self.render_content(display)
        self.render_scroll_indicator(display)
        
        display_2.blit(display, (0, 0))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    click_sound.play()
                    return "back"
            
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_speed -= event.y * 20

        return None

    def run(self):
        while True:
            action = self.handle_input()
            if action is not None:
                return action
            
            # Apply scroll momentum
            self.scroll_y += self.scroll_speed
            self.scroll_speed *= 0.8
            if abs(self.scroll_speed) < 0.1:
                self.scroll_speed = 0

            # Clamp scroll position
            max_scroll = self.content_height - 200
            self.scroll_y = max(0, min(self.scroll_y, max_scroll))
            
            self.render(self.screen, self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)

def about_screen(screen, clock, assets, sfx, shared_background=None):
    about = AboutScreen(screen, clock, assets, sfx, shared_background)
    return about.run()