import turtle
import random
import time
import os

# ----- Config -----
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 20
DELAY = 0.3  # falling speed (seconds) - smaller is faster
HIGHSCORE_FILE = "highscore.txt"

# ----- Shapes (Tetriminoes) -----
# Each shape is a list of rotations; each rotation is a list of (x, y) offsets
SHAPES = {
    'I': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
    ],
    'O': [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    'T': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'L': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    'J': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
    'S': [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
    ],
    'Z': [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
    ]
}

COLORS = {
    'I': 'cyan',
    'O': 'yellow',
    'T': 'purple',
    'L': 'orange',
    'J': 'blue',
    'S': 'green',
    'Z': 'red'
}

# ----- Screen setup -----
screen = turtle.Screen()
screen.title("Tetris - Turtle Version")
screen.bgcolor("#2b2b2b")  # Dark Slate Gray
screen.setup(width=400, height=500)
screen.tracer(0)

# Draw turtle for blocks
drawer = turtle.Turtle()
drawer.hideturtle()
drawer.penup()
drawer.speed(0)

# For drawing static background (field border)
bg_turtle = turtle.Turtle()
bg_turtle.hideturtle()
bg_turtle.penup()
bg_turtle.speed(0)

# For drawing text (score, game over, etc.)
text_turtle = turtle.Turtle()
text_turtle.hideturtle()
text_turtle.penup()
text_turtle.color("white")

# ----- Game state -----
# grid[y][x] = color or None
grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

current_shape = None
next_shape = None
hold_shape = None
can_hold = True
current_rotation = 0
current_x = 3  # start near the middle
current_y = GRID_HEIGHT - 1  # top of the grid
score = 0
level = 1
game_over = False
last_drop_time = 0
high_score = 0
is_paused = False
combo_count = -1
drop_in_progress = False


# ----- Helper functions -----

def load_high_score():
    """Load high score from file."""
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_high_score():
    """Save high score to file."""
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(high_score))
    except:
        pass

high_score = load_high_score()


def get_delay():
    """Calculate delay based on level."""
    return max(0.05, 0.3 - (level - 1) * 0.02)


def get_ghost_y():
    """Calculate the y-position where the current piece would land."""
    if current_shape is None:
        return current_y
    ghost_y = current_y
    while shape_fits(current_shape, current_rotation, current_x, ghost_y - 1):
        ghost_y -= 1
    return ghost_y


def hold_piece():
    """Hold the current piece."""
    global current_shape, hold_shape, next_shape, current_x, current_y, current_rotation, can_hold
    
    if game_over or is_paused or not can_hold:
        return

    if hold_shape is None:
        hold_shape = current_shape
        spawn_new_shape()
    else:
        current_shape, hold_shape = hold_shape, current_shape
        current_x = 3
        current_y = GRID_HEIGHT - 4
        current_rotation = 0
    
    can_hold = False
    draw_grid()


def hard_drop():
    """Instantly drop the current shape to the bottom."""
    global current_y, score, last_drop_time, drop_in_progress
    
    if drop_in_progress:
        return

    current_time = time.time()
    # if game_over or is_paused or current_shape is None or (current_time - last_drop_time < 0.1):
    if drop_in_progress or game_over or is_paused or current_shape is None or (current_time - last_drop_time < 0.1):
        return
        
    drop_in_progress = True
    
    # Check if we can move down at all?
    # Actually, hard drop should lock even if it can't move down (standard rules).
    # But for "safety" against accidental double taps on new pieces:
    # If the piece hasn't dropped due to gravity yet, maybe we shouldn't hard drop?
    # No, speedrunners do that.
    
    while shape_fits(current_shape, current_rotation, current_x, current_y - 1):
        current_y -= 1
        score += 2  # Bonus for hard drop
    
    draw_grid()
    place_shape()
    spawn_new_shape()
    # spawn_new_shape updates last_drop_time too, resetting the cooldown window.
    draw_grid()
    
    # CRITICAL FIX: Update last_drop_time AFTER the drawing is done.
    # Turtle drawing can take time. If we rely on the time set in spawn_new_shape(),
    # the drawing time might eat up the cooldown window.
    last_drop_time = time.time()
    drop_in_progress = False

def draw_layout():
    """Draw the static game board layout."""
    bg_turtle.clear()
    
    # Draw main grid background (Black)
    # Grid dims: GRID_WIDTH * CELL_SIZE x GRID_HEIGHT * CELL_SIZE
    # Centered at (0, 0)
    w = GRID_WIDTH * CELL_SIZE
    h = GRID_HEIGHT * CELL_SIZE
    
    left_x = -w / 2
    bottom_y = -h / 2
    
    bg_turtle.goto(left_x, bottom_y)
    bg_turtle.color("white", "black")  # White border, Black fill
    bg_turtle.begin_fill()
    for _ in range(2):
        bg_turtle.pendown()
        bg_turtle.forward(w)
        bg_turtle.left(90)
        bg_turtle.forward(h)
        bg_turtle.left(90)
    bg_turtle.end_fill()
    bg_turtle.penup()

def draw_cell(x, y, color):
    """Draw a single square cell at grid position (x, y)."""
    screen_x = -GRID_WIDTH * CELL_SIZE / 2 + x * CELL_SIZE
    screen_y = -GRID_HEIGHT * CELL_SIZE / 2 + y * CELL_SIZE
    drawer.goto(screen_x, screen_y)
    drawer.color("gray", color)
    drawer.begin_fill()
    for _ in range(4):
        drawer.pendown()
        drawer.forward(CELL_SIZE)
        drawer.left(90)
    drawer.end_fill()
    drawer.penup()


def draw_grid():
    """Draw the entire grid: placed blocks + current falling piece."""
    drawer.clear()

    # Draw placed blocks
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] is not None:
                draw_cell(x, y, grid[y][x])

    # Draw current shape
    if current_shape is not None:
        shape_cells = SHAPES[current_shape][current_rotation]
        for (cx, cy) in shape_cells:
            gx = current_x + cx
            gy = current_y + cy
    # Draw Ghost Piece
    if current_shape is not None:
        ghost_y = get_ghost_y()
        shape_cells = SHAPES[current_shape][current_rotation]
        for (cx, cy) in shape_cells:
            gx = current_x + cx
            gy = ghost_y + cy
            if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                # Draw outline for ghost
                screen_x = -GRID_WIDTH * CELL_SIZE / 2 + gx * CELL_SIZE
                screen_y = -GRID_HEIGHT * CELL_SIZE / 2 + gy * CELL_SIZE
                drawer.goto(screen_x, screen_y)
                drawer.color("gray", "black") # gray outline, black fill
                drawer.begin_fill()
                for _ in range(4):
                    drawer.pendown()
                    drawer.forward(CELL_SIZE)
                    drawer.left(90)
                drawer.end_fill()
                drawer.penup()

    # Draw current shape
    if current_shape is not None:
        shape_cells = SHAPES[current_shape][current_rotation]
        for (cx, cy) in shape_cells:
            gx = current_x + cx
            gy = current_y + cy
            if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                draw_cell(gx, gy, COLORS[current_shape])

    # Draw score and level
    text_turtle.clear()
    text_turtle.goto(-180, 210)
    text_turtle.write(f"Score:\n{score}", font=("Arial", 12, "bold"))
    
    text_turtle.goto(-180, 160)
    text_turtle.write(f"High Score:\n{high_score}", font=("Arial", 12, "bold"))

    text_turtle.goto(-180, 110)
    text_turtle.write(f"Level: {level}", font=("Arial", 12, "normal"))

    # Draw Next Piece
    text_turtle.goto(110, 150)
    text_turtle.write("Next:", font=("Arial", 12, "normal"))
    
    if next_shape is not None:
        preview_x = 120
        preview_y = 120
        shape_cells = SHAPES[next_shape][0]
        for (cx, cy) in shape_cells:
            screen_x = preview_x + cx * CELL_SIZE
            screen_y = preview_y + cy * CELL_SIZE
            
            drawer.goto(screen_x, screen_y)
            drawer.color("gray", COLORS[next_shape])
            drawer.begin_fill()
            for _ in range(4):
                drawer.pendown()
                drawer.forward(CELL_SIZE)
                drawer.left(90)
            drawer.end_fill()
            drawer.penup()

    # Draw Hold Piece
    text_turtle.goto(-180, 150)
    text_turtle.write("Hold:", font=("Arial", 12, "normal"))
    
    if hold_shape is not None:
        hold_x = -170
        hold_y = 120
        shape_cells = SHAPES[hold_shape][0]
        for (cx, cy) in shape_cells:
            screen_x = hold_x + cx * CELL_SIZE
            screen_y = hold_y + cy * CELL_SIZE
            
            drawer.goto(screen_x, screen_y)
            drawer.color("gray", COLORS[hold_shape])
            drawer.begin_fill()
            for _ in range(4):
                drawer.pendown()
                drawer.forward(CELL_SIZE)
                drawer.left(90)
            drawer.end_fill()
            drawer.penup()

    # Draw Controls Instructions
    text_turtle.goto(-190, -150)
    text_turtle.write("Controls:", font=("Arial", 12, "bold"))
    text_turtle.goto(-190, -170)
    text_turtle.write("← → : Move", font=("Arial", 10, "normal"))
    text_turtle.goto(-190, -190)
    text_turtle.write("↑ : Rotate", font=("Arial", 10, "normal"))
    text_turtle.goto(-190, -210)
    text_turtle.write("↓ : Soft Drop", font=("Arial", 10, "normal"))
    text_turtle.goto(-190, -230)
    text_turtle.write("Space : Hard Drop", font=("Arial", 10, "normal"))
    text_turtle.goto(-190, -250)
    text_turtle.write("C : Hold Piece", font=("Arial", 10, "normal"))
    text_turtle.goto(-190, -270)
    text_turtle.write("P : Pause", font=("Arial", 10, "normal"))
    text_turtle.goto(-190, -290)
    text_turtle.write("R : Restart", font=("Arial", 10, "normal"))

    if is_paused:
        text_turtle.goto(-70, 0)
        text_turtle.write("PAUSED", font=("Arial", 30, "bold"))

    screen.update()


def shape_fits(shape, rotation, x, y):
    """Check if a shape at (x, y) with given rotation fits in grid (no collisions)."""
    for (cx, cy) in SHAPES[shape][rotation]:
        gx = x + cx
        gy = y + cy
        if gx < 0 or gx >= GRID_WIDTH or gy < 0 or gy >= GRID_HEIGHT:
            return False
        if grid[gy][gx] is not None:
            return False
    return True


def place_shape():
    """Lock the current shape into the grid and check for line clears."""
    global grid, score, high_score, combo_count

    for (cx, cy) in SHAPES[current_shape][current_rotation]:
        gx = current_x + cx
        gy = current_y + cy
        if 0 <= gy < GRID_HEIGHT and 0 <= gx < GRID_WIDTH:
            grid[gy][gx] = COLORS[current_shape]

    # Clear full lines
    full_lines = []
    for y in range(GRID_HEIGHT):
        if all(grid[y][x] is not None for x in range(GRID_WIDTH)):
            full_lines.append(y)
    
    if full_lines:
        # Flash effect
        for _ in range(3): # Flash 3 times
            # Turn white
            for y in full_lines:
                for x in range(GRID_WIDTH):
                    draw_cell(x, y, "white")
            screen.update()
            time.sleep(0.05)
            
            # Turn back (or black/invisible for blink effect)
            for y in full_lines:
                for x in range(GRID_WIDTH):
                    draw_cell(x, y, grid[y][x]) # Draw original color
            screen.update()
            time.sleep(0.05)
            
        # Draw all lines black before removing (cleanup)
        for y in full_lines:
             for x in range(GRID_WIDTH):
                    draw_cell(x, y, "black")
        screen.update()


    new_grid = []
    lines_cleared = 0
    for y in range(GRID_HEIGHT):
        if y not in full_lines:
             new_grid.append(grid[y])
        else:
            lines_cleared += 1

    # Add empty rows at the top
    while len(new_grid) < GRID_HEIGHT:
        new_grid.append([None for _ in range(GRID_WIDTH)])

    grid = new_grid
    
    
    if lines_cleared > 0:
        combo_count += 1
        score += lines_cleared * 100 + (combo_count * 50)
    else:
        combo_count = -1

    if score > high_score:
        high_score = score
    
    # helper for update level
    global level
    level = 1 + score // 500


def spawn_new_shape():
    """Spawn a new random shape at the top."""
    global current_shape, current_rotation, current_x, current_y, next_shape, game_over, last_drop_time, can_hold
    
    if next_shape is None:
        next_shape = random.choice(list(SHAPES.keys()))
        
    current_shape = next_shape
    next_shape = random.choice(list(SHAPES.keys()))
    
    current_rotation = 0
    current_x = 3
    current_y = GRID_HEIGHT - 4  # a bit below top to fit tall pieces
    
    # Prevent immediate hard drop of the new piece
    last_drop_time = time.time()

    if not shape_fits(current_shape, current_rotation, current_x, current_y):
        game_over = True
        save_high_score()
        
    global can_hold
    can_hold = True


def move(dx, dy):
    """Try to move current shape by (dx, dy)."""
    global current_x, current_y
    if game_over or is_paused or current_shape is None:
        return
    new_x = current_x + dx
    new_y = current_y + dy
    if shape_fits(current_shape, current_rotation, new_x, new_y):
        current_x = new_x
        current_y = new_y
        draw_grid()


def rotate():
    """Rotate current shape clockwise."""
    global current_rotation, current_x, current_y
    if game_over or is_paused or current_shape is None:
        return
    new_rotation = (current_rotation + 1) % len(SHAPES[current_shape])
    if shape_fits(current_shape, new_rotation, current_x, current_y):
        current_rotation = new_rotation
        draw_grid()
    else:
        # Wall Kicks
        for dx, dy in [(1, 0), (-1, 0), (0, 1)]:
             if shape_fits(current_shape, new_rotation, current_x + dx, current_y + dy):
                 current_x += dx
                 current_y += dy
                 current_rotation = new_rotation
                 draw_grid()
                 return


# ----- Input controls -----

def move_left():
    move(-1, 0)


def move_right():
    move(1, 0)


def move_down():
    move(0, -1)


def rotate_shape():
    rotate()


def toggle_pause():
    global is_paused
    if game_over:
        return
    is_paused = not is_paused
    draw_grid()
    if not is_paused:
        game_loop()


screen.listen()
screen.onkey(move_left, "Left")
screen.onkey(move_right, "Right")
screen.onkey(move_down, "Down")
screen.onkey(rotate_shape, "Up")
screen.onkey(hard_drop, "space")
screen.onkey(hold_piece, "c")
screen.onkey(toggle_pause, "p")
screen.onkey(toggle_pause, "P")


def reset_game():
    """Reset the game state to start over."""
    global grid, score, level, game_over, current_shape, next_shape, hold_shape, can_hold, high_score, is_paused, combo_count, drop_in_progress
    
    save_high_score() # save previous game score
    high_score = load_high_score()
    
    grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    score = 0
    combo_count = -1
    level = 1
    game_over = False
    is_paused = False
    drop_in_progress = False
    current_shape = None
    next_shape = None
    hold_shape = None
    can_hold = True
    
    spawn_new_shape()
    draw_grid()
    game_loop()

screen.onkey(reset_game, "r")


# ----- Game loop -----
def game_loop():
    global current_y, game_over
    
    if is_paused:
        return

    if game_over:
        text_turtle.goto(-80, 0)
        text_turtle.write("GAME OVER", font=("Arial", 24, "bold"))
        text_turtle.goto(-100, -30)
        text_turtle.write("Press 'r' to restart", font=("Arial", 14, "normal"))
        save_high_score()
        screen.update()
        return

    if current_shape is None:
        spawn_new_shape()

    # Try to move down
    if shape_fits(current_shape, current_rotation, current_x, current_y - 1):
        current_y -= 1
    else:
        # Lock shape and spawn new one
        place_shape()
        spawn_new_shape()

    draw_grid()
    screen.ontimer(game_loop, int(get_delay() * 1000))


# Start the game
spawn_new_shape()
draw_layout()
draw_grid()
game_loop()

turtle.done()

