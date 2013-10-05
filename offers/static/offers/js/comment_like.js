$(document).ready(function(){
    $(".like-button-comment").click(click_like);
});

function click_like(){
    var comment_id = $(this).data('comment');
    var button = $("#button-like-" + comment_id);
    button.addClass("disabled");

    $.get("/offers/comment/like/" + comment_id + '/', function(data){
        button.replaceWith(data["button"]);
        console.log($("#like-count-" + comment_id).replaceWith(data["likes"]));

        button = $("#button-like-" + comment_id);
        button.click(click_like);
    }).fail(function(){
        button.removeClass('btn-info').addClass('btn-danger');
    });
}
