const handleSelectListChange = function () {
    $("#options").change(function () {
        let status = $("#options :selected").text().toLowerCase();
        window.location.href = `${window.origin}/dashboard/admin-panel/${status}`
    });
};

handleSelectListChange();

