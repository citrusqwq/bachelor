//for MODERATOR and USER

//global variable for all userstorys
//this is designed save the current state of userstorys
//so u dont have to call the backend over the websocket everytime
//in the array index=id
var GLOBAL_SATZ = []

/**
 * This saves the new or updated satz from backend in global var.
 * @param {json} recv Message from backend
 * @return NONE
 */
 function SatzOnMessage(recv){

    for(var i = 0; i < recv.data.length; ++i){
        if (recv.cmd == "new"){
            while(GLOBAL_SATZ.length < recv.data[i].id){
                GLOBAL_SATZ.push(null)
            }
            GLOBAL_SATZ[recv.data[i].id] = recv.data[i]
        } else if (recv.cmd == "update"){
            GLOBAL_SATZ[recv.data[i].id] = recv.data[i]
        } else if (recv.cmd == "del"){
            GLOBAL_SATZ[recv.data[i]] = null
        }
    }
    //create shotlist from GLOBAL_SATZ
    createShotListSatz();
 }

 /**
 * This function is ued to send a Satz
 * it takes the fields Text and Shot and sends them to the API to be stored
 */
function satzsend() {
    text = document.getElementById("satzText").value;
    shot = document.getElementById("shot-select-satz").value;
    
    var msg = {
        "type": "satz",
        "cmd": "push",
        "data": [
            {
                "id": -1,
                "shot_id": shot,
                "satz": text
            }
        ]   
    };
    
    socket.send(JSON.stringify(msg));

    satzreplace2();

}

/**
 * This function changes the div content when bearbeiten is clicked
 * @param {int} satzID 
 */
function showExistingSatz(satzID){

    document.getElementById("satz-shot-select-update-headline").innerHTML = "Satz " + satzID;
    document.getElementById("satz-update").value= GLOBAL_SATZ[satzID].satz;
    document.getElementById("satzID-hide").value= satzID;

    updateShotSelectionMenu(GLOBAL_SHOTS, "shot-select-update-satz", GLOBAL_SATZ[satzID].shot_id);

    //show edit satz menu
    satzreplace4();
}

/**
 * This function is used to update a Satz (edit)
 */
 function updatesatz() {
    
    satz = document.getElementById("satz-update").value;
    id = document.getElementById("satzID-hide").value;
    shot = document.getElementById("shot-select-update-satz").value;
    
    var msg = {
        "type": "satz",
        "cmd": "push",
        "data": [
            {
                "id": id,
                "shot_id": shot,
                "satz": satz,
            }
        ]
    };
    
    socket.send(JSON.stringify(msg));
    //alert("Satz bearbeitet!");
    satzreplace3();
}

function deletesatz(){

    socket.send(JSON.stringify({
        "type": "satz",
        "cmd": "del",
        "data": [parseInt(document.getElementById("satzID-hide").value, 10)]
    }));

    satzreplace3();
}

/**
 * replaces the div content when hinzufügen is clicked to write a Satz
 */
function satzreplace1() {

    //show current shot in selection menu
    for(var i = 0; i < GLOBAL_SHOTS.length; ++i){
        if((video.currentTime >= GLOBAL_SHOTS[i].frm) && (video.currentTime < GLOBAL_SHOTS[i].to)){
            updateShotSelectionMenu(GLOBAL_SHOTS, "shot-select-satz", i);
        }
    }

    document.getElementById("satz-form-hide").style.display = "none";
    document.getElementById("wrt-satz").style.display = "block";
}

/**
 * replaces the div content after a Satz is written and sent
 */
function satzreplace2() {
    document.getElementById("satz-form-hide").style.display = "block";
    document.getElementById("wrt-satz").style.display = "none";
}


/**
 * replaces the div content after a Satz is updated (edited) when send is clicked
 */
function satzreplace3() {
    document.getElementById("satz-form-hide").style.display = "block";
    document.getElementById("update-satz").style.display = "none";
}


/**
 * replaces the div content when bearbeiten is clicked to update (edit) a Satz
 */
function satzreplace4() {
    document.getElementById("satz-form-hide").style.display = "none";
    document.getElementById("update-satz").style.display = "block";
}


