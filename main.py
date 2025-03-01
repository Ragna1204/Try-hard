import os
import sys
import math
import random
import pygame
import json
from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.pause import pause_menu, options_menu, levels_menu


class Game:
    def __init__(self):
        pygame.init()

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
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }

        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50, 50), (8, 15))

        self.tilemap = Tilemap(self, tile_size=16)

        self.level = 1
        self.max_level = 1
        self.load_level(self.level)

        self.screenshake = 0

        font_path = 'data/fonts/ninjaline/NinjaLine.ttf'
        self.font = pygame.font.Font(font_path, 20)

        self.death_counter = 0  # Initialize death counter
        self.dead = 0

    def save_game_state(self):
        """Save the game state to a file."""
        state = {
            "level": self.level,
            "max_level": self.max_level,
            "death_counter": self.death_counter,
        }
        with open("savefile.json", "w") as save_file:
            json.dump(state, save_file)

    def load_game_state(self):
        """Load the game state from a file."""
        if os.path.exists("savefile.json"):
            with open("savefile.json", "r") as save_file:
                state = json.load(save_file)
                self.level = state.get("level", 1)
                self.max_level = state.get("max_level", 1)
                self.death_counter = state.get("death_counter", 0)

    def load_level(self, map_id):
        self.dead = 0  # Reset death sequence
        self.transition = 0  # Reset transition
        self.level = map_id
        self.max_level = max(self.max_level, map_id)
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

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

    def toggle_fullscreen(self):
        # Toggle between fullscreen and windowed mode
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((640, 480))
            self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        else:
            self.screen = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
            self.display = pygame.Surface((self.screen.get_width() // 2, self.screen.get_height() // 2), pygame.SRCALPHA)

        self.is_fullscreen = not self.is_fullscreen
    def run(self):
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.sfx['ambience'].play(-1)

        try:
            while True:
                self.display.fill((0, 0, 0, 0))
                for index, layer in enumerate(self.assets['background_layers']):
                    layer_scroll = (0, 0)
                    self.display_2.blit(layer, layer_scroll)

                self.screenshake = max(0, self.screenshake - 1)

                if not len(self.enemies):
                    self.transition += 1
                    if self.transition > 30:
                        self.level = min(self.level + 1, len(os.listdir('data/maps')))
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

                self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
                self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
                render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

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

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_a:
                            self.movement[0] = True
                        if event.key == pygame.K_d:
                            self.movement[1] = True
                        if event.key == pygame.K_f:  # Toggle fullscreen when F is pressed
                            self.toggle_fullscreen()
                        if event.key == pygame.K_SPACE:
                            if self.player.jump():
                                self.sfx['jump'].play()
                        if event.key == pygame.K_LSHIFT:
                            self.player.dash()
                        if event.key == pygame.K_ESCAPE:
                            selected_level = pause_menu(self.screen, self.clock, self.level, self.max_level)
                            if selected_level != self.level:
                                self.load_level(selected_level)

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_a:
                            self.movement[0] = False
                        if event.key == pygame.K_d:
                            self.movement[1] = False

                if self.transition:
                    transition_surf = pygame.Surface(self.display.get_size())
                    pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8) #30*8 = 180
                    transition_surf.set_colorkey((255, 255, 255))
                    self.display.blit(transition_surf, (0, 0))

                self.display_2.blit(self.display, (0, 0))

                level_text = self.font.render(f"Level: {self.level}", True, (0, 0, 0))
                self.display_2.blit(level_text, (5, 5))

                enemies_left = len(self.enemies)  # Get the number of enemies left

                small_font = pygame.font.Font('data/fonts/ninjaline/NinjaLine.ttf', 14)
                enemies_text = small_font.render("Enemies Left:", True, (0, 0, 0))
                enemies_count_text = small_font.render(str(enemies_left), True, (0, 0, 0))

                death_counter_text = self.font.render(f"Deaths: {self.death_counter}", True, (0, 0, 0))
                self.display_2.blit(death_counter_text, (5, self.display_2.get_height() - 30))

                # Positioning the text for a line break
                self.display_2.blit(enemies_text, (self.display_2.get_width() - enemies_text.get_width() - 5, 5))
                self.display_2.blit(enemies_count_text, (self.display_2.get_width() - enemies_count_text.get_width() - 10, 10 + enemies_text.get_height()))


                screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
                self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
                pygame.display.update()
                self.clock.tick(60)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.save_game_state()

Game().run()
