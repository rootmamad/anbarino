document.getElementById("signupForm").addEventListener("submit", function (e) {
  const form = e.target;
  const fields = form.querySelectorAll(".form-input");
  let valid = true;
  let passwordValue = "";

  fields.forEach((field) => {
    const error = field.nextElementSibling;
    field.classList.remove("invalid");
    error.style.display = "none";

    if (!field.value.trim()) {
      error.textContent = "این فیلد الزامی است.";
      error.style.display = "block";
      field.classList.add("invalid");
      valid = false;
    } else if (field.name === "password") {
      if (field.value.length < 8) {
        error.textContent = "رمز عبور باید حداقل ۸ کاراکتر باشد.";
        error.style.display = "block";
        field.classList.add("invalid");
        valid = false;
      } else {
        passwordValue = field.value;
      }
    } else if (field.name === "confirm_password") {
      if (field.value !== passwordValue) {
        error.textContent = "رمز عبور با تکرار آن مطابقت ندارد.";
        error.style.display = "block";
        field.classList.add("invalid");
        valid = false;
      }
    }
  });

  if (!valid) e.preventDefault();
});
function showPopup(message, type = "success", duration = 3000, callback = null) {
  const popup = document.getElementById("popup-message");
  const text = document.getElementById("popup-text");

  text.textContent = message;
  popup.className = `popup ${type}`; // success یا error
  popup.classList.remove("hidden");

  setTimeout(() => {
    popup.classList.add("hidden");
    if (callback) callback();
  }, duration);
}
