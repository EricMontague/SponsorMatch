const handleSaveEventClick = function () {
    $(".save-event").click(function () {
        const eventId = $(this).parent().closest("li").attr("id");
        $.ajax({
            type: "POST",
            url: `${window.origin}/events/${eventId}/save`,
            dataType: "json",
            success: function (response) {
                displayAlert(response.message);
                $(".ellipsis-menu").dropdown("toggle");
            },
            error: function (jqXHR, exception) {
                ajaxErrorHandler(jqXHR, exception);
            }
        });
        return false;
    });
};

handleSaveEventClick();
