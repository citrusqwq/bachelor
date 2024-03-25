//for MODERATOR and USER

//global variable for all shots
//this is designed save the current state of shots
//so u dont have to call the backend over the websocket everytime
//in the array index=id
var GLOBAL_SHOTS = []
const shotsLoadedEvent = new Event('shotsLoaded', {
    bubbles:true
})
var shotDivs = [];

function shotsOnMessage(recv){

    //backend always sends all shots with new
    GLOBAL_SHOTS = recv.data
    updateCurrentShot();
    if(recv.cmd == "new"){
        //Funktionen in dieser Reihenfolge aufrufen!
        updateShotBar(recv.data);
        video.dispatchEvent(shotsLoadedEvent);
        //check if updateSlider is defined
        //for user updateSlider is not defined
        //https://stackoverflow.com/a/85822
        if(typeof updateSlider === "function"){
            updateSlider(recv.data);
        }
    }
}

function updateShotBar(data){

    //video is not loaded yet and video.duration returns NaN
    //
    //wait for for video only if updateSlider is not defined -> this is the user
    //as user we only need to call updateShotBar after video.onloadedmetadata
    //
    //as moderator we need to call updateShotBar and updateSlider after video.onloadedmetadata
    //this is defined in shotMod.js thats why the moderator can skip this video.onloadedmetadata down below
    if (isNaN(video.duration) && typeof updateSlider !== "function"){
        video.onloadedmetadata = function() {
            updateShotBar(GLOBAL_SHOTS);
        };
        console.log("waiting for video load");
        return;
    } 

    var shotLength;
    var beginOfShot = 0;
    parent = document.getElementById("shotBar");

    //alte shotbar löschen falls vorhanden
    //TODO dies löscht nicht alle divs in der alten bar
    while (parent.firstChild) {
        parent.removeChild(parent.lastChild);
    }
    //erstelle einen div für jeden shot
    for(var i = 0; i < data.length; i++){
        
        var div = document.createElement("div");
        div.innerHTML = '<p class="text-sm-center">'+i.toString()+"</p>";
        
        if((i + 1) != data.length){
            shotLength = (100 / video.duration) * (data[i + 1].frm - data[i].frm);
            div.style.width = shotLength.toString() + "%";
            
        }else if( i + 1 == data.length){
            shotLength = (100 / video.duration) * (video.duration - data[i].frm);
            div.style.width = shotLength.toString() + "%";
            
        }
        
        
        //Styles setzen und anfangswert als ts setzen
        div.style.height = "100%";
        div.style.background = "DeepSkyBlue";
        div.style.border = "1px solid black";
        div.setAttribute('data-ts', data[i].frm.toString());
        div.setAttribute("data-bs-toggle", "tooltip");
        div.setAttribute("data-bs-placement", "top");
        div.setAttribute("title", data[i].description);
        new bootstrap.Tooltip(div);
        
        console.log("added tooltip")
        
        beginOfShot += Math.ceil(shotLength);
       
        //div anclickbar machen und zu jeweiligen shot springen
        div.style.cursor = 'pointer';
        
        //check if videoSend is defined
        //for user videoSend is not defined
        if(typeof videoSend === "function"){
            //make shots clickable for moderator
            div.onclick = function() {
                videoSend("skip", parseInt(this.getAttribute('data-ts')));
            };
        }
            
        //Hover effekt setzen
        div.addEventListener('mouseenter', function(event) {
            event.target.style.background = "white";
        })
        div.addEventListener('mouseleave', function(event) {
            event.target.style.background = "DeepSkyBlue";
        })

        if(parent != null){
            parent.appendChild(div);
        }
        //Füge div zur divList hinzu
        shotDivs.push(div);
    }
}