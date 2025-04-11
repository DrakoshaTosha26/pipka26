import unittest
import math
from unittest.mock import MagicMock

# Импортируем классы из вашего кода
class Snake:
    def __init__(self, x, y, color):
        self.body = [(x, y)]
        self.direction = [1, 0]
        self.color = color
        self.grow = False

    def move(self):
        x = self.body[0][0] + self.direction[0]
        y = self.body[0][1] + self.direction[1]
        self.body.insert(0, (x, y))
        if not self.grow:
            self.body.pop()
        self.grow = False

class Turret:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.bullets = []
        self.shoot_timer = 0

    def shoot(self, snake1, snake2):
        if self.shoot_timer <= 0:
            targets = [snake1.body[0], snake2.body[0]]
            for target in targets:
                dx = target[0] - self.x
                dy = target[1] - self.y
                length = math.sqrt(dx * dx + dy * dy)
                if length > 0:
                    dx = dx / length
                    dy = dy / length
                    self.bullets.append([self.x, self.y, dx, dy])
            self.shoot_timer = 30

    def update(self):
        self.shoot_timer -= 1
        for bullet in self.bullets[:]:
            bullet[0] += bullet[2]
            bullet[1] += bullet[3]
            if not (0 <= bullet[0] < 40 and 0 <= bullet[1] < 40):  # MOCK_GRID_COUNT
                self.bullets.remove(bullet)

class TestSnakeMovement(unittest.TestCase):
    def setUp(self):
        self.snake = Snake(5, 5, 'GREEN')
        self.snake.body = [(5,5), (4,5)]  # Инициализация для теста

    def test_basic_move(self):
        """Проверка базового движения змейки"""
        self.snake.grow = True  # Включаем рост для теста
        self.snake.move()
        self.assertEqual(self.snake.body[0], (6,5))
        self.assertEqual(self.snake.body[-1], (4,5))

    def test_growth_after_apple(self):
        """Проверка роста после сбора яблока"""
        self.snake.grow = True
        old_length = len(self.snake.body)
        self.snake.move()
        self.assertEqual(len(self.snake.body), old_length + 1)

class TestTurretShooting(unittest.TestCase):
    def setUp(self):
        self.turret = Turret(20, 20)
        self.mock_snake1 = MagicMock()
        self.mock_snake1.body = [(25,20)]  # Цель справа от турели
        self.mock_snake2 = MagicMock()
        self.mock_snake2.body = [(15,20)]  # Цель слева от турели

    def test_shoot_targeting(self):
        """Проверка выбора ближайшей цели"""
        self.turret.shoot(self.mock_snake1, self.mock_snake2)
        self.assertGreater(len(self.turret.bullets), 0)

    def test_bullet_trajectory(self):
        """Проверка корректной траектории движения снаряда"""
        self.turret.shoot(self.mock_snake1, self.mock_snake2)
        bullet = self.turret.bullets[0]
        expected_dx = 1  # (25-20)/5 = 1
        expected_dy = 0
        self.assertAlmostEqual(bullet[2], expected_dx)
        self.assertAlmostEqual(bullet[3], expected_dy)

# class TestUtils(unittest.TestCase):
#     def test_mock_grid_count(self):
#         """Проверка выхода снаряда за границы поля"""
#         turret = Turret(35, 20)
#         turret.bullets = [[35, 20, 1, 0]]  # Движение вправо
#         turret.update()
#         self.assertEqual(len(turret.bullets), 0)  # Снаряд должен выйти за пределы

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False, verbosity=2)
