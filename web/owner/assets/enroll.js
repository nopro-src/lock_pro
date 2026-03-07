// owner/assets/enroll.js
let camStream = null;
let shots = [];

async function enrollInit() {
  guardAuth();
  setActiveNav("enroll");
  await loadMe();
  await loadLocks();
  await loadUsersToSelect();
  updateShotsUI();
}

async function loadLocks() {
  const locks = await apiFetch("/api/locks");
  const sel = document.getElementById("lockSel");
  sel.innerHTML = locks.map(l => `<option value="${l.id}">${escapeHtml(l.name)} (#${l.id})</option>`).join("");
}

async function loadUsersToSelect() {
  const sel = document.getElementById("userSel");
  if (!sel) return;

  const users = await apiFetch("/api/users?limit=200&offset=0");
  sel.innerHTML =
    `<option value="">-- Select user --</option>` +
    users
      .filter(u => (u.global_role || "").toUpperCase() === "USER")
      .map(u => `<option value="${u.id}">${escapeHtml(u.full_name || "")} (#${u.id}) - ${escapeHtml(u.email)}</option>`)
      .join("");
}

async function camStart() {
  try {
    if (camStream) return;
    camStream = await navigator.mediaDevices.getUserMedia({
      video: { width: 960, height: 540 },
      audio: false,
    });
    document.getElementById("cam").srcObject = camStream;
    toast("Camera started", "success");
  } catch (e) {
    toast("Camera error: " + e.message, "danger");
  }
}

function camStop() {
  if (!camStream) return;
  camStream.getTracks().forEach(t => t.stop());
  camStream = null;
  document.getElementById("cam").srcObject = null;
}

function captureShot() {
  const v = document.getElementById("cam");
  if (!camStream || !v.videoWidth) {
    toast("Start camera first", "warning");
    return;
  }
  const c = document.getElementById("canvas");
  c.width = v.videoWidth;
  c.height = v.videoHeight;
  const ctx = c.getContext("2d");
  ctx.drawImage(v, 0, 0, c.width, c.height);
  shots.push(c.toDataURL("image/jpeg", 0.92));
  updateShotsUI();
}

async function autoCapture5() {
  await camStart();
  shots = [];
  updateShotsUI();
  for (let i = 0; i < 5; i++) {
    captureShot();
    await new Promise(r => setTimeout(r, 450));
  }
}

function clearShots() {
  shots = [];
  updateShotsUI();
}

function updateShotsUI() {
  document.getElementById("shotCount").textContent = String(shots.length);
  const box = document.getElementById("shotsBox");
  box.innerHTML = shots
    .map((_, i) => `<span class="px-2 py-1 rounded-lg bg-slate-100 text-slate-700 text-xs">Shot ${i + 1}</span>`)
    .join("");
}

async function readFilesAsBase64(files) {
  const arr = [];
  for (const f of files) {
    const b64 = await new Promise((resolve, reject) => {
      const r = new FileReader();
      r.onload = () => resolve(r.result);
      r.onerror = () => reject(new Error("read file failed"));
      r.readAsDataURL(f);
    });
    arr.push(b64);
  }
  return arr;
}

async function doEnroll() {
  const lock_id = parseInt(document.getElementById("lockSel").value, 10);

  // Prefer dropdown
  const userSel = document.getElementById("userSel");
  let target_account_id = userSel ? parseInt(userSel.value || "", 10) : NaN;

  // Fallback manual input if you keep it
  if (!Number.isFinite(target_account_id)) {
    const manual = document.getElementById("accountId");
    target_account_id = parseInt((manual?.value || "").trim(), 10);
  }

  if (!Number.isFinite(target_account_id) || target_account_id <= 0) {
    toast("Missing account_id: hãy chọn user hoặc nhập Account ID", "danger");
    return;
  }

  let images = shots.slice(0, 5);
  const files = document.getElementById("files").files;
  if (images.length < 5 && files && files.length >= 5) {
    images = await readFilesAsBase64(Array.from(files).slice(0, 5));
  }
  if (images.length < 5) {
    toast("Need 5 images (webcam shots or files)", "warning");
    return;
  }

  try {
    // ✅ gửi theo chuẩn mới: target_account_id
    // backend vẫn hiểu cả account_id và target_account_id
    const out = await apiFetch("/api/enroll", {
      method: "POST",
      body: JSON.stringify({
        lock_id,
        target_account_id,
        images_base64: images,
      }),
    });

    toast(`Enroll OK template=${out.template_id} quality=${out.quality_score.toFixed(2)}`, "success");
    clearShots();
  } catch (e) {
    toast("Enroll failed: " + (e?.message || e), "danger");
  }
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

window.enrollInit = enrollInit;
window.camStart = camStart;
window.camStop = camStop;
window.captureShot = captureShot;
window.autoCapture5 = autoCapture5;
window.clearShots = clearShots;
window.doEnroll = doEnroll;