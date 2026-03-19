let stream = null;

async function verifyInit() {
  guardAuth();
  await loadMe();

  const sel = document.getElementById("lockSel");
  const resultBox = document.getElementById("result");

  if (resultBox) {
    resultBox.textContent = "";
  }

  const locks = await apiFetch("/api/locks");

  if (!Array.isArray(locks) || locks.length === 0) {
    if (sel) {
      sel.innerHTML = `<option value="">No locks available</option>`;
      sel.disabled = true;
    }
    throw new Error("No locks available for verification");
  }

  if (sel) {
    sel.innerHTML = locks
      .map((l) => `<option value="${l.id}">${l.name} (#${l.id})</option>`)
      .join("");
  }
}

async function camStart() {
  if (stream) return;

  const video = document.getElementById("cam");
  if (!video) throw new Error("Camera element not found");

  stream = await navigator.mediaDevices.getUserMedia({
    video: { width: 640, height: 360 },
    audio: false
  });

  video.srcObject = stream;
}

function camStop() {
  const video = document.getElementById("cam");

  if (stream) {
    stream.getTracks().forEach((t) => t.stop());
    stream = null;
  }

  if (video) {
    video.srcObject = null;
  }
}

function captureB64() {
  const v = document.getElementById("cam");
  const c = document.getElementById("canvas");

  if (!v || !c) throw new Error("Camera or canvas element not found");
  if (!stream || !v.videoWidth) throw new Error("Start camera first");

  const srcW = v.videoWidth;
  const srcH = v.videoHeight;

  const cropW = Math.floor(srcW * 0.42);
  const cropH = Math.floor(srcH * 0.60);
  const cropX = Math.floor((srcW - cropW) / 2);
  const cropY = Math.floor((srcH - cropH) / 2);

  // Scale xuống nhỏ hơn để giảm lag
  const outSize = 320;
  c.width = outSize;
  c.height = outSize;

  const ctx = c.getContext("2d");
  if (!ctx) throw new Error("Canvas context not available");

  ctx.clearRect(0, 0, c.width, c.height);
  ctx.drawImage(
    v,
    cropX, cropY, cropW, cropH,
    0, 0, c.width, c.height
  );

  return c.toDataURL("image/jpeg", 0.75);
}

function mapFaceErrorMessage(message) {
  const msg = String(message || "");

  if (msg.includes("Multiple faces detected")) {
    return "Phát hiện nhiều khuôn mặt. Vui lòng chỉ để 1 người trong khung hình.";
  }
  if (msg.includes("No face detected")) {
    return "Không phát hiện khuôn mặt. Hãy đưa mặt vào giữa khung hình.";
  }
  if (msg.includes("Too blurry")) {
    return "Ảnh bị mờ. Hãy đứng yên và thử lại.";
  }
  if (msg.includes("Too dark")) {
    return "Ảnh quá tối. Hãy tăng ánh sáng và thử lại.";
  }
  if (msg.includes("Too bright")) {
    return "Ảnh quá sáng. Hãy giảm chói hoặc đổi góc camera.";
  }
  if (msg.includes("Face too small")) {
    return "Khuôn mặt quá nhỏ trong khung hình. Hãy đứng gần camera hơn.";
  }
  if (msg.includes("No face templates enrolled")) {
    return "Khóa này chưa có dữ liệu khuôn mặt được đăng ký.";
  }
  if (msg.includes("Device not found for this lock")) {
    return "Không tìm thấy thiết bị tương ứng với khóa này.";
  }

  return msg;
}

async function doVerify() {
  const sel = document.getElementById("lockSel");
  const resultBox = document.getElementById("result");

  try {
    if (!sel) throw new Error("Lock selector not found");

    const lock_id = parseInt(sel.value, 10);
    if (!lock_id) throw new Error("Please select a valid lock");

    const image_base64 = captureB64();

    const out = await apiFetch("/api/verify", {
      method: "POST",
      body: JSON.stringify({
        lock_id,
        image_base64,
        source: "web",
        device_uid: "lock_001"
      })
    });

    if (resultBox) {
      resultBox.textContent = JSON.stringify(out, null, 2);
    }

    return out;
  } catch (e) {
    const friendly = mapFaceErrorMessage(e?.message || e);

    if (resultBox) {
      resultBox.textContent = friendly;
    }

    throw new Error(friendly);
  }
}

async function openLockAfterVerify(lockId) {
  return await apiFetch(`/api/locks/${lockId}/open`, {
    method: "POST"
  });
}