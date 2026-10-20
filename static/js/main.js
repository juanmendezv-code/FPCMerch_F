const menuButton = document.querySelector('[data-menu-toggle]');
const mainNav = document.querySelector('[data-main-nav]');
menuButton?.addEventListener('click', () => {
  const opened = mainNav.classList.toggle('is-open');
  menuButton.setAttribute('aria-expanded', String(opened));
});

document.querySelectorAll('.toast').forEach((toast) => {
  window.setTimeout(() => toast.remove(), 4500);
});
