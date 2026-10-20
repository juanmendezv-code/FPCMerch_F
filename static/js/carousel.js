const carousel = document.querySelector('#heroCarousel');
if (carousel) {
  const slides = [...carousel.querySelectorAll('.hero-slide')];
  const dots = carousel.querySelector('#carouselDots');
  let current = 0;
  let timer;
  const show = (index) => {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, position) => slide.classList.toggle('is-active', position === current));
    dots.querySelectorAll('button').forEach((button, position) => button.setAttribute('aria-current', String(position === current)));
  };
  slides.forEach((_, index) => {
    const dot = document.createElement('button');
    dot.type = 'button'; dot.setAttribute('aria-label', `Mostrar diapositiva ${index + 1}`);
    dot.addEventListener('click', () => { show(index); restart(); }); dots.append(dot);
  });
  const next = () => show(current + 1);
  const restart = () => { clearInterval(timer); timer = setInterval(next, 6000); };
  carousel.querySelector('[data-carousel-prev]').addEventListener('click', () => { show(current - 1); restart(); });
  carousel.querySelector('[data-carousel-next]').addEventListener('click', () => { next(); restart(); });
  carousel.addEventListener('mouseenter', () => clearInterval(timer));
  carousel.addEventListener('mouseleave', restart);
  show(0); restart();
}
