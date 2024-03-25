//for MODERATOR and USER


function createShotListUserStory(){

    //remove old shotlist
    var oldShotlist = document.getElementById("user-stories-accordion");
    while (oldShotlist.firstChild) {
        oldShotlist.removeChild(oldShotlist.lastChild);
    }
    
    //create map with only unqiue shot_ids
    var shotsForUserStories = {};
    for(var i = 0; i < GLOBAL_USERSTORY.length; ++i){
        if (GLOBAL_USERSTORY[i] != null){
            shotsForUserStories[GLOBAL_USERSTORY[i].shot_id] = 0;
        }
    }

    //create accordion/shotlist entries for each unique shot_id
    Object.keys(shotsForUserStories).forEach(function(key) { 
        createShotListEntry(key, "user-stories");
    });

    //add all UserStories to accordion/shotlist
    for (var i = 0; i < GLOBAL_USERSTORY.length; ++i) {
        if (GLOBAL_USERSTORY[i] != null){
            addUserStoryToShotList(GLOBAL_USERSTORY[i]);
        }
    }
    
}

function createShotListPoll(){
   
    //remove old shotlist
    var oldShotlist = document.getElementById("umfrage-accordion");
    while (oldShotlist.firstChild) {
        oldShotlist.removeChild(oldShotlist.lastChild);
    }
    
    //create map with only unqiue shot_ids
    var shotsForPolls = {};
   
    for(var i = 0; i < GLOBAL_POLL_RESULT.length; ++i){
        shotsForPolls[GLOBAL_POLL_RESULT[i].shot_id.toString()] = 0;
    }

    //create accordion/shotlist entries for each unique shot_id
    Object.keys(shotsForPolls).forEach(function(key) { 
        createShotListEntry(key, "umfrage");
      
    });

    //add all UserStories to accordion/shotlist
    for (var i = 0; i < GLOBAL_POLL_RESULT.length; ++i) {
        
        addPollToShotList(GLOBAL_POLL_RESULT[i]);
    }
    
}

function createShotListSatz(){

    //remove old shotlist
    var oldShotlist = document.getElementById("satz-accordion");
    while (oldShotlist.firstChild) {
        oldShotlist.removeChild(oldShotlist.lastChild);
    }

    //create map with only unqiue shot_ids
    var shotsForSatz = {};
    for(var i = 0; i < GLOBAL_SATZ.length; ++i){
        if (GLOBAL_SATZ[i] != null){
            shotsForSatz[GLOBAL_SATZ[i].shot_id.toString()] = 0;
        }
    }

    //create accordion/shotlist entries for each unique shot_id
    Object.keys(shotsForSatz).forEach(function(key) { 
        createShotListEntry(key, "satz");
    });

    //add all Sätze to accordion/shotlist
    for (var i = 0; i < GLOBAL_SATZ.length; ++i) {
        if (GLOBAL_SATZ[i] != null){
            addSatzToShotList(GLOBAL_SATZ[i]);
        }
    }
}

/**
 * Create one Accordion list item if there is already one do nothing
 * @param {int} shotsID
 * @param {string} idPrefix  the prefix for all ids
 */
function createShotListEntry(shotsID, idPrefix){

    accordion = document.getElementById(idPrefix+"-accordion");

    //check if there is already an accordion body/item for the given shot
    if (document.getElementById(idPrefix+"-accord-body-" + shotsID.toString()) === null) {

        var accorItem = document.createElement('div');
        accorItem.className = "accordion-item";
        
        //header in accorItem
        var accorHeader = document.createElement('h2');
        accorHeader.className = "accordion-header"
        accorHeader.id = idPrefix+"panelsStayOpen-heading-" + shotsID.toString();

        //button in accorHeader
        var accorHeaderButton = document.createElement('button');
        accorHeaderButton.className = "accordion-button collapsed";
        accorHeaderButton.id = idPrefix+"-accord-button-" + shotsID.toString();
        accorHeaderButton.type = "button";
        accorHeaderButton.setAttribute("data-bs-toggle", "collapse")
        accorHeaderButton.setAttribute("data-bs-target", "#"+idPrefix+"-panelsStayOpen-"+ shotsID.toString())
        accorHeaderButton.setAttribute("aria-expanded", "true")
        accorHeaderButton.setAttribute("aria-controls", idPrefix+"-panelsStayOpen-"+ shotsID.toString())
        accorHeaderButton.innerHTML = `${GLOBAL_SHOTS[shotsID].id.toString()}: ${GLOBAL_SHOTS[shotsID].description}`

        accorHeader.appendChild(accorHeaderButton)
        accorItem.appendChild(accorHeader)

        //create div with content for accorItem
        var accorItemDiv = document.createElement('div');
        accorItemDiv.className = "accordion-collapse collapse"
        //accorItemDiv.className = "accordion-collapse collapse show"
        accorItemDiv.id = idPrefix+"-panelsStayOpen-"+ shotsID.toString();
        accorItemDiv.setAttribute("aria-labelledby", idPrefix+"panelsStayOpen-heading-" + shotsID.toString());

        //create div for accordin-body the div is contained in accorItemDiv
        var accorBody = document.createElement('div');
        accorBody.className = "accordion-body";
        accorBody.id = idPrefix+"-accord-body-" + shotsID.toString();
        
        //add hiden counter how many userstorys are saved in this body
        var hiddenUSCounter = document.createElement('input')
        hiddenUSCounter.type = "hidden";
        hiddenUSCounter.id = idPrefix+"-accord-body-count-" + shotsID.toString();
        hiddenUSCounter.value = 0;
        accorBody.appendChild(hiddenUSCounter)

        //create empty list for all user storys in given shot
        var userstoryList = document.createElement('ul');
        userstoryList.className = "list-group";
        userstoryList.id = idPrefix+"-accord-body-list-"+ shotsID.toString();
        accorBody.appendChild(userstoryList)

        accorItemDiv.appendChild(accorBody);
        accorItem.appendChild(accorItemDiv)
        accordion.appendChild(accorItem);
    }
}

/**
 * Add a userstory to the accordion/list
 * @param {json} userStory 
 */
function addUserStoryToShotList(userStory){

    //create list item
    var listItem = document.createElement('li');
    listItem.className = "list-group-item";
    listItem.id = "user-stories-accord-body-list-item-"+ userStory.id.toString();

    //div with name and button
    var nameDiv = document.createElement('div');
    nameDiv.innerHTML = "UserStory " + userStory.id.toString();

    //add button to change userstory
    var bearbeitenButton = document.createElement('button');
    bearbeitenButton.type = "button";
    bearbeitenButton.className = "btn btn-outline-primary btn-sm mb-1 space-bt bott";
    bearbeitenButton.innerHTML = "Bearbeiten"
    bearbeitenButton.addEventListener("click", function(event){
        showExistingUserStory(userStory.id)
    })
    //nameDiv.innerHTML += '<button class="btn btn-primary space-bt bott" onclick="showExistingUserStory('+ userStory.id +')"/> Bearbeiten';

    nameDiv.appendChild(bearbeitenButton)
    listItem.appendChild(nameDiv);

    //add textArea to preview userstory
    var textArea = document.createElement("textarea");
    textArea.id = "user-stories-accord-body-list-item-text-"+ userStory.id.toString();
    textArea.setAttribute("readonly", "");
    textArea.className = "form-control bott-2";
    textArea.type = "text";
    textArea.innerHTML = userStory.role + " " + userStory.capability + " " + userStory.benefit
    textArea.style.display = "block";
    listItem.appendChild(textArea);

    createShotListEntry(userStory.shot_id, "user-stories");
    document.getElementById("user-stories-accord-body-list-" + userStory.shot_id.toString()).appendChild(listItem);
    document.getElementById("user-stories-panelsStayOpen-"+  userStory.shot_id.toString()).className = "accordion-collapse collapse show"

    checkIfHideTextAreaAdd(userStory.shot_id, "user-stories");
}

/**
 * Add a userstory to the accordion/list
 * @param {json} poll
 */
 function addPollToShotList(poll){

    //create list item
    var listItem = document.createElement('li');
    listItem.className = "list-group-item";
    listItem.id = "umfrage-accord-body-list-item-"+ poll.id.toString();
    //div with name and button
    var nameDiv = document.createElement('div');
    nameDiv.innerHTML = "Umfrage " + poll.id.toString();
    listItem.appendChild(nameDiv);

    //add textArea to preview poll result
    var textArea = document.createElement("textarea");
    textArea.id = "umfrage-accord-body-list-item-text-"+ poll.id.toString();
    textArea.setAttribute("readonly", "");
    textArea.className = "form-control bott-2";
    textArea.type = "text";
    var rowCnt = 2;
    textArea.innerHTML = poll.question + "\n\n"
    for(var i = 0; i < poll.result.length; ++i){
        textArea.innerHTML += poll.result[i].option + " " + poll.result[i].count + "\n";
        rowCnt++;
    }
    textArea.style.overflow= "hidden";
    textArea.style.display = "block";
    textArea.rows = rowCnt.toString();
    textArea.style.resize = "none";
    //textArea.style.overflow = "hidden";
    listItem.appendChild(textArea);

    createShotListEntry(poll.shot_id, "umfrage");
    document.getElementById("umfrage-accord-body-list-" + poll.shot_id.toString()).appendChild(listItem);
    document.getElementById("umfrage-panelsStayOpen-"+  poll.shot_id.toString()).className = "accordion-collapse collapse show"

 }


/**
 * Add a userstory to the accordion/list
 * @param {json} satz 
 */
 function addSatzToShotList(satz){

    //create list item
    var listItem = document.createElement('li');
    listItem.className = "list-group-item";
    listItem.id = "satz-accord-body-list-item-"+ satz.id.toString();

    //div with name and button
    var nameDiv = document.createElement('div');
    nameDiv.innerHTML = "Satz " + satz.id.toString();

    //add button to change userstory
    var bearbeitenButton = document.createElement('button');
    bearbeitenButton.type = "button";
    bearbeitenButton.className = "btn btn-outline-primary btn-sm mb-1 space-bt bott";
    bearbeitenButton.innerHTML = "Bearbeiten"
    bearbeitenButton.addEventListener("click", function(event){
        showExistingSatz(satz.id)
    })

    nameDiv.appendChild(bearbeitenButton)
    listItem.appendChild(nameDiv);

    //add textArea to preview userstory
    var textArea = document.createElement("textarea");
    textArea.id = "satz-accord-body-list-item-text-"+ satz.id.toString();
    textArea.setAttribute("readonly", "");
    textArea.className = "form-control bott-2";
    textArea.type = "text";
    textArea.innerHTML = satz.satz
    textArea.style.display = "block";
    listItem.appendChild(textArea);

    createShotListEntry(satz.shot_id, "satz");
    document.getElementById("satz-accord-body-list-" + satz.shot_id.toString()).appendChild(listItem);
    document.getElementById("satz-panelsStayOpen-"+  satz.shot_id.toString()).className = "accordion-collapse collapse show"

    checkIfHideTextAreaAdd(satz.shot_id, "satz");
}

/**
 * check if we need to hide the preview textareas for shot
 * @param {int} ShotID 
 */
function checkIfHideTextArea(ShotID, count, idPrefix){
    var list = document.getElementById(idPrefix+"-accord-body-list-" + ShotID.toString());
    var listItem = list.getElementsByTagName("li");
    console.log(ShotID, count);

    for (var i = 0; i < listItem.length; i++) {
        for (var j = 0; j < listItem[i].childNodes.length; ++j){
            if (listItem[i].childNodes[j].tagName.toLowerCase() === "textarea"){
                if (count <= "4") {
                    listItem[i].childNodes[j].style.display = "block";
                    console.log("checkIfHideTextArea <=4", listItem[i].childNodes[j])
                } else {
                    listItem[i].childNodes[j].style.display = "none";
                    console.log("checkIfHideTextArea > 4", listItem[i].childNodes[j])
                }
            }
        }
    }
}

/**
 * Add one to counter of hotID(hidden field in html) and check if we need to hide the textarea
 * @param {int} ShotID 
 */
function checkIfHideTextAreaRemove(ShotID, idPrefix) {
    var count = document.getElementById(idPrefix+"-accord-body-count-" + ShotID.toString());
    count.value = parseInt(count.value, 10) - 1;

    checkIfHideTextArea(ShotID, count.value, idPrefix);
}

/**
 * Substract one of the counter of ShotID(hidden field in html) and check if we need to hide the textarea
 * @param {int} ShotID 
 */
function checkIfHideTextAreaAdd(ShotID, idPrefix) {
    var count = document.getElementById(idPrefix+"-accord-body-count-" + ShotID.toString());
    count.value = parseInt(count.value, 10) + 1;

    checkIfHideTextArea(ShotID, count.value, idPrefix);
}

/**
 * This adds the shots to the shots selection menu if you write or update a userstory/satz
 * @param {[json]} shotsArray data array from shots
 * @param {string} selectByID which <select></select> to add the shot options
 * @param {int} defaultID the option which should be marked as default(shot_id)
 * @return NONE
 */
 function updateShotSelectionMenu(shotsArray, selectByID, defaultID){

    select = document.getElementById(selectByID);

    while (select.firstChild) {
        select.removeChild(select.lastChild);
    }

    for(var i = 0; i < shotsArray.length; i++){
        var newOpt = document.createElement("option")
        if (i === defaultID){
            newOpt.setAttribute("selected", true);
        }
        newOpt.value = shotsArray[i].id
        newOpt.innerHTML = `${shotsArray[i].id.toString()}: ${shotsArray[i].description}`
        select.appendChild(newOpt)
    }
}
