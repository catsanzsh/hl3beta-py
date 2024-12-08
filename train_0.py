from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# Initialize Ursina App
app = Ursina()

# State Variables
intro_active = True

# Intro Entities
intro_background = Entity(
    parent=camera.ui,
    model='quad',
    color=color.black,
    scale=(2, 1.5),
    z=0
)

intro_title = Text(
    parent=camera.ui,
    text='Welcome to British Railway Station',
    origin=(0, 0),
    scale=2,
    color=color.red,
    background=True,
    position=(0, 0.2)
)

intro_instructions = Text(
    parent=camera.ui,
    text='Move with WASD.\nPress "E" to interact.\nPress "Enter" to Start.',
    origin=(0, 0),
    scale=1.5,
    color=color.white,
    background=True,
    position=(0, -0.2)
)

# Function to Disable Intro Entities
def disable_intro():
    intro_background.disable()
    intro_title.disable()
    intro_instructions.disable()

# Environment Setup
ground = Entity(
    model='plane',
    scale=(200, 1, 200),
    color=color.dark_gray,
    texture_scale=(100, 100),
    collider='box'  # Prevent falling through
)

# Station Walls using built-in cube model
walls = [
    Entity(model='cube', scale=(1, 10, 200), position=(-100, 5, 0), color=color.white, collider='box'),
    Entity(model='cube', scale=(1, 10, 200), position=(100, 5, 0), color=color.white, collider='box'),
    Entity(model='cube', scale=(200, 10, 1), position=(0, 5, 100), color=color.white, collider='box'),
    Entity(model='cube', scale=(200, 10, 1), position=(0, 5, -100), color=color.white, collider='box')
]

# Lighting
point_light = PointLight(position=(0, 20, 0), color=color.white)
ambient_light = AmbientLight(color=color.rgb(100, 100, 100))
scene.lights.append(point_light)
scene.lights.append(ambient_light)

# Player Setup
player = FirstPersonController()
player.speed = 5
player.enabled = False  # Disabled during intro

# Platforms with Colliders
platforms = [
    Entity(model='cube', scale=(50, 1, 5), position=(-50, 0.5, -20), color=color.gray, collider='box'),
    Entity(model='cube', scale=(50, 1, 5), position=(50, 0.5, -20), color=color.gray, collider='box')
]

# Benches
benches = []
for i in range(-45, 46, 10):
    benches.append(Entity(model='cube', scale=(4, 1, 2), position=(i, 1, -20), color=color.brown, collider='box'))

# Lamp Posts
lamp_posts = []
for i in range(-45, 46, 15):
    # Lamp Pole
    lamp_posts.append(Entity(
        model='cylinder',
        scale=(0.2, 5, 0.2),
        position=(i, 2.5, -18),
        color=color.white,
        collider='box'
    ))
    # Lamp Light
    lamp_posts.append(Entity(
        model='sphere',
        scale=(0.5, 0.5, 0.5),
        position=(i, 5.5, -18),
        color=color.yellow,
        collider='box'
    ))

# Signage
sign = Entity(
    model='quad',
    scale=(5, 2, 1),
    position=(0, 6, -20.25),
    color=color.white,
    collider='box'
)
Text(
    parent=sign,
    text='British Railway Station',
    position=(0, 0.3),
    origin=(0, 0),
    scale=2,
    color=color.black,
    background=True
)

# Train Class with Collision
class Train(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Train Body
        self.body = Entity(
            model='cube',
            scale=(10, 3, 5),
            color=color.white,
            position=(0, 1.5, 0),
            parent=self,
            collider='box'
        )
        
        # Windows
        window_spacing = 2.5
        for i in range(-4, 5):
            Entity(
                model='cube',
                scale=(1, 1, 1),
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
                color=color.black,
                position=(i * wheel_spacing, 0.5, -2.5),
                rotation=(90, 0, 0),
                parent=self.body,
                collider='box'
            )
        
        # Position and Speed
        self.position = Vec3(-80, 1.5, 0)
        self.speed = 8

    def update(self):
        if not intro_active:
            self.x += time.dt * self.speed
            if self.x > 100:
                self.x = -100  # Loop back to start position

# Instantiate Train
train = Train()

# Train Track with Colliders
for i in range(-100, 101, 10):
    Entity(
        model='cube',
        scale=(10, 0.5, 2),
        position=(i, 0.25, 0),
        color=color.black,
        collider='box'
    )

# NPC with Collider
npc = Entity(
    model='cube',
    scale=(1, 2, 1),
    color=color.orange,
    position=(10, 1, -5),
    collider='box'
)

# Door with Collider
door = Entity(
    model='cube',
    scale=(3, 7, 1),
    position=(0, 3.5, 20),
    color=color.blue,
    collider='box'
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
def open_door():
    if abs(player.position.z - door.position.z) < 5 and abs(player.position.x - door.position.x) < 3:
        door.y += time.dt * 2
        if door.y > 7:
            door.y = 7

def update():
    global intro_active

    if intro_active:
        if held_keys['enter']:
            intro_active = False
            disable_intro()
            player.enabled = True  # Enable player control
    else:
        # Train Movement handled within Train class

        # Player Interaction
        if held_keys['e']:
            if abs(player.position.x - npc.position.x) < 2 and abs(player.position.z - npc.position.z) < 2:
                print("NPC Interaction: Welcome to the station!")

        # Door Mechanic
        open_door()

# Add update function to Ursina
app.update = update

# Run the application
app.run()
