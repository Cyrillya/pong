import pygame
import random
import math

# Constants
board_height = 120
board_width = 10
board_speed = 300
board_percent = 0.18
window_size = 840, 480
fps_limit = 144
ball_speed_init = 300
ball_radius = 12
speed_multiplier_max = 2.4

# pygame setup
pygame.display.set_caption("Pong Game")
pygame.init()
screen = pygame.display.set_mode(window_size)
clock = pygame.time.Clock()
running = True
dt = 0

# Resources
start_sound = pygame.mixer.Sound('../sfx/start.wav')
collide_sound = pygame.mixer.Sound('../sfx/collide.wav')
collide_sound.set_volume(0.2)
win_sound = pygame.mixer.Sound('../sfx/win.wav')

# Global variables
left_board_center = pygame.Vector2(int(window_size[0] * board_percent), screen.get_height() / 2)
right_board_center = pygame.Vector2(int(window_size[0] * (1 - board_percent)), screen.get_height() / 2)
ball_center = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
score_font = pygame.font.Font("../fonts/Azonix.otf", 60)
font = pygame.font.Font("../fonts/Azonix.otf", 24)
left_score = 0
right_score = 0
blink_timer = 0
who_just_scored = None
run_speed_multiplier = 1
game_paused = True

def _random_ball_velocity():
    angle_deg = random.choice([random.uniform(-30, 30), random.uniform(150, 210)])
    ang = math.radians(angle_deg)
    return pygame.Vector2(math.cos(ang), math.sin(ang)).normalize()

ball_velocity = _random_ball_velocity()

def draw_ball():
    color = "white"
    border_color = "gray"
    pygame.draw.circle(screen, border_color, (int(ball_center.x), int(ball_center.y)), ball_radius)
    pygame.draw.circle(screen, color, (int(ball_center.x), int(ball_center.y)), ball_radius - 3)

def draw_board(center):
    line_width = 3
    color = "gray"
    rect = get_rect_from_center(center)
    pygame.draw.rect(screen, "white", rect)
    pygame.draw.line(screen, color, rect.topleft, rect.topright, line_width)
    pygame.draw.line(screen, color, rect.topright, rect.bottomright, line_width)
    pygame.draw.line(screen, color, rect.bottomright, rect.bottomleft, line_width)
    pygame.draw.line(screen, color, rect.bottomleft, rect.topleft, line_width)

def get_rect_from_center(center):
    return pygame.Rect(
        center.x - board_width // 2,
        center.y - board_height // 2,
        board_width,
        board_height
    )

def draw():
    screen.fill("black")
    draw_entities()
    draw_score()
    draw_timer_bar()
    pygame.display.flip()

def draw_entities():
    draw_board(left_board_center)
    draw_board(right_board_center)
    draw_ball()

# 绘制比分
def draw_score():
    global left_score, right_score, blink_timer, who_just_scored

    left_color = "white"
    if who_just_scored == 'left' and blink_timer > 0 and blink_timer * 1000 % 400 < 200:
        left_color = "black"
    right_color = "white"
    if who_just_scored == 'right' and blink_timer > 0 and blink_timer * 1000 % 400 < 200:
        right_color = "black"

    left_score_text = score_font.render(left_score.__str__(), True, pygame.Color(left_color))
    right_score_text = score_font.render(right_score.__str__(), True, pygame.Color(right_color))
    left_text_width = left_score_text.get_width()
    right_text_width = right_score_text.get_width()
    percent = 0.4

    screen.blit(left_score_text, (screen.get_width() * percent - left_text_width // 2, 20))
    screen.blit(right_score_text, (screen.get_width() * (1 - percent) - right_text_width // 2, 20))

    # 冒号
    colon = score_font.render(":", True, pygame.Color("white"))
    colon_width = colon.get_width()
    screen.blit(colon, (screen.get_width() // 2 - colon_width // 2, 17))

def draw_timer_bar():
    if blink_timer > 0:
        bar_width = 200
        bar_height = 15
        x = screen.get_width() / 2 - bar_width / 2
        y = screen.get_height() - 40
        percent = blink_timer / 1.5
        pygame.draw.rect(screen, "gray", (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, "white", (x, y, bar_width * percent, bar_height))

def update_ball():
    global ball_center
    # 越来越快
    speed = ball_speed_init * run_speed_multiplier
    ball_center += ball_velocity * speed * dt

# 重置球的位置和方向
def reset_ball(direction=None):
    global ball_center, ball_velocity
    ball_center.update(screen.get_width() / 2, screen.get_height() / 2)
    if direction == 'left':
        ang = math.radians(random.uniform(150, 210))
    elif direction == 'right':
        ang = math.radians(random.uniform(-30, 30))
    else:
        ang = math.radians(random.uniform(-30, 30) if random.random() < 0.5 else random.uniform(150, 210))
    ball_velocity = pygame.Vector2(math.cos(ang), math.sin(ang)).normalize()

def update_collide():
    global ball_center, ball_velocity, blink_timer, who_just_scored, left_score, right_score, run_speed_multiplier

    ball_rect = pygame.Rect(int(ball_center.x - ball_radius), int(ball_center.y - ball_radius), ball_radius * 2, ball_radius * 2)

    # paddle rects
    left_rect = get_rect_from_center(left_board_center)
    right_rect = get_rect_from_center(right_board_center)

    if ball_center.y - ball_radius <= 0:
        ball_center.y = ball_radius
        ball_velocity.y *= -1
    elif ball_center.y + ball_radius >= screen.get_height():
        ball_center.y = screen.get_height() - ball_radius
        ball_velocity.y *= -1

    if ball_rect.colliderect(left_rect):
        ball_center.x = left_rect.right + ball_radius
        ball_velocity.x *= -1
        offset = (ball_center.y - left_board_center.y) / (board_height / 2)
        ball_velocity.y += offset * 0.5
        ball_velocity = ball_velocity.normalize()
        run_speed_multiplier = min(run_speed_multiplier + 0.1, speed_multiplier_max)
        collide_sound.play()
    elif ball_rect.colliderect(right_rect):
        ball_center.x = right_rect.left - ball_radius
        ball_velocity.x *= -1
        offset = (ball_center.y - right_board_center.y) / (board_height / 2)
        ball_velocity.y += offset * 0.5
        ball_velocity = ball_velocity.normalize()
        run_speed_multiplier = min(run_speed_multiplier + 0.1, speed_multiplier_max)
        collide_sound.play()

    # 经过左右边界得分
    if ball_center.x < -ball_radius * 2 - 50:
        reset_ball(direction='right')
        blink_timer = 1.5
        who_just_scored = 'right'
        right_score += 1
        run_speed_multiplier = 1
        win_sound.play()
    elif ball_center.x > screen.get_width() + ball_radius * 2 + 50:
        reset_ball(direction='left')
        blink_timer = 1.5
        who_just_scored = 'left'
        left_score += 1
        run_speed_multiplier = 1
        win_sound.play()

def update_control():
    keys = pygame.key.get_pressed()
    speed = board_speed
    if keys[pygame.K_w]:
        left_board_center.y -= speed * dt
    if keys[pygame.K_s]:
        left_board_center.y += speed * dt
    if keys[pygame.K_UP]:
        right_board_center.y -= speed * dt
    if keys[pygame.K_DOWN]:
        right_board_center.y += speed * dt

    half = board_height / 2
    left_board_center.y = max(half, min(screen.get_height() - half, left_board_center.y))
    right_board_center.y = max(half, min(screen.get_height() - half, right_board_center.y))

def handle_exit(events):
    global game_paused
    for event in events:
        if event.type == pygame.QUIT:
            return True
    return False

def handle_control_key(events):
    global game_paused
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and game_paused is False:
                game_paused = True
                return
            game_paused = False

def update_menu_and_draw():
    screen.fill("black")

    text_lines = [
        "Use W/S to control left board",
        "Use Up/Down to control right board",
        "Press any key to start"
    ]
    text_surfaces = [font.render(line, True, pygame.Color("white")) for line in text_lines]
    height = sum(surface.get_height() for surface in text_surfaces) + 15
    width = max(surface.get_width() for surface in text_surfaces) + 10
    draw_pos = pygame.Vector2(screen.get_width() // 2 - width // 2, screen.get_height() // 2 - height // 2)

    for text_surface in text_surfaces:
        screen.blit(text_surface, draw_pos)
        draw_pos.y += text_surface.get_height() + 5

    pygame.display.flip()

def update():
    global blink_timer, game_paused
    if blink_timer > 0:
        blink_timer -= dt
        if blink_timer <= 0:
            start_sound.play()
    else:
        update_control()
        update_ball()
        update_collide()

while running:
    events = pygame.event.get()
    running = handle_exit(events) is False
    handle_control_key(events)
    if game_paused:
        update_menu_and_draw()
    else:
        update()
        draw()
    # fps限制
    dt = clock.tick(fps_limit) / 1000

pygame.quit()