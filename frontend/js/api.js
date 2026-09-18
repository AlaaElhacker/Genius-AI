const API_BASE = "";

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || "Request failed.");
  }

  return data;
}

export async function fetchDocuments() {
  const data = await apiRequest("/documents");
  return data.documents || [];
}

export async function uploadDocument(file, onProgress) {
  const steps = ["upload", "read", "extract", "chunk", "embed", "index", "done"];
  let stepIndex = 0;

  const progressInterval = setInterval(() => {
    if (stepIndex < steps.length - 1) {
      onProgress?.(steps[stepIndex]);
      stepIndex++;
    }
  }, 600);

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE}/documents/upload`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Upload failed.");
    }

    onProgress?.("done");
    return data;
  } finally {
    clearInterval(progressInterval);
  }
}

export async function deleteDocument(documentId) {
  return apiRequest(`/documents/${documentId}`, { method: "DELETE" });
}

export async function sendChat(question, documentId, history) {
  return apiRequest("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      document_id: documentId || null,
      history,
    }),
  });
}

export function getDocumentFileUrl(documentId) {
  return `${API_BASE}/documents/${documentId}/file`;
}
