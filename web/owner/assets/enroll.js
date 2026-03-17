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
  if (!sel) return;

  sel.innerHTML = locks
    .map((l) => `<option value="${l.id}">${escapeHtml(l.name)} (#${l.id})</option>`)
    .join("");
}

async function loadUsersToSelect() {
  const sel = document.getElementById("userSel");
  if (!sel) return;

  const users = await apiFetch("/api/users?limit=200&offset=0");
  sel.innerHTML =
    `<option value="">-- Select user --</option>` +
    users
      .filter((u) => (u.global_role || "").toUpperCase() === "USER")
      .map(
        (u) =>
          `<option value="${u.id}">${escapeHtml(u.full_name || "")} (#${u.id}) - ${escapeHtml(u.email)}</option>`
      )
      .join("");
}

async function camStart() {
  try {
    if (camStream) return;

    const video = document.getElementById("cam");
    if (!video) throw new Error("Camera element not found");

    camStream = await navigator.mediaDevices.getUserMedia({
      video: { width: 960, height: 540 },
      audio: false,
    });

    video.srcObject = camStream;
    toast("Camera started", "success");
  } catch (e) {
    toast("Camera error: " + e.message, "danger");
    throw e;
  }
}

function camStop() {
  const video = document.getElementById("cam");

  if (camStream) {
    camStream.getTracks().forEach((t) => t.stop());
    camStream = null;
  }

  if (video) {
    video.srcObject = null;
  }
}

function captureShot() {
  const v = document.getElementById("cam");
  const c = document.getElementById("canvas");

  if (!v || !c) {
    toast("Camera or canvas not found", "danger");
    return;
  }

  if (!camStream || !v.videoWidth) {
    toast("Start camera first", "warning");
    return;
  }

  if (shots.length >= 5) {
    toast("Already captured 5 shots", "warning");
    return;
  }

  const ctx = c.getContext("2d");
  if (!ctx) {
    toast("Canvas context unavailable", "danger");
    return;
  }

  // Crop theo cùng tỉ lệ với user verify overlay
  const srcW = v.videoWidth;
  const srcH = v.videoHeight;

  const cropW = Math.floor(srcW * 0.42);
  const cropH = Math.floor(srcH * 0.60);
  const cropX = Math.floor((srcW - cropW) / 2);
  const cropY = Math.floor((srcH - cropH) / 2);

  c.width = cropW;
  c.height = cropH;

  ctx.clearRect(0, 0, c.width, c.height);
  ctx.drawImage(
    v,
    cropX, cropY, cropW, cropH,
    0, 0, c.width, c.height
  );

  shots.push(c.toDataURL("image/jpeg", 0.92));
  updateShotsUI();
}

async function autoCapture5() {
  await camStart();

  shots = [];
  updateShotsUI();

  for (let i = 0; i < 5; i++) {
    captureShot();
    await new Promise((r) => setTimeout(r, 500));
  }
}

function clearShots() {
  shots = [];
  updateShotsUI();
}

function updateShotsUI() {
  const countEl = document.getElementById("shotCount");
  const box = document.getElementById("shotsBox");

  if (countEl) {
    countEl.textContent = String(shots.length);
  }

  if (!box) return;

  box.innerHTML = shots
    .map(
      (src, i) => `
        <div class="relative w-24 h-24 rounded-2xl overflow-hidden border border-slate-200 bg-white shadow-sm">
          <img src="${src}" alt="Shot ${i + 1}" class="w-full h-full object-cover"/>
          <div class="absolute left-2 bottom-2 text-[10px] px-2 py-1 rounded-full bg-slate-900/75 text-white">
            ${i + 1}
          </div>
        </div>
      `
    )
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
  try {
    const lock_id = parseInt(document.getElementById("lockSel").value, 10);

    const userSel = document.getElementById("userSel");
    let target_account_id = userSel ? parseInt(userSel.value || "", 10) : NaN;

    if (!Number.isFinite(target_account_id)) {
      const manual = document.getElementById("accountId");
      target_account_id = parseInt((manual?.value || "").trim(), 10);
    }

    if (!Number.isFinite(target_account_id) || target_account_id <= 0) {
      throw new Error("Missing account_id: hãy chọn user hoặc nhập Account ID");
    }

    let images = shots.slice(0, 5);
    const files = document.getElementById("files")?.files;

    if (images.length < 5 && files && files.length >= 5) {
      images = await readFilesAsBase64(Array.from(files).slice(0, 5));
    }

    if (images.length < 5) {
      throw new Error("Need 5 images (webcam shots or files)");
    }

    const out = await apiFetch("/api/enroll", {
      method: "POST",
      body: JSON.stringify({
        lock_id,
        target_account_id,
        images_base64: images,
      }),
    });

    clearShots();
    toast("Enroll thành công", "success");
    return out;
  } catch (e) {
    const friendly = mapFaceErrorMessage(e.message);
    toast(friendly, "danger");
    throw new Error(friendly);
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
function mapFaceErrorMessage(message) {
  const msg = String(message || "");

  if (msg.includes("Multiple faces detected")) {
    return "Phát hiện nhiều khuôn mặt. Khi đăng ký, chỉ để 1 người trong khung hình.";
  }
  if (msg.includes("No face detected")) {
    return "Không phát hiện khuôn mặt. Hãy đưa mặt vào giữa khung hình.";
  }
  if (msg.includes("Too blurry")) {
    return "Ảnh bị mờ. Hãy giữ máy ổn định và đủ sáng.";
  }

  return msg;
}
window.enrollInit = enrollInit;
window.camStart = camStart;
window.camStop = camStop;
window.captureShot = captureShot;
window.autoCapture5 = autoCapture5;
window.clearShots = clearShots;
window.doEnroll = doEnroll;