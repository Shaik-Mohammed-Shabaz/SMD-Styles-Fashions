// ==========================
// Wishlist Toggle
// ==========================

const wishlistButtons = document.querySelectorAll(".wishlist");

wishlistButtons.forEach((heart) => {
  heart.addEventListener("click", async (event) => {
    event.preventDefault();
    event.stopPropagation();

    const productId = heart.dataset.productId;

    if (!productId) {
      console.error("Wishlist: Product ID missing.");
      showToast("Product ID missing.");
      return;
    }

    try {
      const response = await fetch("/wishlist/toggle", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: new URLSearchParams({
          product_id: productId,
        }),
      });

      console.log("Wishlist response status:", response.status);

      const responseText = await response.text();

      console.log("Wishlist response:", responseText);

      if (!response.ok) {
        showToast("Unable to update Wishlist.");
        return;
      }

      let data;

      try {
        data = JSON.parse(responseText);
      } catch (error) {
        console.error("Invalid JSON response:", responseText);
        showToast("Invalid wishlist response! Kindly login & try again.");
        return;
      }

      if (!data.success) {
        showToast(data.message || "Unable to update Wishlist.");
        return;
      }

      // ==========================
      // Wishlist Added
      // ==========================

      if (data.added) {
        heart.classList.add("active");

        heart.textContent = "♥";

        showToast("❤️ Added to Wishlist");
      }

      // ==========================
      // Wishlist Removed
      // ==========================
      else {
        heart.classList.remove("active");

        heart.textContent = "♡";

        showToast("💔 Removed from Wishlist");
      }
    } catch (error) {
      console.error("Wishlist request failed:", error);

      showToast("Unable to update Wishlist.");
    }
  });
});

const navbar = document.querySelector(".navbar");

let lastScrollY = window.scrollY;

if (navbar) {
  window.addEventListener(
    "scroll",
    () => {
      const currentScrollY = window.scrollY;

      // At the very top
      if (currentScrollY <= 10) {
        navbar.classList.remove("nav-hidden");
        navbar.classList.remove("scrolled");
        lastScrollY = currentScrollY;
        return;
      }

      // Scrolling DOWN → hide navbar
      if (currentScrollY > lastScrollY) {
        navbar.classList.add("nav-hidden");
        navbar.classList.add("scrolled");
      }

      // Scrolling UP → immediately show navbar
      else if (currentScrollY < lastScrollY) {
        navbar.classList.remove("nav-hidden");
        navbar.classList.add("scrolled");
      }

      lastScrollY = currentScrollY;
    },
    { passive: true },
  );
}

const sections = document.querySelectorAll("section");
const navLinks = document.querySelectorAll(".nav-links a");

window.addEventListener("scroll", () => {
  let current = "";

  sections.forEach((section) => {
    const sectionTop = section.offsetTop - 120;
    const sectionHeight = section.clientHeight;

    if (pageYOffset >= sectionTop) {
      current = section.getAttribute("id");
    }
  });

  navLinks.forEach((link) => {
    link.classList.remove("active");

    if (link.getAttribute("href") === "#" + current) {
      link.classList.add("active");
    }
  });
});

let cart = JSON.parse(localStorage.getItem("cart")) || [];

const cartCounter = document.getElementById("cart-count");
const cartButtons = document.querySelectorAll(".cart-btn:not(#modalAddCart)");
const cartItems = document.getElementById("cartItems");
const totalText = document.querySelector(".cart-footer h3");

updateCart();

cartButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const name = button.dataset.name;
    const price = Number(button.dataset.price);

    const productCard = button.closest(".product-card");

    const selectedSize =
      productCard
        ?.querySelector(".wishlist-size-btn.active")
        ?.textContent.trim() || "M";

    const image = productCard?.querySelector("img")?.src || "";

    console.log("Adding to cart:", name, price, selectedSize);

    // Product + Size are treated as separate cart items
    const existingProduct = cart.find(
      (item) => item.name === name && item.size === selectedSize,
    );

    if (existingProduct) {
      existingProduct.quantity++;
    } else {
      cart.push({
        name: name,
        price: price,
        image: image,
        size: selectedSize,
        quantity: 1,
      });
    }

    // Save immediately
    updateCart();

    showToast("🛒 Product added to cart");
  });
});

function updateCart() {
  // Update cart count everywhere
  if (cartCounter) {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

    cartCounter.textContent = totalItems;
  }

  // Save cart everywhere
  localStorage.setItem("cart", JSON.stringify(cart));

  console.log("Cart:", cart);

  // Stop here if the cart sidebar doesn't exist
  if (!cartItems || !totalText) {
    return;
  }

  cartItems.innerHTML = "";

  let total = 0;
  let totalItems = 0;

  cart.forEach((product, index) => {
    total += product.price * product.quantity;

    totalItems += product.quantity;

    const item = document.createElement("div");

    item.className = "cart-item";

    item.innerHTML = `

<img class="cart-product-image" src="${product.image}" alt="${product.name}">

<div class="cart-info">

    <strong>${product.name}</strong>

    <p>Size : ${product.size || "-"}</p>

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

    console.log("Added to sidebar:", product.name);

    item.querySelector(".plus").onclick = () => {
      product.quantity++;

      updateCart();
    };

    item.querySelector(".minus").onclick = () => {
      if (product.quantity > 1) {
        product.quantity--;
      } else {
        cart.splice(index, 1);
      }

      updateCart();
    };

    item.querySelector(".remove-item").onclick = () => {
      cart.splice(index, 1);

      updateCart();
    };
  });

  cartCounter.textContent = totalItems;

  totalText.textContent = `Total: ₹${total}`;

  if (cart.length === 0) {
    cartItems.innerHTML = "<p>Your cart is empty.</p>";
  }
}

const cartLink = document.getElementById("cart-link");
const cartSidebar = document.getElementById("cartSidebar");
const closeCart = document.getElementById("closeCart");

if (cartLink && cartSidebar && closeCart) {
  cartLink.addEventListener("click", (e) => {
    e.preventDefault();

    cartSidebar.classList.add("active");
  });

  closeCart.addEventListener("click", () => {
    cartSidebar.classList.remove("active");
  });
}

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
  quickViewButtons.forEach((button) => {
    button.addEventListener("click", () => {
      modalImage.src = button.dataset.image;
      modalTitle.textContent = button.dataset.name;
      modalPrice.textContent = button.dataset.price;
      modalDescription.textContent = button.dataset.description;
      // Select Medium by default
      modalSizes.forEach((btn) => {
        btn.classList.remove("active");
      });

      const defaultSize = Array.from(modalSizes).find(
        (btn) => btn.textContent.trim() === "M",
      );

      if (defaultSize) {
        defaultSize.classList.add("active");
      }

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
// Quick View Size Selection
// ==========================

const modalSizes = document.querySelectorAll(".size-btn");

modalSizes.forEach((button) => {
  button.addEventListener("click", () => {
    modalSizes.forEach((btn) => {
      btn.classList.remove("active");
    });

    button.classList.add("active");
    console.log("Selected size:", button.textContent);
  });
});

// ==========================
// Product Page Size Selection
// ==========================

const productSizeButtons = document.querySelectorAll(".product-size-btn");

productSizeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    productSizeButtons.forEach((btn) => {
      btn.classList.remove("active");
    });

    button.classList.add("active");

    console.log("Selected product size:", button.textContent.trim());
  });
});

// ==========================
// Product Search + Category Filter
// ==========================

const searchInput = document.getElementById("searchProduct");
const categoryFilter = document.getElementById("categoryFilter");
const productCards = document.querySelectorAll(".product-card");

function filterProducts() {
  const searchText = searchInput.value.toLowerCase();
  const selectedCategory = categoryFilter.value;

  productCards.forEach((card) => {
    const productName = card.querySelector("h3").textContent.toLowerCase();
    const productCategory = card.dataset.category;

    const matchesSearch = productName.includes(searchText);

    const matchesCategory =
      selectedCategory === "all" || productCategory === selectedCategory;

    if (matchesSearch && matchesCategory) {
      card.style.display = "block";
    } else {
      card.style.display = "none";
    }
  });
}

if (searchInput && categoryFilter) {
  searchInput.addEventListener("keyup", filterProducts);

  categoryFilter.addEventListener("change", filterProducts);
}

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

    products.forEach((product) => {
      productGrid.appendChild(product);
    });
  });
}

// ==========================
// Size Selection
// ==========================

const sizeButtons = document.querySelectorAll(".size-selector button");

sizeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    sizeButtons.forEach((btn) => {
      btn.classList.remove("active");
    });

    button.classList.add("active");
  });
});

// ==========================
// Product Image Gallery
// ==========================

const mainImage = document.getElementById("mainImage");
const thumbnails = document.querySelectorAll(".thumbnail");

if (mainImage && thumbnails.length) {
  thumbnails.forEach((thumbnail) => {
    thumbnail.addEventListener("click", () => {
      // Change only the main product image
      mainImage.src = thumbnail.src;

      // Update active thumbnail
      thumbnails.forEach((img) => {
        img.classList.remove("active");
      });

      thumbnail.classList.add("active");
    });
  });
}
// ==========================
// Product Page Add to Cart
// ==========================

const addToCartProduct = document.getElementById("addToCartProduct");

if (addToCartProduct) {
  addToCartProduct.addEventListener("click", () => {
    const name = document.getElementById("productName").textContent.trim();

    const price = Number(
      document.getElementById("productPrice").textContent.replace("₹", ""),
    );

    const selectedSize =
      document.querySelector(".size-selector .active")?.textContent || "M";

    const existingProduct = cart.find(
      (item) => item.name === name && item.size === selectedSize,
    );

    if (existingProduct) {
      existingProduct.quantity++;
    } else {
      cart.push({
        name: name,
        price: price,
        image: document.getElementById("mainImage").src,
        size: selectedSize,
        quantity: 1,
      });
    }

    updateCart();

    showToast("✔ Product added to cart");
  });
}

// ==========================
// Quick View Add to Cart
// ==========================

const modalAddCart = document.getElementById("modalAddCart");
console.log("modalAddCart =", modalAddCart);

if (modalAddCart) {
  modalAddCart.addEventListener("click", () => {
    const name = modalTitle.textContent;

    const price = Number(modalPrice.textContent.replace("₹", ""));

    const activeSize = document.querySelector(".sizes .size-btn.active");

    const selectedSize = activeSize ? activeSize.textContent : "M";

    console.log(name, price, selectedSize);

    const existingProduct = cart.find(
      (item) => item.name === name && item.size === selectedSize,
    );

    if (existingProduct) {
      existingProduct.quantity++;
    } else {
      cart.push({
        name: name,

        price: price,

        image: modalImage.src,

        size: selectedSize,

        quantity: 1,
      });
    }

    updateCart();

    modal.classList.remove("active");

    showToast("✔ Product added to cart");
  });
}

// ==========================
// Checkout Page
// ==========================

const checkoutItems = document.getElementById("checkoutItems");
const checkoutTotal = document.getElementById("checkoutTotal");

if (checkoutItems && checkoutTotal) {
  checkoutItems.innerHTML = "";

  let total = 0;

  const checkoutType = localStorage.getItem("checkoutType");

  const buyNowproduct = JSON.parse(localStorage.getItem("buyNowproduct"));

  const products = checkoutType === "buyNow" ? [buyNowproduct] : cart;

  products.forEach((product) => {
    total += product.price * product.quantity;

    const item = document.createElement("div");

    item.className = "checkout-item";

    item.innerHTML = `

            <h4>${product.name}</h4>

            <p>Size : ${product.size || "-"}</p>

            <p>Quantity : ${product.quantity}</p>

            <p>₹${product.price}</p>

            <hr>

        `;

    checkoutItems.appendChild(item);
  });

  const subtotal = total;
  const discount = Math.floor(total * 0.1);

  const subtotalPrice = document.getElementById("subtotalPrice");
  const discountPrice = document.getElementById("discountPrice");

  if (subtotalPrice) {
    subtotalPrice.textContent = `₹${subtotal}`;
  }

  if (discountPrice) {
    discountPrice.textContent = `-₹${discount}`;
  }

  total = subtotal - discount;

  checkoutTotal.textContent = `Total : ₹${total}`;
}

// ==========================
// Product Page Buy Now
// ==========================

const productBuyNow = document.getElementById("buyNowproduct");

if (productBuyNow) {
  productBuyNow.addEventListener("click", () => {
    const name = document.getElementById("productName").textContent.trim();

    const price = Number(
      document.getElementById("productPrice").textContent.replace("₹", ""),
    );

    const size =
      document.querySelector(".size-selector .active")?.textContent || "M";

    const buyNowproduct = {
      name: name,

      price: price,

      size: size,

      quantity: 1,
    };

    localStorage.setItem("buyNowproduct", JSON.stringify(buyNowproduct));

    localStorage.setItem("checkoutType", "buyNow");

    window.location.href = "/checkout";
  });
}

// ==========================
// Quick View Buy Now
// ==========================

const modalBuyNow = document.getElementById("modalBuyNow");

if (modalBuyNow) {
  modalBuyNow.addEventListener("click", () => {
    const buyNowProduct = {
      name: modalTitle.textContent,

      price: Number(modalPrice.textContent.replace("₹", "")),

      size: document.querySelector(".size-btn.active").textContent,

      quantity: 1,
    };

    localStorage.setItem("buyNowproduct", JSON.stringify(buyNowProduct));

    localStorage.setItem("checkoutType", "buyNow");

    modal.classList.remove("active");

    if (window.location.pathname.includes("/pages/")) {
      window.location.href = "/checkout";
    } else {
      window.location.href = "/checkout";
    }
  });
}

// ==========================
// Card Buy Now - Quick Purchase
// ==========================

const cardBuyNowButtons = document.querySelectorAll(".card-buy-now");

const buyNowModal = document.getElementById("buyNowModal");
const closeBuyNow = document.querySelector(".close-buy-now");

const buyNowImage = document.getElementById("buyNowImage");
const buyNowTitle = document.getElementById("buyNowTitle");
const buyNowPrice = document.getElementById("buyNowPrice");

const buySizeButtons = document.querySelectorAll(".buy-size-btn");
const confirmBuyNow = document.getElementById("confirmBuyNow");

let selectedBuyNowProduct = null;
let selectedBuyNowSize = "M";

cardBuyNowButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const productCard = button.closest(".product-card");

    if (!productCard || !buyNowModal) {
      return;
    }

    const quickViewButton = productCard.querySelector(".quick-view");

    selectedBuyNowProduct = {
      name: button.dataset.name,
      price: Number(button.dataset.price),
      image: quickViewButton
        ? quickViewButton.dataset.image
        : productCard.querySelector("img").src,
    };

    selectedBuyNowSize = "M";

    buyNowImage.src = selectedBuyNowProduct.image;
    buyNowTitle.textContent = selectedBuyNowProduct.name;
    buyNowPrice.textContent = `₹${selectedBuyNowProduct.price}`;

    // Reset size buttons
    buySizeButtons.forEach((btn) => {
      btn.classList.remove("active");
    });

    // M is selected by default
    const defaultSize = Array.from(buySizeButtons).find(
      (btn) => btn.textContent.trim() === "M",
    );

    if (defaultSize) {
      defaultSize.classList.add("active");
    }

    buyNowModal.classList.add("active");
  });
});

// Size selection

buySizeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    buySizeButtons.forEach((btn) => {
      btn.classList.remove("active");
    });

    button.classList.add("active");

    selectedBuyNowSize = button.textContent.trim();
  });
});

// Close Buy Now modal

if (closeBuyNow && buyNowModal) {
  closeBuyNow.addEventListener("click", () => {
    buyNowModal.classList.remove("active");
  });
}

// Continue to Checkout

if (confirmBuyNow) {
  confirmBuyNow.addEventListener("click", () => {
    if (!selectedBuyNowProduct) {
      return;
    }

    const buyNowProduct = {
      name: selectedBuyNowProduct.name,

      price: selectedBuyNowProduct.price,

      image: selectedBuyNowProduct.image,

      size: selectedBuyNowSize,

      quantity: 1,
    };

    localStorage.setItem("buyNowproduct", JSON.stringify(buyNowProduct));

    localStorage.setItem("checkoutType", "buyNow");

    buyNowModal.classList.remove("active");

    window.location.href = "/checkout";
  });
}

// ==========================
// Proceed To Checkout
// ==========================

const checkoutBtn = document.querySelector(".checkout-btn");

if (checkoutBtn) {
  checkoutBtn.addEventListener("click", () => {
    if (cart.length === 0) {
      showToast("Your cart is empty");
      return;
    }

    window.location.href = "/checkout";
  });
}

// ==========================
// Place Order
// ==========================

const placeOrderBtn = document.getElementById("placeOrderBtn");

if (placeOrderBtn) {
  placeOrderBtn.addEventListener("click", () => {
    const form = document.getElementById("checkoutForm");

    if (!form.checkValidity()) {
      form.reportValidity();

      return;
    }

    showToast("🎉 Order placed successfully");

    const currentCheckoutType = localStorage.getItem("checkoutType");

    if (currentCheckoutType === "buyNow") {
      // Buy Now purchase should NOT affect the normal cart
      localStorage.removeItem("buyNowproduct");
      localStorage.removeItem("checkoutType");
    } else {
      // Normal cart checkout: clear the cart after successful order
      localStorage.removeItem("cart");
      localStorage.removeItem("checkoutType");
    }

    setTimeout(() => {
      window.location.href = "/success";
    }, 300);
  });
}

/* ==========================
   Toast Notification
========================== */

const toast = document.getElementById("toast");

function showToast(message) {
  if (!toast) return;

  toast.textContent = message;

  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
  }, 2000);
}

// ==========================
// Product Image Zoom
// ==========================

const productImage = document.getElementById("mainImage");

if (productImage) {
  productImage.addEventListener("mousemove", (e) => {
    const rect = productImage.getBoundingClientRect();

    const x = ((e.clientX - rect.left) / rect.width) * 100;

    const y = ((e.clientY - rect.top) / rect.height) * 100;

    productImage.style.transformOrigin = `${x}% ${y}%`;
  });
}

// ==========================
// Page Loader
// ==========================

window.addEventListener("load", () => {
  const loader = document.getElementById("loader");

  if (loader) {
    setTimeout(() => {
      loader.classList.add("hide");
    }, 600);
  }
});

// ==========================
// Product Search
// ==========================

const productSearch = document.getElementById("productSearch");

if (productSearch) {
  productSearch.addEventListener("keyup", () => {
    const value = productSearch.value.toLowerCase();

    document.querySelectorAll(".product-card").forEach((card) => {
      const title = card.querySelector("h3").textContent.toLowerCase();

      if (title.includes(value)) {
        card.style.display = "block";
      } else {
        card.style.display = "none";
      }
    });
  });
}

// ==========================
// Mobile Menu
// ==========================

const menuToggle = document.querySelector(".menu-toggle");

const navMenu = document.querySelector(".nav-links");

if (menuToggle && navMenu) {
  menuToggle.addEventListener("click", () => {
    navMenu.classList.toggle("active");

    menuToggle.textContent = navMenu.classList.contains("active") ? "✖" : "☰";
  });
}

// ==========================
// Back To Top
// ==========================

const backToTop = document.getElementById("backToTop");

if (backToTop) {
  window.addEventListener("scroll", () => {
    backToTop.style.display = window.scrollY > 300 ? "block" : "none";
  });

  backToTop.addEventListener("click", () => {
    window.scrollTo({
      top: 0,

      behavior: "smooth",
    });
  });
}
