import pygame
import sys
import math
import random


class BattleBox:
    def __init__(self, x: int=80, y: int=60, w: int=320, h: int=240):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    @property
    def center_x(self) -> int:
        return self.x + self.w // 2
    
    @property
    def center_y(self) -> int:
        return self.y + self.h // 2
    
    def draw(self, surface):
        WHITE = (255, 255, 255)
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.w, self.h), 3)


class Soul:
    def __init__(self, x: int, y: int, size: int=8, speed: int=4, hp: int=20):
        self.x: int = x
        self.y: int = y
        self.size: int = size
        self.speed: int = speed
        self.hp: int = hp
        self.max_hp: int = hp
        self.invincible_frames: int = 0

    def move(self, box: BattleBox):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > box.x + 3:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < box.x + box.w - self.size - 3:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > box.y + 3:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < box.y + box.h - self.size - 3:
            self.y += self.speed
        
        # Decrease invincibility frames
        if self.invincible_frames > 0:
            self.invincible_frames -= 1

    def take_damage(self, damage: int):
        if self.invincible_frames <= 0:
            self.hp -= damage
            self.invincible_frames = 30  # 0.5 seconds of invincibility at 60 FPS
            return True
        return False

    def draw(self, surface):
        # Flashing effect when invincible
        if self.invincible_frames > 0 and self.invincible_frames % 6 < 3:
            return  # Don't draw (creates flashing effect)
        
        red = (255, 0, 0)
        # Draw heart shape using polygon
        # Heart is centered at (self.x, self.y)
        scale = self.size / 8.0  # Scale based on size
        
        # Heart shape points (scaled)
        heart_points = [
            (self.x, self.y - 3 * scale),           # Top center
            (self.x - 4 * scale, self.y - 6 * scale),  # Left top curve
            (self.x - 7 * scale, self.y - 3 * scale),  # Left outer
            (self.x - 7 * scale, self.y + 1 * scale),  # Left middle
            (self.x, self.y + 8 * scale),           # Bottom point
            (self.x + 7 * scale, self.y + 1 * scale),  # Right middle
            (self.x + 7 * scale, self.y - 3 * scale),  # Right outer
            (self.x + 4 * scale, self.y - 6 * scale),  # Right top curve
        ]
        
        pygame.draw.polygon(surface, red, heart_points)
        # Add outline for better visibility
        pygame.draw.polygon(surface, (180, 0, 0), heart_points, 1)
    
    def get_rect(self):
        # Collision box for the heart (slightly smaller than visual)
        scale = self.size / 8.0
        return pygame.Rect(
            self.x - 6 * scale, 
            self.y - 5 * scale, 
            12 * scale, 
            13 * scale
        )


# ===== ATTACK PATTERNS =====

class SpinningBullets:
    """Bullets that spin around the center and move inward"""
    def __init__(self, center_x, center_y, radius, count, speed, inward_speed):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.count = count
        self.speed = speed
        self.inward_speed = inward_speed
        self.angle = 0
        self.size = 8
        self.active = True

    def update(self):
        self.angle += self.speed
        self.radius -= self.inward_speed
        if self.radius < 20:
            self.radius = 20

    def get_bullets(self):
        bullets = []
        for i in range(self.count):
            ang = self.angle + (2 * math.pi / self.count) * i
            x = self.center_x + math.cos(ang) * self.radius
            y = self.center_y + math.sin(ang) * self.radius
            bullets.append(pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size))
        return bullets

    def draw(self, surface):
        YELLOW = (255, 255, 0)
        for bullet in self.get_bullets():
            pygame.draw.circle(surface, YELLOW, (int(bullet.centerx), int(bullet.centery)), self.size)


class FallingBones:
    """Bones that fall from the top of the battle box"""
    def __init__(self, box: BattleBox):
        self.box = box
        self.bones = []
        self.spawn_timer = 0
        self.spawn_interval = 30  # Spawn every 0.5 seconds
        self.bone_width = 12
        self.bone_height = 40
        self.fall_speed = 3
        self.active = True

    def update(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            # Spawn a new bone at random x position
            x = random.randint(self.box.x + 10, self.box.x + self.box.w - self.bone_width - 10)
            bone = pygame.Rect(x, self.box.y - self.bone_height, self.bone_width, self.bone_height)
            self.bones.append(bone)
        
        # Move bones down
        for bone in self.bones[:]:
            bone.y += self.fall_speed
            # Remove bones that have left the box
            if bone.y > self.box.y + self.box.h:
                self.bones.remove(bone)

    def get_bullets(self):
        return self.bones

    def draw(self, surface):
        WHITE = (255, 255, 255)
        for bone in self.bones:
            pygame.draw.rect(surface, WHITE, bone)
            # Draw bone details
            pygame.draw.line(surface, (200, 200, 200), 
                           (bone.centerx, bone.top), 
                           (bone.centerx, bone.bottom), 2)


class ConvergingCircles:
    """Circles that move from edges toward the center"""
    def __init__(self, box: BattleBox):
        self.box = box
        self.circles = []
        self.spawn_timer = 0
        self.spawn_interval = 20
        self.size = 10
        self.speed = 2
        self.active = True

    def update(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            # Spawn from random edge
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            if edge == 'top':
                x = random.randint(self.box.x, self.box.x + self.box.w)
                y = self.box.y
            elif edge == 'bottom':
                x = random.randint(self.box.x, self.box.x + self.box.w)
                y = self.box.y + self.box.h
            elif edge == 'left':
                x = self.box.x
                y = random.randint(self.box.y, self.box.y + self.box.h)
            else:  # right
                x = self.box.x + self.box.w
                y = random.randint(self.box.y, self.box.y + self.box.h)
            
            # Calculate direction toward center
            center_x = self.box.center_x
            center_y = self.box.center_y
            dx = center_x - x
            dy = center_y - y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                dx = (dx / dist) * self.speed
                dy = (dy / dist) * self.speed
            
            self.circles.append({
                'rect': pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size),
                'dx': dx,
                'dy': dy
            })
        
        # Move circles
        for circle in self.circles[:]:
            circle['rect'].x += circle['dx']
            circle['rect'].y += circle['dy']
            # Remove if past center significantly
            if (abs(circle['rect'].centerx - self.box.center_x) > self.box.w or
                abs(circle['rect'].centery - self.box.center_y) > self.box.h):
                self.circles.remove(circle)

    def get_bullets(self):
        return [c['rect'] for c in self.circles]

    def draw(self, surface):
        CYAN = (0, 255, 255)
        for circle in self.circles:
            pygame.draw.circle(surface, CYAN, 
                             (int(circle['rect'].centerx), int(circle['rect'].centery)), 
                             self.size)


class GasterBlaster:
    """Gaster Blaster that charges and fires a beam"""
    def __init__(self, box: BattleBox):
        self.box = box
        self.blasters = []
        self.spawn_timer = 0
        self.spawn_interval = 90  # Spawn every 1.5 seconds
        self.active = True

    def update(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            # Spawn a new blaster
            self.spawn_blaster()
        
        # Update all blasters
        for blaster in self.blasters[:]:
            blaster['timer'] += 1
            
            # Charging phase (0-60 frames = 1 second)
            if blaster['timer'] < 60:
                blaster['charge'] = blaster['timer'] / 60.0
            # Firing phase (60-120 frames = 1 second)
            elif blaster['timer'] < 120:
                blaster['firing'] = True
            # Remove after firing
            else:
                self.blasters.remove(blaster)

    def spawn_blaster(self):
        """Spawn a new Gaster Blaster"""
        # Random position and direction
        side = random.choice(['left', 'right', 'top', 'bottom'])
        
        if side == 'left':
            x = self.box.x - 40
            y = random.randint(self.box.y + 20, self.box.y + self.box.h - 20)
            angle = 0  # Point right
            beam_width = self.box.w + 40
            beam_height = 30
        elif side == 'right':
            x = self.box.x + self.box.w + 40
            y = random.randint(self.box.y + 20, self.box.y + self.box.h - 20)
            angle = 180  # Point left
            beam_width = self.box.w + 40
            beam_height = 30
        elif side == 'top':
            x = random.randint(self.box.x + 20, self.box.x + self.box.w - 20)
            y = self.box.y - 40
            angle = 90  # Point down
            beam_width = 30
            beam_height = self.box.h + 40
        else:  # bottom
            x = random.randint(self.box.x + 20, self.box.x + self.box.w - 20)
            y = self.box.y + self.box.h + 40
            angle = 270  # Point up
            beam_width = 30
            beam_height = self.box.h + 40
        
        blaster = {
            'x': x,
            'y': y,
            'side': side,
            'angle': angle,
            'timer': 0,
            'charge': 0.0,
            'firing': False,
            'beam_width': beam_width,
            'beam_height': beam_height
        }
        self.blasters.append(blaster)

    def get_bullets(self):
        """Return collision rects for firing beams"""
        bullets = []
        for blaster in self.blasters:
            if blaster['firing']:
                # Create beam rect based on side
                if blaster['side'] == 'left':
                    beam_rect = pygame.Rect(
                        blaster['x'], 
                        blaster['y'] - blaster['beam_height']//2,
                        blaster['beam_width'], 
                        blaster['beam_height']
                    )
                elif blaster['side'] == 'right':
                    beam_rect = pygame.Rect(
                        blaster['x'] - blaster['beam_width'], 
                        blaster['y'] - blaster['beam_height']//2,
                        blaster['beam_width'], 
                        blaster['beam_height']
                    )
                elif blaster['side'] == 'top':
                    beam_rect = pygame.Rect(
                        blaster['x'] - blaster['beam_width']//2,
                        blaster['y'],
                        blaster['beam_width'], 
                        blaster['beam_height']
                    )
                else:  # bottom
                    beam_rect = pygame.Rect(
                        blaster['x'] - blaster['beam_width']//2,
                        blaster['y'] - blaster['beam_height'],
                        blaster['beam_width'], 
                        blaster['beam_height']
                    )
                bullets.append(beam_rect)
        return bullets

    def draw(self, surface):
        for blaster in self.blasters:
            # Draw charging indicator
            if not blaster['firing']:
                # Warning line showing where beam will fire
                alpha = int(blaster['charge'] * 255)
                color = (255, int(255 * (1 - blaster['charge'])), 0)  # Orange to red
                
                if blaster['side'] in ['left', 'right']:
                    # Horizontal warning line
                    pygame.draw.line(surface, color,
                                   (self.box.x, blaster['y']),
                                   (self.box.x + self.box.w, blaster['y']), 2)
                else:
                    # Vertical warning line
                    pygame.draw.line(surface, color,
                                   (blaster['x'], self.box.y),
                                   (blaster['x'], self.box.y + self.box.h), 2)
                
                # Draw blaster skull (simplified)
                skull_size = int(20 + blaster['charge'] * 10)
                skull_color = (200, 200, 200)
                
                # Skull head
                pygame.draw.circle(surface, skull_color, 
                                 (int(blaster['x']), int(blaster['y'])), skull_size)
                
                # Eye sockets (glowing)
                eye_color = (255, int(100 + blaster['charge'] * 155), 0)
                eye_offset = skull_size // 3
                pygame.draw.circle(surface, eye_color,
                                 (int(blaster['x'] - eye_offset), int(blaster['y'] - eye_offset//2)), 
                                 skull_size//4)
                pygame.draw.circle(surface, eye_color,
                                 (int(blaster['x'] + eye_offset), int(blaster['y'] - eye_offset//2)), 
                                 skull_size//4)
            
            # Draw firing beam
            if blaster['firing']:
                # Main beam (white core)
                beam_rects = self.get_bullets()
                for beam_rect in beam_rects:
                    # Outer glow (light blue)
                    glow_rect = beam_rect.inflate(10, 10)
                    pygame.draw.rect(surface, (100, 150, 255), glow_rect)
                    # Core beam (white)
                    pygame.draw.rect(surface, (255, 255, 255), beam_rect)
                
                # Draw blaster skull while firing
                skull_size = 30
                skull_color = (255, 255, 255)
                pygame.draw.circle(surface, skull_color, 
                                 (int(blaster['x']), int(blaster['y'])), skull_size)
                
                # Bright eyes while firing
                eye_color = (255, 0, 0)
                eye_offset = skull_size // 3
                pygame.draw.circle(surface, eye_color,
                                 (int(blaster['x'] - eye_offset), int(blaster['y'] - eye_offset//2)), 
                                 skull_size//3)
                pygame.draw.circle(surface, eye_color,
                                 (int(blaster['x'] + eye_offset), int(blaster['y'] - eye_offset//2)), 
                                 skull_size//3)


class AttackManager:
    """Manages switching between different attack patterns"""
    def __init__(self, box: BattleBox):
        self.box = box
        self.current_attack = None
        self.attack_timer = 0
        self.attack_duration = 300  # 5 seconds per attack
        self.switch_attack()

    def switch_attack(self):
        """Switch to a random attack pattern"""
        attack_type = random.choice(['spinning', 'bones', 'circles', 'blaster'])
        
        if attack_type == 'spinning':
            self.current_attack = SpinningBullets(
                self.box.center_x, self.box.center_y,
                radius=120, count=6, speed=0.05, inward_speed=0.3
            )
        elif attack_type == 'bones':
            self.current_attack = FallingBones(self.box)
        elif attack_type == 'circles':
            self.current_attack = ConvergingCircles(self.box)
        else:  # blaster
            self.current_attack = GasterBlaster(self.box)
        
        self.attack_timer = 0

    def update(self):
        self.attack_timer += 1
        if self.attack_timer >= self.attack_duration:
            self.switch_attack()
        
        if self.current_attack:
            self.current_attack.update()

    def check_collision(self, soul: Soul) -> bool:
        """Check if any bullet hit the soul"""
        if not self.current_attack:
            return False
        
        soul_rect = soul.get_rect()
        for bullet in self.current_attack.get_bullets():
            if soul_rect.colliderect(bullet):
                return True
        return False

    def draw(self, surface):
        if self.current_attack:
            self.current_attack.draw(surface)


def main():
    pygame.init()
    window = pygame.display.set_mode((480, 360))
    font = pygame.font.SysFont("consolas", 20)
    small_font = pygame.font.SysFont("consolas", 16)
    pygame.display.set_caption("Undertale - Battle System")

    box = BattleBox()
    soul = Soul(box.center_x, box.center_y)
    attack_manager = AttackManager(box)
    
    clock = pygame.time.Clock()
    game_over = False
 
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    # Restart game
                    soul = Soul(box.center_x, box.center_y)
                    attack_manager = AttackManager(box)
                    game_over = False

        if not game_over:
            soul.move(box)
            attack_manager.update()

            # Check collision
            if attack_manager.check_collision(soul):
                if soul.take_damage(1):
                    if soul.hp <= 0:
                        game_over = True

        # Drawing
        window.fill((0, 0, 0))  # black
        box.draw(window)
        
        if not game_over:
            attack_manager.draw(window)
            soul.draw(window)
        
        # HP Bar
        hp_text = font.render(f"HP:", True, (255, 255, 255))
        window.blit(hp_text, (20, window.get_height() - 40))
        
        # HP bar background
        pygame.draw.rect(window, (255, 0, 0), (70, window.get_height() - 35, 200, 20), 2)
        # HP bar fill
        hp_width = int((soul.hp / soul.max_hp) * 196)
        if hp_width > 0:
            pygame.draw.rect(window, (255, 255, 0), (72, window.get_height() - 33, hp_width, 16))
        
        # HP numbers
        hp_num = font.render(f"{soul.hp} / {soul.max_hp}", True, (255, 255, 255))
        window.blit(hp_num, (280, window.get_height() - 40))

        # Game Over screen
        if game_over:
            game_over_text = font.render("YOU DIED", True, (255, 0, 0))
            restart_text = small_font.render("Press R to Restart", True, (255, 255, 255))
            window.blit(game_over_text, (window.get_width()//2 - 60, window.get_height()//2 - 20))
            window.blit(restart_text, (window.get_width()//2 - 90, window.get_height()//2 + 20))

        pygame.display.update()


if __name__ == "__main__":
    main()
