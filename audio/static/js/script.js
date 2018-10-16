var StateEnum = {
    INTRO: 1,
    AYAH_LOADED: 2,
    RECORDING: 3,
    COMMIT_DECISION: 4,
    THANK_YOU: 5
};

const AYAHS_PER_SUBISSION = 5;
var state = StateEnum.INTRO;
var session_id = null;
var session_count = 0;
var ayah_data;
var recording_data = new Array(AYAHS_PER_SUBISSION);
let passedOnBoarding;
let currentSurah;
let demographicData;
let ayahsRecited;
let continuous = false;
let preloadedAyahs = {};

try {
  // Retrieving data stored in the localStorage.
  passedOnBoarding = Boolean(localStorage.getItem("passedOnBoarding"));
  ayah_data = JSON.parse(localStorage.getItem("lastAyah"));
  ayahsRecited = Number(localStorage.getItem("ayahsRecited"));
  continuous = Boolean(localStorage.getItem("continuous"))
  demographicData = JSON.parse(localStorage.getItem("demographicData"))
  // making the continuous mode appears like checked were checked the last time the user visited the app.
  $('#continuous').prop('checked', continuous);

  // this code is hiding the steps and showing thw navbar if the user passed the onboarding stage.
  if(passedOnBoarding) {
    $("#progress").hide();
    $(".navbar").css("display", "flex");
    $(".tg-list-item span").css("display", "none");
  }
} catch (e) {
    console.log(e.message);
}

/*
 - this instance handles the swipe navigation in the website
 ,the index of each screen as it's ordered in index.html
 , .screen1 it's index is 0
*/
window.mySwipe = new Swipe(document.getElementById('slider'), {
    disableScroll: true,
    startSlide: ayah_data ? 1 : 0
});

// truncates given string used in the ayah picker.
String.prototype.trunc =
    function (n) {
        return this.substr(0, n - 1) + (this.length > n ? '&hellip;' : '');
    };

function load_ayah_callback(data) {
  state = StateEnum.AYAH_LOADED;
  ayah_data = data;
  $("#mic").removeClass("recording");
  $("#ayah-text").html(`<p class=ayah-quran-text>${data.line}◌</p>`)
  setLastAyah(data)
  $("#surah-num").text(data.surah);
  $("#ayah-num").text(data.ayah);
  $(".note-button.previous").show();
  $(".note-button.next").show();
  $(".tg-list-item").show();
  session_id = data.hash;
  for (let i=0; i < session_count % AYAHS_PER_SUBISSION + 2; i++) {
    $(".progress-bubble:nth-of-type("+i+")").addClass("complete");
  }
  loadNextAyah(); // preload the next ayah.
  loadPreviousAyah() // preload the previous ayah.
}

// Ayah here is the last Ayah which retrieved from localstorage.
if(ayah_data)
  load_ayah_callback(ayah_data);


function targetHasId(target, id) {
    if ($(target).parents("#" + id).length || $(target).attr('id') == id) {
        return true
    }
    return false
}

// an event handler for every footer button (the lower part of the screen).
$("footer .btn").click(function(evt) {
  if (state == StateEnum.INTRO || state == StateEnum.THANK_YOU) {
    // this code get executed after passing welcome page or after subscribing.
    recording_data = new Array(AYAHS_PER_SUBISSION);
      $(".note-button.previous").show();
      $(".note-button.next").show();
      $(".tg-list-item").show();
      window.mySwipe.slide(1)
      $(".complete").removeClass("complete");
      $("#ayah").show();
      $("#mic").show();
      if(!ayah_data)
        getRandomAyah()
  } else if (targetHasId(evt.target, "submit")) {
    // this code get executed oon clicking next button in both recording modes.
    if(continuous) {
      if (recorder) {
        // exports the recorded file as blob.
        recorder.exportWAV(function(blob) {
          recording_data[session_count % AYAHS_PER_SUBISSION] = {
            surah_num: ayah_data.surah,
            ayah_num: ayah_data.ayah,
            hash_string: session_id,
            audio: blob
          }
          stopRecording()
          const record = recording_data[session_count % AYAHS_PER_SUBISSION];
          if (record) {
            api.send_recording(record.audio, record.surah_num, record.ayah_num, record.hash_string, continuous);
            session_count += 1;
            try {
              localStorage.setItem("ayahsRecited", String(ayahsRecited + session_count))
            } catch (e) {
              console.log(e.message)
            }
          }
          renderCounter(1)
          $(".review").hide();
          $(".note-button.previous-ayah").hide()
          $("#mic").show()
          setNextAyah()
        })
      }
    } else {
      const record = recording_data[session_count % AYAHS_PER_SUBISSION];
      if (record) {
        api.send_recording(record.audio, record.surah_num, record.ayah_num, record.hash_string, continuous);
        session_count += 1;
        try {
          localStorage.setItem("ayahsRecited", String(ayahsRecited + session_count))
        } catch (e) {
          console.log(e.message)
        }
      }
      renderCounter(1);
      if (session_count % AYAHS_PER_SUBISSION == 0 && !passedOnBoarding) {
        // Runs after submitting 5 recordings in the onborading stage.
        state = StateEnum.THANK_YOU;
        window.mySwipe.next();
        $("#ayah").hide();
        $("#thank-you").show();
        $(".tg-list-item span").css("display", "none");
        try {
          localStorage.setItem("passedOnBoarding", String(true))
          passedOnBoarding = true
        }
        catch (e) {
          console.log(e.message)
        }
        $(".review").hide()
      } else {
        $(".review").hide();
        $(".note-button.previous-ayah").hide();
        $("#mic").show();
        setNextAyah()
      }
    }

  } else if (state == StateEnum.AYAH_LOADED ||
      (state == StateEnum.COMMIT_DECISION && targetHasId(evt.target, "retry"))) {
    // runs when retry or record button get clicked.
    if(!continuous) {
      startRecording(() => {
        state = StateEnum.RECORDING;
        $(".review").hide();
        $("#mic").show();
        $("#mic").addClass("recording");
        $("#mic").css("margin-bottom", "60px")
        $(".tg-list-item").hide();
        $(".note-button.next").hide();
        $(".note-button.previous").hide();
        $(".note-button.previous-ayah").hide();
      })
    } else if (continuous) {
      startRecording()
      state = StateEnum.RECORDING;
      $(".review").hide();
      $("#mic").show();
      $("#mic").addClass("recording");
      $(".review").css("display", "flex");
      $("#retry").hide();
      $(".recording-note").show()
      $(".review #submit").css("margin-top", "10px")
      $(".tg-list-item").hide();
      $(".note-button.next").hide();
      $(".note-button.previous").hide();
      $(".note-button.previous-ayah").hide();
    }
  } else if (state == StateEnum.RECORDING) {
    handleStopButton()
  }
});

$('.dropdown .select').click(function (e) {
    const activeList = $(".dropdown.active");
    if (!$(this).parent().hasClass("active")) {
        activeList.find('.dropdown-menu').slideUp(300);
        activeList.removeClass('active');
    }
    $(this).parent().attr('tabindex', 1).focus();
    $(this).parent().toggleClass('active');
    $(this).parent().find('.dropdown-menu').slideToggle(300);
});
$('.dropdown .dropdown-menu ul li').click(handleHeritageListItemClick);
$(".dropdown").click((e) => {
    e.stopPropagation();
});

$(document).click(function () {
    const activeList = $(".dropdown.active");
    activeList.find('.dropdown-menu').slideToggle(300);
    activeList.removeClass('active');
});

function handleHeritageListItemClick() {
    const parent = $(this).parents('.dropdown');
    parent.find('span').text($(this).text());
    parent.find('input[type="hidden"]').attr('value', $(this).attr('id'));
    parent.removeClass('active');
    parent.find('.dropdown-menu').slideUp(300);
}

// renders Surahs in Surah picker.
const renderSurahs = (surahs) => {
    const surahsList = $(".screen5 .content ul");
    surahsList.html("");
    for (let surahKey in surahs) {
        surah = surahs[surahKey];
        surahsList.append(`
    <li onclick="getSurah(${surahKey})" data-key="${surahKey}" class=${ ayah_data.surah === surahKey ? "active" : "" }>
      <p class="number">${ surahKey }</p>
      <div class="text">
        <p>
          ${ surah.latin } (${surah.english})
        </p>
        <p  class="arabic" data-number=${surahKey}/>
      </div>
    </li>
  `);
    }
    const activeOne = document.querySelector(".screen5 .content ul li.active");
    surahsList.scrollTop(Number(activeOne.getAttribute("data-key")) * 75 - (3 * 75));
}

// just to prevent the default behaviour of every form in the website.
$(".screen5 .content form").submit((e) => e.preventDefault());
$(".screen6 .content form").submit((e) => e.preventDefault());
$("#demographics-form").submit((e) => e.preventDefault());


$(".screen5 .content form .input-wrapper input").keyup(e => {
    const value = e.target.value;
    if (!value)
        renderSurahs(surahs);
    const output = {};
    const out = Object.keys(surahs).filter((elm) => {
        return (
            surahs[elm].arabic.includes(value.toLowerCase().trim()) ||
            surahs[elm].english.toLocaleLowerCase().includes(value.toLowerCase().trim()) ||
            surahs[elm].latin.toLocaleLowerCase().includes(value.toLowerCase().trim())
        );
    }).forEach(elm => output[elm] = surahs[elm]);

    renderSurahs(output)
});

$(".screen6 .content form .input-wrapper input").keyup(e => {
    const value = e.target.value;
    currentSurah = currentSurah || ayah_data.surah;
    const ayahs = ayahsDict[currentSurah];
    if (!value)
        renderAyahs(currentSurah, ayahs);
    const output = {};
    const out = Object.keys(ayahs).filter((elm) => {
        return (
            ayahs[elm].text.includes(value.toLowerCase().trim())
        )
    }).forEach(elm => output[elm] = ayahs[elm])

    renderAyahs(currentSurah, output)
});

$(".dropdown-menu .search input[type='text']").keyup(handleHeritageSearch)

const renderAyahs = (surahKey, ayahs) => {
    const $ayahsList = $(".screen6 .content ul");
    $ayahsList.html("");
    for (let ayahKey in ayahs) {
        $ayahsList.append(`
    <li onclick="setAyah(${surahKey}, ${ayahKey})" data-key="${ayahKey}" class=${ ayah_data.ayah === ayahKey && surahKey === ayah_data.surah ? "active" : "" }>
      <p class="number">
        ${ ayahKey }
      </p>
      <p class="text">
        ${ ayahs[ayahKey].displayText.trunc(isMobile.os() ? 60 : 95) }
      </p>
    </li>
  `)
    }
    const activeOne = document.querySelector(".screen6 .content ul li.active")
    if (activeOne) {
        $ayahsList.scrollTop(Number(activeOne.getAttribute("data-key")) * 78 - (3 * 78))
    } else {
        $ayahsList.scrollTop(0)
    }
};

const getSurah = (surahKey) => {
    renderAyahs(surahKey, ayahsDict[surahKey]);
    currentSurah = surahKey;
    $(".screen6 .content .title h3").text(surahs[surahKey].arabic);
    window.mySwipe.slide(5);
};

function setLastAyah(ayah) {
    try {
        localStorage.setItem("lastAyah", JSON.stringify(ayah))
    } catch (e) {
        console.log(e.message)
    }
}

const setAyah = (surahKey, ayah) => {
    if (state == StateEnum.RECORDING) {
        handleStopButton(true)
        $(".note-button.previous-ayah").hide();
    }
    api.get_specific_ayah(surahKey, ayah, load_ayah_callback);
    window.mySwipe.slide(1);
    if (passedOnBoarding) {
        $("#progress").hide();
        $(".navbar").css("display", "flex");
    }
    $("#ayah").show();
    $("#mic").show();
    $(".review").hide();
}

const setPreviousAyah = () => {
    if (preloadedAyahs.prevAyah) {
        load_ayah_callback(preloadedAyahs.prevAyah);
        setLastAyah(preloadedAyahs.prevAyah)
        return false;
    }
    const {ayah, surah} = ayah_data;
    const prevAyah = Number(ayah) - 1;
    if (ayah == 1) {
        if (surah == 1) {
            setAyah(114, 6)
        } else {
            const prevSurah = Number(surah) - 1;
            setAyah(prevSurah, surahs[prevSurah].ayah)
        }
    }
    else
        setAyah(surah, String(prevAyah))
};

const setNextAyah = (dontstart) => {
    if (preloadedAyahs.nextAyah) {
        load_ayah_callback(preloadedAyahs.nextAyah)
        setLastAyah(preloadedAyahs.nextAyah)
        if (!dontstart && continuous && passedOnBoarding)
            $("#mic").trigger("click");
        return false
    }
    const {ayah, surah} = ayah_data
    const nextAyah = Number(ayah) + 1
    if (surahs[surah]["ayah"] == nextAyah - 1) {
        if (surah == "114" && ayah == "6") {
            setAyah("1", "1")
        } else {
            const nextSurah = Number(surah) + 1;
            setAyah(nextSurah, 1)
        }
    }
    else
        setAyah(surah, String(nextAyah))
}

function loadNextAyah() {
  let callback = (data) => {
    preloadedAyahs.nextAyah = data;
  }
  const { ayah, surah } = ayah_data;
  const nextAyah = Number(ayah) + 1;
  if(surahs[surah]["ayah"] == nextAyah - 1) {
    // If curret ayah is the last ayah of the current Surah.
    if(surah == "114" && ayah == "6") {
      // If current ayah is the last ayah of the Quran.
      api.get_specific_ayah(String(1), String(1), callback)
    } else {
      const nextSurah = Number(surah) + 1;
      api.get_specific_ayah(String(nextSurah), String(1), callback)
    }

  }
  else {
    api.get_specific_ayah(surah, String(nextAyah), callback)
  }
}

function loadPreviousAyah() {
  let callback = (data) => {
    preloadedAyahs.prevAyah = data;
  }
    const { ayah, surah } = ayah_data;
    const prevAyah = Number(ayah) - 1;
    if(ayah == 1) {
      if(surah == 1) {
        // If current ayah is the first ayah of the Quran.
        api.get_specific_ayah(String(114), surahs[114].ayah, callback)
      } else {
        // if current ayah is the first ayah of the Surah.
        const prevSurah = Number(surah) - 1;
        api.get_specific_ayah(String(prevSurah), surahs[prevSurah].ayah, callback)
      }

    }
    else {
        api.get_specific_ayah(surah, String(prevAyah), callback)
    }
}

function loadAyahTransliteration() {
    let callback = (data) => {
        $('#translit').html(`
            <p id="translit">${data.line}</p>
        `)
    }
    const {ayah: curr_ayah, surah: curr_surah} = ayah_data;
    api.get_ayah_translit(curr_surah, curr_ayah, callback)
}

// render and update the counter in the navbar of the the main page.
function renderCounter(n) {
    const counter = $(".navbar .counter");
    // const newCount = counter.html().includes("k") ? (Number(counter.html().replace("k", "")) * 1000 + n) : Number(counter.html()) + n
    var newCount = incrementCount()
    newCount = commaFormatter(newCount);
    counter.html(`${newCount}`)
    renderSubscribeCounter(newCount)
}

renderCounter(0);

// Render and update the counter in the subscription page.
function renderSubscribeCounter(count) {
    $(".screen4 .content .text strong").html(count)
}

const goToDemographics = () => {
    window.mySwipe.slide(2)
};

const goToSubscribe = () => {
    window.mySwipe.slide(3)
};

const handleStopButton = (dontGetNext) => {
    if (recorder) {
        recorder.exportWAV(function (blob) {
            recording_data[session_count % AYAHS_PER_SUBISSION] = {
                surah_num: ayah_data.surah,
                ayah_num: ayah_data.ayah,
                hash_string: session_id,
                audio: blob
            }
            stopRecording()
            if (continuous) {
                const record = recording_data[session_count % recording_data.length];
                if (record) {
                    api.send_recording(record.audio, record.surah_num, record.ayah_num, record.hash_string, continuous);
                    session_count += 1;
                    if (!dontGetNext)
                        setNextAyah(true)
                    try {
                        localStorage.setItem("ayahsRecited", String(ayahsRecited + session_count))
                    } catch (e) {
                        console.log(e.message)
                    }
                }
                renderCounter(1)
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
        })
    }
    if (!continuous) {
        state = StateEnum.COMMIT_DECISION;
        $("#mic").css("margin-bottom", "0")
        $(".review").css("display", "flex");
        $("#mic").removeClass("recording");
        $("#mic").hide();
        $(".note-button.previous-ayah").show();
        $(".note-button.next").hide();
        $(".note-button.previous").hide();
    }
}

const submitDemographics = () => {
    const serializedForm = $("#demographics-form").serializeArray();
    const gender = serializedForm[0].value;
    const age = serializedForm[1].value;
    const qiraah = serializedForm[2].value;
    const ethnicity = serializedForm[3].value;
    if (gender && age && ethnicity && qiraah) {
        $.ajax(
            {
                type: "POST",
                url: "/api/demographics/",
                data: $("#demographics-form").serialize(),
                dataType: "json",
                success: (data) => {
                    setDemographicData({gender, age, qiraah, ethnicity})
                }
            }
        );
        window.mySwipe.next()
    }
};

const skipDemographic = () => {
    if (!passedOnBoarding) {
        window.mySwipe.slide(0)
        return false;
    }
    $(".review").hide();
    $("#mic").show();
    $("#ayah").show();
    $("#progress").hide();
    $(".navbar").css("display", "flex");
    $(".note-button.previous-ayah").hide();
    setNextAyah(true)
    window.mySwipe.slide(1)
}

const toggleNavbarMenu = () => {
    const hamburger = document.querySelector(".hamburger svg");
    hamburger.classList.toggle('active');
    $(".navbar ul").toggle()
}

const navigateToChangeAyah = (surahKey = ayah_data.surah) => {
    window.mySwipe.slide(5)
    renderAyahs(surahKey, ayahsDict[surahKey]);
    renderSurahs(surahs)
}

function incrementCount(num) {
    const counter = $(".navbar .counter");
    const newCount = Number(counter.html().replace(",", "")) + 1
    return newCount
}

function commaFormatter(num) {
    return Number(num).toLocaleString()
}

function kFormatter(num) {
    return num > 999 ? (num / 1000).toFixed(1) + 'k' : num
}

$("#continuous").click(() => {
    continuous = $("#continuous").is(":checked")
    if (continuous === false)
        setContinuousChecked("")
    else
        setContinuousChecked(continuous)
})

function setContinuousChecked(value) {
    try {
        localStorage.setItem("continuous", String(value))
    } catch (e) {
        console.log(e.message)
    }
}

function handleReviewPreviousAyah() {
    $(".review").hide();
    $("#mic").show();
    $(".note-button.previous-ayah").hide();
    setPreviousAyah();
}

function getRandomAyah() {
    api.get_ayah(load_ayah_callback);
}

function handleHeritageSearch(e) {
    e.preventDefault()
    const value = e.currentTarget.value.trim().toLowerCase()
    const searchList = $(".dropdown-menu ul.search")
    const mainList = $(".dropdown-menu ul.main")

    if (value) {
        filterHeritageListItems(value)
    } else {
        mainList.show()
        searchList.hide()
    }

    function filterHeritageListItems(value) {
        searchList.show()
        mainList.hide()
        searchList.html($(".dropdown-menu ul.main li").clone().filter(function () {
            const status = $(this).html().toLowerCase().includes(value)
            if (status)
                $(this).click(handleHeritageListItemClick);
            return status
        }))
    }
}

if (isMobile.os()) {
    const userAgent = window.navigator.userAgent,
        embeddedBrowsers = /FBAN|FBForIPhone|FBAV|FBDV|FBSV|FBBV|FBMD|FBSN|FBCR|FBSF|Twitter/
    if (isMobile.os().toLowerCase() === "ios") {
        if (embeddedBrowsers.test(userAgent))
            $(".mobile-app").show();
    }
}
else {
  // Custom Scrollbar Styling.
  const sheet = document.createElement("style")
  sheet.append(`
  *::-webkit-scrollbar {
    width: 8px;
  }

  *::-webkit-scrollbar-track {
    -webkit-box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3);
    border-radius: 23px;
  }

  *::-webkit-scrollbar-thumb {
    background-color: #5ec49e;
    outline: 1px solid slategrey;
    border-radius: 23px;
  }
`);
    document.head.appendChild(sheet)
}

function setDemographicData(obj) {
    try {
        localStorage.setItem("demographicData", JSON.stringify(obj))
        demographicData = obj
    } catch (e) {
        console.log(e.message)
    }
}


const genderRadio = document.querySelector(".gender-radio ul")
genderRadio.querySelector("ul > span").style.width = genderRadio.querySelector("li.active").offsetWidth + "px"

genderRadio.querySelectorAll("li").forEach(el => {
    el.onclick = () => handleGenderRadioChange(el)
})

function handleGenderRadioChange(el) {
    genderRadio.querySelector("ul > span").style.left = el.offsetLeft + "px"
    genderRadio.querySelector("ul > span").style.width = el.offsetWidth + "px"
    genderRadio.querySelector("li.active").classList.remove("active")
    el.classList.add("active");
    genderRadio.parentNode.parentNode.querySelector('input[type="hidden"]').setAttribute('value', el.getAttribute('data-value'));
}

// setting demographics data of current user as defaults in demographics form.
function setDemographicValues() {
  const form = $("#demographics-form")
  const gender = form.find(".form-row .gender-radio")
  const age = form.find(".form-row .dropdown.age ")
  const qiraah = form.find(".form-row .dropdown.qiraah ")
  const heritage = form.find(".form-row .dropdown.heritage ")
  const ageValue = age.find(".dropdown-menu ul li#" + demographicData.age).text()
  const qiraahValue = qiraah.find(".dropdown-menu ul li#" + demographicData.qiraah).text()
  const heritageValue = heritage.find(".dropdown-menu ul.main li#" + demographicData.ethnicity).text()
  age.find(".select span").text(ageValue)
  age.find("input[type='hidden']").val(demographicData.age)
  qiraah.find(".select span").text(qiraahValue)
  qiraah.find("input[type='hidden']").val(demographicData.qiraah)
  heritage.find(".select span").text(heritageValue)
  heritage.find("input[type='hidden']").val(demographicData.ethnicity)
  gender.parent().find("input[type='hidden']").val(demographicData.gender)
  const choice = document.querySelector(".form-row .gender-radio ul li:not(.active)")
  const genderValue = document.querySelector(".form-row .gender-radio ul li.active").getAttribute("data-value")
  if(genderValue !== demographicData.gender) handleGenderRadioChange(choice)
}

if (demographicData){
  setDemographicValues()
}

// Code for forcing portrait view on mobile.
window.addEventListener("orientationchange", function() {
  const page = document.querySelector("html");
  if(screen.orientation.type !== "portrait-primary") {
    page.classList.add("rotate-screen");
    setTimeout(() => {
      const newHeight = (innerWidth / innerHeight).toPrecision(4).slice(0,4) * 100 + "%";
      page.style.height = newHeight
    }, 100)
  } else {
    page.classList.remove("rotate-screen");
    setTimeout(() => {
      page.style.height = "100%";
    }, 100)
  }
}
