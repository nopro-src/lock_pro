const API = "/api";
let token = localStorage.getItem("token") || "";
let stream = null;
let ws = null;

const $ = (id) => document.getElementById(id);

function setAuthUI(loggedIn){
  $("authCard").style.display = loggedIn ? "none" : "block";
  $("logoutBtn").style.display = loggedIn ? "inline-block" : "none";
}

async function apiFetch(path, options={}){
  const headers = options.headers || {};
  headers["Content-Type"] = "application/json";
  if(token) headers["Authorization"] = "Bearer " + token;
  const res = await fetch(API + path, { ...options, headers });
  if(!res.ok){
    const txt = await res.text();
    throw new Error(txt || res.statusText);
  }
  return res.json();
}

async function me(){
  const data = await apiFetch("/auth/me");
  $("meLabel").textContent = `${data.email} (#${data.id})`;
  return data;
}

async function refreshLocks(){
  const locks = await apiFetch("/locks");
  $("lockSelect").innerHTML = "";
  for(const lk of locks){
    const opt = document.createElement("option");
    opt.value = lk.id;
    opt.textContent = `#${lk.id} - ${lk.name}`;
    opt.dataset.code = lk.code;
    $("lockSelect").appendChild(opt);
  }
  if(locks.length){
    $("lockSelect").value = locks[0].id;
    updateLockMeta();
    await refreshMembers();
  }
}

function updateLockMeta(){
  const opt = $("lockSelect").selectedOptions[0];
  if(!opt){ $("lockMeta").textContent=""; return; }
  $("lockMeta").textContent = `Pair code (ESP32 future): ${opt.dataset.code}`;
}

async function refreshMembers(){
  const lockId = Number($("lockSelect").value);
  const ms = await apiFetch(`/locks/${lockId}/members`);
  $("membersList").innerHTML = "";
  for(const m of ms){
    const div = document.createElement("div");
    div.className = "event";
    div.textContent = `account_id=${m.account_id} role=${m.role}`;
    $("membersList").appendChild(div);
  }
}

async function startCam(){
  stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
  $("video").srcObject = stream;
}

function stopCam(){
  if(stream){
    stream.getTracks().forEach(t=>t.stop());
    stream = null;
  }
  $("video").srcObject = null;
}

function snapBase64(){
  const video = $("video");
  const canvas = $("canvas");
  const w = video.videoWidth, h = video.videoHeight;
  canvas.width = w; canvas.height = h;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, w, h);
  // JPEG reduces size; still good enough
  return canvas.toDataURL("image/jpeg", 0.92);
}

function addEvent(obj){
  const div = document.createElement("div");
  div.className = "event";
  div.textContent = `[${new Date().toLocaleTimeString()}] ` + JSON.stringify(obj);
  $("events").prepend(div);
}

function setWs(on){
  $("wsStatus").textContent = on ? "ON" : "OFF";
}

function connectWS(){
  if(ws) ws.close();
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws`);
  ws.onopen = () => setWs(true);
  ws.onclose = () => setWs(false);
  ws.onerror = () => setWs(false);
  ws.onmessage = (ev) => {
    try{ addEvent(JSON.parse(ev.data)); }catch{ addEvent({raw: ev.data}); }
  };
  // keep alive
  setInterval(()=>{ if(ws && ws.readyState===1) ws.send("ping"); }, 12000);
}

async function loadLogs(){
  const lockId = Number($("lockSelect").value);
  const logs = await apiFetch(`/logs/${lockId}?limit=50`);
  $("logs").innerHTML = "";
  for(const l of logs){
    const div = document.createElement("div");
    div.className = "event";
    div.textContent = `${l.created_at} | success=${l.success} | score=${l.score.toFixed(4)} | matched=${l.matched_account_id} | src=${l.source}`;
    $("logs").appendChild(div);
  }
}

async function enroll5(){
  const lockId = Number($("lockSelect").value);
  const targetId = Number($("targetAccountId").value);
  $("enrollStatus").textContent = "Capturing 5 shots...";
  const imgs = [];
  for(let i=0;i<5;i++){
    imgs.push(snapBase64());
    $("enrollStatus").textContent = `Captured ${i+1}/5`;
    await new Promise(r=>setTimeout(r, 350));
  }
  $("enrollStatus").textContent = "Uploading...";
  const out = await apiFetch("/enroll", {
    method:"POST",
    body: JSON.stringify({ lock_id: lockId, target_account_id: targetId, images: imgs })
  });
  $("enrollStatus").textContent = `Enrolled: template_id=${out.template_id}, shots=${out.shots}`;
}

async function verifyNow(){
  const lockId = Number($("lockSelect").value);
  const img = snapBase64();
  const out = await apiFetch("/verify", {
    method:"POST",
    body: JSON.stringify({ lock_id: lockId, image: img, source: "web" })
  });
  $("verifyResult").textContent = JSON.stringify(out, null, 2);
}

async function login(email, password){
  const out = await apiFetch("/auth/login", { method:"POST", body: JSON.stringify({email, password}) });
  token = out.access_token;
  localStorage.setItem("token", token);
}

async function register(email, password){
  const out = await apiFetch("/auth/register", { method:"POST", body: JSON.stringify({email, password, full_name:""}) });
  token = out.access_token;
  localStorage.setItem("token", token);
}

// wire UI
$("startCamBtn").onclick = startCam;
$("stopCamBtn").onclick = stopCam;
$("connectWsBtn").onclick = connectWS;
$("clearEventsBtn").onclick = () => $("events").innerHTML = "";
$("loadLogsBtn").onclick = loadLogs;

$("loginBtn").onclick = async () => {
  try{
    await login($("email").value, $("password").value);
    await initAfterLogin();
  }catch(e){ alert(e.message); }
};
$("registerBtn").onclick = async () => {
  try{
    await register($("email").value, $("password").value);
    await initAfterLogin();
  }catch(e){ alert(e.message); }
};
$("logoutBtn").onclick = () => {
  localStorage.removeItem("token");
  token = "";
  location.reload();
};

$("createLockBtn").onclick = async () => {
  try{
    const name = $("lockName").value || "My Lock";
    await apiFetch("/locks", { method:"POST", body: JSON.stringify({name}) });
    await refreshLocks();
  }catch(e){ alert(e.message); }
};
$("addMemberBtn").onclick = async () => {
  try{
    const lockId = Number($("lockSelect").value);
    await apiFetch(`/locks/${lockId}/members`, {
      method:"POST",
      body: JSON.stringify({ email: $("memberEmail").value, role: $("memberRole").value })
    });
    await refreshMembers();
  }catch(e){ alert(e.message); }
};
$("lockSelect").onchange = async () => {
  updateLockMeta();
  await refreshMembers();
};
$("enroll5Btn").onclick = async () => {
  try{ await enroll5(); }catch(e){ alert(e.message); }
};
$("verifyBtn").onclick = async () => {
  try{ await verifyNow(); }catch(e){ alert(e.message); }
};

async function initAfterLogin(){
  setAuthUI(true);
  await me();
  await refreshLocks();
}

(async function boot(){
  if(token){
    try{
      await initAfterLogin();
      connectWS();
    }catch(e){
      setAuthUI(false);
    }
  }else{
    setAuthUI(false);
  }
})();