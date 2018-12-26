let evaluation_result = false;      // Bool of whether evaluator chose yes or no

/**
 * Gathers all the info needed to update a TajweedEvaluation model and posts
 * data to backend.
 */
function handleSubmit() {
    console.log("Posting updates");
    let platform = navigator.platform;
    let degree = $("input[type='radio']:checked").val();
    let category = $(".rule-text").attr('id');
    let recording_id = $("#ayah-text").attr("data-recording-id");
    let session_id = $(".user-form").attr('id');
    const body = {
        associated_recording: recording_id,
        session_id: session_id,
        degree: degree,
        category: category,
        platform: platform,
        result: evaluation_result
    };
    fetch("/evaluation/submit_tajweed/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body),
    })
        .then((res) => {
            console.log(res)
        })
}

/**
 * Toggles the user form display and adjusts button classes.
 * Sets whether the recitation was correct or incorrect.
 */
function handleWrongAyah() {
    console.log("Wrong ayah received");
    evaluation_result = true;
    $(".vote-button.yes").removeClass("active");
    $(".user-form").toggle();
    $(".vote-button.no").toggleClass("active");
}

/**
 * If the recitation was correct, submit and reload the page to get a new ayah.
 */
function handleRightAyah() {
    console.log("Right ayah received");
    evaluation_result = false;
    $(".vote-button.no").removeClass("active");
    $(".user-form").hide();
    $(".vote-button.yes").toggleClass("active");
    handleSubmit();
    window.location.reload();
}

/**
 * jQuery Functions
 */
$(document).ready(function () {

    /**
     * Starts the play button animation
     * @param audioTag
     */
    function startAnimating(audioTag) {
        const audio_context = new AudioContext();
        const input = audio_context.createMediaElementSource(audioTag.cloneNode(true));
        meter = createAudioMeter(audio_context);
        input.connect(meter);
    }

    /**
     * Creates the background siri-like wave animation div.
     */
    function startWave() {
        return new SiriWave({
            container: document.getElementById('siri-container'),
            width: 640,
            height: 200,
            style: "ios9",
        });
    }

    window.AudioContext = window.AudioContext || window.webkitAudioContext;

    /**
     * Updates the play button icon and waves based on user click.
     */
    $(".primary-button").on("click", () => {
        const audioTag = document.querySelector(".audio");
        const siriContainer = $("#siri-container");
        const primaryButton = $(".primary-button");
        const playIcon = "<svg viewBox=\"0 0 13 15\"><g stroke=\"none\" stroke-width=\"1\" fill=\"none\" fill-rule=\"evenodd\"><g id=\"icon-/-play\" fill=\"#5fc49e\"><path d=\"M0.978009259,0 C1.03819475,0 1.09587164,0.00733847847 1.15104167,0.0220156556 C1.2062117,0.0366928327 1.2613809,0.0538159491 1.31655093,0.0733855186 C1.37172095,0.0929550881 1.42438247,0.117416683 1.47453704,0.146771037 L12.5486111,6.7074364 C12.6388893,6.75636032 12.7191355,6.82240663 12.7893519,6.9055773 C12.8595683,6.98874797 12.9122298,7.08170203 12.947338,7.18444227 C12.9824462,7.28718251 13,7.39236737 13,7.5 C13,7.85225225 12.8495385,8.11643748 12.5486111,8.2925636 L1.45949074,14.853229 C1.38927434,14.9021529 1.31153592,14.9388453 1.22627315,14.9633072 C1.14101038,14.9877692 1.05324119,15 0.962962963,15 C0.882715648,15 0.802469537,14.9902154 0.722222222,14.9706458 C0.641974907,14.9510762 0.566744178,14.9217223 0.496527778,14.8825832 C0.165507604,14.6966723 0,14.4227024 0,14.0606654 L0.0150462963,0.939334638 C0.0150462963,0.577297603 0.1805539,0.30332774 0.511574074,0.11741683 C0.652006875,0.0391385519 0.807483715,0 0.978009259,0 Z\" id=\"play-button\"></path></g></g></svg>";
        const stopIcon = "<svg width=\"28\" height=\"28\" viewBox=\"0 0 28 28\"><defs><path id=\"stop-path2\" d=\"M19.833 0H3.5C1.517 0 0 1.517 0 3.5v16.333c0 1.984 1.517 3.5 3.5 3.5h16.333c1.984 0 3.5-1.516 3.5-3.5V3.5c0-1.983-1.516-3.5-3.5-3.5zM21 19.833c0 .7-.467 1.167-1.167 1.167H3.5c-.7 0-1.167-.467-1.167-1.167V3.5c0-.7.467-1.167 1.167-1.167h16.333c.7 0 1.167.467 1.167 1.167v16.333z\"></path></defs><g fill=\"none\" fill-rule=\"evenodd\" transform=\"translate(2.333 2.333)\"><mask id=\"stop-mask2\" fill=\"#fff\"><use xlink:href=\"#stop-path2\"></use></mask><g fill=\"#FF4F5E\" mask=\"url(#stop-mask2)\"><path d=\"M-2.333-2.333h28v28h-28z\"></path></g></g></svg>";

        const siriWave = startWave();
        $(audioTag).on("ended", () => {
            primaryButton.removeClass("pause");
            primaryButton.addClass("play");
            primaryButton.find("button").html(playIcon);
            siriWave.stop();
            siriContainer.find("canvas").remove()
        });
        if (audioTag.paused) {
            audioTag.play();
            primaryButton.removeClass("play");
            primaryButton.addClass("pause");
            primaryButton.find("button").html(stopIcon);
            siriContainer.show();
            siriWave.start();
            startAnimating(audioTag)
        } else {  // Playing...
            audioTag.pause();
            primaryButton.removeClass("pause");
            primaryButton.addClass("play");
            primaryButton.find("button").html(playIcon);
            siriWave.stop();
            siriContainer.find("canvas").remove()
        }
    })


});
