var toastEl = document.getElementById("toast");
var toastBodyEl = toastEl.querySelector(".toast-body");

function showToast(message, type) {
  // Update background color class based on type
  toastEl.classList.remove("bg-primary", "bg-warning", "bg-danger");
  if (type === "success") {
    toastEl.classList.add("bg-success");
  } else if (type === "warning") {
    toastEl.classList.add("bg-warning");
  } else if (type === "error") {
    toastEl.classList.add("bg-danger");
  }

  toastBodyEl.innerHTML = message;
  var toast = new bootstrap.Toast(toastEl);
  toast.show();
}
