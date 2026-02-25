async function logsInit(){
  guardAuth();
  setActiveNav("logs");
  await loadMe();
  await loadLocksToLogsSelect();
}

async function loadLocksToLogsSelect(){
  const locks = await apiFetch("/api/locks");
  const sel = document.getElementById("lockSelLogs");
  sel.innerHTML = locks.map(l=> `<option value="${l.id}">${l.name} (#${l.id})</option>`).join("");
  await renderLogs();
}

async function renderLogs(){
  const lock_id = parseInt(document.getElementById("lockSelLogs").value, 10);
  const data = await apiFetch(`/api/logs/${lock_id}?limit=200&offset=0`);
  const tbody = document.getElementById("logsTbody");
  tbody.innerHTML = "";
  data.forEach(r=>{
    const badge = r.success ? "<span class='badge badge-soft'>SUCCESS</span>" : "<span class='badge badge-soft-red'>DENY</span>";
    tbody.insertAdjacentHTML("beforeend", `
      <tr>
        <td>${r.id}</td>
        <td>${badge}</td>
        <td>${r.matched_account_id ?? "-"}</td>
        <td>${r.score.toFixed(4)}</td>
        <td>${r.threshold_used.toFixed(2)}</td>
        <td>${r.source}</td>
        <td>${new Date(r.created_at).toLocaleString()}</td>
      </tr>
    `);
  });
}