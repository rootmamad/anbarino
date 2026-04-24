document.getElementById("resetForm").addEventListener("submit", function (e) {
  const form = e.target;
  let valid = true;

  // بررسی اینکه کدوم مرحله است
  const usernameField = form.querySelector("input[name='username']");
  const emailField = form.querySelector("input[name='email']");
  const passwordField = form.querySelector("input[name='password']");
  const confirmField = form.querySelector("input[name='confirm_password']");

  // همه error-message ها رو مخفی کن
  form.querySelectorAll(".error-message").forEach(em => {
    em.style.display = "none";
  });
  form.querySelectorAll(".form-input").forEach(f => {
    f.classList.remove("invalid");
  });

  // مرحله اول: فقط نام کاربری و ایمیل چک میشه
  if (passwordField === null && confirmField === null) {
    [usernameField, emailField].forEach(field => {
      const error = field.nextElementSibling;
      if (!field.value.trim()) {
        error.textContent = "این فیلد الزامی است.";
        error.style.display = "block";
        field.classList.add("invalid");
        valid = false;
      } else if (field.name === "email") {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(field.value)) {
          error.textContent = "ایمیل معتبر وارد کنید.";
          error.style.display = "block";
          field.classList.add("invalid");
          valid = false;
        }
      }
    });
  } else {
    // مرحله دوم: ولیدیشن رمز جدید و تکرارش
    if (!passwordField.value.trim()) {
      const error = passwordField.nextElementSibling;
      error.textContent = "این فیلد الزامی است.";
      error.style.display = "block";
      passwordField.classList.add("invalid");
      valid = false;
    } else if (passwordField.value.length < 8) {
      const error = passwordField.nextElementSibling;
      error.textContent = "رمز عبور باید حداقل ۸ کاراکتر باشد.";
      error.style.display = "block";
      passwordField.classList.add("invalid");
      valid = false;
    }

    if (confirmField.value !== passwordField.value) {
      const error = confirmField.nextElementSibling;
      error.textContent = "رمز عبور با تکرار آن مطابقت ندارد.";
      error.style.display = "block";
      confirmField.classList.add("invalid");
      valid = false;
    }
  }

  if (!valid) e.preventDefault();
});
