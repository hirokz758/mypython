import tkinter as tk
import random

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
cannon_exist = True

enemies = []
my_bullets = []
enemy_bullets = []

# ===== 自機まわり =====
def create_cannon(x, y):
    global cannon_x, cannon_y, cannon_id, cannon_exist
    cannon_x = x
    cannon_y = y
    cannon_id = cv.create_polygon(
        cannon_x, cannon_y - 20,
        cannon_x + 15, cannon_y,
        cannon_x - 15, cannon_y,
        fill="blue", outline="black", tags="cannon"
    )
    cannon_exist = True
    cv.tag_bind("cannon", "<ButtonPress-3>", cannon_pressed)
    cv.tag_bind("cannon", "<Button1-Motion>", cannon_dragged)

def cannon_pressed(event):
    if not cannon_exist:
        return
    create_my_bullet(event.x, CANNON_Y)

def cannon_dragged(event):
    global cannon_x
    if not cannon_exist:
        return
    coords = cv.coords(cannon_id)
    dx = event.x - coords[0]
    cannon_x += dx
    cv.coords(
        cannon_id,
        cannon_x, cannon_y - 20,
        cannon_x + 15, cannon_y,
        cannon_x - 15, cannon_y
    )

def destroy_cannon():
    global cannon_id
    if cannon_id is not None:
        cv.delete(cannon_id)
        cannon_id = None

# ===== キーボード操作の追加 =====
def move_cannon(dx):
    global cannon_x
    if not cannon_exist:
        return
    cannon_x += dx
    cannon_x = max(15, min(WINDOW_WIDTH - 15, cannon_x))
    cv.coords(
        cannon_id,
        cannon_x, cannon_y - 20,
        cannon_x + 15, cannon_y,
        cannon_x - 15, cannon_y
    )

def on_key_press(event):
    if event.keysym == "Left":
        move_cannon(-15)
    elif event.keysym == "Right":
        move_cannon(15)
    elif event.keysym == "space":
        if cannon_exist:
            create_my_bullet(cannon_x, CANNON_Y)

# ===== 自分の弾まわり =====
def create_my_bullet(x, y):
    bullet_id = cv.create_rectangle(
        x - BULLET_WIDTH, y + BULLET_HEIGHT,
        x + BULLET_WIDTH, y - BULLET_HEIGHT,
        fill="blue"
    )
    bullet = {
        "x": x,
        "y": y,
        "id": bullet_id,
        "alive": True
    }
    my_bullets.append(bullet)
    index = len(my_bullets) - 1
    shoot_my_bullet(index)

def shoot_my_bullet(index):
    bullet = my_bullets[index]
    if not bullet["alive"]:
        return
    if bullet["y"] >= 0:
        cv.move(bullet["id"], 0, -BULLET_HEIGHT)
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
                cv.delete(enemy["id"])
                cv.create_text(
                    enemy["x"], enemy["y"],
                    text="wow!", fill="cyan",
                    font=("System", TEXT_GOOD_SIZE),
                    tag="good"
                )
                destroy_my_bullet(index)
                break

def destroy_my_bullet(index):
    bullet = my_bullets[index]
    if bullet["alive"]:
        bullet["alive"] = False
        cv.delete(bullet["id"])

# ===== 敵まわり =====
def create_enemies():
    for i in range(NUMBER_OF_ENEMY):
        x = i * ENEMY_SPACE_X + 50
        y = ENEMY_SPACE_Y
        enemy = {
            "x": x % WINDOW_WIDTH,
            "y": y + x // WINDOW_WIDTH * ENEMY_SPACE_Y,
            "id": None,
            "exist": True
        }
        enemy["id"] = cv.create_rectangle(
            enemy["x"] - 15, enemy["y"] + 20,
            enemy["x"] + 15, enemy["y"] - 20,
            fill="yellow", outline="yellow", tags="enemy"
        )
        enemies.append(enemy)
    for idx in range(len(enemies)):
        move_enemy(idx)

def move_enemy(index):
    enemy = enemies[index]
    if not enemy["exist"]:
        return
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
    enemy["x"] = x
    enemy["y"] = y
    cv.coords(
        enemy["id"],
        enemy["x"] - 15, enemy["y"] + 20,
        enemy["x"] + 15, enemy["y"] - 20
    )
    root.after(ENEMY_MOVE_SPEED, lambda i=index: move_enemy(i))

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
        fill="red"
    )
    bullet = {
        "x": x,
        "y": y,
        "id": bullet_id,
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
        cv.move(bullet["id"], 0, BULLET_HEIGHT)
        bullet["y"] += BULLET_HEIGHT
        collision_enemy_bullet(index)
        root.after(BULLET_SPEED, lambda i=index: shoot_enemy_bullet(i))
    else:
        destroy_enemy_bullet(index)

def collision_enemy_bullet(index):
    global cannon_exist
    if not cannon_exist or cannon_id is None:
        return
    bullet = enemy_bullets[index]
    if not bullet["alive"]:
        return
    cannon_coords = cv.coords(cannon_id)
    bullet_coords = cv.coords(bullet["id"])
    if check_collision_rect(bullet_coords, cannon_coords):
        gameover()

def destroy_enemy_bullet(index):
    bullet = enemy_bullets[index]
    if bullet["alive"]:
        bullet["alive"] = False
        cv.delete(bullet["id"])

# ===== 共通: 四角どうしの当たり判定 =====
def check_collision_rect(a, b):
    return (b[0] < a[0] < b[2] and b[1] < a[1] < b[3])

# ===== GAME CLEAR / GAME OVER =====
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
    root.title("invader (keyboard version)")
    cv = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="yellowgreen")
    cv.pack()

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
