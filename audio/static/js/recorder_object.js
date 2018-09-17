var audio_context;
var recorder;
var audioStream;
let meter;

const isMobile = new MobileDetect(window.navigator.userAgent);

// Handles the animation of the mic button while recording based on the voice volume.
function drawLoop() {
  $("#mic").css("transform", `scale(${ 1 + Number(parseFloat(meter.volume).toFixed(2)) })`)
  rafID = window.requestAnimationFrame( drawLoop );
}


function stopRecording() {
  recorder.stop();
  meter.shutdown();
  audioStream.getTracks()[0].stop();
}
function startRecording(cb) {
  function startUserMedia(stream) {
    audioStream = stream;
    var input = audio_context.createMediaStreamSource(audioStream);
    meter = createAudioMeter(audio_context);
    input.connect(meter);
    drawLoop();
    if(cb) cb()
    recorder = new Recorder(input);
    recorder && recorder.record();
  }
  try {
    // webkit shim.
    window.AudioContext = window.AudioContext || window.webkitAudioContext;
    navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
    window.URL = window.URL || window.webkitURL;

    audio_context = new AudioContext;
    console.log('Audio context set up.');
    console.log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
  } catch (e) {
    console.log('No web audio support in this browser!');
  }

  try {
    navigator.mediaDevices.getUserMedia({audio: true})
      .then(startUserMedia)
      .catch((e) => {
        if(e){
          showRecordingPermissionsError()
          if(continuous) {
            // needed to stop the recording if an error occurred in continuous mode.
            revertContinuous()
          }
        }
      });
  }
  catch (e) {
    showRecordingPermissionsError()
  }
};

function showRecordingPermissionsError() {
  if (isMobile.os()) {
    $(".mobile-app").show();
  } else {
    $(".mic-permissions-blocked").show();
  }
}

function revertContinuous() {
  state = StateEnum.AYAH_LOADED;
  $("#mic").removeClass("recording");
  $(".review #submit").css("margin-top", "35px")
  $(".note-button.next").show();
  $(".note-button.previous").show();
  $(".tg-list-item").show();
  $("#retry").show()
  $(".review").hide()
  $(".recording-note").hide()
}