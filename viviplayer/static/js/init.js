//for MODERATOR and USER

var wsStart = 'ws://';
if (window.location.protocol == 'https:') {
    wsStart = 'wss://'
}
var socket = new WebSocket(wsStart + window.location.host + "/ws" + window.location.pathname);


/**
 * Function called after the video is loaded
 */
function afterVideoLoad(){

    //wait for socket if not open yet
    if (socket.readyState != WebSocket.OPEN){
        socket.onopen = function(event) {
            console.log("WebSocket is open now.");
            init();
        };
    } else {
        //Socket is already open
        init();
    }
    //fix wrong dimensions canvas
    resizedEnded();
}

//retrieve all data from server
function init(){

    console.log("init");
    getAllData("shot");
    getAllData("userstory");
    getAllData("satz");
    getAllData("poll");
    getAllData("annotation");
    getAllData("control");
}

function getAllData(type){
    socket.send(JSON.stringify(
        {
            "type":type,
            "cmd":"get",
            "data":[]
        }
    ));
}

// enable tooltips 
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

// check if we lost connection of websocket
socket.addEventListener('close', function (event) {
    var toastDiv = document.getElementById("error-toast");
    var toastBody = document.getElementById("error-toast-body");
    toastBody.innerHTML = "Error: Verbindung Verloren. Bitte laden sie die Seite neu.";

    var errorToast = new bootstrap.Toast(toastDiv);
    errorToast.show();
});