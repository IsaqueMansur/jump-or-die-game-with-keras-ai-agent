import pygame
import random
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
import threading
import time

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pula ou morre")

font = pygame.font.Font(None, 36)

class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = 100
        self.y = SCREEN_HEIGHT - self.height - 10
        self.velocity = 10
        self.is_jumping = False
        self.jump_height = 150
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.on_ground = True 

    def jump(self):
        if self.on_ground:
            self.is_jumping = True
            self.jump_peak = self.y - self.jump_height
            self.on_ground = False

    def update(self):
        if self.is_jumping:
            if self.y > self.jump_peak:
                self.y -= self.velocity
            else:
                self.is_jumping = False
        elif self.y < SCREEN_HEIGHT - self.height - 10:
            self.y += self.velocity
        else:
            self.on_ground = True
            self.y = SCREEN_HEIGHT - self.height - 10

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        pygame.draw.rect(screen, (0, 255, 0), self.rect)


class Obstacle:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = SCREEN_WIDTH
        self.y = SCREEN_HEIGHT - self.height - 10
        self.velocity = random.randint(6, 10)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.passed_player = False

    def update(self):
        self.x -= self.velocity
        if self.x < -self.width:
            self.reset()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def reset(self):
        self.x = SCREEN_WIDTH
        self.velocity = random.randint(6, 12)
        self.passed_player = False

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)
        
class Coin:
    def __init__(self):
        self.width = 20
        self.height = 20
        self.x = SCREEN_WIDTH
        self.y = SCREEN_HEIGHT - self.height - 100
        self.velocity = random.randint(9, 25)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.passed_player = False

    def update(self):
        self.x -= self.velocity
        if self.x <= 0:
            self.reset()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def reset(self):
        self.x = SCREEN_WIDTH
        self.velocity = random.randint(9, 25)
        self.passed_player = False

    def draw(self):
        pygame.draw.rect(screen, (255, 255, 0), self.rect)


class Game:
    def __init__(self, model_path):
        self.obstacle = Obstacle()
        self.player = Player()
        self.coin = Coin()
        self.score = 0
        self.coins = 0
        self.errors = 0
        self.done = False
        self.penalty_collision = -5
        self.model = load_model(model_path, custom_objects={'mse': MeanSquaredError()})
        self.action = 0
        self.lock = threading.Lock()
        self.model_thread = threading.Thread(target=self.predict_action_loop, daemon=True)
        self.model_thread.start()
        self.interval_to_action = 1
        self.current_frame = 0
        self.fps = 100
        self.cpu_sleep = 0.0001

    def show_text(self, text, x, y, color=(255, 255, 255)):
        render = font.render(text, True, color)
        screen.blit(render, (x, y))

    def reset(self):
        self.score = 0
        self.errors = 0
        self.player.y = SCREEN_HEIGHT - self.player.height - 10
        self.obstacle.reset()

    def check_collision(self):
        if self.player.rect.colliderect(self.obstacle.rect):
            self.errors += 1  # Incrementa o contador de erros
            self.obstacle.reset()
            return self.penalty_collision
        return 0
    
    def check_capture_coin(self):
        if self.player.rect.colliderect(self.coin.rect) and not self.coin.passed_player:
            self.coins += 1
            self.coin.reset()
            return 20
        return 0

    def check_pass(self):
        if (self.obstacle.x + self.obstacle.width) < self.player.x:
            self.score += 1
            self.obstacle.passed_player = True
            self.obstacle.reset()
            return 20
        return 0

    def get_state(self):
        return np.array([
            self.obstacle.x / SCREEN_WIDTH,
            self.obstacle.velocity / 12,
            int(self.player.on_ground),
            (self.player.y - self.obstacle.y) / SCREEN_HEIGHT
        ]).reshape(1, 4)

    def predict_action_loop(self):
        while True:
            state = self.get_state()
            action = self.model.predict(state)
            with self.lock:
                self.action = np.argmax(action[0]) 
            time.sleep(self.cpu_sleep) 

    def run(self):
        running = True
        while running:
            reward = 0
            action = 0
            self.current_frame += 1
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Obtém a ação prevista
            if self.current_frame % self.interval_to_action == 0:
                self.current_frame = 0
                with self.lock:
                    action = self.action

            # Se a ação for pular (1), faz o jogador pular
            if action == 1 and not self.player.is_jumping:
                self.player.jump()

            # Atualizar jogador e obstáculo
            self.player.update()
            self.obstacle.update()
            self.coin.update()

            # Checar colisão e recompensa por passar obstáculo
            reward += self.check_capture_coin()
            reward += self.check_collision()
            reward += self.check_pass()

            # Desenhar elementos do jogo
            self.player.draw()
            self.obstacle.draw()
            self.coin.draw()
            if self.score:
                self.show_text(f"Acertos: {self.score} | ({(100 - ((self.errors * 100) / (self.score + self.errors))):.2f}%)", 10, 10)
                self.show_text(f"Erros: {self.errors} | ({((self.errors * 100) / (self.score + self.errors)):.2f}%)", 10, 50, color=(255, 0, 0))
            if self.coins:
                self.show_text(f"Moedas: {self.coins}", 10, 30, color=(255, 255, 0))


            pygame.display.flip()
            pygame.time.Clock().tick(self.fps)

        pygame.quit()


if __name__ == "__main__":
    model_path = "E:/repositories/jump-or-die-game-with-keras-ai-agent/models-ok/low-rewards-done-per-batch-size-low-gamma5.h5"
    game = Game(model_path)
    game.run()
