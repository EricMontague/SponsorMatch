
const PACKAGE_MODAL_ID = "#addPackageModal";



const isEdittingPackage = function () {
    let fullPath = window.location;
    let path = fullPath.pathname.split("/");
    return path[path.length - 1] === "edit";

};

const redirectUserAfterPackageEdit = function () {
    const eventId = $(".edit-event-content").attr("id");
    $("#addPackageModal").on("hidden.bs.modal", function (e) {
        window.location.href = `${window.origin}/events/${eventId}/packages`;
    });
};


const updatePackage = function (formAction) {
    $(".modal-footer input").click(function () {
        $("#addPackageForm").attr("action", formAction);
        $("#addPackageForm").submit();
    });
};

const onEditView = function () {
    const fullPath = window.location;
    const path = fullPath.pathname.split("/");
    if (isEdittingPackage()) {
        $("#addPackageModal").modal("show");
        redirectUserAfterPackageEdit();
        updatePackage(fullPath.href);
    };
};



const addPackage = function () {
    $(".modal-footer input").click(function () {
        $("#addPackageForm").submit();
    });
};

const deletePackage = function () {
    $(".delete-package").click(function () {
        const eventId = $(".edit-event-content").attr("id");
        const packageId = $(this).parent().closest("li").attr("id");
        $.ajax({
            type: "POST",
            url: `${window.origin}/events/${eventId}/packages/${packageId}/delete`,
            success: function (response) {
                window.location.href = response.url;
            },
            error: function (jqXHR, exception) {
                ajaxErrorHandler(jqXHR, exception);
            }
        });
        return false;
    });
};


addPackage();
deletePackage();
onEditView();
showModalFormErrors(PACKAGE_MODAL_ID);