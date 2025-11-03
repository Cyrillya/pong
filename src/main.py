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
score_font = pygame.font.Font("../fonts/Azonix.otf", 60)
font = pygame.font.Font("../fonts/Azonix.otf", 24)
left_score = 0
right_score = 0
blink_timer = 0
start_direction = None
who_just_scored = None
game_paused = True
left_bot = False
right_bot = True
bot_difficulty_left = 1.0  # 0.0 - 1.0
bot_difficulty_right = 1.0  # 0.0 - 1.0
dt_count = 0

# Instances
ball = Ball(screen)

def restart_game():
    global left_score, right_score, ball, left_board_center, right_board_center, blink_timer, game_paused, dt_count
    left_score = 0
    right_score = 0
    ball = Ball(screen)
    left_board_center = pygame.Vector2(int(window_size[0] * board_percent), screen.get_height() / 2)
    right_board_center = pygame.Vector2(int(window_size[0] * (1 - board_percent)), screen.get_height() / 2)
    blink_timer = 0
    game_paused = True
    dt_count = 0
    print("--- Game Restarted ---")

def update_title():
    text = "Pong Game"
    if game_paused:
        text += " - Paused"
    if left_bot or right_bot:
        text += " - Bot Mode"
    
    text += " - {} FPS".format(int(clock.get_fps()))

    pygame.display.set_caption(text)


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
    screen.fill("black")
    draw_entities()
    draw_score()
    draw_timer_bar()
    draw_bot_indicator()
    pygame.display.flip()


def draw_entities():
    ball.draw()
    draw_board(left_board_center)
    draw_board(right_board_center)


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


def draw_bot_indicator():
    if left_bot:
        text = font.render("BOT {:0.1f}".format(bot_difficulty_left), True, pygame.Color("yellow"))
        screen.blit(text, (20, 20))
    if right_bot:
        text = font.render("BOT {:0.1f}".format(bot_difficulty_right), True, pygame.Color("yellow"))
        screen.blit(text, (screen.get_width() - text.get_width() - 20, 20))

def move_bot_to(center, y, max_distance = board_height / 3):
    if abs(center.y - y) > max_distance:
        if center.y < y:
            center.y += board_speed * dt
        elif center.y > y:
            center.y -= board_speed * dt

def update_bot(self_center, opponent_center, difficulty):
    max_steps = 1000
    ball_towards_self = Helper.sign(self_center.x - opponent_center.x) == Helper.sign(ball.velocity.x)

    # 难度系数决定球离自己多远才开始反应
    if abs(self_center.x - ball.center.x) > screen.get_width() * Helper.lerp(0.2, 1, difficulty):
        return self_center
    
    # 难度影响预测位置和当前位置的混合比例
    # 经过实测，0.75是最好的混合比例
    mix_factor = Helper.lerp(0.0, 0.75, difficulty)

    # 球正在朝自己飞来，预判球落点并移动板子
    if ball_towards_self:
        simulation_dt = 2 * dt
        predicted_ball = ball.__copy__()
        predicted_ball.simulation = True
        while Helper.sign(predicted_ball.velocity.x) == Helper.sign(self_center.x - predicted_ball.center.x) and max_steps > 0:
            predicted_ball.update(left_board_center, right_board_center, screen, simulation_dt)
            max_steps -= 1
            if predicted_ball.passed:
                break
        # 混合比例影响预判位置，越高则越接近预测落点
        destination_y = Helper.lerp(ball.center.y, predicted_ball.center.y, mix_factor)
        move_bot_to(self_center, destination_y)

    # 球不在朝自己飞来
    else:
        # 难度低则无弹前预判
        if difficulty < 0.6:
            return self_center
        predicted_ball = ball.__copy__()
        predicted_ball.simulation = True
        simulation_dt = 4 * dt
        # predicted_ball 正在朝对方飞去
        while Helper.sign(predicted_ball.velocity.x) != Helper.sign(self_center.x - predicted_ball.center.x) and max_steps > 0:
            # 预测与对方板子碰撞的位置
            predicted_board_y = predicted_ball.center.y
            # 如果快要和对方板子碰撞，则检测能不能和目前的板子位置碰撞
            if predicted_ball.distance_x_to(opponent_center) < 60:
                # 如果可以的话，就用当前对手板子位置
                if Helper.line_rect_collision(predicted_ball.center, predicted_ball.center + predicted_ball.velocity * 1000, Helper.get_board_rect(opponent_center)):
                    predicted_board_y = opponent_center.y
                # 如果不能的话，就用对手板子上/下边缘和球碰撞
                else:
                    if predicted_ball.center.y < opponent_center.y:
                        predicted_board_y = opponent_center.y - board_height / 2
                    else:
                        predicted_board_y = opponent_center.y + board_height / 2
            # 更新球
            predicted_ball.update(pygame.Vector2(left_board_center.x, predicted_board_y), pygame.Vector2(right_board_center.x, predicted_board_y), screen, simulation_dt)
            max_steps -= 1
            if predicted_ball.passed:
                break
        # predicted_ball 正在朝自己飞来
        while Helper.sign(predicted_ball.velocity.x) == Helper.sign(self_center.x - predicted_ball.center.x) and max_steps > 0:
            predicted_ball.update(left_board_center, right_board_center, screen, simulation_dt)
            max_steps -= 1
            if predicted_ball.passed:
                break
        # 混合比例影响预判位置，越高则越接近预测落点
        destination_y = Helper.lerp(ball.center.y, predicted_ball.center.y, mix_factor)
        move_bot_to(self_center, destination_y)

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
    
    if right_bot:
        update_bot(right_board_center, left_board_center, bot_difficulty_right)
    if left_bot:
        update_bot(left_board_center, right_board_center, bot_difficulty_left)

    half = board_height / 2
    left_board_center.y = Helper.clamp(left_board_center.y, half, screen.get_height() - half)
    right_board_center.y = Helper.clamp(right_board_center.y, half, screen.get_height() - half)

def check_ball_event():
    global blink_timer, who_just_scored, left_score, right_score, dt_count, start_direction
    dt_count += dt
    events = ball.consume_event()
    if events == "pass_left":
        blink_timer = 1.5
        who_just_scored = 'right'
        right_score += 1
        Sound.play_sound("win")
        print("Right Score! {:0.1f} seconds passed. Now {} - {}".format(dt_count, left_score, right_score))
        dt_count = 0
        start_direction = 'left'
    elif events == "pass_right":
        blink_timer = 1.5
        who_just_scored = 'left'
        left_score += 1
        Sound.play_sound("win")
        print("Left Score! {:0.1f} seconds passed. Now {} - {}".format(dt_count, left_score, right_score))
        dt_count = 0
        start_direction = 'right'
    elif events == "collide_board_left" or events == "collide_board_right":
        Sound.play_sound("collide")
        

def handle_exit(events):
    global game_paused
    for event in events:
        if event.type == pygame.QUIT:
            return True
    return False


def handle_control_key(events):
    global game_paused, bot_difficulty_left, bot_difficulty_right, left_bot, right_bot
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z: 
                left_bot = not left_bot
            if event.key == pygame.K_c:
                right_bot = not right_bot
            if event.key == pygame.K_q:
                bot_difficulty_left += 0.1
                if bot_difficulty_left > 1.0:
                    bot_difficulty_left = 0.0
            if event.key == pygame.K_e:
                bot_difficulty_right += 0.1
                if bot_difficulty_right > 1.0:
                    bot_difficulty_right = 0.0
            if event.key == pygame.K_r:
                restart_game()
            if event.key == pygame.K_ESCAPE:
                game_paused = not game_paused
            if event.key == pygame.K_SPACE and game_paused is True:
                game_paused = False


def update_menu_and_draw():
    screen.fill("black")

    text_lines = [
        "Use W/S to control left board",
        "Use Up/Down to control right board",
        "Use Z/C to toggle bot for left/right board",
        "Use Q/E to adjust bot difficulty",
        "Use R to restart game",
        "Press space to start"
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
            Sound.play_sound("start")
            ball.reset(start_direction)

    update_control()
    ball.update(left_board_center, right_board_center, screen, dt)
    check_ball_event()


while running:
    events = pygame.event.get()
    running = handle_exit(events) is False
    handle_control_key(events)
    update_title()
    if game_paused:
        update_menu_and_draw()
    else:
        update()
        draw()
    # fps限制
    dt = clock.tick(fps_limit) / 1000

pygame.quit()
