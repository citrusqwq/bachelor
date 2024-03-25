//for MODERATOR and USER

var GLOBAL_POLL_RESULT = []

function ListUmfrageOnMessage(recv){
    
    for(var i = 0; i < recv.data.length; ++i){
        if (recv.cmd == "result" && !recv.data[i].active){
            GLOBAL_POLL_RESULT.push(recv.data[i])
        } else if (recv.cmd == "update"){
            try {
                GLOBAL_POLL_RESULT[getIndexByPollID(recv.data[i].id)].shot_id = recv.data[i].shot_id
            } catch (error) {
                //the poll_id was not found in array
                //the update is for a poll that is private, as user we can skip this update
            }
        }
    }
    //create shotlist from GLOBAL_POLL_RESULT
    createShotListPoll();
}

/**
 * This function is needed since a user has a different list than the moderator
 * The GLOBAL_POLL_RESULT is not equal in length for user and mod. Thats why GLOBAL_POLL_RESULT[poll_id] only works for the mod.
 * Since he has all the public and private poll in that array. The user has only public polls.
 * @param {int} pollID 
 * @returns index of poll_id in GLOBAL_POLL_RESULT 
 */
function getIndexByPollID(pollID){
    for (var i = 0; i < GLOBAL_POLL_RESULT.length; ++i){
        if (GLOBAL_POLL_RESULT[i].id === pollID){
            return i
        }else{
            NaN
        }
    }
}

/**
 * this function adds neu answers to the list of poll's options
 */
function addoption() {

var l= document.getElementById("optionlist");
var op= document.getElementById("new-option").value;

l.innerHTML += '<li class="list-group-item " value=' +'"'+ op + '"' + '>'+op+'<button id="btnClick" onclick="remoption(this.parentNode)" type="reset"class="btn btn-danger space-bt ">Löschen</button>'+'</li>';
clearop();
}

/**
 * clears the text area after adding a new answer
 */

function clearop(){
document.getElementById("new-option").value="";

}
/**
 * clear an option from the list
 */
function remoption(element){
    element.parentNode.removeChild(element);
}

/**
 * Takes the content of the poll and sends them to backend over the websocket
 */
function umfragesend() {

    question = document.getElementById("frageText").value;
    options = document.getElementById("optionlist").getElementsByTagName("li");
    shot = document.getElementById("shot-select-umfrage").value;
    var array = [];
    for (let i = 0; i < options.length; i++) {
        let item = options[i].getAttribute('value');
        array.push(item);

    }
    var msg = {
        "type": "poll",
        "cmd": "create",
        "data": [
            {
                "shot_id": shot,
                "response": 0,
                "question": question,
                "options": array
    
            }
        ]
    };

    socket.send(JSON.stringify(msg));
    removeoldpoll();
    umfragereplace2();
}

/**
 * removes the old poll and creats anew one again
 */
function removeoldpoll(){
    var oldpoll = document.getElementById("optionlist");
    // clear the old coll
    while (oldpoll.firstChild) oldpoll.firstChild.remove();
    oldpoll.innerHTML= poll_body;
    document.getElementById("frageText").value="";

}

/**
 * This shows the toast/popup to vote in a poll.
 * @param {array} recv 
 */
function umfrageOnMessage(recv){

    for(var i = 0; i < recv.data.length; ++i){

        //skip non active polls
        if(!recv.data[i].active){
            continue;
        }

        var toastHtml = document.getElementById("umfrageToast");

        var toastBody = document.getElementById("umfrage-toast-body");
        // clear the old content
        while (toastBody.firstChild) toastBody.firstChild.remove();
        
        
        // get the question and options from received data and show them in the toast
        var pollId = recv.data[i].id;
        var question = recv.data[i].question;
        var questionContainer = document.createElement("strong");
        questionContainer.innerHTML = question;

        var options = recv.data[i].options;
        var optionContainer = document.createElement("div");
        optionContainer.className = "option-container";
        
        for(var j = 0; j < options.length; j++){
            var option = document.createElement("button");
            option.className = "btn btn-primary";
            option.innerHTML = options[j];
            option.value=j;
            option.onclick=function() {sendanswer(this, pollId);}
            optionContainer.appendChild(option);
        }
        toastBody.appendChild(questionContainer);
        toastBody.appendChild(optionContainer);

        var toast = new bootstrap.Toast(toastHtml);

        toast.show();
    }
}
/**
 * sends the vote and then hides the toast
 */

function sendanswer(answer_id, pollId){
    var toastHtml = document.getElementById("umfrageToast");
    var toast = new bootstrap.Toast(toastHtml);
    var msg ={
        "type": "poll",
        "cmd": "vote",
        "data": [
            {
                "poll_id": pollId,
                "vote":[parseInt(answer_id.value)]
            }
        ]
    }
    socket.send(JSON.stringify(msg));
    toast.hide();

}

function umfrageHide(){
    var toastHtml = document.getElementById("umfrageToast");
    var toast = new bootstrap.Toast(toastHtml);
    toast.hide();

}

/**
 * This shows the live result for the moderator
 * This doesnt need to be in a own mod file since the user doesn't recieve result messages.
 * @param {array} recv 
 */
function umfrageResultMod(recv){

    for(var i = 0; i < recv.data.length; ++i){

        //skip non active polls
        if(!recv.data[i].active){
            continue;
        }

        var toastHtml = document.getElementById("umfrageToast-control");
        var toastBody = document.getElementById("umfrage-toast-body-control");
        while (toastBody.firstChild) toastBody.firstChild.remove();
        
        var pollId = recv.data[0].id;
        var question = recv.data[0].question;
        var questionContainer = document.createElement("strong");
        questionContainer.innerHTML = question;
        var result = recv.data[0].result;
        //console.log(result);
        var optionContainer = document.createElement("div");
        optionContainer.className = "box";
        toastBody.appendChild(questionContainer);

        for(var j = 0; j < result.length; j++){
            var option = document.createElement("textarea");
            option.className = "form-control bott-2";
            option.type = "text";
            option.setAttribute("readonly", "");
            option.value = result[j].option;
            option.value += "     : " + result[j].count;
            toastBody.appendChild(option);
        }
    
        toastBody.appendChild(optionContainer);
        var toast = new bootstrap.Toast(toastHtml);
        
        var beenden = document.getElementById("UmfrageBeenden");
        beenden.onclick=function() {umfrageEnd(pollId, false);}
        
        var publish = document.getElementById("ergebnisZeigen");
        publish.onclick=function() {umfrageEnd(pollId, true);}
        

        toast.show();
    }
}

function umfrageEnd(pollID, publish){
    var toastHtml1 = document.getElementById("umfrageToast");
    var toast1 = new bootstrap.Toast(toastHtml1);
    
    var msg ={
        "type": "poll",
        "cmd": "close",
        "data":[{
            "id": pollID,
            "publish": publish
        }]
    }
    
    socket.send(JSON.stringify(msg));
    var toastHtml1 = document.getElementById("umfrageToast");
    var toast1 = new bootstrap.Toast(toastHtml1);
    var toastHtml2 = document.getElementById("umfrageToast-control");
    var toast2 = new bootstrap.Toast(toastHtml2);
    toast1.hide();
    toast2.hide();
    
}

 


function umfragereplace1() {

    //show current shot in selection menu
    for(var i = 0; i < GLOBAL_SHOTS.length; ++i){
        if((video.currentTime >= GLOBAL_SHOTS[i].frm) && (video.currentTime < GLOBAL_SHOTS[i].to)){
            updateShotSelectionMenu(GLOBAL_SHOTS, "shot-select-umfrage", i);
        }
    }

    document.getElementById("umfrage-form-hide").style.display = "none";
    document.getElementById("wrt-umfrage").style.display = "block";
}



/**
 * replaces the div content after a Umfrage is written and sent
 */
 function umfragereplace2() {
    document.getElementById("umfrage-form-hide").style.display = "block";
    document.getElementById("wrt-umfrage").style.display = "none";
}


poll_body = `<li id="op1"class="list-group-item" value="ja"> ja<button onclick="remoption(this.parentNode)" id="btnClick" type="reset" 
class="btn btn-danger space-bt">Löschen</button></li>
<li id="op2" class="list-group-item" value="eher ja"> eher ja <button onclick="remoption(this.parentNode)" id="btnClick" type="reset" 
class="btn btn-danger space-bt">Löschen</button></li>
<li id="op3" class="list-group-item" value="eher nein">eher nein<button onclick="remoption(this.parentNode)" id="btnClick" type="reset" 
class="btn btn-danger space-bt">Löschen</button></li>
<li id="op4" class="list-group-item" value="nein">nein<button onclick="remoption(this.parentNode)" id="btnClick" type="reset" 
class="btn btn-danger space-bt">Löschen</button></li> `