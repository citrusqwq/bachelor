//for MODERATOR and USER

var canvasAnno = document.querySelector('.canvasAnno');
var ctxAnno = canvasAnno.getContext('2d');
//Must be initialized with shots_length
//index is the shot_id not the annotation id
var GLOBAL_ANNOS = [];
//Copy made to save annotations when annotation display is disabled
//Must be set on recieve
var GLOBAL_ANNOS_COPY = [];

/**
 * On update or new messge from backend
 * @param {json} recv Message from backend
 * @return NONE
 */
 function annosOnMessage(recv){

  //populate empty GLOBAL_ANNOS/GLOBAL_ANNOS_COPY
  //or both arrays are unequal -> overwrite GLOBAL_ANNOS since we get an update with all anons
  //after shots was changed
  if (GLOBAL_ANNOS.length != GLOBAL_SHOTS.length){
    GLOBAL_ANNOS = new Array(GLOBAL_SHOTS.length);
    GLOBAL_ANNOS.fill(-1, 0, GLOBAL_ANNOS.length);
    GLOBAL_ANNOS_COPY = GLOBAL_ANNOS;
  }    

    //calculate Grid for Annotation
    calculateGrid()
    
    //populate GLOBAL_ANNOS with given data
    for(var i = 0; i < recv.data.length; ++i){
        let annotation = new Annotation(recv.data[i].id, recv.data[i].titel, recv.data[i].pos[0], recv.data[i].pos[1], fieldWidth, fieldHeight, recv.data[i].text);
        GLOBAL_ANNOS[recv.data[i].shot_id] = annotation;
    }

    //display Annotation for current shot if there is one
    if(GLOBAL_ANNOS[currentShot] != -1){
        GLOBAL_ANNOS[currentShot].display(ctxAnno);
    }
}

function annosOnDeleteMessage(recv){
    //overwrite anno we got saved in GLOBAL_ANNOS
    GLOBAL_ANNOS[recv.data.shot_id] = -1;
    //clear canvas if the current shot is the shot_id from the deleted anno
    if (currentShot == recv.data.shot_id){
        ctxAnno.clearRect(0, 0, canvasAnno.width, canvasAnno.height);
    }
}

/* var dataAnno = []; */
//Size of field in Grid
var fieldWidth = 0;
var fieldHeight = 0;
//Amount of grids per row and column
var canvasGridSplitX = 6;
var canvasGridSplitY = 20;

class Annotation{
  constructor(id, title, xCord, yCord, width, height, text){
    this.id = id;
    this.title = title;
    this.xCord = xCord;
    this.yCord = yCord;
    this.width = width;
    this.height = height;
    this.text = text;
    this.open = false;
    var fontHeight = this.height - 5;
    this.font = fontHeight.toString() + "px Helvetica Neue";
    console.log(this.font)
  }
  //displays annotation on canvas
  display(ctx){
    //updating widht and height in case Window was resized
    this.updateValues();
    //display rect on canvas
    ctx.fillStyle = "white";
    console.log("displaying rect ", fieldWidth, fieldHeight, this.xCord, this.yCord);
    ctx.fillRect(fieldWidth * this.xCord, fieldHeight * this.yCord, this.width, this.height);
    //Set text displayed in rect
    ctx.font = this.font;
    ctx.textAlign="left";
    ctx.textBaseline = "top";
    ctx.fillStyle = "black";
    
    ctx.fillText(this.title, fieldWidth * this.xCord, fieldHeight * this.yCord);
    ctx.stroke()
  }
  
  //function called when anno was clicked, opens text field
  openAnno(ctx){
    ctx.font = this.font;
    ctx.textAlign="left";
    ctx.textBaseline = "top";
    ctx.fillStyle = "white";
    var lines = this.text.split('\n');
    //must be same height like font pixel
    var lineheight = 16;
    var lineWidth = this.getLongestLine(lines);
    if((fieldWidth * this.xCord) + lineWidth < canvasAnno.width){
      if(this.yCord + lines.length <= canvasGridSplitY){
        console.log("Doesnt hit anything")
        ctx.fillRect(fieldWidth * this.xCord, fieldHeight * (this.yCord + 1), lineWidth, 20 * lines.length);
        ctx.fillStyle = "black";
        for(var i = 0; i < lines.length; i++){
          ctx.fillText(lines[i], fieldWidth * this.xCord, fieldHeight * (this.yCord + 1) + (lineheight * i));
        }   
      }else{
        console.log("hits bottom");
        ctx.fillRect(fieldWidth * this.xCord, (fieldHeight * this.yCord) - (lines.length * 20), lineWidth, lines.length * 20);
        ctx.fillStyle = "black";
        for(var i = 0; i < lines.length; i++){
          ctx.fillText(lines[i], fieldWidth * this.xCord, (fieldHeight * this.yCord) - (lines.length * 20) + (i * 20));
        }
      }
    }else{
      if(this.yCord + lines.length <= canvasGridSplitY){
        console.log("hits right");
        ctx.fillRect(fieldWidth * (this.xCord) + (fieldWidth - lineWidth), fieldHeight * (this.yCord + 1), lineWidth, this.height * 2);
        ctx.fillStyle = "black";
        for(var i = 0; i < lines.length; i++){
          ctx.fillText(lines[i], (fieldWidth * this.xCord) + (fieldWidth - lineWidth), fieldHeight * (this.yCord + 1) + (lineheight * i));
        }
        
      }else{
        console.log("hits right and bottom");
        ctx.fillRect(fieldWidth * (this.xCord) + (fieldWidth - lineWidth),(fieldHeight * this.yCord) - (lines.length * 20), lineWidth, lines.length * 20);
        ctx.fillStyle = "black";

        for(var i = 0; i < lines.length; i++){
          ctx.fillText(lines[i], (fieldWidth * this.xCord) + (fieldWidth - lineWidth), (fieldHeight * this.yCord) - (lines.length * 20) + (i * 20));
        }
      }
    }

    this.width = this.width * 2;
    this.height = this.height * 2;
    this.open = true;
    
  }

  //returns longest line in linearray
  getLongestLine(lines){
    var result = 0;
    for(var i = 0; i < lines.length; i++){
      console.log("line length: ", ctxAnno.measureText(lines[i]));
      if(ctxAnno.measureText(lines[i]).width > result){
        result = ctxAnno.measureText(lines[i]).width;
      }
    }
    return result;
  }
  //closes annoation
  closeAnno(ctx){
    
    ctx.fillStyle = "white";
    this.width = this.width / 2;
    this.height = this.height / 2;
    ctx.clearRect(0, 0, canvasAnno.width, canvasAnno.height);
    ctx.fillRect(fieldWidth * this.xCord, fieldHeight * this.yCord, this.width, this.height);
    ctx.font = this.font;
    ctx.textAlign="left";
    ctx.textBaseline = "top";
    ctx.fillStyle = "black";
    
    ctx.fillText(this.title, fieldWidth * this.xCord, fieldHeight * this.yCord);
    this.open = false;
  }
  //this function handles a click on the canvas and checks if it was on this annotation
  clickAnno(xmouse, ymouse, ctx){
    if(xmouse < (fieldWidth * this.xCord) + this.width && xmouse > fieldWidth * this.xCord){
      if(ymouse < (fieldHeight * this.yCord) + this.height && ymouse > fieldHeight * this.yCord){
        if(this.open == false){
          this.openAnno(ctx);
        }else{
          this.closeAnno(ctx);
        }
        return true;
      }
    }
    return false;
  }

  updateValues(){
    fieldWidth = canvasAnno.width / canvasGridSplitX;
    fieldHeight = canvasAnno.height / canvasGridSplitY;
    this.width = fieldWidth;
    this.height = fieldHeight;
    var fontHeight = this.height - 5;
    this.font = fontHeight.toString() + "px Helvetica Neue";
  }
}


video.addEventListener('shotChanged', function(){
  console.log("Shot changed");
  ctxAnno.clearRect(0, 0, canvasAnno.width, canvasAnno.height);
  if(GLOBAL_ANNOS[currentShot] != -1){
    GLOBAL_ANNOS[currentShot].display(ctxAnno);
  }
});

//Event listner for clicking on annotation
canvasAnno.addEventListener('click', (event) =>{
  const rect = canvasAnno.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  if(GLOBAL_ANNOS[currentShot] != -1){
    console.log(GLOBAL_ANNOS[currentShot].clickAnno(x, y, ctxAnno));
  }
  
})


function calculateGrid(){
  fieldWidth = canvasAnno.width / canvasGridSplitX;
  fieldHeight = canvasAnno.height / canvasGridSplitY;
}

function drawGrid(){
  for(var x = 0; x <= canvasAnno.width; x += fieldWidth){
    ctxAnno.moveTo(x, 0);
    ctxAnno.lineTo(x, canvasAnno.height);
  }
  for(var y = 0; y <= canvasAnno.height; y += fieldHeight){
    ctxAnno.moveTo(0, y);
    ctxAnno.lineTo(canvasAnno.width, y);
  }
  ctxAnno.strokeStyle = "black";
  ctxAnno.stroke();
}


var annoSwitch = document.getElementById("flexSwitchAnnotationen");
var btnAddAnno = document.getElementById("btnAddAnno");
var btnAnnoDelete = document.getElementById("btnAnnoDelete");
annoSwitch.addEventListener('input', checkAnnoSwitch);
//functions called when annotation switch is clicked
function checkAnnoSwitch(){
  console.log("test")
  if(annoSwitch.checked){
    GLOBAL_ANNOS = GLOBAL_ANNOS_COPY;
    console.log("Current annos: ", GLOBAL_ANNOS);
    if(GLOBAL_ANNOS[currentShot] != -1){
      GLOBAL_ANNOS[currentShot].display(ctxAnno);
    }
    if (btnAddAnno != null){ btnAddAnno.disabled = false; }
    if (btnAnnoDelete != null){ btnAnnoDelete.disabled = false; }
  }else{
    GLOBAL_ANNOS_COPY = GLOBAL_ANNOS;
    GLOBAL_ANNOS = new Array(GLOBAL_SHOTS.length);
    GLOBAL_ANNOS.fill(-1, 0, GLOBAL_ANNOS.length - 1);
    ctxAnno.clearRect(0, 0, canvasAnno.width, canvasAnno.height);
    if (btnAddAnno != null){ btnAddAnno.disabled = true; }
    if (btnAnnoDelete != null){ btnAnnoDelete.disabled = true; }
  }
}
//Event called to adapt canvas to window after this is resized
var resizeId;
$(window).resize(function() {
    clearTimeout(resizeId);
    resizeId = setTimeout(resizedEnded, 500);
});

function resizedEnded(){
  console.log("finished resizing")
  canvasAnno.width = canvasAnno.parentElement.clientWidth;
  canvasAnno.height = canvasAnno.parentElement.clientHeight;
  calculateGrid();
  //make sure the GLOBAL_ANNOS array has the correct length to access index currentShot
  //this can happen if we call this function in the init function
  //in init we dont need to display any anno we just need to fix the dimensions of the canvas
  if(GLOBAL_ANNOS.length > currentShot && GLOBAL_ANNOS[currentShot] != -1){
    GLOBAL_ANNOS[currentShot].display(ctxAnno);
  }
  console.log("Global Annos: ", GLOBAL_ANNOS)
}