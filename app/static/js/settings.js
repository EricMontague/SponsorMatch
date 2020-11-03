const BACKGROUND_COLOR = "#fff";

const openSidebar = function () {
    $("#sidebarToggleBtn").on("click", function (event) {
        $(".sidebar").addClass("show-sidebar");
        $(".bg-overlay-dark").addClass("show");

        onClickOutside();

    });
};


const closeSidebar = function () {
    $(".close-sidebar").on("click", function (event) {
        $(".sidebar").removeClass("show-sidebar");
        $(".bg-overlay-dark").removeClass("show");
    });
};

const onClickOutside = function () {
    // Register event listener so user can click outside of sidebar to close it
    window.addEventListener("click", function (event) {
        if (event.target.classList.contains("bg-overlay-dark")) {
            $(".close-sidebar").trigger("click");
        }
    });
};




openSidebar();
closeSidebar();
setSiteBackgroundColor(BACKGROUND_COLOR);