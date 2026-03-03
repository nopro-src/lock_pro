let camStream = null;
let shots = []; // base64 images

function toggleCreateUser(){
  const on = document.getElementById("createUserToggle").checked;
  document.getElementById("createUserBox").style.display = on ? "block" : "none";
}

function toBase64FromCanvas(canvas){
  return canvas.toDataURL("image/jpeg", 0.92); // jpeg smaller than png
}

async function enrollInit(){
  guardAuth();
  setActiveNav("enroll");
  await loadMe();
  await loadLocksToSelect();
}

async function loadLocksToSelect(){
  const locks = await apiFetch("/api/locks");
  const sel = document.getElementById("lockSel");
  sel.innerHTML = locks.map(l=> `<option value="${l.id}">${l.name} (#${l.id})</option>`).join("");
}

async function camStart(){
  try{
    if(camStream) return;
    camStream = await navigator.mediaDevices.getUserMedia({ video: { width: 960, height: 540 }, audio:false });
    const video = document.getElementById("cam");
    video.srcObject = camStream;
    toast("Camera started", "success");
  }catch(e){
    toast("Camera error: " + e.message, "danger");
  }
}

function camStop(){
  if(!camStream) return;
  camStream.getTracks().forEach(t=>t.stop());
  camStream = null;
  document.getElementById("cam").srcObject = null;
  toast("Camera stopped", "info");
}

function updateShotsUI(){
  document.getElementById("shotCount").textContent = String(shots.length);
  const box = document.getElementById("shotChips");
  box.innerHTML = "";
  shots.forEach((_, idx)=>{
    box.insertAdjacentHTML("beforeend", `<span class="shot-chip">Shot ${idx+1}</span>`);
  });
}

function captureShot(){
  const video = document.getElementById("cam");
  if(!camStream || !video.videoWidth){
    toast("Start camera first", "warning");
    return;
  }

  const canvas = document.getElementById("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  const b64 = toBase64FromCanvas(canvas);
  shots.push(b64);
  updateShotsUI();
  toast("Captured shot " + shots.length, "success");
}

async function capture5Auto(){
  await camStart();
  clearShots();
  // capture 5 shots with small delays to vary pose slightly
  for(let i=0;i<5;i++){
    captureShot();
    await new Promise(r=>setTimeout(r, 450));
  }
}

function clearShots(){
  shots = [];
  updateShotsUI();
}

async function maybeCreateUserIfNeeded(){
  const on = document.getElementById("createUserToggle").checked;
  if(!on) return null;

  const email = document.getElementById("newEmail").value.trim();
  const password = document.getElementById("newPassword").value;
  const full_name = document.getElementById("newFullName").value.trim();

  if(!email || !password){
    throw new Error("Missing new user email/password");
  }

  // requires OWNER (demo: account id=1)
  const u = await apiFetch("/api/users", {
    method:"POST",
    body: JSON.stringify({ email, password, full_name, is_active:true })
  });

  toast("Created user id=" + u.id, "success");
  return u.id;
}

async function doEnrollFromCam(){
  const lock_id = parseInt(document.getElementById("lockSel").value, 10);

  try{
    let account_id = await maybeCreateUserIfNeeded();
    if(!account_id){
      account_id = parseInt(document.getElementById("accountId").value, 10);
    }
    if(!account_id){
      toast("Missing account_id", "danger");
      return;
    }
    if(shots.length < 5){
      toast("Need at least 5 shots", "danger");
      return;
    }

    const out = await apiFetch("/api/enroll", {
      method:"POST",
      body: JSON.stringify({ lock_id, account_id, images_base64: shots.slice(0,5) })
    });

    toast(`Enroll success template_id=${out.template_id} quality=${out.quality_score.toFixed(2)}`, "success");
  }catch(e){
    toast("Enroll failed: " + e.message, "danger");
  }
}