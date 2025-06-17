import asyncio
import platform
import pygame
from collections import deque

# Khởi tạo Pygame
pygame.init()

# Kích thước màn hình
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Supermarket Map")

# Màu sắc
WALL_COLOR = (100, 100, 100)  # Tường
MILK_COLOR = (0, 0, 255)      # Sữa
CANDY_COLOR = (255, 255, 0)   # Bánh kẹo
FRUIT_COLOR = (0, 255, 0)     # Trái cây
WATER_COLOR = (0, 255, 255)   # Nước
SPICE_COLOR = (255, 255, 255) # Muối/Đường
PATH_COLOR = (200, 200, 200)  # Đường đi
USER_COLOR = (255, 0, 0)      # Người dùng
ROUTE_COLOR = (255, 165, 0)   # Đường dẫn

# Kích thước ô
TILE_SIZE = 20

# Tạo bản đồ siêu thị (40x40)
map_data = [[1 for _ in range(40)] for _ in range(40)]

# Đặt đường đi ngang
for y in [2, 5, 10, 15, 20, 25, 30, 35]:
    for x in range(1, 39):
        map_data[y][x] = 0

# Đặt đường đi dọc
for x in [4, 5, 10, 14, 15, 20, 24, 25, 30, 34, 35]:
    for y in range(1, 39):
        map_data[y][x] = 0

# Đặt vị trí người dùng
map_data[2][2] = 2

# Định nghĩa vị trí các kệ
shelf_positions = {
    "sua": (34, 35),
    "banhkeo": (4, 10),
    "traicay": (4, 5),
    "nuoc": (24, 25),
    "muoiduong": (14, 15)
}

# Đảm bảo các vị trí kệ là ô đường đi (0)
for shelf, (x, y) in shelf_positions.items():
    map_data[y][x] = 0

# Tìm vị trí người dùng
def find_user_position():
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            if tile == 2:
                return (x, y)
    return None

# Thuật toán BFS tìm đường đi
def find_path(start, goal):
    if start is None or goal is None:
        return []
    queue = deque([(start, [start])])
    visited = set([start])
    
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == goal:
            return path
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < len(map_data[0]) and 
                0 <= new_y < len(map_data) and 
                (new_x, new_y) not in visited and
                map_data[new_y][new_x] == 0):
                visited.add((new_x, new_y))
                queue.append(((new_x, new_y), path + [(new_x, new_y)]))
    return []

# Vẽ bản đồ với màu sắc và chú thích cho kệ
def draw_map():
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            if (x, y) in shelf_positions.values():
                if (x, y) == shelf_positions["sua"]:
                    color = MILK_COLOR
                elif (x, y) == shelf_positions["banhkeo"]:
                    color = CANDY_COLOR
                elif (x, y) == shelf_positions["traicay"]:
                    color = FRUIT_COLOR
                elif (x, y) == shelf_positions["nuoc"]:
                    color = WATER_COLOR
                elif (x, y) == shelf_positions["muoiduong"]:
                    color = SPICE_COLOR
            elif tile == 1:
                color = WALL_COLOR
            elif tile == 0:
                color = PATH_COLOR
            elif tile == 2:
                color = USER_COLOR
            pygame.draw.rect(screen, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    
    # Thêm chú thích cho từng kệ
    font = pygame.font.SysFont(None, 20)
    for shelf, (x, y) in shelf_positions.items():
        text = font.render(shelf, True, (255, 255, 255))
        screen.blit(text, (x * TILE_SIZE + 5, y * TILE_SIZE + 5))

# Vẽ đường đi
def draw_path(path):
    for x, y in path:
        pygame.draw.rect(screen, ROUTE_COLOR, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

# Hiển thị văn bản
def draw_text(text, pos):
    font = pygame.font.SysFont(None, 24)
    text_surface = font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, pos)

# Thiết lập ban đầu
def setup():
    global user_pos, target_pos, path, current_shelf
    user_pos = find_user_position()
    current_shelf = "sua"
    target_pos = shelf_positions[current_shelf]
    path = find_path(user_pos, target_pos)

# Vòng lặp cập nhật
def update_loop():
    screen.fill((0, 0, 0))
    draw_map()
    if path:
        draw_path(path)
    draw_text(f"Dang di den: {current_shelf}", (10, 30))
    draw_text("Nhan 1: sua, 2: banh keo, 3: trai cay, 4: nuoc, 5: muoi/duong", (10, SCREEN_HEIGHT - 30))
    pygame.display.flip()

# Xử lý sự kiện phím
def handle_key(event):
    global target_pos, path, current_shelf
    key_map = {
        pygame.K_1: "sua",
        pygame.K_2: "banhkeo",
        pygame.K_3: "traicay",
        pygame.K_4: "nuoc",
        pygame.K_5: "muoiduong"
    }
    if event.key in key_map:
        current_shelf = key_map[event.key]
        target_pos = shelf_positions[current_shelf]
        path = find_path(user_pos, target_pos)

# Chạy chương trình
FPS = 30

async def main():
    setup()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                handle_key(event)
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())