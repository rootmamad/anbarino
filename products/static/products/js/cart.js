// توابع باید اول بیاد
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
function updateCartSummary() {
  let totalPrice = 0;
  let totalQuantity = 0;

  // موجودی واقعی یوزر از data-amount
  const amountText = document.querySelector('.amount-text');
  const userStock = Number(amountText.dataset.amount?.trim() , 0);


  console.log("موجودی واقعی کاربر:", userStock); // نمایش موجودی در کنسول

  document.querySelectorAll('.cart-product-card').forEach(card => {
    const price = parseInt(card.querySelector('.price').textContent.replace(/\D/g, '')) || 0;
    const quantity = parseInt(card.querySelector('.quantity').textContent) || 0;

    totalPrice += price * quantity;
    totalQuantity += quantity;
  });

  const totalPriceEl = document.getElementById('total-price');
  const totalQuantityEl = document.getElementById('total-quantity');
  const submitBtn = document.getElementById('submit-cart');

  totalPriceEl.textContent = totalPrice.toLocaleString();
  totalQuantityEl.textContent = totalQuantity;
   console.log(totalPrice,userStock,typeof(totalQuantity),typeof(userStock))
  if(totalPrice > userStock){
    totalPriceEl.style.color = 'red';
    totalQuantityEl.style.color = 'red';
    submitBtn.disabled = true;
  } else {
    totalPriceEl.style.color = 'green';
    totalQuantityEl.style.color = 'green';
    submitBtn.disabled = false;
  }
}


function updateEmptyState() {
  const cartContainer = document.querySelector('.cart-container');
  if (document.querySelectorAll('.cart-product-card').length === 0) {
    const msg = document.createElement('p');
    msg.className = 'empty-cart-message';
    const path = window.location.pathname;

    if (path.includes('/damaged')) {
      msg.textContent = 'لیست خرابی شما خالی است.';
    } else if (path.includes('/returned')) {
      msg.textContent = 'لیست مرجوعی شما خالی است.';
    } else {
      msg.textContent = 'سبد خرید شما خالی است.';
    }
    cartContainer.appendChild(msg);
  }
}

document.addEventListener('DOMContentLoaded', function () {
  const cartContainer = document.querySelector('.cart-container');
   updateCartSummary();
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
        if (res.ok) console.log("yes");
        else console.log("no");
      });
    });
  }

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
      updateCartSummary();
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

      if (document.querySelectorAll('.cart-product-card').length === 0) {
        submitBtn.style.display = 'none';
      }

    }, 400);

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
  updateCartSummary();
});

  });
});




document.addEventListener("DOMContentLoaded", function() {

  // همه فرم‌های تایید/رد ادمین
  document.querySelectorAll(".inline-form").forEach(form => {
    form.addEventListener("submit", function(e) {
      e.preventDefault();

      const formData = new FormData(this);
      const url = this.getAttribute("action");
      const card = this.closest(".cart-product-card");

      fetch(url, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" }
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === "approved") {
          Swal.fire("تایید شد!", data.message, "success");
          if(card) card.remove();
        } else if (data.status === "rejected") {
          Swal.fire("رد شد!", data.message, "error");
          if(card) card.remove();
        } else {
          Swal.fire("خطا", data.message, "warning");
        }
      })
      .catch(() => {
        Swal.fire("خطا", "ارتباط با سرور برقرار نشد!", "error");
      });
    });
  });

});
