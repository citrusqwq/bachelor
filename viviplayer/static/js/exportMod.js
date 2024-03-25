//for MODERATOR only

//string array with all shots
var shots;
//string array with all user storys
var storys;
//string array wiht all sentences
var sentence;

function activateExportWindow() {
    const export_window = document.getElementById('exportWindow');
    const overlay = document.getElementById('overlay-export-popup');

    sentence = GLOBAL_SATZ;
    storys = GLOBAL_USERSTORY;

    listUserStorys();
    listSatz();
    deleteContent();

    export_window.classList.add("active");
    overlay.classList.add("active");
}

function deactivateExportWindow() {
    const export_window = document.getElementById('exportWindow');
    const overlay = document.getElementById('overlay-export-popup');
    export_window.classList.remove("active");
    overlay.classList.remove("active");

    deleteContent();
}

function startDownload(type) {
    document.getElementById('download_file').src = window.location.origin + "/api" + window.location.pathname + "export/?file=" + type;
}

function exportChangeTabs(tab){
    const tabUserStory = document.getElementById("export-window-list-userstory");
    const tabSatz = document.getElementById("export-window-list-satz");
    const content1 = document.getElementById("export-window-content-1");
    const content2 = document.getElementById("export-window-content-2");
    const content3 = document.getElementById("export-window-content-3");

    if(tab === "userstory"){
        deleteContent();
        tabUserStory.classList.add("active");
        tabSatz.classList.remove("active");
        content2.style.display = 'block';
        content3.style.display = 'block';
    }
    if(tab === "satz"){
        deleteContent();
        tabSatz.classList.add("active");
        tabUserStory.classList.remove("active");
        content2.style.display = 'none';
        content3.style.display = 'none';
    }
    return;
}

function listUserStorys(){
    var list = document.getElementById("export-window-list-userstory");
    
    while (list.firstChild) {
        list.removeChild(list.lastChild);
    }

    for(let i = 0; i < storys.length; i++){
        if (storys[i] == null){
            continue
        }
        var itemContainer = document.createElement("li");

        var bearbeitenButton = document.createElement("button");
        bearbeitenButton.className ="btn btn-primary"
        bearbeitenButton.style.width = "100%";
        bearbeitenButton.style.marginBottom = "5px";
        bearbeitenButton.innerHTML = "User Story " + i.toString();
        bearbeitenButton.addEventListener("click", function(event){
            showUserStoryContent(i);
        })
        itemContainer.appendChild(bearbeitenButton);
        list.appendChild(itemContainer);
    }
}

function listSatz(){
    var list = document.getElementById("export-window-list-satz");
    
    while (list.firstChild) {
        list.removeChild(list.lastChild);
    }

    for(let i = 0; i < sentence.length; i++){
        if (sentence[i] == null){
            continue
        }
        var itemContainer = document.createElement("li");
        var bearbeitenButton = document.createElement("button");
        bearbeitenButton.className ="btn btn-primary"
        bearbeitenButton.style.width = "100%";
        bearbeitenButton.style.marginBottom = "5px";
        bearbeitenButton.innerHTML = "Satz " + i.toString();
        bearbeitenButton.addEventListener("click", function(event){
            showSatzContent(i);
        })
        itemContainer.appendChild(bearbeitenButton);
        list.appendChild(itemContainer);
    }
}

function showUserStoryContent(id){
    deleteContent();
    const content1 = document.getElementById("export-window-content-1");
    const content2 = document.getElementById("export-window-content-2");
    const content3 = document.getElementById("export-window-content-3");
    const currentStory = document.getElementById("export-window-edit-content-shotid");
    const shotID = document.getElementById("screenshot-shot-id");
    const screenshot = document.getElementById("export-window-shot-screenshot");
    const screenshotChangeButton = document.getElementById("export-window-screenshot-change")
    const modalTitle = document.getElementById("modalTitle");
    const changeScreenshotVideo = document.getElementById("export-screenshot-change");
    const meetingVideo = document.getElementById("meeting-video").src;
    const currentShotID = document.getElementById("export-screenshot-change-currentshotid");
    const timeline = document.getElementById("export-screenshot-change-video-timeline");
    const timestamp = document.getElementById("export-screenshot-change-video-timeline-timestamp");
    const timestampMin = document.getElementById("timesamp-min");
    const timestampMax = document.getElementById("timesamp-max");
    const exportWindowContent = document.getElementById("export-content");
    const infoText = document.getElementById("export-content-work-info");

    exportWindowContent.style.display = "block";
    infoText.style.display ="none";
    content1.value= storys[id].role;
    content2.value = storys[id].capability;
    content3.value = storys[id].benefit;
    currentStory.innerHTML = "User Story " + id;
    shotID.innerHTML = "Screenshot zu Shot " + GLOBAL_SHOTS[storys[id].shot_id].description;
    screenshot.src = document.getElementById("GLOBAL_SCREENSHOT_PATH").value + storys[id].shot_id + ".jpg"
        + "?t=" + new Date().getTime(); // dont use cached image
    screenshotChangeButton.style.display = "block";
    modalTitle.innerHTML = GLOBAL_SHOTS[storys[id].shot_id].description;
    var videoFrom = String(GLOBAL_SHOTS[storys[id].shot_id].frm)
    var videoTo = String(GLOBAL_SHOTS[storys[id].shot_id].to)
    changeScreenshotVideo.src = String(meetingVideo) + "#t=" + String(videoFrom) + "," + String(videoTo);
    currentShotID.value = storys[id].shot_id;
    timeline.min = parseInt(GLOBAL_SHOTS[storys[id].shot_id].frm,10);
    timeline.max = parseInt(GLOBAL_SHOTS[storys[id].shot_id].to,10);
    timeline.value = parseInt(GLOBAL_SHOTS[storys[id].shot_id].frm,10);
    timestamp.innerHTML = "aktuell: " + String(GLOBAL_SHOTS[storys[id].shot_id].frm);
    timestampMin.innerHTML = "Min: " + String(GLOBAL_SHOTS[storys[id].shot_id].frm);
    timestampMax.innerHTML = "Max: " + String(GLOBAL_SHOTS[storys[id].shot_id].to);
}

function showSatzContent(id){
    deleteContent();
    const content = document.getElementById("export-window-content-1");
    const currentSatz = document.getElementById("export-window-edit-content-shotid");
    const shotID = document.getElementById("screenshot-shot-id");

    const screenshot = document.getElementById("export-window-shot-screenshot");
    const screenshotChangeButton = document.getElementById("export-window-screenshot-change")
    const modalTitle = document.getElementById("modalTitle");
    const changeScreenshotVideo = document.getElementById("export-screenshot-change");
    const meetingVideo = document.getElementById("meeting-video").src;
    const currentShotID = document.getElementById("export-screenshot-change-currentshotid");

    const timeline = document.getElementById("export-screenshot-change-video-timeline");
    const timestamp = document.getElementById("export-screenshot-change-video-timeline-timestamp");
    const timestampMin = document.getElementById("timesamp-min");
    const timestampMax = document.getElementById("timesamp-max");
    const exportWindowContent = document.getElementById("export-content");
    const infoText = document.getElementById("export-content-work-info");

    exportWindowContent.style.display = "block";
    infoText.style.display ="none";
    content.value= sentence[id].satz;
    currentSatz.innerHTML = "Satz " + id;
    shotID.innerHTML = "Screenshot zu Shot " + GLOBAL_SHOTS[sentence[id].shot_id].description;

    screenshot.src = document.getElementById("GLOBAL_SCREENSHOT_PATH").value + sentence[id].shot_id + ".jpg" 
        + "?t=" + new Date().getTime(); // dont use cached image
    screenshotChangeButton.style.display = "block";
    modalTitle.innerHTML = GLOBAL_SHOTS[sentence[id].shot_id].description;
    var videoFrom = String(GLOBAL_SHOTS[sentence[id].shot_id].frm)
    var videoTo = String(GLOBAL_SHOTS[sentence[id].shot_id].to)
    changeScreenshotVideo.src = String(meetingVideo) + "#t=" + String(videoFrom) + "," + String(videoTo);
    currentShotID.value = sentence[id].shot_id;
    timeline.min = parseInt(GLOBAL_SHOTS[sentence[id].shot_id].frm,10);
    timeline.max = parseInt(GLOBAL_SHOTS[sentence[id].shot_id].to,10);
    timeline.value = parseInt(GLOBAL_SHOTS[sentence[id].shot_id].frm,10);
    timestamp.innerHTML = "aktuell: " + String(GLOBAL_SHOTS[storys[id].shot_id].frm);
    timestampMin.innerHTML = "Min: " + String(GLOBAL_SHOTS[storys[id].shot_id].frm);
    timestampMax.innerHTML = "Max: " + String(GLOBAL_SHOTS[storys[id].shot_id].to);
}

function sendScreenshotSave(){
    var changeScreenshotVideo = document.getElementById("export-screenshot-change");
    var currentTime = parseFloat(changeScreenshotVideo.currentTime, 10);
    var currentShotID = parseInt(document.getElementById("export-screenshot-change-currentshotid").value, 10)
    changeScreenshot(currentShotID,currentTime);
}

function safeData(){
    const content1 = document.getElementById("export-window-content-1");
    const content2 = document.getElementById("export-window-content-2");
    const content3 = document.getElementById("export-window-content-3");
    const currentContent = document.getElementById("export-window-edit-content-shotid");
    const getInformation = currentContent.innerHTML.split(' ');
    if(getInformation[0] === "User"){
        var id = parseInt(getInformation[2],10);
        storys[id].role = content1.value;
        storys[id].capability = content2.value;
        storys[id].benefit = content3.value;

        var msg = {
            "type":"userstory",
            "cmd":"push",
            "data":[{
                "id":id,
                "shot_id": storys[id].shot_id,
                "role": storys[id].role,
                "capability": storys[id].capability,
                "benefit": storys[id].benefit
            }]
        };
        socket.send(JSON.stringify(msg));
    }
    if(getInformation[0] === "Satz"){
        var id = parseInt(getInformation[1],10);
        sentence[id].satz = content1.value;

        var msg = {
            "type":"satz",
            "cmd":"push",
            "data":[{
                "id":id,
                "shot_id": sentence[id].shot_id,
                "satz": sentence[id].satz
            }]
        };
        socket.send(JSON.stringify(msg));
    }
    deleteContent();
}

function deleteContent(){
    const title = document.getElementById("export-window-edit-content-shotid");
    const content1 = document.getElementById("export-window-content-1");
    const content2 = document.getElementById("export-window-content-2");
    const content3 = document.getElementById("export-window-content-3");
    const shotID = document.getElementById("screenshot-shot-id");
    const screenshot = document.getElementById("export-window-shot-screenshot");
    const screenshotChangeButton = document.getElementById("export-window-screenshot-change");
    const exportWindowContent = document.getElementById("export-content");
    const infoText = document.getElementById("export-content-work-info");

    exportWindowContent.style.display = "none";
    infoText.style.display = "block";
    title.innerHTML = null;
    content1.value = null;
    content2.value = null;
    content3.value = null;
    shotID.innerHTML = null;
    // use empty data
    screenshot.src = "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=";
    screenshotChangeButton.style.display = "none";
}

function changeScreenshot(shot_id, timestamp){

    console.log(shot_id, timestamp)

    fetch(window.location.origin + "/api" + window.location.pathname + "screenshot/", {
        method: "POST",
        headers: {'Content-Type': 'application/json', "X-CSRFToken": window.CSRF_TOKEN},
        body: JSON.stringify({
            shot_id: shot_id,
            time: timestamp
        })
      }).then(res => {
            //reload screenshot
            var img = document.getElementById("export-window-shot-screenshot");
            img.src = img.src + "?t=" + new Date().getTime(); // trick browser into reload
      });
}

function changeTimeScreenshotExport(mode){
    var theVideo = document.getElementById("export-screenshot-change");
    const timestamp = document.getElementById("export-screenshot-change-video-timeline-timestamp");
    const videoSlider = document.getElementById("export-screenshot-change-video-timeline");
    if(mode === "forward"){
        var forwardSkip = 0.5;
        vid_currentTime = theVideo.currentTime;
        if(vid_currentTime + 1 > videoSlider.max){return}
        theVideo.currentTime = vid_currentTime + forwardSkip;
        timestamp.innerHTML = "aktuell:" + String(vid_currentTime + forwardSkip);
        videoSlider.value = vid_currentTime + forwardSkip;
    }
    if(mode === "backward"){
        var backwardSkip = 0.5;
        vid_currentTime = theVideo.currentTime;
        if(vid_currentTime - 1 < videoSlider.min){return}
        theVideo.currentTime = vid_currentTime - backwardSkip;
        timestamp.innerHTML = "aktuell:" + String(vid_currentTime - backwardSkip);
        videoSlider.value = vid_currentTime - backwardSkip;
    }
}

function exportScreenshotChange(){
    const videoSlider = document.getElementById("export-screenshot-change-video-timeline");
    var theVideo = document.getElementById("export-screenshot-change");
    videoSlider.value = theVideo.currentTime;
    
}

function changeTimestamp(value){
    const timestamp = document.getElementById("export-screenshot-change-video-timeline-timestamp")
    var theVideo = document.getElementById("export-screenshot-change");
    theVideo.currentTime = value;
    timestamp.innerHTML = "aktuell: " + String(value);
}