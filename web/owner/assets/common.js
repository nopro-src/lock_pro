// owner/assets/common.js
const API_BASE = ""; // same origin
const TOKEN_KEY = "SLFP_OWNER_TOKEN";

function getToken(){ return localStorage.getItem(TOKEN_KEY); }
function setToken(t){ localStorage.setItem(TOKEN_KEY, t); }
function clearToken(){ localStorage.removeItem(TOKEN_KEY); }

function toast(msg, type="info"){
  const box = document.getElementById("toastArea");
  if(!box) return alert(msg);
  const color = type==="success" ? "bg-emerald-600" :
                type==="danger" ? "bg-rose-600" :
                type==="warning"? "bg-amber-600" : "bg-slate-800";
  const el = document.createElement("div");
  el.className = `toast ${color} text-white px-4 py-3 rounded-xl shadow-lg mb-2`;
  el.textContent = msg;
  box.appendChild(el);
  setTimeout(()=> el.remove(), 3200);
}

async function apiFetch(path, opts={}){
  const headers = Object.assign({"Content-Type":"application/json"}, opts.headers||{});
  const token = getToken();
  if(token) headers["Authorization"] = "Bearer " + token;

  const res = await fetch(API_BASE + path, {...opts, headers});
  const ct = res.headers.get("content-type") || "";
  let data = null;
  if(ct.includes("application/json")) data = await res.json();
  else data = await res.text();

  if(!res.ok){
    const msg = (data && data.detail) ? JSON.stringify(data.detail) : (data?.message || res.statusText);
    throw new Error(msg);
  }
  return data;
}

function guardAuth(){
  if(!getToken()) location.href = "/owner/login.html";
}

function setActiveNav(page){
  document.querySelectorAll("[data-nav]").forEach(a=>{
    a.classList.toggle("bg-blue-50", a.dataset.nav===page);
    a.classList.toggle("text-blue-700", a.dataset.nav===page);
  });
}

async function loadMe(){
  const me = await apiFetch("/api/auth/me");
  // Owner-only access
  if(me.global_role !== "OWNER"){
    clearToken();
    location.href = "/owner/login.html";
    return;
  }
  document.querySelectorAll("[data-me]").forEach(el=>{
    const k = el.getAttribute("data-me");
    el.textContent = me[k] ?? "";
  });
  return me;
}