// web/owner/assets/users.js
// Depends on: common.js (apiFetch, toast, setActiveNav), auth.js (guardAuth, loadMe)

let _locksCache = [];

async function usersInit() {
  guardAuth();
  setActiveNav("users");

  await loadMe();
  await loadLocksToSelect();
  await loadUsersTable();
}

/** Modal controls (Tailwind modal) */
function openUserModal() {
  const m = document.getElementById("userModal");
  if (m) m.classList.remove("hidden");
}

function closeUserModal() {
  const m = document.getElementById("userModal");
  if (m) m.classList.add("hidden");
}

/** Load locks into dropdown */
async function loadLocksToSelect() {
  const sel = document.getElementById("userLockId");
  if (!sel) return;

  const locks = await apiFetch("/api/locks");
  _locksCache = Array.isArray(locks) ? locks : [];

  sel.innerHTML =
    `<option value="">-- Select lock --</option>` +
    _locksCache
      .map((l) => `<option value="${l.id}">${escapeHtml(l.name)} (#${l.id})</option>`)
      .join("");

  // default select first lock for convenience
  if (_locksCache.length > 0 && !sel.value) {
    sel.value = String(_locksCache[0].id);
  }
}

/** Render users table */
async function loadUsersTable() {
  const tbody = document.getElementById("usersTbody");
  if (!tbody) return;

  const rows = await apiFetch("/api/users?limit=200&offset=0");
  tbody.innerHTML = rows
    .map(
      (r) => `
    <tr class="border-b border-slate-100">
      <td class="py-3">${r.id}</td>
      <td class="py-3 font-medium text-slate-900">${escapeHtml(r.full_name || "")}</td>
      <td class="py-3">${escapeHtml(r.email)}</td>
      <td class="py-3">${escapeHtml(r.global_role || "")}</td>
      <td class="py-3">
        <span class="inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold ${
          r.is_active ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-600"
        }">
          ${r.is_active ? "ACTIVE" : "DISABLED"}
        </span>
      </td>
    </tr>
  `
    )
    .join("");
}

/** CREATE USER (Owner flow)
 *  IMPORTANT: backend now REQUIRES lock_id
 *  IMPORTANT: DO NOT send global_role here unless backend schema accepts it
 */
async function createUser() {
  const emailEl = document.getElementById("uEmail");
  const passEl = document.getElementById("uPass");
  const nameEl = document.getElementById("uName");
  const activeEl = document.getElementById("uActive");
  const lockEl = document.getElementById("userLockId");

  const email = (emailEl?.value || "").trim();
  const password = (passEl?.value || "").trim();
  const full_name = (nameEl?.value || "").trim();
  const is_active = activeEl ? !!activeEl.checked : true;
  const lock_id = lockEl ? parseInt(lockEl.value, 10) : NaN;

  if (!email) return toast("Email là bắt buộc", "danger");
  if (!password || password.length < 8) return toast("Password tối thiểu 8 ký tự", "danger");
  if (!Number.isFinite(lock_id) || lock_id <= 0) return toast("Bạn phải chọn Lock", "danger");

  const body = { email, password, full_name, is_active, lock_id };

  try {
    await apiFetch("/api/users", { method: "POST", body: JSON.stringify(body) });
    toast("Tạo user thành công", "success");

    // reset form (giữ lock)
    if (emailEl) emailEl.value = "";
    if (passEl) passEl.value = "";
    if (nameEl) nameEl.value = "";
    if (activeEl) activeEl.checked = true;

    await loadUsersTable();
    closeUserModal();
  } catch (e) {
    toast(String(e?.message || e), "danger");
  }
}

/** helpers */
function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

// expose for HTML onclick / onload
window.usersInit = usersInit;
window.openUserModal = openUserModal;
window.closeUserModal = closeUserModal;
window.createUser = createUser;