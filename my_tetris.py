import turtle
import random
import time

# ----- Config -----
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 20
DELAY = 0.3  # falling speed (seconds) - smaller is faster

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
screen.bgcolor("black")
screen.setup(width=400, height=500)
screen.tracer(0)

# Draw turtle for blocks
drawer = turtle.Turtle()
drawer.hideturtle()
drawer.penup()
drawer.speed(0)

# For drawing text (score, game over, etc.)
text_turtle = turtle.Turtle()
text_turtle.hideturtle()
text_turtle.penup()
text_turtle.color("white")

# ----- Game state -----
# grid[y][x] = color or None
grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

current_shape = None
current_rotation = 0
current_x = 3  # start near the middle
current_y = GRID_HEIGHT - 1  # top of the grid
score = 0
game_over = False


# ----- Helper functions -----

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
            if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                draw_cell(gx, gy, COLORS[current_shape])

    # Draw score
    text_turtle.clear()
    text_turtle.goto(-180, 200)
    text_turtle.write(f"Score: {score}", font=("Arial", 14, "normal"))

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
    global grid, score

    for (cx, cy) in SHAPES[current_shape][current_rotation]:
        gx = current_x + cx
        gy = current_y + cy
        if 0 <= gy < GRID_HEIGHT and 0 <= gx < GRID_WIDTH:
            grid[gy][gx] = COLORS[current_shape]

    # Clear full lines
    new_grid = []
    lines_cleared = 0
    for y in range(GRID_HEIGHT):
        if all(grid[y][x] is not None for x in range(GRID_WIDTH)):
            lines_cleared += 1
        else:
            new_grid.append(grid[y])

    # Add empty rows at the top
    while len(new_grid) < GRID_HEIGHT:
        new_grid.append([None for _ in range(GRID_WIDTH)])

    grid = new_grid
    score += lines_cleared * 100


def spawn_new_shape():
    """Spawn a new random shape at the top."""
    global current_shape, current_rotation, current_x, current_y, game_over
    current_shape = random.choice(list(SHAPES.keys()))
    current_rotation = 0
    current_x = 3
    current_y = GRID_HEIGHT - 4  # a bit below top to fit tall pieces

    if not shape_fits(current_shape, current_rotation, current_x, current_y):
        game_over = True


def move(dx, dy):
    """Try to move current shape by (dx, dy)."""
    global current_x, current_y
    if game_over or current_shape is None:
        return
    new_x = current_x + dx
    new_y = current_y + dy
    if shape_fits(current_shape, current_rotation, new_x, new_y):
        current_x = new_x
        current_y = new_y
        draw_grid()


def rotate():
    """Rotate current shape clockwise."""
    global current_rotation
    if game_over or current_shape is None:
        return
    new_rotation = (current_rotation + 1) % len(SHAPES[current_shape])
    if shape_fits(current_shape, new_rotation, current_x, current_y):
        current_rotation = new_rotation
        draw_grid()


# ----- Input controls -----

def move_left():
    move(-1, 0)


def move_right():
    move(1, 0)


def move_down():
    move(0, -1)


def rotate_shape():
    rotate()


screen.listen()
screen.onkey(move_left, "Left")
screen.onkey(move_right, "Right")
screen.onkey(move_down, "Down")
screen.onkey(rotate_shape, "Up")


# ----- Game loop -----
def game_loop():
    global current_y, game_over

    if game_over:
        text_turtle.goto(-80, 0)
        text_turtle.write("GAME OVER", font=("Arial", 24, "bold"))
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
    screen.ontimer(game_loop, int(DELAY * 1000))


# Start the game
spawn_new_shape()
draw_grid()
game_loop()

turtle.done()

