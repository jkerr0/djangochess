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
    turn = data['game_state']['turn'];

    enableDisableDragging();
    makeMove(data.move);
    handleGameState((data['game_state']))
    handleSpecialMoves(data['special_move_info'], data.move);
    if (data['promoted_to_piece'] !== null && typeof data['promoted_to_piece'] !== 'undefined') {
        replacePiece(data.move.end_pos, data['promoted_to_piece']);
    }
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

const makeMoveSilent = (move) => {
    const startField = document.getElementById(move.start_pos.toString());
    const endField = document.getElementById(move.end_pos.toString());

    if (move.start_pos === startPos && move.end_pos === endPos) {
        return;
    }
    const movedPiece = startField.children[0];
    [...endField.children].forEach(child => endField.removeChild(child));
    addPieceToFieldIfPossible(endField, movedPiece);
    [...startField.children].forEach(child => startField.removeChild(child));
}

const makeMove = (move) => {
    makeMoveSilent(move);
    clearHighlightedFields();
    highlightMove(move);
    onEnemyMove();
}



const bindDraggingEvents = (piece) => {
       piece.setAttribute('draggable', 'true');

    piece.addEventListener('dragstart', e => {
        if (!isPlayersTurn()) {
            return;
        }
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
    });
}

playerPieces.forEach(bindDraggingEvents);

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
    if (isPlayersTurn()) {
        enableDragging();
    } else {
        disableDragging();
    }
}

const isPlayersTurn = () => {
    return turn === playerColor;
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
    playAudioById('message-pop');
}

const playCheckSound = () => {
    playAudioById('check-sound');
}

const playEndGameSound = () => {
    playAudioById('end-game-sound');
}

const playAudioById = (id) => {
    const audio = new Audio(document.getElementById(id).getAttribute('src'));
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

const replacePiece = (position, newPieceHtml) => {
    const field = document.getElementById(position.toString());
    field.innerHTML = newPieceHtml;
    [...field.children].forEach(bindDraggingEvents);
}

const getPosX = (pos) => {
    return pos % 8;
}

const getPosY = (pos) => {
    return Math.floor(pos / 8);
}

const getPosFromXY = (x, y) => y * 8 + x;

const handleEnpassant = (move) => {
    let x = getPosX(move.end_pos);
    let y = getPosY(move.start_pos);
    document.getElementById(getPosFromXY(x, y).toString()).innerHTML = '';
}

const handleCastle = (move) => {
    let start_x = getPosX(move.start_pos);
    let end_x = getPosX(move.end_pos);
    let y = getPosY(move.start_pos);
    let diff = end_x - start_x;
    let rook_pos, move_to;
    if (diff < 0) {
        rook_pos = getPosFromXY(0, y);
        move_to = getPosFromXY(3, y);
    } else if (diff > 0) {
        rook_pos = getPosFromXY(7, y);
        move_to = getPosFromXY(5, y);
    }
    makeMoveSilent({
        'start_pos': rook_pos,
        'end_pos': move_to
    })

}

const handleSpecialMoves = (specialMoveInfo, move) => {
    if (specialMoveInfo['enpassant']) {
        handleEnpassant(move);
    } else if (specialMoveInfo['castled']) {
        handleCastle(move);
    }
}

const handleGameState = (gameState) => {
    if (gameState['is_checkmate']) {
        $('#stateModalLabel').html("Checkmate");
        $('#stateModal').modal();
        playEndGameSound();
    } else if (gameState['is_draw']) {
        $('#stateModalLabel').html("Draw");
        $('#stateModal').modal();
        playEndGameSound();
    } else if (gameState['is_check']) {
        playCheckSound();
    }
}

handleGameState(JSON.parse(document.getElementById('game-state').textContent));