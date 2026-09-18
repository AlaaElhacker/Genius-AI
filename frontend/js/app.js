import { loadLibrary, setupUpload, setScopeChangeHandler } from "./library.js";
import { initChat } from "./chat.js";

const toastContainer = document.getElementById("toastContainer");

window.showToast = function (message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
};

async function bootstrap() {
  setupUpload();
  initChat();
  setScopeChangeHandler(() => {});

  try {
    await loadLibrary();
  } catch (err) {
    showToast("Could not load research library.", "error");
  }
}

bootstrap();
