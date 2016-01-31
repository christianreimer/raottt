var restClient = undefined;
var userToken = undefined;
var gameId = undefined;
var sizes = undefined;
var playerColor = undefined;
var playerData = undefined;
var instructions = undefined;


function raottt() {
    // Overlay is used to blank out the board while getting a new game
    // from the server
    $('html').loader('show', {image: '../images/loading.gif'});

    // The REST interface back to the server.
    setupRestInterface();

    // To support many different screen sizes, everything is calculated based
    // on the window size.
    sizes = calculateSizeFactors(window.innerWidth, window.innerHeight);
    // sizes = calculateSizeFactors($('#Board').width(), $('#Board').height());

    positionBoard(sizes);

    fetchUser().pipe(sayHello).pipe(resetBoard);
}


function setupRestInterface() {
    restClient = new $.RestClient();
    restClient.add('game');
    restClient.add('player');
    restClient.add('score');
}


function fetchUser() {
    console.log("fetchUser called")

    var deferred = $.Deferred();
    var token = $.cookie('token');

    if(token) {
        // Returning user
        var request = restClient.player.read(token);

        request.done(function(data) {
            userToken = data.token;
            playerColor = data.color;
            playerData = data;
            $.cookie('token', data.token, {expires: 7});
            deferred.resolve(data);
        });
    } else {
        // New user
        var request = restClient.player.create();

        request.done(function(data){
            userToken = data.token;
            playerColor = data.color;
            playerData = data;
            $.cookie('token', data.token, {expires: 7});
            deferred.resolve(data);
        });
    }

    return deferred.promise();
}


function sayHello(data) {
    console.log('sayHello called with %o', data);

    if(data.returning) {
        showPopup(returnGreeting(data.name, data.color, data.score));
    }
    else {
        showPopup(firstTimeGreeting(data.name, data.color));
    }

    updateScore(data);   
    return data.token;       
}


function getGame(token) {
    console.log("getGame called with token %o", token);
    var deferred = $.Deferred();

    if(!token) {
        alert("Why are we getting here???");
    }

    var request = restClient.game.read(token);
    request.done(function(data){
        gameId = data.ugid;
        playerColor = data.nextPlayer;
        instructions = data.instructions;

        console.log('getGame returned %o', data);
        deferred.resolve(data);
    });

    return deferred.promise();
}

function getScore(token) {
    console.log("getScore called with token %o", token);
    var deferred = $.Deferred();

    var request = restClient.score.read(token);
    request.done(function(data){
        console.log('getScore returned %o', data);
        deferred.resolve(data);
    });

    return deferred.promise();
}


function calculateSizeFactors(wWidth, wHeight)
{
    console.log('wWidth:' + wWidth + ' wHeight:'+ wHeight);

    var headerSize = 50;
    var maxSize = 600;

    wHeight -= headerSize;

    // Use the smaller of height/width as the window size
    var windowSize = wWidth < wHeight ? wWidth : wHeight;
    windowSize = windowSize > maxSize ? maxSize : windowSize;

    // Everything is based of the tilesize. For consistency, we want it
    // to be an even number.
    var tileSize = Math.floor(windowSize / 3.2);
    tileSize = tileSize % 2 ? tileSize - 1 : tileSize;

    console.log("wHeight:" + wHeight + " wWidth:" + wWidth + " tileSize:" + tileSize);

    s = {};
    s.tile = tileSize;
    s.font = Math.floor(tileSize * 0.75);
    s.padding = Math.floor(tileSize / 50);
    s.padding = s.padding % 2 ? s.padding + 1 : s.padding;
    s.boardSize = 4 * s.padding + 3 * s.tile;
    s.offset = wWidth / 2 - s.board / 2;
    s.radius = Math.floor(tileSize / 15);
    return s;
};

function positionBoard(sizes) {
        $("body").css("width", sizes.boardSize);
        $('#Board').css('width', sizes.boardSize);
        $('#Board').css('height', sizes.boardSize);
        $('#Board').css('top', 100);
};


function resetBoard(token) {
    // First we have to remove all the pieces from the previous game
    // and remove the droppable class from the tiles
    $(".piece").remove();
    $(".tile").remove();

    getGame(token).pipe(
        layoutBoard).pipe(
            addPieces).pipe(
                setupInteraction).pipe(
                    function() {
                        $('html').loader('hide');
                    });
}


function addPieces(data) {
    console.log("addPieces called with %o", data);

    function add(i, color, count, movable) {
        var div = $('<div class="ui-widget-content piece"></div>');
        div.attr("data-source", i);
        div.attr("data-color", color);
        div.html(count);
        div.addClass(color);
        var pos = calculatePosition(i);
        div.css("top", pos.top);
        div.css("left", pos.left);
        div.css("height", sizes.tile);
        div.css("width", sizes.tile);
        
        if(movable && data.offBoard == false) {
            div.addClass("draggable");
        }

        scalePiece(div);

        $("#Board").append(div);
    };

    $(data.board).each(function(i) {
        if(data.board[i].color) {
            var info = data.board[i];
            add(i, info.color, info.count, info.movable);
        } 
    });

    $(".tile").each(function(i) {
        // console.log("tile["+i+"]");

        if(data.board[i].color) {
            // This position has a piece in it (see above) so we do not want
            // it to be able to receive drops or clicks
        } else if(data.offBoard) {
            // This is an empty spot and we are still adding pieces to the 
            // board, so hook up a click handler
            $(this).click(function() {
                add(i, data.nextPlayer, 5, false);
                processMove(data.nextPlayer, -1, i);
            });
        } else {
            // Normal open tile should be a drop target
            $(this).addClass('droppable');
        }
    });

    return data;
}


function scalePiece(piece) {
    piece.css("width", sizes.tile - sizes.padding);
    piece.css("height", sizes.tile - sizes.padding);
    piece.css("font-size", sizes.font);
    piece.css("border-radius", sizes.radius);    
}


function layoutBoard(data) {
    tileSize = sizes.tile;
    padding = sizes.padding;

    setupTiles();

    $(".tile").each(function(i) {
        $(this).css("width", tileSize);
        $(this).css("height", tileSize);

        var col = i % 3;
        var row = Math.floor(i/3);

        $(this).css("left", padding * (col + 1) + col * tileSize);
        $(this).css("top",  padding * (row + 1) + row * tileSize);
        $(this).attr("data-target", i);
    });

    return data;
}


function calculatePosition(i) {
    var tile = undefined;

    if(i === -1) {
        tile = $(".benchTile")[0];
    } else {
        tile = $(".tile")[i];
    }

    return {left: parseInt(tile.style.left) + sizes.padding - 1, 
            top:  parseInt(tile.style.top)  + sizes.padding - 1};
}


function processMove(color, source, target) {
    $('html').loader('show', {image: '../images/loading.gif'});
    console.log(color + " moved from " + source + " to " + target);

    var obj = {token: userToken,
               gameId: gameId,
               color: color,
               source: source,
               target: target};

    console.log("PUTing back to server %o", obj);

    restClient.game.update(gameId, obj).done(function(data) {
        console.log("Response from PUT %o", data);
        
        $.removeCookie('game');

        updateScore(data);
        playerData = data;

        if(data.message) {
            showPopup(data.message);
        }
        
        // Remove all the droppable and click handlers before re-constructing
        // the board
        $(".tile").each(function(i) {
            if($(this).droppable()) {
                $(this).droppable('destroy');
            }
            $(this).unbind('click');
        });

        resetBoard(userToken);  
    });
}


function setupInteraction(data) {
    console.log("setupInteraction called");

    $(".draggable").draggable({
        revertDuration: 200,
        zIndex: 100,
        cursor: "crosshair",
        revert: function(event, ui) { 
            if(event) {
                return false;
            }
            return true;
        }
    });


    $(".droppable").droppable({
        accept: ".draggable",
        hoverClass: "drop-hover-" + playerColor,
        drop: function(event, ui) {
            var sourceTile = $(ui.draggable).attr("data-source");
            var targetTile = $(this).attr("data-target");
            var color = $(ui.draggable).attr("data-color");

            $(ui.draggable).css('top',
                $(this).position().top + sizes.padding-1);
            $(ui.draggable).css('left',
                $(this).position().left + sizes.padding-1);

            processMove(color, sourceTile, targetTile);
        }
    });

    return data;
}


function showScore() {
    getScore(userToken).pipe(function (data) {
        var html = "<p>Your have scored a total of " + data.score + " points. " +
                   "You have participated in " + data.games + " games, and " +
                   "made " + data.turns + " moves.</p>" +
                   "<p>In total, " + data.totalTurns + " moves have been made. " +
                   "The Red team has won " + data.redWins + " games, while the " +
                   "Blue team has won " + data.blueWins + ".</p>";

        showPopup(html);
    });
}


function showInstructions() {
    var html = "<p>" + instructions + "<p>";
    showPopup(html);
}


function showPopup(data) {
    console.log("showPopup called");

    $('html').loader('hide');
    $("#WelcomeText").html(data);
    $("#welcomePopup").popup('show');
}


function firstTimeGreeting(name, color) {
    var txt = "<h3>Welcome to Random Acts Of Tic Tac Toe</h3>" +
              "<p>I don't think I have seen you before... I shall call you " + 
              "<b>" + name + "</b> and you will play for the " + 
              "<font style='color:" + color + ";'><b>" + color + "</b></font> team.</p>" +
              "<p>If you want a different name, to be able to play across devices, " + 
              "or if you want to play for a specific color, then you will have to login " +
              "by clicking on the twitter icon.</p>" +
              "<p>You can click the <font style='color:green;'><b>?</b></font> " +
              "at any time for instructions.</p>";
    return txt;
}

function returnGreeting(name, color, score) {
    var txt = "Welcome back " + name + " (remember that I gave you a name when " +
              "you first stopped by?).</p>" + 
              "<p>You are still playing for the " + 
              "<font style='color:" + color + ";'><b>" + color + "</b></font> team. " + 
              "You have <b>" + score + "</b> points (way to go!)</p>" + 
              "<p>You can still login if you want more control, and remember that " + 
              "you can click the <font style='color:green;'><b>?</b></font> " +
              "at any time for instructions.</p>";
    return txt;
}


function setupTiles() {
    var board = $("#Board");
    for(var i=0; i<9; i++) {
        // console.log("Append tile " + i);
        $(board).append('<div class="ui-widget-content tile"></div>');
    }
}


function updateScore(data) {
    var txt = $('#ScoreNumber').text();
    var num = parseInt(txt.replace(',', ''));

    $('#ScoreNumber').numerator({
        duration: 750,
        delimiter: ',',
        toValue: data.score,
        fromValue: num});
}
