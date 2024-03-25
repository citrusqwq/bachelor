//for MODERATOR and USER

const videoPlayer = document.querySelector( '.video-player')
const video = document.querySelector( '.video')
const playButton = document.querySelector( '.play-button')
const volume = videoPlayer.querySelector( '.volume')
const currentTimeElement = videoPlayer.querySelector('.current')
const durationTimeElement = videoPlayer.querySelector('.duration')
const progress = videoPlayer.querySelector('.video-progress')
const progressBar = videoPlayer.querySelector('.video-progress-filled')

const shotChanged = new Event('shotChanged', {
  bubbles:true
})
var currentShot = 0;
//Volume
volume.addEventListener('mousemove', (e) => {
  video.volume = e.target.value
})


//Current time and duration
const currentTime =  () => {
  let currentMinutes = Math.floor(video.currentTime / 60)
  let currentSeconds = Math.floor(video.currentTime - currentMinutes * 60)
  let durationMinutes = Math.floor(video.duration / 60)
  let durationSeconds = Math.floor(video.duration - durationMinutes * 60)

  currentTimeElement.innerHTML = `${currentMinutes}:${currentSeconds < 10 ? '0' + currentSeconds : currentSeconds}`
  durationTimeElement.innerHTML = `${durationMinutes}:${durationSeconds < 10 ? '0' + durationSeconds : durationSeconds}`
}

video.addEventListener('timeupdate', currentTime)

//Progressbar
video.addEventListener('timeupdate', () => {
  const percentage = (video.currentTime / video.duration) * 100
  progressBar.style.width = `${percentage}%`
  // checkIfAutoStop needs to be called before updateCurrentShot is called
  // if not autostop fails since the shots gets updated and autostop doesn't know we passed a shot
  // since checkIfAutoStop is a mod only function we need to check if the function is present
  if(typeof checkIfAutoStop === "function"){
    checkIfAutoStop()
  }
  updateCurrentShot();
})


function updateCurrentShot(){
  for(var i = 0; i < GLOBAL_SHOTS.length; i++){
      if(video.currentTime >= GLOBAL_SHOTS[i].frm && video.currentTime <= GLOBAL_SHOTS[i].to){
          if(i != currentShot){
              
              currentShot = i;
              console.log("new Shot = ", i);
              video.dispatchEvent(shotChanged);
          }
          
      }
  }
}

function videoOnMessage(recv){
    
    if(recv.cmd == "play"){
        video.currentTime  = recv.data[0].ts;
        videoPlay();
    }else if(recv.cmd == "pause"){
        video.currentTime  = recv.data[0].ts;
        video.pause();
        playButton.textContent = '▶️';
    }else if(recv.cmd == "skip"){
        video.currentTime = recv.data[0].ts;
    }
}

/**
 * Start video playback and notfiy user if MediaAutoplay is disabled.
 * https://stackoverflow.com/a/49939655
 */
function videoPlay(){
  var promise = video.play();
  promise.then(_ => {
    // video started!
    playButton.textContent = '⏸︎';
  }).catch(error => {
    // Autoplay not allowed!
    // Mute video and try to play again
    video.muted = true;
    video.play().then(_ => {
      //muted is ok
      volume.value = 0;
      playButton.textContent = '⏸︎';
      createErrorToastOverwrite(`Das Video wurde stumm gestartet da dein Browser den Sound blockiert.
      Bitte erlaube "Automatische Wiedergabe von Medien mit Sound"(Firefox)/"Ton"(Chrome) für diese Website.`);
    }).catch(error => {
      //even muted failed
      createErrorToastOverwrite(`Error: Das Video wurde vom Moderator gestartet aber dein Browser blockiert die automatische Wiedergabe von Medien. 
      Bitte erlaube "Automatische Wiedergabe von Medien mit Sound"(Firefox)/"Ton"(Chrome) für diese Website um das Video zu sehen.`);
    });
  });
}
