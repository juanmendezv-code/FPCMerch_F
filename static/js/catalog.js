const range = document.querySelector('#priceRange');
const output = document.querySelector('#priceOutput');
range?.addEventListener('input', () => { output.textContent = `$${Number(range.value).toLocaleString('es-CO')}`; });
document.querySelector('[data-filter-toggle]')?.addEventListener('click', () => document.querySelector('[data-filter-panel]')?.classList.toggle('is-open'));
