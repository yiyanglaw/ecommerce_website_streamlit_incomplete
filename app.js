// app.js
document.addEventListener("DOMContentLoaded", function () {
    loadContent("Home");

    // Navigation
    document.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", function () {
            const page = this.dataset.page;
            loadContent(page);
        });
    });
});

// Function to load content dynamically
function loadContent(page) {
    fetchContent(page).then(html => {
        document.getElementById("app").innerHTML = html;
    });
}

// Function to fetch content from the server (replace with your server logic)
async function fetchContent(page) {
    let response;
    switch (page) {
        case "Home":
            response = await fetch("/home"); // Replace with your server endpoint
            break;
        case "Shop":
            response = await fetch("/shop"); // Replace with your server endpoint
            break;
        case "Account":
            response = await fetch("/account"); // Replace with your server endpoint
            break;
        default:
            response = await fetch("/404"); // Replace with your server endpoint for 404
    }

    return response.text();
}
