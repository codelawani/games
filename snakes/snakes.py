import random
import sys
import pydoc
try:
    from termcolor import colored, cprint
except (ModuleNotFoundError):
    print("You need To install termcolor, Enter:\n\
          pip install termcolor")
    exit()

HELP = """
Welcome to the game of Snake and Ladder!

In this game, your objective is to reach the end of the board by rolling a dice and moving forward.

The board is a grid of squares, numbered from 1 to 100.
Some squares have ladders on them, which allow you to climb up the board and skip ahead several spaces.
Other squares have snakes on them, which force you to slide down the board and lose progress.

To start playing, each player is randomly given a token and places it on the starting square.
Players take turns rolling the dice and moving their token forward the number of spaces indicated by the dice roll.

If you land on a ladder space, you get to climb up the board to a higher space.
If you land on a snake space, you have to slide down the board to a lower space.

If you land on the last square of the board, you win the game!

Tips and Strategies:
- Try to land on ladder spaces as often as possible to skip ahead on the board.
- Avoid landing on snake spaces, as they will send you back down the board.
- If you roll a high number, you can strategize to move backward in order to land on a ladder space.

To play the game, you can use the following commands:
- Roll the dice: type 'r'.
- Quit the game: type 'q'.
- Quit this doc: type 'q'.

Have fun playing!
"""


def assign_bead_colors(players):
    """
    Assigns a unique color to each player's bead.

    Args:
        players (dict): A dictionary that maps player
        names to a list of their bead and position.

    Returns:
        dict: A dictionary that maps each bead to a
        unique color chosen from a list of predefined colors.
    """

    colors = ["red", "green", "cyan", "magenta"]
    random.shuffle(colors)
    bead_colors = {}
    for player_name, (bead, _) in players.items():
        bead_colors[bead] = colors.pop()
    return bead_colors


def prepare_board():
    """
    Generates a game board as a nested list.

    Returns:
    - board: A nested list representing the game board.
            The list contains 10 sub-lists, each with 10 elements.
            The elements are string representations
            of numbers from 100 to 1, arranged in a serpentine pattern.
    """

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
    """
    Displays a game board with player positions, ladders, and snakes.

    Args:
    - players: A dictionary containing player names mapped
                to a list of bead and position.
                dictionary(name -> [bead,position])
    - board: A list of list of numbers representing the game board.
            Use the prepare_board() function to generate the board.
    - colors: A dictionary containing bead mapped to colors.

    Returns: None
    """

    snakes = {16: 4, 33: 20, 48: 24, 62: 56, 78: 69, 94: 16, 99: 40}
    ladders = {3: 12, 7: 23, 20: 56, 47: 53, 60: 72, 80: 94}

    # creates a dictionary (position -> (bead))
    # list is used due to possibility of many beads at a position
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
                    cprint("∫", "white",
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
    """
    Updates the position of a player on the board, based on the dice roll.

    Args:
        players (dict): A dictionary containing player names mapped
                        to a list of bead and position.
                        dict(name -> [bead,number])
        name (str): The name of the player to update.
        dice (int): The number rolled on the dice.

    Returns:
        dict: A dictionary containing the updated positions of all players.
                dict(name -> [bead,number])
    """

    def is_snake(position):
        snakes = {16: 4, 33: 20, 48: 24, 62: 56, 78: 69, 94: 16, 99: 40}
        if position in snakes:
            return (position, snakes[position])

    def is_ladder(position):
        ladders = {3: 12, 7: 23, 20: 56, 47: 53, 60: 72, 80: 94}
        if position in ladders:
            return (position, ladders[position])

    player_p = players[name][1]
    currentPos = player_p + dice
    if is_snake(player_p + dice):
        print(f"A snake ∫ is found on \"{is_snake(currentPos)[0]}\" and "
              f"you've been  bitten ...")
        print(f"Now you're at {is_snake(player_p + dice)[1]}.\n")
        players[name][1] = is_snake(player_p + dice)[1]
    elif is_ladder(player_p + dice):
        print("Wow! You found a ladder... \n Let's gooo!!")
        print(
            f"Now you're at \"{is_ladder(currentPos)[1]}\".\n")
        players[name][1] = is_ladder(player_p + dice)[1]
    elif players[name][1] + dice < 101:
        players[name][1] += dice
        print(f"You {name} have moved to \"{currentPos}\".\n")


def get_player_count(prompt):
    """
    Prompts the user to enter the number of players and validates the input.

    Args:
        prompt (str): A string prompt to be displayed to the user.

    Returns:
        int or None: The number of players entered by the user,
        or None if the user entered '0' to quit the game.

    """

    print("Enter a number between 1 and 4")
    print("Only 4 players allowed at a time")
    while True:
        try:
            cprint("Enter q to quit the game".center(
                32), "red", attrs=["blink"])
            player_count = input(prompt)
            if player_count == 'q':
                return
            if int(player_count) < 1:
                cprint("Enter a number between 1 and 4.", "red")
            elif int(player_count) > 4:
                cprint("Sorry, we can't accommodate more than 4 players.\n",
                       "red")
            else:
                return int(player_count)
        except ValueError:
            cprint("Invalid input: please enter a number.\n", "red")


def create_player_dict(num_players):
    """
    Creates a dictionary of players with their bead and starting position.

    Args:
        num_players (int): The number of players in the game.

    Returns:
        dict: A dictionary of player names mapped to a list
        containing their bead symbol and starting position.

    """

    def get_player_name(players, prompt):
        """
        Prompts the user to enter a player name and validates it.

        Args:
            players (dict): A dictionary of player names mapped
            to their bead symbol and starting position.
            prompt (str): A string prompt to be displayed to the user.

        Returns:
            str or None: The player's name entered by the user,
            or None if the user entered '0' or 'q' to quit the game.

        """
        cprint("Enter q to quit the game".center(32),
               "red", attrs=["blink"])
        while True:
            name = input(prompt).lower().strip()
            print(name)
            if name in ("0", "q"):
                return
            elif not name:
                print("Please enter a name")
            elif name not in players:
                return name
            else:
                print("That name is already taken. Please try another name.")
    print()

    players = {}
    rankings = ["first", "second", "third", "fourth"]
    beads = ["@", "#", "%", "*"]
    random.shuffle(beads)
    for i in range(num_players):
        player_name = get_player_name(
            players, f"Enter {rankings[i]} player's name: ")
        if not player_name:
            return
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


def display_quit_msg():
    """Displays quit message
    """
    cprint(" You quit!!! ".center(50, "="), "red", attrs=["bold"])
    cprint("GAME OVER! Come back next time :)".center(50),
           "black", attrs=["bold"])


def play_game():
    """Game engine that runs the game"""
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
    numbers = get_player_count("\nHow many people want to play: ")
    if not numbers:
        display_quit_msg()
        exit()
    # make dict of players
    players = create_player_dict(numbers)
    if not players:
        display_quit_msg()
        exit()
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
        cprint("To roll the dice, Press any button and click Enter",
               "blue")
        cprint("'q/quit' quits the game",
               "red", attrs=["blink"])
        # print("Hint: r gets the dice rolling :)")
        pos = players[active_player][1]
        display_pos = f"Your bead {colorBead} is currently at position {pos}"

        prompt = (f"Now It's {player}'s chance: {display_pos}\n"
                  f"roll the DICE: ")
        player_input = input(prompt).lower().strip()
        # if player_input in ["r", "roll", ""]:

        if player_input in ["q", "quit"]:
            display_quit_msg()
            exit()
        else:
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

        # increase the counter
        counter += 1
    print("\n\nGAME OVER, {%s} is the winner\n\n".format(colored(
        check_game_over(players)[1], "white", None, ["bold", "underline"])))


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1 and sys.argv[1].strip() in ("--help", "-h", "help"):
            pydoc.pager(HELP)
            sys.exit(0)
        else:
            play_game()
    except (EOFError, KeyboardInterrupt):
        display_quit_msg()
        exit()
