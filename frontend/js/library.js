import {
  fetchDocuments,
  uploadDocument,
  deleteDocument,
  getDocumentFileUrl,
} from "./api.js";

const documentList = document.getElementById("documentList");
const scopeOptions = document.getElementById("scopeOptions");
const docCount = document.getElementById("docCount");
const uploadZone = document.getElementById("uploadZone");
const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const uploadProgress = document.getElementById("uploadProgress");

let documents = [];
let selectedScope = "";
let onScopeChange = null;

export function getSelectedScope() {
  return selectedScope;
}

export function setScopeChangeHandler(handler) {
  onScopeChange = handler;
}

export async function loadLibrary() {
  documents = await fetchDocuments();
  renderLibrary();
}

function renderLibrary() {
  docCount.textContent = `${documents.length} paper${documents.length !== 1 ? "s" : ""}`;

  if (documents.length === 0) {
    documentList.innerHTML = `<div class="empty-library">No papers yet. Upload a PDF to begin.</div>`;
    scopeOptions.innerHTML = "";
    return;
  }

  documentList.innerHTML = documents
    .map(
      (doc) => `
    <div class="doc-card" data-id="${doc.document_id}">
      <div class="doc-card-header">
        <span class="doc-icon">📄</span>
        <span class="doc-card-title">${escapeHtml(doc.file_name.replace(/_/g, " ").replace(".pdf", ""))}</span>
      </div>
      <div class="doc-card-meta">
        <span>${doc.page_count} pages</span>
        <span class="indexed">Indexed ✓</span>
      </div>
      <div class="doc-card-actions">
        <button class="btn-chat" data-action="chat" data-id="${doc.document_id}">Chat</button>
        <button class="btn-delete" data-action="delete" data-id="${doc.document_id}">Delete</button>
      </div>
    </div>
  `
    )
    .join("");

  scopeOptions.innerHTML = documents
    .map(
      (doc) => `
    <label class="scope-option">
      <input type="radio" name="scope" value="${doc.document_id}" ${selectedScope === doc.document_id ? "checked" : ""}>
      <span>${escapeHtml(doc.file_name.replace(/_/g, " ").replace(".pdf", ""))}</span>
    </label>
  `
    )
    .join("");

  bindEvents();
}

function bindEvents() {
  documentList.querySelectorAll("[data-action]").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      const id = e.currentTarget.dataset.id;
      const action = e.currentTarget.dataset.action;

      if (action === "chat") {
        selectScope(id);
      } else if (action === "delete") {
        if (confirm("Remove this paper from your research library?")) {
          await handleDelete(id);
        }
      }
    });
  });

  document.querySelectorAll('input[name="scope"]').forEach((radio) => {
    radio.addEventListener("change", (e) => {
      selectedScope = e.target.value;
      onScopeChange?.(selectedScope);
    });
  });
}

function selectScope(documentId) {
  selectedScope = documentId;
  const radio = document.querySelector(`input[name="scope"][value="${documentId}"]`);
  if (radio) radio.checked = true;
  onScopeChange?.(selectedScope);
}

async function handleDelete(documentId) {
  try {
    await deleteDocument(documentId);
    if (selectedScope === documentId) {
      selectedScope = "";
      const allRadio = document.querySelector('input[name="scope"][value=""]');
      if (allRadio) allRadio.checked = true;
    }
    await loadLibrary();
    window.showToast?.("Document removed.", "success");
  } catch (err) {
    window.showToast?.(err.message, "error");
  }
}

function setupUpload() {
  browseBtn.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length) handleFile(fileInput.files[0]);
  });

  uploadZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadZone.classList.add("drag-over");
  });

  uploadZone.addEventListener("dragleave", () => {
    uploadZone.classList.remove("drag-over");
  });

  uploadZone.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadZone.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });
}

async function handleFile(file) {
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    window.showToast?.("Please upload a PDF file.", "error");
    return;
  }

  const uploadContent = uploadZone.querySelector(".upload-content");
  uploadContent.classList.add("hidden");
  uploadProgress.classList.remove("hidden");

  const steps = uploadProgress.querySelectorAll(".progress-step");
  steps.forEach((s) => s.classList.remove("active", "done"));

  try {
    const result = await uploadDocument(file, (step) => {
      steps.forEach((s) => {
        const sStep = s.dataset.step;
        s.classList.remove("active");
        if (sStep === step) s.classList.add("active");
        const stepOrder = ["upload", "read", "extract", "chunk", "embed", "index", "done"];
        if (stepOrder.indexOf(sStep) < stepOrder.indexOf(step)) {
          s.classList.add("done");
        }
      });
    });

    window.showToast?.(result.message || "Paper indexed successfully.", "success");
    await loadLibrary();
  } catch (err) {
    window.showToast?.(err.message, "error");
  } finally {
    uploadContent.classList.remove("hidden");
    uploadProgress.classList.add("hidden");
    fileInput.value = "";
    steps.forEach((s) => s.classList.remove("active", "done"));
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

export { getDocumentFileUrl, setupUpload };
