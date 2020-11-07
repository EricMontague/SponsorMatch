const handleRemoveEventClick = function () {
    $(".remove-event").click(function (event) {
        event.preventDefault();
        const eventId = $(this).parent().closest("li").attr("id");
        $.ajax({
            type: "POST",
            url: `${window.origin}/events/saved-events/${eventId}/delete`,
            success: function () {
                displayAlert("Event deleted!", "success");
                $(`#${eventId}`).remove();
            },
            error: function (jqXHR, exception) {
                ajaxErrorHandler(jqXHR, exception);
            }
        });
        return false;
    });
}
handleRemoveEventClick();