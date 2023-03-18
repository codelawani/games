# Snake and Ladder Game
This is a simple implementation of the classic Snake and Ladder board game in Python. The game is played in the command line interface.

## Installation
---
To run the game, you will need Python 3 installed on your computer. You can download the latest version of Python from the official website [here](https://www.python.org/downloads/).


## Dependencies
---
This game requires the following modules to be installed:

`termcolor`: Used to display colored output in the command line interface. You can install it using the following command:

```pip install termcolor```

## How to Play
---
To start the game, navigate to the directory where the game files are stored in your command line interface and run the following command:

```python3 game.py```

This will start the game and display the game board in your command line interface.

**To roll the dice, click any button and click enter.** 

**`q`/ `quit` quits the game**

The game will automatically move your token forward the number of spaces indicated by the dice roll.
If you land on a ladder space, you will climb up the board to a higher space.
> Ladder spaces are indicated by `†`

If you land on a snake space, you will slide down the board to a lower space.
> Snake spaces are indicated by `∫`

The game continues until one player reaches the final square on the board and wins the game.
