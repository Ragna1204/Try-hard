import pygame
import sys
import math
from scripts.about import about_screen
from scripts.shared_background import SharedBackground

pygame.init()
pygame.mixer.init()

click_sound = pygame.mixer.Sound('data/menu.wav')
click_sound.set_volume(0.2)

def options_menu(screen, clock, current_level, max_level, assets=None, sfx=None, shared_background=None):
    font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 20)
    title_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 40)
    options_items = ["Key-bindings", "Volume", "Back"]
    selected_item = 0
    
    # Create shared background if not provided
    if not shared_background and assets:
        shared_background = SharedBackground(assets)

    while True:
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
        for i, item in enumerate(options_items):
            color = (255, 255, 255) if i == selected_item else (200, 200, 200)
            text = font.render(item, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, 150 + i * 30))
            screen.blit(text, text_rect)

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(options_items)
                    click_sound.play()
                elif event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(options_items)
                    click_sound.play()
                elif event.key == pygame.K_RETURN:
                    click_sound.play()
                    if selected_item == 0:  # Key-bindings
                        key_bindings_menu(screen, clock)
                    elif selected_item == 1:  # Volume
                        volume_menu(screen, clock, sfx, shared_background)
                    elif selected_item == 2:  # Back
                        return current_level
                elif event.key == pygame.K_ESCAPE:  # Escape to go back
                    return current_level

        clock.tick(60)


def volume_menu(screen, clock, sfx, shared_background=None):
    """Volume control menu with sliders for music and effects"""
    font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 20)
    title_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 40)
    small_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 16)

    music_volume = 1.0  # Default music volume
    effects_volume = 1.0  # Default effects volume

    selected_slider = 0  # 0 for music, 1 for effects
    title_glow = 0

    slider_width = 200
    slider_height = 20
    slider_x = screen.get_width() // 2 - slider_width // 2

    # Group music and effects controls for alignment and boxing
    music_group_y = 120
    effects_group_y = 220
    group_height = 80

    if hasattr(pygame.mixer.music, 'set_volume'):
        pygame.mixer.music.set_volume(music_volume)

    if sfx:
        for sound in sfx.values():
            if hasattr(sound, 'set_volume'):
                sound.set_volume(effects_volume)

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
            pygame.draw.rect(screen, (blink_intensity, blink_intensity, blink_intensity), music_group_rect, 2)
        else:
            pygame.draw.rect(screen, (255, 255, 255), music_group_rect, 1)

        music_label_color = (blink_intensity, blink_intensity, blink_intensity) if selected_slider == 0 else (255, 255, 255)
        music_text = font.render("Music Volume", True, music_label_color)
        music_rect = music_text.get_rect(center=(screen.get_width() // 2, music_group_y + 20))
        screen.blit(music_text, music_rect)

        music_slider_y = music_group_y + 40
        pygame.draw.rect(screen, (100, 100, 100), (slider_x, music_slider_y, slider_width, slider_height))
        pygame.draw.rect(screen, (255, 255, 255), (slider_x, music_slider_y, slider_width, slider_height), 2)
        handle_x_music = slider_x + int(music_volume * (slider_width - 10))
        pygame.draw.rect(screen, (255, 255, 255), (handle_x_music, music_slider_y - 2, 10, slider_height + 4))
        music_percent = int(music_volume * 100)
        percent_text_music = small_font.render(f"{music_percent}%", True, music_label_color)
        percent_rect_music = percent_text_music.get_rect(center=(screen.get_width() // 2, music_slider_y + 30))
        screen.blit(percent_text_music, percent_rect_music)

        # Effects Volume Group
        effects_group_rect = pygame.Rect(slider_x - 20, effects_group_y, slider_width + 40, group_height)
        if selected_slider == 1:
            blink_intensity = int(128 + 127 * math.sin(title_glow))
            pygame.draw.rect(screen, (blink_intensity, blink_intensity, blink_intensity), effects_group_rect, 2)
        else:
            pygame.draw.rect(screen, (255, 255, 255), effects_group_rect, 1)

        effects_label_color = (blink_intensity, blink_intensity, blink_intensity) if selected_slider == 1 else (255, 255, 255)
        effects_text = font.render("Effects Volume", True, effects_label_color)
        effects_rect = effects_text.get_rect(center=(screen.get_width() // 2, effects_group_y + 20))
        screen.blit(effects_text, effects_rect)

        effects_slider_y = effects_group_y + 40
        pygame.draw.rect(screen, (100, 100, 100), (slider_x, effects_slider_y, slider_width, slider_height))
        pygame.draw.rect(screen, (255, 255, 255), (slider_x, effects_slider_y, slider_width, slider_height), 2)
        handle_x_effects = slider_x + int(effects_volume * (slider_width - 10))
        pygame.draw.rect(screen, (255, 255, 255), (handle_x_effects, effects_slider_y - 2, 10, slider_height + 4))
        effects_percent = int(effects_volume * 100)
        percent_text_effects = small_font.render(f"{effects_percent}%", True, effects_label_color)
        percent_rect_effects = percent_text_effects.get_rect(center=(screen.get_width() // 2, effects_slider_y + 30))
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
                    return
                if event.key == pygame.K_UP:
                    selected_slider = (selected_slider - 1) % 2
                    click_sound.play()
                if event.key == pygame.K_DOWN:
                    selected_slider = (selected_slider + 1) % 2
                    click_sound.play()
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


def levels_menu(screen, clock, current_level, max_level):
    font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 20)
    title_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 40)

    levels_per_row = 5
    total_levels = 10  # Adjust this to match your total number of levels
    selected_level = current_level

    while True:
        screen.fill((0, 0, 0, 180))  # Semi-transparent background

        # Draw the title "Levels"
        title_text = title_font.render("Levels", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(title_text, title_rect)

        # Draw level numbers
        for i in range(total_levels):
            level_number = i + 1
            row = i // levels_per_row
            col = i % levels_per_row

            x = screen.get_width() // 2 + (col - 2) * 60  # Center the grid
            y = 150 + row * 40

            # Determine color based on whether the level is cleared
            if level_number <= max_level:
                color = (255, 255, 255)  # White for cleared levels
            else:
                color = (160, 160, 160)  # Off-white for uncleared levels

            # Highlight the selected level
            if level_number == selected_level:
                pygame.draw.rect(screen, (100, 100, 255), (x - 15, y - 15, 30, 30), 2)

            # Highlight the current level with a box
            if level_number == current_level:
                pygame.draw.rect(screen, (255, 255, 0), (x - 20, y - 20, 40, 40), 2)

            level_text = font.render(str(level_number), True, color)
            level_rect = level_text.get_rect(center=(x, y))
            screen.blit(level_text, level_rect)

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and selected_level > 0:
                    selected_level -= 1
                    click_sound.play()
                elif event.key == pygame.K_RIGHT and selected_level < total_levels - 1:
                    selected_level += 1
                    click_sound.play()
                elif event.key == pygame.K_UP and selected_level >= levels_per_row:
                    selected_level -= levels_per_row
                    click_sound.play()
                elif event.key == pygame.K_DOWN and selected_level < total_levels - levels_per_row:
                    selected_level += levels_per_row
                    click_sound.play()
                elif event.key == pygame.K_RETURN:
                    if selected_level <= max_level:
                        click_sound.play()
                        return selected_level  # Return the selected level if it's cleared
                elif event.key == pygame.K_ESCAPE:
                    return current_level  # Return the current level if no selection was made

        clock.tick(60)

def key_bindings_menu(screen, clock):
    font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 20)
    title_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 40)
    bindings = [
        "Move Left : A",
        "Move Right : D",
        "Jump : Space",
        "Dash/Attack : L_Shift",
        "Wall jump : Space (while on wall)",
        "Pause : Esc",
        "Toggle fullscreen : F"
    ]

    while True:
        screen.fill((0, 0, 0, 180))  # Semi-transparent background

        # Draw the title "Key-bindings"
        title_text = title_font.render("Key-bindings", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(title_text, title_rect)

        # Display each key-binding
        for i, binding in enumerate(bindings):
            text = font.render(binding, True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, 150 + i * 30))
            screen.blit(text, text_rect)

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Pressing ESC will return to options menu
                    return

        clock.tick(60)


def about_menu(screen, clock):
    normal_font = pygame.font.Font(None, 20)
    font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 20)
    title_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 40)

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
                    click_sound.play()                    # Pressing ESC will return to pause menu
                    return

        clock.tick(60)


def pause_menu(screen, clock, current_level, max_level, assets=None, sfx=None, shared_background=None):
    font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 20)
    title_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 48)
    menu_items = ["Resume", "Main Menu", "Options", "Levels", "About", "Exit"]
    selected_item = 0

    while True:
        screen.fill((0, 0, 0, 180))  # Semi-transparent background

        # Draw the title "TRY-HARD"
        title_text = title_font.render("TRY-HARD", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(title_text, title_rect)

        # Draw menu options
        for i, item in enumerate(menu_items):
            color = (255, 255, 255) if i == selected_item else (160, 160, 160)
            text = font.render(item, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, 150 + i * 30))
            screen.blit(text, text_rect)

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(menu_items)
                    click_sound.play()
                elif event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(menu_items)
                    click_sound.play()
                elif event.key == pygame.K_RETURN:
                    click_sound.play()
                    if selected_item == 0:  # Resume
                        return current_level
                    elif selected_item == 1:  # Main Menu
                        return "menu"
                    elif selected_item == 2:  # Options
                        return options_menu(screen, clock, current_level, max_level, assets, sfx, shared_background)
                    elif selected_item == 3:  # Levels
                        return levels_menu(screen, clock, current_level, max_level)
                    elif selected_item == 4:  # About
                        if assets and sfx and shared_background:
                            about_screen(screen, clock, assets, sfx, shared_background)
                        else:
                            about_menu(screen, clock)
                    elif selected_item == 5:  # Exit
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_ESCAPE:  # Escape to resume game
                    return current_level

        clock.tick(60)