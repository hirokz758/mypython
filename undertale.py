import pygame
import sys
import math


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
    def __init__(self, x: int, y: int, size: int=4, speed: int=8, hp: int=20):
        self.x: int = x
        self.y: int = y
        self.size: int = size
        self.speed: int = speed
        self.hp: int = hp

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

    def draw(self, surface):
        red = (255, 0, 0)
        pygame.draw.rect(surface, red, (self.x, self.y, self.size, self.size))


"""
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
"""

"""
def check_collision_hit(soul_x, soul_y, soul_size) -> bool:
    soul_rect = pygame.Rect(soul_x, soul_y, soul_size, soul_size)
    for (sx, sy) in sun_attack.get_positions():
        sun_rect = pygame.Rect(
            sx - sun_attack.size,
            sy - sun_attack.size,
            sun_attack.size * 2,
            sun_attack.size * 2
        )
        if soul_rect.colliderect(sun_rect):
            return True
    return False
"""


def main():
    pygame.init()
    window = pygame.display.set_mode((480, 360))
    font = pygame.font.SysFont("consolas", 20)
    pygame.display.set_caption("Undertale - Simple Battle")

    box = BattleBox()
    soul = Soul(box.center_x, box.center_y)
 
    while True:
        pygame.time.Clock().tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        soul.move(box)
        # sun_attack.update()

        #if check_collision_hit(soul.x, soul.y, soul.size):
        #    soul.hp -= 1
        #    if soul.hp <= 0:
        #        print("You Died.")
        #        pygame.quit()
        #        sys.exit()

        window.fill((0, 0, 0))  # black
        box.draw(window)
        soul.draw(window)
        hp_text = font.render(f"HP: {soul.hp}", True, (255, 255, 255))
        window.blit(hp_text, (20, window.get_height() - 40))

        #for (sx, sy) in sun_attack.get_positions():
        #    pygame.draw.circle(window, YELLOW, (int(sx), int(sy)), sun_attack.size)

        pygame.display.update()


if __name__ == "__main__":
    main()
