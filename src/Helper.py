import pygame
from src.Constants import Constants

class Helper:
    @staticmethod
    def clamp(value, min, max):
        return max if value > max else min if value < min else value

    @staticmethod
    def lerp(a, b, t):
        return a + (b - a) * t

    @staticmethod
    def sign(value):
        return (value > 0) - (value < 0)

    @staticmethod
    def get_board_rect(center):
        return pygame.Rect(
            center.x - Constants.board_width // 2,
            center.y - Constants.board_height // 2,
            Constants.board_width,
            Constants.board_height
        )