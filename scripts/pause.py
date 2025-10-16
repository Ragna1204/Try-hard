import pygame
import sys
import math
from scripts.about import about_screen
from scripts.shared_background import SharedBackground
from scripts.keybindings_menu import keybindings_menu
from scripts.levels_menu import levels_menu
from scripts.utils import resource_path

pygame.init()
pygame.mixer.init()


def confirmation_dialog(screen, clock, message, assets=None, sfx=None, shared_background=None):
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

def options_menu(screen, clock, current_level, max_level, assets=None, sfx=None, shared_background=None):
    font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 20)
    title_font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 40)
    options_items = ["Key-bindings", "Volume", "Back"]
    selected_item = 0
    hovered_item = None
    title_glow = 0

    # Create shared background if not provided
    if not shared_background and assets:
        shared_background = SharedBackground(assets)

    while True:
        title_glow += 0.1
        # Clear screen
        screen.fill((0, 0, 0))

        # Render parallax background if available
        if shared_background:
            shared_background.render_background(screen)
            shared_background.render_particles(screen)
            shared_background.update()

        # Semi-transparent overlay
        overlay = pygame.Surface(screen.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        # Draw the title "Options"
        title_text = title_font.render("Options", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(title_text, title_rect)

        # Draw options menu items
        start_y = 150
        item_height = 40
        for i, item in enumerate(options_items):
            y_pos = start_y + i * item_height

            # Check for hover effect
            mouse_x, mouse_y = pygame.mouse.get_pos()
            item_rect = pygame.Rect(screen.get_width() // 2 - 100, y_pos - 10, 200, 20)
            is_hovered = item_rect.collidepoint(mouse_x, mouse_y)

            # Update hover state and play sound on hover change
            prev_hovered = hovered_item
            if is_hovered:
                hovered_item = i
            elif hovered_item == i:
                hovered_item = None

            # Play sound when hover changes (only once per hover)
            if prev_hovered != hovered_item:
                if (prev_hovered is None and hovered_item is not None) or (prev_hovered is not None and hovered_item is None):
                    sfx['menu_click'].play()

            # Unified highlight system - hover takes priority
            if i == hovered_item:
                # Hover takes priority
                blink_intensity = int(128 + 127 * math.sin(title_glow))
                color = (blink_intensity, blink_intensity, blink_intensity)
                selected_item = i  # Update selection to hovered item
            elif i == selected_item:
                # Blink effect for keyboard selection
                blink_intensity = int(128 + 127 * math.sin(title_glow))
                color = (blink_intensity, blink_intensity, blink_intensity)
            else:
                color = (255, 255, 255)

            # Render text
            text = font.render(item, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, y_pos))
            screen.blit(text, text_rect)

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(options_items)
                    sfx['menu_click'].play()
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(options_items)
                    sfx['menu_click'].play()
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    sfx['menu_click'].play()
                    if selected_item == 0:  # Key-bindings
                        keybindings_menu(screen, clock, assets, sfx, shared_background)
                    elif selected_item == 1:  # Volume
                        volume_result = volume_menu(screen, clock, sfx, shared_background)
                        if volume_result != "back":
                            return volume_result  # shouldn't happen, but handle
                    elif selected_item == 2:  # Back
                        return "back"
                elif event.key == pygame.K_ESCAPE:  # Escape to go back
                    return "back"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    for i, item in enumerate(options_items):
                        y_pos = start_y + i * item_height
                        item_rect = pygame.Rect(screen.get_width() // 2 - 100, y_pos - 10, 200, 20)
                        if item_rect.collidepoint(mouse_x, mouse_y):
                            if i == 0:  # Key-bindings
                                result = keybindings_menu(screen, clock, assets, sfx, shared_background)
                                if result != "back":
                                    return result  # handle if not back
                            elif i == 1:  # Volume
                                volume_result = volume_menu(screen, clock, sfx, shared_background)
                                if volume_result != "back":
                                    return volume_result
                            elif i == 2:  # Back
                                return "back"
                            break

        clock.tick(60)


def volume_menu(screen, clock, sfx, shared_background=None):
    """Volume control menu with sliders for music and effects"""
    font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 20)
    title_font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 40)
    small_font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 16)

    # Initialize base volumes if not already done
    if not hasattr(volume_menu, 'base_sfx_volumes'):
        volume_menu.base_sfx_volumes = {key: sound.get_volume() for key, sound in sfx.items() if hasattr(sound, 'get_volume')}
    if not hasattr(volume_menu, 'base_music_volume'):
        volume_menu.base_music_volume = pygame.mixer.music.get_volume()

    # Set current slider positions based on current volumes
    # This logic is a bit tricky because we can't perfectly reverse the scaling
    # A simpler approach is to store the master volume levels themselves.
    if not hasattr(volume_menu, 'master_music_vol'):
        volume_menu.master_music_vol = 1.0
    if not hasattr(volume_menu, 'master_effects_vol'):
        volume_menu.master_effects_vol = 1.0

    music_volume = volume_menu.master_music_vol
    effects_volume = volume_menu.master_effects_vol

    selected_slider = 0  # 0 for music, 1 for effects
    title_glow = 0

    slider_width = 200
    slider_height = 20
    slider_x = screen.get_width() // 2 - slider_width // 2

    music_group_y = 120
    effects_group_y = 220
    group_height = 80

    def apply_volumes():
        # Apply music volume
        if hasattr(pygame.mixer.music, 'set_volume'):
            pygame.mixer.music.set_volume(volume_menu.base_music_volume * music_volume)
        
        # Apply SFX volume
        if sfx:
            for key, sound in sfx.items():
                if key in volume_menu.base_sfx_volumes:
                    sound.set_volume(volume_menu.base_sfx_volumes[key] * effects_volume)
        
        # Store master volumes
        volume_menu.master_music_vol = music_volume
        volume_menu.master_effects_vol = effects_volume

    while True:
        title_glow += 0.1
        screen.fill((0, 0, 0))

        if shared_background:
            shared_background.render_background(screen)
            shared_background.render_particles(screen)
            shared_background.update()

        overlay = pygame.Surface(screen.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        title_text = title_font.render("Volume Settings", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(title_text, title_rect)

        # Music Volume Group
        music_group_rect = pygame.Rect(slider_x - 20, music_group_y, slider_width + 40, group_height)
        if selected_slider == 0:
            blink_intensity = int(128 + 127 * math.sin(title_glow))
            pygame.draw.rect(screen, (0, 0, 0), music_group_rect.inflate(4, 4))
            pygame.draw.rect(screen, (blink_intensity, blink_intensity, blink_intensity), music_group_rect, 2)
        else:
            pygame.draw.rect(screen, (0, 0, 0), music_group_rect.inflate(2, 2))
            pygame.draw.rect(screen, (255, 255, 255), music_group_rect, 1)

        music_label_color = (blink_intensity, blink_intensity, blink_intensity) if selected_slider == 0 else (255, 255, 255)
        music_text = font.render("Music Volume", True, music_label_color)
        music_rect = music_text.get_rect(center=(screen.get_width() // 2, music_group_y + 20))
        screen.blit(music_text, music_rect)

        music_slider_y = music_group_y + 40
        pygame.draw.rect(screen, (100, 100, 100), (slider_x, music_slider_y, slider_width, slider_height))
        handle_x_music = slider_x + int(music_volume * (slider_width - 10))
        pygame.draw.rect(screen, (255, 255, 255), (handle_x_music, music_slider_y - 2, 10, slider_height + 4))
        music_percent = int(music_volume * 100)
        percent_text_music = small_font.render(f"{music_percent}%", True, music_label_color)
        percent_rect_music = percent_text_music.get_rect(center=(screen.get_width() // 2, music_slider_y + 35))
        screen.blit(percent_text_music, percent_rect_music)

        # Effects Volume Group
        effects_group_rect = pygame.Rect(slider_x - 20, effects_group_y, slider_width + 40, group_height)
        if selected_slider == 1:
            blink_intensity = int(128 + 127 * math.sin(title_glow))
            pygame.draw.rect(screen, (0, 0, 0), effects_group_rect.inflate(4, 4))
            pygame.draw.rect(screen, (blink_intensity, blink_intensity, blink_intensity), effects_group_rect, 2)
        else:
            pygame.draw.rect(screen, (0, 0, 0), effects_group_rect.inflate(2, 2))
            pygame.draw.rect(screen, (255, 255, 255), effects_group_rect, 1)

        effects_label_color = (blink_intensity, blink_intensity, blink_intensity) if selected_slider == 1 else (255, 255, 255)
        effects_text = font.render("Effects Volume", True, effects_label_color)
        effects_rect = effects_text.get_rect(center=(screen.get_width() // 2, effects_group_y + 20))
        screen.blit(effects_text, effects_rect)

        effects_slider_y = effects_group_y + 40
        pygame.draw.rect(screen, (100, 100, 100), (slider_x, effects_slider_y, slider_width, slider_height))
        handle_x_effects = slider_x + int(effects_volume * (slider_width - 10))
        pygame.draw.rect(screen, (255, 255, 255), (handle_x_effects, effects_slider_y - 2, 10, slider_height + 4))
        effects_percent = int(effects_volume * 100)
        percent_text_effects = small_font.render(f"{effects_percent}%", True, effects_label_color)
        percent_rect_effects = percent_text_effects.get_rect(center=(screen.get_width() // 2, effects_slider_y + 35))
        screen.blit(percent_text_effects, percent_rect_effects)

        back_text = small_font.render("Press ESC to go back", True, (200, 200, 200))
        back_rect = back_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30))
        screen.blit(back_text, back_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    selected_slider = (selected_slider - 1) % 2
                    sfx['menu_click'].play()
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    selected_slider = (selected_slider + 1) % 2
                    sfx['menu_click'].play()
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    if selected_slider == 0:
                        music_volume = max(0, music_volume - 0.1)
                    else:
                        effects_volume = max(0, effects_volume - 0.1)
                    apply_volumes()
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    if selected_slider == 0:
                        music_volume = min(1, music_volume + 0.1)
                    else:
                        effects_volume = min(1, effects_volume + 0.1)
                    apply_volumes()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if music_group_rect.collidepoint(mouse_x, mouse_y):
                        selected_slider = 0
                        music_volume = max(0, min(1, (mouse_x - slider_x) / slider_width))
                        if hasattr(pygame.mixer.music, 'set_volume'):
                            pygame.mixer.music.set_volume(music_volume)
                    elif effects_group_rect.collidepoint(mouse_x, mouse_y):
                        selected_slider = 1
                        effects_volume = max(0, min(1, (mouse_x - slider_x) / slider_width))
                        if sfx:
                            for sound in sfx.values():
                                if hasattr(sound, 'set_volume'):
                                    sound.set_volume(effects_volume)
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                if music_group_rect.collidepoint(mouse_x, mouse_y):
                    selected_slider = 0
                elif effects_group_rect.collidepoint(mouse_x, mouse_y):
                    selected_slider = 1

                if event.buttons[0]:
                    if selected_slider == 0:
                        music_volume = max(0, min(1, (mouse_x - slider_x) / slider_width))
                        if hasattr(pygame.mixer.music, 'set_volume'):
                            pygame.mixer.music.set_volume(music_volume)
                    elif selected_slider == 1:
                        effects_volume = max(0, min(1, (mouse_x - slider_x) / slider_width))
                        if sfx:
                            for sound in sfx.values():
                                if hasattr(sound, 'set_volume'):
                                    sound.set_volume(effects_volume)

        clock.tick(60)





def about_menu(screen, clock, sfx):
    normal_font = pygame.font.Font(None, 20)
    font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 20)
    title_font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 40)

    while True:
        screen.fill((0, 0, 0, 180))  # Semi-transparent background

        # Draw the title "About"
        title_text = title_font.render("About", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(title_text, title_rect)

        # Display developer and studio information
        developer_text = font.render("Developed by : Samarth Sharma", True, (255, 255, 255))
        studio_text = font.render("Studio : 105", True, (255, 255, 255))

        developer_rect = developer_text.get_rect(center=(screen.get_width() // 2, 150))
        studio_rect = studio_text.get_rect(center=(screen.get_width() // 2, 180))

        screen.blit(developer_text, developer_rect)
        screen.blit(studio_text, studio_rect)

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sfx['menu_click'].play()                    # Pressing ESC will return to pause menu
                    return "back"

        clock.tick(60)


def pause_menu(screen, clock, current_level, max_level, assets=None, sfx=None, shared_background=None):
    font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 28) # Use Protest_Revolution for pause menu options
    title_font = pygame.font.Font(resource_path('data/fonts/ninjaline/NinjaLine.ttf'), 48) # Use NinjaLine for title consistency
    menu_items = ["Resume", "Main Menu", "Options", "Levels", "About", "Exit"]
    selected_item = 0
    hovered_item = None
    prev_hovered_item = None  # Track previous hover for sound logic
    title_glow = 0

    while True:
        title_glow += 0.1
        screen.fill((0, 0, 0, 180))  # Semi-transparent background

        # Draw the title "TRY-HARD"
        title_color = (255, 255, 255)
        title_text = title_font.render("TRY-HARD", True, title_color)
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(title_text, title_rect)

        # Draw menu options with hover and selection effects
        start_y = 150
        item_height = 30
        for i, item in enumerate(menu_items):
            y_pos = start_y + i * item_height
            base_y_pos = y_pos

            # Check for hover effect
            mouse_x, mouse_y = pygame.mouse.get_pos()
            item_rect = pygame.Rect(screen.get_width() // 2 - 100, y_pos - 10, 200, 20)
            is_hovered = item_rect.collidepoint(mouse_x, mouse_y)
            if is_hovered:
                hovered_item = i
            elif hovered_item == i:
                hovered_item = None

            # Track hover changes for sound
            if prev_hovered_item != hovered_item:
                prev_hovered_item = hovered_item
                # Play sound only when entering a new hover
                if hovered_item is not None:
                    sfx['menu_click'].play()

            # Unified highlight system - hover takes priority
            if i == hovered_item:
                # Hover takes priority
                blink_intensity = int(128 + 127 * math.sin(title_glow))
                color = (blink_intensity, blink_intensity, blink_intensity)
                selected_item = i  # Update selection to hovered item
            elif i == selected_item:
                # Blink effect for keyboard selection
                blink_intensity = int(128 + 127 * math.sin(title_glow))
                color = (blink_intensity, blink_intensity, blink_intensity)
            else:
                color = (160, 160, 160)

            # Render text
            text = font.render(item, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, y_pos))
            screen.blit(text, text_rect)

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_item = (selected_item + 1) % len(menu_items)
                    sfx['menu_click'].play()
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_item = (selected_item - 1) % len(menu_items)
                    sfx['menu_click'].play()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    sfx['menu_click'].play()
                    if selected_item == 0:  # Resume
                        return current_level
                    elif selected_item == 1:  # Main Menu
                        confirmed = confirmation_dialog(screen, clock, "Return to Main Menu?\nUnsaved progress will be lost.", assets, sfx, shared_background)
                        if confirmed:
                            return "menu"
                    elif selected_item == 2:  # Options
                        result = options_menu(screen, clock, current_level, max_level, assets, sfx, shared_background)
                        if result != "back":
                            return result
                    elif selected_item == 3:  # Levels
                        result = levels_menu(screen, clock, current_level, max_level, sfx)
                        if result != "back":
                            return result
                    elif selected_item == 4:  # About
                        if assets and sfx and shared_background:
                            result = about_screen(screen, clock, assets, sfx, shared_background)
                            if result != "back":
                                return result  # could be "exit"
                        else:
                            result = about_menu(screen, clock, sfx)
                            if result != "back":
                                return result
                    elif selected_item == 5:  # Exit
                        confirmed = confirmation_dialog(screen, clock, "Exit the game?\nUnsaved progress will be lost.", assets, sfx, shared_background)
                        if confirmed:
                            pygame.quit()
                            sys.exit()
                elif event.key == pygame.K_ESCAPE:  # Escape to resume game
                    return current_level

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    for i, item in enumerate(menu_items):
                        y_pos = start_y + i * item_height
                        item_rect = pygame.Rect(screen.get_width() // 2 - 100, y_pos - 10, 200, 20)
                        if item_rect.collidepoint(mouse_x, mouse_y):
                            selected_item = i
                            sfx['menu_click'].play()
                            if selected_item == 0:  # Resume
                                return current_level
                            elif selected_item == 1:  # Main Menu
                                confirmed = confirmation_dialog(screen, clock, "Return to Main Menu?\nUnsaved progress will be lost.", assets, sfx, shared_background)
                                if confirmed:
                                    return "menu"
                            elif selected_item == 2:  # Options
                                result = options_menu(screen, clock, current_level, max_level, assets, sfx, shared_background)
                                if result != "back":
                                    return result
                            elif selected_item == 3:  # Levels
                                result = levels_menu(screen, clock, current_level, max_level, sfx)
                                if result != "back":
                                    return result
                            elif selected_item == 4:  # About
                                if assets and sfx and shared_background:
                                    result = about_screen(screen, clock, assets, sfx, shared_background)
                                    if result != "back":
                                        return result  # could be "exit"
                                else:
                                    result = about_menu(screen, clock, sfx)
                                    if result != "back":
                                        return result
                            elif selected_item == 5:  # Exit
                                confirmed = confirmation_dialog(screen, clock, "Exit the game?\nUnsaved progress will be lost.", assets, sfx, shared_background)
                                if confirmed:
                                    pygame.quit()
                                    sys.exit()

        clock.tick(60)
