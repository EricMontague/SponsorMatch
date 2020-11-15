
class SimpleSearchHandler {
    constructor(searchForm, queryKey, searchEndpoint) {
        this.searchForm = searchForm;
        this.queryKey = queryKey;
        this.searchEndpoint = searchEndpoint
    }

    onPaginationClick() {
        const paginationNav = document.getElementById(this.searchEndpoint);
        paginationNav.addEventListener("click", function (event) {
            event.preventDefault;
            const page = this.getPageNumber(this.children[0]);
            const currentQuery = this.getPreviousQuery();
            this.executeSearch(page, currentQuery);

        })
    }

    getPageNumber(pagination) {
        const [_, currentPage] = parseInt(pagination.id.split("#"));
        let pageNumber;
        // event bubbling
        if (event.target.id === "next" && !event.target.classList.contains("disabled")) {
            pageNumber = currentPage + 1;
        } else if (event.target.id === "prev" && !event.target.classList.contains("disabled")) {
            pageNumber = currentPage - 1;
        } else {
            pageNumber = event.target.textContent;
        }
        return pageNumber;
    }

    getPreviousQuery() {
        return sessionStorage.getItem(this.queryKey);
    }

    executeSearch(page, query) {
        this.searchForm.action = `${window.origin}/search?query=${query}&${page}`;
        this.searchForm.submit();
    }

}



class AdvancedSearchHandler {
    constructor(searchForm, queryKey, searchEndpoint) {
        this.searchForm = searchForm;
        this.queryKey = queryKey;
        this.searchEndpoint = searchEndpoint
    }

    onPaginationClick() {
    }

    getPageNumber(pagination) {
        const [_, currentPage] = parseInt(pagination.id.split("#"));
        let pageNumber;
        // event bubbling
        if (event.target.id === "next" && !event.target.classList.contains("disabled")) {
            pageNumber = currentPage + 1;
        } else if (event.target.id === "prev" && !event.target.classList.contains("disabled")) {
            pageNumber = currentPage - 1;
        } else {
            pageNumber = event.target.textContent;
        }
        return pageNumber;
    }

    getPreviousQuery() {
        return sessionStorage.getItem(this.queryKey);
    }

    executeSearch(page, query) {

    }
}

const simpleSearchHandler = new SimpleSearchHandler(
    document.querySelector(".has-search").parentElement,
    "simpleSearchQuery",
    "main.search"
);


simpleSearchHandler.onPaginationClick();