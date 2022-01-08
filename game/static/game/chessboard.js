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
    moveGraph = data['move_graph'];
    turn = data['turn'];
    enableDisableDragging();
    makeMove(data.move)
};

gameSocket.onclose = e => {
    console.error('Game socket closed unexpectedly');
};

// drag and drop
const playerColor = JSON.parse(document.getElementById('player-color').textContent);
const playerPieces = document.querySelectorAll('.' + playerColor);

// state
let startPos = null;
let endPos = null;
let moveGraph = JSON.parse(document.getElementById('move-graph').textContent);
let turn = JSON.parse(document.getElementById('turn').textContent);

const sendMove = () => {
    gameSocket.send(JSON.stringify({'move': {'start_pos': startPos, 'end_pos': endPos}}));
}

const onSelfMove = () => {
    sendMove();
    playMoveSound();
    clearHighlightedFields();
}

const onEnemyMove = () => {
    playMoveSound();
}

const makeMove = (move) => {
    const startField = document.getElementById(move.start_pos.toString());
    const endField = document.getElementById(move.end_pos.toString());

    if (move.start_pos === startPos && move.end_pos === endPos) {
        return;
    }

    const movedPiece = startField.children[0];
    [...endField.children].forEach(child => endField.removeChild(child));
    addPieceToFieldIfPossible(endField, movedPiece);
    [...startField.children].forEach(child => startField.removeChild(child));
    highlightMove(move);
    onEnemyMove();
}

playerPieces.forEach(piece => {
    piece.setAttribute('draggable', 'true');

    piece.addEventListener('dragstart', e => {
        piece.classList.add('dragging');
        startPos = parseInt(piece.parentElement.id);
        clearHighlightedFields();
        highlightPossibleEndPositions();

        document.querySelectorAll('.field').forEach(field => {
            field.addEventListener('dragover', e => {
                if (getFieldsToDropTo().every(dropabble => dropabble !== document.getElementById(field.id))) {
                    endPos = startPos;
                    return;
                }
                endPos = parseInt(field.id);
                e.preventDefault();
                showAllPiecesFromOtherFields(field);
                hideEnemyPiecesOnField(field, piece);
                addPieceToFieldIfPossible(field, document.querySelector('.dragging'));
            });
        });
    });

    piece.addEventListener('dragend', e => {
        clearHighlightedFields();
        removeEnemyPiecesOnField(piece.parentElement, piece);
        piece.classList.remove('dragging');
        if (startPos !== endPos) {
            onSelfMove();
        }
    })
});

const enableDragging = () => {
    playerPieces.forEach(piece => {
        piece.setAttribute('draggable', 'true');
    });
}

const disableDragging = () => {
    playerPieces.forEach(piece => {
        piece.setAttribute('draggable', 'false');
    })
}

const enableDisableDragging = () => {
    if (turn === playerColor) {
        enableDragging();
    } else {
        disableDragging();
    }
}

enableDisableDragging();

const hideEnemyPiecesOnField = (field, piece) => {
    [...field.getElementsByClassName(getEnemyPieceClass(piece))].forEach(enemyPiece => {
        enemyPiece.classList.add('invisible');
    })
}

const removeEnemyPiecesOnField = (field, piece) => {
    [...field.getElementsByClassName(getEnemyPieceClass(piece))].forEach(enemyPiece => {
        field.removeChild(enemyPiece);
    })
}

const showAllPiecesFromOtherFields = field => {
    let invisiblePieces = document.getElementsByClassName('piece invisible');
    [...invisiblePieces].filter(piece => piece.parentElement !== field)
        .forEach(piece => piece.classList.remove('invisible'));
}

const addPieceToFieldIfPossible = (field, piece) => {
    if (isFriendOnField(field, piece)) {
        // do not append
        return;
    }

    const currentChildren = [...field.children];
    currentChildren.forEach(element => field.removeChild(element));
    field.appendChild(piece);
    currentChildren.forEach(child => field.appendChild(child));
}

const isFriendOnField = (field, piece) => {
    let isFriend = false;
    [...field.children].forEach(otherPiece => {
        if (otherPiece.classList.contains(getFriendPieceClass(piece))) {
            isFriend = true;
        }
    });
    return isFriend;
}

const getEnemyPieceClass = piece => {
    return piece.classList.contains('white_piece') ? 'black_piece' : 'white_piece';
}

const getFriendPieceClass = piece => {
    return piece.classList.contains('white_piece') ? 'white_piece': 'black_piece';
}

const getFieldsToDropTo = () => {
    return [...moveGraph[startPos.toString()].map(endFieldId => document.getElementById(endFieldId.toString())),
            document.getElementById(startPos.toString())];
}

const playMoveSound = () => {
    const audio = new Audio(document.getElementById('message-pop').getAttribute('src'));
    audio.play();
}

const highlightMove = (move) => {
    const startField = document.getElementById(move.start_pos.toString());
    const endField = document.getElementById(move.end_pos.toString());

    [startField, endField].forEach(field => {
        ['black_field', 'white_field'].forEach(fieldClass => {
            field.classList.replace(fieldClass, 'highlighted_' + fieldClass);
        })
    })
}

const clearHighlightedFields = () => {
    document.querySelectorAll('.field').forEach(field => {
        ['black_field', 'white_field'].forEach(fieldClass => {
            field.classList.replace('highlighted_' + fieldClass, fieldClass);
        })
    })
}

const highlightPossibleEndPositions = () => {
    moveGraph[startPos.toString()].forEach(endFieldId => {
        const field = document.getElementById(endFieldId.toString());
        ['black_field', 'white_field'].forEach(fieldClass => {
            field.classList.replace(fieldClass, 'highlighted_' + fieldClass);
        })
    })
}




