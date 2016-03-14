
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


### Points
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


## Playing

There are several different ways to interact with the game. The simplest one is
via the console.

### Console
The game can be played from the console
```bash
$ ./play --help
Simple harness that will run the TTT game. Can do any of Human vs Human,
Human vs Computer, or Computer vs Computer.

Usage: play [--blue=<b>] [--red=<r>] [--games=<n>] [--show]

Options:
    --blue=<b>      Blue player type (Human or Computer) [default: Computer]
    --red=<r>       Red plater type (Human or Computer) [default: Computer]
    --games=<n>     Number of games to play [default: 1]
    --show          Show boards between turns [default: false]
```

Simply try ```./play --show``` to get started ...

### REST API

The backend is exposed as a REST service built using [Flask](http://flask.pocoo.org/). It has endpoints for Game, Player, Score, and Authentication. The authentication is Twitter oauth, and is simply there to allow people to play across devices without having to register yet another place ...

### Browser

The primary UI is JavaScript and HTML using JQuery and JQuery Touch to give a decent experience on a touch screen. The Nature of the game -- moving pieces around -- lends itself nicely to touch screens. Also, the UI is so simple that it is well suited for smaller screens such as phones.

## Spok

Spok is a helper task that runs periodically in the background. The purpose of Spok is to make sure the game play can always continue. This is done by making sure there are always games ready to be played by either color. Spok ensures this by starting new games as needed and using a min-max algorithm, plays a few rounds of the game.

Spok also does housekeeping. Most importantly is finding games that have been abandoned and returning them to the pool. This is needed so that games with potentially long history -- and thus high value -- are not lost simply because a player was served a game and then stopped playing before taking their turn.
