Chess Game
----------

This game is an implementation of the chess board game in the python programing language. It features all the features and rules of the standard chess game. 

Features
========

* 8 x 8 board
* 2 players
	1. white
	2. black
* 6 pieces per player
	1. King
	2. Queen
	3. Bishop
	4. Knight
	5. Rook
	6. Pawn
* Checkmate
* Stalemate
* Pawn promotion
* Dead position

Rules
=====
Seventy-five move rule:
	If the last 75 moves (by both players) have been made without any
	captures or pawn moves, it's a draw.
Fifty-move rule:
	This rule states that a player can claim a draw if no pawn has been
	moved and no piece has been captured in the last 50 moves.
Five-fold repetition rule:
	If the same position occurs on the board for the fifth time, it is a
	draw.
Three-fold repetition rules:
	If the same position occurs on the board for the third time, with the
	same player to move and the same set of legal moves, it's a draw.
	
	
The game also implements a couple of cool features to enhance user experience.


HOW TO PLAY
==========
change directory into the game directory and run

python3 -m chess
