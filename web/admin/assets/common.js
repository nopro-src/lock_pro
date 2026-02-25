const API_BASE = ""; // same origin

function getToken(){ return localStorage.getItem("access_token"); }
function setToken(t){ localStorage.setItem("access_token", t); }
function clearToken(){ localStorage.removeItem("access_token"); }

function authHeaders(){
  const t = getToken();
  return t ? { "Authorization": "Bearer " + t } : {};
}

async function apiFetch(path, opts={}){
  const headers = Object.assign(
    { "Content-Type": "application/json" },
    opts.headers || {},
    authHeaders()
  );
  const res = await fetch(API_BASE + path, Object.assign({}, opts, { headers }));
  if(res.status === 401){
    clearToken();
    if(!location.pathname.endsWith("/login.html")) location.href = "/admin/login.html";
  }
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch(e){ data = { raw: text }; }
  if(!res.ok){
    const msg = (data && data.detail) ? data.detail : ("HTTP " + res.status);
    throw new Error(msg);
  }
  return data;
}

function toast(msg, type="info"){
  const el = document.getElementById("toastArea");
  if(!el) return alert(msg);

  const id = "t" + Math.random().toString(16).slice(2);
  const html = `
  <div id="${id}" class="toast align-items-center text-bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
    <div class="d-flex">
      <div class="toast-body">${msg}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  </div>`;
  el.insertAdjacentHTML("beforeend", html);
  const toastEl = document.getElementById(id);
  const t = new bootstrap.Toast(toastEl, { delay: 2800 });
  t.show();
  toastEl.addEventListener("hidden.bs.toast", ()=> toastEl.remove());
}

function guardAuth(){
  if(!getToken() && !location.pathname.endsWith("/login.html")){
    location.href = "/admin/login.html";
  }
}

function setActiveNav(page){
  document.querySelectorAll(".sidebar .nav-link").forEach(a=>{
    if(a.getAttribute("data-page") === page) a.classList.add("active");
  });
}