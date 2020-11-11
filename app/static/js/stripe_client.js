
// Code taken from Stripe's documentation and modified for this application
// Source - https://stripe.com/docs/payments/integration-builder

// A reference to Stripe.js initialized with a fake API key.
// Sign in to see examples pre-filled with your key.
const stripe = Stripe("pk_test_BwwGznIRJevFxs6X3ZaFPZLF00tr4JEERX");


// Disable the button until we have Stripe set up on the page
document.querySelector(".stripe-button").disabled = true;

// Show a spinner on payment submission
const loading = function (isLoading) {
    if (isLoading) {
        // Disable the button and show a spinner
        document.querySelector(".stripe-button").disabled = true;
        document.querySelector("#spinner").classList.remove("hidden");
        document.querySelector("#button-text").classList.add("hidden");
    } else {
        document.querySelector(".stripe-button").disabled = false;
        document.querySelector("#spinner").classList.add("hidden");
        document.querySelector("#button-text").classList.remove("hidden");
    }
};


/* ------- UI helpers ------- */

// Shows a success message when the payment is complete
const orderComplete = function (paymentIntentId) {
    loading(false);
    document.querySelector(".stripe-button").disabled = true;
    const eventId = document.querySelector(".purchase-page").id;
    fetch(`${window.origin}/payments/checkout-success`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ eventId: eventId })
    }).then(function (result) {
        return result.json();
    }).then(function (data) {
        if (data.code == 400) {
            displayAlert(data.message, "danger");
        } else {
            displayAlert(data.message, "success");
            document.querySelector(".result-message").classList.remove("hidden");
        }
        setTimeout(function () {
            window.location.href = window.origin;
        }, 3000);
    }).catch(function (error) {
        console.log(error);
    })
};

// Show the customer the error from Stripe if their card fails to charge
const showError = function (errorMsgText) {
    loading(false);
    const errorMsg = document.querySelector("#card-error");
    errorMsg.textContent = errorMsgText;
    setTimeout(function () {
        errorMsg.textContent = "";
    }, 5000);
};

// Calls stripe.confirmCardPayment
// If the card requires authentication Stripe shows a pop-up modal to
// prompt the user to enter authentication details without leaving your page.
const payWithCard = function (stripe, card, clientSecret) {
    loading(true);
    stripe
        .confirmCardPayment(clientSecret, {
            payment_method: {
                card: card
            }
        })
        .then(function (result) {
            if (result.error) {
                // Show error to your customer
                showError(result.error.message);
            } else {
                // The payment succeeded!
                orderComplete(result.paymentIntent.id);
            }
        });
};

const getOrderTotal = function () {
    const tableDataTag = document.getElementById("orderTotal");
    return Number(tableDataTag.textContent.slice(1)) * 100;
};


const createCardEventListener = function (card) {
    card.on("change", function (event) {
        // Disable the Pay button if there are no card details in the Element
        document.querySelector(".stripe-button").disabled = event.empty;
        document.querySelector("#card-error").textContent = event.error ? event.error.message : "";
    });
};


const createFormEventListener = function (card, data) {
    const form = document.getElementById("payment-form");
    form.addEventListener("submit", function (event) {
        event.preventDefault();
        // Complete payment when the submit button is clicked
        payWithCard(stripe, card, data.clientSecret);
    });
}


const createStripeCard = function () {
    const elements = stripe.elements();

    const style = {
        base: {
            color: "#32325d",
            fontFamily: 'Arial, sans-serif',
            fontSmoothing: "antialiased",
            fontSize: "16px",
            "::placeholder": {
                color: "#32325d"
            }
        },
        invalid: {
            fontFamily: 'Arial, sans-serif',
            color: "#fa755a",
            iconColor: "#fa755a"
        }
    };
    const card = elements.create("card", { style: style });
    // Stripe injects an iframe into the DOM
    card.mount("#card-element");
    return card;

};

const processOrder = function () {
    const orderTotal = getOrderTotal();
    fetch(`${window.origin}/payments/create-payment-intent`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ orderTotal: orderTotal })
    })
        .then(function (result) {
            return result.json();
        })
        .then(function (data) {
            const card = createStripeCard();
            createCardEventListener(card);
            createFormEventListener(card, data);
        })
        .catch(function (error) {
            console.log(error);
        });
};


processOrder();