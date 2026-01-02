import pygame
import sys

# 初期設定
pygame.init()
WIDTH, HEIGHT = 600, 500
BOX_RECT = pygame.Rect(200, 150, 200, 200) # 戦闘枠
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# 色
BLACK, WHITE, RED, BLUE, CYAN = (0,0,0), (255,255,255), (255,0,0), (0,0,255), (0,255,255)

class Heart:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2, HEIGHT//2, 16, 16)
        self.mode = "RED" # RED または BLUE
        self.vy = 0       # 垂直方向の速度（重力用）
        self.on_ground = False

    def update(self):
        keys = pygame.key.get_pressed()
        speed = 4

        if self.mode == "RED":
            # 赤いソウル：自由移動
            if keys[pygame.K_LEFT] and self.rect.left > BOX_RECT.left: self.rect.x -= speed
            if keys[pygame.K_RIGHT] and self.rect.right < BOX_RECT.right: self.rect.x += speed
            if keys[pygame.K_UP] and self.rect.top > BOX_RECT.top: self.rect.y -= speed
            if keys[pygame.K_DOWN] and self.rect.bottom < BOX_RECT.bottom: self.rect.y += speed
        
        else: # 青いソウル：重力
            # 左右移動
            if keys[pygame.K_LEFT] and self.rect.left > BOX_RECT.left: self.rect.x -= speed
            if keys[pygame.K_RIGHT] and self.rect.right < BOX_RECT.right: self.rect.x += speed
            
            # ジャンプ（上キー）
            if keys[pygame.K_UP] and self.on_ground:
                self.vy = -8
                self.on_ground = False
            
            # 重力計算
            self.vy += 0.5 # 常に下に引っ張る力
            self.rect.y += self.vy
            
            # 床との当たり判定
            if self.rect.bottom >= BOX_RECT.bottom:
                self.rect.bottom = BOX_RECT.bottom
                self.vy = 0
                self.on_ground = True

    def draw(self):
        color = RED if self.mode == "RED" else BLUE
        pygame.draw.rect(screen, color, self.rect)

class Blaster:
    def __init__(self, target_x):
        self.x = target_x - 20 # ターゲットの真上
        self.timer = 0
        self.active = True

    def update(self):
        self.timer += 1
        if self.timer > 60: # 1秒（60フレーム）経ったら消える
            self.active = False

    def draw(self):
        if self.timer < 30:
            # 溜め：細い線（予兆）
            pygame.draw.line(screen, WHITE, (self.x + 20, BOX_RECT.top), (self.x + 20, BOX_RECT.bottom), 1)
        else:
            # 発射：太いビーム
            beam_rect = pygame.Rect(self.x, BOX_RECT.top, 40, BOX_RECT.height)
            pygame.draw.rect(screen, CYAN, beam_rect)
            return beam_rect
        return None

# メインループ
heart = Heart()
blasters = []

while True:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g: # Gキーでモード切替
                heart.mode = "BLUE" if heart.mode == "RED" else "RED"
                heart.vy = 0
            if event.key == pygame.K_SPACE: # スペースでブラスター！
                blasters.append(Blaster(heart.rect.centerx))

    # 1. 枠の描画
    pygame.draw.rect(screen, WHITE, BOX_RECT, 2)

    # 2. ハートの更新
    heart.update()
    heart.draw()

    # 3. ブラスターの更新
    for b in blasters[:]:
        beam_hitbox = b.draw()
        b.update()
        if beam_hitbox and heart.rect.colliderect(beam_hitbox):
            print("ダメージ！")
        if not b.active:
            blasters.remove(b)

    pygame.display.flip()
    clock.tick(60)
