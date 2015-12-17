var restClient = undefined;
var userToken = undefined;
var gameId = undefined;
var sizes = undefined;
var playerColor = undefined;
var showWelcome = false;
var score = 0;
var setupDone = false;


function raottt() {
    $.removeCookie('token');
    showWelcome = true;

    // Overlay is used to blank out the board while getting a new game
    // from the server.
    $("#Overlay").hide(0);

    // The sidebar contains additional stats and settings.
    setupSideBar();

    // The REST interface back to the server.
    setupRestInterface();

    // To support many different screen sizes, everything is calculated based
    // on the window size.
    // sizes = calculateSizeFactors(window.innerWidth, window.innerHeight);
    sizes = calculateSizeFactors($('#Board').width(), $('#Board').height());

    positionBoard(sizes);

    // layoutBoard(sizes.tile, sizes.padding);

    getUserToken().pipe(resetBoard);
}


function setupRestInterface() {
    restClient = new $.RestClient('http://127.0.0.1:8888/');
    // restClient = new $.RestClient('http://192.168.1.6:8888/');
    restClient.add('game');
    restClient.add('player');
}


function getUserToken() {
    console.log("getUserToken called")
    var deferred = $.Deferred();

    var token = $.cookie('token');
    if(token) {
        var request = restClient.player.read(token);
        request.done(function(data) {
            $.cookie('name', data.name);
            $.cookie('color', data.color);
            $('#HelpText').html(returnAnonGreeting(
                $.cookie('name'), $.cookie('color'), data.score));
            userToken = data.token;
            score = data.score;
            deferred.resolve(data.token);
        });
    } else {
        var request = restClient.player.create();
        request.done(function(data){
            $.cookie('token', data.token);
            $.cookie('name', data.name);
            $.cookie('color', data.color);
            $('#HelpText').html(firstTimeGreeting(
                $.cookie('name'), $.cookie('color')));
            userToken = data.token;
            deferred.resolve(data.token);
        });
    }

    return deferred.promise();
}

function getGame(token) {
    console.log("getGame called with token %o", token);
    var deferred = $.Deferred();

    // if($.cookie('game')) {
    //  deferred.resolve($.cookie('game'));
    // }

    if(!token) {
        token = $.cookie('token');
    }

    var request = restClient.game.read(token);
    request.done(function(data){
        // $.cookie('game', data.token);
        gameId = data.ugid;
        playerColor = data.nextPlayer;
        deferred.resolve(data);
    });

    return deferred.promise();
}


function calculateSizeFactors(wWidth, wHeight)
{
    wHeight -= 50;
    var windowSize = wWidth < wHeight ? wWidth : wHeight;

    // Everything is based of the tilesize. For consistency, we want it
    // to be an even number.
    var tileSize = Math.floor(windowSize / 3.2);
    tileSize = tileSize % 2 ? tileSize - 1 : tileSize;

    // console.log("wHeight:" + wHeight + 
    //          " wWidth:" + wWidth +
    //          " tileSize:" + tileSize);

    s = {};
    s.tile = tileSize;
    s.font = Math.floor(tileSize * 0.75);
    s.padding = Math.floor(tileSize / 40);
    s.padding = s.padding % 2 ? s.padding + 1 : s.padding;
    s.board = 4 * s.padding + 3 * s.tile;
    s.offset = wWidth / 2 - s.board / 2;
    s.radius = Math.floor(tileSize / 15);
    return s;
};

function positionBoard(sizes) {
    $("#Board").css("left", sizes.offset);
    $("#Board").css("width", sizes.board);

    $("#Stats").css("left", sizes.offset);
    $("#Stats").css("width", sizes.board);
};


function resetBoard(token) {
    // First we have to remove all the pieces from the previous game
    // and remove the droppable class from the tiles
    $(".piece").remove();
    $(".tile").remove();

    getGame(token).pipe(
        layoutBoard).pipe(
            addPieces).pipe(
                scalePieces).pipe(
                    setupInteraction).pipe(
                        showStats);
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

function scalePieces(data) {
    console.log("scalePieces called");
    $(".piece").each(function(i) {
        // scalePiece($(this));
        // $(this).css("width", sizes.tile - sizes.padding);
        // $(this).css("height", sizes.tile - sizes.padding);
        // $(this).css("font-size", sizes.font);
        // $(this).css("border-radius", sizes.radius);
    });

    return data;
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
    $('#Overlay').show();

    console.log(color + " moved from " + source + " to " + target);

    var obj = {token: $.cookie('token'),  // userToken,
               gameId: gameId,
               color: color,
               source: source,
               target: target};

    console.log("PUTing back to server %o", obj);

    restClient.game.update(gameId, obj).done(function(data) {
        console.log("Response from PUT %o", data);
        
        $.removeCookie('game');
        $("#ScoreNumber").html(data.score);

        if(data.displayMsg) {
            alert(data.message);
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


function setupInteraction() {
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
        hoverClass: "drop-hover",
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
}

function showStats(data) {
    console.log("showStats called");
    
    if(showWelcome) {
        $("#my_popup").popup('show');
        showWelcome = false;
    }

    $("#Overlay").hide(0);
};  

function firstTimeGreeting(name, color) {
    var txt = "Hello anonymous person, I shall call you " + name + " (it is much more personal, don't you think?)<br><br>You will play for the " + color + " team.<br><br>If you wish to play in a network, or for a different team, or on multiple devices, then you will have to login. If not, just start playing ...";
    return txt;
}

function returnAnonGreeting(name, color, score) {
    var txt = "Welcome back " + name + " (remember that I gave you a name when you first stopped by?).<br><br>You are still playing for the " + color + " team.<br><br>You have " + score + " points!<br><br>You can still login if you want more control.";
    return txt;
}


function setupSideBar() {
    var settingsSidebar = new $.slidebars();
    settingsSidebar.slidebars.close();

    $("#ToggleSlidebar").click(function() {
        if(settingsSidebar.slidebars.active('right')) {
            settingsSidebar.slidebars.close();  
        } else {
            settingsSidebar.slidebars.open('right');
        }
    });
}


function setupHelpPopup() {
    $('#my_popup').popup({
        opacity: 0.3,
        transition: 'all 0.3s'
        });         
}


function showHelpPopup(txt) {
    $('#HelpText').html(txt);
    $('#my_popup').popus('show');
}


function setupTiles() {
    var board = $("#Board");
    for(var i=0; i<9; i++) {
        // console.log("Append tile " + i);
        $(board).append('<div class="ui-widget-content tile"></div>');
    }
}

