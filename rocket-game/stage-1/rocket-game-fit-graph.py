import pygame
import random
import numpy as np
from collections import deque
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import os

class DQNAgent:
    def __init__(self): 
        self.model = Sequential([
            Dense(32, activation='relu', input_shape=(7,)),
            Dense(32, activation='relu'),
            Dense(64, activation='relu'),
            Dense(3, activation='linear')
        ])
        self.model.compile(optimizer='adam', loss='mse')
        self.memory = deque(maxlen=2000)
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.99
        self.gamma = 0.95
        self.model_name = f"rocket-model-gm--{self.gamma}-mem--{self.memory.maxlen}--32-32-64"
        
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        
    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randint(0, 2)
        q_values = self.model.predict(np.array([state]), verbose=0)
        return np.argmax(q_values[0])
    
    def replay(self, batch_size=32):
        if len(self.memory) < batch_size:
            return
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target += self.gamma * np.amax(self.model.predict(np.array([next_state]), verbose=0)[0])
            target_f = self.model.predict(np.array([state]), verbose=0)
            target_f[0][action] = target
            self.model.fit(np.array([state]), target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        print(f"Epsilon: {self.epsilon}")
        
    def save_model(self):
        current_path = os.path.abspath(os.path.dirname(__file__))
        self.model.save(f"{current_path}/{self.model_name}.h5")



class Target:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (0, 255, 0) 

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        
    def calculate_distance_to_rocket(self, rocket_rect):
        return abs(self.rect.centerx - rocket_rect.centerx) + abs(self.rect.centery - rocket_rect.centery)
        

class Rocket:
    def __init__(self, x, y, width, height):
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.original_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.original_image.fill((255, 0, 0)) 
        self.image = self.original_image

        self.rocket_rect = self.image.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        
        self.DEFAULT_SPEED = 1
        self.SPEED_UP = 1.02
        self.GRAVITY_DOWN = 1.05
        self.MAX_SPEED = 5
        self.GRAVITY_DESACELARATION = 0.965
        self.MAX_GRAVITY_DOWN_SPEED = 2.3
        
        self.speed = 0.7
        self.started_thrust_on_down = False
        self.win_gravity_down = False
        self.request_deceleration = False
        self.start_deceleration = False
        self.move_left = False
        self.move_right = False
        self.thrust = False
        self.started_thrust = False
        self.noise_angle = 0 

    def handle_input(self, action):
            if action == 0:
                self.thrust = not self.thrust
                self.move_right = False
                self.move_left = False
            if action == 1:
                self.move_left = True
                self.move_right = False
            if action == 2:
                self.move_right = True
                self.move_left = False

    def handle_gravity_down(self, screen_height):
        if self.y < (screen_height - self.height) and not self.thrust and not self.started_thrust_on_down and not self.request_deceleration:
            if not self.start_deceleration:
                self.request_deceleration = True
            else:
                self.win_gravity_down = False
                self.started_thrust = False
                self.y += self.speed
                if self.speed < self.MAX_SPEED:
                    self.speed *= self.GRAVITY_DOWN

    def handle_thrust(self):
        if self.thrust and not self.started_thrust_on_down:
            if not self.win_gravity_down:
                self.request_deceleration = False
                self.start_deceleration = False
                self.started_thrust_on_down = True
            self.started_thrust = True
            self.y -= self.speed
            if self.speed < self.MAX_SPEED:
                self.speed *= self.SPEED_UP

    def handle_deceleration(self):
        if self.request_deceleration:
            if self.speed > self.DEFAULT_SPEED:
                self.speed *= self.GRAVITY_DESACELARATION
                self.y -= self.speed
            else:
                self.request_deceleration = False
                self.start_deceleration = True

    def handle_thrust_on_down(self):
        if self.started_thrust_on_down:
            if self.speed > self.DEFAULT_SPEED:
                self.speed *= self.GRAVITY_DESACELARATION
                self.y += self.speed
            else:
                self.started_thrust_on_down = False
                self.win_gravity_down = True

    def handle_horizontal_movement(self):
        angle_limit = 35
        if self.move_left:
            self.noise_angle -= 0.3
            if self.noise_angle < -angle_limit:
                self.noise_angle = -angle_limit 
            
        elif self.move_right:
            self.noise_angle += 0.3
            if self.noise_angle > angle_limit:
                self.noise_angle = angle_limit 
                
        if self.noise_angle > 0:
            self.x += (abs(self.noise_angle) / self.MAX_SPEED) 
        elif self.noise_angle < 0:
            self.x -= (abs(self.noise_angle) / self.MAX_SPEED)     
             
        if not self.move_left and not self.move_right:
            if self.noise_angle > 0:
                self.noise_angle -= 0.2
                if self.noise_angle < 0:
                    self.noise_angle = 0
            elif self.noise_angle < 0:
                self.noise_angle += 0.2
                if self.noise_angle > 0:
                    self.noise_angle = 0

    def handle_boundary_conditions(self, screen_width, screen_height):
        if self.x < 0:
            self.x = 0
        elif self.x > screen_width - self.width:
            self.x = screen_width - self.width
        if self.y < 0:
            self.y = 0
        elif self.y > screen_height - self.height:
            self.y = screen_height - self.height

    def reset_speed_on_ground(self, screen_height):
        if self.y == (screen_height - self.height):
            self.speed = self.DEFAULT_SPEED
            self.started_thrust_on_down = False
            self.win_gravity_down = False
            self.request_deceleration = False

    def update(self, screen_width, screen_height):
        self.reset_speed_on_ground(screen_height)
        self.handle_deceleration()
        self.handle_gravity_down(screen_height)
        self.handle_thrust_on_down()
        self.handle_thrust()
        self.handle_horizontal_movement()
        self.handle_boundary_conditions(screen_width, screen_height)

        self.rocket_rect.center = (self.x + self.width // 2, self.y + self.height // 2)

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.original_image, -self.noise_angle)
        new_rect = rotated_image.get_rect(center=self.rocket_rect.center)
        screen.blit(rotated_image, new_rect.topleft)

class Game:
    def __init__(self):
        pygame.init()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1000, 750
        
        # Inicialização da tela e componentes gráficos
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Foguetão")
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.clock = pygame.time.Clock()
        self.FPS = 20
        self.running = True

        rocket_x = self.SCREEN_WIDTH // 2 - 25 
        rocket_y = self.SCREEN_HEIGHT - 47
        
        target_x = random.randint(30, self.SCREEN_WIDTH - 30)
        target_y = random.randint(30, self.SCREEN_HEIGHT - 30)
        
        self.rocket = Rocket(rocket_x, rocket_y, 30, 47)
        self.target = Target(target_x, target_y, 10, 10)
        
        self.agent = DQNAgent()
        self.ACTIONS_NUMBER_TO_CALLBACK_FIT = 300
    
    def reset_rocket(self):
        self.rocket = Rocket(self.SCREEN_WIDTH // 2 - 25, self.SCREEN_HEIGHT - 47, 30, 47)
        self.target = Target(random.randint(30, self.SCREEN_WIDTH - 30), random.randint(30, self.SCREEN_HEIGHT - 30), 10, 10)
        

    def run(self):
        action_number = 0
        try:
            while self.running:
                # Loop de eventos para manter a janela responsiva
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                action_number += 1
                state = self.get_state()
                action = self.agent.act(state)
                distance_to_target = self.target.calculate_distance_to_rocket(self.rocket.rocket_rect)
                reward = (2000 - distance_to_target) / 100
                self.rocket.handle_input(action)
                
                self.rocket.update(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
                
                new_distance_to_target = self.target.calculate_distance_to_rocket(self.rocket.rocket_rect)
                if new_distance_to_target > distance_to_target:
                    reward -=1
                else:
                    reward += (distance_to_target - new_distance_to_target) / 100

                # Código de desenho
                self.screen.fill(self.BLACK)
                self.rocket.draw(self.screen)
                self.target.draw(self.screen)
                pygame.display.update()
                self.clock.tick(self.FPS)
                
                next_state = self.get_state()
                done = new_distance_to_target == 0
                if done:
                    reward += 100
                    print(f"Episódio encerrado! Distância final: {new_distance_to_target}")
                    self.reset_rocket()
                    
                reward = max(reward, -10)
                
                self.agent.remember(state, action, reward, next_state, done)

                if action_number % self.ACTIONS_NUMBER_TO_CALLBACK_FIT == 0:
                    self.agent.replay()
                    print(f"Distância: {distance_to_target}")
                    print(f"Recomepnsa atual: {reward}")
                    
                if action_number % 3000 == 0:
                    self.agent.save_model()
                
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        finally:
            pygame.quit()
            
    def get_state(self):
        rocket_distance_to_target = self.target.calculate_distance_to_rocket(self.rocket.rocket_rect)
        return np.array(
            [
                rocket_distance_to_target / 2000, 
                self.rocket.noise_angle / 35, 
                self.rocket.x / self.SCREEN_WIDTH,
                self.rocket.y / self.SCREEN_HEIGHT,
                int(self.rocket.thrust),
                int(self.rocket.start_deceleration),
                int(self.rocket.started_thrust_on_down)
            ])

if __name__ == "__main__":
    game = Game()
    game.run()
