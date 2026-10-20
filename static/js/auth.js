document.querySelectorAll('input[type="password"]').forEach((input) => {
  if (input.dataset.toggleReady) return;
  input.dataset.toggleReady = 'true';
  input.id ||= `password-${Math.random().toString(36).slice(2)}`;
  const button = document.createElement('button');
  button.type = 'button'; button.className = 'password-toggle'; button.textContent = 'Mostrar';
  button.setAttribute('aria-label', 'Mostrar u ocultar contraseña'); button.setAttribute('aria-controls', input.id); button.setAttribute('aria-pressed', 'false');
  input.insertAdjacentElement('afterend', button);
});
document.querySelectorAll('[data-password-toggle], .password-toggle').forEach((button) => {
  button.addEventListener('click', () => {
    const input = document.getElementById(button.getAttribute('aria-controls'));
    if (!input) return;
    input.type = input.type === 'password' ? 'text' : 'password';
    button.setAttribute('aria-pressed', String(input.type === 'text'));
    button.textContent = input.type === 'text' ? 'Ocultar' : 'Mostrar';
  });
});
