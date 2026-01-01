import pygame
import sys
import math

pygame.init()

# -----------------------------
# Window setup
# -----------------------------
WIDTH, HEIGHT = 480, 360
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Undertale Battle Demo")

CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 20)

# -----------------------------
# Colors
# -----------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 150, 0)

# -----------------------------
# Battle box
# -----------------------------
BOX_X = 80
BOX_Y = 60
BOX_W = 320
BOX_H = 240

# -----------------------------
# Player soul
# -----------------------------
soul_x = BOX_X + BOX_W // 2
soul_y = BOX_Y + BOX_H // 2
soul_speed = 4
soul_size = 8

player_hp = 20


# -----------------------------
# Rotating Sun Attack
# -----------------------------
class SunAttack:
    def __init__(self, center_x, center_y, radius, count, speed, inward_speed):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.count = count
        self.speed = speed
        self.inward_speed = inward_speed
        self.angle = 0
        self.size = 12

    def update(self):
        self.angle += self.speed
        self.radius -= self.inward_speed
        if self.radius < 20:
            self.radius = 20

    def get_positions(self):
        positions = []
        for i in range(self.count):
            ang = self.angle + (2 * math.pi / self.count) * i
            x = self.center_x + math.cos(ang) * self.radius
            y = self.center_y + math.sin(ang) * self.radius
            positions.append((x, y))
        return positions


sun_attack = SunAttack(
    center_x=BOX_X + BOX_W // 2,
    center_y=BOX_Y + BOX_H // 2,
    radius=100,
    count=6,
    speed=0.05,
    inward_speed=0.1
)


# -----------------------------
# Sun Blaster Attack
# -----------------------------
class SunBlaster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.charge = 0
        self.max_charge = 60
        self.firing = False
        self.beam_time = 30
        self.beam_timer = 0

    def update(self):
        if not self.firing:
            self.charge += 1
            if self.charge >= self.max_charge:
                self.firing = True
                self.beam_timer = self.beam_time
        else:
            self.beam_timer -= 1
            if self.beam_timer <= 0:
                self.reset()

    def reset(self):
        self.charge = 0
        self.firing = False

    def draw(self, win):
        # Draw the blaster head
        pygame.draw.circle(win, ORANGE, (self.x, self.y), 20)

        # Charging glow
        if not self.firing:
            glow = int((self.charge / self.max_charge) * 20)
            pygame.draw.circle(win, YELLOW, (self.x, self.y), 20 + glow, 2)

        # Beam
        if self.firing:
            pygame.draw.rect(win, YELLOW, (self.x, BOX_Y, 10, BOX_H))


sun_blaster = SunBlaster(BOX_X + BOX_W // 2, BOX_Y + 30)


# -----------------------------
# Drawing
# -----------------------------
def draw_window():
    WIN.fill(BLACK)

    # Battle box
    pygame.draw.rect(WIN, WHITE, (BOX_X, BOX_Y, BOX_W, BOX_H), 3)

    # Soul
    pygame.draw.rect(WIN, RED, (soul_x, soul_y, soul_size, soul_size))

    # Rotating sun bullets
    for (sx, sy) in sun_attack.get_positions():
        pygame.draw.circle(WIN, YELLOW, (int(sx), int(sy)), sun_attack.size)

    # Sun Blaster
    sun_blaster.draw(WIN)

    # HP
    hp_text = FONT.render(f"HP: {player_hp}", True, WHITE)
    WIN.blit(hp_text, (20, HEIGHT - 40))

    pygame.display.update()


# -----------------------------
# Movement
# -----------------------------
def handle_movement(keys):
    global soul_x, soul_y

    if keys[pygame.K_LEFT] and soul_x > BOX_X + 3:
        soul_x -= soul_speed
    if keys[pygame.K_RIGHT] and soul_x < BOX_X + BOX_W - soul_size - 3:
        soul_x += soul_speed
    if keys[pygame.K_UP] and soul_y > BOX_Y + 3:
        soul_y -= soul_speed
    if keys[pygame.K_DOWN] and soul_y < BOX_Y + BOX_H - soul_size - 3:
        soul_y += soul_speed


# -----------------------------
# Collision
# -----------------------------
def check_collisions():
    global player_hp

    soul_rect = pygame.Rect(soul_x, soul_y, soul_size, soul_size)

    # Sun bullets
    for (sx, sy) in sun_attack.get_positions():
        sun_rect = pygame.Rect(
            sx - sun_attack.size,
            sy - sun_attack.size,
            sun_attack.size * 2,
            sun_attack.size * 2
        )
        if soul_rect.colliderect(sun_rect):
            player_hp -= 1

    # Sun Blaster beam
    if sun_blaster.firing:
        beam_rect = pygame.Rect(sun_blaster.x, BOX_Y, 10, BOX_H)
        if soul_rect.colliderect(beam_rect):
            player_hp -= 2


# -----------------------------
# Main Loop
# -----------------------------
def main():
    global player_hp

    while True:
        CLOCK.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        handle_movement(keys)

        sun_attack.update()
        sun_blaster.update()
        check_collisions()

        draw_window()

        if player_hp <= 0:
            print("You Died.")
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()
