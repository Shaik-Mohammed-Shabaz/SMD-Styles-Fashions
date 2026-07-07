// ==========================
// Wishlist Toggle
// ==========================

const wishlistButtons = document.querySelectorAll(".wishlist");

wishlistButtons.forEach((heart) => {

    heart.addEventListener("click", () => {

        heart.classList.toggle("active");

    });

});