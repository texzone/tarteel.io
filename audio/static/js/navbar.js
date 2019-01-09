const toggleNavbarMenu = () => {
    const hamburger = document.querySelector(".hamburger svg");
    hamburger.classList.toggle('active');
    $(".navbar > .list").toggle();
    $(".navbar .list .hidden").show();
    $(".settings").hide();
    $(".settings-menu").hide()
};
$(".settings").on("click", () => {
    $(".settings-menu").addClass("active")
});
$(document).on("click", (e) => {
    if (!document.querySelector(".settings-menu").contains(e.target) && !document.querySelector(".settings").contains(e.target)) {
        $(".settings-menu").removeClass("active")
    }
});
