$(function() {
    $("#navbar-dropdown").on("click", function() {
        $("#navbar-dropdown").toggleClass("is-active");
    });

    $("#signup-prompt-modal .modal-close").on("click", function() {
        $("#signup-prompt-modal").removeClass("is-active");
    });

    $(".navbar-burger").click(function() {
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");
    });
});
