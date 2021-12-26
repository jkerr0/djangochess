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
    document.getElementById('white_nickname').innerText = data.white_player_nick;
    document.getElementById('black_nickname').innerText = data.black_player_nick;
}

lobbySocket.onclose = e => {
    console.error('Game socket closed unexpectedly');
}

const white = "white", black = "black";

const sendPlayAs = colorName => {
    lobbySocket.send(JSON.stringify({'play-as': colorName}))
}

document.getElementById('as-black').addEventListener('click', e => {
    sendPlayAs(black);
});

document.getElementById('as-white').addEventListener('click', e => {
    sendPlayAs(white);
});
