from ursina import *
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import Material
import numpy as np
import sys
import time

class AdvancedLightingSystem:
    """
    Implements advanced lighting with HDR-like effects
    """
    def __init__(self, scene_brightness=1.5):
        self.exposure = 1.0
        self.scene_brightness = scene_brightness
        self.bloom_threshold = 0.8
        self.setup_lighting()
        
    def setup_lighting(self):
        # Main directional light (sun)
        self.sun = DirectionalLight(
            y=20, 
            rotation=(45, -45, 0),
            shadows=True,
            shadow_resolution=2048
        )
        
        # Ambient lighting for bounce light simulation
        self.ambient = AmbientLight(
            color=color.rgba(0.1, 0.1, 0.15, 0.5)
        )
        
        # Dynamic point lights for enhanced atmosphere
        self.point_lights = []
        
    def create_point_light(self, position, color=color.white, intensity=1.0):
        light = PointLight(
            position=position,
            color=color * intensity,
            shadows=True
        )
        self.point_lights.append(light)
        return light
        
    def update_exposure(self, dt):
        # Simulate auto-exposure adjustment
        target_luminance = scene.average_luminance
        self.exposure = lerp(self.exposure, 1.0/max(target_luminance, 0.1), dt)

class EnhancedAssetManager:
    def __init__(self):
        self.textures = {}
        self.materials = {}
        self._load_assets()
    
    def _load_assets(self):
        # Enhanced texture loading with PBR materials
        texture_data = {
            'brick': {
                'albedo': 'assets/brick_wall_albedo.png',
                'normal': 'assets/brick_wall_normal.png',
                'roughness': 'assets/brick_wall_roughness.png',
                'metallic': 'assets/brick_wall_metallic.png'
            },
            'platform': {
                'albedo': 'assets/platform_albedo.png',
                'normal': 'assets/platform_normal.png',
                'roughness': 'assets/platform_roughness.png'
            }
        }
        
        for key, paths in texture_data.items():
            try:
                material = self.create_pbr_material(paths)
                self.materials[key] = material
            except Exception as e:
                print(f"Failed to load material '{key}': {e}")
                self.materials[key] = None
                
    def create_pbr_material(self, texture_paths):
        """Creates a PBR material from texture maps"""
        shader = lit_with_shadows_shader
        material = Material(shader)
        
        for map_type, path in texture_paths.items():
            try:
                texture = load_texture(path)
                setattr(material, f'{map_type}_texture', texture)
            except:
                print(f"Failed to load texture: {path}")
        
        return material

class EnhancedStation(Entity):
    """
    Enhanced train station with improved visuals
    """
    def __init__(self, assets, lighting):
        super().__init__()
        self.assets = assets
        self.lighting = lighting
        self.create_environment()
        
    def create_environment(self):
        # Ground plane with tessellation for better shadows
        self.ground = Entity(
            model=Mesh(vertices=self.generate_tessellated_plane(200, 200),
                      uvs=self.generate_uvs(200, 200)),
            scale=(200, 1, 200),
            material=self.assets.materials['platform'],
            collider='mesh'
        )
        
        # Walls with PBR materials
        self.create_walls()
        
        # Add atmospheric effects
        self.create_atmosphere()
        
    def generate_tessellated_plane(self, width, height):
        vertices = []
        for z in range(height + 1):
            for x in range(width + 1):
                vertices.append(Vec3(
                    x - width/2,
                    np.sin(x/10) * 0.1, # Subtle height variation
                    z - height/2
                ))
        return vertices
        
    def create_walls(self):
        wall_data = [
            ((-100, 5, 0), (1, 10, 200)),
            ((100, 5, 0), (1, 10, 200)),
            ((0, 5, 100), (200, 10, 1)),
            ((0, 5, -100), (200, 10, 1))
        ]
        
        for pos, scale in wall_data:
            Entity(
                model='cube',
                scale=scale,
                position=pos,
                material=self.assets.materials['brick'],
                collider='box'
            )
            
    def create_atmosphere(self):
        # Volumetric fog
        self.fog = Entity(
            model='sphere',
            scale=500,
            color=color.rgb(200, 200, 255),
            alpha=0.1
        )
        
        # Particle systems for atmosphere
        self.dust_particles = ParticleSystem(
            emitter_type='sphere',
            position=(0, 10, 0),
            emission_rate=10,
            lifetime=5,
            scale=0.1,
            color=color.rgba(1, 1, 1, 0.1)
        )

class EnhancedGameManager:
    def __init__(self):
        self.app = Ursina()
        window.title = 'Enhanced Railway Station'
        window.vsync = True
        
        # Initialize systems
        self.lighting = AdvancedLightingSystem()
        self.assets = EnhancedAssetManager()
        self.station = EnhancedStation(self.assets, self.lighting)
        
        # Enhanced post-processing
        self.setup_post_processing()
        
        # Player setup with enhanced camera
        self.setup_player()
        
    def setup_post_processing(self):
        self.bloom = Entity(
            model='quad',
            scale=2,
            shader=Shader(
                vertex='shader/bloom.vert',
                fragment='shader/bloom.frag'
            )
        )
        
        self.hdr = Entity(
            model='quad',
            scale=2,
            shader=Shader(
                vertex='shader/hdr.vert',
                fragment='shader/hdr.frag'
            )
        )
        
    def setup_player(self):
        self.player = FirstPersonController()
        self.player.speed = 5
        camera.shader = lit_with_shadows_shader
        camera.clip_plane_near = 0.1
        camera.clip_plane_far = 1000
        
    def update(self):
        self.lighting.update_exposure(time.dt)
        
    def run(self):
        self.app.run()

if __name__ == '__main__':
    game = EnhancedGameManager()
    game.run()
