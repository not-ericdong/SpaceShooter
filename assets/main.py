from PIL import Image, ImageDraw
import random
import os
import time
import pygame

# pygame setup
pygame.font.init()
WIDTH, HEIGHT = 600, 900
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("APOLLO ADVENTURE")

# background generator
assets = os.path.dirname(__file__)
bg_filename = os.path.join(assets, 'background.jpg')


def create_background():
    space = Image.new("RGB", (WIDTH, HEIGHT+10), "black")
    d = ImageDraw.Draw(space)

    star_number = random.randrange(100, 260, 10)
    colour_list = ["#4291E5", "#70ABE9", "#B8D3EF",
                   "#FEF8EC", "#FDE4B2", "#E9C57D", "#F5AC1B"]

    # stars can be though of as 5 squares of equal size organized into a cross
    # offset is how far away from origin (top left corner)
    for x in range(star_number):
        offsetx = random.randrange(0, WIDTH)
        offsety = random.randrange(0, HEIGHT)
        colour = random.choices(colour_list, weights=(3, 3, 5, 3, 2, 2, 6))[0]
        # more accurate weight distribution: weights=(0.0000003, 0.0013, 0.006, 0.03, 0.076, 0.121, 0.7645)
        size = random.randrange(1, 3)

        if space.getpixel((offsetx, offsety)) is not (0, 0, 0):
            star_x = d.rectangle([offsetx, size + offsety,
                                  3 * size + offsetx, 2 * size + offsety], fill=colour)
            star_y = d.rectangle([size + offsetx, offsety,
                                  2 * size + offsetx, 3 * size + offsety], fill=colour)
    space.save(bg_filename)
create_background()

# Load the images
SPACESHIP = pygame.image.load(os.path.join(assets, "spaceship_s.png"))
UFO1 = pygame.image.load(os.path.join(assets, "ufo_blue.png"))
UFO2 = pygame.image.load(os.path.join(assets, "ufo_pink.png"))
UFO3 = pygame.image.load(os.path.join(assets, "ufo_purple.png"))
UFO4 = pygame.image.load(os.path.join(assets, "ufo_orange.png"))
UFO1_S = pygame.image.load(os.path.join(assets, "ufo_blue_s.png"))
UFO2_S = pygame.image.load(os.path.join(assets, "ufo_pink_s.png"))
UFO3_S = pygame.image.load(os.path.join(assets, "ufo_purple_s.png"))
UFO4_S = pygame.image.load(os.path.join(assets, "ufo_orange_s.png"))

PROJECTILE = pygame.image.load(os.path.join(assets, "tennis_ball_s.png"))
PROJECTILE_BAD_S = pygame.image.load(os.path.join(assets, "tennis_ball_red_s.png"))
PROJECTILE_BAD = pygame.image.load(os.path.join(assets, "tennis_ball_red.png"))

POWERUP_BONE = pygame.image.load(os.path.join(assets, "bone.png"))
POWERUP_HEART = pygame.image.load(os.path.join(assets, "heart.png"))
POWERUP_BOMB = pygame.image.load(os.path.join(assets, "bomb.png"))
POWERUP_SHIELD = pygame.image.load(os.path.join(assets, "shield.png"))

EMPTY = pygame.image.load(os.path.join(assets, "empty.png"))
BACKGROUND = pygame.image.load(bg_filename)


class Projectile:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, speed):
        self.y += speed

    def offscreen(self, height):
        return not (height >= self.y >= 0) # todo sometimes spawning balls get glitched at top

    def collision(self, obj):
        return collide(self, obj)


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y))) is not None


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ship_img = None
        self.projectile_img = None
        self.projectiles = []
        self.cool_down = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for projectile in self.projectiles:
            projectile.draw(window)

    def projectile_movement(self, speed, obj):
        self.cooldown()
        for projectile in self.projectiles:
            projectile.move(speed)
            if projectile.offscreen(HEIGHT):
                self.projectiles.remove(projectile)
            elif projectile.collision(obj):
                obj.health -= 10
                self.projectiles.remove(projectile)

    def cooldown(self):
        if self.cool_down >= self.COOLDOWN:
            self.cool_down = 0
        elif self.cool_down > 0:
            self.cool_down += 1

    def shoot(self):
        if self.cool_down == 0:
            projectile = Projectile(self.x + self.get_width()/2,  # need to subtract the width of the projectile
                                    self.y, self.projectile_img)
            self.projectiles.append(projectile)
            self.cool_down = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player1(Ship):
    def __init__(self, x, y, health=40):
        super().__init__(x, y)
        self.health = health
        self.ship_img = SPACESHIP
        self.projectile_img = PROJECTILE
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.score = 0

    def projectile_movement(self, speed, ufos):
        self.cooldown()
        for projectile in self.projectiles:
            projectile.move(speed)
            if projectile.offscreen(HEIGHT):
                self.projectiles.remove(projectile)
            else:
                for ufo in ufos:
                    if projectile.collision(ufo):  # removes ufo after it gets hit with player projectile
                        self.score += 1
                        ufo.ship_img = EMPTY
                        ufo.mask = pygame.mask.from_surface(ufo.ship_img)
                        if projectile in self.projectiles:
                            self.projectiles.remove(projectile)  # removes player projectile after hitting ufo

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                               self.ship_img.get_width(), 5))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                               (self.health/self.max_health) * self.ship_img.get_width(), 5))
        # todo still a bit of green left after no health remove this


class EnemyShip(Ship):
    colour_picker = {
                    "purple": (UFO3, PROJECTILE_BAD),
                    "blue": (UFO1, PROJECTILE_BAD),
                    "orange": (UFO4, PROJECTILE_BAD),
                    "pink": (UFO2, PROJECTILE_BAD),
                    "purple_s": (UFO3_S, PROJECTILE_BAD_S),
                    "blue_s": (UFO1_S, PROJECTILE_BAD_S),
                    "orange_s": (UFO4_S, PROJECTILE_BAD_S),
                    "pink_s": (UFO2_S, PROJECTILE_BAD_S)
                    }

    def __init__(self, x, y, colour):
        super().__init__(x, y)
        self.ship_img, self. projectile_img = self.colour_picker[colour]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):  # todo add x movement random
        self.y += vel

    def shoot(self):   # added child shoot method since projectiles for ufos shoot from under
        if self.cool_down == 0:
            projectile = Projectile(self.x + self.get_width()/2 - 10,  # need to subtract the width of the projectile
                                    self.y + self.get_height(), self.projectile_img)
            self.projectiles.append(projectile)
            self.cool_down = 1


class PowerUP(Projectile):
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        self.power_up_list = []

    def spawn_power(self):
        self.power_up_list.append(self)

    def offscreen(self, height):
        return not (height >= self.y)


class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def empty(self):
        return not bool(self.items)

    def size(self):
        return len(self.items)


class Background:
    def __init__(self, y, bg, x=0):
        self.x = x
        self.y = y
        self.bg = bg

    def draw(self, window):
        window.blit(self.bg, (self.x, self.y))

    def move(self):
        self.y += 1


def main():
    run = True
    fps = 60
    clock = pygame.time.Clock()
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("Arial", 20)
    lost_font = pygame.font.SysFont("Arial", 50)
    lost = False
    lost_count = 0

    player_speed = 8
    player = Player1(WIDTH/2,
                     HEIGHT - 100)
    score = player.score
    proj_speed = 10
    proj_speed_bad = min(5 + level, 15)
    powerup_speed = 4
    powerup_counter1 = 0
    power_list = []

    enemy_list = []
    wave_length = 3
    enemy_speed = 1.5
    dead_enemy_speed = proj_speed_bad - 1
    moving_background = Background(-10, BACKGROUND)
    moving_background2 = Background(-HEIGHT-10, BACKGROUND)

    def redraw_window():
        moving_background.draw(WINDOW)
        moving_background2.draw(WINDOW)

        # Ships
        player.draw(WINDOW)
        for enemy in enemy_list:
            enemy.draw(WINDOW)
        for item in power_list:
            item.draw(WINDOW)

        # UI
        level_display = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        lives_display = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        score_display = main_font.render(f"Score: {score}", 1, (255, 255, 255))
        WINDOW.blit(lives_display, (20, 20))
        WINDOW.blit(score_display, (20, HEIGHT - 50))
        WINDOW.blit(level_display, (WIDTH - level_display.get_width() - 20, 20))
        if lost:
            #time.sleep(0.5)
            WINDOW.blit(BACKGROUND, (0, 0))
            lost_title = lost_font.render('YOU LOSE', 1, (255, 255, 255))
            WINDOW.blit(lost_title, (WIDTH / 2 - lost_title.get_width() / 2,
                                     HEIGHT / 2 - lost_title.get_height() / 2))
            WINDOW.blit(score_display, (WIDTH / 2 - score_display.get_width() / 2,
                                        HEIGHT / 2 - score_display.get_height() / 2 + 50))
        # todo maybe have ppl click out of the losing screen instead of set time
        pygame.display.update()

    #  ---------------MAIN LOOP---------------
    while run:
        clock.tick(fps)
        redraw_window()
        score = player.score

        moving_background.move()
        moving_background2.move()
        # there is two background imgs of height HEIGHT+10, both imgs move down
        # the +10 is band of black pixels to ensure smooth transition from one img to the next
        # if top of img hit top of game window
        # then make img below = img above, create new img above
        # since both imgs always move down another img above will hit top of game window - repeat
        if moving_background2.y >= 0:
            moving_background = moving_background2
            create_background()
            moving_background2 = Background(-HEIGHT - 10, BACKGROUND)


        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        if lost:
            if lost_count > fps*2:
                run = False
            else:
                continue

        # click X to exit program
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        # Movement of player ship
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player.y - player_speed > 0:  # up
            player.y -= player_speed
        if keys[pygame.K_a] and player.x - player_speed > 0:  # left
            player.x -= 1.2*player_speed
        if keys[pygame.K_s] and player.y + player_speed + player.get_height() < HEIGHT:  # down
            player.y += player_speed
        if keys[pygame.K_d] and player.x + player_speed + player.get_width() < WIDTH:  # right
            player.x += 1.2*player_speed
        if keys[pygame.K_SPACE]:
            player.shoot()
        player.projectile_movement(-proj_speed, enemy_list)

        # ship spawning - balance at the end
        if len(enemy_list) == 0:
            level += 1
            wave_length += 2
            for n in range(wave_length):
                enemy = EnemyShip(random.randrange(10, WIDTH - 200),
                                  random.randrange(-500, -100),
                                  random.choice(["purple", "blue", "pink", "orange",
                                                 "purple_s", "blue_s", "pink_s", "orange_s"])
                                  )
                enemy_list.append(enemy)

            # powerup spawning
            if random.randrange(0, 2) == 0 or powerup_counter1 == 0:
            #if level == 2 or powerup_counter1 == 3:
                powerup_counter1 = 0
                power_maker = PowerUP(random.randrange(10, WIDTH - 50),
                                      random.randrange(-500, -100),
                                      random.choice([POWERUP_HEART, POWERUP_BONE,
                                                     POWERUP_BOMB, POWERUP_SHIELD])
                                      )
                power_list.append(power_maker)
            else:
                powerup_counter1 += 1

            #health shouldnt spawn earlier

        # powerup movement
        for powerup in power_list:
            powerup.move(powerup_speed)
            if collide(powerup, player):
                if powerup.img == POWERUP_HEART:
                    player.health = 40
                    lives += 1
                if powerup.img == POWERUP_BONE:
                    player.health = 40
                if powerup.img == POWERUP_BOMB:
                    player.health = 40
                if powerup.img == POWERUP_SHIELD:
                    player.health = 40
                power_list.remove(powerup)
            elif powerup.y + 50 > HEIGHT:
                power_list.remove(powerup)

        # enemy behavior
        for enemy in enemy_list:
            enemy.move(enemy_speed)
            if enemy.ship_img == EMPTY:
                enemy.move(dead_enemy_speed)
            enemy.projectile_movement(proj_speed_bad, player)

            if random.randrange(0, 2*fps) == 1:  # for quicker testing
            # if random.randrange(0, min(3,(11-level))*fps) == 1:
                if enemy.ship_img != EMPTY:
                    enemy.shoot()
            if collide(enemy, player):  # if ufo and player collide lose 20 health ufo is destroyed
                player.health -= 20
                enemy_list.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:  # if enemy falls under screen lose a life
                if enemy.ship_img != EMPTY:
                    lives -= 1
                enemy_list.remove(enemy)

# todo add a proper main menu with instructions maybe different modes/hacks
def main_menu():
    run = True
    title_font = pygame.font.SysFont("Arial", 50)
    while run:
        WINDOW.blit(BACKGROUND, (0, 0))
        title = title_font.render("Press the mouse to begin!", 1, (255, 255, 255))
        WINDOW.blit(title, (WIDTH/2 - title.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
