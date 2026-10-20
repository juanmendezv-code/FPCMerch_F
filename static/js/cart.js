const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
const badge = document.querySelector('#cartBadge');
const drawer = document.querySelector('#cartDrawer');
const overlay = document.querySelector('#cartDrawerOverlay');
const drawerBody = document.querySelector('#cartDrawerBody');
const drawerFooter = document.querySelector('#cartDrawerFooter');
const drawerCount = document.querySelector('[data-drawer-count]');
const toasts = document.querySelector('#toastContainer');
const notify = (message, error = false) => {
  const toast = document.createElement('div'); toast.className = `toast${error ? ' error' : ''}`; toast.textContent = message;
  toasts?.append(toast); setTimeout(() => toast.remove(), 4000);
};
const post = async (url, payload) => {
  const response = await fetch(url, {method:'POST', headers:{'Content-Type':'application/json','X-CSRFToken':csrf,'X-Requested-With':'XMLHttpRequest'}, body:JSON.stringify(payload)});
  const data = await response.json();
  if (!response.ok || !data.ok) throw new Error(data.error || 'No se pudo actualizar el carrito.');
  return data;
};
const updateDrawer = async () => {
  try {
    const response = await fetch('/api/carrito/'); const data = await response.json();
    if (badge) badge.textContent = data.count;
    if (drawerCount) drawerCount.textContent = data.count;
    drawerBody?.replaceChildren();
    if (!data.items.length) {
      const empty = document.createElement('p'); empty.textContent = 'Tu carrito está vacío.'; drawerBody?.append(empty);
      if (drawerFooter) drawerFooter.replaceChildren(carritoLink());
      return;
    }
    data.items.forEach((item) => {
      const row = document.createElement('div'); row.className = 'drawer-item';
      const name = document.createElement('strong'); name.textContent = item.product;
      const detail = document.createElement('span'); detail.textContent = `${item.size} · ${item.quantity} × $${Number(item.price).toLocaleString('es-CO')}`;
      const subtotal = document.createElement('b'); subtotal.textContent = `$${Number(item.subtotal).toLocaleString('es-CO')}`;
      row.append(name, detail, subtotal); drawerBody?.append(row);
    });
    const total = document.createElement('p'); total.className = 'drawer-total'; total.textContent = `Total: $${Number(data.total).toLocaleString('es-CO')}`;
    if (drawerFooter) drawerFooter.replaceChildren(total, carritoLink());
  } catch { /* El carrito completo sigue disponible en su página. */ }
};
const carritoLink = () => { const link = document.createElement('a'); link.className = 'button button-dark full-width'; link.href = '/carrito/'; link.textContent = 'Ver carrito'; return link; };
const openDrawer = () => { drawer?.classList.add('is-open'); drawer?.setAttribute('aria-hidden','false'); overlay.hidden = false; updateDrawer(); };
const closeDrawer = () => { drawer?.classList.remove('is-open'); drawer?.setAttribute('aria-hidden','true'); overlay.hidden = true; };
document.querySelector('#cartBtn')?.addEventListener('click', (event) => { if (drawer) { event.preventDefault(); openDrawer(); } });
document.querySelector('[data-drawer-close]')?.addEventListener('click', closeDrawer);
overlay?.addEventListener('click', closeDrawer);
document.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeDrawer(); });

document.querySelectorAll('[data-cart-form]').forEach((form) => form.addEventListener('submit', async (event) => {
  event.preventDefault(); const fields = new FormData(form);
  try {
    await post('/api/carrito/agregar/', {product_id:form.dataset.productId, size_id:fields.get('size_id'), quantity:fields.get('quantity') || 1});
    notify('Producto agregado al carrito.'); await updateDrawer(); openDrawer();
  } catch (error) { notify(error.message, true); }
}));
document.querySelectorAll('[data-cart-update]').forEach((form) => form.addEventListener('submit', async (event) => {
  event.preventDefault(); const fields = new FormData(form);
  try { await post('/api/carrito/actualizar/', {size_id:fields.get('size_id'), quantity:fields.get('quantity')}); notify('Cantidad actualizada.'); window.location.reload(); }
  catch (error) { notify(error.message, true); }
}));
document.querySelectorAll('[data-cart-remove]').forEach((form) => form.addEventListener('submit', async (event) => {
  event.preventDefault(); const fields = new FormData(form);
  try { await post('/api/carrito/eliminar/', {size_id:fields.get('size_id')}); notify('Producto eliminado.'); window.location.reload(); }
  catch (error) { notify(error.message, true); }
}));
if (drawer) updateDrawer();
