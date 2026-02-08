// zoom.js

const zoomInBtn = document.querySelector('.zoom-in-btn');
const zoomOutBtn = document.querySelector('.zoom-out-btn');

function zoomIN() {

    document.querySelector('.chat-section').style.display = 'none';
    document.querySelector('.heder').style.display = 'none';
    document.querySelector('.container').style.height = '100%';
    document.querySelector('.code-section').style.width = '100%';
    zoomOutBtn.style.display = 'flex';
}

function zoomOut() {
    document.querySelector('.chat-section').style.display = 'flex';
    document.querySelector('.heder').style.display = 'flex';
    document.querySelector('.container').style.height = '95vh';
    document.querySelector('.code-section').style.width = '70%';
    zoomOutBtn.style.display = 'none';
}


zoomInBtn.addEventListener('click', zoomIN);
zoomOutBtn.addEventListener('click', zoomOut);