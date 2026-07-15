// ==========================
// Wishlist Toggle
// ==========================

const wishlistButtons = document.querySelectorAll(".wishlist");

wishlistButtons.forEach((heart) => {

    heart.addEventListener("click", () => {

        heart.classList.toggle("active");

    });

});

const navbar = document.querySelector(".navbar");

window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
        navbar.classList.add("scrolled");
    } else {
        navbar.classList.remove("scrolled");
    }
});

const sections = document.querySelectorAll("section");
const navLinks = document.querySelectorAll(".nav-links a");

window.addEventListener("scroll", () => {

    let current = "";

    sections.forEach(section => {
        const sectionTop = section.offsetTop - 120;
        const sectionHeight = section.clientHeight;

        if (pageYOffset >= sectionTop) {
            current = section.getAttribute("id");
        }
    });

    navLinks.forEach(link => {
        link.classList.remove("active");

        if (link.getAttribute("href") === "#" + current) {
            link.classList.add("active");
        }
    });

});

let cart = JSON.parse(localStorage.getItem("cart")) || [];

const cartCounter = document.getElementById("cart-count");
const cartButtons = document.querySelectorAll(".cart-btn");
const cartItems = document.getElementById("cartItems");
const totalText = document.querySelector(".cart-footer h3");

updateCart();

cartButtons.forEach(button => {

    button.addEventListener("click", () => {

        const name = button.dataset.name;
        const price = Number(button.dataset.price);

        const existingProduct = cart.find(item => item.name === name);

        if(existingProduct){

            existingProduct.quantity++;

        }else{

            cart.push({
                name:name,
                price:price,
                quantity:1
            });

        }

        updateCart();

    });

});

function updateCart(){

    cartItems.innerHTML = "";

    let total = 0;
    let totalItems = 0;

    cart.forEach((product,index)=>{

        total += product.price * product.quantity;

        totalItems += product.quantity;

        const item = document.createElement("div");

        item.className="cart-item";

        item.innerHTML=`

            <div class="cart-info">

                <strong>${product.name}</strong>

                <p>₹${product.price}</p>

            </div>

            <div class="quantity">

                <button class="minus">-</button>

                <span>${product.quantity}</span>

                <button class="plus">+</button>

            </div>

            <button class="remove-item">🗑</button>

        `;

        cartItems.appendChild(item);

        item.querySelector(".plus").onclick=()=>{

            product.quantity++;

            updateCart();

        };

        item.querySelector(".minus").onclick=()=>{

            if(product.quantity>1){

                product.quantity--;

            }else{

                cart.splice(index,1);

            }

            updateCart();

        };

        item.querySelector(".remove-item").onclick=()=>{

            cart.splice(index,1);

            updateCart();

        };

    });

    cartCounter.textContent=totalItems;

    totalText.textContent=`Total: ₹${total}`;

    if(cart.length===0){

        cartItems.innerHTML="<p>Your cart is empty.</p>";

    }
    localStorage.setItem("cart", JSON.stringify(cart));

}

const cartLink = document.getElementById("cart-link");
const cartSidebar = document.getElementById("cartSidebar");
const closeCart = document.getElementById("closeCart");

cartLink.addEventListener("click", (e) => {

    e.preventDefault();

    cartSidebar.classList.add("active");

});

closeCart.addEventListener("click", () => {

    cartSidebar.classList.remove("active");

});

// ==========================
// Quick View Modal
// ==========================

const quickViewButtons = document.querySelectorAll(".quick-view");

const modal = document.getElementById("quickViewModal");
const closeModal = document.querySelector(".close-modal");

const modalImage = document.getElementById("modalImage");
const modalTitle = document.getElementById("modalTitle");
const modalPrice = document.getElementById("modalPrice");
const modalDescription = document.getElementById("modalDescription");

if (quickViewButtons.length && modal && closeModal) {

    quickViewButtons.forEach(button => {

        button.addEventListener("click", () => {

            modalImage.src = button.dataset.image;
            modalTitle.textContent = button.dataset.name;
            modalPrice.textContent = button.dataset.price;
            modalDescription.textContent = button.dataset.description;

            modal.classList.add("active");

        });

    });

    closeModal.addEventListener("click", () => {

        modal.classList.remove("active");

    });

    window.addEventListener("click", (e) => {

        if (e.target === modal) {

            modal.classList.remove("active");

        }

    });

}

// ==========================
// Product Search + Category Filter
// ==========================

const searchInput = document.getElementById("searchProduct");
const categoryFilter = document.getElementById("categoryFilter");
const productCards = document.querySelectorAll(".product-card");

function filterProducts() {

    const searchText = searchInput.value.toLowerCase();
    const selectedCategory = categoryFilter.value;

    productCards.forEach(card => {

        const productName = card.querySelector("h3").textContent.toLowerCase();
        const productCategory = card.dataset.category;

        const matchesSearch = productName.includes(searchText);

        const matchesCategory =
            selectedCategory === "all" ||
            productCategory === selectedCategory;

        if (matchesSearch && matchesCategory) {

            card.style.display = "block";

        } else {

            card.style.display = "none";

        }

    });

}

searchInput.addEventListener("keyup", filterProducts);

categoryFilter.addEventListener("change", filterProducts);

// ==========================
// Product Sorting
// ==========================

const sortProducts = document.getElementById("sortProducts");
const productGrid = document.querySelector(".product-grid");

if (sortProducts && productGrid) {

    sortProducts.addEventListener("change", () => {

        const products = Array.from(productGrid.querySelectorAll(".product-card"));

        products.sort((a, b) => {

            const nameA = a.querySelector("h3").textContent.toLowerCase();
            const nameB = b.querySelector("h3").textContent.toLowerCase();

            const priceA = Number(a.querySelector(".cart-btn").dataset.price);
            const priceB = Number(b.querySelector(".cart-btn").dataset.price);

            switch (sortProducts.value) {

                case "low-high":
                    return priceA - priceB;

                case "high-low":
                    return priceB - priceA;

                case "az":
                    return nameA.localeCompare(nameB);

                case "za":
                    return nameB.localeCompare(nameA);

                default:
                    return 0;

            }

        });

        products.forEach(product => {

            productGrid.appendChild(product);

        });

    });

}