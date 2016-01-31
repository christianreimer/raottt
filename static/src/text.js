var generateText = {
    firstTimeGreeting: function(name, color) {
        return "<h3>Welcome to Random Acts Of Tic Tac Toe</h3>" +
              "<p>I don't think I have seen you before! I will call you " + 
              "<b>" + name + "</b> and you will play for the " + 
              "<font style='color:" + color + ";'><b>" + color + "</b></font> team.</p>" +
              "<p>If you want a different name, to be able to play across devices, " + 
              "or if you want to play for a specific color, then you will have to login " +
              "with Twitter.</p>" + this.instructionsText(undefined);
    },

    returnGreeting: function(name, color, score) {
        return "Welcome back <b>" + name + "</b> (remember that I gave you a name when " +
              "you first stopped by?).</p>" + 
              "<p>You are still playing for the " + 
              "<font style='color:" + color + ";'><b>" + color + "</b></font> team. " + 
              "You have <b>" + score + "</b> points (way to go!)</p>" + 
              "<p>You can login with Twitter if you want a different name or team, and remember that " + 
              "you can click the <font style='color:green;'><b>?</b></font> " +
              "at any time for instructions.</p>";
    },

    scoreText: function(data) {
        return "<p>Your have scored a total of " + data.score + " points, by " +
               "making " + data.turns + " moves in " + data.games + " games.</p>" +
               "<p>In total, " + data.totalTurns + " moves have been made. " +
               "The Red team has won " + data.redWins + " games, while the " +
               "Blue team has won " + data.blueWins + ".</p>";
    },

    instructionsText: function(hint) {
        if(hint) {
            var hintText = "<p><b>Hint</b></p><p>" + hint + "</p>";
        }
        else {
            var hintText = "";
        }

        return hintText + "<hr><p><b>Game Instructions</b></p>" +
               "<p>The objective of the game is to move three pieces of the same " +
               "color into a row (horizontal, vertical, or diagonal). Unlike regular " +
               "Tic Tac Toe, this game has a few additional challenges:" + 
               "<ul><li>You will be playing many different games at the same time -- each " +
               "turn might be for a different game with a differnt board layout</li>" +
               "<li>If your color has fewer than 3 pieces on the board, then you can tap/click an empty square to add a piece</li>" +
               "<li>Each color only gets 3 pieces; onces all pieces are on the board, the game " +
               "contines by moving an existing piece to a new location</li>" + 
               "<li>Any given piece can only be in the same position for 5 rounds, once the count " +
               "reaches 1, you will have to move that pice</li>" + 
               "<li>You get awarded points for each move based on the value of the move</li>" + 
               "<li>When a game is won (or lost), all the players who particpiated in that game " +
               "will receive points (or loose points) depending on their contribution to the game</li>" +
               "</ul></p><p>These instructions, along with hints, can be access at any point via the " +
               "<font style='color:green;'><b>?</b></font> button on at the top of the screen.</p>";
    }
};

 