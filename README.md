
# Random Acts Of Tic Tac Toe

A modified version of Tic Tac Toe (Noughts and Crosses, Xs and Os) where each
player only gets 3 pieces. Once a player has placed all pieces on the board,
subsequent moves are made by moving a piece to an empty spot. Thus, the game
continues on and could -- in theory -- go on forever.

As an added twist, each piece can only remain in the same spot for 5 rounds.
Once the time is up the player is forces to move that piece. This ensure a
player does not occupy the center spot for the entire game, and adds another
dimension for the player to consider.

In addition to the above rule modifications, any one player will participate in
many different games at the same time. Essentially, a game is picked at random,
a player takes a turn, and then another game is picked. This goes on
indefinitely.


## Points
Since the game never ends, players are awarded points to track their progress.
The scores are calculated as follows:

```
Points awarded after each move

+1 for every move
+1 if the move improved the value of the board for the player's color
-1 if the move lowered the value of the board for the player's color
+2 if the move changed the player's color from being behind to ahead
-1 if the move changed the player's color from being ahead to behind
+5 if this was the winning move
-3 if the game is lost on the next move
```

When a game is won, the value of the game (which is determined based on all the 
moves made for that game) is spit out among all the players that participated. 
The player are awarded points based on the color they played for (the loosing
color has points subtracted), and in proportion to the number of moves the
player made in that game.
