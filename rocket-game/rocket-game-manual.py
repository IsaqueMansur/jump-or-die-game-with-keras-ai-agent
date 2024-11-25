import pygame
import os

class Rocket:
    def __init__(self, x, y, width, height, image_path):
        
        self.width = width
        self.height = height
        self.image = pygame.transform.scale(pygame.image.load(image_path), (self.width, self.height))
        self.x = x
        self.y = y
        
        self.DEFAULT_SPEED = 0.05
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

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.thrust = True
            if event.key == pygame.K_a:
                self.move_left = True
            if event.key == pygame.K_d:
                self.move_right = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self.thrust = False
            if event.key == pygame.K_a:
                self.move_left = False
            if event.key == pygame.K_d:
                self.move_right = False

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
        if self.move_left:
            self.x -= self.speed
            self.noise_angle -= 0.5
            if self.noise_angle == 0:
                self.noise_angle = 359.5
                
        if self.move_right:
            self.x += self.speed
            self.noise_angle += 0.5
            if self.noise_angle == 360:
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

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Game:
    def __init__(self):
        pygame.init()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1000, 750
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.running = True

        rocket_image_path = os.path.join('F:/repositories/minigame-python/rocket-game/rocket.png')
        rocket_x = self.SCREEN_WIDTH // 2 - 25 
        rocket_y = self.SCREEN_HEIGHT - 47
        self.rocket = Rocket(rocket_x, rocket_y, 35, 47, rocket_image_path)

    def run(self):
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    else:
                        self.rocket.handle_input(event)

                self.rocket.update(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

                self.screen.fill(self.BLACK)
                self.rocket.draw(self.screen)
                pygame.display.update()
                self.clock.tick(self.FPS)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
