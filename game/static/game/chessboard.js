//websocket setup and functions
const gameId = JSON.parse(document.getElementById('game-id').textContent);

const gameSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/game/chessboard/'
    + gameId
    + '/'
);

gameSocket.onmessage = e => {
    const data = JSON.parse(e.data);
    //TODO move pieces after opponent's move
};

gameSocket.onclose = e => {
    console.error('Game socket closed unexpectedly');
};

// drag and drop
const playerColor = JSON.parse(document.getElementById('player-color').textContent);
const playerPieces = document.querySelectorAll('.' + playerColor);


let startPos = null;
let endPos = null;

const sendMove = () => {
    gameSocket.send(JSON.stringify({'move': {'start_pos': startPos, 'end_pos': endPos}}));
}


playerPieces.forEach(piece => {
    piece.setAttribute('draggable', 'true');

    piece.addEventListener('dragstart', e => {
        piece.classList.add('dragging');
        startPos = parseInt(piece.parentElement.id);

        getFieldsToDropTo().forEach(field => {
            field.addEventListener('dragover', e => {
                e.preventDefault();
                endPos = parseInt(field.id);
                field.appendChild(document.querySelector('.dragging'));
            });
        });
    });

    piece.addEventListener('dragend', e => {
        piece.classList.remove('dragging');
        if (startPos !== endPos) {
            sendMove();
        }
    })
})

const getFieldsToDropTo = () => {
    // TODO - find piece moves by startPos in move graph
    return document.querySelectorAll('.field');
}






