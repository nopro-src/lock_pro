let ws = null;
const MAX_EVENTS = 50;

function wsConnect(lockId) {
  const token = getToken();
  if (!token) return;

  if (ws && (ws.readyState === WebSocket.CONNECTING || ws.readyState === WebSocket.OPEN)) {
    ws.close();
  }

  ensureRealtimeEmptyState();

  ws = new WebSocket(
    `${location.origin.replace("http", "ws")}/ws?token=${encodeURIComponent(token)}`
  );

  ws.onopen = () => {
    ws.send(JSON.stringify({ action: "join", lock_id: lockId }));
    addEvent("INFO", { msg: `connected, joining lock ${lockId}` });
  };

  ws.onmessage = (ev) => {
    try {
      const e = JSON.parse(ev.data);
      addEvent((e.type || "INFO").toUpperCase(), e.payload || e);
    } catch (_) {
      addEvent("INFO", { raw: ev.data });
    }
  };

  ws.onerror = () => {
    addEvent("ERROR", { msg: "websocket error" });
  };

  ws.onclose = () => {
    addEvent("ERROR", { msg: "ws closed" });
  };
}

function addEvent(type, payload) {
  const panel = document.getElementById("realtimePanel");
  if (!panel) return;

  removeRealtimeEmptyState();

  const styles = getEventStyle(type);
  const t = new Date().toLocaleTimeString("vi-VN");

  const item = document.createElement("div");
  item.className =
    `rounded-2xl border border-slate-200 border-l-4 ${styles.leftBorder} bg-white px-4 py-3 shadow-sm`;

  item.innerHTML = `
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${styles.badge}">
          ${escapeHtml(type)}
        </span>
        <span class="text-xs text-slate-400">${t}</span>
      </div>
    </div>

    <pre class="mt-3 rounded-xl bg-slate-50 border border-slate-200 p-3 text-xs leading-6 text-slate-700 whitespace-pre-wrap break-words overflow-x-auto">${escapeHtml(
      JSON.stringify(payload, null, 2)
    )}</pre>
  `;

  panel.prepend(item);
  trimEvents(panel);
}

function getEventStyle(type) {
  switch (type) {
    case "ERROR":
      return {
        badge: "bg-rose-100 text-rose-700 border-rose-200",
        leftBorder: "border-l-rose-400"
      };
    case "VERIFY":
      return {
        badge: "bg-emerald-100 text-emerald-700 border-emerald-200",
        leftBorder: "border-l-emerald-400"
      };
    case "ENROLL":
      return {
        badge: "bg-blue-100 text-blue-700 border-blue-200",
        leftBorder: "border-l-blue-400"
      };
    case "WARNING":
      return {
        badge: "bg-amber-100 text-amber-700 border-amber-200",
        leftBorder: "border-l-amber-400"
      };
    case "INFO":
    default:
      return {
        badge: "bg-slate-100 text-slate-700 border-slate-200",
        leftBorder: "border-l-slate-300"
      };
  }
}

function ensureRealtimeEmptyState() {
  const panel = document.getElementById("realtimePanel");
  if (!panel) return;
  if (panel.children.length > 0) return;

  panel.innerHTML = `
    <div data-empty="true" class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500">
      Waiting for live events...
    </div>
  `;
}

function removeRealtimeEmptyState() {
  const panel = document.getElementById("realtimePanel");
  if (!panel) return;
  const empty = panel.querySelector("[data-empty='true']");
  if (empty) empty.remove();
}

function trimEvents(panel) {
  while (panel.children.length > MAX_EVENTS) {
    panel.removeChild(panel.lastElementChild);
  }
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (m) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  }[m]));
}