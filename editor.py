import pygame
import json
import os

# --- Config ---
TILE_SIZE = 16
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PALETTE_HEIGHT = TILE_SIZE + 4
INSTRUCTION_HEIGHT = 20
BOTTOM_BAR_HEIGHT = PALETTE_HEIGHT + INSTRUCTION_HEIGHT
FPS = 60

# --- Init ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + BOTTOM_BAR_HEIGHT))
pygame.display.set_caption("Infinite Level Editor")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 16)

# --- Load Tiles ---
tile_dir = "assets"
tile_images = {}
tile_ids = []
file_list = sorted([f for f in os.listdir(tile_dir) if f.endswith(".png")])

for idx, filename in enumerate(file_list):
    img = pygame.image.load(os.path.join(tile_dir, filename)).convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    tile_images[idx] = img
    tile_ids.append(idx)

current_tile = tile_ids[0] if tile_ids else 0
drawing = False
camera_x, camera_y = 0, 0

# --- Load existing level.json ---
grid = {}
if os.path.exists("level.json") and os.path.getsize("level.json") > 0:
    try:
        with open("level.json", "r") as f:
            data = json.load(f)
            for key, tid in data.items():
                x_str, y_str = key.split(",")
                grid[(int(x_str), int(y_str))] = tid
        print("✅ Loaded existing level.json")
    except json.JSONDecodeError:
        print("⚠️ level.json is invalid, starting with empty grid.")
else:
    print("ℹ️ No valid level.json found, starting with empty grid.")

# --- Drawing ---
def draw_world():
    cols = SCREEN_WIDTH // TILE_SIZE + 2
    rows = SCREEN_HEIGHT // TILE_SIZE + 2

    for dy in range(rows):
        for dx in range(cols):
            wx = camera_x + dx
            wy = camera_y + dy
            tile_id = grid.get((wx, wy), -1)
            if tile_id >= 0 and tile_id in tile_images:
                screen.blit(tile_images[tile_id], (dx * TILE_SIZE, dy * TILE_SIZE))
            pygame.draw.rect(screen, (30, 30, 30), (dx * TILE_SIZE, dy * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

def draw_palette():
    for i, tid in enumerate(tile_ids):
        x = i * TILE_SIZE
        y = SCREEN_HEIGHT
        screen.blit(tile_images[tid], (x, y))
        color = (255, 255, 0) if tid == current_tile else (100, 100, 100)
        pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE), 2)

def draw_instructions():
    text = "[Arrows/WASD] Move  |  [Mouse] Paint  |  [Click Palette] Change Tile  |  [E] Save to level.json"
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, (5, SCREEN_HEIGHT + PALETTE_HEIGHT + 2))

# --- Main Loop ---
running = True
while running:
    screen.fill((0, 0, 0))
    draw_world()
    draw_palette()
    draw_instructions()

    mx, my = pygame.mouse.get_pos()
    tx = mx // TILE_SIZE + camera_x
    ty = my // TILE_SIZE + camera_y

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if SCREEN_HEIGHT <= my < SCREEN_HEIGHT + PALETTE_HEIGHT:
                index = mx // TILE_SIZE
                if index < len(tile_ids):
                    current_tile = tile_ids[index]
            else:
                drawing = True

        elif event.type == pygame.MOUSEBUTTONUP:
            drawing = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                with open("level.json", "w") as f:
                    json.dump({f"{x},{y}": tid for (x, y), tid in grid.items()}, f, indent=2)
                print("💾 Saved to level.json")

    # Scroll
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        camera_x -= 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        camera_x += 1
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        camera_y -= 1
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        camera_y += 1

    # Paint
    if drawing and my < SCREEN_HEIGHT:
        grid[(tx, ty)] = current_tile

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
