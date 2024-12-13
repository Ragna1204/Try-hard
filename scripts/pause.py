import pygame
import sys

pygame.init()
pygame.mixer.init()

click_sound = pygame.mixer.Sound('data/menu.wav')
click_sound.set_volume(0.2)

def options_menu(screen, clock, current_level, max_level):
    font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 20)
    title_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 40)
    options_items = ["Key-bindings", "Back"]
    selected_item = 0

    while True:
        screen.fill((0, 0, 0, 180))  # Semi-transparent background

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
                    elif selected_item == 1:  # Levels
                        return levels_menu(screen, clock, current_level, max_level)
                    elif selected_item == 2:  # Back
                        return current_level
                elif event.key == pygame.K_ESCAPE:  # Escape to go back
                    return current_level

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


def pause_menu(screen, clock, current_level, max_level):
    font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 20)
    title_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 48)
    menu_items = ["Resume", "Options", "Levels", "About", "Exit"]
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
                    elif selected_item == 1:  # Options
                        return options_menu(screen, clock, current_level, max_level)
                    elif selected_item == 2:  # Levels
                        return levels_menu(screen, clock, current_level, max_level)
                    elif selected_item == 3:  # About
                        about_menu(screen, clock)
                    elif selected_item == 4:  # Exit
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_ESCAPE:  # Escape to resume game
                    return current_level

        clock.tick(60)