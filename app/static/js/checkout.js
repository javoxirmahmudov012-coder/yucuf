/**
 * Checkout & Buyurtma rasmiylashtirish moduli
 */

document.addEventListener('DOMContentLoaded', () => {
  const checkoutForm = document.getElementById('checkout-form');
  const cartSummaryContainer = document.getElementById('checkout-cart-items');
  const itemsTotalEl = document.getElementById('checkout-items-total');
  const deliveryFeeEl = document.getElementById('checkout-delivery-fee');
  const discountRow = document.getElementById('checkout-discount-row');
  const discountValEl = document.getElementById('checkout-discount-value');
  const grandTotalEl = document.getElementById('checkout-grand-total');
  const regionSelect = document.getElementById('order-region');
  const deliveryMethodRadios = document.querySelectorAll('input[name="delivery_method"]');
  const promoInput = document.getElementById('promo-code-input');
  const promoApplyBtn = document.getElementById('apply-promo-btn');
  const promoMsg = document.getElementById('promo-msg');
  const phoneInput = document.getElementById('order-phone');

  let appliedPromo = null;
  let discountAmount = 0;

  // Telefon raqam maskasi (+998 90 123-45-67)
  if (phoneInput) {
    phoneInput.addEventListener('input', (e) => {
      let val = e.target.value.replace(/\D/g, '');
      if (!val.startsWith('998')) {
        val = '998' + val;
      }
      val = val.substring(0, 12);
      
      let formatted = '+998 ';
      if (val.length > 3) formatted += '(' + val.substring(3, 5);
      if (val.length >= 5) formatted += ') ' + val.substring(5, 8);
      if (val.length >= 8) formatted += '-' + val.substring(8, 10);
      if (val.length >= 10) formatted += '-' + val.substring(10, 12);
      
      e.target.value = formatted;
    });
  }

  // Render Checkout Cart Items from LocalStorage
  function renderCheckoutItems() {
    if (!window.cartManager) return;
    const cart = window.cartManager.cart;
    
    if (cart.length === 0) {
      if (cartSummaryContainer) {
        cartSummaryContainer.innerHTML = `
          <div class="py-8 text-center text-gray-400">
            <p>Savat bo'sh. Buyurtma berish uchun mahsulot tanlang.</p>
            <a href="/catalog" class="inline-block mt-3 px-4 py-2 bg-amber-500 text-black font-semibold rounded-lg">Katalogga o'tish</a>
          </div>
        `;
      }
      return;
    }

    if (cartSummaryContainer) {
      let html = '';
      cart.forEach(item => {
        html += `
          <div class="flex items-center justify-between py-3 border-b border-gray-800">
            <div class="flex items-center gap-3">
              <img src="${item.image_url}" alt="${item.title}" class="w-12 h-12 object-cover rounded-lg border border-gray-700">
              <div>
                <h4 class="text-sm font-semibold text-white">${item.title}</h4>
                <p class="text-xs text-amber-500">${item.artist}</p>
                <span class="text-xs text-gray-400">${item.quantity} dona × ${item.price.toLocaleString()} so'm</span>
              </div>
            </div>
            <span class="text-sm font-bold text-white">${(item.price * item.quantity).toLocaleString()} so'm</span>
          </div>
        `;
      });
      cartSummaryContainer.innerHTML = html;
    }

    recalculateTotals();
  }

  function getDeliveryFee() {
    const itemsTotal = window.cartManager ? window.cartManager.getItemsTotal() : 0;
    if (itemsTotal >= 300000) return 0; // 300 000 so'mdan oshsa bepul!

    const isExpress = document.querySelector('input[name="delivery_method"]:checked')?.value === 'express';
    if (isExpress) return 45000;

    const region = regionSelect ? regionSelect.value : 'Toshkent shahri';
    if (region === 'Toshkent shahri') {
      return 25000;
    } else {
      return 40000; // Viloyatlar
    }
  }

  function recalculateTotals() {
    if (!window.cartManager) return;
    const itemsTotal = window.cartManager.getItemsTotal();
    const deliveryFee = getDeliveryFee();
    const grandTotal = Math.max(0, itemsTotal - discountAmount + deliveryFee);

    if (itemsTotalEl) itemsTotalEl.textContent = `${itemsTotal.toLocaleString()} so'm`;
    if (deliveryFeeEl) {
      deliveryFeeEl.textContent = deliveryFee === 0 ? "BEPUL 🎉" : `${deliveryFee.toLocaleString()} so'm`;
    }
    if (grandTotalEl) grandTotalEl.textContent = `${grandTotal.toLocaleString()} so'm`;

    if (discountAmount > 0 && discountRow && discountValEl) {
      discountRow.classList.remove('hidden');
      discountValEl.textContent = `-${discountAmount.toLocaleString()} so'm`;
    } else if (discountRow) {
      discountRow.classList.add('hidden');
    }
  }

  // Region and Delivery Method changes
  if (regionSelect) regionSelect.addEventListener('change', recalculateTotals);
  deliveryMethodRadios.forEach(radio => radio.addEventListener('change', recalculateTotals));

  // Promokodni tekshirish
  if (promoApplyBtn && promoInput) {
    promoApplyBtn.addEventListener('click', async () => {
      const code = promoInput.value.trim();
      if (!code) return;

      const itemsTotal = window.cartManager ? window.cartManager.getItemsTotal() : 0;

      try {
        const res = await fetch('/api/check-promo', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code: code, cart_total: itemsTotal })
        });
        const data = await res.json();

        if (data.valid) {
          appliedPromo = code;
          discountAmount = data.discount_amount;
          promoMsg.textContent = `✅ Promokod faollashtirildi! Chegirma: ${discountAmount.toLocaleString()} so'm`;
          promoMsg.className = 'text-xs text-emerald-400 mt-2 block';
          recalculateTotals();
        } else {
          discountAmount = 0;
          appliedPromo = null;
          promoMsg.textContent = `❌ ${data.message || 'Yaroqsiz promokod'}`;
          promoMsg.className = 'text-xs text-rose-400 mt-2 block';
          recalculateTotals();
        }
      } catch (err) {
        promoMsg.textContent = "Xatolik yuz berdi. Qayta urinib ko'ring.";
        promoMsg.className = 'text-xs text-rose-400 mt-2 block';
      }
    });
  }

  // Buyurtmani rasmiylashtirish (Submit)
  if (checkoutForm) {
    checkoutForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!window.cartManager || window.cartManager.cart.length === 0) {
        alert("Savatingiz bo'sh. Iltimos, mahsulot qo'shing.");
        return;
      }

      const submitBtn = document.getElementById('checkout-submit-btn');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="animate-spin inline-block mr-2">⏳</span> Rasmiylashtirilmoqda...`;
      }

      const orderPayload = {
        customer_name: document.getElementById('order-name').value,
        customer_phone: document.getElementById('order-phone').value,
        customer_email: document.getElementById('order-email')?.value || null,
        region: document.getElementById('order-region').value,
        district: document.getElementById('order-district')?.value || null,
        address: document.getElementById('order-address').value,
        landmark: document.getElementById('order-landmark')?.value || null,
        delivery_notes: document.getElementById('order-notes')?.value || null,
        delivery_method: document.querySelector('input[name="delivery_method"]:checked')?.value || 'standard',
        payment_method: document.querySelector('input[name="payment_method"]:checked')?.value || 'payme',
        promo_code: appliedPromo,
        items: window.cartManager.cart.map(item => ({
          product_id: item.id,
          quantity: item.quantity
        }))
      };

      try {
        const response = await fetch('/api/create-order', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(orderPayload)
        });

        const result = await response.json();

        if (response.ok && result.success) {
          // Savatni tozalash
          window.cartManager.clearCart();
          
          // To'lov sahifasiga yoki chek sahifasiga yo'naltirish
          if (result.payment_redirect_url && (result.payment_method === 'payme' || result.payment_method === 'click')) {
            window.location.href = result.payment_redirect_url;
          } else {
            window.location.href = `/payment/success/${result.order_id}`;
          }
        } else {
          alert(`Xatolik: ${result.detail || 'Buyurtma yaratilmadi'}`);
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `Buyurtmani Tasdiqlash`;
          }
        }
      } catch (err) {
        alert("Server bilan ulanishda xatolik yuz berdi.");
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = `Buyurtmani Tasdiqlash`;
        }
      }
    });
  }

  renderCheckoutItems();
});
