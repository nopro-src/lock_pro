let vStream = null;

async function vStart(){
  try{
    if(vStream) return;
    vStream = await navigator.mediaDevices.getUserMedia({ video: { width: 960, height: 540 }, audio:false });
    document.getElementById("vCam").srcObject = vStream;
    toast("Verify camera started", "success");
  }catch(e){
    toast("Camera error: " + e.message, "danger");
  }
}

function vStop(){
  if(!vStream) return;
  vStream.getTracks().forEach(t=>t.stop());
  vStream = null;
  document.getElementById("vCam").srcObject = null;
  toast("Verify camera stopped", "info");
}

function vCaptureB64(){
  const video = document.getElementById("vCam");
  if(!vStream || !video.videoWidth) throw new Error("Start verify camera first");

  const canvas = document.getElementById("vCanvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/jpeg", 0.92);
}

async function verifyOnce(){
  try{
    // reuse lock selector from dashboard (lockSel)
    const lockId = parseInt(document.getElementById("lockSel").value, 10);
    const image_base64 = vCaptureB64();

    const out = await apiFetch("/api/verify", {
      method:"POST",
      body: JSON.stringify({ lock_id: lockId, image_base64, source:"web" })
    });

    document.getElementById("verifyOut").textContent = JSON.stringify(out, null, 2);
    toast(out.success ? "VERIFY SUCCESS" : "VERIFY DENY", out.success ? "success" : "danger");
  }catch(e){
    toast("Verify failed: " + e.message, "danger");
  }
}