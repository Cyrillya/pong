import math
import random

import pygame

from src.Ball import Ball
from src.Sound import Sound
from src.Constants import Constants
from src.Helper import Helper

# Constants
board_height = Constants.board_height
board_width = Constants.board_width
board_speed = Constants.board_speed
board_percent = Constants.board_percent
window_size = Constants.window_size
fps_limit = Constants.fps_limit

# pygame setup
pygame.display.set_caption("Pong Game")
pygame.init()
screen = pygame.display.set_mode(window_size)
clock = pygame.time.Clock()
running = True
dt = 0

# Global variables
left_board_center = pygame.Vector2(int(window_size[0] * board_percent), screen.get_height() / 2)
right_board_center = pygame.Vector2(int(window_size[0] * (1 - board_percent)), screen.get_height() / 2)
old_left_board_ys = [left_board_center.y]
old_right_board_ys = [right_board_center.y]
score_font = pygame.font.Font("../fonts/Azonix.otf", 60)
font = pygame.font.Font("../fonts/Azonix.otf", 24)
left_score = 0
right_score = 0
blink_timer = 0
who_just_scored = None
game_paused = True
bot_mode = True
bot_random_move_point = None

# Instances
ball = Ball(screen)

def draw_ball():
    color = "white"
    border_color = "gray"
    pygame.draw.circle(screen, border_color, (int(ball.center.x), int(ball.center.y)), Ball.radius)
    pygame.draw.circle(screen, color, (int(ball.center.x), int(ball.center.y)), Ball.radius - 3)


def draw_board(center):
    line_width = 3
    color = "gray"
    rect = Helper.get_board_rect(center)
    pygame.draw.rect(screen, "white", rect)
    pygame.draw.line(screen, color, rect.topleft, rect.topright, line_width)
    pygame.draw.line(screen, color, rect.topright, rect.bottomright, line_width)
    pygame.draw.line(screen, color, rect.bottomright, rect.bottomleft, line_width)
    pygame.draw.line(screen, color, rect.bottomleft, rect.topleft, line_width)

def draw():
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


def update_old_centers():
    old_left_board_ys.append(left_board_center.copy().y)
    old_right_board_ys.append(right_board_center.copy().y)
    if len(old_left_board_ys) > 10:
        old_left_board_ys.pop(0)
    if len(old_right_board_ys) > 10:
        old_right_board_ys.pop(0) 

def move_bot_to(center, y, max_distance = board_height / 3):
    if abs(center.y - y) > max_distance:
        if center.y < y:
            center.y += board_speed * dt
        elif center.y > y:
            center.y -= board_speed * dt

def update_bot(self_center, opponent_center):
    global bot_random_move_point
    simulation_dt = 1 * dt
    ball_towards_self = Helper.sign(self_center.x - opponent_center.x) == Helper.sign(ball.velocity.x)
    # 球正在朝自己飞来，预判球落点并移动板子
    if ball_towards_self:
        bot_random_move_point = None
        predicted_ball = ball.__copy__()
        while Helper.sign(predicted_ball.velocity.x) == Helper.sign(self_center.x - predicted_ball.center.x):
            predicted_ball.update(left_board_center, right_board_center, screen, simulation_dt)
        move_bot_to(self_center, predicted_ball.center.y)

    # 球不在朝自己飞来，则随机移动到场地中心附近
    else:
        predicted_ball = ball.__copy__()
        while Helper.sign(predicted_ball.velocity.x) != Helper.sign(self_center.x - predicted_ball.center.x):
            predicted_board_y = predicted_ball.center.y
            if Helper.line_rect_collision(predicted_ball.center, predicted_ball.center + predicted_ball.velocity * 1000, Helper.get_board_rect(opponent_center)):
                predicted_board_y = opponent_center.y
            predicted_ball.update(pygame.Vector2(left_board_center.x, predicted_board_y), pygame.Vector2(right_board_center.x, predicted_board_y), screen, simulation_dt)
        while Helper.sign(predicted_ball.velocity.x) == Helper.sign(self_center.x - predicted_ball.center.x):
            predicted_ball.update(left_board_center, right_board_center, screen, simulation_dt)
        move_bot_to(self_center, predicted_ball.center.y)
        return self_center
        if bot_random_move_point is None:
            bot_random_move_point = screen.get_height() / 2 + random.randint(-100, 100)
        else:
            move_bot_to(self_center, bot_random_move_point, 10)
    return self_center

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
    
    if bot_mode:
        update_bot(right_board_center, left_board_center)
        # update_bot(left_board_center, right_board_center)

    half = board_height / 2
    left_board_center.y = Helper.clamp(left_board_center.y, half, screen.get_height() - half)
    right_board_center.y = Helper.clamp(right_board_center.y, half, screen.get_height() - half)

def check_ball_event():
    global blink_timer, who_just_scored, left_score, right_score
    events = ball.consume_event()
    if events == "pass_left":
        blink_timer = 1.5
        who_just_scored = 'right'
        right_score += 1
        Sound.play_sound("win")
    elif events == "pass_right":
        blink_timer = 1.5
        who_just_scored = 'left'
        left_score += 1
        Sound.play_sound("win")
    elif events == "collide_board_left" or events == "collide_board_right":
        Sound.play_sound("collide")
        

def handle_exit(events):
    global game_paused
    for event in events:
        if event.type == pygame.QUIT:
            return True
    return False


def handle_control_key(events):
    global game_paused, bot_mode
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                if bot_mode:
                    bot_mode = False
                else:
                    bot_mode = True
            if event.key == pygame.K_ESCAPE and game_paused is False:
                game_paused = True
                return
            game_paused = False


def update_menu_and_draw():
    screen.fill("black")

    text_lines = [
        "Use W/S to control left board",
        "Use Up/Down to control right board",
        "Press Q to switch bot mode",
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
    global blink_timer, game_paused, who_just_scored, left_score, right_score
    if blink_timer > 0:
        blink_timer -= dt
        if blink_timer <= 0:
            Sound.play_sound("start")
    else:
        update_control()
        ball.update(left_board_center, right_board_center, screen, dt)
        check_ball_event()


while running:
    screen.fill("black")
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
