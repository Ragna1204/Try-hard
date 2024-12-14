import sys
import pygame
from scripts.utils import load_images  # Function to load tile images from directories
from scripts.tilemap import Tilemap    # Tilemap class to handle tile-based maps

RENDER_SCALE = 2.0  # Scaling factor for rendering

class Editor:
    def __init__(self):
        pygame.init()  # Initialize pygame

        pygame.display.set_caption('Editor')  # Set window title
        self.screen = pygame.display.set_mode((640, 480))  # Set the main window size
        self.display = pygame.Surface((320, 240))  # Surface to render on, then upscale to main window

        self.clock = pygame.time.Clock()  # Clock to control the frame rate

        # Load different categories of tiles into self.assets
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'spawners': load_images('tiles/spawners'),
        }

        # Movement tracking for camera (WASD)
        self.movement = [False, False, False, False]

        self.tilemap = Tilemap(self, tile_size=16)  # Initialize the tilemap with a tile size of 16x16

        try:
            self.tilemap.load('data/maps/7.json')  # Load the saved map if available
        except FileNotFoundError:
            pass  # No map file found, continue without loading

        self.scroll = [0, 0]  # Camera scroll position

        self.tile_list = list(self.assets)  # Get a list of tile categories (decor, grass, etc.)
        self.tile_group = 0  # Current tile category
        self.tile_variant = 0  # Current tile within the category

        # State tracking
        self.clicking = False  # Left mouse button state
        self.rightclick = False  # Right mouse button state
        self.shift = False  # Shift key state for tile variant switching
        self.ongrid = True  # Whether tiles are placed on the grid or free-form

    def run(self):
        while True:
            self.display.fill((0, 0, 0))  # Fill the display with black

            # Handle movement and adjust scroll position
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2  # A and D (horizontal)
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2  # W and S (vertical)

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))  # Store scroll as integers

            # Render the tilemap with the scroll offset
            self.tilemap.render(self.display, offset=render_scroll)

            # Load and display the current tile image (partially transparent)
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)  # Set transparency to 100 (out of 255)

            # Get the mouse position and scale it for rendering
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)

            # Calculate which tile the mouse is over
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size),
                        int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            # If tiles are placed on the grid, display them at the grid-aligned position
            if self.ongrid:
                self.display.blit(current_tile_img,
                                  (tile_pos[0] * self.tilemap.tile_size - self.scroll[0],
                                   tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)  # Display at the mouse position for free-form

            # Handle tile placement/removal
            if self.clicking and self.ongrid:
                # Place the tile in the tilemap at the calculated grid position
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group],
                                                                                  'variant': self.tile_variant,
                                                                                  'pos': tile_pos}
            if self.rightclick:
                # Remove tiles at the grid position
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                # Remove off-grid tiles that are clicked
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1],
                                         tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            # Display the current tile being hovered over in the top left for reference
            self.display.blit(current_tile_img, (5, 5))

            # Handle events (input)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()  # Quit the game
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Left-click for placing tiles
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
                    # Right-click for removing tiles
                    if event.button == 3:
                        self.rightclick = True
                    # Mouse wheel for changing tile variants or groups
                    if self.shift:
                        if event.button == 4:  # Scroll up to change tile variant
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:  # Scroll down to change tile variant
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:  # Scroll up to change tile group
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0  # Reset variant
                        if event.button == 5:  # Scroll down to change tile group
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0  # Reset variant
                if event.type == pygame.MOUSEBUTTONUP:
                    # Stop placing/removing tiles on mouse release
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.rightclick = False

                if event.type == pygame.KEYDOWN:
                    # Movement (WASD)
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    # Toggle grid mode
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    # Auto-tile functionality
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    # Save the map
                    if event.key == pygame.K_o:
                        self.tilemap.save('data/maps/7.json')
                    # Enable shift for changing tile variants
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True

                if event.type == pygame.KEYUP:
                    # Stop movement on key release
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    # Disable shift when released
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            # Scale the display surface to the window size and update the screen
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)  # Cap the frame rate at 60 FPS

# Start the editor
Editor().run()

# TODO:
# 1. Add support for moving with arrow keys in addition to WASD.
# 2. Improve background separation with larger images.
# 3. Add more cloud layers.
# 4. Implement jumping mechanics like in Doodle Jump or Flappy Bird.
