import pygame
import random
import math
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)

SHIELD = 1
SPEED = 2
POOP_EATER = 3
TURRET = 4

class Turret:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.bullets = []
        self.shoot_timer = 0

    def shoot(self, snake1, snake2):
        if self.shoot_timer <= 0:
            # Target closest snake
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
            if not (0 <= bullet[0] < GRID_COUNT and 0 <= bullet[1] < GRID_COUNT):
                self.bullets.remove(bullet)

class FartEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lifetime = 20
        self.radius = 1

class PoopMonster:
    def __init__(self, x, y, target_snake):
        self.x = x
        self.y = y
        self.target_snake = target_snake
        self.speed = 0.5

    def move(self):
        if self.target_snake:
            # Move towards snake's tail, avoiding head
            tail = self.target_snake.body[-1]
            head = self.target_snake.body[0]
            dx = tail[0] - self.x
            dy = tail[1] - self.y

            # Avoid head collision
            head_dx = head[0] - self.x
            head_dy = head[1] - self.y
            if abs(head_dx) < GRID_SIZE and abs(head_dy) < GRID_SIZE:
                dx = -head_dx
                dy = -head_dy


            if abs(dx) > abs(dy):
                self.x += self.speed if dx > 0 else -self.speed
            else:
                self.y += self.speed if dy > 0 else -self.speed

class PoopSpot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.stink_effects = []
        self.stink_timer = 0

class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type

class Snake:
    def __init__(self, x, y, color):
        self.body = [(x, y)]
        self.direction = [1, 0]
        self.color = color
        self.grow = False
        self.score = 0
        self.poop_spots = []
        self.fart_effects = []
        self.apples_eaten = 0
        self.god_mode = False
        self.shield = 0
        self.speed_boost = 0
        self.poop_eater = 0
        self.extra_turret = None

    def move(self):
        x = self.body[0][0] + self.direction[0]
        y = self.body[0][1] + self.direction[1]
        if x < 0:
            if self.god_mode:
                x = GRID_COUNT - 1
            else:
                return True
        elif x >= GRID_COUNT:
            if self.god_mode:
                x = 0
            else:
                return True
        if y < 0:
            if self.god_mode:
                y = GRID_COUNT - 1
            else:
                return True
        elif y >= GRID_COUNT:
            if self.god_mode:
                y = 0
            else:
                return True
        self.body.insert(0, (x, y))
        if not self.grow:
            self.body.pop()
        self.grow = False

        if self.apples_eaten >= 2:
            poop_spot = PoopSpot(self.body[-1][0], self.body[-1][1])
            poop_spot.stink_timer = 20
            self.poop_spots.append(poop_spot)
            self.apples_eaten = 0
            # Make all nearby monsters chase this snake
            for monster in poop_monsters:
                if monster.target_snake != (snake2 if self == snake1 else snake1):
                    monster.target_snake = self
        return False

    def check_collision(self, other_snake, turrets):
        head = self.body[0]
        # Self collision
        if head in self.body[1:]:
            if not self.god_mode:
                return True
        # Other snake collision
        if head in other_snake.body:
            if not self.god_mode:
                return True
        # Bullet collision
        for turret in turrets:
            for bullet in turret.bullets:
                if int(bullet[0]) == head[0] and int(bullet[1]) == head[1]:
                    if not self.god_mode:
                        return True
        # Poop collision
        for snake in [self, other_snake]:
            for poop in snake.poop_spots:
                if head[0] == poop.x and head[1] == poop.y and not snake.poop_eater:
                    if not self.god_mode:
                        return True
        return False

def spawn_food():
    while True:
        x = random.randint(1, GRID_COUNT - 2)  # Avoid walls
        y = random.randint(1, GRID_COUNT - 2)  # Avoid walls
        food_pos = (x, y)
        # Check if not in snakes, turret position, or power-up position
        if (food_pos not in snake1.body and 
            food_pos not in snake2.body and 
            not any(food_pos == (t.x, t.y) for t in turrets) and
            food_pos != (power_up.x, power_up.y) if power_up else True):
            return food_pos


def spawn_power_up():
    while True:
        x = random.randint(1, GRID_COUNT - 2)
        y = random.randint(1, GRID_COUNT - 2)
        power_up_pos = (x, y)
        if (power_up_pos not in snake1.body and
                power_up_pos not in snake2.body and
                not any(power_up_pos == (t.x, t.y) for t in turrets) and
                power_up_pos != food):
            power_up_type = random.choice([SHIELD, SPEED, POOP_EATER, TURRET])
            return PowerUp(x, y, power_up_type)

def draw_background():
    # Draw checkerboard pattern
    for i in range(GRID_COUNT):
        for j in range(GRID_COUNT):
            if (i + j) % 2 == 0:
                pygame.draw.rect(screen, (30, 30, 30), 
                               (i * GRID_SIZE, j * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def reset_game():
    global snake1, snake2, food, game_over, turrets, countdown_timer, poop_monsters, power_up
    score1 = snake1.score if 'snake1' in globals() else 0
    score2 = snake2.score if 'snake2' in globals() else 0
    countdown_timer = 15  # 2 seconds at 30 FPS
    snake1 = Snake(5, GRID_COUNT//2, GREEN)
    snake2 = Snake(GRID_COUNT-6, GRID_COUNT//2, BLUE)
    snake1.score = score1
    snake2.score = score2
    snake1.poop_spots = []
    snake2.poop_spots = []
    snake1.fart_effects = []
    snake2.fart_effects = []
    food = spawn_food()
    game_over = False
    turrets = [
        Turret(GRID_COUNT//2, GRID_COUNT//2)  # Single turret in center
    ]
    power_up = spawn_power_up()


def draw_scores():
    font = pygame.font.Font(None, 36)
    score1 = font.render(f'Player 1: {snake1.score}', True, GREEN)
    score2 = font.render(f'Player 2: {snake2.score}', True, BLUE)
    screen.blit(score1, (10, 10))
    screen.blit(score2, (WINDOW_SIZE - 150, 10))

# Initialize game
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('Snake Battle')
clock = pygame.time.Clock()

current_level = 1
apples_eaten_this_level = 0
poop_monsters = []
countdown_timer = 15  # 2 seconds at 30 FPS

power_up = None
snake1 = Snake(5, GRID_COUNT // 2, GREEN)
snake2 = Snake(GRID_COUNT - 6, GRID_COUNT // 2, BLUE)
turrets = [
    Turret(GRID_COUNT//2, GRID_COUNT//2)
]
food = spawn_food()
power_up = spawn_power_up()
game_over = False

def next_level():
    global current_level, apples_eaten_this_level, food, poop_monsters, power_up
    current_level += 1
    apples_eaten_this_level = 0

    # Keep snake positions and directions, just clear poop
    snake1.poop_spots = []
    snake2.poop_spots = []

    # Add new poop monster that will chase snake that poops
    if current_level > 1:
        x = random.randint(1, GRID_COUNT - 2)
        y = random.randint(1, GRID_COUNT - 2)
        poop_monsters.append(PoopMonster(x, y, None))  # Target will be set when snake poops

    food = spawn_food()
    power_up = spawn_power_up()

game_paused = False #added for pause functionality

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == KEYDOWN:
            if game_over and event.key == K_r:
                reset_game()
                continue
            # Player 1 controls (WASD)
            if event.key == K_w and snake1.direction != [0, 1]:
                snake1.direction = [0, -1]
            elif event.key == K_s and snake1.direction != [0, -1]:
                snake1.direction = [0, 1]
            elif event.key == K_a and snake1.direction != [1, 0]:
                snake1.direction = [-1, 0]
            elif event.key == K_d and snake1.direction != [-1, 0]:
                snake1.direction = [1, 0]
            # Player 2 controls (Arrows)
            elif event.key == K_UP and snake2.direction[1] != 1:
                snake2.direction = [0, -1]
            elif event.key == K_DOWN and snake2.direction[1] != -1:
                snake2.direction = [0, 1]
            elif event.key == K_LEFT and snake2.direction[0] != 1:
                snake2.direction = [-1, 0]
            elif event.key == K_RIGHT and snake2.direction[0] != -1:
                snake2.direction = [1, 0]
            # Fart controls
            elif event.key == K_e:  # Green snake farts with 'E' key
                if len(snake1.body) > 1:
                    fart_pos = snake1.body[-1]
                    for _ in range(3):  # Create multiple fart effects
                        effect = FartEffect(fart_pos[0], fart_pos[1])
                        effect.radius = random.randint(1, 3)
                        snake1.fart_effects.append(effect)
            elif event.key == K_1 or event.key == K_KP1:  # Blue snake farts with '1' key
                if len(snake2.body) > 1:
                    fart_pos = snake2.body[-1]
                    for _ in range(3):  # Create multiple fart effects
                        effect = FartEffect(fart_pos[0], fart_pos[1])
                        effect.radius = random.randint(1, 3)
                        snake2.fart_effects.append(effect)
            elif event.key == K_g:
                snake1.god_mode = not snake1.god_mode
                snake2.god_mode = not snake2.god_mode
            elif event.key == K_h: #toggle help menu
                game_paused = not game_paused


    # Draw everything
    screen.fill(BLACK)
    draw_background()

    # Check for help menu
    show_help = pygame.key.get_pressed()[K_h]

    if not game_paused and not game_over and countdown_timer <= 0:
        # Update turrets
        for turret in turrets:
            turret.update()
            turret.shoot(snake1, snake2)

        # Move snakes
        if snake1.move() or snake2.move():
            game_over = True

        # Update power-ups
        for snake in [snake1, snake2]:
            if snake.shield > 0:
                snake.shield -= 1
            if snake.speed_boost > 0:
                snake.speed_boost -= 1
            if snake.poop_eater > 0:
                snake.poop_eater -= 1

        # Check power-up collision
        if power_up:
            for snake in [snake1, snake2]:
                if snake.body[0] == (power_up.x, power_up.y):
                    # Add collection effects
                    if power_up.type == SHIELD:
                        snake.shield = 100
                        # Add shield effect
                        for i in range(8):
                            angle = i * math.pi / 4
                            effect = FartEffect(snake.body[0][0] + math.cos(angle), snake.body[0][1] + math.sin(angle))
                            effect.radius = 2
                            effect.lifetime = 15
                            snake.fart_effects.append(effect)
                    elif power_up.type == SPEED:
                        snake.speed_boost = 100
                        # Add speed effect
                        for i in range(5):
                            effect = FartEffect(snake.body[0][0] - i, snake.body[0][1])
                            effect.radius = 1
                            effect.lifetime = 10
                            snake.fart_effects.append(effect)
                    elif power_up.type == POOP_EATER:
                        snake.poop_eater = 100
                        # Add poop eater effect
                        for i in range(4):
                            effect = FartEffect(snake.body[0][0], snake.body[0][1])
                            effect.radius = 3
                            effect.lifetime = 20
                            snake.fart_effects.append(effect)
                    elif power_up.type == TURRET:
                        if not snake.extra_turret:
                            snake.extra_turret = Turret(power_up.x, power_up.y)
                            turrets.append(snake.extra_turret)
                            # Add turret effect
                            for i in range(6):
                                angle = i * math.pi / 3
                                effect = FartEffect(power_up.x + math.cos(angle), power_up.y + math.sin(angle))
                                effect.radius = 2
                                effect.lifetime = 15
                                snake.fart_effects.append(effect)
                    power_up = spawn_power_up()

        # Check food collision
        if snake1.body[0] == food:
            snake1.grow = True
            snake1.score += 1
            snake1.apples_eaten += 1
            apples_eaten_this_level += 1
            food = spawn_food()
        if snake2.body[0] == food:
            snake2.grow = True
            snake2.score += 1
            snake2.apples_eaten += 1
            apples_eaten_this_level += 1
            food = spawn_food()

        # Check if level complete
        if apples_eaten_this_level >= 4:
            next_level()

        # Update poop monsters
        for monster in poop_monsters:
            monster.move()
            # Check if monster caught a snake
            monster_x = int(monster.x)
            monster_y = int(monster.y)
            if (monster_x, monster_y) in snake1.body or (monster_x, monster_y) in snake2.body:
                if not snake1.god_mode and not snake2.god_mode:
                    game_over = True

        # Check collisions
        if (snake1.check_collision(snake2, [t for t in turrets if t != snake1.extra_turret]) or 
            snake2.check_collision(snake1, [t for t in turrets if t != snake2.extra_turret])):
            game_over = True

    # Draw everything
    screen.fill(BLACK)
    draw_background()

    # Draw walls
    pygame.draw.rect(screen, DARK_RED, (0, 0, WINDOW_SIZE, GRID_SIZE))  # Top
    pygame.draw.rect(screen, DARK_RED, (0, WINDOW_SIZE-GRID_SIZE, WINDOW_SIZE, GRID_SIZE))  # Bottom
    pygame.draw.rect(screen, DARK_RED, (0, 0, GRID_SIZE, WINDOW_SIZE))  # Left
    pygame.draw.rect(screen, DARK_RED, (WINDOW_SIZE-GRID_SIZE, 0, GRID_SIZE, WINDOW_SIZE))  # Right

    # Draw poop spots and stink effects
    for snake in [snake1, snake2]:
        for poop in snake.poop_spots:
            # Draw poop
            pygame.draw.rect(screen, BROWN, (poop.x * GRID_SIZE, poop.y * GRID_SIZE,
                                         GRID_SIZE - 1, GRID_SIZE - 1))
            # Draw stink waves
            if poop.stink_timer > 0:
                for i in range(3):
                    radius = (20 - poop.stink_timer + i * 5) * 2
                    pygame.draw.circle(screen, (139, 69, 19, 50), 
                                     (poop.x * GRID_SIZE + GRID_SIZE//2, 
                                      poop.y * GRID_SIZE + GRID_SIZE//2), 
                                     radius, 1)
                poop.stink_timer -= 1

        # Draw fart effects
        for fart in snake.fart_effects[:]:
            if fart.lifetime > 0:
                pygame.draw.circle(screen, (0, 255, 0, 50),
                                 (fart.x * GRID_SIZE + GRID_SIZE//2,
                                  fart.y * GRID_SIZE + GRID_SIZE//2),
                                 fart.radius * 3, 1)
                fart.lifetime -= 1
                fart.radius += 0.5
            else:
                snake.fart_effects.remove(fart)

    # Draw turrets and bullets
    for turret in turrets:
        pygame.draw.rect(screen, PURPLE, (turret.x * GRID_SIZE, turret.y * GRID_SIZE,
                                        GRID_SIZE - 1, GRID_SIZE - 1))
        for bullet in turret.bullets:
            pygame.draw.rect(screen, YELLOW, (bullet[0] * GRID_SIZE, bullet[1] * GRID_SIZE,
                                            GRID_SIZE/2, GRID_SIZE/2))

    # Draw food
    pygame.draw.rect(screen, RED, (food[0] * GRID_SIZE, food[1] * GRID_SIZE,
                                 GRID_SIZE - 1, GRID_SIZE - 1))

    # Draw Power-up with animation
    if power_up:
        # Calculate floating animation
        float_offset = math.sin(pygame.time.get_ticks() * 0.005) * 5
        power_up_y = power_up.y * GRID_SIZE + float_offset

        if power_up.type == SHIELD:
            pygame.draw.circle(screen, (0, 0, 255), (power_up.x * GRID_SIZE + GRID_SIZE // 2, power_up_y + GRID_SIZE // 2), GRID_SIZE // 2)
            # Add shield glow
            glow_size = math.sin(pygame.time.get_ticks() * 0.01) * 3 + 3
            pygame.draw.circle(screen, (100, 100, 255), (power_up.x * GRID_SIZE + GRID_SIZE // 2, power_up_y + GRID_SIZE // 2), GRID_SIZE // 2 + glow_size, 2)
        elif power_up.type == SPEED:
            pygame.draw.rect(screen, (255, 255, 0), (power_up.x * GRID_SIZE, power_up_y, GRID_SIZE, GRID_SIZE))
            # Add speed lines
            for i in range(3):
                offset = math.sin(pygame.time.get_ticks() * 0.01 + i) * 5
                pygame.draw.line(screen, (255, 255, 100), 
                               (power_up.x * GRID_SIZE - offset, power_up_y),
                               (power_up.x * GRID_SIZE - offset - 5, power_up_y + GRID_SIZE), 2)
        elif power_up.type == POOP_EATER:
            pygame.draw.circle(screen, (139, 69, 19), (power_up.x * GRID_SIZE + GRID_SIZE // 2, power_up_y + GRID_SIZE // 2), GRID_SIZE // 2)
            # Add stink waves
            for i in range(2):
                wave_size = math.sin(pygame.time.get_ticks() * 0.01 + i * math.pi) * 5 + 10
                pygame.draw.circle(screen, (139, 69, 19), (power_up.x * GRID_SIZE + GRID_SIZE // 2, power_up_y + GRID_SIZE // 2), GRID_SIZE // 2 + wave_size, 1)
        elif power_up.type == TURRET:
            pygame.draw.rect(screen, (128, 0, 128), (power_up.x * GRID_SIZE, power_up_y, GRID_SIZE, GRID_SIZE))
            # Add rotating turret animation
            angle = pygame.time.get_ticks() * 0.01
            end_x = power_up.x * GRID_SIZE + GRID_SIZE//2 + math.cos(angle) * GRID_SIZE//2
            end_y = power_up_y + GRID_SIZE//2 + math.sin(angle) * GRID_SIZE//2
            pygame.draw.line(screen, (200, 0, 200),
                           (power_up.x * GRID_SIZE + GRID_SIZE//2, power_up_y + GRID_SIZE//2),
                           (end_x, end_y), 3)


    # Draw snakes
    for segment in snake1.body:
        pygame.draw.rect(screen, snake1.color,
                        (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE,
                         GRID_SIZE - 1, GRID_SIZE - 1))
    for segment in snake2.body:
        pygame.draw.rect(screen, snake2.color,
                        (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE,
                         GRID_SIZE - 1, GRID_SIZE - 1))

    # Draw poop monsters
    for monster in poop_monsters:
        pygame.draw.rect(screen, BROWN, 
                        (int(monster.x * GRID_SIZE), int(monster.y * GRID_SIZE),
                         GRID_SIZE - 1, GRID_SIZE - 1))
        # Draw monster eyes
        eye_color = RED
        eye_size = GRID_SIZE // 4
        pygame.draw.rect(screen, eye_color,
                        (int(monster.x * GRID_SIZE) + eye_size,
                         int(monster.y * GRID_SIZE) + eye_size,
                         eye_size, eye_size))
        pygame.draw.rect(screen, eye_color,
                        (int(monster.x * GRID_SIZE) + GRID_SIZE - 2*eye_size,
                         int(monster.y * GRID_SIZE) + eye_size,
                         eye_size, eye_size))

    # Draw scores and level
    draw_scores()
    font = pygame.font.Font(None, 36)
    level_text = font.render(f'Level: {current_level}', True, WHITE)
    screen.blit(level_text, (WINDOW_SIZE // 2 - 50, 10))

    # Draw god mode status
    if snake1.god_mode or snake2.god_mode:
        god_text = font.render('GOD MODE: ON', True, YELLOW)
        screen.blit(god_text, (WINDOW_SIZE // 2 - 70, 40))

    # Draw countdown
    if countdown_timer > 0:
        countdown_font = pygame.font.Font(None, 74)
        countdown_text = countdown_font.render(str((countdown_timer // 30) + 1), True, WHITE)
        screen.blit(countdown_text, (WINDOW_SIZE // 2 - 20, WINDOW_SIZE // 2 - 50))
        countdown_timer -= 1

    if game_over:
        font = pygame.font.Font(None, 74)
        text = font.render('Game Over!', True, RED)
        restart_text = font.render('Press R to Restart', True, WHITE)
        screen.blit(text, (WINDOW_SIZE // 4, WINDOW_SIZE // 2))
        screen.blit(restart_text, (WINDOW_SIZE // 4, WINDOW_SIZE // 2 + 80))

    # Draw help menu if H is pressed
    if show_help or game_paused:
        # Semi-transparent background
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(230)  # Increased darkness to 90%
        screen.blit(overlay, (0, 0))

        help_surface = pygame.Surface((WINDOW_SIZE - 100, WINDOW_SIZE - 100))
        help_surface.fill((50, 50, 50))
        help_font = pygame.font.Font(None, 32)

        help_texts = [
            "Power-ups Guide:",
            "Blue Shield: Temporary invincibility",
            "Yellow Lightning: Speed boost",
            "Brown Circle: Eat poop without dying",
            "Purple Square: Place your own turret",
            "",
            "Controls:",
            "Player 1: WASD + E(fart)",
            "Player 2: Arrows + 1(fart)",
            "G: Toggle God Mode",
            "H: Show/Hide Help"
        ]

        y_offset = 20
        for text in help_texts:
            text_surface = help_font.render(text, True, WHITE)
            help_surface.blit(text_surface, (20, y_offset))
            y_offset += 40

        screen.blit(help_surface, (50, 50))

    pygame.display.flip()
    clock.tick(10)
