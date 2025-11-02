import pygame
from pygame import Vector2

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

    @staticmethod
    def line_intersects_line(a, b, c, d):
        """
        判断两条线段ab和cd是否相交
        使用向量叉积方法
        """
        def cross(o, a, b):
            return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)

        # 检查两条线段是否互相跨越
        if (cross(a, c, d) * cross(b, c, d) < 0 and
                cross(c, a, b) * cross(d, a, b) < 0):
            return True

        # 检查端点是否在另一条线段上
        def on_segment(p, a, b):
            return (min(a.x, b.x) <= p.x <= max(a.x, b.x) and
                    min(a.y, b.y) <= p.y <= max(a.y, b.y))

        if cross(a, c, d) == 0 and on_segment(a, c, d):
            return True
        if cross(b, c, d) == 0 and on_segment(b, c, d):
            return True
        if cross(c, a, b) == 0 and on_segment(c, a, b):
            return True
        if cross(d, a, b) == 0 and on_segment(d, a, b):
            return True

        return False

    @staticmethod
    def lerp_vector2(a: Vector2, b: Vector2, t: float) -> Vector2:
        return Vector2(
            Helper.lerp(a.x, b.x, t),
            Helper.lerp(a.y, b.y, t)
        )

    @staticmethod
    def line_rect_collision(line_start, line_end, rect):
        # 转换为Vector2以便进行向量运算
        p1 = Vector2(line_start)
        p2 = Vector2(line_end)
    
        # 如果线段完全在矩形的一侧，则不可能相交
        if (p1.x < rect.left and p2.x < rect.left) or \
                (p1.x > rect.right and p2.x > rect.right) or \
                (p1.y < rect.top and p2.y < rect.top) or \
                (p1.y > rect.bottom and p2.y > rect.bottom):
            return False
    
        # 检查线段是否与矩形的任何一条边相交
        edges = [
            (Vector2(rect.left, rect.top), Vector2(rect.right, rect.top)),    # 上边
            (Vector2(rect.right, rect.top), Vector2(rect.right, rect.bottom)), # 右边
            (Vector2(rect.right, rect.bottom), Vector2(rect.left, rect.bottom)), # 下边
            (Vector2(rect.left, rect.bottom), Vector2(rect.left, rect.top))   # 左边
        ]
    
        for edge_start, edge_end in edges:
            if Helper.line_intersects_line(p1, p2, edge_start, edge_end):
                return True
    
        return False
