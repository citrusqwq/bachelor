//for MODERATOR only

function activateEditShotListPopup(){
    const popup = document.getElementById('shot-edit-list-popup');
    const overlay = document.getElementById('overlay-shot-edit-popup');

    popup.classList.add("active");
    overlay.classList.add("active");
    listAllShots(GLOBAL_SHOTS);
}
function listAllShots(shotsArray){
    var list = document.getElementById("shot-list");
    
    while (list.firstChild) {
        list.removeChild(list.lastChild);
    }
    if(shotsArray.length == 0){
        var shot = document.createElement('li');
        shot.innerHTML = "Kein Shot verfügbar";
        return;
    }

    for(let i = 0; i < shotsArray.length; i++){
        var itemContainer = document.createElement("div");
        itemContainer.className="mb-3";
        itemContainer.style.alignContent="left";
        
        var shotName = i.toString() + ": " + shotsArray[i].description.toString() + "&nbsp;&nbsp;";
        var nameP = document.createElement("p");
        nameP.innerHTML = shotName;
        nameP.style.display = "inline-block";
        itemContainer.appendChild(nameP);

        var bearbeitenButton = document.createElement("button");
        bearbeitenButton.className = "btn btn-outline-primary btn-sm";
        bearbeitenButton.innerHTML = "bearbeiten";
        bearbeitenButton.style.display = "inline-block";
        bearbeitenButton.style.marginRight = "3px";
        bearbeitenButton.addEventListener("click", function(event){
            activateShotEditPopup(shotsArray[i].id, shotsArray[i].description);
        })
        itemContainer.appendChild(bearbeitenButton);
        list.appendChild(itemContainer);
    }
}
function deactivateEditShotListPopup(){
    const popup = document.getElementById('shot-edit-list-popup');
    const overlay = document.getElementById('overlay-shot-edit-popup');

    popup.classList.remove("active");
    overlay.classList.remove("active");
}
function activateShotEditPopup(id, shotName){
    const popup = document.getElementById('shot-edit-popup');
    const overlay = document.getElementById('overlay-shot-edit-popup');
    const number = document.getElementById('current-shot-number');
    const name = document.getElementById('edit-name');
    name.innerHTML = shotName;
    name.value = shotName;

    number.innerHTML = "Shot " + id;
    popup.classList.add("active");
}
function deactivateShotEditPopup(){
    const popup = document.getElementById('shot-edit-popup');
    popup.classList.remove("active");
}
function sendShotName(){
    const currentShot = document.getElementById('edit-name');
    const currentShotName = currentShot.innerHTML;
    const newshotName = currentShot.value;
    console.log("leerer shot name   ",newshotName);
    if(newshotName === ""){
        alert("shotName must not be empty");
        return;
    }
    if(currentShotName != newshotName){
        const shotNmb = document.getElementById('current-shot-number');
        var number = shotNmb.innerHTML.toString();
        var arr = number.split(' ');
        var shotnumber = parseInt(arr[1],10)
        var shot = GLOBAL_SHOTS[shotnumber];
        var frm = shot.frm;
        var to = shot.to;
        console.log("id    ",shotnumber);
        var msg = {
            "type":"shot",
            "cmd":"push",
            "data":[{
                "id":shotnumber,
                "description":newshotName,
                "frm":frm,
                "to":to
            }]
        };
        socket.send(JSON.stringify(msg));
        deactivateShotEditPopup();
        deactivateEditShotListPopup();
    }
    if(currentShotName == newshotName){
        deactivateShotEditPopup();
        return;
    }
}
function deleteCurrentShot(){
    const shotNmb = document.getElementById('current-shot-number');
    var userConfirm = window.confirm("Soll der Shot wirklich gelöscht werden?");
    if(userConfirm == true){
        var number = shotNmb.innerHTML.toString();
        var arr = number.split(' ');
        var shotnumber = parseInt(arr[1],10)
        var msg = {
                "type":"shot",
                "cmd":"del",
                "data":[shotnumber]
        };
        socket.send(JSON.stringify(msg));
        deactivateShotEditPopup();
        deactivateEditShotListPopup();
    }
    if(userConfirm == false){
        return;
    }
}
function insertShot(direction){
    const shotNmb = document.getElementById('current-shot-number');
    if(direction === "before"){
        var number = shotNmb.innerHTML.toString();
        var arr = number.split(' ');
        var shotnumber = parseInt(arr[1],10)
        var msg = {
                "type":"shot",
                "cmd":"pushleft",
                "data":[shotnumber]
        };
        socket.send(JSON.stringify(msg));
        deactivateShotEditPopup();
        deactivateEditShotListPopup();
    }
    if(direction === "after"){
        var number = shotNmb.innerHTML.toString();
        var arr = number.split(' ');
        var shotnumber = parseInt(arr[1],10)
        var msg = {
                "type":"shot",
                "cmd":"pushright",
                "data":[shotnumber]
        };
        socket.send(JSON.stringify(msg));
        deactivateShotEditPopup();
        deactivateEditShotListPopup();
    }
    
}
function activateAnnotationsPopup(){
    const overlay = document.getElementById('overlay-shot-edit-popup');
    const popup = document.getElementById('annotations-popup');

    popup.classList.add("active");
    overlay.classList.add("active");
}
function deactivateShotAnnotation(){
    const overlay = document.getElementById('overlay-shot-edit-popup');
    const popup = document.getElementById('annotations-popup');

    popup.classList.remove("active");
    overlay.classList.remove("active");
}
function shotAnnotation(){
    window.alert("annotations");
    deactivateShotEditPopup();
    deactivateEditShotListPopup();
    activateAnnotationsPopup();
}