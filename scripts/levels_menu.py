import pygame
import sys
from scripts.utils import resource_path

def levels_menu(screen, clock, current_level, max_level, sfx):
    import math
    import random
    font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 28)
    title_font = pygame.font.Font(resource_path('data/fonts/ninjaline/NinjaLine.ttf'), 48)
    small_font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 16)

    levels_per_row = 5
    total_levels = 10  # Adjust this to match your total number of levels
    selected_level = current_level
    hovered_level = None
    title_glow = 0
    animation_time = 0

    # Animation and styling data
    level_data = {}
    for i in range(total_levels):
        level_data[i+1] = {
            'animation_offset': random.uniform(0, 2 * math.pi),
            'pulse_scale': 1.0,
            'selected': False,
            'unlocked': (i+1) <= max_level
        }

    while True:
        animation_time += 0.05
        screen.fill((0, 0, 0, 180))  # Semi-transparent background

        # Draw the title with glow effect
        title_glow += 0.1
        glow_intensity = int(50 + 30 * math.sin(title_glow))
        title_text = title_font.render("LEVEL SELECT", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 40))

        # Add title glow/shadow
        for offset in [(-3, -3), (3, -3), (-3, 3), (3, 3), (-2, 0), (2, 0), (0, -2), (0, 2)]:
            shadow_text = title_font.render("LEVEL SELECT", True, (0, 0, 0))
            screen.blit(shadow_text, (title_rect.x + offset[0], title_rect.y + offset[1]))
        screen.blit(title_text, title_rect)

        # Draw level buttons
        for i in range(total_levels):
            level_number = i + 1
            row = i // levels_per_row
            col = i % levels_per_row

            base_x = screen.get_width() // 2 + (col - 2) * 70  # Horizontal spacing
            base_y = 110 + row * 100  # More vertical gap between rows

            # Animation calculations
            level_info = level_data[level_number]
            x = base_x
            y = base_y

            # Idle floating animation
            float_offset = 3 * math.sin(animation_time + level_info['animation_offset'])
            y += float_offset

            # Determine if level is being hovered or selected
            mouse_x, mouse_y = pygame.mouse.get_pos()
            level_rect = pygame.Rect(x - 30, y - 30, 60, 60)  # Larger hitbox
            is_hovered = level_rect.collidepoint(mouse_x, mouse_y)

            # Update selection state when hovering
            prev_hovered = hovered_level
            if is_hovered:
                hovered_level = level_number
                selected_level = level_number  # Immediate update on hover
            elif hovered_level == level_number:
                hovered_level = None

            # Play sound when hover changes (only once per hover)
            if prev_hovered != hovered_level and prev_hovered is None and hovered_level is not None:
                sfx['menu_click'].play()

            # Determine visual state
            is_active = (hovered_level == level_number) or (level_number == selected_level and not hovered_level)
            is_current = level_number == current_level

            # Calculate scale and colors based on state
            base_color = (255, 255, 255) if level_info['unlocked'] else (100, 100, 100)
            scale = 1.0

            if is_active:
                # Pulsing scale effect for active levels with crimson energy
                pulse_rate = 0.2
                scale = 1.0 + 0.15 * math.sin(animation_time * pulse_rate)
                glow_intensity = int(200 + 55 * math.sin(animation_time * 3))
                color = (glow_intensity, 80, 80)  # Crimson glow
            else:
                color = base_color

            # Draw level background circle/button with multiple layers for depth
            button_color = (50, 50, 50) if not level_info['unlocked'] else (80, 80, 80)
            if is_active:
                button_color = (120, 120, 120)

            # Updated button size (smaller)
            button_radius = 28

            # Draw button shadow
            pygame.draw.circle(screen, (0, 0, 0), (x + 2, y + 2), button_radius, 0)

            # Draw ninja-themed button background with crimson theme
            if level_info['unlocked']:
                if is_active:
                    button_color = (180, 50, 50)  # Dark crimson for active
                else:
                    button_color = (120, 40, 40)  # Blood red for normal
            else:
                button_color = (80, 80, 80)  # Dark gray for locked

            # Add blood-stained parchment texture to unlocked buttons
            if level_info['unlocked']:
                # Base parchment color (blood-stained)
                parchment_color = button_color if is_active else (140, 60, 60)
                pygame.draw.circle(screen, parchment_color, (x, y), button_radius, 0)

                # Add subtle parchment texture pattern
                texture_color = (int(parchment_color[0] * 0.7), int(parchment_color[1] * 0.7), int(parchment_color[2] * 0.7))
                for angle in range(0, 360, 30):
                    angle_rad = math.radians(angle)
                    dot_x = int(x + (button_radius - 5) * math.cos(angle_rad))
                    dot_y = int(y + (button_radius - 5) * math.sin(angle_rad))
                    pygame.draw.circle(screen, texture_color, (dot_x, dot_y), 1)
            else:
                pygame.draw.circle(screen, button_color, (x, y), button_radius, 0)

            # Draw ninja-themed button border with crimson energy
            if level_info['unlocked']:
                if is_active:
                    # Crimson energy aura
                    glow_intensity = int(220 + 35 * math.sin(animation_time * 6))
                    border_color = (glow_intensity, 70, 70)
                else:
                    border_color = (200, 100, 100)  # Blood red border
            else:
                border_color = (120, 50, 50)  # Reddish for locked

            pygame.draw.circle(screen, border_color, (x, y), button_radius, 3)

            # Draw level number with scaling
            level_text = font.render(str(level_number), True, color)
            if scale != 1.0:
                scale_factor = scale
                scaled_text = pygame.transform.smoothscale(level_text,
                    (int(level_text.get_width() * scale_factor), int(level_text.get_height() * scale_factor)))
                scaled_rect = scaled_text.get_rect(center=(x, y))
                screen.blit(scaled_text, scaled_rect)
            else:
                text_rect = level_text.get_rect(center=(x, y))
                screen.blit(level_text, text_rect)

            # Draw special indicators
            if is_current:
                # Yellow indicator for current level
                pygame.draw.circle(screen, (255, 255, 0), (x, y), 45, 3)

            if not level_info['unlocked']:
                # Lock visual indicator for unlocked levels
                lock_color = (150, 50, 50)  # Reddish for locked
                pygame.draw.circle(screen, lock_color, (x, y), 25, 2)
                lock_text = small_font.render("LOCKED", True, lock_color)
                lock_rect = lock_text.get_rect(center=(x, y + 45))
                screen.blit(lock_text, lock_rect)

        # Draw navigation hints at bottom
        nav_text = small_font.render("Use ARROW KEYS or MOUSE to select, ENTER/SPACE to confirm", True, (200, 200, 200))
        nav_rect = nav_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30))
        screen.blit(nav_text, nav_rect)

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT] and selected_level > 0:
                    selected_level -= 1
                    sfx['menu_click'].play()
                elif event.key in [pygame.K_RIGHT] and selected_level < total_levels - 1:
                    selected_level += 1
                    sfx['menu_click'].play()
                elif event.key in [pygame.K_UP] and selected_level >= levels_per_row:
                    selected_level -= levels_per_row
                    sfx['menu_click'].play()
                elif event.key in [pygame.K_DOWN] and selected_level < total_levels - levels_per_row:
                    selected_level += levels_per_row
                    sfx['menu_click'].play()
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if selected_level <= max_level:
                        sfx['menu_click'].play()
                        return selected_level  # Return the selected level if it's cleared
                elif event.key == pygame.K_ESCAPE:
                    return "back"  # Return to pause menu

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    for i in range(total_levels):
                        level_number = i + 1
                        if level_number <= max_level:
                            row = i // levels_per_row
                            col = i % levels_per_row
                            x = screen.get_width() // 2 + (col - 2) * 70  # Match horizontal spacing
                            y = 110 + row * 100  # Match vertical spacing
                            # Account for floating animation in hit detection
                            adjusted_y = y + 3 * math.sin(animation_time + level_data[level_number]['animation_offset'])
                            level_rect = pygame.Rect(x - button_radius, adjusted_y - button_radius, button_radius * 2, button_radius * 2)
                            if level_rect.collidepoint(mouse_x, mouse_y):
                                sfx['menu_click'].play()
                                return level_number

        clock.tick(60)
