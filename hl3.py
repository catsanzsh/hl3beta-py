from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# Initialize Ursina App
app = Ursina()

# Load Textures
brick_texture = load_texture('assets/brick_wall.png')
platform_texture = load_texture('assets/platform.png')
bench_texture = load_texture('assets/bench.png')
lamp_post_texture = load_texture('assets/lamp_post.png')
sign_texture = load_texture('assets/sign.png')
train_body_texture = load_texture('assets/train_body.png')
train_window_texture = load_texture('assets/train_window.png')
train_wheel_texture = load_texture('assets/train_wheel.png')

# Environment Setup
ground = Entity(
    model='plane',
    scale=(200, 1, 200),
    texture='white_cube',
    texture_scale=(100, 100),
    color=color.dark_gray,
    collider='box'  # Added collider to prevent falling through
)

# Station Walls
walls = [
    Entity(model='cube', scale=(1, 10, 200), position=(-100, 5, 0), texture=brick_texture, color=color.white, collider='box'),
    Entity(model='cube', scale=(1, 10, 200), position=(100, 5, 0), texture=brick_texture, color=color.white, collider='box'),
    Entity(model='cube', scale=(200, 10, 1), position=(0, 5, 100), texture=brick_texture, color=color.white, collider='box'),
    Entity(model='cube', scale=(200, 10, 1), position=(0, 5, -100), texture=brick_texture, color=color.white, collider='box')
]

# Lighting
PointLight(position=(0, 20, 0), color=color.white)
AmbientLight(color=color.rgba(100, 100, 100, 0.2))

# Player Setup
player = FirstPersonController()
player.speed = 5

# Platforms with Colliders
platforms = [
    Entity(model='cube', scale=(50, 1, 5), position=(-50, 0.5, -20), texture=platform_texture, color=color.gray, collider='box'),
    Entity(model='cube', scale=(50, 1, 5), position=(50, 0.5, -20), texture=platform_texture, color=color.gray, collider='box')
]

# Benches
benches = []
for i in range(-45, 46, 10):
    benches.append(Entity(model='cube', scale=(4, 1, 2), position=(i, 1, -20), texture=bench_texture, color=color.brown, collider='box'))

# Lamp Posts
lamp_posts = []
for i in range(-45, 46, 15):
    # Lamp Pole
    lamp_posts.append(Entity(
        model='cylinder',
        scale=(0.2, 5, 0.2),
        position=(i, 2.5, -18),
        texture=lamp_post_texture,
        color=color.white,
        collider='box'
    ))
    # Lamp Light
    lamp_posts.append(Entity(
        model='sphere',
        scale=(0.5, 0.5, 0.5),
        position=(i, 5.5, -18),
        texture='white_cube',
        color=color.yellow,
        collider='box'
    ))

# Signage
sign = Entity(
    model='quad',
    scale=(5, 2, 1),
    position=(0, 6, -20.25),
    texture=sign_texture,
    color=color.white,
    collider='box'
)
Text(
    text='British Railway Station',
    position=(0, 0.3),
    origin=(0, 0),
    scale=2,
    background=True,
    parent=sign
)

# Train Class with Collision
class Train(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Train Body
        self.body = Entity(
            model='cube',
            scale=(10, 3, 5),
            texture=train_body_texture,
            color=color.white,
            position=(0, 1.5, 0),
            parent=self,
            collider='box'  # Added collider
        )
        
        # Windows
        window_spacing = 2.5
        for i in range(-4, 5):
            Entity(
                model='cube',
                scale=(1, 1, 1),
                texture=train_window_texture,
                color=color.blue,
                position=(i * window_spacing, 1.5, 2.6),
                parent=self.body,
                collider='box'  # Optional: if windows should have collision
            )
        
        # Wheels
        wheel_spacing = 3
        for i in range(-3, 4, 3):
            Entity(
                model='cylinder',
                scale=(1, 0.5, 1),
                texture=train_wheel_texture,
                color=color.black,
                position=(i * wheel_spacing, 0.5, -2.5),
                rotation=(90, 0, 0),
                parent=self.body,
                collider='box'  # Added collider
            )
        
        # Position and Speed
        self.position = Vec3(-80, 1.5, 0)
        self.speed = 8

    def update(self):
        self.x += time.dt * self.speed
        if self.x > 50:
            self.x = -80  # Reset to start position for looping

# Instantiate Train
train = Train()

# Train Track with Colliders
for i in range(-100, 101, 10):
    Entity(
        model='cube',
        scale=(10, 0.5, 2),
        position=(i, 0.25, 0),
        texture='white_cube',
        color=color.black,
        collider='box'  # Added collider
    )

# NPC with Collider
npc = Entity(
    model='cube',
    scale=(1, 2, 1),
    texture='white_cube',
    color=color.orange,
    position=(10, 1, -5),
    collider='box'  # Added collider
)

# Door with Collider
door = Entity(
    model='cube',
    scale=(3, 7, 1),
    position=(0, 3.5, 20),
    texture='white_cube',
    color=color.blue,
    collider='box'  # Added collider
)

# HUD
info_text = Text(
    text='Move with WASD. Press "E" to interact.',
    position=(-0.6, 0.45),
    origin=(0, 0),
    scale=1.5,
    background=True
)

# Scripted Events
train_arrived = False

def open_door():
    if abs(player.position.z - door.position.z) < 5 and abs(player.position.x - door.position.x) < 3:
        door.y += time.dt * 2
        if door.y > 7:
            door.y = 7

def update():
    global train_arrived

    # Train Movement handled within Train class

    # Player Interaction
    if held_keys['e']:
        if abs(player.position.x - npc.position.x) < 2 and abs(player.position.z - npc.position.z) < 2:
            print("NPC Interaction: Welcome to the station!")

    # Door Mechanic
    open_door()

# Start Application
app.run()
