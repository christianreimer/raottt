var generateText = {
    firstTimeGreeting: function(name, color) {
        return "<p>Welcome to the game. I don't think I have seen you before! I will call you " + 
              "<b>" + name + "</b> and you will play for the " + 
              "<span class='help-text-" + color + "'>" + color + "</span> team.</p>" +

              "<p>If you want a different name, or to be able to play across devices, " + 
              "then you will have to login with Twitter.</p>" + this.instructionsText(undefined);
    },

    returnGreetingAnon: function(name, color, score) {
        return "Welcome back <b>" + name + "</b> " + 
              "(remember that I gave you a name when you first stopped by?)</p>" +

              "<p>You are playing for the " + 
              "<span class='help-text-" + color + "'>" + color + "</span> team. " + 
              "You have <b>" + score + "</b> points (way to go!)</p>" + 

              "<p>You can login with Twitter if you want a different name, " +
              "and remember that you can click the <span class='green-mini-button'>" +
              "<i class='fa fa-info-circle'></i></span> at any time for instructions.</p>";
    },

    returnGreetingCreds: function(name, color, score) {
        return "Welcome back <b>" + name + "</b>, nice to see you again.</p>" +

              "<p>You are playing for the " + 
              "<span class='help-text-" + color + "'>" + color + "</span> team. " + 
              "You have <b>" + score + "</b> points (way to go!)</p>" + 

              "<p>Remember that you can click the " + 
              "<span class='green-mini-button'><i class='fa fa-info-circle'></i></span> " +
              "at any time for instructions.</p>";
    },

    scoreText: function(data, color) {
        return "<p>You are playing for the " + 
               "<span class='help-text-" + color + "'>" + color + "</span> team.</p>" +

               "<p>Your have scored a total of " + data.score + " points, by " +
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
               "turn might be for a different game with a different board layout</li>" +
               "<li>If your color has fewer than 3 pieces on the board, then you can tap/click an empty square to add a piece</li>" +
               "<li>Each color only gets 3 pieces; onces all pieces are on the board, the game " +
               "continues by moving an existing piece to a new location</li>" + 
               "<li>Any given piece can only be in the same position for 5 rounds, once the count " +
               "reaches 1, you will have to move that piece</li>" + 
               "<li>You get awarded points for each move based on the value of the move</li>" + 
               "<li>When a game is won (or lost), all the players who participated in that game " +
               "will receive points (or loose points) depending on their contribution to the game</li>" +
               "</ul></p><p>These instructions, along with hints, can be accessed at any point via the " +
               "<span class='green-mini-button'><i class='fa fa-info-circle'></i></span> button on at the top of the screen.</p>";
    },

    loginText: function() {
      return "<p>Login with Twitter so that you can play across multiple devices, " +
             "restore sessions, and use your twitter name.</p>";
    },

    logoutText: function(name) {
      return "<p>You are currently logged in with Twitter and know " +
             "as <b>" + name + "</b>. If you want to, you can " +
             "logout and go back to player anonymously</p>";
    },

    newTwitterUser: function(name, color, score) {
        return "<p>You will now be know as <b>" + name + "</b> (isn't that much better?)</p>" + 
               "<p>You are playing for the " + 
               "<span class='help-text-" + color + "'>" + color + "</span> team. " + 
               "You have <b>" + score + "</b> points (way to go!)</p>" + 
               "<p>Lets get back to the game ...</p>";
    }
};

 