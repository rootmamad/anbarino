document.addEventListener('DOMContentLoaded', function () {
  const cartContainer = document.querySelector('.cart-container');

  function updateEmptyState() {
    if (document.querySelectorAll('.cart-product-card').length === 0) {
      const msg = document.createElement('p');
      msg.className = 'empty-cart-message';
      msg.textContent = 'سبد خرید شما خالی است.';
      cartContainer.appendChild(msg);
    }
  }



  // دکمه ثبت نهایی
  const submitBtn = document.getElementById('submit-cart');
  if (submitBtn) {
    submitBtn.addEventListener('click', () => {
      const data = [];

      document.querySelectorAll('.cart-product-card').forEach(function (card) {
        const id = card.dataset.productId;
        const quantity = parseInt(card.querySelector('.quantity').textContent);
        data.push({ id, quantity });
      });

      if (data.length === 0) {
        alert("هیچ محصولی در سبد خرید باقی نمانده!");
        return;
      }

      fetch('/cart/submit/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ items: data })
      }).then(res => {
        if (res.ok) alert('خرید با موفقیت ثبت شد!');
        else alert('خطا در ثبت خرید');
      });
    });

  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      document.cookie.split(';').forEach(cookie => {
        const [key, value] = cookie.trim().split('=');
        if (key === name) cookieValue = decodeURIComponent(value);
      });
    }
    return cookieValue;
  }
});
document.querySelectorAll('.cart-product-card').forEach(function (card) {
  const plusBtn = card.querySelector('.btn-plus');
  const minusBtn = card.querySelector('.btn-minus');
  const quantitySpan = card.querySelector('.quantity');
  const quantityInput = card.querySelector('.quantity-input');
  const submitBtn = document.getElementById('submit-cart');

  plusBtn.addEventListener('click', () => {
    let q = parseInt(quantitySpan.textContent);
    q++;
    quantitySpan.textContent = q;
    quantityInput.value = q;
  });

  minusBtn.addEventListener('click', () => {
    let q = parseInt(quantitySpan.textContent);
    const productId = card.dataset.productId;

    if (q > 1) {
      q--;
      quantitySpan.textContent = q;
      quantityInput.value = q;
    } else {
      card.classList.add('removing');
      setTimeout(() => {
        card.remove();
        updateEmptyState();
      }, 400);
      submitBtn.style.display = 'none';

      fetch(`/cart/remove/${productId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        }
      }).then(res => {
        if (!res.ok) {
          alert('خطا در حذف محصول از سبد.');
        }
      });
    }
  });
});
