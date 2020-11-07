const handleDeleteEventClickDashboard = function () {
    $(".delete-event").click(function (event) {
        event.preventDefault();
        let eventId = $(this).parent().closest("li").attr("id");
        $.ajax({
            type: "POST",
            url: `${window.origin}/events/${eventId}/delete`,
            dataType: "json",
            success: function (response) {
                $(`#${eventId}`).remove();
            },
            error: function (jqXHR, exception) {
                ajaxErrorHandler(jqXHR, exception);
            }
        });
        return false;
    });
};


const handleEventStatusListChange = function () {
    $("#options").change(function () {
        let status = $("#options :selected").text().toLowerCase();
        window.location.href = `${window.origin}/dashboard/events/${status}`
    });
};


handleDeleteEventClickDashboard();
handleEventStatusListChange();