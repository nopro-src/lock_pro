// user/assets/verify.js
let stream = null;

async function verifyInit(){
  guardAuth();
  await loadMe();

  // Minimal: user can see all locks via /api/locks currently.
  // Recommended: add endpoint /api/locks/mine later.
  const locks = await apiFetch("/api/locks");
  const sel = document.getElementById("lockSel");
  sel.innerHTML = locks.map(l=> `<option value="${l.id}">${l.name} (#${l.id})</option>`).join("");
}

async function camStart(){
  try{
    if(stream) return;
    stream = await navigator.mediaDevices.getUserMedia({video:{width:960,height:540},audio:false});
    document.getElementById("cam").srcObject = stream;
    toast("Camera started", "success");
  }catch(e){
    toast("Camera error: " + e.message, "danger");
  }
}
function camStop(){
  if(!stream) return;
  stream.getTracks().forEach(t=>t.stop());
  stream=null;
  document.getElementById("cam").srcObject=null;
}

function captureB64(){
  const v = document.getElementById("cam");
  if(!stream || !v.videoWidth) throw new Error("Start camera first");
  const c = document.getElementById("canvas");
  c.width=v.videoWidth; c.height=v.videoHeight;
  c.getContext("2d").drawImage(v,0,0,c.width,c.height);
  return c.toDataURL("image/jpeg",0.92);
}

async function doVerify(){
  try{
    const lock_id = parseInt(document.getElementById("lockSel").value,10);
    const image_base64 = captureB64();
    const out = await apiFetch("/api/verify", {
      method:"POST",
      body: JSON.stringify({lock_id, image_base64, source:"web"})
    });

    document.getElementById("result").textContent = JSON.stringify(out, null, 2);
    toast(out.success ? "Unlocked" : "Denied", out.success ? "success" : "danger");
  }catch(e){
    toast("Verify failed: " + e.message, "danger");
  }
}