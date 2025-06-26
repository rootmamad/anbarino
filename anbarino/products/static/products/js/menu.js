document.addEventListener('DOMContentLoaded', function() {
  // تنظیمات قابل تغییر
  const settings = {
    showDelay: 300,    // تاخیر قبل از نمایش منو (میلی‌ثانیه)
    hideDelay: 200,    // تاخیر قبل از پنهان شدن منو (میلی‌ثانیه)
    animationDuration: '0.3s', // مدت زمان انیمیشن
    verticalOffset: '10px' // میزان جابجایی عمودی هنگام نمایش/پنهان شدن
  };

  // انتخاب عناصر DOM
  const userMenu = document.querySelector('.user-menu');
  const userAvatar = document.getElementById('user-avatar');
  const userDropdown = document.querySelector('.user-dropdown');
  const togglePassword = document.querySelector('.toggle-password');
  const passwordText = document.querySelector('.password-text');

  // متغیرهای زمان‌سنج
  let showTimeout, hideTimeout;

  // تنظیم استایل اولیه منو
  userDropdown.style.transition = `
    opacity ${settings.animationDuration} ease,
    transform ${settings.animationDuration} ease,
    visibility 0s linear ${settings.animationDuration}
  `;
  userDropdown.style.transform = `translateY(${settings.verticalOffset})`;

  // نمایش منو با تاخیر
  const showMenu = () => {
    clearTimeout(hideTimeout);
    showTimeout = setTimeout(() => {
      userDropdown.style.opacity = '1';
      userDropdown.style.visibility = 'visible';
      userDropdown.style.transform = 'translateY(0)';
      userDropdown.style.transitionDelay = '0s';
    }, settings.showDelay);
  };

  // پنهان کردن منو با تاخیر
  const hideMenu = () => {
    clearTimeout(showTimeout);
    hideTimeout = setTimeout(() => {
      userDropdown.style.opacity = '0';
      userDropdown.style.visibility = 'hidden';
      userDropdown.style.transform = `translateY(${settings.verticalOffset})`;
    }, settings.hideDelay);
  };

  // رویدادهای ماوس برای منو
  userMenu.addEventListener('mouseenter', showMenu);
  userMenu.addEventListener('mouseleave', hideMenu);
  userDropdown.addEventListener('mouseenter', showMenu);
  userDropdown.addEventListener('mouseleave', hideMenu);

  // مدیریت نمایش رمز (نمایش محدود شده)
  if (togglePassword && passwordText) {
    togglePassword.addEventListener('click', function() {
      const isHidden = passwordText.textContent.includes('••••••');

      if (isHidden) {
        // نمایش نمونه محدود شده (4 کاراکتر آخر)
        const hashedPass = "{{ user.password }}";
        const shortPass = hashedPass.length > 4 ? '...' + hashedPass.slice(-4) : hashedPass;
        passwordText.textContent = `رمز: ${shortPass}`;
        this.innerHTML = '<i class="fas fa-eye-slash"></i>';
      } else {
        passwordText.textContent = 'رمز: ••••••';
        this.innerHTML = '<i class="fas fa-eye"></i>';
      }
    });
  }

  // افکت hover برای آواتار کاربر
  if (userAvatar) {
    userAvatar.addEventListener('mouseenter', function() {
      this.style.transform = 'scale(1.1)';
    });

    userAvatar.addEventListener('mouseleave', function() {
      this.style.transform = 'scale(1)';
    });
  }
});

// تابع کمکی برای مدیریت تاخیرها
function debounce(func, delay) {
  let timeoutId;
  return function() {
    const context = this;
    const args = arguments;
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      func.apply(context, args);
    }, delay);
  };

}