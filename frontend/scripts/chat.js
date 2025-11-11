import ApiService from "../services/apiService.js";

const AgentName = "techai_agent";
let activeSessionId = null;
let currentFile = null;
// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  initChat();
});

function initChat() {
  const newSessionButton = document.getElementById("new-session");
  newSessionButton.addEventListener("click", createSession);
  listSessions();
}

// DOM elements
const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const fileInput = document.getElementById("file-input");
const uploadList = document.getElementById("upload-list");
const sessionsListWrapper = document.getElementById("sessions-list");

const filePreview = document.createElement("div");
filePreview.className = "file-preview";
form.insertBefore(filePreview, form.firstChild);




// --- Sessions ---
async function listSessions() {
  try {
    const sessions = await ApiService.get(`/apps/${AgentName}/users/user/sessions`);
    sessionsListWrapper.innerHTML = "";

    if (!sessions.length) return;

    // Render all sessions
    sessions.forEach((s) => createSessionElement(s.id));

    // Load first session by default if none active
    if (!activeSessionId) {
      await updateActiveSession(sessions[0].id);
    }
  } catch (err) {
    console.error("Failed to list sessions:", err);
  }
}

function createSessionElement(id) {
  const li = document.createElement("li");
  li.id = `id-${id}`;
  li.className = "session-item";

  const spanEl = document.createElement("span");
  spanEl.textContent = id;

  const deleteIcon = document.createElement("i");
  deleteIcon.className = "fa fa-trash delete-session";
  deleteIcon.onclick = (e) => deleteSession(e, id);

  li.appendChild(spanEl);
  li.appendChild(deleteIcon);
  li.onclick = () => updateActiveSession(id);

  sessionsListWrapper.appendChild(li);

  // Automatically select first session if none active
  if (!activeSessionId) {
    activeSessionId = id;
    li.classList.add("active");
    updateActiveSession(id);
  }
}

async function createSession() {
  try {
    const session = await ApiService.post(`/apps/${AgentName}/users/user/sessions`);
    createSessionElement(session.id);
    await updateActiveSession(session.id);
  } catch (err) {
    console.error("Failed to create session:", err);
  }
}

async function deleteSession(event, id) {
  event.stopPropagation();
  try {
    await ApiService.delete(`/apps/${AgentName}/users/user/sessions/${id}`);
    const sessionEl = document.getElementById(`id-${id}`);
    if (!sessionEl) return;

    const wasActive = sessionEl.classList.contains("active");
    sessionEl.remove();

    if (wasActive) {
      const firstSession = document.querySelector(".session-item");
      if (firstSession) await updateActiveSession(firstSession.id.replace("id-", ""));
    }
  } catch (err) {
    console.error("Failed to delete session:", err);
  }
}

async function updateActiveSession(id) {
  try {
    const sessionResponse = await ApiService.get(`/apps/${AgentName}/users/user/sessions/${id}`);
    activeSessionId = id;

    document.querySelectorAll(".session-item").forEach((el) => el.classList.remove("active"));
    const activeEl = document.getElementById(`id-${id}`);
    if (activeEl) activeEl.classList.add("active");

    messagesEl.innerHTML = "";
    renderEvents(sessionResponse.events || []);
  } catch (err) {
    console.error("Failed to update active session:", err);
  }
}

// --- Messages ---
function renderEvents(events) {
  events.forEach((event) => {
    if (event.content) appendMessage(event.content, event.content.role);
  });
}

function appendMessage(content, who = "model") {
  const el = document.createElement("div");

  if (content.parts) {
    content.parts.forEach((part) => {
      if (part.functionResponse) {
        el.className = "message model function";
        el.innerHTML = `<i class="fa fa-check"></i> ${part.functionResponse.name}`;
      } else {
        el.className = `message ${who}`;
        if (part.text) el.innerHTML = marked.parse(part.text);
        if (part.functionCall) el.classList.add("function");
        if (part.functionCall) el.innerHTML = `<i class="fa fa-bolt"></i> ${part.functionCall.name}`;
        if (part.inlineData) {
          const mediaEl = createMediaElement(part.inlineData);
          if (mediaEl) el.appendChild(mediaEl);
        }
      }
    });
  }

  messagesEl.appendChild(el);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

// --- Media ---
function createMediaElement({ data, mimeType, displayName }) {
  const wrapper = document.createElement("div");
  wrapper.className = "message-media";
  const base64Data = data.replace(/_/g, "/").replace(/-/g, "+");

  if (mimeType.startsWith("image/")) {
    const img = document.createElement("img");
    img.src = `data:${mimeType};base64,${base64Data}`;
    img.alt = displayName;
    img.loading = "lazy";
    wrapper.appendChild(img);
  } else {
    const link = document.createElement("a");
    link.href = `data:${mimeType};base64,${base64Data}`;
    link.download = displayName;
    link.innerHTML = `<i class="fa fa-download"></i> ${displayName}`;
    wrapper.appendChild(link);
  }

  return wrapper;
}

// --- Sending Messages ---
function setSending(isSending) {
  sendBtn.disabled = isSending;
  input.disabled = isSending;
}

async function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () =>
      resolve({ data: reader.result.split(",")[1], displayName: file.name, mimeType: file.type });
    reader.onerror = reject;
  });
}

function showFilePreview(file) {
  filePreview.innerHTML = "";
  if (!file) return;

  const wrapper = document.createElement("div");
  wrapper.className = "preview-wrapper";

  if (file.type.startsWith("image/")) {
    const img = document.createElement("img");
    img.className = "message-media preview";
    const reader = new FileReader();
    reader.onload = (e) => (img.src = e.target.result);
    reader.readAsDataURL(file);
    wrapper.appendChild(img);
  } else {
    const fileInfo = document.createElement("div");
    fileInfo.className = "file-info";
    fileInfo.innerHTML = `<i class="fa fa-file"></i> ${file.name}`;
    wrapper.appendChild(fileInfo);
  }

  const removeBtn = document.createElement("button");
  removeBtn.className = "remove-preview";
  removeBtn.innerHTML = '<i class="fa fa-times"></i>';
  removeBtn.onclick = clearFilePreview;
  wrapper.appendChild(removeBtn);

  filePreview.appendChild(wrapper);
}

function clearFilePreview() {
  filePreview.innerHTML = "";
  currentFile = null;
  fileInput.value = "";
}

async function sendMessage(text, attachedFile = null) {
  if (!text && !attachedFile) return;
  if (!activeSessionId) {
    console.warn("No active session selected yet. Message will not be sent.");
    return;
  }

  setSending(true);

  const parts = [];
  if (text) parts.push({ text });
  if (attachedFile) parts.push({ inlineData: await fileToBase64(attachedFile) });

  appendMessage({ parts }, "user");
  clearFilePreview();

  const payload = {
    appName: AgentName,
    newMessage: { role: "user", parts },
    sessionId: activeSessionId,
    stateDelta: null,
    streaming: false, // ✅ enable streaming
    userId: "user",
  };

  try {
    await ApiService.postWithStream("/run_sse", payload, (chunk) => {
      if (chunk && typeof chunk === "object") {
      appendMessage(chunk.content, "model");
      messagesEl.scrollTop = messagesEl.scrollHeight;
      }
    });
  } catch (err) {
    console.error("Chat error:", err);
  } finally {
    setSending(false);
  }
}

// --- Event Listeners ---
fileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (file) {
    currentFile = file;
    showFilePreview(file);
  }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  input.value = "";
  await sendMessage(text, currentFile);
});
