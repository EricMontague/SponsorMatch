const handleSelectListChange = function () {
    $("#filter").change(function () {
        let status = $("#filter :selected").text().toLowerCase();
        window.location.href = `${window.origin}/dashboard/admin/${status}`
    });
};

handleSelectListChange();

