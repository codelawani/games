r'''
                            _        __   __   ___       ___
                           / /     /  / /  /  / __ \   / __ \ 
                          / /     /  / /  /  / / / /  / / / /
                         / /_ _  /  / /  /  / /_/ /  / /_/ /
                        /_ _ _/  \_ _ _ /  /_ _ _/   \_ _ /
'''

# Importing Modules

from time import sleep
import pygame
from   pygame import mixer
import random
import time
import logging
from rich.console import Console


console = Console()

# Initializing pygame

pygame.init()
pygame.display.set_caption("Ludo")
screen = pygame.display.set_mode((680, 600))

# Loading Images
board = pygame.image.load('Board.jpg')
star  = pygame.image.load('star.png')
one   = pygame.image.load('1.png')
two   = pygame.image.load('2.png')
three = pygame.image.load('3.png')
four  = pygame.image.load('4.png')
five  = pygame.image.load('5.png')
six   = pygame.image.load('6.png')
dice_idle = pygame.image.load('Idle.png')

red    = pygame.image.load('red.png')
blue   = pygame.image.load('blue.png')
green  = pygame.image.load('green.png')
yellow = pygame.image.load('yellow.png')

DICE  = [one, two, three, four, five, six]
color = [red, green, yellow, blue]

# Loading Sounds

killSound   = mixer.Sound("Killed.wav")
tokenSound  = mixer.Sound("Token Movement.wav")
diceSound   = mixer.Sound("Dice Roll.wav")
winnerSound = mixer.Sound("Reached Star.wav")

# Initializing Variables

number        = 1
currentPlayer = 3
playerKilled  = False
diceRolled    = False
winnerRank    = []
has_started = False

# Rendering Text

font = pygame.font.Font('freesansbold.ttf', 11)
FONT = pygame.font.Font('freesansbold.ttf', 16)
currentPlayerText = font.render('Current Player', True, (0, 0, 0))
line = font.render('------------------------------------', True, (0, 0, 0))

# Defining Important Coordinates

HOME = [[(110, 58),  (61, 107),  (152, 107), (110, 152)],  # Red
        [(466, 58),  (418, 107), (509, 107), (466, 153)],  # Green
        [(466, 415), (418, 464), (509, 464), (466, 510)],  # Yellow
        [(110, 415), (61, 464),  (152, 464), (110, 510)]]  # Blue
"The coordinates of the home position."

        # Red      # Green    # Yellow    # Blue
SAFE = [(50, 240), (328, 50), (520, 328), (240, 520),
        (88, 328), (240, 88), (482, 240), (328, 482)]
"The coordinates of safe zones."

position = [[[110, 58],  [61, 107],  [152, 107], [110, 152]],  # Red
            [[466, 58],  [418, 107], [509, 107], [466, 153]],  # Green
            [[466, 415], [418, 464], [509, 464], [466, 510]],  # Yellow
            [[110, 415], [61, 464],  [152, 464], [110, 510]]]  # Blue
"The positions of each piece on the board."

jump = {(202, 240): (240, 202),  # R1 -> G3
        (328, 202): (368, 240),  # G1 -> Y3
        (368, 328): (328, 368),  # Y1 -> B3
        (240, 368): (202, 328)}  # B1 -> R3
"The coordinates of the jump."

         # Red        # Green     # Yellow    # Blue
WINNER = [[240, 284], [284, 240], [330, 284], [284, 330]]
"The coordinates of the winner position."

is_idle = True
"Used to check if the dice is idle."

# Blit Token Movement

def move_player(x, y):
    """This function is used to blit the token movement."""
    console.log(f"move_player({x}, {y})")
    screen.fill((255, 255, 255))
    screen.blit(board, (0, 0))

    for i in SAFE[4:]:
        screen.blit(star, i)

    console.log(f"move_player(): displaying tokens")
    for i in range(len(position)):
        for j in position[i]:
            screen.blit(color[i], j)


    if position[x][y] in WINNER:
        winnerSound.play()
    else:
        tokenSound.play()

    console.log(f"move_player(): bliting current player")
    screen.blit(color[currentPlayer], (620, 28))
    screen.blit(currentPlayerText, (600, 10))
    screen.blit(line, (592, 59))

    console.log(f"move_player(): updating display")
    for i in range(len(winnerRank)):
        rank = FONT.render(f'{i+1}.', True, (0, 0, 0))
        screen.blit(rank, (600, 85 + (40*i)))
        screen.blit(color[winnerRank[i]], (620, 75 + (40*i)))

    pygame.display.update()
    sleep(0.2)

# Bliting in while loop

def blit_all():

    for i in SAFE[4:]:
        screen.blit(star, i)

    for i in range(len(position)):
        for j in position[i]:
            screen.blit(color[i], j)

    if is_idle:
        screen.blit(dice_idle, (605, 270))
    else:
        screen.blit(DICE[number-1], (605, 270))

    if has_started:
        screen.blit(color[currentPlayer], (620, 28))
        screen.blit(currentPlayerText, (600, 10))
        screen.blit(line, (592, 59))

    for i in range(len(winnerRank)):
        rank = FONT.render(f'{i+1}.', True, (0, 0, 0))
        screen.blit(rank, (600, 85 + (40*i)))
        screen.blit(color[winnerRank[i]], (620, 75 + (40*i)))


def to_home(x, y) -> bool:
    """This function is used to check if the token is in the home position."""
    #  R2
    if (position[x][y][1] == 284 and position[x][y][0] <= 202 and x == 0) \
            and (position[x][y][0] + 38*number > WINNER[x][0]):
        return False

    #  Y2
    elif (position[x][y][1] == 284 and 368 < position[x][y][0] and x == 2) \
            and (position[x][y][0] - 38*number < WINNER[x][0]):
        return False
    #  G2
    elif (position[x][y][0] == 284 and position[x][y][1] <= 202 and x == 1) \
            and (position[x][y][1] + 38*number > WINNER[x][1]):
        return False
    #  B2
    elif (position[x][y][0] == 284 and position[x][y][1] >= 368 and x == 3) \
            and (position[x][y][1] - 38*number < WINNER[x][1]):
        return False
    return True

# Moving the token

def move_token(x, y):
    """This function is used to move the token."""
    global currentPlayer, diceRolled, is_idle

    # Taking Token out of HOME
    if tuple(position[x][y]) in HOME[currentPlayer] and number == 6:
        position[x][y] = list(SAFE[currentPlayer])
        tokenSound.play()
        diceRolled = False

    # Moving token which is not in HOME
    elif tuple(position[x][y]) not in HOME[currentPlayer]:
        diceRolled = False

        # Way to WINNER position

        #  R2
        if (position[x][y][1] == 284 and position[x][y][0] <= 202 and x == 0) \
                and (position[x][y][0] + 38*number <= WINNER[x][0]):
            for i in range(number):
                position[x][y][0] += 38
                move_player(x, y)

        #  Y2
        elif (position[x][y][1] == 284 and 368 < position[x][y][0] and x == 2) \
                and (position[x][y][0] - 38*number >= WINNER[x][0]):
            for i in range(number):
                position[x][y][0] -= 38
                move_player(x, y)

        #  G2
        elif (position[x][y][0] == 284 and position[x][y][1] <= 202 and x == 1) \
                and (position[x][y][1] + 38*number <= WINNER[x][1]):
            for i in range(number):
                position[x][y][1] += 38
                move_player(x, y)
        #  B2
        elif (position[x][y][0] == 284 and position[x][y][1] >= 368 and x == 3) \
                and (position[x][y][1] - 38*number >= WINNER[x][1]):
            for i in range(number):
                position[x][y][1] -= 38
                move_player(x, y)

        # Other Paths
        else:
            for _ in range(number):

                #  R1, Y3
                if (position[x][y][1] == 240 and position[x][y][0] < 202) \
                        or (position[x][y][1] == 240 and 368 <= position[x][y][0] < 558):
                    position[x][y][0] += 38
                # R3 -> R2 -> R1
                elif (position[x][y][0] == 12 and position[x][y][1] > 240):
                    position[x][y][1] -= 44

                #  R3, Y1
                elif (position[x][y][1] == 328 and 12 < position[x][y][0] <= 202) \
                        or (position[x][y][1] == 328 and 368 < position[x][y][0]):
                    position[x][y][0] -= 38
                #  Y3 -> Y2 -> Y1
                elif (position[x][y][0] == 558 and position[x][y][1] < 328):
                    position[x][y][1] += 44

                #  G3, B1
                elif (position[x][y][0] == 240 and 12 < position[x][y][1] <= 202) \
                        or (position[x][y][0] == 240 and 368 < position[x][y][1]):
                    position[x][y][1] -= 38
                # G3 -> G2 -> G1
                elif (position[x][y][1] == 12 and 240 <= position[x][y][0] < 328):
                    position[x][y][0] += 44

                #  B3, G1
                elif (position[x][y][0] == 328 and position[x][y][1] < 202) \
                        or (position[x][y][0] == 328 and 368 <= position[x][y][1] < 558):
                    position[x][y][1] += 38
                #  B3 -> B2 -> B1
                elif (position[x][y][1] == 558 and position[x][y][0] > 240):
                    position[x][y][0] -= 44
                
                else:
                    for i in jump:
                        if position[x][y] == list(i):
                            position[x][y] = list(jump[i])
                            break

                move_player(x, y)

        if not number == 6:
            currentPlayer = (currentPlayer + 1) % 4
            is_idle = True
            console.log("DICE is idle")

        # Killing Player
        if tuple(position[x][y]) not in SAFE:
            for i in range(len(position)):
                for j in range(len(position[i])):
                    if position[i][j] == position[x][y] and i != x:
                        position[i][j] = list(HOME[i][j])
                        killSound.play()
                        currentPlayer = (currentPlayer+3) % 4


# Checking Winner
def check_winner():
    global currentPlayer
    if currentPlayer not in winnerRank:
        for i in position[currentPlayer]:
            if i not in WINNER:
                return
        winnerRank.append(currentPlayer)
    else:
        currentPlayer = (currentPlayer + 1) % 4


# Main LOOP
running = True
while(running):
    screen.fill((255, 255, 255))
    screen.blit(board, (0, 0)) # Bliting Board

    check_winner()

    for event in pygame.event.get():

        # Event QUIT
        if event.type == pygame.QUIT:
            running = False

        # When MOUSEBUTTON is clicked
        if event.type == pygame.MOUSEBUTTONUP:
            coordinate = pygame.mouse.get_pos()

            # Rolling Dice
            if not diceRolled and (605 <= coordinate[0] <= 669) and (270 <= coordinate[1] <= 334):
                is_idle = False
                number = random.randint(1, 6)
                diceSound.play()
                flag = True
                for i in range(len(position[currentPlayer])):
                    if tuple(position[currentPlayer][i]) not in HOME[currentPlayer] and to_home(currentPlayer, i):
                        flag = False
                        break
                if (flag and number == 6) or not flag:
                    diceRolled = True
                    console.log("dice 🎲 is not idle")
                else:
                    is_idle = False
                    blit_all()
                    if not has_started:
                        currentPlayer = (currentPlayer+1) % 4
                        screen.blit(currentPlayerText, (600, 10))
                        screen.blit(color[currentPlayer], (620, 28))
                        screen.blit(line, (592, 59))
                    pygame.display.update()
                    sleep(0.4)
                    has_started = True
                    console.log("dice is rolled but not moved")
                    currentPlayer = (currentPlayer+1) % 4
                    is_idle = True
                    console.log("dice 🎲 is idle")

            # Moving Player
            elif diceRolled:
                for j in range(len(position[currentPlayer])):
                    if position[currentPlayer][j][0] <= coordinate[0] <= position[currentPlayer][j][0]+31 \
                            and position[currentPlayer][j][1] <= coordinate[1] <= position[currentPlayer][j][1]+31:
                        move_token(currentPlayer, j)
                        break

    blit_all()

    pygame.display.update()
