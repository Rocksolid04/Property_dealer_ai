function changeMainImage(url) {
    const mainImage =
        document.getElementById("mainPropertyImage");

    if (mainImage) {
        mainImage.src = url;
    }
}


document.addEventListener("DOMContentLoaded", () => {

    const forms =
        document.querySelectorAll("form");

    forms.forEach((form) => {

        form.addEventListener("submit", () => {

            const button =
                form.querySelector(
                    'button[type="submit"]'
                );

            if (!button) {
                return;
            }

            button.dataset.originalText =
                button.textContent;

            button.textContent =
                "Searching...";

            button.disabled = true;

        });

    });

});