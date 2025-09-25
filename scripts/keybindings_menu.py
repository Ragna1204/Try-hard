import pygame
import json
import sys
import math

def render_text_with_outline(surface, font, text, color, position, outline_color=(0, 0, 0)):
    """Renders text with an outline."""
    text_surface = font.render(text, True, color)
    outline_surface = font.render(text, True, outline_color)

    # Render the outline by blitting the outline surface multiple times
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        surface.blit(outline_surface, (position[0] + dx, position[1] + dy))
    
    # Render the main text on top
    surface.blit(text_surface, position)

def keybindings_menu(screen, clock, assets, sfx, shared_background):
    keybindings = {}
    try:
        with open('keybindings.json', 'r') as f:
            keybindings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        keybindings = {
            'left': 'a',
            'right': 'd',
            'jump': 'space',
            'dash': 'left shift'
        }

    font_path = 'data/fonts/ninjaline/NinjaLine.ttf'
    title_font = pygame.font.Font(font_path, 40)
    option_font = pygame.font.Font(font_path, 22)

    actions = list(keybindings.keys())
    menu_items = actions + ["Restore Defaults", "Back"]
    selected_index = 0
    
    changing_key_for = None
    title_glow = 0

    while True:
        screen.fill((0, 0, 0))
        if shared_background:
            shared_background.render_background(screen)
            shared_background.render_particles(screen)
            shared_background.update()
        
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # --- Find duplicates --- #
        key_counts = {}
        for action, key in keybindings.items():
            if key not in key_counts:
                key_counts[key] = []
            key_counts[key].append(action)
        
        duplicate_keys = {key for key, bound_actions in key_counts.items() if len(bound_actions) > 1}

        # --- Render --- #
        title_pos = (screen.get_width() // 2 - title_font.render("Keybindings", True, (255, 255, 255)).get_width() // 2, 80)
        render_text_with_outline(screen, title_font, "Keybindings", (255, 255, 255), title_pos)

        y_pos = 180
        for i, item in enumerate(menu_items):
            is_selected = (i == selected_index)
            
            if is_selected:
                title_glow += 0.1
                blink_intensity = int(128 + 127 * math.sin(title_glow))
                color = (blink_intensity, blink_intensity, blink_intensity)
            else:
                color = (255, 255, 255)

            if item == "Back" or item == "Restore Defaults":
                text_width = option_font.render(item, True, color).get_width()
                pos = (screen.get_width() // 2 - text_width // 2, y_pos + 20)
                render_text_with_outline(screen, option_font, item, color, pos)
            else:
                action_display = item.replace('_', ' ').title()
                key_display = keybindings[item].upper()

                if changing_key_for == item:
                    key_display = "..."

                key_color = color
                if keybindings[item] in duplicate_keys:
                    key_color = (255, 50, 50) # Red for duplicates

                action_width = option_font.render(action_display, True, color).get_width()
                
                action_pos = (screen.get_width() // 2 - action_width - 30, y_pos)
                key_pos = (screen.get_width() // 2 + 30, y_pos)

                render_text_with_outline(screen, option_font, action_display, color, action_pos)
                render_text_with_outline(screen, option_font, ":", color, (screen.get_width() // 2 - 5, y_pos))
                render_text_with_outline(screen, option_font, key_display, key_color, key_pos)

            y_pos += 45

        # --- Handle Input --- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if changing_key_for:
                    new_key = pygame.key.name(event.key)
                    keybindings[changing_key_for] = new_key
                    with open('keybindings.json', 'w') as f:
                        json.dump(keybindings, f, indent=4)
                    changing_key_for = None
                    sfx['menu_click'].play()
                else:
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        selected_index = (selected_index + 1) % len(menu_items)
                        sfx['menu_click'].play()
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        selected_index = (selected_index - 1 + len(menu_items)) % len(menu_items)
                        sfx['menu_click'].play()
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        selected_item = menu_items[selected_index]
                        if selected_item == "Back":
                            sfx['menu_click'].play()
                            return "back"
                        elif selected_item == "Restore Defaults":
                            defaults = {
                                'left': 'a',
                                'right': 'd',
                                'jump': 'space',
                                'dash': 'left shift'
                            }
                            keybindings.clear()
                            keybindings.update(defaults)
                            with open('keybindings.json', 'w') as f:
                                json.dump(keybindings, f, indent=4)
                            sfx['menu_click'].play()
                        else:
                            changing_key_for = selected_item
                            sfx['menu_click'].play()
                    elif event.key == pygame.K_ESCAPE:
                        return "back"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                y_pos = 180
                for i, item in enumerate(menu_items):
                    text_height = option_font.get_height()
                    if item == "Back":
                        item_rect = pygame.Rect(screen.get_width() // 2 - 50, y_pos + 20, 100, text_height)
                    else:
                        item_rect = pygame.Rect(screen.get_width() // 2 - 150, y_pos, 300, text_height)
                    
                    if item_rect.collidepoint(event.pos):
                        selected_index = i
                        selected_item = menu_items[selected_index]
                        if selected_item == "Back":
                            sfx['menu_click'].play()
                            return "back"
                        else:
                            changing_key_for = selected_item
                            sfx['menu_click'].play()
                        break
                    y_pos += 45

        pygame.display.update()
        clock.tick(60)
