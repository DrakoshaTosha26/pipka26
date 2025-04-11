import unittest
import random
import math
import pygame
from game import (
    WINDOW_SIZE,
    GRID_SIZE,
    GRID_COUNT,
    Snake,
    PoopMonster,
    Turret,
    spawn_food,
    spawn_power_up,
    SHIELD, SPEED, POOP_EATER, TURRET
)

# Для тестирования можно инициализировать pygame (если это требуется для создания поверхностей)
pygame.init()

class TestGameLogic(unittest.TestCase):
    def setUp(self):
        # Инициализируем базовое состояние для тестов
        # Эти объекты могут использоваться для тестирования функций spawn_* и collision detection
        self.snake1 = Snake(5, GRID_COUNT // 2, (0, 255, 0))
        self.snake2 = Snake(GRID_COUNT - 6, GRID_COUNT // 2, (0, 0, 255))
        self.snake1.body = [(5, 10), (4, 10), (3, 10)]
        self.snake2.body = [(15, 10), (16, 10), (17, 10)]
        # Задаём турели, которых нужно исключать при генерации еды/апплов (если используется аналогичная логика)
        self.turrets = [Turret(GRID_COUNT // 2, GRID_COUNT // 2)]
        
        # Переопределим глобальные объекты (если нужно)
        # Например, если spawn_food использует глобальные snake1, snake2, power_up, можно их задать
        global snake1, snake2, power_up
        snake1 = self.snake1
        snake2 = self.snake2
        power_up = None

    def test_spawn_food(self):
        # Функция должна возвращать координаты, не пересекающиеся с телами змей или турелями
        food = spawn_food()
        self.assertNotIn(food, self.snake1.body, "Еда не должна попадать в тело змеи 1")
        self.assertNotIn(food, self.snake2.body, "Еда не должна попадать в тело змеи 2")
        for turret in self.turrets:
            self.assertNotEqual(food, (turret.x, turret.y), "Еда не должна генерироваться на турели")

    def test_spawn_power_up(self):
        # Здесь аналогичная логика для power-up
        food = spawn_food()  # чтобы гарантировать несоприкосновение с едой в power-up
        power = spawn_power_up()
        self.assertNotIn((power.x, power.y), self.snake1.body, "PowerUp не должен генерироваться на змее 1")
        self.assertNotIn((power.x, power.y), self.snake2.body, "PowerUp не должен генерироваться на змее 2")
        # Проверяем типы: они должны быть одним из заданных
        self.assertIn(power.type, (SHIELD, SPEED, POOP_EATER, TURRET), "Неверный тип power-up")

    def test_snake_move_wrapping_in_god_mode(self):
        # Проверяем, что при активированном god_mode змейка появляется с противоположной стороны
        self.snake1.god_mode = True
        # Поместим голову змеи в крайнюю позицию
        self.snake1.body = [(GRID_COUNT - 1, 10)]
        self.snake1.direction = [1, 0]
        collision = self.snake1.move()
        new_head = self.snake1.body[0]
        self.assertEqual(new_head[0], 0, "При god_mode голова должна появиться с противоположной стороны по оси X")
        self.assertFalse(collision, "В режиме god_mode столкновения не должны приводить к завершению игры")

    def test_snake_collision_with_self(self):
        # Проверим самопересечение змеи
        self.snake1.god_mode = False
        # Искусственно создаём пересечение
        self.snake1.body = [(10, 10), (10, 11), (10, 12), (10, 10)]
        collision = self.snake1.check_collision(self.snake2, [])
        self.assertTrue(collision, "Столкновение с собственным телом должно срабатывать")

    def test_snake_collision_with_other(self):
        # Проверяем столкновение голов двух змей
        self.snake1.god_mode = False
        self.snake2.god_mode = False
        common_head = (5, 5)
        self.snake1.body = [common_head] + self.snake1.body[1:]
        self.snake2.body = [common_head] + self.snake2.body[1:]
        collision = self.snake1.check_collision(self.snake2, [])
        self.assertTrue(collision, "Столкновение с другой змеёй должно срабатывать")

    def test_turret_shooting(self):
        # Проверяем, что турель при вызове shoot добавляет пули, если таймер истёк
        turret = Turret(10, 10)
        # Обнуляем таймер, чтобы турель могла стрелять
        turret.shoot_timer = 0
        turret.shoot(self.snake1, self.snake2)
        self.assertGreater(len(turret.bullets), 0, "Турель должна создать пулю при стрельбе")
        # Проверяем, что направление пули корректно (вектор нормализован)
        for bullet in turret.bullets:
            dx, dy = bullet[2], bullet[3]
            length = math.sqrt(dx*dx + dy*dy)
            self.assertAlmostEqual(length, 1.0, places=2, msg="Вектор пули должен быть нормализован")

    def test_poop_monster_movement(self):
        # Проверяем, что монстр перемещается в направлении хвоста выбранной змеи
        monster = PoopMonster(5, 5, self.snake1)
        # Установим хвост змеи дальше от головы
        self.snake1.body = [(5, 5), (5, 6), (5, 7)]
        init_x, init_y = monster.x, monster.y
        monster.move()
        self.assertNotEqual((monster.x, monster.y), (init_x, init_y),
                            "PoopMonster должен перемещаться при вызове move()")

if __name__ == '__main__':
    unittest.main()
