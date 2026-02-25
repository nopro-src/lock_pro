function toBase64(file){
  return new Promise((resolve,reject)=>{
    const r = new FileReader();
    r.onload = ()=> resolve(r.result);
    r.onerror = reject;
    r.readAsDataURL(file);
  });
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

async function doEnroll(){
  const lock_id = parseInt(document.getElementById("lockSel").value, 10);
  const account_id = parseInt(document.getElementById("accountId").value, 10);

  const files = document.getElementById("shots").files;
  if(!files || files.length < 5){
    toast("Need at least 5 images", "danger");
    return;
  }

  const images_base64 = [];
  for(const f of files){
    images_base64.push(await toBase64(f));
  }

  try{
    const out = await apiFetch("/api/enroll", {
      method:"POST",
      body: JSON.stringify({ lock_id, account_id, images_base64 })
    });
    toast(`Enroll success template_id=${out.template_id} quality=${out.quality_score.toFixed(2)}`, "success");
  }catch(e){
    toast("Enroll failed: " + e.message, "danger");
  }
}