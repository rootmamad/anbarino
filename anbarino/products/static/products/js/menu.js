document.addEventListener('DOMContentLoaded', function () {
  const settings = {
    showDelay: 300,
    hideDelay: 200,
    animationDuration: '0.3s',
    verticalOffset: '10px',
  };

  const userMenu = document.querySelector('.user-menu');
  const userAvatar = document.getElementById('user-avatar');
  const userDropdown = document.querySelector('.user-dropdown');
  const toggleAmount = document.querySelector('.toggle-amount');
  const amountText = document.querySelector('.amount-text');

  let showTimeout, hideTimeout;

  // Initial dropdown style
  if (userDropdown) {
    userDropdown.style.transition = `
      opacity ${settings.animationDuration} ease,
      transform ${settings.animationDuration} ease,
      visibility 0s linear ${settings.animationDuration}
    `;
    userDropdown.style.transform = `translateY(${settings.verticalOffset})`;
  }

  const showMenu = () => {
    clearTimeout(hideTimeout);
    showTimeout = setTimeout(() => {
      userDropdown.style.opacity = '1';
      userDropdown.style.visibility = 'visible';
      userDropdown.style.transform = 'translateY(0)';
      userDropdown.style.transitionDelay = '0s';
    }, settings.showDelay);
  };

  const hideMenu = () => {
    clearTimeout(showTimeout);
    hideTimeout = setTimeout(() => {
      userDropdown.style.opacity = '0';
      userDropdown.style.visibility = 'hidden';
      userDropdown.style.transform = `translateY(${settings.verticalOffset})`;
    }, settings.hideDelay);
  };

  // Hover events
  if (userMenu && userDropdown) {
    userMenu.addEventListener('mouseenter', showMenu);
    userMenu.addEventListener('mouseleave', hideMenu);
    userDropdown.addEventListener('mouseenter', showMenu);
    userDropdown.addEventListener('mouseleave', hideMenu);
  }

  // Toggle "amount" visibility (مثل رمز چشمک‌زن)
  if (toggleAmount && amountText) {
    toggleAmount.addEventListener('click', function () {
      const isHidden = amountText.textContent.includes('•••');

      if (isHidden) {
        const realAmount = amountText.dataset.amount || 'نامشخص';
        amountText.textContent = `موجودی: ${realAmount}`;
        this.innerHTML = '<i class="fas fa-eye-slash"></i>';
      } else {
        amountText.textContent = 'موجودی: •••••';
        this.innerHTML = '<i class="fas fa-eye"></i>';
      }
    });
  }

  // Avatar animation
  if (userAvatar) {
    userAvatar.addEventListener('mouseenter', function () {
      this.style.transform = 'scale(1.1)';
    });

    userAvatar.addEventListener('mouseleave', function () {
      this.style.transform = 'scale(1)';
    });
  }
});
document.addEventListener('DOMContentLoaded', function () {
  const input = document.getElementById('live-search-input');
  const resultsBox = document.getElementById('search-results-box');
  let timeout = null;

  input.addEventListener('input', function () {
    const query = this.value.trim();

    clearTimeout(timeout);
    if (query.length < 2) {
      resultsBox.style.display = 'none';
      return;
    }

    timeout = setTimeout(() => {
      fetch(`/api/reindex/`).then(res => res.json()).then(data => {console.log(data)})

      fetch(`/api/search/?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
          if (data.results.length > 0) {
            resultsBox.innerHTML = '';
            data.results.forEach(item => {
              const div = document.createElement('div');
              div.className = 'search-result-item';
              div.textContent = item.name;
              div.onclick = () => {
                window.location.href = `/product/${item.id}`;
              };
              resultsBox.appendChild(div);
            });
            resultsBox.style.display = 'block';
          } else {
            resultsBox.innerHTML = '<div class="search-result-item">نتیجه‌ای یافت نشد</div>';
            resultsBox.style.display = 'block';
          }
        })
        .catch(err => {
          resultsBox.innerHTML = '<div class="search-result-item">خطا در جستجو</div>';
          resultsBox.style.display = 'block';
        });
    }, 300); // تأخیر ۳۰۰ میلی‌ثانیه
  });

  // وقتی بیرون کلیک بشه، نتایج بسته می‌شن
  document.addEventListener('click', function (e) {
    if (!document.getElementById('live-search-form').contains(e.target)) {
      resultsBox.style.display = 'none';
    }
  });
});


document.querySelectorAll(".slider-wrapper").forEach((wrapper) => {
  let scrollVelocity = 0;
  const friction = 0.92;    // اصطکاک بیشتر برای توقف سریع‌تر
  const maxVelocity = 20;    // حداکثر سرعت کمتر برای اسکرول آهسته‌تر
  const scrollFactor = 0.3;  // کاهش تاثیر چرخ موس

  const animate = () => {
    if (Math.abs(scrollVelocity) > 0.1) {
      wrapper.scrollLeft += scrollVelocity;
      scrollVelocity *= friction;
      requestAnimationFrame(animate);
    }
  };

  wrapper.addEventListener("wheel", (e) => {
    e.preventDefault();

    scrollVelocity += e.deltaY * scrollFactor;

    // محدود کردن سرعت
    if (scrollVelocity > maxVelocity) scrollVelocity = maxVelocity;
    if (scrollVelocity < -maxVelocity) scrollVelocity = -maxVelocity;

    requestAnimationFrame(animate);
  }, { passive: false });
});