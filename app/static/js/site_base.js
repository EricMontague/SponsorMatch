//Show the modal if the user entered invalid data
const showModalFormErrors = function (modalId) {
    const errors = $(".invalid-feedback");
    if (errors.length > 0) {
        $(modalId).modal("show");
    }
};



// Remove create event link if this is the sponsorship or auth blueprints
const removeCreateEventNavLink = function () {
    const splitPath = window.location.pathname.split("/");
    if (splitPath[3] === "sponsorships" || splitPath[1] === "auth") {
        $("#createEvent").remove();
    };
};

const handleDeleteEventClick = function (eventId) {
    $("#createEvent a").click(function () {
        const response = window.confirm("Are you sure you want to delete this event?  This cannot be undone.");
        if (response === true) {
            $.ajax({
                method: "POST",
                url: `${window.origin}/events/${eventId}/delete`,
                dataType: "json",
                success: function () {
                    window.location.href = `${window.origin}`;
                }
            });
        }
        return false;
    });
};

const showDeleteEventLink = function () {
    const regex = /^\/events\/\d+\/[A-Za-z]+/;
    const splitPath = window.location.pathname.split("/");
    if (regex.test(window.location.pathname) === true) {
        const eventId = parseInt(splitPath[2]);
        if (Number.isInteger(eventId)) {
            $("#createEvent a").text("Delete Event");
            handleDeleteEventClick(eventId);
        };
    };

};

const setSiteBackgroundColor = function (color) {
    document.body.style.backgroundColor = color;
};


const displayAlert = function (message, alertType) {
    const hiddenMessage = $("#hiddenMessage");
    $("#message").text(message);
    if (hiddenMessage.hasClass("hidden")) {
        hiddenMessage.removeClass("hidden").show();
        hiddenMessage.addClass("alert-" + alertType);
    } else {
        hiddenMessage.show();
    }
};

const ajaxErrorHandler = function (jqXHR, exception, showAlert = false) {
    let message = ""
    if (jqXHR.status === 0) {
        message = "Not connect.\n Verify Network.";
    } else if (jqXHR.status == 404) {
        message = "Requested page not found. [404]";
    } else if (jqXHR.status == 500) {
        message = "Internal Server Error [500].";
    } else if (exception === 'parsererror') {
        message = "Requested JSON parse failed.";
    } else if (exception === 'timeout') {
        message = "Time out error.";
    } else if (exception === 'abort') {
        message = "Ajax request aborted.";
    } else {
        message = "Uncaught Error.\n" + jqXHR.responseText;
    }
    if (showAlert === true) {
        alert(message);
    } else {
        displayAlert(message, "danger");
    }

};

const handleCloseAlertClick = function () {
    $("#hiddenMessage .close").click(function () {
        $("#hiddenMessage").hide();
    });
};

const cacheSimpleSearchQuery = function () {
    const searchForm = document.querySelector(".has-search").parentElement;

    searchForm.addEventListener("submit", function (event) {
        const searchInput = this.elements[0];
        sessionStorage.setItem("simpleSearchQuery", searchInput.value);

    });


}

showDeleteEventLink();
removeCreateEventNavLink();
handleCloseAlertClick();
cacheSimpleSearchQuery();