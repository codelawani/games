from termcolor import colored, cprint
import random


def assign_bead_colors(players):
    """Assigns different colors to each player's bead.
        players: dictionary(name -> [bead,position])
        returns: dictionary(bead -> color)"""

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
        players: dictionary(name -> [bead,position])
        board: list of numbers(use prepare_board() function
        returns: None
        """
    snakes = {16: 4, 33: 20, 48: 24, 62: 56, 78: 69, 94: 16, 99: 9}
    ladders = {3: 12, 7: 23, 20: 56, 47: 53, 60: 72, 80: 94}

    # creates a dictionary (position -> (bead))
    # list is used due possibility of many beads at a position

    bead_place = {}
    for i in players:
        bead = players[i][0]
        position = players[i][1]
        if position in bead_place:
            bead_place[position].append(bead)
        else:
            bead_place[position] = list(bead)
    print("".center(111, "-"))
    for i in board:
        print("|", end="")
        for j in i:
            if int(j) in bead_place:
                print(j.rjust(6), end="")
                for k in bead_place[int(j)]:
                    cprint(k, colors[k],
                           None, attrs=["bold"], end="")
                print("".ljust(4 - len(bead_place[int(j)])), end="")
            else:
                if int(j) in snakes:
                    print(j.rjust(6), end="")
                    cprint("∫", "white", None,
                           attrs=["blink", "bold"], end="")
                    print(" "*3, end="")
                elif int(j) in ladders:
                    print(j.rjust(6), end="")
                    cprint("†", "yellow", None,
                           attrs=["blink", "bold"], end="")
                    print(" "*3, end="")
                else:
                    print(j.center(10), end="")
            print("|", end="")
        print()
        print("".center(111, "-"))


def update_players(players, name, dice):
    """ updates the position of the the players
        players: dict(name -> [bead,number])
        dice: list
        returns: dict(name -> [bead,number]) """
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
        print(f"A snake ∫ is found on \"{is_snake(player_p + dice)[0]}\" and \
              you've been  bitten ...")
        print(f"Went to {is_snake(player_p + dice)[1]}.\n")
        players[name][1] = is_snake(player_p + dice)[1]
    elif is_ladder(player_p + dice):
        print("Wow! A ladder has been discovered... \nQuickly climb it!")
        print(
            f"Climbed up to \"{is_ladder(player_p + dice)[1]}\".\n")
        players[name][1] = is_ladder(player_p + dice)[1]
    elif players[name][1] + dice < 101:
        players[name][1] += dice


def get_player_count(prompt):
    """Prompts the user to enter the number of players,
        and validates the input."""

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
    """Creates a dictionary of players with their
        bead and starting position."""

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
        print(f"Your bead is: {colored(beads[i], 'blue', None, ['bold'])}")
    return players


def get_random_player_order(players):
    """Randomly shuffle the order of players in a game.

    Args:
    players (dict): A dictionary with the names
        of players as keys and a list of
        their bead and current position as values.

    Returns:
    list: A shuffled list of the player names.
    """
    random_players = list(players.keys()).copy()
    random.shuffle(random_players)
    return random_players


def check_game_over(players):
    """Check whether the game is over by checking if
        any player has reached the winning position.

    Args:
    players (dict): A dictionary with the names
        of players as keys and a list of
        their bead and current position as values.

    Returns:
    tuple: A tuple containing a Boolean value and
        the name of the winning player, if any.
        The Boolean value is True
        if the game is over and False otherwise.
    """
    for player_name, (bead, position) in players.items():
        if position >= 100:
            return (False, None)
    return (True, player_name)


def dice(chance):
    """
    This function takes an integer value 'chance' as input and
    prints a graphical representation of a dice with 'chance'
    number of dots on its face. The output is printed in the
    terminal using the `cprint` function from the `termcolor` library.

    Parameters:
    ----------
    chance: int
        The number of dots to display on the face of the dice.
        This value must be an integer between 1 and 6 (inclusive).

    Returns:
    -------
    None
    """
    dots = {1: ["     ", "  *  ", "     "],
            2: ["*    ", "     ", "    *"],
            3: ["*    ", "  *  ", "    *"],
            4: ["*   *", "     ", "*   *"],
            5: ["*   *", "  *  ", "*   *"],
            6: ["*   *", "*   *", "*   *"]}

    print("".center(9, "_"))
    for i in range(3):
        print("|", end="")
        cprint(dots[chance][i].center(7), "yellow", attrs=["bold"], end="")
        print("|")
    print("".center(9, "-"), "\n")


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
    # assign different color to the beads
    colors = assign_bead_colors(players)
    # randomly assign the players chances
    random_chances = get_random_player_order(players)
    # counter to keep track of the chances
    counter = 0
    # while all the player position <= 100
    while check_game_over(players)[0]:
        # show the board with the beads
        display_board(players, prepare_board(), colors)
        # print whose chance is this and roll the dice
        active_player = random_chances[counter % len(players)]
        # current player's bead
        active_player_bead = players[active_player][0]
        # colored bead of the current player
        colorBead = colored(
            active_player_bead, colors[active_player_bead], None, ["bold"])
        player = active_player.capitalize()
        print("To roll the dice, Type r and click Enter")
        print("To quit the game, Type q and click Enter")

        prompt = f"It's {player}'s {colorBead} chance:\nroll the DICE: "
        player_input = input(prompt).lower().strip()
        if player_input == "r":
            current_chance = random.randrange(1, 7)
            print("\nROLLING ...\n")
            colored_chance = colored(current_chance, "blue", None, [
                                     "bold", "underline"])
            print(f'It\'s a {colored_chance} !.')
            # show the dice image
            dice(current_chance)
            # see whose chance is this, roll the dice
            # and move the player's bead
            update_players(players, active_player, current_chance)
            if not (check_game_over(players)[0]):
                display_board(players, prepare_board(), colors)
        elif player_input == "q":
            cprint(" You quit!!! ".center(50, "="), "red", attrs=["bold"])
            cprint("GAME OVER! Come back next time :)".center(50),
                   "black", attrs=["bold"])
            exit()
        else:
            print("You missed ur chance because you did'nt roll the dice !!")
        # increase the counter
        counter += 1
    print("\n\nGAME OVER, {%s} is the winner\n\n".format(colored(
        check_game_over(players)[1], "white", None, ["bold", "underline"])))


if __name__ == '__main__':
    try:
        play_game()
    except (EOFError, KeyboardInterrupt):
        print("\nGame ended")
        exit()
