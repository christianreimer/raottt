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
    spinner(true);

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
    restClient.add('debug');
    restClient.add('auth');
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
    if(data.popupType == 'returningPlayer') {
        if(data.creds) {

            var text = generateText.returnGreetingCreds(
                data.name, data.color, data.score);

            showPopup(text, standardCloseButton(), false, true);
        }
        else {
            var text = generateText.returnGreetingAnon(
                data.name, data.color, data.score);

            showPopup(text, standardCloseButton(), false, true);
        }
    }
    else if (data.popupType == 'newPlayer') {
        showPopup(generateText.firstTimeGreeting(data.name, data.color),
            standardCloseButton(), false, true);
    }
    else if (data.popupType == 'updatedPlayer') {
        showPopup('You have been updated',
            standardCloseButton(), false, true);
    }
    else if (data.popupType == 'newTwitter') {
        showPopup(generateText.newTwitterUser(data.name, data.color, data.score),
            standardCloseButton(), false, false);
    }
    else {
        alert('Unknown popupType ' + data.popupType);
    }

    updateScore(data);   
    return data.token;       
}


function getGame(token) {
    var deferred = $.Deferred();

    var request = restClient.game.read(token);
    request.done(function(data){
        gameId = data.ugid;
        playerColor = data.nextPlayer;
        instructions = data.instructions;
        deferred.resolve(data);
    });

    return deferred.promise();
}

function getScore(token) {
    var deferred = $.Deferred();

    var request = restClient.score.read(token);
    request.done(function(data){
        deferred.resolve(data);
    });

    return deferred.promise();
}


function calculateSizeFactors(wWidth, wHeight)
{
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
                    spinner(false));
}


function addPieces(data) {

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
        } else {
            div.addClass("non-draggable");
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
    spinner(true);

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
            showPopup(data.message, standardCloseButton(), false, true);
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
    spinner(true);

    getScore(userToken).pipe(function (data) {

        showPopup(generateText.scoreText(data, playerColor),
            standardCloseButton(), false, true);
    });
}


function showInstructions() {
    showPopup(generateText.instructionsText(instructions),
        standardCloseButton(), false, true);
}


function showPopup(text, buttonOneDiv, buttonTwoDiv, easyClose) {
    spinner(false);
    
    var maxWidth = $(window).width();
    maxWidth = maxWidth > 550 ? 550 : maxWidth - 2;
    $("#Popup").css( "maxWidth", maxWidth + "px" );

    $("#PopupTitle").html('<h3>Random Acts Of Tic Tac Toe</h3>');
    $("#PopupText").html(text);

    if(buttonOneDiv) {
        $("#PopupButton1").replaceWith(buttonOneDiv);
        $("#PopupButton1").show();
    } else {
        $("#PopupButton1").hide();
    }

    if(buttonTwoDiv) {
        $("#PopupButton2").replaceWith(buttonTwoDiv);
        $("#PopupButton2").addClass('SpaceAbove');
        $("#PopupButton2").show();
    } else {
        $("#PopupButton2").hide();
    }

    if(easyClose) {
        $("#Popup").addClass("Popup_close");
    } else {
        $("#Popup").removeClass("Popup_close");   
    }

    $("#Popup").popup('show');
}


function setupTiles() {
    var board = $("#Board");
    for(var i=0; i<9; i++) {
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


function spinner(show) {
    if(show) {
        $.LoadingOverlay("show", {
            image: "",
            fontawesome: "fa fa-spinner fa-spin"});
    }
    else {
        $.LoadingOverlay("hide");
    }
}


function showDebug() {
    spinner(true);

    getDebug(gameId).pipe(function (data) {
        var text = "<ul>";
        for (var prop in data) {
            if(prop === "score") {
                continue;
            }
            text += "<li><b>" + prop + "</b> " + data[prop] +"</li>";
        }

        for (var prop in data.score) {
            text += "<li><b>score " + prop + "</b> " + data[prop] +"</li>";   
        }

        text += "</ul>";
        showPopup(text, standardCloseButton, false, true);
    });
}


function getDebug(token) {
    var deferred = $.Deferred();

    var request = restClient.debug.read(token);
    request.done(function(data){
        deferred.resolve(data);
    });

    return deferred.promise();
}


function showLoginPopup() {
    // Call back to the server with the uid token to determine which popup
    // to show

    getLoginType().pipe(function (data) {
        if(data.popupType == 'startLogin') {

            var func = "loadUrl('" + data.url + "')";
            var button = buttonDiv(1, 'PopupButtonBlue',
                'Login With Twitter', func, false);

            showPopup(generateText.loginText(),
                button, standardCloseButton(2), false);

        } else if(data.popupType == 'logout') {

            var button = buttonDiv(1, 'PopupButtonBlue',
                'Logout From Twitter', 'logOut()', false);

            showPopup(generateText.logoutText(data.name),
                button, standardCloseButton(2), false);
        }
    });
}


function getLoginType(token) {
    console.log('getLoginType called with token %o', token);

    var deferred = $.Deferred();
    var request = restClient.auth.read(userToken);
    request.done(function(data){
        deferred.resolve(data);
    });

    return deferred.promise();

}


function loadUrl(url) {
    window.location.replace(url);
}


function logOut() {
    spinner(true);
    $.removeCookie('token');

    userToken = undefined;
    gameId = undefined;
    playerData = undefined;

    fetchUser().pipe(sayHello).pipe(resetBoard);
}


function buttonDiv(number, color, text, clickTarget, close) {
    var template = '<div id="PopupButton{0}" class="PopupButton {1}{2}"{3}>{4}</div>';
    template = template.replace('{0}', number);
    template = template.replace('{1}', color);
    template = template.replace('{2}', (close ? ' Popup_close' : ''));
    template = template.replace('{3}', (clickTarget ? ' onClick="' + clickTarget + '"' : ''));
    template = template.replace('{4}', text);
    return template;
}

function standardCloseButton(num) {
    num = num ? num : '1'
    return buttonDiv(num, 'PopupButtonGray', "Got it, let's play!", false, true);
}
