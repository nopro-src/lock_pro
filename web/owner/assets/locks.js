// owner/assets/locks.js
async function locksInit() {
  guardAuth();
  setActiveNav("locks");
  await loadMe();
  await loadLocks();
}

async function loadLocks() {
  const rows = await apiFetch("/api/locks");
  const tb = document.getElementById("locksTbody");
  tb.innerHTML = rows.map(l => `
    <tr class="border-b">
      <td class="py-3">${l.id}</td>
      <td class="py-3 font-medium">${l.name}</td>
      <td class="py-3">${l.code}</td>
      <td class="py-3">${l.threshold_override ?? "-"}</td>
      <td class="py-3 text-right">
        <button class="px-3 py-1 rounded-lg bg-emerald-100 text-emerald-700" onclick='openLock(${l.id})'>Open</button>
        <button class="px-3 py-1 rounded-lg bg-amber-100 text-amber-700 ml-2" onclick='closeLock(${l.id})'>Close</button>
        <button class="px-3 py-1 rounded-lg bg-slate-100 ml-2" onclick='openEditLock(${JSON.stringify(l)})'>Edit</button>
        <button class="px-3 py-1 rounded-lg bg-rose-100 text-rose-700 ml-2" onclick='deleteLock(${l.id})'>Delete</button>
      </td>
    </tr>
  `).join("");
}

function openNewLock() {
  document.getElementById("lockId").value = "";
  document.getElementById("lockName").value = "";
  document.getElementById("lockCode").value = "";
  document.getElementById("lockThreshold").value = "";
  document.getElementById("lockModalTitle").textContent = "Create Lock";
  document.getElementById("lockModal").classList.remove("hidden");
}

function openEditLock(l) {
  document.getElementById("lockId").value = l.id;
  document.getElementById("lockName").value = l.name;
  document.getElementById("lockCode").value = l.code;
  document.getElementById("lockThreshold").value = l.threshold_override ?? "";
  document.getElementById("lockModalTitle").textContent = "Edit Lock";
  document.getElementById("lockModal").classList.remove("hidden");
}

function closeLockModal() {
  document.getElementById("lockModal").classList.add("hidden");
}

async function saveLock() {
  const id = document.getElementById("lockId").value;
  const name = document.getElementById("lockName").value.trim();
  const code = document.getElementById("lockCode").value.trim();
  const threshold_override_raw = document.getElementById("lockThreshold").value.trim();
  const threshold_override = threshold_override_raw ? parseFloat(threshold_override_raw) : null;

  try {
    if (!id) {
      await apiFetch("/api/locks", { method: "POST", body: JSON.stringify({ name, code, threshold_override }) });
      toast("Lock created", "success");
    } else {
      await apiFetch(`/api/locks/${id}`, { method: "PUT", body: JSON.stringify({ name, code, threshold_override }) });
      toast("Lock updated", "success");
    }
    closeLockModal();
    await loadLocks();
  } catch (e) {
    toast("Save failed: " + e.message, "danger");
  }
}

async function deleteLock(id) {
  if (!confirm("Delete lock #" + id + "?")) return;
  try {
    await apiFetch(`/api/locks/${id}`, { method: "DELETE" });
    toast("Deleted", "success");
    await loadLocks();
  } catch (e) {
    toast("Delete failed: " + e.message, "danger");
  }
}

async function openLock(id) {
  try {
    await apiFetch(`/api/locks/${id}/open`, { method: "POST" });
    toast(`Open command sent for lock #${id}`, "success");
  } catch (e) {
    toast("Open failed: " + e.message, "danger");
  }
}

async function closeLock(id) {
  try {
    await apiFetch(`/api/locks/${id}/close`, { method: "POST" });
    toast(`Close command sent for lock #${id}`, "success");
  } catch (e) {
    toast("Close failed: " + e.message, "danger");
  }
}