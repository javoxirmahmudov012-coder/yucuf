/**
 * Kassetalar Online Store - Savat (Cart) boshqaruv moduli
 */

const CART_STORAGE_KEY = 'kassetalar_cart_v1';

class CartManager {
  constructor() {
    this.cart = this.loadCart();
    this.initUI();
  }

  loadCart() {
    try {
      const data = localStorage.getItem(CART_STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      return [];
    }
  }

  saveCart() {
    try {
      localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(this.cart));
      this.updateBadges();
      this.renderMiniCart();
      window.dispatchEvent(new CustomEvent('cart-updated', { detail: this.cart }));
    } catch (e) {
      console.error("Cart save error", e);
    }
  }

  addItem(product, quantity = 1) {
    const existingIndex = this.cart.findIndex(item => item.id === product.id);
    if (existingIndex > -1) {
      this.cart[existingIndex].quantity += quantity;
    } else {
      this.cart.push({
        id: product.id,
        title: product.title,
        artist: product.artist,
        price: product.price,
        image_url: product.image_url,
        genre: product.genre,
        tape_type: product.tape_type,
        quantity: quantity
      });
    }
    this.saveCart();
    this.showToast(`📼 "${product.title}" savatga qo'shildi!`);
  }

  updateQuantity(productId, quantity) {
    const item = this.cart.find(item => item.id === productId);
    if (item) {
      item.quantity = Math.max(1, quantity);
      this.saveCart();
    }
  }

  removeItem(productId) {
    this.cart = this.cart.filter(item => item.id !== productId);
    this.saveCart();
    this.showToast("Mahsulot savatdan o'chirildi", "info");
  }

  clearCart() {
    this.cart = [];
    this.saveCart();
  }

  getTotalCount() {
    return this.cart.reduce((total, item) => total + item.quantity, 0);
  }

  getItemsTotal() {
    return this.cart.reduce((total, item) => total + (item.price * item.quantity), 0);
  }

  initUI() {
    this.updateBadges();
    this.renderMiniCart();
    this.bindGlobalCartButtons();
  }

  updateBadges() {
    const totalCount = this.getTotalCount();
    const badges = document.querySelectorAll('.cart-badge-count');
    badges.forEach(badge => {
      badge.textContent = totalCount;
      if (totalCount > 0) {
        badge.classList.remove('hidden');
      } else {
        badge.classList.add('hidden');
      }
    });
  }

  renderMiniCart() {
    const container = document.getElementById('mini-cart-items');
    const totalEl = document.getElementById('mini-cart-total');
    if (!container) return;

    if (this.cart.length === 0) {
      container.innerHTML = `
        <div class="py-12 text-center text-gray-400">
          <i data-lucide="shopping-bag" class="w-12 h-12 mx-auto mb-3 opacity-30"></i>
          <p class="text-base font-medium">Savatingiz hozircha bo'sh</p>
          <p class="text-xs text-gray-500 mt-1">Katalogdan yoqqan kassetalarni tanlang</p>
        </div>
      `;
      if (totalEl) totalEl.textContent = "0 so'm";
    } else {
      let html = '';
      this.cart.forEach(item => {
        html += `
          <div class="flex items-center gap-3 p-3 bg-gray-900/60 rounded-xl border border-gray-800">
            <img src="${item.image_url}" alt="${item.title}" class="w-14 h-14 object-cover rounded-lg border border-gray-700 flex-shrink-0">
            <div class="flex-1 min-w-0">
              <h4 class="text-sm font-semibold text-white truncate">${item.title}</h4>
              <p class="text-xs text-amber-500 truncate">${item.artist}</p>
              <div class="flex items-center justify-between mt-1">
                <span class="text-xs text-gray-400">${item.quantity} × ${item.price.toLocaleString()} so'm</span>
                <span class="text-xs font-bold text-white">${(item.price * item.quantity).toLocaleString()} so'm</span>
              </div>
            </div>
            <button onclick="window.cartManager.removeItem(${item.id})" class="text-gray-500 hover:text-red-400 p-1">
              <i data-lucide="trash-2" class="w-4 h-4"></i>
            </button>
          </div>
        `;
      });
      container.innerHTML = html;
      if (totalEl) totalEl.textContent = `${this.getItemsTotal().toLocaleString()} so'm`;
    }
    if (window.lucide) lucide.createIcons();
  }

  bindGlobalCartButtons() {
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.add-to-cart-btn');
      if (btn) {
        const productData = {
          id: parseInt(btn.dataset.id),
          title: btn.dataset.title,
          artist: btn.dataset.artist,
          price: parseInt(btn.dataset.price),
          image_url: btn.dataset.image,
          genre: btn.dataset.genre || 'Audio Kasseta',
          tape_type: btn.dataset.tapetype || 'Type I'
        };
        const qty = parseInt(btn.dataset.quantity || 1);
        this.addItem(productData, qty);
      }
    });
  }

  showToast(message, type = 'success') {
    let toast = document.getElementById('global-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'global-toast';
      toast.className = 'fixed bottom-24 right-6 z-50 transform transition-all duration-300 translate-y-10 opacity-0 pointer-events-none';
      document.body.appendChild(toast);
    }

    const bgClass = type === 'success' ? 'bg-amber-500 text-black font-semibold' : 'bg-gray-800 text-white border border-gray-700';
    toast.innerHTML = `
      <div class="${bgClass} px-5 py-3 rounded-xl shadow-2xl flex items-center gap-3">
        <i data-lucide="check-circle-2" class="w-5 h-5"></i>
        <span>${message}</span>
      </div>
    `;
    if (window.lucide) lucide.createIcons();

    toast.classList.remove('translate-y-10', 'opacity-0', 'pointer-events-none');
    toast.classList.add('translate-y-0', 'opacity-100');

    setTimeout(() => {
      toast.classList.add('translate-y-10', 'opacity-0', 'pointer-events-none');
      toast.classList.remove('translate-y-0', 'opacity-100');
    }, 3000);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.cartManager = new CartManager();
});

// Mini Cart Drawer toggles
function toggleMiniCart() {
  const drawer = document.getElementById('mini-cart-drawer');
  if (drawer) {
    drawer.classList.toggle('translate-x-full');
  }
}
