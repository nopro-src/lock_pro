const API_BASE = "";
const TOKEN_KEY = "SLFP_USER_TOKEN";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(t) {
  localStorage.setItem(TOKEN_KEY, t);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function toast(msg, type = "info") {
  const box = document.getElementById("toastArea");
  if (!box) return alert(msg);

  const color =
    type === "success"
      ? "bg-emerald-600"
      : type === "danger"
      ? "bg-rose-600"
      : type === "warning"
      ? "bg-amber-500 text-slate-900"
      : "bg-slate-800";

  const el = document.createElement("div");
  el.className = `toast ${color} px-4 py-3 rounded-2xl shadow-lg border border-white/10 text-white`;
  el.textContent = msg;

  if (type === "warning") {
    el.classList.remove("text-white");
  }

  box.appendChild(el);

  setTimeout(() => {
    el.classList.add("opacity-0", "translate-y-2");
    setTimeout(() => el.remove(), 250);
  }, 3000);
}

async function apiFetch(path, opts = {}) {
  const headers = Object.assign(
    { "Content-Type": "application/json" },
    opts.headers || {}
  );

  const token = getToken();
  if (token) {
    headers["Authorization"] = "Bearer " + token;
  }

  const res = await fetch(API_BASE + path, { ...opts, headers });
  const ct = res.headers.get("content-type") || "";

  let data = null;
  if (ct.includes("application/json")) data = await res.json();
  else data = await res.text();

  if (!res.ok) {
    const msg =
      data && data.detail
        ? JSON.stringify(data.detail)
        : data?.message || res.statusText;
    throw new Error(msg);
  }

  return data;
}

function guardAuth() {
  if (!getToken()) {
    location.href = "/user/login.html";
  }
}

async function loadMe() {
  const me = await apiFetch("/api/auth/me");

  if (me.global_role !== "USER") {
    clearToken();
    location.href = "/user/login.html";
    return;
  }

  document.querySelectorAll("[data-me]").forEach((el) => {
    const k = el.getAttribute("data-me");
    el.textContent = me[k] ?? "";
  });

  return me;
}