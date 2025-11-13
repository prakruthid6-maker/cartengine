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
let cart = JSON.parse(localStorage.getItem('cart')) || [];
let orders = JSON.parse(localStorage.getItem('orders')) || [];
const CURRENT_USER = 'user123';
let allProducts = [];
let filteredProducts = [];
let recognition = null;
let compareList = JSON.parse(localStorage.getItem('compareList')) || [];

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  loadProducts();
  updateCartCount();
  initCartAndOrders();
  initFilters();
  initVoiceSearch();
  startLiveActivity();
  initCompare();
  initAnalytics();
  updateCompareCount();
  initDarkMode();
  initKeyboardShortcuts();
});

function initCartAndOrders() {
  const cartBtn = document.getElementById('cartBtn');
  const ordersBtn = document.getElementById('ordersBtn');
  
  if (cartBtn) {
    cartBtn.onclick = (e) => {
      e.preventDefault();
      showCartModal();
    };
  }
  
  if (ordersBtn) {
    ordersBtn.onclick = (e) => {
      e.preventDefault();
      showOrdersModal();
    };
  }
}

function updateCartCount() {
  const badge = document.getElementById('cartCount');
  if (badge) badge.textContent = cart.length;
}

// --- API Interaction ---
async function loadProducts() {
  try {
    const products = await ApiService.fetchAllProducts();
    allProducts = products;
    filteredProducts = products;
    populateFilterOptions();
    renderProducts(products);
  } catch (error) {
    console.error("Error fetching products:", error);
    productList.innerHTML = `<p class="error-text">Failed to load products. Check console for details.</p>`;
  }
}

// --- Filter Functions ---
function initFilters() {
  const applyBtn = document.getElementById('applyFilters');
  const resetBtn = document.getElementById('resetFilters');
  
  if (applyBtn) {
    applyBtn.onclick = applyFilters;
  }
  
  if (resetBtn) {
    resetBtn.onclick = resetFilters;
  }
}

function populateFilterOptions() {
  const categoryFilter = document.getElementById('categoryFilter');
  const badgeFilter = document.getElementById('badgeFilter');
  
  const categories = [...new Set(allProducts.map(p => p.categoryId))];
  const badges = [...new Set(allProducts.map(p => p.badge).filter(b => b))];
  
  categoryFilter.innerHTML = '<option value="">All Categories</option>' + 
    categories.map(c => `<option value="${escapeAttr(c)}">${escapeHtml(c)}</option>`).join('');
  
  badgeFilter.innerHTML = '<option value="">All Badges</option>' + 
    badges.map(b => `<option value="${escapeAttr(b)}">${escapeHtml(b)}</option>`).join('');
}

function applyFilters() {
  const category = document.getElementById('categoryFilter').value;
  const priceRange = document.getElementById('priceFilter').value;
  const badge = document.getElementById('badgeFilter').value;
  
  filteredProducts = allProducts.filter(product => {
    let match = true;
    
    if (category && product.categoryId !== category) match = false;
    if (badge && product.badge !== badge) match = false;
    
    if (priceRange) {
      if (priceRange === '0-50' && product.price >= 50) match = false;
      if (priceRange === '50-100' && (product.price < 50 || product.price >= 100)) match = false;
      if (priceRange === '100-500' && (product.price < 100 || product.price >= 500)) match = false;
      if (priceRange === '500+' && product.price < 500) match = false;
    }
    
    return match;
  });
  
  renderProducts(filteredProducts);
  showToast(`Found ${filteredProducts.length} product(s)`);
}

function resetFilters() {
  document.getElementById('categoryFilter').value = '';
  document.getElementById('priceFilter').value = '';
  document.getElementById('badgeFilter').value = '';
  filteredProducts = allProducts;
  renderProducts(allProducts);
  showToast('Filters reset');
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
    productList.innerHTML = `
      <div class="empty-state">
        <i class="fa-solid fa-box-open"></i>
        <h3>No Products Found</h3>
        <p>Try adjusting your filters or add new products</p>
        <button class="btn" onclick="resetFilters()">Reset Filters</button>
      </div>
    `;
    return;
  }

  console.log('Rendering products:', products.length);
  window.productsData = {};
  products.forEach(p => { window.productsData[p.id] = p; });
  
  productList.innerHTML = products
    .map(
      (product, index) => `
        <div class="product-card" style="animation-delay: ${index * 0.05}s">
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
            <button type="button" class="btn-buy" data-pid="${product.id}">
              <i class="fa-solid fa-shopping-cart"></i> Add to Cart
            </button>
            <button type="button" class="btn-compare" data-pid="${product.id}">
              <i class="fa-solid fa-code-compare"></i>
            </button>
            <button type="button" class="btn-edit" data-pid="${product.id}">
              <i class="fa-solid fa-pen"></i>
            </button>
            <button type="button" class="btn-delete" data-pid="${product.id}" data-cid="${product.categoryId}">
              <i class="fa-solid fa-trash"></i>
            </button>
          </div>
        </div>
      `
    )
    .join("");
  
  setTimeout(() => {
    document.querySelectorAll('.btn-buy').forEach(btn => {
      btn.addEventListener('click', function() {
        const product = window.productsData[this.dataset.pid];
        addToCart(product);
      });
    });
    
    document.querySelectorAll('.btn-compare').forEach(btn => {
      btn.addEventListener('click', function() {
        const product = window.productsData[this.dataset.pid];
        addToCompare(product);
      });
    });
    
    document.querySelectorAll('.btn-edit').forEach(btn => {
      btn.addEventListener('click', function() {
        const product = window.productsData[this.dataset.pid];
        editProduct(this.dataset.pid, product);
      });
    });
    
    document.querySelectorAll('.btn-delete').forEach(btn => {
      btn.addEventListener('click', function() {
        deleteProduct(this.dataset.pid, this.dataset.cid);
      });
    });
  }, 100);
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

// --- Cart Functions ---
function addToCart(product) {
  const existing = cart.find(item => item.id === product.id);
  if (existing) {
    existing.quantity++;
  } else {
    cart.push({...product, quantity: 1});
  }
  localStorage.setItem('cart', JSON.stringify(cart));
  updateCartCount();
  showToast('Added to cart!');
}

function removeFromCart(productId) {
  cart = cart.filter(item => item.id !== productId);
  localStorage.setItem('cart', JSON.stringify(cart));
  updateCartCount();
  showCartModal();
}

function updateQuantity(productId, change) {
  const item = cart.find(item => item.id === productId);
  if (item) {
    item.quantity += change;
    if (item.quantity <= 0) {
      removeFromCart(productId);
    } else {
      localStorage.setItem('cart', JSON.stringify(cart));
      showCartModal();
    }
  }
}

function showCartModal() {
  const overlay = document.createElement('div');
  overlay.className = 'cart-modal show';
  
  const box = document.createElement('div');
  box.className = 'cart-box';
  
  const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  
  box.innerHTML = `
    <h3><i class="fa-solid fa-shopping-cart"></i> Shopping Cart</h3>
    ${cart.length === 0 ? '<p>Your cart is empty</p>' : cart.map(item => `
      <div class="cart-item">
        <img src="${escapeAttr(item.image)}" alt="${escapeAttr(item.name)}" onerror="this.src='https://placehold.co/80x80'" />
        <div class="cart-item-info">
          <h4>${escapeHtml(item.name)}</h4>
          <p>$${item.price.toFixed(2)} × ${item.quantity}</p>
        </div>
        <div class="cart-item-actions">
          <button class="qty-btn" onclick="window.updateQuantity('${item.id}', -1)">-</button>
          <span>${item.quantity}</span>
          <button class="qty-btn" onclick="window.updateQuantity('${item.id}', 1)">+</button>
          <button class="remove-btn" onclick="window.removeFromCart('${item.id}')"><i class="fa-solid fa-trash"></i></button>
        </div>
      </div>
    `).join('')}
    ${cart.length > 0 ? `
      <div class="cart-total">
        <h4>Total: $${total.toFixed(2)}</h4>
      </div>
      <div class="cart-buttons">
        <button class="btn btn-primary" onclick="window.checkoutCart()">Checkout</button>
        <button class="btn btn-cancel" onclick="this.closest('.cart-modal').remove()">Close</button>
      </div>
    ` : '<button class="btn" onclick="this.closest(\'.cart-modal\').remove()">Close</button>'}
  `;
  
  overlay.appendChild(box);
  document.body.appendChild(overlay);
  overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
}

function checkoutCart() {
  if (cart.length === 0) return;
  
  const overlay = document.createElement('div');
  overlay.className = 'buy-modal show';
  
  const box = document.createElement('div');
  box.className = 'buy-box';
  
  const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  
  box.innerHTML = `
    <h3>Checkout</h3>
    <p><strong>Total Items:</strong> ${cart.length}</p>
    <p><strong>Total Amount:</strong> $${total.toFixed(2)}</p>
    <form id="checkoutForm">
      <label>Delivery Address:</label>
      <textarea id="address" rows="3" required placeholder="Enter your delivery address"></textarea>
      <label>Payment Method:</label>
      <select id="paymentMethod" required>
        <option value="Credit Card">Credit Card</option>
        <option value="Debit Card">Debit Card</option>
        <option value="PayPal">PayPal</option>
        <option value="Cash on Delivery">Cash on Delivery</option>
      </select>
      <div class="buy-buttons">
        <button type="submit" class="btn btn-primary">Place Order</button>
        <button type="button" class="btn btn-cancel" onclick="this.closest('.buy-modal').remove()">Cancel</button>
      </div>
    </form>
  `;
  
  overlay.appendChild(box);
  document.body.appendChild(overlay);
  
  const form = box.querySelector('#checkoutForm');
  form.onsubmit = async (e) => {
    e.preventDefault();
    const address = document.getElementById('address').value;
    const paymentMethod = document.getElementById('paymentMethod').value;
    
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';
    
    try {
      // Create orders in backend for each cart item
      const orderIds = [];
      for (const item of cart) {
        const response = await fetch('https://8080-kode-ws-4b191181a.hebbale.academy/orders/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product_id: item.id,
            quantity: item.quantity,
            user_id: CURRENT_USER,
            delivery_address: address,
            payment_method: paymentMethod
          })
        });
        
        const result = await response.json();
        if (result.order_id) orderIds.push(result.order_id);
      }
      
      // Save to localStorage for frontend display
      const order = {
        order_id: orderIds[0] || 'ORD-LOCAL',
        user_id: CURRENT_USER,
        items: [...cart],
        total_price: total,
        status: 'Order Placed',
        delivery_address: address,
        payment_method: paymentMethod,
        order_date: new Date().toISOString()
      };
      
      orders.push(order);
      localStorage.setItem('orders', JSON.stringify(orders));
      cart = [];
      localStorage.setItem('cart', JSON.stringify(cart));
      updateCartCount();
      
      overlay.remove();
      document.querySelector('.cart-modal')?.remove();
      showToast(`Order placed! IDs: ${orderIds.join(', ')}\nTrack via chat: "track order ${orderIds[0]}"`);
    } catch (error) {
      console.error('Error placing order:', error);
      showToast('Error placing order. Please try again.');
      submitBtn.disabled = false;
      submitBtn.textContent = 'Place Order';
    }
  };
  
  overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
}

function showOrdersModal() {
  const overlay = document.createElement('div');
  overlay.className = 'orders-modal show';
  
  const box = document.createElement('div');
  box.className = 'orders-box';
  
  box.innerHTML = `
    <h3><i class="fa-solid fa-box"></i> My Orders</h3>
    ${orders.length === 0 ? '<p>No orders yet</p>' : orders.map(order => `
      <div class="order-item">
        <div class="order-header">
          <span class="order-id">${order.order_id}</span>
          <span class="order-status status-${order.status.toLowerCase().replace(' ', '-')}">${order.status}</span>
        </div>
        <div class="order-details">
          <p><strong>Date:</strong> ${new Date(order.order_date).toLocaleDateString()}</p>
          <p><strong>Items:</strong> ${order.items.length} product(s)</p>
          <p><strong>Total:</strong> $${order.total_price.toFixed(2)}</p>
          <p><strong>Address:</strong> ${escapeHtml(order.delivery_address)}</p>
          <p><strong>Payment:</strong> ${order.payment_method}</p>
        </div>
        ${order.status !== 'Cancelled' && order.status !== 'Delivered' ? `
          <button class="btn btn-cancel-order" onclick="window.cancelOrder('${order.order_id}')">
            <i class="fa-solid fa-times"></i> Cancel Order
          </button>
        ` : ''}
      </div>
    `).join('')}
    <div class="cart-buttons">
      <button class="btn" onclick="this.closest('.orders-modal').remove()">Close</button>
    </div>
  `;
  
  overlay.appendChild(box);
  document.body.appendChild(overlay);
  overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
}

// --- Order Cancellation ---
async function cancelOrder(orderId) {
  const confirm = await customConfirm('Are you sure you want to cancel this order?');
  if (!confirm) return;
  
  try {
    const response = await fetch(`https://8080-kode-ws-4b191181a.hebbale.academy/orders/cancel/${orderId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    
    const result = await response.json();
    
    if (response.ok) {
      const order = orders.find(o => o.order_id === orderId);
      if (order) order.status = 'Cancelled';
      localStorage.setItem('orders', JSON.stringify(orders));
      document.querySelector('.orders-modal')?.remove();
      showToast('Order cancelled successfully');
      showOrdersModal();
    } else {
      showToast(result.detail || 'Failed to cancel order');
    }
  } catch (error) {
    console.error('Error cancelling order:', error);
    showToast('Error cancelling order');
  }
}

window.cancelOrder = cancelOrder;

// --- Product Comparison ---
function initCompare() {
  const compareBtn = document.getElementById('compareBtn');
  if (compareBtn) {
    compareBtn.onclick = (e) => {
      e.preventDefault();
      showCompareModal();
    };
  }
}

function addToCompare(product) {
  if (compareList.find(p => p.id === product.id)) {
    showToast('Already in comparison', 'info');
    return;
  }
  if (compareList.length >= 4) {
    showToast('Maximum 4 products for comparison', 'warning');
    return;
  }
  compareList.push(product);
  localStorage.setItem('compareList', JSON.stringify(compareList));
  updateCompareCount();
  showToast('Added to comparison', 'success');
}

function updateCompareCount() {
  const badge = document.getElementById('compareCount');
  if (badge) badge.textContent = compareList.length;
}

function removeFromCompare(productId) {
  compareList = compareList.filter(p => p.id !== productId);
  localStorage.setItem('compareList', JSON.stringify(compareList));
  updateCompareCount();
  showCompareModal();
}

function showCompareModal() {
  const overlay = document.createElement('div');
  overlay.className = 'compare-modal show';
  
  const box = document.createElement('div');
  box.className = 'compare-box';
  
  if (compareList.length === 0) {
    box.innerHTML = `
      <h3><i class="fa-solid fa-code-compare"></i> Product Comparison</h3>
      <div class="empty-state">
        <i class="fa-solid fa-code-compare"></i>
        <h3>No Products to Compare</h3>
        <p>Add products using the compare button</p>
      </div>
      <button class="btn" onclick="this.closest('.compare-modal').remove()">Close</button>
    `;
  } else {
    box.innerHTML = `
      <h3><i class="fa-solid fa-code-compare"></i> Compare Products (${compareList.length}/4)</h3>
      <div class="compare-table">
        <table>
          <thead>
            <tr>
              <th>Feature</th>
              ${compareList.map(p => `<th>${escapeHtml(p.name)}</th>`).join('')}
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Image</strong></td>
              ${compareList.map(p => `<td><img src="${escapeAttr(p.image)}" alt="${escapeAttr(p.name)}" style="width:80px;height:80px;object-fit:cover;border-radius:8px;"></td>`).join('')}
            </tr>
            <tr>
              <td><strong>Price</strong></td>
              ${compareList.map(p => `<td class="price-highlight">$${p.price.toFixed(2)}</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Rating</strong></td>
              ${compareList.map(p => `<td>${'⭐'.repeat(Math.round(p.ratings))} ${p.ratings.toFixed(1)}</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Reviews</strong></td>
              ${compareList.map(p => `<td>${p.reviews} reviews</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Category</strong></td>
              ${compareList.map(p => `<td>${escapeHtml(p.categoryId)}</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Badge</strong></td>
              ${compareList.map(p => `<td>${p.badge ? `<span class="badge-mini">${escapeHtml(p.badge)}</span>` : '-'}</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Action</strong></td>
              ${compareList.map(p => `<td><button class="btn-remove-compare" onclick="window.removeFromCompare('${p.id}')"><i class="fa-solid fa-times"></i></button></td>`).join('')}
            </tr>
          </tbody>
        </table>
      </div>
      <div class="compare-actions">
        <button class="btn" onclick="window.clearCompare()">Clear All</button>
        <button class="btn" onclick="this.closest('.compare-modal').remove()">Close</button>
      </div>
    `;
  }
  
  overlay.appendChild(box);
  document.body.appendChild(overlay);
  overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
}

function clearCompare() {
  compareList = [];
  localStorage.setItem('compareList', JSON.stringify(compareList));
  updateCompareCount();
  document.querySelector('.compare-modal')?.remove();
  showToast('Comparison cleared', 'info');
}

window.removeFromCompare = removeFromCompare;
window.clearCompare = clearCompare;

// --- Analytics Dashboard ---
function initAnalytics() {
  const analyticsBtn = document.getElementById('analyticsBtn');
  if (analyticsBtn) {
    analyticsBtn.onclick = (e) => {
      e.preventDefault();
      showAnalyticsModal();
    };
  }
}

// --- Dark Mode ---
function initDarkMode() {
  const darkModeToggle = document.getElementById('darkModeToggle');
  const isDark = localStorage.getItem('darkMode') === 'true';
  
  if (isDark) {
    document.body.classList.add('dark-mode');
    darkModeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
  }
  
  darkModeToggle.onclick = () => {
    document.body.classList.toggle('dark-mode');
    const isDarkNow = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkNow);
    darkModeToggle.innerHTML = isDarkNow ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
    showToast(isDarkNow ? 'Dark mode enabled' : 'Light mode enabled', 'info');
  };
}

// --- Keyboard Shortcuts ---
function initKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    
    if (e.key === '?') {
      e.preventDefault();
      showShortcutsModal();
    } else if (e.key === 'c' && e.ctrlKey) {
      e.preventDefault();
      document.getElementById('cartBtn')?.click();
    } else if (e.key === 'o' && e.ctrlKey) {
      e.preventDefault();
      document.getElementById('ordersBtn')?.click();
    } else if (e.key === 'a' && e.ctrlKey) {
      e.preventDefault();
      document.getElementById('analyticsBtn')?.click();
    } else if (e.key === 'd' && e.ctrlKey) {
      e.preventDefault();
      document.getElementById('darkModeToggle')?.click();
    } else if (e.key === 'r' && e.ctrlKey) {
      e.preventDefault();
      resetFilters();
    }
  });
  
  setTimeout(() => {
    const hint = document.getElementById('shortcutsHint');
    if (hint) hint.classList.add('show');
    setTimeout(() => hint?.classList.remove('show'), 5000);
  }, 2000);
}

function showShortcutsModal() {
  const overlay = document.createElement('div');
  overlay.className = 'shortcuts-modal show';
  
  const box = document.createElement('div');
  box.className = 'shortcuts-box';
  
  box.innerHTML = `
    <h3><i class="fa-solid fa-keyboard"></i> Keyboard Shortcuts</h3>
    <div class="shortcuts-grid">
      <div class="shortcut-item">
        <kbd>?</kbd>
        <span>Show shortcuts</span>
      </div>
      <div class="shortcut-item">
        <kbd>Ctrl</kbd> + <kbd>C</kbd>
        <span>Open cart</span>
      </div>
      <div class="shortcut-item">
        <kbd>Ctrl</kbd> + <kbd>O</kbd>
        <span>View orders</span>
      </div>
      <div class="shortcut-item">
        <kbd>Ctrl</kbd> + <kbd>A</kbd>
        <span>Open analytics</span>
      </div>
      <div class="shortcut-item">
        <kbd>Ctrl</kbd> + <kbd>D</kbd>
        <span>Toggle dark mode</span>
      </div>
      <div class="shortcut-item">
        <kbd>Ctrl</kbd> + <kbd>R</kbd>
        <span>Reset filters</span>
      </div>
    </div>
    <button class="btn" onclick="this.closest('.shortcuts-modal').remove()">Close</button>
  `;
  
  overlay.appendChild(box);
  document.body.appendChild(overlay);
  overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
}

function showAnalyticsModal() {
  const totalProducts = allProducts.length;
  const avgPrice = allProducts.reduce((sum, p) => sum + p.price, 0) / totalProducts;
  const avgRating = allProducts.reduce((sum, p) => sum + p.ratings, 0) / totalProducts;
  const categories = [...new Set(allProducts.map(p => p.categoryId))];
  const categoryData = categories.map(cat => ({
    name: cat,
    count: allProducts.filter(p => p.categoryId === cat).length
  }));
  
  const overlay = document.createElement('div');
  overlay.className = 'analytics-modal show';
  
  const box = document.createElement('div');
  box.className = 'analytics-box';
  
  box.innerHTML = `
    <h3><i class="fa-solid fa-chart-line"></i> Analytics Dashboard</h3>
    <div class="analytics-grid">
      <div class="stat-card">
        <i class="fa-solid fa-box"></i>
        <div>
          <h4>${totalProducts}</h4>
          <p>Total Products</p>
        </div>
      </div>
      <div class="stat-card">
        <i class="fa-solid fa-dollar-sign"></i>
        <div>
          <h4>$${avgPrice.toFixed(2)}</h4>
          <p>Avg Price</p>
        </div>
      </div>
      <div class="stat-card">
        <i class="fa-solid fa-star"></i>
        <div>
          <h4>${avgRating.toFixed(1)}</h4>
          <p>Avg Rating</p>
        </div>
      </div>
      <div class="stat-card">
        <i class="fa-solid fa-shopping-cart"></i>
        <div>
          <h4>${cart.length}</h4>
          <p>Cart Items</p>
        </div>
      </div>
      <div class="stat-card">
        <i class="fa-solid fa-receipt"></i>
        <div>
          <h4>${orders.length}</h4>
          <p>Total Orders</p>
        </div>
      </div>
      <div class="stat-card">
        <i class="fa-solid fa-tags"></i>
        <div>
          <h4>${categories.length}</h4>
          <p>Categories</p>
        </div>
      </div>
    </div>
    <div class="category-breakdown">
      <h4>Products by Category</h4>
      <div class="category-bars">
        ${categoryData.map(cat => `
          <div class="category-bar-item">
            <span class="category-name">${cat.name}</span>
            <div class="category-bar">
              <div class="category-bar-fill" style="width: ${(cat.count / totalProducts) * 100}%"></div>
            </div>
            <span class="category-count">${cat.count}</span>
          </div>
        `).join('')}
      </div>
    </div>
    <button class="btn" onclick="this.closest('.analytics-modal').remove()">Close</button>
  `;
  
  overlay.appendChild(box);
  document.body.appendChild(overlay);
  overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
}

// --- Voice Search ---
function initVoiceSearch() {
  const voiceBtn = document.getElementById('voiceSearchBtn');
  const voiceStatus = document.getElementById('voiceStatus');
  
  if (!voiceBtn) return;
  
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    voiceBtn.style.display = 'none';
    voiceStatus.textContent = 'Voice not supported';
    return;
  }
  
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-US';
  
  voiceBtn.onclick = () => {
    try {
      recognition.start();
      voiceStatus.textContent = 'Listening...';
      voiceBtn.classList.add('listening');
    } catch (e) {
      console.error('Voice error:', e);
      voiceStatus.textContent = 'Click again';
      voiceBtn.classList.remove('listening');
    }
  };
  
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript.toLowerCase();
    voiceStatus.textContent = `"${transcript}"`;
    processVoiceCommand(transcript);
    setTimeout(() => voiceStatus.textContent = '', 3000);
  };
  
  recognition.onend = () => {
    voiceBtn.classList.remove('listening');
  };
  
  recognition.onerror = (event) => {
    console.error('Speech error:', event.error);
    voiceStatus.textContent = 'Try again';
    voiceBtn.classList.remove('listening');
    setTimeout(() => voiceStatus.textContent = '', 3000);
  };
}

function processVoiceCommand(text) {
  console.log('Voice command:', text);
  
  if (text.includes('under') || text.includes('below')) {
    const match = text.match(/\d+/);
    if (match) {
      const price = parseInt(match[0]);
      document.getElementById('priceFilter').value = price <= 50 ? '0-50' : price <= 100 ? '50-100' : price <= 500 ? '100-500' : '500+';
      applyFilters();
      return;
    }
  }
  
  if (text.includes('electronics') || text.includes('electronic')) {
    document.getElementById('categoryFilter').value = 'Electronics';
    applyFilters();
    return;
  }
  
  if (text.includes('clothing') || text.includes('clothes')) {
    document.getElementById('categoryFilter').value = 'Clothing';
    applyFilters();
    return;
  }
  
  if (text.includes('books') || text.includes('book')) {
    document.getElementById('categoryFilter').value = 'Books';
    applyFilters();
    return;
  }
  
  if (text.includes('sale') || text.includes('discount')) {
    document.getElementById('badgeFilter').value = 'Sale';
    applyFilters();
    return;
  }
  
  if (text.includes('reset') || text.includes('clear')) {
    resetFilters();
    return;
  }
  
  showToast('Try: "Show electronics under 100"', 'info');
}

// --- Live Activity Feed ---
function startLiveActivity() {
  const activities = [
    { icon: 'fa-shopping-cart', text: 'Sarah just purchased iPhone 13', color: '#10b981' },
    { icon: 'fa-eye', text: '5 people viewing this product', color: '#6366f1' },
    { icon: 'fa-star', text: 'New 5-star review added', color: '#f59e0b' },
    { icon: 'fa-fire', text: 'Hot deal: 20% off Electronics', color: '#ef4444' },
    { icon: 'fa-truck', text: 'Order #12345 shipped', color: '#3b82f6' },
    { icon: 'fa-heart', text: 'Product added to 10 wishlists', color: '#ec4899' },
    { icon: 'fa-tag', text: 'Flash sale starts in 5 min', color: '#8b5cf6' },
    { icon: 'fa-user-plus', text: 'John joined the platform', color: '#14b8a6' }
  ];
  
  setInterval(() => {
    const activity = activities[Math.floor(Math.random() * activities.length)];
    showLiveActivity(activity);
  }, 8000);
  
  setTimeout(() => showLiveActivity(activities[0]), 2000);
}

function showLiveActivity(activity) {
  const container = document.getElementById('liveActivity');
  const notification = document.createElement('div');
  notification.className = 'live-notification';
  notification.innerHTML = `
    <i class="fa-solid ${activity.icon}" style="color: ${activity.color}"></i>
    <span>${activity.text}</span>
  `;
  container.appendChild(notification);
  
  setTimeout(() => notification.classList.add('show'), 100);
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => notification.remove(), 300);
  }, 5000);
}

function showToast(message, type = 'success') {
  const colors = {
    success: '#10b981',
    error: '#ef4444',
    info: '#6366f1',
    warning: '#f59e0b'
  };
  const icons = {
    success: 'fa-check-circle',
    error: 'fa-times-circle',
    info: 'fa-info-circle',
    warning: 'fa-exclamation-circle'
  };
  const toast = document.createElement('div');
  toast.className = 'toast-notification';
  toast.style.background = colors[type];
  toast.innerHTML = `<i class="fa-solid ${icons[type]}"></i><span>${message}</span>`;
  document.body.appendChild(toast);
  setTimeout(() => toast.classList.add('show'), 100);
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Expose functions to window for onclick handlers
window.updateQuantity = updateQuantity;
window.removeFromCart = removeFromCart;
window.checkoutCart = checkoutCart;

// --- Buy Modal ---
function showBuyModal(productId, productName, productPrice) {
  const overlay = document.createElement("div");
  overlay.className = "buy-modal show";

  const box = document.createElement("div");
  box.className = "buy-box";

  box.innerHTML = `
    <h3>Complete Your Purchase</h3>
    <p><strong>Product:</strong> ${escapeHtml(productName)}</p>
    <p><strong>Price:</strong> $${escapeHtml(productPrice)}</p>
    <form id="buyForm">
      <label>Quantity:</label>
      <input type="number" id="quantity" value="1" min="1" required />
      <label>Delivery Address:</label>
      <textarea id="address" rows="3" required placeholder="Enter your delivery address"></textarea>
      <label>Payment Method:</label>
      <select id="paymentMethod" required>
        <option value="Credit Card">Credit Card</option>
        <option value="Debit Card">Debit Card</option>
        <option value="PayPal">PayPal</option>
        <option value="Cash on Delivery">Cash on Delivery</option>
      </select>
      <div class="buy-buttons">
        <button type="submit" class="btn btn-primary">Place Order</button>
        <button type="button" class="btn btn-cancel">Cancel</button>
      </div>
    </form>
  `;

  overlay.appendChild(box);
  document.body.appendChild(overlay);

  const form = box.querySelector("#buyForm");
  const cancelBtn = box.querySelector(".btn-cancel");

  form.onsubmit = async (e) => {
    e.preventDefault();
    const quantity = parseInt(document.getElementById("quantity").value);
    const address = document.getElementById("address").value;
    const paymentMethod = document.getElementById("paymentMethod").value;
    
    try {
      overlay.remove();
      alert(`Order placed successfully! Product: ${productName}, Quantity: ${quantity}\nYou can track your order through the chat interface.`);
    } catch (error) {
      console.error("Error placing order:", error);
      alert("Failed to place order. Please try again.");
    }
  };

  cancelBtn.onclick = () => overlay.remove();
  overlay.onclick = (e) => {
    if (e.target === overlay) overlay.remove();
  };
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
