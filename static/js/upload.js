// static/js/upload.js

document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const fileInput = document.getElementById("file");

    form.addEventListener("submit", (e) => {
        const file = fileInput.files[0];

        if (!file) {
            alert("Please select a file before uploading.");
            e.preventDefault();
            return;
        }

        if (!file.name.toLowerCase().endsWith(".csv")) {
            alert("Only CSV files are allowed.");
            e.preventDefault();
            return;
        }

        // Optional cosmetic feedback
        alert("Uploading file...");
    });
});
