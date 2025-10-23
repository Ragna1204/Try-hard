# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**Try-Hard** is a 2D ninja platformer game built entirely in Python using pygame-ce. The game features fast-paced action with precise controls, wall-sliding mechanics, dash attacks, and challenging level progression. Players must eliminate all enemies in each level to progress while avoiding projectiles and environmental hazards.

## Key Development Commands

### Running the Game
```bash
# Install pygame dependency (required)
pip install pygame

# Run the main game
python main.py

# Run the level editor
python editor.py
```

### Building Executable
```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Build executable using existing spec file
pyinstaller main.spec
```

## Code Architecture

### Core Game Structure
The codebase follows a modular architecture centered around a main `Game` class that orchestrates all game systems:

- **Game Loop**: Located in `main.py`, handles the primary game loop with 60 FPS rendering, event processing, and game state management
- **Entity System**: `scripts/entities.py` contains the physics-based entity hierarchy (`PhysicsEntity` → `Player`/`Enemy`)
- **Level Management**: `scripts/tilemap.py` handles tile-based level loading, collision detection, and auto-tiling functionality
- **Asset Pipeline**: `scripts/utils.py` provides image loading utilities and animation system

### Key Systems

**Physics & Movement**:
- Gravity-based physics with collision detection against tilemap
- Wall-sliding mechanics with reduced fall speed
- Dash system with invincibility frames and particle effects
- Variable movement speed multipliers

**Level Progression**:
- JSON-based level storage in `data/maps/`
- Save/load system tracks level progress and death counter
- Automatic level transitions when all enemies are eliminated
- Level editor for creating new content

**Audio & Visual**:
- Layered background rendering with parallax scrolling
- Particle systems for visual feedback (leaf spawners, dash trails, hit effects)
- Screen shake effects for impact feedback
- Custom font rendering with NinjaLine font

**Menu System**:
- Pause menu with level selection, key bindings, and options
- Level selection grid showing progress and availability
- Sound effects for menu interactions

### File Organization

**Main Files**:
- `main.py`: Core game logic and main loop
- `editor.py`: Level editor with tile placement tools

**Scripts Module** (`scripts/`):
- `entities.py`: Player, Enemy, and PhysicsEntity classes
- `tilemap.py`: Level loading, collision detection, auto-tiling
- `utils.py`: Asset loading utilities and Animation class
- `pause.py`: All menu systems (pause, options, levels, key bindings)
- `clouds.py`, `particle.py`, `spark.py`: Visual effect systems

**Data Structure** (`data/`):
- `images/`: Sprite assets organized by type (entities, tiles, backgrounds)
- `maps/`: JSON level files
- `sfx/`: Sound effect files
- `fonts/`: Custom font files
- `music.wav`, `menu.wav`: Background audio

### Entity Interaction Patterns

**Combat System**:
- Player dash attack (when `abs(dashing) >= 50`) destroys enemies on contact
- Enemy projectiles kill player unless dashing (invincibility frames)
- Collision generates particle effects and screen shake

**Level Completion**:
- Track enemy count; when zero, trigger level transition
- Save progress including current level, max unlocked level, and death counter
- Automatic progression to next level with transition effects

### Development Notes

**Editor Usage**:
- WASD: Camera movement
- Mouse wheel: Change tile types/variants
- Shift + Mouse wheel: Change tile variants within type
- Left click: Place tiles
- Right click: Remove tiles
- G: Toggle grid/free placement
- T: Auto-tile current tilemap
- O: Save current map

**Game Controls**:
- A/D: Move left/right
- Space: Jump (or wall jump when wall-sliding)
- Left Shift: Dash/attack
- F: Toggle fullscreen
- Escape: Pause menu

**Performance Considerations**:
- Game renders at 320x240 internal resolution, scaled to window size
- Uses sprite batching and efficient collision detection
- Particle systems are culled automatically when animations complete

### Asset Dependencies

The game expects a specific asset structure under `data/images/`:
- Character sprites with idle/run/jump/slide/wall_slide animations
- Tile sets for grass, stone, decor, large_decor, spawners
- Background layers for parallax scrolling
- Particle sprites for effects
- UI elements (gun, projectile sprites)

Game saves progress to `saves/savefile_*.json` in the saves directory and requires all audio files to be present for proper sound functionality.
