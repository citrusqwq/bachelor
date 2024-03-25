//for MODERATOR and USER

//global variable for all userstorys
//this is designed save the current state of userstorys
//so u dont have to call the backend over the websocket everytime
//in the array index=id
var GLOBAL_USERSTORY = []

/**
 * This saves the new or updated userstory from backend in global var.
 * @param {json} recv Message from backend
 * @return NONE
 */
function UserStoryOnMessage(recv){
    
    for(var i = 0; i < recv.data.length; ++i){
        if (recv.cmd == "new"){
            while(GLOBAL_USERSTORY.length < recv.data[i].id){
                GLOBAL_USERSTORY.push(null)
            }
            GLOBAL_USERSTORY[recv.data[i].id] = recv.data[i]
        } else if (recv.cmd == "update"){
            GLOBAL_USERSTORY[recv.data[i].id] = recv.data[i] 
        } else if (recv.cmd == "del"){
            GLOBAL_USERSTORY[recv.data[i]] = null
        }
    }
    //create shotlist from GLOBAL_USERSTORY
    createShotListUserStory();
   
}

/**
 * Takes the content of the user story fields and sends them to backend over the websocket
 */
 function userstorysend() {
    
    role = document.getElementById("role").value;
    capability = document.getElementById("capability").value;
    benefit = document.getElementById("benefit").value;
    shot = document.getElementById("shot-select").value;
    
    var msg = {
        "type": "userstory",
        "cmd": "push",
        "data": [
            {
                "id": -1,
                "shot_id": shot,
                "role": role,
                "capability": capability,
                "benefit": benefit
            }
        ]
    };

    socket.send(JSON.stringify(msg));
    //alert("User Story hinzugefügt!");

    replace2();
}

/**
 * This function changes the div content when bearbeiten is clicked
 */
 function showExistingUserStory(storyID){

    document.getElementById("user-stories-shot-select-update-headline").innerHTML = "UserStory " + storyID;
    document.getElementById("userstoryID-hide").value = storyID;
    document.getElementById("role-update").value = GLOBAL_USERSTORY[storyID].role;
    document.getElementById("capability-update").value = GLOBAL_USERSTORY[storyID].capability;
    document.getElementById("benefit-update").value = GLOBAL_USERSTORY[storyID].benefit;
    
    updateShotSelectionMenu(GLOBAL_SHOTS, "shot-select-update", GLOBAL_USERSTORY[storyID].shot_id);
    
    //show edit userstory menu
    replace4();
}

/**
 * This function is used to update a user story 
 */
 function updatestory() {

    role = document.getElementById("role-update").value;
    capability = document.getElementById("capability-update").value;
    benefit = document.getElementById("benefit-update").value;
    shot = document.getElementById("shot-select-update").value;
    userStoryID = document.getElementById("userstoryID-hide").value;
    
    var msg = {
        "type": "userstory",
        "cmd": "push",
        "data": [
            {
                "id": userStoryID,
                "shot_id": shot,
                "role": role,
                "capability": capability,
                "benefit": benefit
            }
        ]
    };
    
    socket.send(JSON.stringify(msg));
    //alert("User Story bearbeitet!");
    replace3();
}

function deletestory(){

    socket.send(JSON.stringify({
        "type": "userstory",
        "cmd": "del",
        "data": [parseInt(document.getElementById("userstoryID-hide").value, 10)]
    }));

    replace3();
}


/**
 * replaces the div content when hinzufügen is clicked to write a user story
 */
function replace1() {
    
    //show current shot in selection menu
    for(var i = 0; i < GLOBAL_SHOTS.length; ++i){
        if((video.currentTime >= GLOBAL_SHOTS[i].frm) && (video.currentTime < GLOBAL_SHOTS[i].to)){
            updateShotSelectionMenu(GLOBAL_SHOTS, "shot-select", i);
        }
    }

    document.getElementById("form-hide").style.display = "none";
    document.getElementById("wrt-usr-stry").style.display = "block";
}


/**
 * replaces the div content after a user story is written to get to the view user stories
 */
function replace2() {
    document.getElementById("form-hide").style.display = "block";
    document.getElementById("wrt-usr-stry").style.display = "none";
}

/**
 * replaces the div content after a user story is updated (edited)
 */
function replace3() {
    document.getElementById("form-hide").style.display = "block";
    document.getElementById("update-usr-stry").style.display = "none";
}


/**
 * replaces the div content to edit a user story
 */
function replace4() {
    document.getElementById("form-hide").style.display = "none";
    document.getElementById("update-usr-stry").style.display = "block";
}

