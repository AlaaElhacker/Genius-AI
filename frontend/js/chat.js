import { sendChat } from "./api.js";
import { getDocumentFileUrl, getSelectedScope } from "./library.js";
import { marked } from "https://esm.run/marked@9";
import DOMPurify from "https://esm.run/dompurify@3";

const chatMessages = document.getElementById("chatMessages");
const welcomeScreen = document.getElementById("welcomeScreen");
const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");

let messages = [];
let isSending = false;

export function initChat() {
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    await handleSend();
  });

  questionInput.addEventListener("input", () => {
    questionInput.style.height = "auto";
    questionInput.style.height = Math.min(questionInput.scrollHeight, 120) + "px";
    sendBtn.disabled = !questionInput.value.trim() || isSending;
  });

  questionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!sendBtn.disabled) handleSend();
    }
  });
}

async function handleSend() {
  const question = questionInput.value.trim();
  if (!question || isSending) return;

  isSending = true;
  sendBtn.disabled = true;
  questionInput.value = "";
  questionInput.style.height = "auto";

  hideWelcome();
  appendMessage("user", question);
  messages.push({ role: "user", content: question });

  const typingEl = showTyping();

  try {
    const scope = getSelectedScope();
    const response = await sendChat(question, scope || null, messages.slice(0, -1));

    typingEl.remove();
    appendMessage("assistant", response.answer, response.sources);
    messages.push({ role: "assistant", content: response.answer });
  } catch (err) {
    typingEl.remove();
    appendMessage("assistant", `Sorry, something went wrong: ${err.message}`);
  } finally {
    isSending = false;
    sendBtn.disabled = !questionInput.value.trim();
  }
}

function hideWelcome() {
  if (welcomeScreen) welcomeScreen.classList.add("hidden");
}

function appendMessage(role, content, sources = []) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const label = role === "user" ? "You" : "MedicalResearch AI";
  let sourcesHtml = "";

  if (sources && sources.length > 0) {
    sourcesHtml = `
      <div class="sources-block">
        <div class="sources-title">Sources</div>
        ${sources
          .map(
            (s) => `
          <a class="source-card" href="${getDocumentFileUrl(s.document_id)}#page=${s.page || 1}" target="_blank" rel="noopener">
            📄 ${escapeHtml(formatFileName(s.file_name))}${s.page ? ` · <span class="page">p.${s.page}</span>` : ""}
          </a>
        `
          )
          .join("")}
      </div>
    `;
  }

  wrapper.innerHTML = `
    <div class="message-label">${label}</div>
    <div class="message-bubble">${role === "assistant" ? renderAssistantContent(content) : escapeHtml(content)}${sourcesHtml}</div>
  `;

  chatMessages.appendChild(wrapper);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTyping() {
  const el = document.createElement("div");
  el.className = "message assistant";
  el.innerHTML = `
    <div class="message-label">MedicalResearch AI</div>
    <div class="message-bubble">
      <div class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    </div>
  `;
  chatMessages.appendChild(el);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return el;
}

function formatFileName(name) {
  return name.replace(/_/g, " ").replace(/\.pdf$/i, "");
}
function renderAssistantContent(content) {
  try {
    return DOMPurify.sanitize(marked.parse(content));
  } catch (e) {
    console.error("Markdown render failed:", e);
    return escapeHtml(content);
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

export function clearChat() {
  messages = [];
  chatMessages.innerHTML = "";
  if (welcomeScreen) {
    welcomeScreen.classList.remove("hidden");
    chatMessages.appendChild(welcomeScreen);
  }
}
