const handleSponsorshipStatusListChange = function () {
    $("#filter").change(function () {
        const status = $("#filter :selected").text().toLowerCase();
        window.location.href = `${window.origin}/dashboard/sponsorships/${status}`
    });

}


const handleEventLinkClick = function () {
    $(".event-title").click(function () {
        location = $(this).find("a").attr("href");
        // Needed to prevent modal from opening before the new link is followed
        $(".sponsorship").unbind("click");
        window.location.href = window.origin + location;

    });
}


const handleOpenModalClick = function () {
    $(".sponsorship").click(function () {
        const packageId = $(this).attr("id");
        $.ajax({
            type: "GET",
            url: `${window.origin}/events/packages/${packageId}`,
            dataType: "json",
            success: function (response) {
                $(".price").html(`<span class="custom-font-semibold">Price</span>: $${response.price}`);
                $(".audience-reached").html(`<span class="custom-font-semibold">Audience Reached</span>: ${response.audience}`);
                $(".description").html(`<span class="custom-font-semibold">Description</span>: ${response.description}`);
                $(".type").html(`<span class="custom-font-semibold">Package Type</span>: ${response.package_type}`);
                $("#viewEvent").attr("href", `${window.origin}/events/${response.event_id}`);
                $("#packageModal").modal("show");
            },
            error: function (jqXHR, exception) {
                $("#packageModal").modal("toggle");
                ajaxErrorHandler(jqXHR, exception);
            }
        })
        return false;
    });

}

handleSponsorshipStatusListChange();
handleEventLinkClick();
handleOpenModalClick();