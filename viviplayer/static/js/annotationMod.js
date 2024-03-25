//Moderator only

var canvasScreenShot = document.querySelector('#screenShotCanvas');
var ctxScreenShot = canvasScreenShot.getContext('2d');
//function called when "add annotation" is clicked
function addAnnotation(){
  videoSend("pause", video.currentTime)
  canvasScreenShot.width = video.clientWidth / 2;
  canvasScreenShot.height = video.clientHeight / 2;
  ctxScreenShot.fillRect(0, 0, canvasScreenShot.width, canvasScreenShot.height);
  ctxScreenShot.drawImage(video, 0, 0, canvasScreenShot.width, canvasScreenShot.height);
}

//function called when "delete annotation" is called
function deleteAnnotation(){
  msg = {
    "type": "annotation", 
    "cmd": "del", 
    "data": [GLOBAL_ANNOS[currentShot].id]
  } 
  socket.send(JSON.stringify(msg));
}
//Coordinates were mod wants to place the annotation
var xCorGlobal = null;
var yCorGlobal = null;
canvasScreenShot.addEventListener('click', (event) =>{
  if(GLOBAL_ANNOS[currentShot] != -1){
    alert("You can only set one annotation per shot.")
    return;
  }
  
  const rect = canvasScreenShot.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  var screenFieldWidth = canvasScreenShot.width / canvasGridSplitX;
  var screenFieldHeight = canvasScreenShot.height / canvasGridSplitY;
  var xCor = 0;
  var yCor = 0;
  for(var i = 0; i <= canvasScreenShot.width; i += screenFieldWidth){
    if(x > i && x < i + screenFieldWidth){
      for(var j = 0; j <= canvasScreenShot.height; j += screenFieldHeight){
        if(y > j && y < j + screenFieldHeight){
          xCorGlobal = xCor;
          yCorGlobal = yCor;
        }
        yCor++;
      }
    }
    xCor++;
  }
  
  $("#annoInputModal").modal('toggle');
  /* $("#annoInputModal").modal({focus: true}); */
  $("#annoModal").modal('hide');
})

function annoInputSave(){
  var title = document.querySelector("#annoTitelInput").value;
  var text = document.querySelector("#annoTextInput").value;
  
  msg = {
    "type": "annotation", 
    "cmd": "push", 
    "data": [
      {
        "id": -1, 
        "shot_id": currentShot, 
        "pos":[xCorGlobal,yCorGlobal], 
        "titel":title, 
        "text_type": 0, 
        "text": text
      }
    ]
  } 
  socket.send(JSON.stringify(msg));
  $("#annoInputModal").modal('hide');
}

//Function for textinput, sets max rows
function limitTextarea(textarea, maxLines, maxChar) {
  var lines = textarea.value.replace(/\r/g, '').split('\n'), lines_removed, char_removed, i;
  if (maxLines && lines.length > maxLines) {
      lines = lines.slice(0, maxLines);
      lines_removed = 1
  }
  if (maxChar) {
      i = lines.length;
      while (i-- > 0) if (lines[i].length > maxChar) {
          lines[i] = lines[i].slice(0, maxChar);
          char_removed = 1
      }
      if (char_removed || lines_removed) {
          textarea.value = lines.join('\n')
      }
  }
}



