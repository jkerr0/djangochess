const gameId = JSON.parse(document.getElementById('game-id').textContent);

const lobbySocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/game/lobby/'
    + gameId
    + '/'
);

lobbySocket.onmessage = e => {
    const data = JSON.parse(e.data);
    console.log(data);

    if (data.start_game_url != null) {
        window.location.replace(data.start_game_url);
    }

    if (data.setup != null) {
        document.getElementById('white_nickname').textContent = data.setup.white_player_nick;
        document.getElementById('black_nickname').textContent = data.setup.black_player_nick;
    }
}

lobbySocket.onclose = e => {
    console.error('Game socket closed unexpectedly');
}

const white = "white", black = "black";

const sendPlayAs = colorName => {
    lobbySocket.send(JSON.stringify({
        'play_as': colorName,
        'start_game': false
    }))
}

const sendStartGame = () => {
    lobbySocket.send(JSON.stringify({
        'play_as': null,
        'start_game': true
    }))
}

document.getElementById('as-black').addEventListener('click', e => {
    sendPlayAs(black);
});

document.getElementById('as-white').addEventListener('click', e => {
    sendPlayAs(white);
});

document.getElementById('start_game').addEventListener('click', e => {
    sendStartGame();
})