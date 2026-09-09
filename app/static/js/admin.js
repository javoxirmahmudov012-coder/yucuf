/**
 * Kassetalar Admin Panel Moduli
 */

async function updateOrderStatus(orderId, newStatus) {
  if (!confirm(`Buyurtma holatini "${newStatus}" ga o'zgartirishni tasdiqlaysizmi?`)) {
    return;
  }

  try {
    const res = await fetch(`/admin/orders/${orderId}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });

    if (res.ok) {
      location.reload();
    } else {
      alert("Holatni yangilashda xatolik yuz berdi.");
    }
  } catch (e) {
    alert("Serverga ulanish xatosi.");
  }
}

async function quickUpdateStock(productId, delta) {
  try {
    const res = await fetch(`/admin/products/${productId}/stock`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ delta: delta })
    });
    if (res.ok) {
      location.reload();
    }
  } catch (e) {
    alert("Stokni yangilashda xatolik.");
  }
}

async function deleteProduct(productId, title) {
  if (!confirm(`"${title}" kassetasini o'chirishni tasdiqlaysizmi?`)) return;

  try {
    const res = await fetch(`/admin/products/${productId}/delete`, {
      method: 'POST'
    });
    if (res.ok) {
      location.reload();
    }
  } catch (e) {
    alert("Mahsulotni o'chirishda xatolik.");
  }
}

function printInvoice() {
  window.print();
}
