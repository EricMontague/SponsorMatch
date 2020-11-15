const getQueryParams = function (formElements) {
    const queryParams = {};
    for (let index = 0; index < formElements.length; index++) {
        const input = formElements[index];
        if (input.type !== "submit" && input.type !== "hidden") {
            queryParams[[input.name]] = input.value;
        }
    }
    return queryParams;
};

const cacheAdvancedSearchQuery = function () {
    const advancedSearchForm = document.querySelector(".advanced-search-form");
    advancedSearchForm.addEventListener("submit", function (event) {
        const queryParams = getQueryParams(this.elements);
        sessionStorage.setItem("advancedSearchQuery", JSON.stringify(queryParams));
    });
};


cacheAdvancedSearchQuery();