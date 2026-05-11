document.addEventListener('DOMContentLoaded', function () {
  const input = document.querySelector('.search-input');
  const resultsGrid = document.querySelector('.results-grid');

  if (!input || !resultsGrid) return;

  let timeout = null;

  input.addEventListener('input', function () {
    const query = this.value.trim();
    clearTimeout(timeout);

    if (query.length < 2) {
      resultsGrid.innerHTML = ''; // پاک کردن نتایج
      return;
    }

    timeout = setTimeout(() => {
      fetch(`/api/search/?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
          // انیمیشن محو شدن قبل از آپدیت
          resultsGrid.style.transition = 'opacity 0.2s ease';
          resultsGrid.style.opacity = 0;

          setTimeout(() => {
            resultsGrid.innerHTML = '';
            if (data.results && data.results.length > 0) {
              data.results.forEach(product => {
                const card = document.createElement('div');
                card.className = 'product-card';
                card.innerHTML = `
                  <div class="image-wrapper">
                    <img src="${product.image.url || '/static/products/images/placeholder.png'}" alt="${product.name}">
                  </div>
                  <div class="card-body">
                    <h5 class="product-title">${product.name}</h5>
                    ${product.price ? `<p class="product-price">💰 ${product.price} تومان</p>` : ''}
                    ${product.quantity ? `<p class="product-qty">📦 موجودی: ${product.quantity}</p>` : ''}
                    <a href="/product/${product.id}/" class="view-btn">مشاهده محصول</a>
                  </div>
                `;
                resultsGrid.appendChild(card);
              });
            } else {
              resultsGrid.innerHTML = '<p class="no-results">هیچ محصولی یافت نشد 😢</p>';
            }
            // انیمیشن ظاهر شدن
            resultsGrid.style.opacity = 1;
          }, 200); // 200ms فاصله برای محو شدن
        })
        .catch(err => console.error(err));
    }, 300);
  });
});
