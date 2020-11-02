const BACKGROUND_COLOR = "#fff";
const CONTACT_MODAL_ID = "#contactModal";

//Show the modal if the user entered invalid data
const showModalFormErrors = function (modalId) {
    const errors = $(".invalid-feedback");
    if (errors.length > 0) {
        $(modalId).modal("show");
    }
};

const adjustEventInfoWidth = function () {

    const adjustWidth = function () {
        const mainEventImage = $(".main-event-image");
        const eventInfoDiv = $(".event-info");
        // The width() method is returning the main event images'
        // width as 2 pixels greater than it really is, so subtracting
        // by two accounts for that
        eventInfoDiv.width(mainEventImage.width() - 2);
    };
    window.addEventListener("load", function () {
        adjustWidth();
    });
    window.addEventListener("resize", function () {
        adjustWidth();
    });

};

const handleSaveButtonClick = function () {
    $(".save-btn").click(function () {
        const eventId = $(".event-page").attr("id");
        $.ajax({
            type: "POST",
            url: `${window.origin}/events/${eventId}/save`,
            dataType: "json",
            success: function (response) {
                displayAlert(response.message);
            }
        });
        return false;
    });
};


const handlePackageAccordionClick = function () {
    $(".packages-accordion .card-header a").click(function () {
        const packageId = $(this).attr("data-target").split("_")[1];
        const plusIcon = $(this).find(".plus-icon");
        const minusIcon = $(this).find(".minus-icon");
        if ($(plusIcon).hasClass("d-none")) {
            $(plusIcon).removeClass("d-none");
            $(minusIcon).addClass("d-none");
        } else {
            $(minusIcon).removeClass("d-none");
            $(plusIcon).addClass("d-none");
        }
    });
};

const handleInfoTabButtonClick = function () {
    $("#eventInfoTab").click(function () {
        const eventId = $(".event-page").attr("id");
        $.ajax({
            type: "GET",
            url: `${window.origin}/events/${eventId}/info`,
            dataType: "html",
            success: function (response) {
                const anchorTag = $("#sponsorsTab").find("a");
                const active = anchorTag.hasClass("active");
                if (active) {
                    anchorTag.removeClass("active");
                    $("#eventInfoTab").find("a").addClass("active");
                };
                $(".event-page-content").html(response);
            }
        });
        return false;
    });
};


const handleSponsorsTabClick = function () {
    $("#sponsorsTab").click(function () {
        const eventId = $(".event-page").attr("id");
        $.ajax({
            type: "GET",
            url: `${window.origin}/events/${eventId}/sponsors`,
            dataType: "html",
            success: function (response) {
                const anchorTag = $("#eventInfo").find("a");
                const active = anchorTag.hasClass("active");
                if (active) {
                    anchorTag.removeClass("active");
                    $("#sponsorsTab").find("a").addClass("active");
                };
                $(".event-page-content").html(response);
            }
        });
        return false;
    });
};


const handleSelectedPackageClick = function () {
    $(".select-package").click(function () {
        const regexPrice = /\d+\.\d{2}/;
        const regexQty = /\d+/;
        const $element = $(this);
        const quantity = parseInt(regexQty.exec($("#packageQuantity").text()));
        const total = parseFloat(regexPrice.exec($("#total").text()));
        const cost = parseFloat(regexPrice.exec($(this).siblings(".price").text()));
        if ($element.text() === "Add") {
            $element.text("Remove");
            if (total === 0.00) {
                $("#checkout").removeClass("disabled");
            };
            $("#packageQuantity").text(`QTY: ${quantity + 1}`);
            $("#total").text(`USD $${(total + cost).toFixed(2)}`);
        } else {
            $element.text("Add");
            if (parseInt(total - cost) === 0) {
                $("#checkout").addClass("disabled");
            };
            $("#packageQuantity").text(`QTY: ${quantity - 1}`);
            $("#total").text(`USD $${(total - cost).toFixed(2)}`);
        };
        const package = $element.closest(".collapse")[0]
        $(package).toggleClass("selected");
    });
};


const handleCheckoutButtonClick = function () {
    $("#checkout").click(function () {
        const eventId = $(".event-page").attr("id");
        const packageIds = [];
        $(".selected").each(function (index) {
            packageIds.push($(this).attr("id").split("_")[1]);
        });
        $.ajax({
            type: "POST",
            url: `${window.origin}/events/${eventId}/sponsorships`,
            contentType: "application/json",
            data: JSON.stringify({ "ids": packageIds }),
            dataType: "json",
            success: function (response) {
                window.location.href = response.url;
            },
            error: function (jqXHR, exception) {
                $("#packageModal").modal("toggle");
                ajaxErrorHandler(jqXHR, exception);
            }
        });
        return false;
    });
};



setSiteBackgroundColor(BACKGROUND_COLOR);
adjustEventInfoWidth();
handleSaveButtonClick();
handlePackageAccordionClick();
handleInfoTabButtonClick();
handleSponsorsTabClick();
handleSelectedPackageClick();
handleCheckoutButtonClick();
showModalFormErrors(CONTACT_MODAL_ID);
