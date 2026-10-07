import math
import sys
import pygame

# Khởi tạo Pygame
pygame.init()

# Cấu hình màn hình
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mr Bullet - Python Ricochet Shooter")

# Màu sắc
BG_COLOR = (15, 52, 96)
GROUND_COLOR = (22, 33, 62)
PLAYER_COLOR = (78, 84, 200)
ENEMY_COLOR = (255, 77, 77)
WALL_COLOR = (233, 69, 96)
BULLET_COLOR = (249, 213, 110)
WHITE = (255, 255, 255)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 22, bold=True)


# Lớp Nhân vật (Người chơi & Kẻ địch)
class Character:

    def __init__(self, x, y, width=30, height=50, color=PLAYER_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.alive = True

    def draw(self, surface):
        if self.alive:
            pygame.draw.rect(surface, self.color, self.rect)
            # Vẽ mắt cho nhân vật
            eye_color = WHITE if self.color == ENEMY_COLOR else (0, 0, 0)
            pygame.draw.rect(
                surface, eye_color, (self.rect.x + 5, self.rect.y + 10, 5, 5)
            )


# Lớp Viên đạn
class Bullet:

    def __init__(self, x, y, angle, speed=12):
        self.x = x
        self.y = y
        self.radius = 5
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.bounces = 0
        self.max_bounces = 5

    def update(self, walls):
        self.x += self.vx
        self.y += self.vy

        # Va chạm biên ngoài màn hình (Nảy đạn)
        if (
            self.x - self.radius < 0
            or self.x + self.radius > WIDTH
        ):
            self.vx *= -1
            self.bounces += 1
        if (
            self.y - self.radius < 0
            or self.y + self.radius > HEIGHT - 70
        ):  # Trừ độ cao mặt đất
            self.vy *= -1
            self.bounces += 1

        # Va chạm vật cản (Walls)
        bullet_rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2,
        )
        for wall in walls:
            if bullet_rect.colliderect(wall):
                # Đổi hướng đạn đơn giản khi va chạm
                self.vx *= -1
                self.vy *= -1
                self.bounces += 1
                break

    def draw(self, surface):
        pygame.draw.circle(
            surface, BULLET_COLOR, (int(self.x), int(self.y)), self.radius
        )


# Dữ liệu các Màn chơi (Level)
LEVELS = [
    {
        "ammo": 3,
        "enemies": [Character(650, 380, color=ENEMY_COLOR)],
        "walls": [pygame.Rect(400, 250, 20, 180)],
    },
    {
        "ammo": 2,
        "enemies": [Character(700, 150, color=ENEMY_COLOR)],
        "walls": [pygame.Rect(500, 0, 20, 300), pygame.Rect(650, 200, 100, 20)],
    },
]

# Trạng thái Game
current_level = 0
player = Character(80, 380, color=PLAYER_COLOR)
ammo = 0
bullets = []
enemies = []
walls = []


def load_level(level_idx):
    global ammo, bullets, enemies, walls
    data = LEVELS[level_idx % len(LEVELS)]
    ammo = data["ammo"]
    bullets = []
    # Khôi phục trạng thái sống cho kẻ địch
    enemies = [Character(e.rect.x, e.rect.y, color=ENEMY_COLOR) for e in data["enemies"]]
    walls = [w.copy() for w in data["walls"]]


load_level(current_level)

# Vòng lặp chính của Game
running = True
while running:
    clock.tick(60)  # Giới hạn 60 FPS
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # --- 1. XỬ LÝ SỰ KIỆN ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if ammo > 0:
                # Tính góc bắn theo con trỏ chuột
                start_x = player.rect.x + 15
                start_y = player.rect.y + 15
                angle = math.atan2(mouse_y - start_y, mouse_x - start_x)

                bullets.append(Bullet(start_x, start_y, angle))
                ammo -= 1

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Nhấn 'R' để chơi lại màn
                load_level(current_level)

    # --- 2. CẬP NHẬT LOGIC ---
    for bullet in bullets[:]:
        bullet.update(walls)

        # Kiểm tra bắn trúng kẻ địch
        bullet_rect = pygame.Rect(
            bullet.x - bullet.radius,
            bullet.y - bullet.radius,
            bullet.radius * 2,
            bullet.radius * 2,
        )
        for enemy in enemies:
            if enemy.alive and bullet_rect.colliderect(enemy.rect):
                enemy.alive = False
                if bullet in bullets:
                    bullets.remove(bullet)

        # Xóa đạn nếu nảy quá nhiều
        if bullet.bounces > bullet.max_bounces and bullet in bullets:
            bullets.remove(bullet)

    # Kiểm tra điều kiện Thắng / Thua
    remaining_enemies = sum(1 for e in enemies if e.alive)
    if remaining_enemies == 0:
        current_level += 1
        pygame.time.delay(500)
        load_level(current_level)

    # --- 3. VẼ ĐỒ HỌA ---
    screen.fill(BG_COLOR)

    # Vẽ mặt đất
    pygame.draw.rect(screen, GROUND_COLOR, (0, 430, WIDTH, 70))

    # Vẽ đường định hướng (Laser line)
    if ammo > 0:
        pygame.draw.line(
            screen,
            (200, 200, 200),
            (player.rect.x + 15, player.rect.y + 15),
            (mouse_x, mouse_y),
            1,
        )

    # Vẽ vật cản (Walls)
    for wall in walls:
        pygame.draw.rect(screen, WALL_COLOR, wall)

    # Vẽ Người chơi & Kẻ địch
    player.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)

    # Vẽ Đạn
    for bullet in bullets:
        bullet.draw(screen)

    # Vẽ Giao diện UI (Màn chơi & Số đạn)
    level_text = font.render(
        f"Man: {current_level + 1}", True, WHITE
    )
    ammo_text = font.render(f"Dan: {ammo}", True, WHITE)
    reset_text = font.render("Nhan 'R' de choi lai", True, (180, 180, 180))

    screen.blit(level_text, (20, 20))
    screen.blit(ammo_text, (WIDTH - 120, 20))
    screen.blit(reset_text, (20, 450))

    pygame.display.flip()

pygame.quit()
sys.exit()
