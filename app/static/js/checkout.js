let subtotal = 0;
let userCompany = $(".view-profile").attr("id");


// Calculate sales tax, order total, set form action attribute and script data-amount attribute
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
let calculateSalesTax = function () {
    return (subtotal * 0.08).toFixed(2);
}
let calculateTotal = function () {
    return (parseFloat(calculateSalesTax()) + subtotal).toFixed(2);
}
$("#salesTax").text(`$${calculateSalesTax()}`);
$("#orderTotal").text(`$${calculateTotal()}`);

// Delete Sponsorship objects from db if the user navigates away from the page
$(window).on("unload", function () {
    let eventId = $(".container.purchase-page").attr("id");
    let success = navigator.sendBeacon(`${window.origin}/events/${eventId}/sponsorships/cancel-purchase`);
    window.location.href = window.origin;
    return false;
});


$("#upcomingEvents").click(function () {
    window.open(`${window.origin}/users/${userCompany}`);
});

$("#pastEvents").click(function () {
    window.open(`${window.origin}/users/${userCompany}?past=1`);
});

// will be declared in main.js which will be included before this script on the page
setSiteBackgroundColor("#fff");