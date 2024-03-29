# Amy Liu
# Game.py
# June 16, 2023
'''
This is a program that runs a game. This game is a vertical scroller that involves the player jumping from randomly generated platform to platform. The game is an endless one where the goal is to last as long as possible, and
ends either when the player loses all their lives or goes off of the screen from the bottom. Platforms can be moving, breakable or normal, and may have different objects that help or hinder the player. There can be obstacles
of two types: laser or spikes. Helpful objects, or tokens, can be a few different types: ones that give you an extra jump, up to a max of three, a star which can slow the scrolling of the screen down when enough are collected,
a jetpack that boosts the player up for a time, and TNT that launches a player and destroys platforms beneath it.
There is a start menu that leads to a menu for the instructions and to a screen for selecting difficulty. The game can be easy, normal or hard, and the difficulty increases with each mode.
'''

# importing libraries
from pygame import *
from math import *
from random import *

font.init()

vec = math.Vector2
myClock = time.Clock()

# setting constants
GREEN = (0, 255, 0)
RED = (255, 0, 0)

WIDTH = 600    # width and height of screen
HEIGHT = 700
PLATWIDTH = 20    # thickness of platforms
FPS = 60

MAXDIST = 300
MINPLATMOVE = 80    # minimum range that a moving platform can move around in

# constants to make it easier to keep track of types of things
NORMAL = 0
BREAK = 1
MOVE = 2

JUMP = 0
STAR = 1
JETPACK = 2

SPIKE = 0
LASER = 1

X = 0
Y = 1

maxDist = 200
minDist = 100    # minimum distance that can be present between platforms

screen = display.set_mode((WIDTH, HEIGHT))


fnt = font.SysFont("Consolas", 50)
starFnt = font.SysFont("Consolas", 30, bold = True)

# loading images and converting them to run smoother

menus = ["main", "instruction", "difficulty", "gameover"]    # image of menus, which will evetually have buttons to be able to interact with them
loadedMenu = []   # list for loaded images
playerSprite = [image.load("playerRight.png").convert_alpha(), image.load("playerLeft.png").convert_alpha()]
backgrounds = ["star", "sky", "skydark", "starlight"]    # backgrounds for in the game

# loading sprites for things that can be interacted with in-game
loadedBack = []
platSprites = ["shortgrass", "medgrass", "longgrass", "shortspace", "medspace", "longspace", "shortspacebreak", "medspacebreak", "longspacebreak", "shortgrassbreak", "medgrassbreak", "longgrassbreak"]
loadedPlat = []
toks = ["jetpack", "jump", "star", "tnt"]
loadedToks = []
obsSprites = ["laser", "spikeShort", "spikeMed", "spikeLong", "laserEnd"]
loadedObs = []

# icons that keep track of lives and extra jumps
icons = ["jumpFilled", "jumpEmpty", "heartFilled", "heartEmpty"]
loadedIcons = []

# for loops for loading and appending to lists
for m in menus:
    loadedMenu.append(image.load(m + "Menu.png").convert_alpha())

for back in backgrounds:
    loadedBack.append(image.load(back + "Back.png").convert_alpha())

for sprite in platSprites:
    loadedPlat.append(image.load(sprite + "Plat.png").convert_alpha())

for t in toks:
    loadedToks.append(image.load(t + "Tok.png").convert_alpha())

for o in obsSprites:
    loadedObs.append(image.load(o + ".png").convert_alpha())

for i in icons:
    loadedIcons.append(image.load(i + ".png").convert_alpha())


# classes
class Player():
    '''
    Stores all the information about the player that the user controls. Also has the functions that directly affect the player: moving/updating the player's position, jumping, canceling jumps, jetpacking, and invincibility frames
    '''
    def __init__(self, pos, rect):
        # initializes variables
        self.pos = pos
        self.vel = vec(0, 0)    # player's velocity
        self.acc = vec(0, 0)    # player's acceleration
        self.rect = rect
        self.facing = "R"
        self.sprite = playerSprite[0]
        self.invincible = False    # controls if the player is affected by obstacles, activates if the player is hit
        self.invincibleTime = 1 * FPS    # the amount of time that the player is invincible for
        self.jumping = False    # whether the player is jumping or not
        self.maxSpeed = 10    # speed of player's horizontal movement
        self.collision = False
        self.available = 1    # whether the player has already double jumped or not in a jump
        self.jetpack = False    # whether or not the player is in the jetpack state
        self.jetpackTime = randint(2, 3) * FPS    # the amount of time the player has in the jetpack state

        
    def move(self):
        '''
        Changes the player's position based on the preset gravity and the user's inputs
        Referenced from https://coderslegacy.com/python/pygame-gravity-and-jumping/
        '''
        
        self.acc = vec(0, 0.9)    # 0.9 creates gravity by constantly increasing the player's downward velocity
        self.vel.x = 0    # resets the player's horizontal velocity to 0 so that the player can stop after moving

        keys = key.get_pressed()
        
        # changes the player's horizontal velocity
        if keys[K_LEFT]:
            self.vel.x = -self.maxSpeed    
            self.facing = "L"    # the direction that the player is facing, used to draw the player sprite in the corresponding direction
        elif keys[K_RIGHT]:
            self.vel.x = self.maxSpeed
            self.facing = "R"

        # updating the player's position based  on the current speed
        self.vel = self.vel + self.acc
        self.pos[1] += self.vel.y
        self.pos[0] += self.vel.x
        self.rect[0] = self.pos[0]
        self.rect[1] = self.pos[1]    # updates the player's rect to match the position

        # teleports the player to the other side of the screen if they go off from the side
        if self.rect.left >= WIDTH:
            self.pos[X] = -40
        if self.rect.right <= 0:
            self.pos[X] = WIDTH

    def playerJump(self):
        '''
        Makes the player jump or double jump when called
        '''

        global jumps
        self.jumping = True
        if self.vel.y != 0:    # if the player is currently in the air
            if jumps > 0:
                if self.available:    # if the player has not already double jumped
                    jumps -= 1
                    self.available = 0
                    self.vel.y = -24

        if self.vel.y == 0:
            self.vel.y = -24    # increases the upward velocity, resulting in a jump

    def jumpCancel(self):
        '''
        Cancels a jump early if the spacebar is released
        '''
        
        if self.jumping:
            if self.vel.y < -10:
                self.vel.y = -10
            
    def spriteChange(self):
        '''
        Changes the player's sprite based on the way it is facing
        '''
        
        if self.facing == "R":
            self.sprite = playerSprite[0]
        if self.facing == "L":
            self.sprite = playerSprite[1]
        

    
    def collide(self, plats):
        '''
        Controls what happens when a player collides with a platform
        '''

        
        self.collision = False
        for plat in plats:
            if plat.rect.colliderect(self.rect):
                if self.vel.y > 0:
                    if (self.rect.bottom >= plat.rect.top and self.rect.bottom < plat.rect.bottom) and self.rect.top < plat.rect.top:    # makes sure that the player only gets placed on top of the platform if it is entirely above the platform
                        self.jumping = False
                        self.collision = True
                        self.vel.y = 0
                        self.acc.y = 0    # gravity stops when the player is on a platform
                        self.pos[Y] = plat.rect.top - self.rect[3] + 1    # places the player on the top of the platform so that they are not stuck in the platform
                        self.available = 1    # the double jump is refreshed

                        # makes the player move with a moving platform
                        if plat.mode == MOVE:
                            if plat.dir == "R":
                                self.pos[X] += 2
                            if plat.dir == "L":
                                self.pos[X] -= 2

    def jetpacking(self):
        '''
        Contols the player's movement when in the jetpacking state
        '''
        
        global scrollSpeed
        if self.jetpackTime > 0:
            self.jetpackTime -= 1
            self.vel.y = -20
            self.acc.y = 0
            scrollSpeed = -self.vel.y    # increases the scroll speed to that the screen follows the player

            # gradually draws more platforms as the jetpacking state ends so that the player has platforms to stand on
            if self.jetpackTime == 25:    # 25 frames left
                for i in range(3):
                    genPlat(-100, -20)
            if self.jetpackTime == 15:    # 15 frames left
                for i in range(3):
                    genPlat(-100, -20)
            if self.jetpackTime == 10:    # 10 frames left
                for i in range(5):
                    genPlat(-300, -20)
                    
            if self.jetpackTime == 0:    # jetpack state ends
                self.jetpack = False
                self.jetpackTime = randint(2, 3) * FPS    # resets the jetpack time
                scrollSpeed = startingScroll

    def invincibility(self):
        '''
        Makes the player uninvincible after some time so that the player has i-frames after touching an obstacle
        '''
        
        if self.invincible == True:
            if self.invincibleTime > 0:
                self.invincibleTime -= 1    # time starts counting down when invincibile is first set to true

                if self.invincibleTime == 0:    # i-frames end
                    self.invincible = False
                    self.invincibleTime = 1 * FPS    # resets invincibility time
            
        
        
        
class Platform():
    '''
    Contains the information about a platform: the type/mode, position, rect, sprite, objects on it, etc.
    '''
    def __init__(self, rect, mode, length, spriteType):
        # initialize variables
        self.rect = rect
        self.pos = [self.rect[0], self.rect[1]]
        self.mode = mode    # the type of platform: normal, breakable, or moving
        self.spriteType = spriteType    # which theme the sprite will be: "grass" - grassy or "space" - futuristic

        # sets which of three lengths of platform this one will be
        if length == 0:
            self.length = 40
        if length == 1:
            self.length = 50
        if length == 2:
            self.length = 70

        # sets what the platform's sprite will be
        if self.length == 40:
            if self.spriteType == "grass":    # grassy platforms
                if self.mode == BREAK:
                    self.sprite = loadedPlat[9]
                else:
                    self.sprite = loadedPlat[0]
            if self.spriteType == "space":    # futuristic platforms
                if self.mode == BREAK:
                    self.sprite = loadedPlat[6]
                else:
                    self.sprite = loadedPlat[3]
                
        if self.length == 50:
            if self.spriteType == "grass":
                if self.mode == BREAK:
                    self.sprite = loadedPlat[10]
                else:
                    self.sprite = loadedPlat[1]
            if self.spriteType == "space":
                if self.mode == BREAK:
                    self.sprite = loadedPlat[7]
                else:
                    self.sprite = loadedPlat[4]

        if self.length == 70:
            if self.spriteType == "grass":
                if self.mode == BREAK:
                    self.sprite = loadedPlat[11]
                else:
                    self.sprite = loadedPlat[2]
                
            if self.spriteType == "space":
                if self.mode == BREAK:
                    self.sprite = loadedPlat[8]
                else:
                    self.sprite = loadedPlat[5]

        # whether this platform will have any extra objects on it and what kind they will be
        self.attribute = "none"
        self.obstacle = "none"

        # if the extra platforms objects have been drawn on already, otherwise will draw them multiple times
        self.drawnAtt = False    
        self.drawnObs = False

        if self.mode != MOVE:   # so that moving platforms will not have objects or obstacles on it
            chance = randint(1, 101)
            if chance <= spikeChance:
                self.obstacle = "spike"
            elif chance <= spikeChance + laserChance:
                self.obstacle = "laser"
        if self.mode != MOVE:
            chance = randint(1, 101)
            if  chance <= TNTChance:
                self.attribute = "TNT"
            elif chance <= TNTChance + jumpChance:
                self.attribute = "jump"
            elif chance <= TNTChance + jumpChance + starChance:
                self.attribute = "star"
            elif chance <= TNTChance + jumpChance + starChance + jetpackChance:
                self.attribute = "jetpack"

        # set some attributes based on the platform's type
        if self.mode == NORMAL:
            self.colour = GREEN
        if self.mode == BREAK:
            self.colour = RED
            self.visible = True   # whether the platform has been broken or not
            self.timer = 10
            self.setTimer = False    # sets a timer for the platform to disappear after the player goes on it
        if self.mode == MOVE:
            self.valid = True    # if the platform is one that can exist
            self.colour = (0, 255, 255)
            self.startPos = (self.pos[X], self.pos[Y])    # the position that the platform starts in
                    
            if self.pos[X] + MINPLATMOVE < WIDTH - self.rect[2]:
                self.endPos = (randint(self.pos[X] + MINPLATMOVE, WIDTH - self.rect[2]), self.pos[Y])    # the point at which the platform switches directions - "WIDTH - self.rect[2]" guarantees that it will be on the screen 
                self.pathRect = Rect(self.startPos[X], self.startPos[Y], self.endPos[X] - self.startPos[X] + self.rect[2], self.rect[3])    # a Rect that represents the path that the platform will take - all possible positions of the platform
            else:
                self.valid = False
                
            self.dir = "R"    # current moving direction of the platform
            

    def breakMode(self, player):
        '''
        Controls the breaking of breakable platforms
        '''
        
        if self.visible:
            nonCorrected = player.rect    # the position of the player when colliding with a platform, before it is placed on top of the plaforms
            nonCorrected[Y] += 1
            if player.collision and nonCorrected.colliderect(self.rect):
                self.setTimer = True

            if self.setTimer:
                self.timer -= 1
            if self.timer == 0:
                self.visible = False

    def moveMode(self):
        '''
        Controls the movement of moving platforms
        '''
        
        if self.dir == "R":
            self.rect[X] += 2
            self.pos[X] = self.pos[X] + 2
        if self.dir == "L":
            self.rect[X] -= 2
            self.pos[X] = self.pos[X] - 2
        # switches directions
        if self.rect[X] >= self.endPos[X]:
            self.dir = "L"
        if self.rect[X] <= self.startPos[X]:
            self.dir = "R"

    def pathUpdate(self):
        # updates the position of the path rect based on the current position of the plaform
        self.pathRect[1] = self.rect[1]
            


class TNT():
    '''
    Contains all the information about a TNT: the platform it is on, its position/rect, sprite, etc.
    Has function explode()
    '''
    def __init__(self, plat):
        self.plat = plat
        if self.plat.obstacle == "spike":    # raises TNT placement to not overlap with spikes
            self.pos = (randint(plat.rect.left, plat.rect.right - 20), plat.rect.top - 40 - spikeHeight - 10)
        else:
            self.pos = (randint(plat.rect.left, plat.rect.right - 20), plat.rect.top - 40)
        self.rect = Rect(self.pos[0], self.pos[1], 30, 40)
        self.sprite = loadedToks[3]
        self.exploded = False    # whether the TNT has been collided with yet

    def explode(self):
        '''
        Deletes the TNT and platforms below it when colliding with it and launches th player
        '''
        global platforms
        global TNTList
        
        killList = []
        if player.rect.colliderect(self.rect):
            self.exploded = True
            player.TNTed = True
            player.jumping = False
            for i in range(len(platforms)):
                if platforms[i].rect[1] >= self.rect.bottom:    # adds the index of platforms below the TNT to the list of platforms to be removed
                    killList.append(i)

            player.vel.y = -40    # increases the upwards velocity of the player by a large amount

        platforms = kill(platforms, killList)

class Token():
    '''
    Contains information about a token object: the platform its on, the kind of token it is, etc.
    '''
    
    def __init__(self, plat, mode):
        size = 30
        self.plat = plat
        if self.plat.obstacle == "none" or self.plat.obstacle == "laser":
            self.pos = (self.plat.rect[0] + self.plat.rect[3]/2, self.plat.rect.top - size - 10)
            self.rect = Rect(self.pos[X], self.pos[Y], size, size)
        if self.plat.obstacle == "spike":    # raises token placement to not overlap with spikes
            self.pos = (self.plat.rect[0] + self.plat.rect[3]/2, self.plat.rect.top - size - spikeHeight - 10)
            self.rect = Rect(self.pos[X], self.pos[Y], size, size)
            
        self.mode = mode
            
        self.gone = False    # sets to true when the token is collided with - it is consumed

        if self.mode == JUMP:
            self.colour = (255, 255, 255)
            self.sprite = loadedToks[1]
        if self.mode == STAR:
            self.colour = (255, 255, 0)
            self.sprite = loadedToks[2]
        if self.mode == JETPACK:
            self.colour = (0, 0, 255)
            self.sprite = loadedToks[0]

    # following functions perform similar functions: setting the token to "gone" and triggering the respective events when collided with
    def doubJumpTok(self):
        # double jump token
        global jumps
        if player.rect.colliderect(self.rect):
            if jumps < 3:
                jumps += 1
            self.gone = True

    def starTok(self):
        global stars
        if player.rect.colliderect(self.rect):
            print("collide")
            if stars < 8:
                stars += 1
            self.gone = True

    def jetpackTok(self):
        if player.rect.colliderect(self.rect):
            player.jetpack = True    # starts the jetpack state
            self.gone = True


class Obs():
    '''
    Contains information about obstacles: the platform it is on, the type of obstacle, sprite, etc.
    '''
    
    def __init__(self, plat, mode):
        self.plat = plat
        self.mode = mode

        if self.mode == SPIKE:
            self.rect = Rect(self.plat.rect[X], self.plat.rect[Y] - spikeHeight, self.plat.length, spikeHeight)    # length of spikes depends on length of platform
            self.colour = (128, 128, 0)

            # sprite of spike based on platform length
            if plat.length == 40:
                self.sprite = loadedObs[1]
            if plat.length == 50:
                self.sprite = loadedObs[2]
            if plat.length == 70:
                self.sprite = loadedObs[3]


        if self.mode == LASER:
            self.endPoint = randint(100, 500)    # random point for the laser to end
            self.rect = Rect(self.plat.rect.center[X], self.plat.rect.top - self.endPoint, laserWidth, self.endPoint)    
            self.colour = (255, 0, 0)
            self.topSprite = loadedObs[4]    # sprites for the top and bottom of the lasers
            self.bottomSprite = loadedObs[0]
            self.topSpriteRect = Rect(self.rect[0] - self.topSprite.get_width()/2 + 5, self.rect.top - 4, self.topSprite.get_width(), self.topSprite.get_height())
            self.bottomSpriteRect = Rect(self.rect[0] - self.topSprite.get_width()/2 + 5, self.rect.bottom - self.topSprite.get_height(), self.topSprite.get_width(), self.topSprite.get_height())
    
    def obsCollide(self):
        '''
        Reduce the lives by one when the player collides with an obstacle
        '''
        global lives
        if player.rect.colliderect(self.rect) and player.invincible == False:    # only triggers if player is not invicible
            screen.fill((255, 0, 0))
            if lives > 0:
                lives -= 1
            player.invincible = True    # invincible state begins

    def laserUpdate(self):
        '''
        Updates the opsition of the top and bottom sprites for the lasers
        '''
        self.topSpriteRect[Y] = self.rect.top - 4
        self.bottomSpriteRect[Y] = self.rect.bottom - self.topSprite.get_height()



# functions

def killToken():
    # Removes "gone" tokens from the token list

    global tokenList
    killList = []
    for tok in range(len(tokenList)):
        if tokenList[tok].gone == True:
            killList.append(tok)    # adds the indices of "gone" platforms to list to be removed

    tokenList = kill(tokenList, killList)
        


def scroll(objects):
    # Adds the scroll speed to the objects to make them change position
    speed = scrollSpeed

    for i in objects:
        i.rect[Y] += speed

def center(objects):
    # Adds to the positions of objects to instantly scroll up
    diff = HEIGHT/1.5 - player.pos[Y]
    for i in objects:
        i.rect[Y] += diff

    
def killPlat(objects):
    # Removes objects that are no longer visible
    killList = []
    for index in range(len(objects)):
        if objects[index - 1].rect[1] > HEIGHT + 500:    # so that lasers will be off the screen when the platforms are removed
            killList.append(index - 1)

    return kill(objects, killList)

def breakPlat():
    # Removes breakable platforms and the objects on them when they are broken
    killList = []
    global platforms
    global tokList
    global obsList
    for plat in range(len(platforms)):
        if platforms[plat].mode == BREAK:
            if platforms[plat].visible == False:
                killList.append(plat)

    platforms = kill(platforms, killList)

    killList = []

    for o in range(len(obsList)):
        if obsList[o].plat not in platforms:
            killList.append(o)

    obsList = kill(obsList, killList)

    
def platsCollide(platform, platforms):
    # Checks if a platform collides with other platforms; returns True if it does collide, False if it does not
    if platform.mode == NORMAL or platform.mode == BREAK:
        for plat in platforms:
            if plat.mode == MOVE:
                if platform.rect.colliderect(plat.pathRect):    # checks if a platform is in the path of any moving platforms
                    return True
            
            if platform.rect.colliderect(plat.rect):
                return True

        return False

    if platform.mode == MOVE:
        if platform.valid:    # only checks if the platform is valid
            for plat in platforms:
                if plat.mode == MOVE:
                        if plat.pathRect.colliderect(platform.pathRect):    # checks if a moving platform's path is in the path of any moving platforms
                            return True
                if plat.rect.colliderect(platform.pathRect):    # checks if any platforms are in the moving platform's path
                    return True

        else:
            return True

    return False

    
def checkPlat(checking):
    # Checks that there is enougth distance between the platform and other platforms
    global platforms
    
    if platsCollide(checking, platforms):
        return True
                
    for plat in platforms:
        distance = dist((plat.rect[X], plat.rect[Y]), (checking.rect[X], checking.rect[Y]))

        if distance < minDist:
            return True

    return False


def genPlat(range1, range2):
    # Generates a platform - will re-generate it if it does not meet the requirements
    global platforms, maxDist, minDist
    
    platType = randint(1, 101)    # determines the theme that the platform will be
    if altitude < 14000:
        spriteType = "grass"
    if altitude >= 14000:
        spriteType = "space"
    
    length = randint(0, 2)    # determines the length of platform it will be
    if length == 0:
        rectLength = 40
    if length == 1:
        rectLength = 50
    if length == 2:
        rectLength = 70

    # generating the platform
    if platType < normalChance:
        invalid = True
        # while loop that wil generate platforms until they fulfill the requirements
        while invalid:
            newRect = Rect(randint(0, WIDTH), randint(range1, range2), rectLength, PLATWIDTH)
            newPlat = Platform(newRect, NORMAL, length, spriteType)
            
            invalid = checkPlat(newPlat)    # loops ends when "invalid" is False

        platforms.append(newPlat)
            
            
    elif platType < normalChance + breakChance:
        invalid = True
        while invalid:
            newRect = Rect(randint(0, WIDTH), randint(range1, range2), rectLength, PLATWIDTH)
            newPlat = Platform(newRect, BREAK, length, spriteType)
            
            invalid = checkPlat(newPlat)
        
        platforms.append(newPlat)
        
        
    elif platType <= normalChance + movingChance + breakChance:
        invalid = True
        while invalid:
            newRect = Rect(randint(0, WIDTH), randint(range1, range2), rectLength, PLATWIDTH)
            newPlat = Platform(newRect, MOVE, length, spriteType)
            
            invalid = checkPlat(newPlat)
        
        if newPlat.valid:    # only appends if the platform if valid
            platforms.append(newPlat)
 

def genTok():
    '''
    Generates a token if a platform is marked for one 
    '''
    for plat in platforms:
        if plat.attribute == "TNT":
            if plat.drawnAtt == False:
                newTok = TNT(plat)    # Generates new TNT object and adds it to the list
                plat.drawnAtt = True
                TNTList.append(newTok)
                
        # Generates new token object and adds it to the list
        if plat.attribute == "jump":
            if plat.drawnAtt == False:
                newTok = Token(plat, JUMP)    
                plat.drawnAtt = True
                tokenList.append(newTok)

        if plat.attribute == "star":
            if plat.drawnAtt == False:
                newTok = Token(plat, STAR)
                plat.drawnAtt = True
                tokenList.append(newTok)

        if plat.attribute == "jetpack":
            if plat.drawnAtt == False:
                newTok = Token(plat, JETPACK)
                plat.drawnAtt = True
                tokenList.append(newTok)

def genObs():
    '''
    Generates an obstacle if a platform is marked for one 
    '''
    for plat in platforms:
        if plat.obstacle == "spike":
                newObs = Obs(plat, SPIKE)    # Generates new obstacle and adds it to the list
                obsList.append(newObs)
        if plat.obstacle == "laser":
            if plat.drawnAtt == False:
                newObs = Obs(plat, LASER)
                plat.drawnAtt = True
                obsList.append(newObs)
                

def kill(list1, killList):
    # removes the elements of "list1" at the indexes of the numbers of the "killList" and returns the resulting list
    for i in killList:
        list1[i] = 0    # sets the elements to zero
    while 0 in list1:
        list1.remove(0)    # removes the zeroes
    return list1






# variables that determine which loop is running
mainRunning = False    # main game running
menuRunning = True    # main menu
instructionsRunning = False    # how to play page
difficultyRunning = False    # difficulty selecting page
gameOverRunning = False    # game over page
quitting = False    # quitting the game
page = "menu"

gameMode = ""

# buttons in the menus
# menus 
menuButtons = [Rect(210, 334, 180, 49), Rect(210, 395, 180, 49)]
instructionsButtons = [Rect(210, 600, 180, 49)]
difficultyButtons = [Rect(210, 192, 180, 49), Rect(210, 257, 180, 49), Rect(210, 322, 180, 49), Rect(210, 458, 180, 49)]
gameOverButtons = [Rect(210, 488, 180, 49)]

highScoreStuff = open("highscore.txt", "a")
highScoreList = open("highscore.txt").read().strip().split("\n")
highScore = int(highScoreList[-1])    # the last element of the file will he the highest number


while page != "quit":    # game will run until the page is set to "quit"
    if page == "menu":
        menuRunning = True
    else:
        menuRunning = False
    if page == "instructions":
        instructionsRunning = True
    else:
        instructionsRunning = False
    if page == "difficulty":
        difficultyRunning = True
    else:
        difficultyRunning = False
    if page == "gameover":
        gameOverRunning = True
    else:
        gameOverRunning = False
    if page == "main":
        mainRunning = True
    else:
        mainRunning = False


# Main menu
    while menuRunning:
        mouseDown = False
        space = False
        down = False
        for evt in event.get():
            if evt.type == QUIT:
                menuRunning = False
                page = "quit"    # sets page to "quit", ending the loop
            if evt.type == MOUSEBUTTONDOWN:
                mouseDown = True
            if evt.type == KEYDOWN:
                if evt.key == K_SPACE:
                    space = True
                if evt.key == K_DOWN:
                    down = True

        mb = mouse.get_pressed()
        mx, my = mouse.get_pos()

        # drawing the menu background
        screen.blit(loadedMenu[0], (0, 0))

        # detecting mouse collisions with buttons
        if menuButtons[0].collidepoint((mx, my)):
            if mouseDown:
                page = "difficulty"
                menuRunning = False

        if menuButtons[1].collidepoint((mx, my)):
            if mouseDown:
                page = "instructions"
                menuRunning = False



        display.flip()

    # instructions
    while instructionsRunning:
        mouseDown = False
        space = False
        down = False
        for evt in event.get():
            if evt.type == QUIT:
                instructionsRunning = False
                page = "quit"
            if evt.type == MOUSEBUTTONDOWN:
                mouseDown = True
            if evt.type == KEYDOWN:
                if evt.key == K_SPACE:
                    space = True
                if evt.key == K_DOWN:
                    down = True

        mb = mouse.get_pressed()
        mx, my = mouse.get_pos()
        
        screen.blit(loadedMenu[1], (0, 0))

        # button-mouse collisions
        if instructionsButtons[0].collidepoint((mx, my)):
            if mouseDown:
                page = "menu"
                instructionsRunning = False


        display.flip()


    # difficulty

    while difficultyRunning:
        mouseDown = False
        space = False
        down = False
        for evt in event.get():
            if evt.type == QUIT:
                difficultyRunning = False
                page = "quit"
            if evt.type == MOUSEBUTTONDOWN:
                mouseDown = True
            if evt.type == KEYDOWN:
                if evt.key == K_SPACE:
                    space = True
                if evt.key == K_DOWN:
                    down = True

        mb = mouse.get_pressed()
        mx, my = mouse.get_pos()
        screen.blit(loadedMenu[2], (0, 0))
        

        if difficultyButtons[3].collidepoint((mx, my)):
            if mouseDown:
                page = "menu"
                difficultyRunning = False

        # setting the difficulty mode
        if difficultyButtons[0].collidepoint((mx, my)):
            if mouseDown:
                gameMode = "easy"
                page = "main"
                difficultyRunning = False

        if difficultyButtons[1].collidepoint((mx, my)):
            if mouseDown:
                gameMode = "normal"
                page = "main"
                difficultyRunning = False

        if difficultyButtons[2].collidepoint((mx, my)):
            if mouseDown:
                gameMode = "hard"
                page = "main"
                difficultyRunning = False


        display.flip()


    written = False
    while gameOverRunning:
        mouseDown = False
        space = False
        down = False
        for evt in event.get():
            if evt.type == QUIT:
                gameOverRunning = False
                page = "quit"
            if evt.type == MOUSEBUTTONDOWN:
                mouseDown = True
            if evt.type == KEYDOWN:
                if evt.key == K_SPACE:
                    space = True
                if evt.key == K_DOWN:
                    down = True

        mb = mouse.get_pressed()
        mx, my = mouse.get_pos()
        screen.blit(loadedMenu[3], (0, 0))
        scoreText = starFnt.render(f"Score: {int(altitude)}", True, (255, 255, 255))    # draws the score to the screen
        screen.blit(scoreText, (300 - scoreText.get_width()/2, 350))

        if int(altitude) > highScore and written == False:    # writes the score to the file if the score is larger than the last value
            highScore = int(altitude)
            written = True
            highScoreStuff.write(str(int(altitude)) + "\n")
        
        scoreText = starFnt.render(f"High Score: {int(highScore)}", True, (255, 255, 0))    # draws the high score to the screen
        screen.blit(scoreText, (300 - scoreText.get_width()/2, 300))
        
        if gameOverButtons[0].collidepoint((mx, my)) and mouseDown:
            page = "menu"
            gameOverRunning = False

        display.flip()



    # setting the starting conditions of the game
    
    jumps = 3
    stars = 0
    lives = 5

    # chances for having a type of platform
    movingChance = 30
    breakChance = 10
    normalChance = 60

    # chances for having an object on a platform
    TNTChance = 10
    jumpChance = 10
    starChance = 3
    jetpackChance = 2
    spikeChance = 10
    laserChance = 10
    spikeHeight = 30
    laserWidth = 15
  
    startingScroll = 3     # the base scrolling speed
    scrollSpeed = startingScroll
    genSpeed = 30    # the speed that the platforms that are generated at

    # setting conditions based on the game mode
    if gameMode == "easy":
        movingChance = 30
        breakChance = 5
        normalChance = 65

        TNTChance = 10
        jumpChance = 20
        starChance = 8
        jetpackChance = 5
        spikeChance = 3
        laserChance = 2
        spikeHeight = 30
        laserWidth = 5

        startingScroll = 1
        scrollSpeed = startingScroll
        genSpeed = 30
        
    if gameMode == "normal":
        movingChance = 40
        breakChance = 20
        normalChance = 40

        TNTChance = 10
        jumpChance = 10
        starChance = 5
        jetpackChance = 3
        spikeChance = 10
        laserChance = 10
        spikeHeight = 30
        laserWidth = 10

        startingScroll = 2
        scrollSpeed = startingScroll
        genSpeed = 30

    if gameMode == "hard":
        movingChance = 40
        breakChance = 40
        normalChance = 20

        TNTChance = 15
        jumpChance = 8
        starChance = 2
        jetpackChance = 1
        spikeChance = 15
        laserChance = 15
        spikeHeight = 30
        laserWidth = 15

        startingScroll = 3
        scrollSpeed = startingScroll
        genSpeed = 30


        

        
    frames = 0     # the number of frames that have passed
    altitude = 0    # the distance that the screen has moves since the game started
    scoreText = fnt.render(str(altitude), False, (255, 255, 255))

    hearts = [Rect(10 + i*40, HEIGHT - 40, 30, 30) for i in range(5)]    # rects representing the number of lives had
    heartsState = [True for i in range(5)]    # list for keeping track of which hearts are filled in
    jumpIcons = [Rect(480 + i*40, HEIGHT - 40, 30, 30) for i in range(3)]    # same function as previous two lists
    jumpState = [True for i in range(3)]

    player = Player([200, 400], Rect(200, 400, 57, 81))    # player object that is what the user controls
    ground = Platform(Rect(200, 500, 70, 35), NORMAL, 2, "grass")    # starting platform that the player spawns on
    ground.attribute = "none"    # setting the base platform to not having anything on it
    ground.obstacle = "none"
    platforms = [ground]    # list that stores all platforms that will be drawn to the screen
    
    TNTList = []    # list for all the TNT objects
    tokenList = []    # list for all the token objects
    obsList = []    # list for all the obstacles
    timer = 0

    background = loadedBack[1]    # starting background
    listList = [platforms, TNTList, tokenList, obsList]    # list for all the main lists that are drawn

    for i in range(9):    # generates starting platforms
        genPlat(0, 500)

    while mainRunning:
        space = False
        down = False
        spaceUp = False
        for evt in event.get():
            if evt.type == QUIT:
                mainRunning = False
                page = "quit"
            if evt.type == KEYDOWN:
                if evt.key == K_SPACE:
                    space = True
                if evt.key == K_DOWN:
                    down = True
            if evt.type == KEYUP:
                if evt.key == K_SPACE:
                    spaceUp = True
                    
        frames += 1

        # set the list for jumps and hearts to False so it can be updated
        for i in range(len(heartsState)):
            heartsState[i] = False
        for i in range(len(jumpState)):
            jumpState[i] = False

        # sets the changing background based on altitude
        if altitude >= 10000:
            background = loadedBack[2]
        if altitude >= 14000:
            background = loadedBack[3]
        if altitude >= 15000:
            background = loadedBack[0]
            
        screen.blit(background, (0, 0))    # draws the background
        
        
        for lis in listList:    # does the things that apply to almost all game objects
            scroll(lis)
            killPlat(lis)
        
        player.pos[Y] += scrollSpeed    # also scrolls the player

        
        if player.pos[Y] <= -60:    # re-centers the screen if the player goes off from the top
            for i in range(7):
                genPlat(-600, -300)    # generates more platforms so there is no big gap
            for lis in listList:
                center(lis)

            diff = HEIGHT/1.5 - player.pos[Y]
            player.pos[Y] += diff
            altitude += diff    # adds the change to the score
            
            
        # speeds up the platform generation rate as the scrolling speeds up so the density stays the same
        if scrollSpeed == startingScroll:
            genSpeed = 30
        if scrollSpeed == startingScroll + 1:
            genSpeed = 20
        if scrollSpeed == startingScroll + 2:
            genSpeed = 15
        
        if frames%genSpeed == 0:    # generates the platforms
            genPlat(-300, -20)

        genTok()    # generates the tokens and obstacles
        genObs()

        # updating the player's conditions  
        if space:
            player.playerJump()
        if spaceUp:
            player.jumpCancel()    # cancels the jump if the spacebar is released

        player.move()
        player.spriteChange()
        if player.jetpack:
            player.jetpacking()
        player.collide(platforms)
        player.invincibility()
        screen.blit(player.sprite, player.rect)

        
        breakPlat()    # update breakable platforms
        killToken()    # remove consumed tokens from list


        # drawing obstacles and tokens
        for obst in obsList:
            if obst.mode == SPIKE:
                screen.blit(obst.sprite, (obst.rect[X], obst.rect[Y]))
            if obst.mode == LASER:
                obst.laserUpdate()
                draw.rect(screen, obst.colour, obst.rect)
                screen.blit(obst.topSprite, obst.topSpriteRect)
                screen.blit(obst.bottomSprite, obst.bottomSpriteRect)
            obst.obsCollide()

        for tok in tokenList:
            screen.blit(tok.sprite, (tok.rect[X], tok.rect[Y]))

            # calls the functions for the tokens
            if tok.mode == JUMP:
                tok.doubJumpTok()
            if tok.mode == STAR:
                tok.starTok()
            if tok.mode == JETPACK:
                tok.jetpackTok()


        for plat in platforms:
                # drawing platforms and calling platform functions
                if plat.mode == NORMAL:
                    if plat.spriteType == "grass":
                        if plat.length == 50:
                            screen.blit(plat.sprite, (plat.rect[X], plat.rect[Y] - 10))    # offsets the drawing of the sprite so the player can stand on the surface of the sprite
                        elif plat.length == 70:
                            screen.blit(plat.sprite, (plat.rect[X], plat.rect[Y] - 15))
                        else:
                            screen.blit(plat.sprite, (plat.rect[X], plat.rect[Y]))
                        
                    if plat.spriteType == "space":
                        screen.blit(plat.sprite, (plat.rect[X], plat.rect[Y]))
                if plat.mode == BREAK:

                    plat.breakMode(player)    # updates broken platforms

                    if plat.visible:
                        screen.blit(plat.sprite, (plat.rect[X], plat.rect[Y]))
                        
                if plat.mode == MOVE:
                    plat.moveMode()   # updates the conditions of moving platforms
                    plat.pathUpdate()
                    
                    if plat.spriteType == "grass":
                        if plat.length == 50:
                            screen.blit(plat.sprite, (plat.rect[X], plat.rect[Y] - 10))
                        elif plat.length == 70:
                            screen.blit(plat.sprite, (plat.rect[X], plat.rect[Y] - 15))
                        else:
                            screen.blit(plat.sprite, (plat.rect[X], plat.rect[Y]))
                        
                    if plat.spriteType == "space":
                        screen.blit(plat.sprite, (plat.rect[X], plat.rect[Y]))


        # drawing TNT
        if TNTList:
            for i in range(len(TNTList)):
                if i < len(TNTList):
                    screen.blit(TNTList[i].sprite, (TNTList[i].rect[X], TNTList[i].rect[Y]))
                    TNTList[i].explode()
                    if TNTList[i].exploded == True:
                        TNTList = kill(TNTList, [i])    # removes exploded TNT from the list


        # updates the hearts and jumps drawn
        for i in range(lives):
            if lives > 0:
                heartsState[i] = True

        for i in range(jumps):
            if jumps > 0:
                jumpState[i] = True

        # draws the hearts and jumps based on the list of heart/jump states: True for filled in, False for empty
        for i in range(len(heartsState)):
            if heartsState[i] == True:
                screen.blit(loadedIcons[2], hearts[i])
            if heartsState[i] == False:
                screen.blit(loadedIcons[3], hearts[i])

        for i in range(len(jumpState)):
            if jumpState[i] == True:
                screen.blit(loadedIcons[0], jumpIcons[i])
            if jumpState[i] == False:
                screen.blit(loadedIcons[1], jumpIcons[i])
                                
        
        if lives == 0 or player.pos[Y] > 1000:    # the game ends when the player loses all their lives or goes off the bottom of the screen
            page = "gameover"
            mainRunning = False

        if stars == 4:    # slows the scrolling down when the player obtains 4 stars
            stars = 0
            scrollSpeed = startingScroll
        
        if scrollSpeed < startingScroll + 2:
            timer += 1

            if timer%(5*FPS) == 0:    # adds to the scroll speed after some amount of time
                scrollSpeed += 1
                timer = 0

        # draw score to the screen
        scoreText = fnt.render(str(int(altitude)), True, (255, 255, 255))
        screen.blit(scoreText, (300 - scoreText.get_width()/2, 60))
        
        # draw star counter
        starText = starFnt.render(f"{stars}/4", True, (255, 255, 0))
        screen.blit(starText, (320, HEIGHT - 40))
        screen.blit(loadedToks[2], (275, HEIGHT - 45))
    
        altitude += scrollSpeed    # update the current altitude
        myClock.tick(FPS)

        display.flip()

highScoreStuff.close()
quit()
        



















