//establish websocket
const gameSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/game/'
    + '/'
);

gameSocket.onmessage = e => {
    const data = JSON.parse(e.data);
    //TODO move pieces after opponent's move
};

gameSocket.onclose = e => {
    console.error('Game socket closed unexpectedly');
};

//handle dragging and clicking
const pieces = document.querySelectorAll('.piece');
const fields = document.querySelectorAll('.field');

fields.forEach(field => {
    field.addEventListener('click', e => {
        //TODO
    })
})

