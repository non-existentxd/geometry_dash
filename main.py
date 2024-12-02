import csv
import os
import random

import pygame

pygame.init()

screen = pygame.display.set_mode([800, 600])

done = False

start = False

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


color = lambda: tuple([random.randint(0, 255) for i in range(3)]) 




class Player(pygame.sprite.Sprite):
    win: bool
    died: bool

    def __init__(self, image, platforms, pos, *groups):

        super().__init__(*groups)
        self.onGround = False 
        self.platforms = platforms  
        self.died = False  
        self.win = False  

        self.image = pygame.transform.smoothscale(image, (32, 32))
        self.rect = self.image.get_rect(center=pos) 
        self.jump_amount = 10 
        self.particles = [] 
        self.isjump = False 



    def collide(self, yvel, platforms):
        global coins

        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                """pygame sprite builtin collision method,
                sees if player is colliding with any obstacles"""
                if isinstance(p, Orb) and (keys[pygame.K_UP] or keys[pygame.K_SPACE]):
                    pygame.draw.circle(alpha_surf, (255, 255, 0), p.rect.center, 18)
                    screen.blit(pygame.image.load("images/editor-0.9s-47px.gif"), p.rect.center)
                    self.jump_amount = 12  # gives a little boost when hit orb
                    self.jump()
                    self.jump_amount = 10  # return jump_amount to normal

                if isinstance(p, End):
                    self.win = True

                if isinstance(p, Spike):
                    self.died = True  # die on spike

                if isinstance(p, Coin):
                    # keeps track of all coins throughout the whole game(total of 6 is possible)
                    coins += 1

                    # erases a coin
                    p.rect.x = 0
                    p.rect.y = 0

                if isinstance(p, Platform):  # these are the blocks (may be confusing due to self.platforms)

                    if yvel > 0:
                        """if player is going down(yvel is +)"""
                        self.rect.bottom = p.rect.top  # dont let the player go through the ground
                        self.vel.y = 0  # rest y velocity because player is on ground

                        # set self.onGround to true because player collided with the ground
                        self.onGround = True

                        # reset jump
                        self.isjump = False
                    elif yvel < 0:
                        """if yvel is (-),player collided while jumping"""
                        self.rect.top = p.rect.bottom  # player top is set the bottom of block like it hits it head
                    else:
                        """otherwise, if player collides with a block, he/she dies."""
                        self.vel.x = 0
                        self.rect.right = p.rect.left  # dont let player go through walls
                        self.died = True

    def jump(self):
        self.vel.y = -self.jump_amount  # players vertical velocity is negative so ^

    def update(self):
        """update player"""
        if self.isjump:
            if self.onGround:
                """if player wants to jump and player is on the ground: only then is jump allowed"""
                self.jump()

        if not self.onGround:  # only accelerate with gravity if in the air
            self.vel += GRAVITY  # Gravity falls

            # max falling speed
            if self.vel.y > 100: self.vel.y = 100

        # do x-axis collisions
        self.collide(0, self.platforms)

        # increment in y direction
        self.rect.top += self.vel.y

        # assuming player in the air, and if not it will be set to inversed after collide
        self.onGround = False

        # do y-axis collisions
        self.collide(self.vel.y, self.platforms)

        # check if we won or if player won
        eval_outcome(self.win, self.died)



# Parent class
class Draw(pygame.sprite.Sprite):
    """parent class to all obstacle classes; Sprite class"""

    def __init__(self, image, pos, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)



class Platform(Draw):
    """block"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Spike(Draw):
    """spike"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Coin(Draw):
    """coin. get 6 and you win the game"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Orb(Draw):
    """orb. click space or up arrow while on it to jump in midair"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Trick(Draw):
    """block, but its a trick because you can go through it"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class End(Draw):
    "place this at the end of the level"

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)




def won_screen():
    """show this screen when beating a level"""
    global attempts, level, fill
    attempts = 0
    player_sprite.clear(player.image, screen)
    screen.fill(pygame.Color("yellow"))
    txt_win1 = txt_win2 = "Nothing"
    if level == 1:
        if coins == 6:
            txt_win1 = f"Coin{coins}/6! "
            txt_win2 = "the game, Congratulations"
    else:
        txt_win1 = f"level{level}"
        txt_win2 = f"Coins: {coins}/6. "
    txt_win = f"{txt_win1} You beat {txt_win2}! Press SPACE to restart, or ESC to exit"

    won_game = font.render(txt_win, True, BLUE)

    screen.blit(won_game, (200, 300))
    level += 1

    wait_for_key()
    reset()


def death_screen():
    """show this screenon death"""
    global attempts, fill
    fill = 0
    player_sprite.clear(player.image, screen)
    attempts += 1
    game_over = font.render("Game Over. [SPACE] to restart", True, WHITE)

    screen.fill(pygame.Color("sienna1"))
    screen.blits([[game_over, (100, 100)], [tip, (100, 400)]])

    wait_for_key()
    reset()


def eval_outcome(won: bool, died: bool):
    if won:
        won_screen()
    if died:
        death_screen()


def block_map(level_num):
    lvl = []
    with open(level_num, newline='') as csvfile:
        trash = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in trash:
            lvl.append(row)
    return lvl


