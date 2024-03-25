//for MODERATOR only

//Update div wenn Slider verändert wird
function onEventUpdateDivs(values, handle){
    GLOBAL_SHOTS[handle + 1].frm = parseInt(values[handle]);
    GLOBAL_SHOTS[handle].to = parseInt(values[handle]);
    console.log("new Values: ", GLOBAL_SHOTS[handle + 1].frm);
        
    console.log("New Data", GLOBAL_SHOTS);
    var msg = {
        "type": "shot",
        "cmd": "push",
        "data": GLOBAL_SHOTS
    }
    socket.send(JSON.stringify(msg));

}


//Slider initialisieren und onEventlistner setzen
function updateSlider(data){

    // video is not loaded yet and video.duration returns NaN
    if (isNaN(video.duration)){
        video.onloadedmetadata = function() {
                updateShotBar(GLOBAL_SHOTS);
                updateSlider(GLOBAL_SHOTS);
        };
        console.log("waiting for video load");
        return;
    } 

    // TODO funktioniert so das der alte slider gelöscht wird und dann wieder ein neuer erstellt wird.
    // ich weiß nicht ob das die ideal Lösung ist aber es funktioniert
    var sliderContainer = document.getElementById("sliderContainer");

    // delete old slider
    while (sliderContainer.firstChild) {
        sliderContainer.removeChild(sliderContainer.lastChild);
    }

    // create new slider div and add it to sliderContainer
    var slider = document.createElement("div");
    slider.id = "slider";
    sliderContainer.appendChild(slider);

    var start = [];
    var toolTips = []
    for(var i = 0; i < data.length; i++){
        if(i + 1 != data.length){
            start.push(data[i + 1].frm);
            toolTips.push( wNumb({decimals: 0}));
        }
    }
    
    noUiSlider.create(slider, {
        start: start,
        connect: true,
        tooltips: toolTips,
        range: {
            'min': 0,
            'max': video.duration,
        }
    }) 

    slider.noUiSlider.on('change', onEventUpdateDivs);
}
