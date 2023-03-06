import termcolor as tc
import random
import colorama
colorama.init()


def assign_bead_colors(players):
    """Assigns different colors to each player's bead.
        players: dictionary(name -> [beed,position])
        returns: dictionary(beed -> color)"""

    colors = ["red", "green", "cyan", "magenta"]
    random.shuffle(colors)
    bead_colors = {}
    for player_name, (bead, _) in players.items():
        bead_colors[bead] = colors.pop()
    return bead_colors


def prepare_board():
    """ make board in form of nested lists
        returns: nested lists  """

    board = []
    temp = []
    for i in range(100, 0, -1):
        temp.append(str(i))
        if (i-1) % 10 == 0:
            if len(board) % 2:
                temp.reverse()
            board.append(temp)
            temp = []
    return board


def display_board(players, board, colors):
    """ prints the board in a pretty manner
        players: dictionary(name -> [beed,position])
        board: list of numbers(use prepare_board() function
        returns: None
        """
    snakes = {16: 4, 33: 20, 48: 24, 62: 56, 78: 69, 94: 16, 99: 9}
    ladders = {3: 12, 7: 23, 20: 56, 47: 53, 60: 72, 80: 94}

    # creates a dictionary (position -> (beed)) list is used due possibility of many beeds at a position
    # players:{'nico': ['*', 1], 'dav': ['#', 1]}
    # beed_place:{1: ['*', '#']}
    beed_place = {}
    for i in players:
        if players[i][1] in beed_place:
            beed_place[players[i][1]].append(players[i][0])
        else:
            beed_place[players[i][1]] = list(players[i][0])
    print(f"pl:{players}")
    print("".center(111, "-"))
    for i in board:
        print("|", end="")
        for j in i:
            if int(j) in beed_place:
                print(j.rjust(6), end="")
                for k in beed_place[int(j)]:
                    print(tc.colored(k, colors[k],
                          None, attrs=["bold"]), end="")
                print("".ljust(4 - len(beed_place[int(j)])), end="")
            else:
                if int(j) in snakes:
                    print(j.rjust(6), end="")
                    print(tc.colored("∫", "white", None,
                          attrs=["blink", "bold"]), end="")
                    print(" "*3, end="")
                elif int(j) in ladders:
                    print(j.rjust(6), end="")
                    print(tc.colored("†", "yellow", None,
                          attrs=["blink", "bold"]), end="")
                    print(" "*3, end="")
                else:
                    print(j.center(10), end="")
            print("|", end="")
        print()
        print("".center(111, "-"))
    print(f"bp:{beed_place}")


def update_players(players, name, dice):
    """ updates the position of the the players
        players: dict(name -> [beed,number])
        dice: list
        returns: dict(name -> [beed,number]) """
    def is_snake(position):
        snakes = {16: 4, 33: 20, 48: 24, 62: 56, 78: 69, 94: 16, 99: 9}
        if position in snakes:
            return (position, snakes[position])

    def is_ladder(position):
        ladders = {3: 12, 7: 23, 20: 56, 47: 53, 60: 72, 80: 94}
        if position in ladders:
            return (position, ladders[position])

    player_p = players[name][1]
    if is_snake(player_p + dice):
        print("A snake ∫ is found on \"%d\" and it bites you ..." %
              (is_snake(player_p + dice)[0]))
        print("Went to %d.\n" % (is_snake(player_p + dice)[1]))
        players[name][1] = is_snake(player_p + dice)[1]
    elif is_ladder(player_p + dice):
        print("WooW!! a ladder is found...\nClimb it fast...")
        print("Climbed up to \"%d\".\n" % (is_ladder(player_p + dice)[1]))
        players[name][1] = is_ladder(player_p + dice)[1]
    elif players[name][1] + dice < 101:
        players[name][1] += dice


def get_player_count(prompt):
    """Prompts the user to enter the number of players, and validates the input."""

    while True:
        try:
            player_count = int(input(prompt))
            if player_count < 1:
                print("Invalid input: number of players must be at least 1.\n")
            elif player_count > 4:
                print("Sorry, we can't accommodate more than 4 players.\n")
            else:
                return player_count
        except ValueError:
            print("Invalid input: please enter a number.\n")


def create_player_dict(num_players):
    """Creates a dictionary of players with their bead and starting position."""

    def get_player_name(players, prompt):
        """Prompts the user to enter a player name, and validates it."""

        while True:
            name = input(prompt).lower().strip()
            if name not in players:
                return name
            else:
                print("That name is already taken. Please try another name.")

    players = {}
    rankings = ["first", "second", "third", "fourth"]
    beads = ["@", "#", "%", "*"]
    random.shuffle(beads)
    for i in range(num_players):
        player_name = get_player_name(
            players, f"Enter {rankings[i]} player's name: ")
        players[player_name] = [beads[i], 1]
        print(f"Your bead is: {tc.colored(beads[i], 'blue', None, ['bold'])}")
    return players


def get_random_player_order(players):
    """Randomly shuffle the order of players in a game.

    Args:
    players (dict): A dictionary with the names of players as keys and a list of
        their bead and current position as values.

    Returns:
    list: A shuffled list of the player names.
    """
    random_players = list(players.keys()).copy()
    random.shuffle(random_players)
    return random_players


def check_game_over(players):
    """Check whether the game is over by checking if any player has reached the winning position.

    Args:
    players (dict): A dictionary with the names of players as keys and a list of
        their bead and current position as values.

    Returns:
    tuple: A tuple containing a Boolean value and the name of the winning player,
        if any. The Boolean value is True if the game is over and False otherwise.
    """
    for player_name, (bead, position) in players.items():
        if position >= 100:
            return (False, None)
    return (True, player_name)


def dice(chance):
    print("".center(9, "_"))

    print("|", end="")
    if chance == 4 or chance == 6 or chance == 5:
        print(tc.colored("*   *".center(7), "yellow",
              None, attrs=["bold"]), end="")
    elif chance == 2:
        print(tc.colored("*".center(7), "yellow",
              None, attrs=["bold"]), end="")
    elif chance == 3:
        print(tc.colored("*".rjust(7), "yellow", None, attrs=["bold"]), end="")
    elif chance == 1:
        print("".rjust(7), end="")
    print("|")

    print("|", end="")
    if chance == 4 or chance == 6:
        print(tc.colored("*   *".center(7), "yellow",
              None, attrs=["bold"]), end="")
    elif chance == 3 or chance == 5:
        print(tc.colored("*".center(7), "yellow",
              None, attrs=["bold"]), end="")
    elif chance == 2 or chance == 1:
        print(tc.colored("*".center(7), "yellow", None, ["bold"]), end="")
    print("|")

    if chance != 4 and chance != 2:
        print("|", end="")
        if chance == 5 or chance == 6:
            print(tc.colored("*   *".center(7), "yellow",
                  None, attrs=["bold"]), end="")
        elif chance == 1:
            print("".center(7), end="")
        elif chance == 3:
            print(tc.colored("*".ljust(7), "yellow",
                  None, attrs=["bold"]), end="")
        print("|")

    print("".center(9, "-"), "\n")


""" def dice(chance):
    dots = {1: ["     ", "  *  ", "     "],
            2: ["*    ", "     ", "    *"],
            3: ["*    ", "  *  ", "    *"],
            4: ["*   *", "     ", "*   *"],
            5: ["*   *", "  *  ", "*   *"],
            6: ["* * *", "     ", "* * *"]}

    print("".center(9, "_"))
    for i in range(3):
        print("|", end="")
        print(dots[chance][i].center(7), end="")
        print("|")
    print("".center(9, "-"), "\n") """


def play_game():

    print("\n"+"WELCOME TO".center(50, "."), "\n")
    print(r"""        /\		     |-----|
       //\\                  |-----|
       ||                    |-----|
       || SNAKES     and     |-----| LADDERS
       ||                    |-----|
    \\//                     |-----|
     \/	                     |-----|
    """)
    # ask user how many players (must be less than <=4)
    numbers = get_player_count("\nHow many people want to play:")
    # make dict of players
    players = create_player_dict(numbers)
    print(players)
    # assign different color to the beads
    colors = assign_bead_colors(players)
    # randomly assign the players chances
    random_chances = get_random_player_order(players)
    # counter to keep track of the chances
    counter = 0
    # while all the player position <= 100
    while check_game_over(players)[0]:
        # show the board with the beeds
        display_board(players, prepare_board(), colors)
        # print whose chance is this and roll the dice
        crrnt_plyr = random_chances[counter % len(players)]
        # current player's beed
        crrnt_plyr_beed = players[crrnt_plyr][0]
        # colored beed of the current player
        crrnt_plyr_clr = tc.colored(
            crrnt_plyr_beed, colors[crrnt_plyr_beed], None, ["bold"])
        if input("It's %s's %s chance:\nroll the DICE: " % (crrnt_plyr.capitalize(), crrnt_plyr_clr)).lower().strip() == "roll".lower().strip():
            current_chance = random.randrange(1, 7)
            print("\nROLLING ...\n")
            print("It's a %s !." % (tc.colored(
                current_chance, "blue", None, ["bold", "underline"])))
            # show the dice image
            dice(current_chance)
            # see whose chance is this, roll the dice and move the player's beed
            update_players(players, crrnt_plyr, current_chance)
            if not (check_game_over(players)[0]):
                display_board(players, prepare_board(), colors)
        else:
            print("Your chance is dismissed because you did'nt roll the dice !!")
        # increase the counter
        counter += 1
    print("\n\nCONGO, %s is the winner\n\n" % (tc.colored(
        check_game_over(players)[1], "white", None, ["bold", "underline"])))


if __name__ == '__main__':
    play_game()
