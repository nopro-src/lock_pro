// owner/assets/users.js
async function usersInit(){
  guardAuth();
  setActiveNav("users");
  await loadMe();
  await loadUsers();
}

async function loadUsers(){
  const rows = await apiFetch("/api/users?limit=200&offset=0");
  const tb = document.getElementById("usersTbody");
  tb.innerHTML = rows.map(u=> `
    <tr class="border-b">
      <td class="py-3">${u.id}</td>
      <td class="py-3 font-medium">${u.full_name}</td>
      <td class="py-3">${u.email}</td>
      <td class="py-3">${u.global_role}</td>
      <td class="py-3">${u.is_active ? `<span class="px-2 py-1 rounded-lg bg-emerald-100 text-emerald-700 text-xs font-medium">ACTIVE</span>` : `<span class="px-2 py-1 rounded-lg bg-slate-100 text-slate-700 text-xs font-medium">DISABLED</span>`}</td>
    </tr>
  `).join("");
}

function openUserModal(){
  document.getElementById("uEmail").value = "";
  document.getElementById("uPass").value = "";
  document.getElementById("uName").value = "";
  document.getElementById("uRole").value = "USER";
  document.getElementById("uActive").checked = true;
  document.getElementById("userModal").classList.remove("hidden");
}
function closeUserModal(){ document.getElementById("userModal").classList.add("hidden"); }

async function createUser(){
  const email = document.getElementById("uEmail").value.trim();
  const password = document.getElementById("uPass").value;
  const full_name = document.getElementById("uName").value.trim();
  const global_role = document.getElementById("uRole").value;
  const is_active = document.getElementById("uActive").checked;

  if(password.length < 8){
    toast("Password must be >= 8 chars", "warning");
    return;
  }

  try{
    await apiFetch("/api/users", {
      method:"POST",
      body: JSON.stringify({email, password, full_name, is_active, global_role})
    });
    toast("User created", "success");
    closeUserModal();
    await loadUsers();
  }catch(e){
    toast("Create failed: " + e.message, "danger");
  }
}   