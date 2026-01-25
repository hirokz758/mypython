import tkinter as tk
import random
import math
import os
import sys

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 600

CANNON_Y = 550

ENEMY_SPACE_X = 100
ENEMY_SPACE_Y = 40
ENEMY_MOVE_SPACE_X = 20
ENEMY_MOVE_SPEED = 500
NUMBER_OF_ENEMY = 10
ENEMY_SHOOT_INTERVAL = 1000

BULLET_HEIGHT = 10
BULLET_WIDTH = 5
BULLET_SPEED = 10

TEXT_GOOD_SIZE = 10
TEXT_CONGRATULATIONS_SIZE = 50
TEXT_GAMECLEAR_SIZE = 60
TEXT_GAMEOVER_SIZE = 90

cannon_x = WINDOW_WIDTH // 2
cannon_y = CANNON_Y
cannon_id = None
cannon_glow_id = None
cannon_exist = True

enemies = []
my_bullets = []
enemy_bullets = []
particles = []
stars = []
screen_shake_offset = [0, 0]
glow_phase = 0

# ===== Particle System =====
class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.age = 0
        self.id = cv.create_oval(
            x - size, y - size, x + size, y + size,
            fill=color, outline=""
        )
    
    def update(self):
        self.age += 1
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # gravity
        alpha = 1 - (self.age / self.lifetime)
        if alpha <= 0:
            return False
        cv.coords(self.id, self.x - self.size, self.y - self.size,
                  self.x + self.size, self.y + self.size)
        return True
    
    def destroy(self):
        cv.delete(self.id)

def create_explosion(x, y, color_palette):
    """Create particle explosion effect"""
    for _ in range(12):  # Reduced from 20 to 12
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        color = random.choice(color_palette)
        size = random.randint(2, 5)
        lifetime = random.randint(10, 20)  # Reduced from 20-40 to 10-20
        particles.append(Particle(x, y, vx, vy, color, size, lifetime))

def update_particles():
    """Update all particles"""
    global particles
    particles = [p for p in particles if p.update()]
    root.after(20, update_particles)

# ===== Starfield Background =====
class Star:
    def __init__(self):
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(0, WINDOW_HEIGHT)
        self.speed = random.uniform(0.2, 0.8)  # Slower movement
        self.size = random.randint(1, 2)  # Smaller stars
        # More subtle, dimmer colors
        brightness = random.choice(['#444444', '#555555', '#666666', '#4A5568'])
        self.id = cv.create_oval(
            self.x, self.y, self.x + self.size, self.y + self.size,
            fill=brightness, outline=""
        )
    
    def update(self):
        self.y += self.speed
        if self.y > WINDOW_HEIGHT:
            self.y = 0
            self.x = random.randint(0, WINDOW_WIDTH)
        cv.coords(self.id, self.x, self.y, self.x + self.size, self.y + self.size)

def create_starfield():
    """Create animated starfield background"""
    for _ in range(15):  # Fewer stars for cleaner look
        stars.append(Star())

def update_starfield():
    """Update starfield animation"""
    for star in stars:
        star.update()
    root.after(80, update_starfield)  # Slower update rate

# ===== Screen Shake Effect =====
def screen_shake(intensity=10, duration=200):
    """Apply screen shake effect"""
    global screen_shake_offset
    start_time = [0]
    
    def shake_step():
        if start_time[0] < duration:
            screen_shake_offset[0] = random.randint(-intensity, intensity)
            screen_shake_offset[1] = random.randint(-intensity, intensity)
            cv.move("all", screen_shake_offset[0], screen_shake_offset[1])
            start_time[0] += 20
            root.after(20, shake_step)
        else:
            cv.move("all", -screen_shake_offset[0], -screen_shake_offset[1])
            screen_shake_offset[0] = 0
            screen_shake_offset[1] = 0
    
    shake_step()

# ===== 自機まわり =====
def create_cannon(x, y):
    global cannon_x, cannon_y, cannon_id, cannon_glow_id, cannon_exist
    cannon_x = x
    cannon_y = y
    
    # Store all spacecraft parts
    cannon_id = []
    
    # Engine glow (bottom thrusters)
    engine_glow_left = cv.create_oval(
        cannon_x - 18, cannon_y - 5,
        cannon_x - 10, cannon_y + 8,
        fill="#00FFFF", outline="#0088FF", width=2, tags="cannon_engine"
    )
    engine_glow_right = cv.create_oval(
        cannon_x + 10, cannon_y - 5,
        cannon_x + 18, cannon_y + 8,
        fill="#00FFFF", outline="#0088FF", width=2, tags="cannon_engine"
    )
    
    # Main fuselage (body)
    fuselage = cv.create_polygon(
        cannon_x, cannon_y - 25,      # nose
        cannon_x + 12, cannon_y - 10,  # right side
        cannon_x + 10, cannon_y + 5,   # right bottom
        cannon_x - 10, cannon_y + 5,   # left bottom
        cannon_x - 12, cannon_y - 10,  # left side
        fill="#2E86AB", outline="#1A5F7A", width=2, tags="cannon_body", smooth=True
    )
    
    # Wings
    left_wing = cv.create_polygon(
        cannon_x - 12, cannon_y - 8,
        cannon_x - 25, cannon_y,
        cannon_x - 20, cannon_y + 3,
        cannon_x - 10, cannon_y - 5,
        fill="#1A5F7A", outline="#0D3B52", width=2, tags="cannon_wing"
    )
    right_wing = cv.create_polygon(
        cannon_x + 12, cannon_y - 8,
        cannon_x + 25, cannon_y,
        cannon_x + 20, cannon_y + 3,
        cannon_x + 10, cannon_y - 5,
        fill="#1A5F7A", outline="#0D3B52", width=2, tags="cannon_wing"
    )
    
    # Cockpit window
    cockpit = cv.create_oval(
        cannon_x - 5, cannon_y - 18,
        cannon_x + 5, cannon_y - 8,
        fill="#00FFFF", outline="#FFFFFF", width=1, tags="cannon_cockpit"
    )
    
    # Weapon barrels
    left_barrel = cv.create_rectangle(
        cannon_x - 15, cannon_y - 15,
        cannon_x - 13, cannon_y - 5,
        fill="#FF6B35", outline="#C44900", width=1, tags="cannon_weapon"
    )
    right_barrel = cv.create_rectangle(
        cannon_x + 13, cannon_y - 15,
        cannon_x + 15, cannon_y - 5,
        fill="#FF6B35", outline="#C44900", width=1, tags="cannon_weapon"
    )
    
    # Outer glow aura
    cannon_glow_id = cv.create_oval(
        cannon_x - 30, cannon_y - 30,
        cannon_x + 30, cannon_y + 30,
        fill="", outline="cyan", width=2, tags="cannon_glow"
    )
    
    # Store all IDs
    cannon_id = {
        "fuselage": fuselage,
        "left_wing": left_wing,
        "right_wing": right_wing,
        "cockpit": cockpit,
        "left_barrel": left_barrel,
        "right_barrel": right_barrel,
        "engine_left": engine_glow_left,
        "engine_right": engine_glow_right,
        "glow": cannon_glow_id
    }
    
    cannon_exist = True
    cv.tag_bind("cannon_body", "<ButtonPress-3>", cannon_pressed)
    cv.tag_bind("cannon_body", "<Button1-Motion>", cannon_dragged)
    cv.tag_bind("cannon_wing", "<Button1-Motion>", cannon_dragged)
    cv.tag_bind("cannon_cockpit", "<Button1-Motion>", cannon_dragged)
    animate_cannon_glow()
    animate_engine_thrust()

def animate_engine_thrust():
    """Animate the engine thrust glow"""
    if not cannon_exist or not cannon_id:
        return
    
    # Pulsing engine effect
    phase = random.uniform(0, 0.5)
    colors = ["#00FFFF", "#00DDFF", "#00BBFF", "#0099FF"]
    
    if "engine_left" in cannon_id and "engine_right" in cannon_id:
        cv.itemconfig(cannon_id["engine_left"], fill=random.choice(colors))
        cv.itemconfig(cannon_id["engine_right"], fill=random.choice(colors))
    
    root.after(100, animate_engine_thrust)

def animate_cannon_glow():
    """Animate the glowing effect around cannon"""
    global glow_phase
    if not cannon_exist or not cannon_id or "glow" not in cannon_id:
        return
    glow_phase += 0.1
    size = 30 + math.sin(glow_phase) * 5
    cv.coords(cannon_id["glow"],
              cannon_x - size, cannon_y - size,
              cannon_x + size, cannon_y + size)
    root.after(50, animate_cannon_glow)

def cannon_pressed(event):
    if not cannon_exist:
        return
    create_my_bullet(event.x, CANNON_Y)
    create_muzzle_flash(event.x, CANNON_Y)

def create_muzzle_flash(x, y):
    """Create muzzle flash effect when shooting"""
    flash_id = cv.create_oval(
        x - 15, y - 15, x + 15, y + 15,
        fill="yellow", outline="orange", width=2
    )
    root.after(50, lambda: cv.delete(flash_id))

def cannon_dragged(event):
    global cannon_x
    if not cannon_exist or not cannon_id:
        return
    
    # Calculate movement delta
    old_x = cannon_x
    cannon_x = event.x
    dx = cannon_x - old_x
    
    # Move all spacecraft parts
    cv.move("cannon_body", dx, 0)
    cv.move("cannon_wing", dx, 0)
    cv.move("cannon_cockpit", dx, 0)
    cv.move("cannon_weapon", dx, 0)
    cv.move("cannon_engine", dx, 0)
    cv.move("cannon_glow", dx, 0)

def destroy_cannon():
    global cannon_id
    if cannon_id:
        # Delete all spacecraft parts
        for part_id in cannon_id.values():
            if part_id:
                cv.delete(part_id)
        cannon_id = None

# ===== キーボード操作の追加 =====
def move_cannon(dx):
    global cannon_x
    if not cannon_exist or not cannon_id:
        return
    cannon_x += dx
    cannon_x = max(30, min(WINDOW_WIDTH - 30, cannon_x))
    
    # Move all spacecraft parts
    cv.move("cannon_body", dx, 0)
    cv.move("cannon_wing", dx, 0)
    cv.move("cannon_cockpit", dx, 0)
    cv.move("cannon_weapon", dx, 0)
    cv.move("cannon_engine", dx, 0)
    cv.move("cannon_glow", dx, 0)

def on_key_press(event):
    if event.keysym == "Left":
        move_cannon(-15)
    elif event.keysym == "Right":
        move_cannon(15)
    elif event.keysym == "space":
        if cannon_exist:
            create_my_bullet(cannon_x, CANNON_Y)
            create_muzzle_flash(cannon_x, CANNON_Y)

# ===== 自分の弾まわり =====
def create_my_bullet(x, y):
    bullet_id = cv.create_rectangle(
        x - BULLET_WIDTH, y + BULLET_HEIGHT,
        x + BULLET_WIDTH, y - BULLET_HEIGHT,
        fill="cyan", outline="white", width=1
    )
    # Create bullet glow
    glow_id = cv.create_oval(
        x - 8, y - 8, x + 8, y + 8,
        fill="", outline="cyan", width=2
    )
    bullet = {
        "x": x,
        "y": y,
        "id": bullet_id,
        "glow_id": glow_id,
        "alive": True,
        "trail": []
    }
    my_bullets.append(bullet)
    index = len(my_bullets) - 1
    shoot_my_bullet(index)

def shoot_my_bullet(index):
    bullet = my_bullets[index]
    if not bullet["alive"]:
        return
    if bullet["y"] >= 0:
        # Create trail particle - reduced frequency
        if random.random() < 0.2:  # Reduced from 0.5 to 0.2
            particles.append(Particle(
                bullet["x"], bullet["y"], 
                random.uniform(-0.5, 0.5), random.uniform(0, 1),
                "cyan", 2, 15
            ))
        
        cv.move(bullet["id"], 0, -BULLET_HEIGHT)
        cv.move(bullet["glow_id"], 0, -BULLET_HEIGHT)
        bullet["y"] -= BULLET_HEIGHT
        defeat_enemy_with_bullet(index)
        root.after(BULLET_SPEED, lambda i=index: shoot_my_bullet(i))
    else:
        destroy_my_bullet(index)

def defeat_enemy_with_bullet(index):
    bullet = my_bullets[index]
    if not bullet["alive"]:
        return
    bullet_coords = cv.coords(bullet["id"])
    for enemy in enemies:
        if enemy["exist"]:
            enemy_coords = cv.coords(enemy["id"])
            if check_collision_rect(bullet_coords, enemy_coords):
                enemy["exist"] = False
                # Create explosion effect
                create_explosion(enemy["x"], enemy["y"], 
                               ["yellow", "orange", "red", "white"])
                # Create expanding ring effect
                create_ring_effect(enemy["x"], enemy["y"])
                
                # Delete all UFO parts
                if "parts" in enemy:
                    for part_id in enemy["parts"].values():
                        if part_id:
                            cv.delete(part_id)
                cv.delete(enemy["id"])
                
                # Animated text
                text_id = cv.create_text(
                    enemy["x"], enemy["y"],
                    text="BOOM!", fill="yellow",
                    font=("System", TEXT_GOOD_SIZE * 2, "bold"),
                    tag="good"
                )
                animate_text_fade(text_id, enemy["y"])
                destroy_my_bullet(index)
                break

def create_ring_effect(x, y):
    """Create expanding ring effect"""
    ring_id = cv.create_oval(x-5, y-5, x+5, y+5, 
                             outline="yellow", width=3, fill="")
    
    def expand_ring(size, alpha):
        if size < 50 and alpha > 0:
            cv.coords(ring_id, x-size, y-size, x+size, y+size)
            root.after(20, lambda: expand_ring(size+3, alpha-0.1))
        else:
            cv.delete(ring_id)
    
    expand_ring(5, 1.0)

def animate_text_fade(text_id, start_y):
    """Animate text floating up and fading"""
    def fade_step(y, steps):
        if steps > 0:
            cv.move(text_id, 0, -2)
            root.after(30, lambda: fade_step(y-2, steps-1))
        else:
            cv.delete(text_id)
    fade_step(start_y, 20)

def destroy_my_bullet(index):
    bullet = my_bullets[index]
    if bullet["alive"]:
        bullet["alive"] = False
        cv.delete(bullet["id"])
        if "glow_id" in bullet:
            cv.delete(bullet["glow_id"])

# ===== 敵まわり =====
def create_enemies():
    colors = ["#FF6B6B", "#FFA500", "#FFD700", "#FF1493", "#FF4500"]
    for i in range(NUMBER_OF_ENEMY):
        x = i * ENEMY_SPACE_X + 50
        y = ENEMY_SPACE_Y
        color = colors[i % len(colors)]
        enemy = {
            "x": x % WINDOW_WIDTH,
            "y": y + x // WINDOW_WIDTH * ENEMY_SPACE_Y,
            "parts": {},  # Store all UFO parts
            "exist": True,
            "color": color,
            "pulse_phase": random.uniform(0, 2 * math.pi),
            "beam_phase": random.uniform(0, 2 * math.pi)
        }
        
        # Create UFO flying saucer
        create_ufo(enemy)
        enemies.append(enemy)
    
    for idx in range(len(enemies)):
        move_enemy(idx)
    pulse_enemies()
    animate_ufo_beams()

def create_ufo(enemy):
    """Create a detailed UFO flying saucer"""
    x = enemy["x"]
    y = enemy["y"]
    color = enemy["color"]
    
    # Light beam underneath (animated)
    beam = cv.create_polygon(
        x - 3, y + 15,
        x + 3, y + 15,
        x + 8, y + 30,
        x - 8, y + 30,
        fill="#FFFF00", outline="", stipple="gray25", tags="enemy_beam"
    )
    
    # Outer glow
    glow = cv.create_oval(
        x - 22, y - 22,
        x + 22, y + 22,
        fill="", outline=color, width=2, tags="enemy_glow"
    )
    
    # Saucer bottom (darker shade)
    bottom_color = darken_color(color)
    saucer_bottom = cv.create_oval(
        x - 18, y + 5,
        x + 18, y + 15,
        fill=bottom_color, outline=darken_color(bottom_color), width=1, tags="enemy_body"
    )
    
    # Main saucer body
    saucer = cv.create_oval(
        x - 20, y - 5,
        x + 20, y + 10,
        fill=color, outline="white", width=2, tags="enemy_body"
    )
    
    # Dome top
    dome = cv.create_oval(
        x - 10, y - 15,
        x + 10, y + 5,
        fill=lighten_color(color), outline="white", width=1, tags="enemy_body"
    )
    
    # Cockpit window (glowing)
    window = cv.create_oval(
        x - 5, y - 10,
        x + 5, y,
        fill="#00FFFF", outline="#FFFFFF", width=1, tags="enemy_window"
    )
    
    # Small lights on saucer edge
    light1 = cv.create_oval(
        x - 15, y + 2,
        x - 12, y + 5,
        fill="#00FF00", outline="", tags="enemy_lights"
    )
    light2 = cv.create_oval(
        x + 12, y + 2,
        x + 15, y + 5,
        fill="#FF0000", outline="", tags="enemy_lights"
    )
    light3 = cv.create_oval(
        x - 2, y + 8,
        x + 2, y + 11,
        fill="#0000FF", outline="", tags="enemy_lights"
    )
    
    # Store all parts
    enemy["parts"] = {
        "beam": beam,
        "glow": glow,
        "saucer_bottom": saucer_bottom,
        "saucer": saucer,
        "dome": dome,
        "window": window,
        "light1": light1,
        "light2": light2,
        "light3": light3
    }
    
    # Store main ID for collision
    enemy["id"] = saucer

def lighten_color(hex_color):
    """Lighten a hex color"""
    # Simple lightening by adding to RGB values
    r = min(255, int(hex_color[1:3], 16) + 40)
    g = min(255, int(hex_color[3:5], 16) + 40)
    b = min(255, int(hex_color[5:7], 16) + 40)
    return f"#{r:02X}{g:02X}{b:02X}"

def darken_color(hex_color):
    """Darken a hex color"""
    r = max(0, int(hex_color[1:3], 16) - 40)
    g = max(0, int(hex_color[3:5], 16) - 40)
    b = max(0, int(hex_color[5:7], 16) - 40)
    return f"#{r:02X}{g:02X}{b:02X}"

def animate_ufo_beams():
    """Animate the UFO light beams"""
    for enemy in enemies:
        if enemy["exist"] and "beam" in enemy["parts"]:
            enemy["beam_phase"] += 0.15
            # Pulsing opacity effect by changing stipple
            if math.sin(enemy["beam_phase"]) > 0:
                cv.itemconfig(enemy["parts"]["beam"], stipple="gray25")
            else:
                cv.itemconfig(enemy["parts"]["beam"], stipple="gray50")
    root.after(100, animate_ufo_beams)

def move_enemy(index):
    enemy = enemies[index]
    if not enemy["exist"]:
        return
    
    old_x = enemy["x"]
    old_y = enemy["y"]
    
    x = enemy["x"]
    y = enemy["y"]
    if x > WINDOW_WIDTH:
        x -= ENEMY_MOVE_SPACE_X
        y += ENEMY_SPACE_Y
    elif x < 0:
        x += ENEMY_MOVE_SPACE_X
        y += ENEMY_SPACE_Y
    if y % (ENEMY_SPACE_Y * 2) == ENEMY_SPACE_Y:
        x += ENEMY_MOVE_SPACE_X
    else:
        x -= ENEMY_MOVE_SPACE_X
    
    dx = x - old_x
    dy = y - old_y
    
    enemy["x"] = x
    enemy["y"] = y
    
    # Move all UFO parts together
    if "parts" in enemy:
        for part_id in enemy["parts"].values():
            if part_id:
                cv.move(part_id, dx, dy)
    
    root.after(ENEMY_MOVE_SPEED, lambda i=index: move_enemy(i))

def pulse_enemies():
    """Animate pulsing effect for enemies"""
    for enemy in enemies:
        if enemy["exist"] and "parts" in enemy and "glow" in enemy["parts"]:
            enemy["pulse_phase"] += 0.1
            size_offset = math.sin(enemy["pulse_phase"]) * 3
            cv.coords(
                enemy["parts"]["glow"],
                enemy["x"] - 22 - size_offset, enemy["y"] - 22 - size_offset,
                enemy["x"] + 22 + size_offset, enemy["y"] + 22 + size_offset
            )
    root.after(50, pulse_enemies)

def enemy_random_shoot():
    alive_indexes = [i for i, e in enumerate(enemies) if e["exist"]]
    if alive_indexes:
        idx = random.choice(alive_indexes)
        enemy = enemies[idx]
        create_enemy_bullet(enemy["x"], enemy["y"])
    root.after(ENEMY_SHOOT_INTERVAL, enemy_random_shoot)

# ===== 敵の弾まわり =====
def create_enemy_bullet(x, y):
    bullet_id = cv.create_rectangle(
        x - BULLET_WIDTH, y + BULLET_HEIGHT,
        x + BULLET_WIDTH, y - BULLET_HEIGHT,
        fill="#FF0000", outline="orange", width=1
    )
    glow_id = cv.create_oval(
        x - 8, y - 8, x + 8, y + 8,
        fill="", outline="red", width=2
    )
    bullet = {
        "x": x,
        "y": y,
        "id": bullet_id,
        "glow_id": glow_id,
        "alive": True
    }
    enemy_bullets.append(bullet)
    index = len(enemy_bullets) - 1
    shoot_enemy_bullet(index)

def shoot_enemy_bullet(index):
    bullet = enemy_bullets[index]
    if not bullet["alive"]:
        return
    if bullet["y"] <= WINDOW_HEIGHT:
        # Create trail particle - reduced frequency
        if random.random() < 0.15:  # Reduced from 0.3 to 0.15
            particles.append(Particle(
                bullet["x"], bullet["y"], 
                random.uniform(-0.5, 0.5), random.uniform(-1, 0),
                "red", 2, 15
            ))
        
        cv.move(bullet["id"], 0, BULLET_HEIGHT)
        cv.move(bullet["glow_id"], 0, BULLET_HEIGHT)
        bullet["y"] += BULLET_HEIGHT
        collision_enemy_bullet(index)
        root.after(BULLET_SPEED, lambda i=index: shoot_enemy_bullet(i))
    else:
        destroy_enemy_bullet(index)

def collision_enemy_bullet(index):
    global cannon_exist
    if not cannon_exist or not cannon_id or "fuselage" not in cannon_id:
        return
    bullet = enemy_bullets[index]
    if not bullet["alive"]:
        return
    cannon_coords = cv.coords(cannon_id["fuselage"])
    bullet_coords = cv.coords(bullet["id"])
    if check_collision_rect(bullet_coords, cannon_coords):
        # Create explosion at cannon position
        create_explosion(cannon_x, cannon_y, 
                       ["red", "orange", "yellow", "white"])
        screen_shake(15, 300)
        gameover()

def destroy_enemy_bullet(index):
    bullet = enemy_bullets[index]
    if bullet["alive"]:
        bullet["alive"] = False
        cv.delete(bullet["id"])
        if "glow_id" in bullet:
            cv.delete(bullet["glow_id"])

# ===== 共通: 四角どうしの当たり判定 =====
def check_collision_rect(a, b):
    return (b[0] < a[0] < b[2] and b[1] < a[1] < b[3])

# ===== GAME CLEAR / GAME OVER =====
def gameover():
    global cannon_exist
    cannon_exist = False
    destroy_cannon()
    cv.create_text(
        WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
        text="GAME OVER", fill="red",
        font=("System", TEXT_GAMEOVER_SIZE, "bold"),
        tags="game_over_text"
    )
    cv.create_text(
        WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80,
        text="Press R to Restart", fill="white",
        font=("System", 20),
        tags="game_over_text"
    )
    # Bind restart key
    root.bind("<KeyPress-r>", lambda e: reset_game())
    root.bind("<KeyPress-R>", lambda e: reset_game())

def reset_game():
    """Reset the game to initial state"""
    global cannon_exist, enemies, my_bullets, enemy_bullets, particles, stars
    
    # Delete ALL canvas items (including game over text, enemies, bullets, particles)
    cv.delete("all")
    
    # Clear particle objects
    for particle in particles:
        particle.destroy()
    
    # Reset game state lists
    enemies.clear()
    my_bullets.clear()
    enemy_bullets.clear()
    particles.clear()
    stars.clear()
    
    # Recreate starfield background
    create_starfield()
    
    # Recreate game objects
    create_cannon(WINDOW_WIDTH // 2, CANNON_Y)
    create_enemies()
    enemy_random_shoot()
    gameclear()

def gameclear():
    winflag = 0
    for enemy in enemies:
        if not enemy["exist"]:
            winflag += 1
    if winflag == NUMBER_OF_ENEMY:
        cv.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80,
            text="Congratulations!", fill="lime",
            font=("System", TEXT_CONGRATULATIONS_SIZE)
        )
        cv.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20,
            text="GAME CLEAR!", fill="lime",
            font=("System", TEXT_GAMECLEAR_SIZE)
        )

# ===== メイン処理 =====
if __name__ == "__main__":
    root = tk.Tk()
    root.title("🚀 SPACE INVADERS - ENHANCED EDITION 🚀")
    cv = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="#0a0a1a")
    cv.pack()

    # Create animated starfield background
    create_starfield()
    update_starfield()

    # Start particle system
    update_particles()

    # 自機を作る
    create_cannon(WINDOW_WIDTH // 2, CANNON_Y)

    # 敵を作って動かす
    create_enemies()

    # 敵のランダムショット開始
    enemy_random_shoot()

    # クリア判定開始
    gameclear()

    # キーボード操作のバインド
    root.bind("<KeyPress>", on_key_press)

    root.mainloop()
