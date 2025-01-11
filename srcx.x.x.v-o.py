from ursina import *
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.first_person_controller import FirstPersonController

# -----------------------------------------------------------
# Safe Texture Loading with Color Fallback
# -----------------------------------------------------------
def load_texture_or_color(path, fallback_color=color.white):
    """
    Attempts to load a texture from 'path'. If it fails, we'll return:
      texture = None
      color   = fallback_color
    This way, Ursina won't attempt to interpret a Color as a Texture.
    """
    loaded_tex = load_texture(path)
    if loaded_tex is None:
        print(f"Warning: Missing texture '{path}'. Using fallback color {fallback_color}.")
        return None, fallback_color
    else:
        return loaded_tex, None


# -----------------------------------------------------------
# Advanced Lighting System
# -----------------------------------------------------------
class AdvancedLightingSystem:
    """
    Implements directional light (sun), ambient light,
    and a limit on point lights for performance.
    """
    def __init__(self):
        # Directional 'Sun' light
        self.sun = DirectionalLight(
            y=20,
            rotation=(45, -45, 0),
            shadows=True,
            shadow_resolution=2048
        )
        # Ambient Light
        self.ambient = AmbientLight(color=color.rgba(0.3, 0.3, 0.4, 0.5))
        # Manage dynamic point lights
        self.point_lights = []

    def create_point_light(self, position, color=color.white, intensity=1.0):
        # Keep only 4 point lights for performance
        MAX_POINT_LIGHTS = 4
        if len(self.point_lights) >= MAX_POINT_LIGHTS:
            print("Max point lights reached.")
            return None

        light = PointLight(
            position=position,
            color=color * intensity,
            shadows=True
        )
        self.point_lights.append(light)
        return light


# -----------------------------------------------------------
# Enhanced Station Environment
# -----------------------------------------------------------
class EnhancedStation(Entity):
    """
    Creates a 'station' environment with a ground plane, four walls,
    and adds a point light + sky.
    """
    def __init__(self, lighting):
        super().__init__()
        self.lighting = lighting
        self.create_environment()

    def create_environment(self):
        # ---------- Ground Plane ----------
        ground_tex, ground_col = load_texture_or_color(
            'assets/platform_albedo.png',
            fallback_color=color.gray
        )
        # If ground_tex is None, we'll use color=ground_col
        self.ground = Entity(
            model='plane',
            scale=(100, 1, 100),
            texture=ground_tex,
            color=ground_col,
            shader=lit_with_shadows_shader,
            collider='box'
        )

        # ---------- Walls ----------
        wall_tex, wall_col = load_texture_or_color(
            'assets/brick_wall_albedo.png',
            fallback_color=color.brown
        )
        wall_positions = [(-50, 5, 0), (50, 5, 0), (0, 5, 50), (0, 5, -50)]
        for pos in wall_positions:
            Entity(
                model='cube',
                scale=(1, 10, 100) if abs(pos[0]) > abs(pos[2]) else (100, 10, 1),
                position=pos,
                texture=wall_tex,
                color=wall_col,
                shader=lit_with_shadows_shader,
                collider='box'
            )

        # ---------- Additional Lighting ----------
        self.lighting.create_point_light(position=(0, 10, 0), color=color.yellow, intensity=1.5)

        # ---------- Skybox ----------
        Sky()


# -----------------------------------------------------------
# Main Game Manager
# -----------------------------------------------------------
class GameManager:
    """
    Orchestrates the Ursina app, lighting, environment, player, etc.
    """
    def __init__(self):
        self.app = Ursina()
        window.title = "Advanced Ursina Environment"
        # We'll do a quick hack to show how to manually set window size:
        print("---------------set size to: (1440, 935)")
        window.size = (1440, 935)
        window.borderless = False
        window.exit_button.visible = True
        window.fps_counter.enabled = True

        # Setup lighting and environment
        self.lighting = AdvancedLightingSystem()
        self.station = EnhancedStation(self.lighting)

        # Setup player
        self.player = FirstPersonController()
        self.player.speed = 5

        # Use Ursina's shadow shader on camera
        camera.shader = lit_with_shadows_shader

    def run(self):
        self.app.run()


# -----------------------------------------------------------
# Main Execution
# -----------------------------------------------------------
if __name__ == "__main__":
    game = GameManager()
    game.run()
