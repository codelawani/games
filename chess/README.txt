Chess Game
----------

This game is an implementation of the chess board game in the python programing language.
It has many of the features and rules of a complete standard chess game. Instead of a regular
GUI, it has a Text User Interface. This means that the app runs well in a terminal environment
without needing a gui library.

The UI was intended to be unique just like the chess game and also very accessible. It can be
run from a remote server with no GUI.


Features
========

* 8 x 8 board ✔
* 2 players (white and black) ✔
* 6 pieces per player ✔
	1. King ✔
	2. Queen ✔
	3. Bishop ✔
	4. Knight ✔
	5. Rook ✔
	6. Pawn ✔
* Checkmate (win) ✔
	When a king is trapped and is under check ✔
* Stalemate (draw) ✔
	When a king is trapped but is not under check ✔
* Pawn promotion ✔
* Undo last moves ✔
	A previous move can be reverted by using Ctrl+D on your keyboard.
	('Control' key then 'D').
* Save game's progress ✔
	You would be asked if you want to save when you try to exit the game using
	Ctrl+Q ('Control' key then 'D'). You can intentionally save while the game
	is going on by using Ctrl+S ('Control' key then 'S').
* Load presaved game ✔
	If a game has been saved before and you start the program, you'll be asked
	if you would like to continue the last game. If you don't continue, you'll
	lose the saved game.
* Possible moves indicator ✔
	Click on a piece to see the possible moves it can make.
	The boxes where the selected piece moved to would be highlighted.
* Check ✔
	This is when the king is under attack. You'll know when a king is under
	attack because the king's box would be highlighted and the only moves
	that would be available are moves that would rescue the king in danger.
* Active player indicator ✔
	This shows which player's turn it is.
* Scores indicator ✔
	This would show the cummulative points of every piece captured by each
	player.
* Captured pieces indicator ✔
	This would show every piece captured by each player.
	


Rules
=====
* Seventy-five move rule: (not yet implemented in ui ❌)
	If the last 75 moves (by both players) have been made without any
	captures or pawn moves, it's a draw.
* Fifty-move rule: (not yet implemented in ui ❌)
	This rule states that a player can claim a draw if no pawn has been
	moved and no piece has been captured in the last 50 moves.
* Five-fold repetition rule: (not yet implemented in ui ❌)
	If the same position occurs on the board for the fifth time, it is a
	draw.
* Three-fold repetition rules: (not yet implemented in ui ❌)
	If the same position occurs on the board for the third time, with the
	same player to move and the same set of legal moves, it's a draw.
	
	
Requirements
============

- Python: Version 3.8 and above. This game was built using python 3.10.5

- Textual: This was used for the ui, install it using `pip install textual`

- Rich: This works with textual to create amazing TUIs. Install using `pip install rich`

- Environment: Must be run in a terminal environment (⚠ Don't use IDE terminals).
	An environment like gnome-shell and powershell would be suitable for playing the game.


HOW TO PLAY
===========
change directory into the `chess` directory and run...

`python -m src`

	OR

`python3 -m src`

...depending on how you refer to python3 in your environment.
