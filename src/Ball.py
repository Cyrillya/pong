import pygame

import random
import math

from src.Constants import Constants
from src.Helper import Helper
from src.Sound import Sound


class Ball:
    # Constants
    speed_multiplier_min = Constants.ball_speed_multiplier_min
    speed_multiplier_max = Constants.ball_speed_multiplier_max
    speed_init = Constants.ball_speed_init
    radius = Constants.ball_radius
    
    def __init__(self, screen):
        self.screen = screen
        self.speed_multiplier = Ball.speed_multiplier_min
        self.center = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        self.velocity = Ball._random_ball_velocity()
        self.event = None
        
    def __copy__(self):
        new_ball = Ball(self.screen)
        new_ball.center = self.center.copy()
        new_ball.velocity = self.velocity.copy()
        new_ball.speed_multiplier = self.speed_multiplier
        new_ball.event = self.event
        return new_ball
    
    def distance_to(self, point):
        return self.center.distance_to(point)
    
    def distance_x_to(self, point):
        return abs(self.center.x - point.x)

    @staticmethod
    def _random_ball_velocity():
        angle_deg = random.choice([random.uniform(-30, 30), random.uniform(150, 210)])
        ang = math.radians(angle_deg)
        return pygame.Vector2(math.cos(ang), math.sin(ang)).normalize()

    def get_ball_speed(self, dt):
        # 越来越快
        speed = Ball.speed_init * self.speed_multiplier
        return self.velocity * speed * dt

    @staticmethod
    def get_collide_velocity(b_velocity, board_y, ball_y):
        velocity = b_velocity.copy()
        velocity.x *= -1
        offset = (ball_y - board_y) / (Constants.board_height / 2)
        velocity.y += offset * 0.5
        velocity.y = Helper.clamp(velocity.y, -1, 1)
        velocity = velocity.normalize()
        return velocity
    
    def consume_event(self):
        event = self.event
        self.event = None
        return event

    def update_collide(self, left_board_center, right_board_center, screen):
        ball_rect = pygame.Rect(int(self.center.x - Ball.radius), int(self.center.y - Ball.radius), Ball.radius * 2, Ball.radius * 2)
    
        # paddle rects
        left_rect = Helper.get_board_rect(left_board_center)
        right_rect = Helper.get_board_rect(right_board_center)
    
        # 碰上墙
        if self.center.y - Ball.radius <= 0:
            self.center.y = Ball.radius
            self.velocity.y *= -1
            self.event = "collide_wall_up"
        elif self.center.y + Ball.radius >= screen.get_height():
            self.center.y = screen.get_height() - Ball.radius
            self.velocity.y *= -1
            self.event = "collide_wall_down"
    
        # 碰到板子
        if ball_rect.colliderect(left_rect):
            self.center.x = left_rect.right + Ball.radius
            self.velocity = Ball.get_collide_velocity(self.velocity, left_board_center.y, self.center.y)
            self.speed_multiplier = min(self.speed_multiplier + 0.2, Ball.speed_multiplier_max)
            self.event = "collide_board_left"
        elif ball_rect.colliderect(right_rect):
            self.center.x = right_rect.left - Ball.radius
            self.velocity = Ball.get_collide_velocity(self.velocity, right_board_center.y, self.center.y)
            self.speed_multiplier = min(self.speed_multiplier + 0.2, Ball.speed_multiplier_max)
            self.event = "collide_board_right"
    
        # 经过左右边界得分
        if self.center.x < -Ball.radius * 2 - 50:
            self.reset(direction='right')
            self.event = "pass_left"
        elif self.center.x > screen.get_width() + Ball.radius * 2 + 50:
            self.reset(direction='left')
            self.event = "pass_right"

    def update(self, left_board_center, right_board_center, screen, dt):
        self.center += self.get_ball_speed(dt)
        self.update_collide(left_board_center, right_board_center, screen)

    # 重置球的位置和方向
    def reset(self, direction = None):
        self.speed_multiplier = Ball.speed_multiplier_min
        self.center.update(self.screen.get_width() / 2, self.screen.get_height() / 2)
        if direction == 'left':
            ang = math.radians(random.uniform(150, 210))
        elif direction == 'right':
            ang = math.radians(random.uniform(-30, 30))
        else:
            ang = math.radians(random.uniform(-30, 30) if random.random() < 0.5 else random.uniform(150, 210))
        self.velocity = pygame.Vector2(math.cos(ang), math.sin(ang)).normalize()
        