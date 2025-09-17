document.getElementById("loginForm").addEventListener("submit", function (e) {
  const form = e.target;
  const fields = form.querySelectorAll(".form-input");
  let valid = true;

  fields.forEach((field) => {
    const error = field.nextElementSibling;
    field.classList.remove("invalid");
    error.style.display = "none";

    if (!field.value.trim()) {
      error.textContent = "این فیلد الزامی است.";
      error.style.display = "block";
      field.classList.add("invalid");
      valid = false;
    }
  });

  if (!valid) e.preventDefault();
});

function showPopup(message, type = "success", duration = 3000, callback = null) {
  const popup = document.getElementById("popup-message");
  const text = document.getElementById("popup-text");

  text.textContent = message;
  popup.className = `popup ${type}`;
  popup.classList.remove("hidden");

  setTimeout(() => {
    popup.classList.add("hidden");
    if (callback) callback();
  }, duration);
}
