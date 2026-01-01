import pygame
import random
import math

pygame.init()

# Screen
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Watermelon Game (Lite)")

clock = pygame.time.Clock()

# Fruit sizes (like Suika Game)
FRUIT_SIZES = [20, 28, 36, 48, 60, 75]  # small → big
FRUIT_COLORS = [
    (255, 100, 100),
    (255, 150, 80),
    (255, 220, 80),
    (150, 255, 80),
    (80, 200, 255),
    (255, 80, 255)
]

gravity = 0.3

class Fruit:
    def __init__(self, x, size_index):
        self.x = x
        self.y = 50
        self.size_index = size_index
        self.radius = FRUIT_SIZES[size_index]
        self.color = FRUIT_COLORS[size_index]
        self.vy = 0
        self.landed = False

    def update(self, fruits):
        if not self.landed:
            self.vy += gravity
            self.y += self.vy

        # Floor collision
        if self.y + self.radius > HEIGHT - 10:
            self.y = HEIGHT - 10 - self.radius
            self.vy = 0
            self.landed = True

        # Collision with other fruits
        for f in fruits:
            if f is self:
                continue
            dx = self.x - f.x
            dy = self.y - f.y
            dist = math.hypot(dx, dy)
            min_dist = self.radius + f.radius

            if dist < min_dist:
                overlap = min_dist - dist
                angle = math.atan2(dy, dx)

                # Push fruits apart
                self.x += math.cos(angle) * overlap / 2
                self.y += math.sin(angle) * overlap / 2
                f.x -= math.cos(angle) * overlap / 2
                f.y -= math.sin(angle) * overlap / 2

                # If same size → merge
                if self.size_index == f.size_index and not self.landed and not f.landed:
                    if self.size_index < len(FRUIT_SIZES) - 1:
                        new_size = self.size_index + 1
                        fruits.append(Fruit(self.x, new_size))
                    fruits.remove(self)
                    fruits.remove(f)
                    return

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


fruits = []
current_fruit = Fruit(WIDTH // 2, 0)
score = 0

running = True
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Drop fruit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                fruits.append(current_fruit)
                current_fruit = Fruit(WIDTH // 2, random.randint(0, 2))

    # Move fruit left/right
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        current_fruit.x -= 4
    if keys[pygame.K_RIGHT]:
        current_fruit.x += 4

    # Clamp inside screen
    current_fruit.x = max(current_fruit.radius, min(WIDTH - current_fruit.radius, current_fruit.x))

    # Update fruits
    for f in fruits[:]:
        f.update(fruits)

    # Draw fruits
    for f in fruits:
        f.draw()

    # Draw current fruit
    current_fruit.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
