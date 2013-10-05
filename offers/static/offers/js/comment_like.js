$(document).ready(function(){
    $(".like-button-comment").click(click_like);
    $(".popoverify").popover();
});

function click_like(){
    var comment_id = $(this).data('comment');
    var button = $("#button-like-" + comment_id);
    button.addClass("disabled");
    $("#like-count-" + comment_id).popover('hide');

    $.get("/offers/comment/like/" + comment_id + '/', function(data){
        button.replaceWith(data["button"]);
        $("#like-count-" + comment_id).replaceWith(data["likes"]);
        $("#like-count-" + comment_id).popover();

        button = $("#button-like-" + comment_id);
        button.click(click_like);
    }).fail(function(){
        button.removeClass('btn-info').addClass('btn-danger');
    });
}
