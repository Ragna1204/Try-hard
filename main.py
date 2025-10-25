import os
import sys
import math
import random
import pygame
import json
from scripts.utils import load_image, load_images, Animation, resource_path
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.pause import pause_menu, options_menu
from scripts.levels_menu import levels_menu
from scripts.main_menu import main_menu
from scripts.save_select import save_select
from scripts.level_select import level_select
from scripts.about import about_screen
from scripts.shared_background import SharedBackground


class Game:
    def load_keybindings(self):
        self.keybindings = {
            'left': pygame.K_a,
            'right': pygame.K_d,
            'jump': pygame.K_SPACE,
            'dash': pygame.K_LSHIFT
        }
        try:
            with open('keybindings.json', 'r') as f:
                keybindings = json.load(f)
                for action, key_name in keybindings.items():
                    self.keybindings[action] = pygame.key.key_code(key_name)
        except (FileNotFoundError, json.JSONDecodeError):
            with open('keybindings.json', 'w') as f:
                json.dump({
                    'left': 'a',
                    'right': 'd',
                    'jump': 'space',
                    'dash': 'left shift'
                }, f, indent=4)

    def __init__(self):
        pygame.init()

        # Keybindings
        self.load_keybindings()

        pygame.display.set_caption('Tryhard')
        self.is_fullscreen = True
        self.screen = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background_layers': [
                load_image('sky.png'),
                load_image('far-mountains.png'),
                load_image('middle-mountains.png'),
                load_image('far-trees.png'),
                load_image('myst.png'),
                load_image('near-trees.png'),
            ],
            'clouds': load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
        }

        self.sfx = {
            'jump': pygame.mixer.Sound(resource_path('data/sfx/jump.wav')),
            'dash': pygame.mixer.Sound(resource_path('data/sfx/dash.wav')),
            'hit': pygame.mixer.Sound(resource_path('data/sfx/hit.wav')),
            'shoot': pygame.mixer.Sound(resource_path('data/sfx/shoot.wav')),
            'ambience': pygame.mixer.Sound(resource_path('data/sfx/ambience.wav')),
            'menu_click': pygame.mixer.Sound(resource_path('data/menu.wav')),
        }

        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)
        self.sfx['menu_click'].set_volume(0.3)

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50, 50), (8, 15))

        self.tilemap = Tilemap(self, tile_size=16)

        self.level = 1
        self.max_level = 1
        self.load_level(self.level)

        self.screenshake = 0

        font_path = resource_path('data/fonts/ninjaline/NinjaLine.ttf')
        self.font = pygame.font.Font(font_path, 20)

        self.death_counter = 0  # Initialize death counter
        self.dead = 0
        
        # Game state management
        self.game_state = "menu"  # menu, playing, paused
        self.show_menu = True
        self.current_save_slot = 0  # Track which save slot is currently being used
        
        # Shared background for consistent animation across screens
        self.shared_background = SharedBackground(self.assets)


    def get_save_path(self, filename=None):
        """Get the correct path for save files, works for dev and executable"""
        if filename:
            return resource_path(f'saves/{filename}')
        return resource_path('saves/savefile.json')

    def save_game_state(self):
        """Save the game state to a file."""
        state = {
            "level": self.level,
            "max_level": self.max_level,
            "death_counter": self.death_counter,
        }
        try:
            # Use current save slot if available, otherwise default to saves/savefile.json
            if hasattr(self, 'current_save_slot'):
                save_file = self.get_save_path(f'savefile_{self.current_save_slot + 1}.json')
            else:
                save_file = self.get_save_path()
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_file), exist_ok=True)
            with open(save_file, "w") as f:
                json.dump(state, f)
        except Exception as e:
            print(f"Error saving game state: {e}")

    def load_game_state(self):
        """Load the game state from a file."""
        save_file = self.get_save_path()
        if os.path.exists(save_file):
            try:
                with open(save_file, "r") as save_file_obj:
                    state = json.load(save_file_obj)
                    self.level = state.get("level", 1)
                    self.max_level = state.get("max_level", 1)
                    self.death_counter = state.get("death_counter", 0)
            except (json.JSONDecodeError, FileNotFoundError):
                print("Failed to load game state, using default values.")
                self.level = 1
                self.max_level = 1
                self.death_counter = 0

        else:
            self.level = 1
            self.max_level = 1
            self.death_counter = 0

    def load_level(self, map_id):
        """Load a level and reset relevant game states."""
        self.dead = 0  # Reset death sequence
        self.transition = 0  # Reset transition
        self.level = map_id
        self.max_level = max(self.max_level, map_id)
        self.tilemap.load(resource_path('data/maps/' + str(map_id) + '.json'))

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.FRect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))

        self.projectiles = []
        self.particles = []
        self.sparks = []

        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30

        # Save progress when a new level is loaded
        self.death_counter = getattr(self, "death_counter", 0)
        self.save_game_state()

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((640, 480))

        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))
    
    def handle_menu_action(self, action):
        """Handle menu actions and return True if game should continue"""
        if action == "exit":
            return False
        elif action == "start_game":
            # Show save selection screen
            selected_save = save_select(self.screen, self.clock, self.assets, self.sfx, self.shared_background)
            if selected_save == "back":
                return True  # Return to main menu
            elif selected_save == "exit":
                return False
            else:
                # Set the current save slot
                self.current_save_slot = selected_save

                # Load the selected save file
                save_file = self.get_save_path(f'savefile_{selected_save + 1}.json')
                if os.path.exists(save_file):
                    try:
                        with open(save_file, "r") as f:
                            save_data = json.load(f)
                            self.level = save_data.get("level", 1)
                            self.max_level = save_data.get("max_level", 1)
                            self.death_counter = save_data.get("death_counter", 0)
                    except (json.JSONDecodeError, FileNotFoundError):
                        # Corrupt file, create new one with defaults
                        self.level = 1
                        self.max_level = 1
                        self.death_counter = 0
                else:
                    # New save file
                    self.level = 1
                    self.max_level = 1
                    self.death_counter = 0

                # Create/save the save file (whether existing or new)
                save_data = {
                    "level": self.level,
                    "max_level": self.max_level,
                    "death_counter": self.death_counter
                }
                try:
                    os.makedirs(os.path.dirname(save_file), exist_ok=True)
                    with open(save_file, "w") as f:
                        json.dump(save_data, f)
                except Exception as e:
                    print(f"Error creating save file: {e}")
                
                # Show level selection screen
                selected_level = level_select(self.screen, self.clock, self.assets, self.sfx, self.max_level, self.shared_background)
                if selected_level == "back":
                    return True  # Return to main menu
                elif selected_level == "exit":
                    return False
                else:
                    self.level = selected_level
                    self.game_state = "playing"
                    self.show_menu = False
                    self.load_level(self.level)
        elif action == "options":
            options_menu(self.screen, self.clock, self.level, self.max_level, self.assets, self.sfx, self.shared_background)
            self.load_keybindings()
        elif action == "about":
            about_result = about_screen(self.screen, self.clock, self.assets, self.sfx, self.shared_background)
            if about_result == "exit":
                return False
            # If "back", continue to main menu
        return True
    
    def run(self):
        pygame.mixer.music.load(resource_path('data/music.wav'))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.sfx['ambience'].play(-1)

        try:
            while True:
                # Show main menu if needed
                if self.show_menu:
                    action = main_menu(self.screen, self.clock, self.assets, self.sfx, self.shared_background)
                    if not self.handle_menu_action(action):
                        break
                    continue
                self.display.fill((0, 0, 0, 0))
                
                # Calculate camera scroll first
                self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
                self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
                render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
                
                # Render background layers with parallax effect and proper tiling
                # Each layer moves at different speeds to create depth
                parallax_factors = [0.05, 0.1, 0.2, 0.35, 0.5, 0.65]  # Adjusted for 6 layers
                
                for index, layer in enumerate(self.assets['background_layers']):
                    if index < len(parallax_factors):
                        # Calculate parallax offset for horizontal scrolling only
                        parallax_x = render_scroll[0] * parallax_factors[index]
                        
                        # Get layer dimensions
                        layer_width = layer.get_width()
                        layer_height = layer.get_height()
                        
                        # Scale the background to fit screen height if needed
                        screen_height = self.display_2.get_height()
                        if layer_height < screen_height:
                            # Scale layer to fit screen height
                            scale_factor = screen_height / layer_height
                            scaled_layer = pygame.transform.scale(layer, (int(layer_width * scale_factor), screen_height))
                            layer_width = scaled_layer.get_width()
                        else:
                            scaled_layer = layer
                        
                        # Calculate how many horizontal tiles we need
                        tiles_x = (self.display_2.get_width() // layer_width) + 3
                        
                        # Wrap the horizontal parallax offset for seamless tiling
                        offset_x = -(parallax_x % layer_width)
                        
                        # Draw horizontally tiled background (no vertical tiling)
                        for tile_x in range(-1, tiles_x):
                            pos_x = offset_x + tile_x * layer_width
                            pos_y = 0  # Always start at top of screen
                            self.display_2.blit(scaled_layer, (pos_x, pos_y))
                    else:
                        # Fallback for extra layers - stretch to fit screen
                        scaled_layer = pygame.transform.scale(layer, (self.display_2.get_width(), self.display_2.get_height()))
                        self.display_2.blit(scaled_layer, (0, 0))

                self.screenshake = max(0, self.screenshake - 1)

                if not len(self.enemies):
                    self.transition += 1
                    if self.transition > 30:
                        self.level = min(self.level + 1, len(os.listdir(resource_path('data/maps'))))
                        self.max_level = max(self.max_level, self.level)
                        self.load_level(self.level)
                if self.transition < 0:
                    self.transition += 1

                if self.dead:
                    self.dead += 1
                    if self.dead >= 10:
                        self.transition = min(30, self.transition + 1)
                    if self.dead > 40:
                        self.load_level(self.level)

                for rect in self.leaf_spawners:
                    if random.random() * 49999 < rect.width * rect.height:
                        pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                        self.particles.append(
                            Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

                self.clouds.update()
                self.clouds.render(self.display_2, offset=render_scroll)

                self.tilemap.render(self.display, offset=render_scroll)

                for enemy in self.enemies.copy():
                    kill = enemy.update(self.tilemap, (0, 0))
                    enemy.render(self.display, offset=render_scroll)
                    if kill:
                        self.enemies.remove(enemy)

                if not self.dead:
                    self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                    self.player.render(self.display, offset=render_scroll)

                # [[x, y], direction, timer]
                for projectile in self.projectiles.copy():
                    projectile[0][0] += projectile[1]
                    projectile[2] += 1
                    img = self.assets['projectile']
                    self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0],
                                            projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                    if self.tilemap.solid_check(projectile[0]):
                        self.projectiles.remove(projectile)
                        for i in range(4):
                            self.sparks.append(
                                Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0),
                                      2 + random.random()))
                    elif projectile[2] > 360:
                        self.projectiles.remove(projectile)
                    elif abs(self.player.dashing) < 50:
                        if self.player.rect().collidepoint(projectile[0]):
                            self.projectiles.remove(projectile)
                            self.dead += 1
                            self.sfx['hit'].play()
                            self.screenshake = max(16, self.screenshake)
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                                self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

                for spark in self.sparks.copy():
                    kill = spark.update()
                    spark.render(self.display, offset=render_scroll)
                    if kill:
                        self.sparks.remove(spark)

                display_mask = pygame.mask.from_surface(self.display)
                display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
                for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    self.display_2.blit(display_sillhouette, offset)

                for particle in self.particles.copy():
                    kill = particle.update()
                    particle.render(self.display, offset=render_scroll)
                    if particle.type == 'leaf':
                        particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                    if kill:
                        self.particles.remove(particle)

                if self.dead:
                    self.dead += 1  # Increment the death animation/frame counter
                    if self.dead == 2:  # Increment death counter only once per death
                        self.death_counter += 1
                    if self.dead >= 10:  # Start transition to respawn
                        self.transition = min(30, self.transition + 1)
                    if self.dead > 40:  # After animation finishes, reload the level
                        self.load_level(self.level)



                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    # Always handle KEYUP events to prevent stuck input states
                    if event.type == pygame.KEYUP:
                        if event.key == self.keybindings['left']:
                            self.movement[0] = False
                        if event.key == self.keybindings['right']:
                            self.movement[1] = False
                        if event.key == self.keybindings['jump']:
                            self.player.cut_jump()

                    if self.transition == 0:
                        if event.type == pygame.KEYDOWN:
                            if event.key == self.keybindings['left']:
                                self.movement[0] = True
                            if event.key == self.keybindings['right']:
                                self.movement[1] = True
                            if event.key == pygame.K_f:  # Toggle fullscreen when F is pressed
                                self.toggle_fullscreen()
                            if event.key == self.keybindings['jump']:
                                if self.player.jump():
                                    self.sfx['jump'].play()
                            if event.key == self.keybindings['dash']:
                                self.player.dash()
                            if event.key == pygame.K_ESCAPE:
                                selected_level = pause_menu(self.screen, self.clock, self.level, self.max_level, self.assets, self.sfx, self.shared_background)
                                self.load_keybindings()
                                if selected_level == "menu":

                                    self.show_menu = True
                                    self.game_state = "menu"
                                elif selected_level != self.level:
                                    self.load_level(selected_level)

                if self.transition:
                    transition_surf = pygame.Surface(self.display.get_size())
                    pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8) #30*8 = 180
                    transition_surf.set_colorkey((255, 255, 255))
                    self.display.blit(transition_surf, (0, 0))

                self.display_2.blit(self.display, (0, 0))

                # Game screen HUD with Protest_Revolution font - black labels, dark bright red numbers
                ui_font = pygame.font.Font(resource_path('data/fonts/Protest_Revolution/ProtestRevolution-Regular.ttf'), 18)

                # Level display at top-left with black labels and dark bright red numbers with thin black padding
                level_label = ui_font.render("Level:", True, (0, 0, 0))
                level_number = ui_font.render(str(self.level), True, (255, 50, 50))

                # Position level display
                level_label_pos = (10, 10)
                level_number_pos = (level_label_pos[0] + level_label.get_width() + 5, level_label_pos[1])

                # Add thin black outline around number
                for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    outline_text = ui_font.render(str(self.level), True, (0, 0, 0))
                    self.display_2.blit(outline_text, (level_number_pos[0] + offset[0], level_number_pos[1] + offset[1]))

                self.display_2.blit(level_label, level_label_pos)
                self.display_2.blit(level_number, level_number_pos)

                enemies_left = len(self.enemies)  # Get the number of enemies left

                # Enemies display at top-right with black labels and dark bright red numbers with thin black padding
                enemies_label = ui_font.render("Enemies:", True, (0, 0, 0))
                enemies_number = ui_font.render(str(enemies_left), True, (255, 50, 50))

                # Position enemies display
                enemies_label_x = self.display_2.get_width() - enemies_label.get_width() - enemies_number.get_width() - 15
                enemies_number_x = enemies_label_x + enemies_label.get_width() + 5

                # Add thin black outline around enemy count
                for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    outline_text = ui_font.render(str(enemies_left), True, (0, 0, 0))
                    self.display_2.blit(outline_text, (enemies_number_x + offset[0], 10 + offset[1]))

                self.display_2.blit(enemies_label, (enemies_label_x, 10))
                self.display_2.blit(enemies_number, (enemies_number_x, 10))

                # Death counter at bottom-left with black labels and dark bright red numbers with thin black padding
                death_label = ui_font.render("Deaths:", True, (0, 0, 0))
                death_number = ui_font.render(str(self.death_counter), True, (255, 50, 50))

                # Position death counter
                death_label_pos = (10, self.display_2.get_height() - 28)
                death_number_pos = (death_label_pos[0] + death_label.get_width() + 5, death_label_pos[1])

                # Add thin black outline around death count
                for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    outline_text = ui_font.render(str(self.death_counter), True, (0, 0, 0))
                    self.display_2.blit(outline_text, (death_number_pos[0] + offset[0], death_number_pos[1] + offset[1]))

                self.display_2.blit(death_label, death_label_pos)
                self.display_2.blit(death_number, death_number_pos)


                screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
                self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
                pygame.display.update()
                self.clock.tick(60)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.save_game_state()

Game().run()
