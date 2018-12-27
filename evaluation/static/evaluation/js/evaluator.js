let played = false
let currentStep = 1

function submitAyah(evaluation) {
  const ayah = {
    "recording_id": $("#ayah-text").attr("data-recording-id"),
    "evaluation": evaluation,
  }
  fetch("/api/evaluator/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ayah})
  })
    .then((res => {
      if (res.status === 201) {
        console.log("Successfully Submitted!");
      }
    }))
    .catch((e) => {
      console.log(e.message);
    })
}

async function handleAyahChange(vote) {
  if (currentStep < 5) {
    played = false
    disableVoteButtons()
    const activePill = $(".pill.active")
    const speakerIcon = "<svg width=\"24\" height=\"24\" viewBox=\"0 0 24 24\"><defs><path id=\"volume-path\" d=\"M10.388.108c-.3-.198-.799-.099-1.099.1L4.595 3.982H.999c-.6 0-.999.397-.999.993v5.96c0 .595.4.993.999.993h3.596l4.694 3.774c.2.1.4.199.6.199.1 0 .3 0 .4-.1.299-.198.599-.496.599-.894V1.002c.1-.397-.1-.695-.5-.894zM8.99 12.822L5.594 10.14c-.2-.1-.4-.199-.6-.199H1.998V5.968h2.996c.2 0 .4-.099.6-.198L8.99 3.088v9.734zm6.193-9.039c2.297 2.285 2.297 6.059 0 8.443-.2.198-.5.298-.7.298-.2 0-.499-.1-.699-.298a.956.956 0 0 1 0-1.39c1.599-1.59 1.599-4.073 0-5.662a.956.956 0 0 1 0-1.39c.4-.398 1.1-.398 1.399 0zm3.596 11.919c-.2.199-.5.298-.7.298-.2 0-.499-.1-.699-.298a.956.956 0 0 1 0-1.39c3.496-3.477 3.496-9.138 0-12.615a.956.956 0 0 1 0-1.39.97.97 0 0 1 1.399 0c4.295 4.172 4.295 11.124 0 15.395z\"></path></defs><g fill=\"none\" fill-rule=\"evenodd\" transform=\"translate(0 4)\"><mask id=\"volume-mask\" fill=\"#fff\"><use xlink:href=\"#volume-path\"></use></mask><g fill=\"#4A4A4A\" mask=\"url(#volume-mask)\"><path d=\"M-1-4h24v24H-1z\"></path></g></g></svg>"
    activePill.find(".contents").html("")
    activePill.removeClass("active").addClass(vote)
    const newActivePill = activePill.next()
    newActivePill.addClass("active")
    newActivePill.find(".contents").append(speakerIcon)
    const ayah = await getNewAyah()
    const ayahText =  $("#ayah-text");
    ayahText.find("p").text(ayah.ayah_text)
    ayahText.find("span").text(`(${ ayah.surah_num }:${ ayah.ayah_num })`)
    ayahText.attr("data-recording-id", ayah.recording_id)
    const audioTag = $(".audio")
    audioTag.find("source").attr("src", ayah.audio_url)
    audioTag[0].pause();
    audioTag[0].load();
    $(audioTag).trigger("ended")
    currentStep = currentStep + 1;
  } else {
    getEvaluationsCount()
      .then((count) => {
        $("#modal").modal({
          escapeClose: false,
          clickClose: false,
          showClose: false
        });
        $("#modal .count").text(count)
      });
  }
}

async function getEvaluationsCount() {
  const res = await fetch("/api/get_evaluations_count/").then(res => res.json());
  return res.count
}

function handleWrongAyah() {
  handleAyahChange("wrong")
  submitAyah("incorrect")
}

function handleRightAyah() {
  handleAyahChange("right")
  submitAyah("correct")

}

function handleSkip() {
  handleAyahChange("skipped")
}

/**
 * Creates a POST request to get a random new ayah. Returns as a JSON.
 * Notice that a CORS error will occur when testing locally if 127.0.0.1 is not mapped to localhost.
 * Otherwise, just change 127.0.0.1 (and port if different) to the server you are using.
 */
function getNewAyah() {
  return fetch("/api/evaluator/json?format=json")
    .then(res => res.json())
    .then(json => json)
}

$(document).ready(() => {

  function startAnimating(audioTag) {
    const audio_context = new AudioContext();
    const input = audio_context.createMediaElementSource(audioTag.cloneNode(true));
    meter = createAudioMeter(audio_context);
    input.connect(meter);
  }

  function startWave() {
    const siriWave = new SiriWave({
      container: document.getElementById('siri-container'),
      width: 640,
      height: 200,
      style: "ios9",
    });
    return siriWave
  }

  function unDisableVoteButtons() {
    $(".vote-button").attr("disabled", false)
    $(".instruction").css("opacity", 0)
  }

  disableVoteButtons = () => {
    $(".vote-button").attr("disabled", true)
    $(".instruction").css("opacity", 1)
  }

  window.AudioContext = window.AudioContext || window.webkitAudioContext;

  $(".primary-button").on("click", () => {
    const audioTag = document.querySelector(".audio")
    const siriContainer = $("#siri-container")
    const primaryButton = $(".primary-button")
    const playIcon = "<svg viewBox=\"0 0 13 15\"><g stroke=\"none\" stroke-width=\"1\" fill=\"none\" fill-rule=\"evenodd\"><g id=\"icon-/-play\" fill=\"#5fc49e\"><path d=\"M0.978009259,0 C1.03819475,0 1.09587164,0.00733847847 1.15104167,0.0220156556 C1.2062117,0.0366928327 1.2613809,0.0538159491 1.31655093,0.0733855186 C1.37172095,0.0929550881 1.42438247,0.117416683 1.47453704,0.146771037 L12.5486111,6.7074364 C12.6388893,6.75636032 12.7191355,6.82240663 12.7893519,6.9055773 C12.8595683,6.98874797 12.9122298,7.08170203 12.947338,7.18444227 C12.9824462,7.28718251 13,7.39236737 13,7.5 C13,7.85225225 12.8495385,8.11643748 12.5486111,8.2925636 L1.45949074,14.853229 C1.38927434,14.9021529 1.31153592,14.9388453 1.22627315,14.9633072 C1.14101038,14.9877692 1.05324119,15 0.962962963,15 C0.882715648,15 0.802469537,14.9902154 0.722222222,14.9706458 C0.641974907,14.9510762 0.566744178,14.9217223 0.496527778,14.8825832 C0.165507604,14.6966723 0,14.4227024 0,14.0606654 L0.0150462963,0.939334638 C0.0150462963,0.577297603 0.1805539,0.30332774 0.511574074,0.11741683 C0.652006875,0.0391385519 0.807483715,0 0.978009259,0 Z\" id=\"play-button\"></path></g></g></svg>"
    const stopIcon = "<svg width=\"28\" height=\"28\" viewBox=\"0 0 28 28\"><defs><path id=\"stop-path2\" d=\"M19.833 0H3.5C1.517 0 0 1.517 0 3.5v16.333c0 1.984 1.517 3.5 3.5 3.5h16.333c1.984 0 3.5-1.516 3.5-3.5V3.5c0-1.983-1.516-3.5-3.5-3.5zM21 19.833c0 .7-.467 1.167-1.167 1.167H3.5c-.7 0-1.167-.467-1.167-1.167V3.5c0-.7.467-1.167 1.167-1.167h16.333c.7 0 1.167.467 1.167 1.167v16.333z\"></path></defs><g fill=\"none\" fill-rule=\"evenodd\" transform=\"translate(2.333 2.333)\"><mask id=\"stop-mask2\" fill=\"#fff\"><use xlink:href=\"#stop-path2\"></use></mask><g fill=\"#FF4F5E\" mask=\"url(#stop-mask2)\"><path d=\"M-2.333-2.333h28v28h-28z\"></path></g></g></svg>"

    const siriWave = startWave()
    $(audioTag).on("ended", () => {
      primaryButton.removeClass("pause")
      primaryButton.addClass("play")
      primaryButton.find("button").html(playIcon)
      siriWave.stop()
      siriContainer.find("canvas").remove()
    })
    if (audioTag.paused) { // Before Playing
      played = true
      unDisableVoteButtons()
      audioTag.play()
      primaryButton.removeClass("play")
      primaryButton.addClass("pause")
      primaryButton.find("button").html(stopIcon)
      siriContainer.show()
      siriWave.start()
      startAnimating(audioTag)
    } else {  // While Playing...
      audioTag.pause()
      primaryButton.removeClass("pause")
      primaryButton.addClass("play")
      primaryButton.find("button").html(playIcon)
      siriWave.stop()
      siriContainer.find("canvas").remove()
    }
  })
});