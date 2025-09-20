import pygame
import random

class SharedBackground:
    def __init__(self, assets):
        self.assets = assets
        self.background_scroll = 0
        self.particles = []
        self.init_particles()
    
    def init_particles(self):
        """Initialize particle effects"""
        for i in range(15):
            particle = {
                'pos': [random.random() * 320, random.random() * 240],
                'velocity': [random.random() * 0.3 - 0.15, random.random() * 0.3 - 0.15],
                'size': random.randint(1, 2),
                'alpha': random.randint(30, 100),
                'life': random.randint(100, 300)
            }
            self.particles.append(particle)
    
    def update(self):
        """Update background animation and particles"""
        # Update background scroll
        self.background_scroll += 0.1
        
        # Update particles
        for particle in self.particles:
            particle['pos'][0] += particle['velocity'][0]
            particle['pos'][1] += particle['velocity'][1]
            particle['life'] -= 1
            
            # Wrap particles around screen
            if particle['pos'][0] < 0:
                particle['pos'][0] = 320
            elif particle['pos'][0] > 320:
                particle['pos'][0] = 0
            if particle['pos'][1] < 0:
                particle['pos'][1] = 240
            elif particle['pos'][1] > 240:
                particle['pos'][1] = 0
            
            # Respawn particles
            if particle['life'] <= 0:
                particle['pos'] = [random.random() * 320, random.random() * 240]
                particle['life'] = random.randint(100, 300)
    
    def render_background(self, display_2):
        """Render animated background with parallax effect"""
        self._render_parallax_layers(display_2)
    
    def _render_parallax_layers(self, surface):
        """Render parallax layers to a surface"""
        parallax_factors = [0.05, 0.1, 0.2, 0.35, 0.5, 0.65]
        
        for index, layer in enumerate(self.assets['background_layers']):
            if index < len(parallax_factors):
                parallax_x = self.background_scroll * parallax_factors[index]
                
                layer_width = layer.get_width()
                layer_height = layer.get_height()
                
                screen_height = surface.get_height()
                if layer_height < screen_height:
                    scale_factor = screen_height / layer_height
                    scaled_layer = pygame.transform.scale(layer, (int(layer_width * scale_factor), screen_height))
                    layer_width = scaled_layer.get_width()
                else:
                    scaled_layer = layer
                
                tiles_x = (surface.get_width() // layer_width) + 3
                offset_x = -(parallax_x % layer_width)
                
                for tile_x in range(-1, tiles_x):
                    pos_x = offset_x + tile_x * layer_width
                    pos_y = 0
                    surface.blit(scaled_layer, (pos_x, pos_y))
            else:
                scaled_layer = pygame.transform.scale(layer, (surface.get_width(), surface.get_height()))
                surface.blit(scaled_layer, (0, 0))
    
    def render_particles(self, display):
        """Render particle effects"""
        for particle in self.particles:
            color = (255, 255, 255, particle['alpha'])
            pygame.draw.circle(display, color, (int(particle['pos'][0]), int(particle['pos'][1])), particle['size'])
