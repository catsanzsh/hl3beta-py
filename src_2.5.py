from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import sys
import time

class AssetManager:
    """
    Manages loading and storing textures.
    """
    def __init__(self):
        self.textures = {}
        self._load_textures()
    
    def _load_textures(self):
        texture_paths = {
            'brick': 'assets/brick_wall.png',
            'platform': 'assets/platform.png',
            'bench': 'assets/bench.png',
            'lamp_post': 'assets/lamp_post.png',
            'sign': 'assets/sign.png',
            'train_body': 'assets/train_body.png',
            'train_window': 'assets/train_window.png',
            'train_wheel': 'assets/train_wheel.png'
        }
        
        for key, path in texture_paths.items():
            try:
                self.textures[key] = load_texture(path)
            except Exception as e:
                print(f"Warning: Failed to load texture '{path}': {e}")
                self.textures[key] = 'white_cube'

class Station:
    """
    Constructs the train station environment.
    """
    def __init__(self, assets):
        self.assets = assets
        self.create_environment()
        self.create_platforms()
        self.create_furniture()
    
    def create_environment(self):
        # Ground
        self.ground = Entity(
            model='plane',
            scale=(200, 1, 200),
            texture='white_cube',
            texture_scale=(100, 100),
            color=color.dark_gray,
            collider='box'
        )
        
        # Walls
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
                texture=self.assets.textures['brick'],
                color=color.white,
                collider='box'
            )
        
        # Lighting
        PointLight(position=(0, 20, 0), color=color.white)
        AmbientLight(color=color.rgba(100, 100, 100, 0.2))
    
    def create_platforms(self):
        platform_positions = [(-50, 0.5, -20), (50, 0.5, -20)]
        
        for pos in platform_positions:
            Entity(
                model='cube',
                scale=(50, 1, 5),
                position=pos,
                texture=self.assets.textures['platform'],
                color=color.gray,
                collider='box'
            )
    
    def create_furniture(self):
        # Benches
        for i in range(-45, 46, 10):
            Entity(
                model='cube',
                scale=(4, 1, 2),
                position=(i, 1, -20),
                texture=self.assets.textures['bench'],
                color=color.brown,
                collider='box'
            )
        
        # Lamp Posts
        for i in range(-45, 46, 15):
            # Lamp Pole (using 'cube' model to avoid missing model issues)
            Entity(
                model='cube',
                scale=(0.2, 5, 0.2),
                position=(i, 2.5, -18),
                texture=self.assets.textures['lamp_post'],
                color=color.white,
                collider='box'
            )
            # Lamp Light
            Entity(
                model='sphere',
                scale=0.5,
                position=(i, 5.5, -18),
                color=color.yellow,
                collider='box'
            )

class Train(Entity):
    """
    Represents the moving train with collision detection.
    """
    def __init__(self, assets):
        super().__init__()
        self.assets = assets
        self.stopped = False
        self.create_train()
    
    def create_train(self):
        # Body
        self.body = Entity(
            parent=self,
            model='cube',
            scale=(10, 3, 5),
            texture=self.assets.textures['train_body'],
            position=(0, 1.5, 0),
            collider='box'
        )
        
        # Windows
        for i in range(-4, 5):
            Entity(
                parent=self.body,
                model='cube',
                scale=(1, 1, 1),
                texture=self.assets.textures['train_window'],
                position=(i * 2.5, 1.5, 2.6)
            )
        
        # Wheels
        for i in range(-3, 4, 3):
            Entity(
                parent=self.body,
                model='cylinder',
                scale=(1, 0.5, 1),
                texture=self.assets.textures['train_wheel'],
                position=(i * 3, 0.5, -2.5),
                rotation=(90, 0, 0)
            )
        
        self.position = Vec3(-80, 1.5, 0)
        self.speed = 8
    
    def update(self):
        if not self.stopped:
            self.x += time.dt * self.speed
            if self.x > 50:
                self.stop_at_platform()
    
    def stop_at_platform(self):
        self.stopped = True
        invoke(self.restart_journey, delay=5)
    
    def restart_journey(self):
        self.x = -80
        self.stopped = False

class HUD:
    """
    Manages the Heads-Up Display elements.
    """
    def __init__(self, player, train):
        self.player = player
        self.train = train
        self.start_time = time.time()
        
        # Station Name
        Text(
            text='British Railway Station',
            position=(0, 0.45),
            origin=(0, 0),
            scale=2,
            background=True
        )
        
        # Train Status
        self.train_status = Text(
            text='Train Status: En Route',
            position=(-0.85, 0.4),
            scale=1.2,
            background=True
        )
        
        # Player Position
        self.position_text = Text(
            text='Position: X: 0 Y: 0 Z: 0',
            position=(-0.85, 0.35),
            scale=1,
            background=True
        )
        
        # Interaction Prompt
        self.interaction_text = Text(
            text='',
            position=(0, -0.4),
            origin=(0, 0),
            scale=1.2,
            background=True
        )
        
        # Controls Help
        Text(
            text='Controls: WASD - Move | SPACE - Jump | E - Interact | ESC - Exit',
            position=(0, -0.45),
            origin=(0, 0),
            scale=1,
            background=True
        )
        
        # FPS Counter
        self.fps_counter = Text(
            text='FPS: 60',
            position=(0.8, 0.45),
            scale=1,
            background=True
        )
        
        # Game Time
        self.time_display = Text(
            text='Time: 00:00',
            position=(0.8, 0.4),
            scale=1,
            background=True
        )
    
    def update(self):
        # Update train status
        status = 'Stopped at Platform' if self.train.stopped else 'En Route'
        self.train_status.text = f'Train Status: {status}'
        
        # Update player position
        pos = self.player.position
        self.position_text.text = f'Position: X: {pos.x:.1f} Y: {pos.y:.1f} Z: {pos.z:.1f}'
        
        # Update FPS
        self.fps_counter.text = f'FPS: {int(1 / time.dt) if time.dt > 0 else "N/A"}'
        
        # Update game time
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        self.time_display.text = f'Time: {minutes:02d}:{seconds:02d}'
        
        # Update interaction prompt
        self.update_interaction_prompt()
    
    def update_interaction_prompt(self):
        # Clear previous prompt
        self.interaction_text.text = ''
        
        # Check for nearby interactable objects
        if distance(self.player.position, self.train.position) < 5:
            self.interaction_text.text = 'Press E to board the train'

def distance(pos1, pos2):
    """
    Calculates the Euclidean distance between two positions.
    """
    return (pos1 - pos2).length()

class Door(Entity):
    """
    Represents a hinged door with physics-like behavior.
    """
    def __init__(self, position=(0, 3.5, 20), scale=(3, 7, 1), color=color.blue, **kwargs):
        super().__init__(
            model='cube',
            position=position,
            scale=scale,
            color=color,
            collider='box',
            **kwargs
        )
        # Set origin to the left side to simulate a hinge
        self.origin = Vec3(-0.5, 0, 0)  # Hinge on the left
        self.rotation_y = 0  # Initial closed position
        self.is_open = False  # Door state
    
    def toggle(self):
        """
        Toggles the door between open and closed states with animation.
        """
        if self.is_open:
            # Close the door
            self.animate_rotation_y(0, duration=0.5, curve=curve.ease_out)
            self.is_open = False
        else:
            # Open the door by rotating 90 degrees
            self.animate_rotation_y(90, duration=0.5, curve=curve.ease_out)
            self.is_open = True

class GameManager:
    """
    Manages the overall game, including initialization and updates.
    """
    def __init__(self):
        self.app = Ursina()
        window.title = 'Railway Station Simulation'
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        window.fps_counter.enabled = False

        self.assets = AssetManager()
        self.station = Station(self.assets)
        self.train = Train(self.assets)
        
        # Player Setup
        self.player = FirstPersonController()
        self.player.speed = 5
        self.player.gravity = 0.5
        
        # HUD Setup
        self.hud = HUD(self.player, self.train)
        
        # Door Setup
        self.door = Door()
        
        # Interaction Flags
        self.door_nearby = False
        
        # Assign update method
        self.app.update = self.update

    def update(self):
        self.handle_door()
        self.hud.update()
        self.train.update()
        self.handle_interactions()
        self.handle_exit()
    
    def handle_door(self):
        """
        Handles door animations based on player proximity and input.
        """
        distance_to_door = distance(self.player.position, self.door.position)
        self.door_nearby = distance_to_door < 5  # Define proximity threshold
        
        if self.door_nearby and held_keys['e']:
            if not self.door.is_open:
                self.door.toggle()
        elif not self.door_nearby and self.door.is_open:
            self.door.toggle()
    
    def handle_interactions(self):
        """
        Handles player interactions with NPCs and other entities.
        """
        # Example: Interaction with NPC can be added here
        # Placeholder for future interactions
        pass
    
    def handle_exit(self):
        """
        Allows the player to exit the game using the ESC key.
        """
        if held_keys['escape']:
            sys.exit()
    
    def run(self):
        """
        Runs the Ursina application.
        """
        try:
            self.app.run()
        except Exception as e:
            print(f"Error running game: {e}")
            sys.exit(1)

if __name__ == '__main__':
    game = GameManager()
    game.run()
