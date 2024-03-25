//for MODERATOR only
//Event called when the shot changes

var autoStop = document.getElementById("flexSwitchCheckAutostop");


//Play and pause button
playButton.addEventListener('click', (e) => {
    if (video.paused) {
        videoSend("play", video.currentTime)
    } else {
        videoSend("pause", video.currentTime)
    }
})

//change Progressbar on click
progress.addEventListener('click', (e) => {
    const progressTime = (e.offsetX / progress.offsetWidth) * video.duration;
    console.log(currentShot);
    videoSend("skip", progressTime)
})

//check if we need to stop the video based on current shot
//autostop function
//this needs to be called before updateCurrentShot() in timeupdate in videoUser.js
function checkIfAutoStop(){
    if(autoStop.checked && !video.paused){
        if(video.currentTime >= GLOBAL_SHOTS[currentShot].to){
            //console.log("autoStop Times: ", video.currentTime, GLOBAL_SHOTS[currentShot].to)
            videoSend("pause", video.currentTime);
        }
    }
}

function videoSend(cmd, timestamp) {

    var msg = {
        "type": "video",
        "cmd": cmd,
        "data": [
            {
                "ts": timestamp
            }
        ]
    };
    socket.send(JSON.stringify(msg));
}

function sendCompare() {
    var status
    if (video.paused) {
        status = 0
    } else {
        status = 1
    }
    var msg = {
        "type": "video",
        "cmd": "cmp",
        "data": [
            {
                "ts": video.currentTime,
                "status": status
            }
        ]
    };
    socket.send(JSON.stringify(msg));
}

var myInterval = setInterval(sendCompare, 5000);


function stopFunction() {
    clearInterval(myInterval);
}