// function to change the appropriate tab to active
const toggleTab = function (tab) {
    $(".nav-tabs .nav-link").each(function () {
        if ($(this).hasClass("active") && $(this) !== tab) {
            $(this).removeClass("active");
        };

    });

    $(tab).find(".nav-link").addClass("active");
};

const handleLiveTabClick = function () {
    $("#live").click(function () {
        const userId = $(".user-profile").attr("id");
        const status = $(this).attr("id");
        $.ajax({
            type: "GET",
            url: `${window.origin}/users/${userId}/events/${status}`,
            dataType: "html",
            success: function (response) {
                toggleTab("#live");
                $("#eventThumbnails").html(response);
            }
        });
        return false;
    });
};


const handlePastEventTabClick = function () {
    $("#pastEvent").click(function () {
        const userId = $(".user-profile").attr("id");
        $.ajax({
            type: "GET",
            url: `${window.origin}/users/${userId}/events/past`,
            dataType: "html",
            success: function (response) {
                toggleTab("#pastEvent");
                $("#eventThumbnails").html(response);
            }
        });
        return false;
    });
};

const handleCurrentTabClick = function () {
    $("#current").click(function () {
        const userId = $(".user-profile").attr("id");
        const status = $(this).attr("id");

        $.ajax({
            type: "GET",
            url: `${window.origin}/users/${userId}/sponsorships/${status}`,
            dataType: "html",
            success: function (response) {
                toggleTab("#current");
                $("#eventThumbnails").html(response);
            }
        });
        return false;
    });
};



const handlePastSponsorshipTabClick = function () {
    $("#pastSponsorship").click(function () {
        const userId = $(".user-profile").attr("id");
        const status = $(this).attr("id");
        $.ajax({
            type: "GET",
            url: `${window.origin}/users/${userId}/sponsorships/past`,
            dataType: "html",
            success: function (response) {
                toggleTab("#pastSponsorship");
                $("#eventThumbnails").html(response);
            },
            error: function (jqXHR, exception) {
                ajaxErrorHandler(jqXHR, exception);
            }
        });
        return false;
    });

};

handleLiveTabClick();
handlePastEventTabClick();
handleCurrentTabClick();
handlePastSponsorshipTabClick();