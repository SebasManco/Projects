console.log(JSON.parse(localStorage.getItem('score')))

let score = JSON.parse(localStorage.getItem
('score')) || {
    wins: 0,
    loses: 0,
    ties: 0
};

// if (score === null) {
//     score = {
//         wins:0,
//         loses: 0,
//         ties:0 
//     };
// }

updateScoreElement();

function playGame(playerMove,computerMove) {
    let result = '';

    if (playerMove === 'scissors'){
        if (computerMove === 'rock') {
            result = 'The computer wins'
        } else if (computerMove === 'paper') {
            result = 'You win';
        } else {
            result = 'You Tie'
        }
    } else if (playerMove === 'rock') {
        if (computerMove === 'rock') {
            result = 'You Tie'
        } else if (computerMove === 'paper') {
            result = 'The computer wins'
        } else {
            result = 'You win';
        }
    } else {
        if (computerMove === 'rock') {
            result = 'You win';
        } else if (computerMove === 'paper') {
            result = 'You Tie'
        } else {
            result = 'The computer wins'
        }
    }
    
    if(result === 'You win'){
        score.wins += 1;
    } else if(result === 'You Tie'){
        score.ties += 1;
    } else {
        score.loses += 1;
    }
    
    localStorage.setItem('score',JSON.stringify(score));
    updateResultElement(result);
    updateScoreElement();
    showMove(playerMove,computerMove)
}

function updateScoreElement() {
    document.querySelector('.js-score')
        .innerHTML = `Wins: ${score.wins}. Losses: ${score.loses}, Ties: ${score.ties}`;
};

function updateResultElement(result) {
    document.querySelector('.js-result')
        .innerHTML = `${result}`;
};

function showMove(playerMove,computerMove) {
    document.querySelector('.js-moves')
        .innerHTML = `You
<img src="images/${playerMove}-emoji.png" alt="" class="move-icon">
<img src="images/${computerMove}-emoji.png" alt="" class="move-icon">
Computer`;
};

function pickComputerMove() {
    let computerMove = '';
    const randomNumber = Math.random();
    
    if (randomNumber >= 0 && randomNumber < 1/3) {
        computerMove = 'rock'
    } else if (randomNumber >= 1/3 && randomNumber < 2/3) {
        computerMove = 'paper'
    } else {
        computerMove = 'scissors'
    }

    return computerMove;
}