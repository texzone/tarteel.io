var audio_context;
var recorder;
var audioStream;
let meter;

const isMobile = new MobileDetect(window.navigator.userAgent);

function drawLoop(time) {
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
    // webkit shim
    window.AudioContext = window.AudioContext || window.webkitAudioContext;
    navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
    window.URL = window.URL || window.webkitURL;
    if(!audio_context) audio_context = new AudioContext;
    console.log('Audio context set up.');
    console.log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
  } catch (e) {
    console.log('No web audio support in this browser!');
  }

  navigator.mediaDevices.getUserMedia({audio: true})
    .then(startUserMedia)
    .catch((e) => {
      if(e){
        if (isMobile.os()) {
          $(".mobile-app").show();
        } else {
          $(".mic-permissions-blocked").show();
        }
        if(continuous) {
          revertContinuous()
        }
      }
      console.log('No live audio input: ' + e.message);
    });
};

function revertContinuous() {
  state = StateEnum.AYAH_LOADED;
  $("#mic").removeClass("recording");
  $(".review #submit").css("margin-top", "35px")
  $(".note-button.next").show();
  $(".note-button.previous").show();
  $(".tg-list-item").show();
  $("#retry").show()
  $(".review").hide()
  $("#mic").html(`
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 34"><path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/></svg>
          `)
  $(".recording-note").hide()
}