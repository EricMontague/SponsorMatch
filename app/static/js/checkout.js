
const userCompany = $(".view-profile").attr("id");


// Calculate sales tax, order total, set form action attribute and script data-amount attribute
const calculateSubTotal = function () {
    let subtotal = 0;
    $(".subtotal").each(function (index) {
        let price = "";
        let elementText = $(this).text();
        for (let index = 0; index < elementText.length; index++) {
            if (elementText[index] === "." || $.isNumeric(elementText[index])) {
                price += elementText[index];
            }
        }
        subtotal += parseFloat(price);
    });
    return subtotal;
};


const calculateSalesTax = function () {
    const subtotal = calculateSubTotal();
    return (subtotal * 0.08).toFixed(2);
}
const calculateTotal = function () {
    const subtotal = calculateSubTotal();
    return (parseFloat(calculateSalesTax()) + subtotal).toFixed(2);
}

const setSalesTax = function () {
    $("#salesTax").text(`$${calculateSalesTax()}`);
};

const setOrderTotal = function () {
    $("#orderTotal").text(`$${calculateTotal()}`);
};



// Delete Sponsorship objects from db if the user navigates away from the page
const deleteSponsorshipOnUnload = function () {
    $(window).on("unload", function () {
        const eventId = $(".container.purchase-page").attr("id");
        const success = navigator.sendBeacon(`${window.origin}/events/${eventId}/sponsorships/cancel-purchase`);
        window.location.href = window.origin;
        return false;
    });
};



const handleUpcomingEventsClick = function (company) {
    $("#upcomingEvents").click(function () {
        window.open(`${window.origin}/users/${company}`);
    });

};

const handlePastEventsClick = function (company) {
    $("#pastEvents").click(function () {
        window.open(`${window.origin}/users/${company}?past=1`);
    });
};

setSalesTax();
setOrderTotal();
deleteSponsorshipOnUnload();
handleUpcomingEventsClick(userCompany);
handlePastEventsClick(userCompany);

// will be declared in main.js which will be included before this script on the page
setSiteBackgroundColor("#fff");