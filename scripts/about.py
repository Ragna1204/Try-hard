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

        # Fonts - dark theme focused
        self.title_font = pygame.font.Font(resource_path('data/fonts/ninjaline/NinjaLine.ttf'), 36)
        self.section_font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 20)
        self.text_font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 16)
        self.caption_font = pygame.font.Font(resource_path('data/fonts/AmaticSC/AmaticSC-Regular.ttf'), 16)

        # Animation variables
        self.glow_phase = 0

        # Colors - emphasize dark red and black theme
        self.colors = {
            'title': (255, 255, 255),
            'title_glow': (180, 40, 40),
            'subtitle': (240, 100, 100),
            'text': (230, 230, 230),
            'section': (240, 100, 100),
            'separator': (120, 30, 30),
            'exit_hint': (150, 150, 150),
            'background': (0, 0, 0, 140)
        }

        # Shared background
        self.shared_background = shared_background or SharedBackground(assets)

        # Minimal content structure
        self.content = {
            "title": "TRY-HARD",
            "subtitle": "A Precision Platformer",
            "description": [
                "Master the art of movement in this challenging",
                "ninja-inspired platformer.",
                "Test your reflexes, precision, and patience as you",
                "progress through increasingly difficult challenges."
            ],
            "features": [
                "• Precise platforming mechanics",
                "• Fluid character movement",
                "• Challenge-focused gameplay"
            ],
            "credits": [
                "Developed by Samarth Sharma",
                "Manipal University Jaipur"
            ],
            "exit_hint": "Press SPACE or ESC to return"
        }

    def render_title(self, display, center_x, y_pos):
        """Render the glowing title"""
        self.glow_phase += 0.05
        glow_intensity = int(128 + 127 * math.sin(self.glow_phase))

        # Crimson glow effect
        glow_color = (glow_intensity // 2, 25, 25)
        glow_text = self.title_font.render(self.content["title"], True, glow_color)

        # Main title in dark red theme
        title_text = self.title_font.render(self.content["title"], True, self.colors['title'])

        # Center both
        title_rect = title_text.get_rect(center=(center_x, y_pos))

        # Draw glow first (slightly offset)
        for offset in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            glow_rect = title_rect.copy()
            glow_rect.centerx += offset[0]
            glow_rect.centery += offset[1]
            display.blit(glow_text, glow_rect)

        # Draw main title
        display.blit(title_text, title_rect)

    def render_text_block(self, display, center_x, start_y, lines, font, color, line_spacing=26):
        """Render a block of text with centered alignment"""
        y_offset = start_y
        for line in lines:
            if line.strip() == "":  # Empty line
                y_offset += line_spacing // 2
                continue

            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(center_x, y_offset))
            display.blit(text_surface, text_rect)
            y_offset += line_spacing
        return y_offset

    def render_section(self, display, center_x, start_y, section_title, section_content):
        """Render a complete section with title and content"""
        # Section title in crimson (only render if not empty)
        if section_title:
            title_y = start_y
            section_surface = self.section_font.render(section_title, True, self.colors['section'])
            section_rect = section_surface.get_rect(center=(center_x, title_y))
            display.blit(section_surface, section_rect)
            content_y = start_y + 30
        else:
            content_y = start_y

        # Content
        if isinstance(section_content, list):
            final_y = self.render_text_block(display, center_x, content_y, section_content, self.text_font, self.colors['text'])
        return final_y

    def render_red_separator(self, display, center_x, y_pos):
        """Render a subtle red separator line"""
        pygame.draw.rect(display, self.colors['separator'],
                        (center_x - 150, y_pos - 1, 300, 2))

    def render(self, display, display_2):
        """Main render method - dark red/black themed single page"""
        # Clear displays
        display.fill((0, 0, 0, 0))
        display_2.fill((0, 0, 0))

        # Render background using shared background
        self.shared_background.render_background(display_2)

        # Create dark overlay for readability
        overlay = pygame.Surface(display_2.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(140)  # Dark enough for contrast
        display_2.blit(overlay, (0, 0))

        # Render particles for atmosphere
        self.shared_background.render_particles(display)

        center_x = display.get_width() // 2
        current_y = 35

        # Title section
        self.render_title(display, center_x, current_y)
        current_y = 90

        # Subtitle
        subtitle_y = 75
        subtitle_text = self.section_font.render(self.content["subtitle"], True, self.colors['subtitle'])
        subtitle_rect = subtitle_text.get_rect(center=(center_x, subtitle_y))
        display.blit(subtitle_text, subtitle_rect)

        # Description section
        current_y = 110
        current_y = self.render_section(display, center_x, current_y, "", self.content["description"])
        self.render_red_separator(display, center_x, current_y + 10)

        # Features section
        current_y += 30
        current_y = self.render_section(display, center_x, current_y, "Features", self.content["features"])
        self.render_red_separator(display, center_x, current_y + 10)

        # Credits section
        current_y += 35
        current_y = self.render_section(display, center_x, current_y, "Credits", self.content["credits"])

        # Exit hint at bottom
        exit_y = display.get_height() - 25
        exit_text = self.caption_font.render(self.content["exit_hint"], True, self.colors['exit_hint'])
        exit_rect = exit_text.get_rect(center=(center_x, exit_y))
        display.blit(exit_text, exit_rect)

        # Composite displays
        display_2.blit(display, (0, 0))

    def handle_input(self):
        """Handle input and return action"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    click_sound.play()
                    return "back"
            # Removed scroll wheel handling since not scrollable anymore
        return None

    def run(self):
        """Main about screen loop - single page"""
        while True:
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

def about_screen(screen, clock, assets, sfx, shared_background=None):
    """Entry point for about screen"""
    about = AboutScreen(screen, clock, assets, sfx, shared_background)
    return about.run()
