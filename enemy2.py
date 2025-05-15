import pygame
import random

class Enemy2(pygame.sprite.Sprite):
    def __init__(self, screen_width, speed_up=False):
        super().__init__()
        self.image = pygame.image.load("assets/images/enemy2.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = 2.5 if speed_up else 2
        #speed_upがTrueなら、self.speedに2.5が代入でもしspeed_upがFalseなら、self.speedに2が代入

    def update(self):
        self.rect.y += self.speed
        return self.rect.top > 600



