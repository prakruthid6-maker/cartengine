import ApiService from "../services/apiService.js";

// --- Element Selectors ---
const productList = document.getElementById("productList");
const addProductBtn = document.getElementById("addProductBtn");
const modal = document.getElementById("productModal");
const closeModalBtn = document.getElementById("closeModalBtn");
const productForm = document.getElementById("productForm");
const modalTitle = document.getElementById("modalTitle");
const idInput = document.getElementById("id");

let editProductId = "";

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  loadProducts();
});

// --- API Interaction ---
async function loadProducts() {
  try {
    const products = await ApiService.fetchAllProducts();
    renderProducts(products);
  } catch (error) {
    console.error("Error fetching products:", error);
    productList.innerHTML = `<p class="error-text">Failed to load products. Check console for details.</p>`;
  }
}

// --- Form Submit (Create / Update) ---
productForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const productData = {
    id: idInput.value || crypto.randomUUID(),
    name: productForm.name.value,
    categoryId: productForm.categoryId.value,
    description: productForm.description.value,
    price: parseFloat(productForm.price.value),
    ratings: parseFloat(productForm.ratings.value),
    reviews: parseInt(productForm.reviews.value, 10),
    image: productForm.image.value,
    badge: productForm.badge.value || null,
  };

  try {
    if (editProductId) {
      // Update existing product
      await ApiService.updateProduct(productData);
    } else {
      // Create new product
      await ApiService.createProduct(productData);
    }
    closeModal();
    loadProducts();
  } catch (error) {
    console.error("Error saving product:", error);
    alert("Failed to save product. Check console for details.");
  }
});

// --- Delete Product ---
async function deleteProduct(productId, categoryId) {
  const confirm = await customConfirm(
    "Are you sure you want to delete this product?"
  );
  if (!confirm) return;

  try {
    await ApiService.deleteProduct(productId, categoryId);
    loadProducts(); // Refresh the product list
    alert("✅ Product deleted successfully");
  } catch (err) {
    console.error("Error deleting product:", err);
    alert("Failed to delete product. Check console for details.");
  }
}

// --- UI Rendering ---
function renderRatings(rating) {
  const fullStar = '<i class="fa-solid fa-star" style="color:#f59e0b;"></i>';
  const halfStar = '<i class="fa-solid fa-star-half-stroke" style="color:#f59e0b;"></i>';
  const emptyStar = '<i class="fa-regular fa-star" style="color:#cbd5e1;"></i>';

  let stars = "";
  const roundedRating = Math.round(rating * 2) / 2;

  for (let i = 1; i <= 5; i++) {
    if (i <= roundedRating) stars += fullStar;
    else if (i - 0.5 === roundedRating) stars += halfStar;
    else stars += emptyStar;
  }
  return `<span class="ratings">${stars}</span>`;
}

function renderProducts(products = []) {
  if (!products.length) {
    productList.innerHTML = `<p class="text-center p-4">No products found. Use the "Add Product" button to create a new listing!</p>`;
    return;
  }

  productList.innerHTML = products
    .map(
      (product) => `
        <div class="product-card">
          <div class="product-image-container">
            <img 
              src="${escapeAttr(product.image)}" 
              alt="${escapeAttr(product.name)}" 
              class="product-image"
              onerror="this.onerror=null; this.src='https://placehold.co/300x200/e2e8f0/333d47?text=No+Image';"
            />
            ${
              product.badge
                ? `<span class="product-badge">${escapeHtml(product.badge)}</span>`
                : ""
            }
          </div>
          <div class="product-info">
            <h3>${escapeHtml(product.name)}</h3>
            <p class="category-text"><strong>Category:</strong> ${escapeHtml(product.categoryId)}</p>
            <p class="price-text"><strong>$${escapeHtml(product.price.toFixed(2))}</strong></p>
            <div class="rating-info">
              ${renderRatings(product.ratings)} 
              <span class="review-count">(${escapeHtml(product.reviews)} reviews)</span>
            </div>
            <p class="description-text">${escapeHtml(product.description).substring(0, 80)}...</p>
          </div>
          <div class="product-actions">
            <button
              class="btn-edit"
              data-action="edit"
              data-id="${product.id}"
              data-product='${escapeAttr(JSON.stringify(product))}'
              title="Edit Product"
            >
              <i class="fa-solid fa-pen"></i>
            </button>
            <button
              class="btn-delete"
              data-action="delete"
              data-id="${product.id}"
              data-product='${escapeAttr(JSON.stringify(product))}'
              title="Delete Product"
            >
              <i class="fa-solid fa-trash"></i>
            </button>
          </div>
        </div>
      `
    )
    .join("");
}

// --- Modal Handling ---
function openModal(product = null) {
  modal.classList.add("show");
  if (product) {
    modalTitle.textContent = "Edit Product";
    editProductId = product.id;
    idInput.value = product.id;
    productForm.name.value = product.name;
    productForm.categoryId.value = product.categoryId;
    productForm.description.value = product.description;
    productForm.price.value = product.price;
    productForm.ratings.value = product.ratings;
    productForm.reviews.value = product.reviews;
    productForm.image.value = product.image;
    productForm.badge.value = product.badge;
  } else {
    modalTitle.textContent = "Add New Product";
    editProductId = null;
    productForm.reset();
    idInput.value = crypto.randomUUID();
  }
}

function closeModal() {
  modal.classList.remove("show");
  editProductId = null;
  productForm.reset();
}

function editProduct(id, data) {
  editProductId = id;
  openModal(data);
}

// --- Event Listeners ---
addProductBtn.addEventListener("click", () => openModal());
closeModalBtn.addEventListener("click", () => closeModal());
window.onclick = (event) => {
  if (event.target === modal) closeModal();
};

productList.addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-action]");
  if (!btn) return;

  const action = btn.dataset.action;
  const id = btn.dataset.id;

  if (action === "edit") {
    try {
      const productData = JSON.parse(btn.dataset.product);
      editProduct(id, productData);
    } catch (e) {
      console.error("Failed to parse product data for edit:", e);
    }
  } else if (action === "delete") {
    const productData = JSON.parse(btn.dataset.product);
    deleteProduct(id, productData.categoryId);
  }
});

// --- Utility ---
function escapeHtml(str = "") {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function escapeAttr(str = "") {
  return String(str).replaceAll('"', "&quot;");
}

// --- Custom Confirm Modal ---
function customConfirm(message) {
  return new Promise((resolve) => {
    const overlay = document.createElement("div");
    overlay.className = "confirm-modal show";

    const box = document.createElement("div");
    box.className = "confirm-box";

    const title = document.createElement("h4");
    title.textContent = "Confirm Action";

    const text = document.createElement("p");
    text.textContent = message;

    const buttons = document.createElement("div");
    buttons.className = "confirm-buttons";

    const yes = document.createElement("button");
    yes.className = "btn btn-danger";
    yes.textContent = "Yes";

    const cancel = document.createElement("button");
    cancel.className = "btn";
    cancel.textContent = "Cancel";

    buttons.append(yes, cancel);
    box.append(title, text, buttons);
    overlay.append(box);
    document.body.append(overlay);

    yes.onclick = () => {
      overlay.remove();
      resolve(true);
    };
    cancel.onclick = () => {
      overlay.remove();
      resolve(false);
    };
  });
}
