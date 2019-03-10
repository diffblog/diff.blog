import { setup_ajax } from "./helpers";
setup_ajax();

$(function () {
    $("#follow_list").on("click", ".following", function() {
        $(this).removeClass("is-light");
        $(this).removeClass("following");
        $(this).addClass("is-dark");
        $(this).addClass("follow");
        $(this).text("Follow");

        $.ajax({
            type: "DELETE",
            url: "/api/user/following",
            data: {"user_id": $(this).data("user-id")},
            success: function(response) {

            }
        })
    });
    $("#follow_list").on("click", ".follow", function() {
        $(this).removeClass("is-dark");
        $(this).removeClass("follow");
        $(this).addClass("is-light");
        $(this).addClass("following");
        $(this).text("Following");

        $.ajax({
            type: "POST",
            url: "/api/user/following",
            data: {"user_id": $(this).data("user-id")},
            success: function(response) {

            }
        })
    });
});