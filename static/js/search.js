const input = document.querySelector('#searchInput');
const results = document.querySelector('#searchSuggestions');
let debounce;
input?.addEventListener('input', () => {
  clearTimeout(debounce);
  const query = input.value.trim();
  if (query.length < 2) { results.hidden = true; results.replaceChildren(); return; }
  debounce = setTimeout(async () => {
    try {
      const response = await fetch(`/api/buscar/?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      results.replaceChildren();
      data.results.forEach((item) => {
        const link = document.createElement('a'); link.href = item.url;
        const name = document.createElement('span'); name.textContent = item.name;
        const price = document.createElement('small'); price.textContent = `$${Number(item.price).toLocaleString('es-CO')}`;
        link.append(name, price); results.append(link);
      });
      results.hidden = data.results.length === 0;
    } catch { results.hidden = true; }
  }, 250);
});
document.addEventListener('click', (event) => { if (!event.target.closest('.search-wrap')) results && (results.hidden = true); });
