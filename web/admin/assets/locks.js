async function locksInit(){
  guardAuth();
  setActiveNav("locks");
  await loadMe();
  await renderLocks();
}

async function renderLocks(){
  const data = await apiFetch("/api/locks");
  const tbody = document.getElementById("locksTbody");
  tbody.innerHTML = "";
  data.forEach(l=>{
    const thr = (l.threshold_override === null || l.threshold_override === undefined) ? "<span class='small-muted'>default</span>" : l.threshold_override.toFixed(2);
    tbody.insertAdjacentHTML("beforeend", `
      <tr>
        <td>${l.id}</td>
        <td>${l.name}</td>
        <td><code>${l.code}</code></td>
        <td>${thr}</td>
      </tr>
    `);
  });
}

async function createLock(){
  const name = document.getElementById("lockName").value.trim();
  const code = document.getElementById("lockCode").value.trim();
  const thrStr = document.getElementById("lockThr").value.trim();
  const threshold_override = thrStr ? parseFloat(thrStr) : null;

  try{
    await apiFetch("/api/locks", {
      method:"POST",
      body: JSON.stringify({ name, code, threshold_override })
    });
    toast("Created lock", "success");
    bootstrap.Modal.getInstance(document.getElementById("lockModal")).hide();
    await renderLocks();
  }catch(e){
    toast(e.message, "danger");
  }
}