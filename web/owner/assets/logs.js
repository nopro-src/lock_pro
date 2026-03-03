// owner/assets/logs.js
async function logsInit(){
  guardAuth();
  setActiveNav("logs");
  await loadMe();
  await loadLocks();
  await loadLogs();
}

async function loadLocks(){
  const locks = await apiFetch("/api/locks");
  const sel = document.getElementById("lockSel");
  sel.innerHTML = locks.map(l=> `<option value="${l.id}">${l.name} (#${l.id})</option>`).join("");
}

async function loadLogs(){
  const lockId = parseInt(document.getElementById("lockSel").value,10);
  const rows = await apiFetch(`/api/logs/${lockId}?limit=200&offset=0`);
  const tb = document.getElementById("logsTbody");
  tb.innerHTML = rows.map(r=> `
    <tr class="border-b">
      <td class="py-3">${r.id}</td>
      <td class="py-3">${r.created_at}</td>
      <td class="py-3">${r.matched_account_id ?? "-"}</td>
      <td class="py-3">${r.score?.toFixed ? r.score.toFixed(3) : r.score}</td>
      <td class="py-3">${r.threshold_used}</td>
      <td class="py-3">${r.success ? `<span class="px-2 py-1 rounded-lg bg-emerald-100 text-emerald-700 text-xs font-medium">ALLOW</span>` : `<span class="px-2 py-1 rounded-lg bg-rose-100 text-rose-700 text-xs font-medium">DENY</span>`}</td>
      <td class="py-3">${r.source}</td>
    </tr>
  `).join("");
}