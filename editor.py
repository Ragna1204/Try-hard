import sys
import pygame
from scripts.utils import load_images  # Function to load tile images from directories
from scripts.tilemap import Tilemap    # Tilemap class to handle tile-based maps

RENDER_SCALE = 2.0  # Scaling factor for rendering

class Editor:
    def __init__(self):
        pygame.init()  # Initialize pygame

        pygame.display.set_caption('Editor')  # Set window title
        self.screen = pygame.display.set_mode((960, 480))  # Set the main window size
        self.display = pygame.Surface((480, 240))  # Surface to render on, then upscale to main window

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

        self.tile_list = list(self.assets)
        self.selected_tile = {'type': self.tile_list[0], 'variant': 0}
        self.expanded_category = None
        self.category_scroll = 0

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

            game_surf = pygame.Surface((320, 240))
            game_surf.fill((0,0,0))
            # Render the tilemap with the scroll offset
            self.tilemap.render(game_surf, offset=render_scroll)

            # Load and display the current tile image (partially transparent)
            current_tile_img = self.assets[self.selected_tile['type']][self.selected_tile['variant']].copy()
            current_tile_img.set_alpha(100)  # Set transparency to 100 (out of 255)
            
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)

            # Calculate which tile the mouse is over
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size),
                        int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            # If tiles are placed on the grid, display them at the grid-aligned position
            if self.ongrid:
                game_surf.blit(current_tile_img,
                                  (tile_pos[0] * self.tilemap.tile_size - self.scroll[0],
                                   tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                game_surf.blit(current_tile_img, mpos)  # Display at the mouse position for free-form


            # Display the current tile being hovered over in the top left for reference
            game_surf.blit(current_tile_img, (5, 5))

            self.display.blit(game_surf, (0, 0))

            # Interactable & scrollable sidebar
            SIDEBAR_WIDTH = 160
            SIDEBAR_HEIGHT = 240
            sidebar = pygame.Surface((SIDEBAR_WIDTH, SIDEBAR_HEIGHT))
            sidebar.fill((50, 50, 50))

            if self.expanded_category is None:
                # Collapsed view
                y_offset = 4
                for i, category in enumerate(self.tile_list):
                    tile_img = self.assets[category][0]
                    pos = (4, y_offset)
                    sidebar.blit(tile_img, pos)
                    y_offset += tile_img.get_height() + 4
            else:
                # Expanded view
                category = self.expanded_category
                tiles = self.assets[category]
                for i, tile_img in enumerate(tiles):
                    row = i // 8
                    col = i % 8
                    pos = (col * (tile_img.get_width() + 2) + 2, row * (tile_img.get_height() + 2) + 2 - self.category_scroll)
                    
                    if self.selected_tile['type'] == category and self.selected_tile['variant'] == i:
                        pygame.draw.rect(sidebar, (255, 255, 255), (pos[0] - 1, pos[1] - 1, tile_img.get_width() + 2, tile_img.get_height() + 2), 1)

                    sidebar.blit(tile_img, pos)

            self.display.blit(sidebar, (320, 0))

            # Handle events (input)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    mpos = pygame.mouse.get_pos()
                    mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
                    if mpos[0] > 320:
                        if self.expanded_category is None:
                            y_offset = 4
                            for i, category in enumerate(self.tile_list):
                                tile_img = self.assets[category][0]
                                tile_r = pygame.Rect(320 + 4, y_offset, tile_img.get_width(), tile_img.get_height())
                                if tile_r.collidepoint(mpos):
                                    self.expanded_category = category
                                    self.category_scroll = 0
                                    break
                                y_offset += tile_img.get_height() + 4
                    else:
                        self.expanded_category = None

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mpos = pygame.mouse.get_pos()
                    mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
                    if event.button == 1:
                        if mpos[0] > 320:
                            # Clicked on sidebar
                            if self.expanded_category is not None:
                                category = self.expanded_category
                                tiles = self.assets[category]
                                for i, tile_img in enumerate(tiles):
                                    row = i // 8
                                    col = i % 8
                                    pos = (320 + col * (tile_img.get_width() + 2) + 2, row * (tile_img.get_height() + 2) + 2 - self.category_scroll)
                                    
                                    tile_r = pygame.Rect(pos[0], pos[1], tile_img.get_width(), tile_img.get_height())
                                    if tile_r.collidepoint(mpos):
                                        self.selected_tile = {'type': category, 'variant': i}
                                        break
                        else:
                            self.clicking = True
                            if not self.ongrid:
                                self.tilemap.offgrid_tiles.append({'type': self.selected_tile['type'], 'variant': self.selected_tile['variant'], 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
                    if event.button == 3:
                        self.rightclick = True
                    
                    if mpos[0] > 320: # if mouse on sidebar
                        if self.expanded_category is not None:
                            if event.button == 4:
                                self.category_scroll = max(0, self.category_scroll - 16)
                            if event.button == 5:
                                self.category_scroll += 16
                    else:
                        if event.button == 4:
                            self.selected_tile['variant'] = (self.selected_tile['variant'] - 1) % len(self.assets[self.selected_tile['type']])
                        if event.button == 5:
                            self.selected_tile['variant'] = (self.selected_tile['variant'] + 1) % len(self.assets[self.selected_tile['type']])


                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.rightclick = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_o:
                        self.tilemap.save('data/maps/7.json')
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False
            
            # Handle tile placement/removal
            if self.clicking and self.ongrid:
                # Place the tile in the tilemap at the calculated grid position
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.selected_tile['type'],
                                                                                  'variant': self.selected_tile['variant'],
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


            # Scale the display surface to the window size and update the screen
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)  # Cap the frame rate at 60 FPS

# Start the editor
Editor().run()