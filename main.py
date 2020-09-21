from PIL import Image, ImageDraw
import random
import os
import pygame

# pygame setup
pygame.font.init()
WIDTH, HEIGHT = 600, 900
game_display_window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("APOLLO ADVENTURE")
current_path = os.path.dirname(__file__)
assets = os.path.join(current_path, "assets/")
bg_filename = os.path.join(assets, 'background.jpg')
bg_filename1 = os.path.join(assets, 'background1.jpg')


# background generator
def create_background(file_path):
    space = Image.new("RGB", (WIDTH, HEIGHT + 10), "black")
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
            d.rectangle([offsetx, size + offsety,
                        3 * size + offsetx, 2 * size + offsety], fill=colour)
            d.rectangle([size + offsetx, offsety,
                        2 * size + offsetx, 3 * size + offsety], fill=colour)
    space.save(file_path)


create_background(bg_filename)
create_background(bg_filename1)

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
PROJECTILE_BIG = pygame.image.load(os.path.join(assets, "tennis_ball.png"))
PROJECTILE_BAD_S = pygame.image.load(os.path.join(assets, "tennis_ball_red_s.png"))
PROJECTILE_BAD = pygame.image.load(os.path.join(assets, "tennis_ball_red.png"))

POWERUP_BONE = pygame.image.load(os.path.join(assets, "bone.png"))
POWERUP_HEART = pygame.image.load(os.path.join(assets, "heart.png"))
POWERUP_BOMB = pygame.image.load(os.path.join(assets, "bomb.png"))
POWERUP_SHIELD = pygame.image.load(os.path.join(assets, "shield.png"))
FORCEFIELD = pygame.image.load(os.path.join(assets, "force_field_small.png"))

EXPLOSION1 = pygame.image.load(os.path.join(assets, "explosion(half)1.png"))
EXPLOSION4 = pygame.image.load(os.path.join(assets, "explosion(half)4.png"))
EXPLOSION5 = pygame.image.load(os.path.join(assets, "explosion(half)5.png"))
EXPLOSION8 = pygame.image.load(os.path.join(assets, "explosion(half)8.png"))
EXPLOSION9 = pygame.image.load(os.path.join(assets, "explosion(half)9.png"))
EXPLOSION = [EXPLOSION1, EXPLOSION4, EXPLOSION5, EXPLOSION8, EXPLOSION9]

EMPTY = pygame.image.load(os.path.join(assets, "empty.png"))
BACKGROUND = pygame.image.load(bg_filename)
BACKGROUND1 = pygame.image.load(bg_filename1)


class Projectile:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x - (self.get_width()/2),
                               self.y))

    def move(self, speed):
        self.y += speed

    def offscreen(self, height):
        return not (height >= self.y > 0)

    def get_width(self):
        return self.img.get_width()

    def get_height(self):
        return self.img.get_height()

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
        self.bone_count = 1

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
                if obj.shield_health > 0:
                    obj.shield_health -= 10
                else:
                    obj.health -= 10
                self.projectiles.remove(projectile)

    def cooldown(self):
        if self.cool_down >= self.COOLDOWN:
            self.cool_down = 0
        elif self.cool_down > 0:
            self.cool_down += min(1 * self.bone_count, 4)

    def shoot(self):
        if self.cool_down == 0:
            if self.bone_count >= 4:
                projectile = Projectile(self.x + self.get_width()/2 + 20,
                                        self.y, self.projectile_img)
                projectile1 = Projectile(self.x + self.get_width()/2 - 20,
                                         self.y-1, self.projectile_img)
                self.projectiles.append(projectile)
                self.projectiles.append(projectile1)
            else:
                projectile = Projectile(self.x + self.get_width()/2,
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
        self.max_health = health
        self.ship_img = SPACESHIP
        self.projectile_img = PROJECTILE
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.shield_img = FORCEFIELD
        self.shield_health = 0
        self.score = 0

    def shield(self):
        self.shield_health = 19
        self.ship_img = FORCEFIELD
        self.mask = pygame.mask.from_surface(self.shield_img)

    def deshield(self):
        self.ship_img = SPACESHIP
        self.mask = pygame.mask.from_surface(self.ship_img)

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
        if self.health <= 0:
            pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                                   self.ship_img.get_width(), 5))
        else:
            pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                                   (self.health/self.max_health) * self.ship_img.get_width(), 5))


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
            projectile = Projectile(self.x + self.get_width()/2,
                                    self.y + self.get_height(), self.projectile_img)
            self.projectiles.append(projectile)
            self.cool_down = 1


class PowerUP(Projectile):
    def __init__(self, x, y, img):
        super().__init__(x, y, img)
        self.mask = pygame.mask.from_surface(self.img)
        self.power_up_list = []

    def spawn_power(self):
        self.power_up_list.append(self)

    def offscreen(self, height):
        return not (height >= self.y)


class Background:
    def __init__(self, y, bg, x=0):
        self.x = x
        self.y = y
        self.bg = bg

    def draw(self, window):
        window.blit(self.bg, (self.x, self.y))

    def move(self):
        self.y += 0.5  # todo change this value at the end


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
    player = Player1(WIDTH/2, HEIGHT-100)
    score = player.score
    proj_speed = 10
    proj_speed_bad = min(5+level, 15)
    powerup_speed = 4
    powerup_counter = 0
    bomb_count = 1
    bomb_cooldown = 0
    power_list = []

    enemy_list = []
    wave_length = 0
    enemy_speed = min(7.5, 1.3+level*0.1)
    dead_enemy_speed = proj_speed_bad-1
    moving_background_bottom = Background(-10, BACKGROUND)
    moving_background_top = Background(-HEIGHT-10, BACKGROUND)
    moving_background_placeholder = None

    def redraw_window():
        moving_background_bottom.draw(game_display_window)
        moving_background_top.draw(game_display_window)

        # Ships & Powers
        player.draw(game_display_window)

        for enemy in enemy_list:
            enemy.draw(game_display_window)

        for item in power_list:
            item.draw(game_display_window)

        # UI
        level_display = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        lives_display = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        score_display = main_font.render(f"Score: {score}", 1, (255, 255, 255))
        bomb_display = main_font.render(f"Bombs: {bomb_count}", 1, (255, 255, 255))
        game_display_window.blit(score_display, (20, 20))
        game_display_window.blit(lives_display, (20, HEIGHT-50))
        game_display_window.blit(level_display, (WIDTH-level_display.get_width()-20, 20))
        game_display_window.blit(bomb_display, (WIDTH-bomb_display.get_width()-20, HEIGHT-50))
        if lost:
            game_display_window.blit(BACKGROUND, (0, 0))
            lost_title = lost_font.render('YOU LOSE', 1, (255, 255, 255))
            game_display_window.blit(lost_title, (WIDTH/2-lost_title.get_width()/2,
                                                  HEIGHT/2-lost_title.get_height()/2))
            game_display_window.blit(score_display, (WIDTH/2-score_display.get_width()/2,
                                                     HEIGHT/2-score_display.get_height()/2 + 50))

        pygame.display.update()

    #  ---------------MAIN LOOP---------------
    while run:
        clock.tick(fps)
        redraw_window()
        score = player.score

        moving_background_bottom.move()
        moving_background_top.move()
        # there is two background imgs of height HEIGHT+10, both imgs move down
        # the +10 is band of black pixels to ensure smooth transition from one img to the next
        # if top of img hit top of game window
        # then make img below = img above, create new img above
        # since both imgs always move down another img above will hit top of game window - repeat
        if moving_background_top.y >= 0:

            moving_background_bottom = moving_background_top  # todo background are always the same
                                                              #     - might have to make two background imgs
            create_background(bg_filename)
            moving_background_top = Background(-HEIGHT-10, BACKGROUND)


            # moving_background_bottom = moving_background_top
            # create_background()
            # moving_background_top = Background(-HEIGHT-10, BACKGROUND)

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

        # ship spawning - todo balance at the end
        if len(enemy_list) == 0:
            level += 1
            wave_length += 3
            for n in range(wave_length):
                enemy = EnemyShip(random.randrange(10, WIDTH-200),
                                  random.randrange(-1000+level*50, -100),
                                  random.choice(["purple", "blue", "pink", "orange",
                                                 "purple_s", "blue_s", "pink_s", "orange_s"])
                                  )
                enemy_list.append(enemy)

            # powerup spawning - todo balance later - maybe spawn multiple powerups per level
            def power_spawn_rules():
                if player.bone_count >= 5:
                    return random.choice([POWERUP_HEART, POWERUP_BOMB, POWERUP_SHIELD])
                if level < 2 or player.health == player.max_health:
                    return random.choice([POWERUP_BONE, POWERUP_BOMB, POWERUP_SHIELD])
                else:
                    return random.choice([POWERUP_HEART, POWERUP_BONE, POWERUP_BOMB, POWERUP_SHIELD])

            if random.randrange(0, 2) == 0 or powerup_counter == 2:
                powerup_counter = 0
                power_maker = PowerUP(random.randrange(10, WIDTH-50),
                                      random.randrange(-500, -100),
                                      power_spawn_rules()
                                      )
                power_list.append(power_maker)
            else:
                powerup_counter += 1

        # powerup behavior
        for powerup in power_list:
            powerup.move(powerup_speed)
            if collide(powerup, player):
                if powerup.img == POWERUP_HEART:
                    player.health = 40
                    lives += 1
                if powerup.img == POWERUP_BONE:
                    player.bone_count += 1
                if powerup.img == POWERUP_BOMB:
                    bomb_count += 1
                if powerup.img == POWERUP_SHIELD:
                    player.shield()
                power_list.remove(powerup)
            elif powerup.y > HEIGHT:
                power_list.remove(powerup)
        # bones
        if player.bone_count == 3:
            player.projectile_img = PROJECTILE_BIG

        # explode bomb
        if bomb_cooldown == 0:
            if keys[pygame.K_f]:
                bomb_cooldown = 2*fps  # 2 sec cooldown for bombs
                if bomb_count > 0:
                    bomb_count -= 1
                    for enemy in enemy_list:
                        if 0 <= enemy.x and 0 <= enemy.y:
                            if enemy.ship_img != EMPTY:
                                for explode in EXPLOSION:
                                    enemy.ship_img = explode
                                    redraw_window()
                                    pygame.time.wait(1)  # todo tweek this
                                enemy.ship_img = EMPTY
                                enemy.mask = pygame.mask.from_surface(enemy.ship_img)
        elif bomb_cooldown > 0:
            bomb_cooldown -= 1

        # remove shield
        if player.shield_health <= 0:
            player.deshield()

        # Enemy behavior
        for enemy in enemy_list:
            enemy.move(enemy_speed)
            if enemy.ship_img == EMPTY:
                enemy.move(dead_enemy_speed)
            enemy.projectile_movement(proj_speed_bad, player)

            if random.randrange(0, 3*fps) == 1:  # for quicker testing
            # if random.randrange(0, min(3*fps, (8-level))*fps) == 1: # todo balance at end
                if enemy.ship_img != EMPTY:
                    enemy.shoot()
            if collide(enemy, player):  # if ufo and player collide lose 20 health ufo is destroyed
                player.health -= 20
                enemy_list.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:  # if enemy falls under screen lose a life
                if enemy.ship_img != EMPTY:
                    lives -= 1
                enemy_list.remove(enemy)


def instructions():
    run = True
    fps = 60
    clock = pygame.time.Clock()

    def redraw_window():
        text_font = pygame.font.SysFont("Arial", 18)
        lines = [line.rstrip('\n') for line in open("instructions.txt", "r")]
        spacing = 20

        pygame.draw.rect(game_display_window, (0, 0, 0),  # left, top, width, height
                         (0, 0, WIDTH, HEIGHT))

        for line in lines:
            spacing += 20
            message = text_font.render(line, 1, (255, 255, 255))
            game_display_window.blit(message, (WIDTH/2 - message.get_width()/2, spacing))

        game_display_window.blit(POWERUP_HEART, (WIDTH/8, 450))
        game_display_window.blit(POWERUP_BOMB, (WIDTH/8, 550))
        game_display_window.blit(POWERUP_SHIELD, (WIDTH/8, 650))
        game_display_window.blit(POWERUP_BONE, (WIDTH/8, 750))

        heart_str = "This power up will heal you to full health"
        heart_text = text_font.render(heart_str, 1, (255, 255, 255))
        game_display_window.blit(heart_text, (WIDTH/8 + 2*POWERUP_HEART.get_width(), 450))
        heart_str1 = "and grant you a full health bar."
        heart_text1 = text_font.render(heart_str1, 1, (255, 255, 255))
        game_display_window.blit(heart_text1, (WIDTH / 8 + 2 * POWERUP_HEART.get_width(), 470))
        bomb_str = "Press 'F' to use this power up to destroy all enemies"
        bomb_text = text_font.render(bomb_str, 1, (255, 255, 255))
        game_display_window.blit(bomb_text, (WIDTH/8 + 2*POWERUP_BOMB.get_width(), 550))
        bomb_str1 = "on the screen (no score will be added for bomb kills)."
        bomb_text1 = text_font.render(bomb_str1, 1, (255, 255, 255))
        game_display_window.blit(bomb_text1, (WIDTH / 8 + 2 * POWERUP_BOMB.get_width(), 570))
        shield_str = "This power up will absorb two enemy projectiles."
        shield_text = text_font.render(shield_str, 1, (255, 255, 255))
        game_display_window.blit(shield_text, (WIDTH/8 + 2*POWERUP_SHIELD.get_width(), 650))
        bone_str = "This power up will increase your rate of fire"
        bone_text = text_font.render(bone_str, 1, (255, 255, 255))
        game_display_window.blit(bone_text, (WIDTH/8 + 2*POWERUP_BONE.get_width(), 750))
        bone_str1 = "Collect more to gain extra special powers!"
        bone_text1 = text_font.render(bone_str1, 1, (255, 255, 255))
        game_display_window.blit(bone_text1, (WIDTH / 8 + 2 * POWERUP_BONE.get_width(), 770))
        exit_str = "Click anywhere to go back to the main menu"
        exit_text = text_font.render(exit_str, 1, (255, 255, 255))
        game_display_window.blit(exit_text, (WIDTH/2-exit_text.get_width()/2, HEIGHT-70))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                main_menu()

    while run:
        clock.tick(fps)
        redraw_window()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()


def main_menu():
    # run = True
    title_font = pygame.font.SysFont("Arial", 50)
    buttons_font = pygame.font.SysFont("Arial", 30)
    button_colour = (130, 145, 170)
    bright_button_colour = (174, 196, 232)
    while True:
        # main menu button clicks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN \
                    and WIDTH / 3 * 2 > mouse[0] > WIDTH / 3 \
                    and HEIGHT / 4 + 75 > mouse[1] > HEIGHT / 4:
                main()
            if event.type == pygame.MOUSEBUTTONDOWN \
                    and WIDTH / 3 * 2 > mouse[0] > WIDTH / 3 \
                    and HEIGHT / 2 + 75 > mouse[1] > HEIGHT / 2:
                instructions()
            if event.type == pygame.MOUSEBUTTONDOWN \
                    and WIDTH / 3 * 2 > mouse[0] > WIDTH / 3 \
                    and HEIGHT * 3 / 4 + 75 > mouse[1] > HEIGHT * 3 / 4:
                quit()

        # create background
        game_display_window.blit(BACKGROUND, (0, 0))
        # create buttons
        pygame.draw.rect(game_display_window, button_colour,  # left, top, width, height
                         (WIDTH/3, HEIGHT/4, WIDTH/3, 75))
        pygame.draw.rect(game_display_window, button_colour,
                         (WIDTH/3, HEIGHT/2, WIDTH/3, 75))
        pygame.draw.rect(game_display_window, button_colour,
                         (WIDTH/3, HEIGHT*3/4, WIDTH/3, 75))
        # change button colour
        mouse = pygame.mouse.get_pos()
        if WIDTH/3*2 > mouse[0] > WIDTH/3 and HEIGHT/4+75 > mouse[1] > HEIGHT/4:
            pygame.draw.rect(game_display_window, bright_button_colour,
                             (WIDTH/3, HEIGHT/4, WIDTH/3, 75))
        if WIDTH/3*2 > mouse[0] > WIDTH/3 and HEIGHT/2+75 > mouse[1] > HEIGHT/2:
            pygame.draw.rect(game_display_window, bright_button_colour,
                             (WIDTH/3, HEIGHT/2, WIDTH/3, 75))
        if WIDTH/3*2 > mouse[0] > WIDTH/3 and HEIGHT*3/4+75 > mouse[1] > HEIGHT*3/4:
            pygame.draw.rect(game_display_window, bright_button_colour,
                             (WIDTH/3, HEIGHT*3/4, WIDTH/3, 75))
        # make title & button text
        title = title_font.render("Apollo Adventure", 1, (255, 255, 255))
        game_display_window.blit(title, (WIDTH/2 - title.get_width()/2, HEIGHT/8))
        play = buttons_font.render("Start", 1, (255, 255, 255))
        game_display_window.blit(play, (WIDTH/2 - play.get_width()/2, HEIGHT/4 + play.get_height()/2))
        controls = buttons_font.render("Instructions", 1, (255, 255, 255))
        game_display_window.blit(controls, (WIDTH/2 - controls.get_width()/2, HEIGHT/2 + play.get_height()/2))
        quit_button = buttons_font.render("Quit", 1, (255, 255, 255))
        game_display_window.blit(quit_button, (WIDTH/2 - quit_button.get_width()/2, HEIGHT*3/4 + play.get_height()/2))

        pygame.display.update()

    pygame.quit()


main_menu()
