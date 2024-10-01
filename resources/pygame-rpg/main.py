import pygame
from pygame.locals import *
import sys
import random

# Constants
WIDTH, HEIGHT = 700, 350
ACC, FRIC = 0.3, -0.10
FPS = 60
PLAYER_POS = (340, 240)
GROUND_POS = (350, 350)
ENEMY_POS_Y = 235
ENEMY_VEL_RANGE = (2, 6)
ENEMY_GEN_INTERVAL = 2000
HIT_COOLDOWN_TIME = 1000

# Initialize Pygame
pygame.init()
vec = pygame.math.Vector2
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
FPS_CLOCK = pygame.time.Clock()

dialogue_font = pygame.font.SysFont("arial", 15)
name_font = pygame.font.SysFont("Helvetica", 20)
game_over_font = pygame.font.SysFont("Verdana", 60)
headingfont = pygame.font.SysFont("arial", 30)
color_dark = (100, 100, 100)


# Load images once
def load_images(prefix, count):
    return [pygame.image.load(f"assets/{prefix}{i}.png") for i in range(1, count + 1)]


run_ani_R = load_images("Player_Sprite_R", 6) + [
    pygame.image.load("assets/Player_Sprite_R1.png")
]
run_ani_L = load_images("Player_Sprite_L", 6) + [
    pygame.image.load("assets/Player_Sprite_L1.png")
]
attack_ani_R = (
    [pygame.image.load("assets/Player_Sprite_R1.png")]
    + load_images("Player_Attack_R", 5) * 2
    + [pygame.image.load("assets/Player_Sprite_R1.png")]
)
attack_ani_L = (
    [pygame.image.load("assets/Player_Sprite_L1.png")]
    + load_images("Player_Attack_L", 5) * 2
    + [pygame.image.load("assets/Player_Sprite_L1.png")]
)

health_ani = [
    pygame.image.load("assets/heart0.png"),
    pygame.image.load("assets/heart.png"),
    pygame.image.load("assets/heart2.png"),
    pygame.image.load("assets/heart3.png"),
    pygame.image.load("assets/heart4.png"),
    pygame.image.load("assets/heart5.png"),
]


class StageDisplay(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.text = headingfont.render("STAGE: " + str(handler.stage), True, color_dark)
        self.rect = self.text.get_rect()
        self.posx = -100
        self.posy = 100
        self.display = False

    def move_display(self):
        # Create the text to be displayed
        self.text = headingfont.render("STAGE: " + str(handler.stage), True, color_dark)
        if self.posx < 700:
            self.posx += 5
            displaysurface.blit(self.text, (self.posx, self.posy))
        else:
            self.display = False
            self.kill()


class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.bgimage = pygame.image.load("assets/Background.png")
        self.bgX, self.bgY = 0, 0

    def render(self):
        displaysurface.blit(self.bgimage, (self.bgX, self.bgY))


class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/Ground.png")
        self.rect = self.image.get_rect(center=GROUND_POS)

    def render(self):
        displaysurface.blit(self.image, (self.rect.x, self.rect.y))


class HealthBar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/heart5.png")

    def render(self):
        displaysurface.blit(self.image, (10, 10))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/Player_Sprite_R1.png")
        self.rect = self.image.get_rect()
        self.pos = vec(PLAYER_POS)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.direction = "RIGHT"
        self.jumping = self.running = self.attacking = self.cooldown = False
        self.move_frame = self.attack_frame = 0
        self.health = 5

    def player_hit(self):
        if self.cooldown is False:
            self.cooldown = True  # Enable the cooldown
            pygame.time.set_timer(hit_cooldown, 1000)  # Resets cooldown in 1 second

            self.health = self.health - 1
            health.image = health_ani[self.health]

            if self.health <= 0:
                self.kill()
                pygame.display.update()

    def gravity_check(self):
        hits = pygame.sprite.spritecollide(self, ground_group, False)
        if self.vel.y > 0 and hits:
            lowest = hits[0]
            if self.pos.y < lowest.rect.bottom:
                self.pos.y = lowest.rect.top + 1
                self.vel.y = 0
                self.jumping = False

    def move(self):
        self.acc = vec(0, 0.5)
        self.running = abs(self.vel.x) > 0.3
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        self.rect.midbottom = self.pos

    def update(self):
        if self.move_frame > 6:
            self.move_frame = 0
            return
        if not self.jumping and self.running:
            self.image = (
                run_ani_R[self.move_frame]
                if self.vel.x > 0
                else run_ani_L[self.move_frame]
            )
            self.direction = "RIGHT" if self.vel.x > 0 else "LEFT"
            self.move_frame += 1
        if abs(self.vel.x) < 0.2 and self.move_frame != 0:
            self.move_frame = 0
            self.image = (
                run_ani_R[self.move_frame]
                if self.direction == "RIGHT"
                else run_ani_L[self.move_frame]
            )

    def correction(self):
        if self.attack_frame == 1:
            self.pos.x -= 20
        if self.attack_frame == 10:
            self.pos.x += 20

    def attack(self):
        if self.attack_frame > 10:
            self.attack_frame = 0
            self.attacking = False
        self.image = (
            attack_ani_R[self.attack_frame]
            if self.direction == "RIGHT"
            else attack_ani_L[self.attack_frame]
        )
        if self.direction == "LEFT":
            self.correction()
        self.attack_frame += 1

    def jump(self):
        self.rect.x += 1
        hits = pygame.sprite.spritecollide(self, ground_group, False)
        self.rect.x -= 1
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -12


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/Enemy.png")
        self.rect = self.image.get_rect()
        self.pos = vec(0, ENEMY_POS_Y)
        self.vel = vec(random.randint(*ENEMY_VEL_RANGE) / 2, 0)
        self.direction = random.randint(0, 1)
        self.pos.x = 0 if self.direction == 0 else WIDTH

    def move(self):
        if self.pos.x >= (WIDTH - 20):
            self.direction = 1
        elif self.pos.x <= 0:
            self.direction = 0
        self.pos.x += self.vel.x if self.direction == 0 else -self.vel.x
        self.rect.center = self.pos

    def render(self):
        displaysurface.blit(self.image, (self.pos.x, self.pos.y))

    def update(self):
        hits = pygame.sprite.spritecollide(self, Playergroup, False)
        if hits and player.attacking:
            self.kill()
            print("Enemy killed")
        elif hits and not player.attacking:
            player.player_hit()


class Castle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.hide = False
        self.image = pygame.image.load("assets/castle.png")

    def update(self):
        if not self.hide:
            displaysurface.blit(self.image, (400, 80))


class EventHandler:
    def __init__(self):
        self.stage = self.enemy_count = 0
        self.battle = False
        self.enemy_generation = pygame.USEREVENT + 1
        self.stage_enemies = [int((x**2 / 2) + 1) for x in range(1, 21)]
        print(self.enemy_count)

    def next_stage(self):
        self.stage += 1
        self.enemy_count = 0
        print("Stage: " + str(self.stage))
        pygame.time.set_timer(self.enemy_generation, 1500 - (50 * self.stage))

    def stage_handler(self):
        self.world1()

    def world1(self):
        pygame.time.set_timer(self.enemy_generation, ENEMY_GEN_INTERVAL)
        castle.hide = True
        self.battle = True


health = HealthBar()
background = Background()
ground = Ground()
ground_group = pygame.sprite.Group(ground)
castle = Castle()
handler = EventHandler()
stage_display = StageDisplay()
player = Player()
Playergroup = pygame.sprite.Group(player)
Enemies = pygame.sprite.Group()

while True:
    hit_cooldown = pygame.USEREVENT + 1
    player.gravity_check()
    for event in pygame.event.get():
        if event.type == handler.enemy_generation:
            if handler.enemy_count < handler.stage_enemies[handler.stage - 1]:
                enemy = Enemy()
                Enemies.add(enemy)
                handler.enemy_count += 1
        if event.type == hit_cooldown:
            player.cooldown = False
            pygame.time.set_timer(hit_cooldown, 0)
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                if handler.battle is True and len(Enemies) == 0:
                    handler.next_stage()
                    stage_display = StageDisplay()
                    stage_display.display = True
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_RETURN and not player.attacking:
                player.attack()
                player.attacking = True
            if event.key == pygame.K_e and 450 < player.rect.x < 550:
                handler.stage_handler()

    # Render stage display
    if stage_display.display is True:
        stage_display.move_display()
    player.update()
    if player.attacking:
        player.attack()
    player.move()
    background.render()
    ground.render()
    castle.update()
    if player.health > 0:
        displaysurface.blit(player.image, player.rect)
    health.render()
    for entity in Enemies:
        entity.update()
        entity.move()
        entity.render()

    pygame.display.update()
    FPS_CLOCK.tick(FPS)
