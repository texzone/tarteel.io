let currentLocale;

$.extend($.i18n.parser.emitter, {
    // Handle SITENAME keywords
    sitename: function () {
        return 'Wikipedia';
    },
    // Handle LINK keywords
    link: function (nodes) {
        return '<a href="' + nodes[1] + '">' + nodes[0] + '</a>';
    }
});

jQuery(document).ready(function () {
    getCurrentLocale()
    const update_texts = function () {
        $('body').i18n();
        $("#mc-embedded-subscribe").attr("value", $.i18n("subscribe-page-email-button-text"))
        $("#mce-EMAIL").attr("placeholder", $.i18n("subscribe-page-email-placeholder-text"))
        $(".screen5 input[name='search']").attr("placeholder", $.i18n("surah-picker-search-placeholder"))
        $(".screen6 input[name='search']").attr("placeholder", $.i18n("ayah-picker-search-placeholder"))
        if (location.pathname === "/about/")
            aboutLocalizationCallback()
    };

    $.i18n().load({
        'en': '/static/js/i18n/languages/en.json',
        'ar': '/static/js/i18n/languages/ar.json'
    }).done(() => {
        update_texts();
    })

    // Switch languages, button event from bottom left corner
    $(".lang-switch").click((e) => {
        const locale = $(e.target).data("locale")
        $.i18n({
            locale
        });
        update_texts()
        setCurrentLocale(locale)
        styleArabicText(locale)

    })

    // Show transliteration under ayah
    $("#translit-button").click(function() {
        $("#translit").toggle();
    });

    function styleArabicText(locale) {
        if (locale === "ar") {
            $(".arabic-text").css({"font-size": "16px", "font-weight": 600})
            $(".large-arabic-text").css({"font-size": "16px", "font-weight": 600})
            $(".small-arabic-text").css({"font-size": "14px", "font-weight": 600})
            $(".form-row").css("flex-flow", "row-reverse")
            $(".rtl").css({"direction": "rtl", "text-align": "right"})
        }
        else {
            $(".arabic-text").css({"font-size": "14px", "font-weight": "normal"})
            $(".large-arabic-text").css({"font-size": "16px", "font-weight": "normal"})
            $(".small-arabic-text").css({"font-size": "12px", "font-weight": "normal"})
            $(".form-row").css("flex-flow", "row")
            $(".rtl").css({"direction": "ltr", "text-align": "left"})
        }
    }

    async function getCurrentLocale() {
        try {
            currentLocale = await localStorage.getItem("currentLocale")
            $.i18n({
                locale: currentLocale
            });
            update_texts()
            styleArabicText(currentLocale)
        } catch (e) {
            console.log(e.message)
        }
    }

    function setCurrentLocale(locale) {
        try {
            localStorage.setItem("currentLocale", String(locale))
            currentLocale = locale
        } catch (e) {
            console.log(e.message)
        }
    }


});

