async function usersInit(){
  guardAuth();
  setActiveNav("users");
  await loadMe();
  await renderUsers();
}

async function renderUsers(){
  // OWNER only: demo rule account id=1
  try{
    const data = await apiFetch("/api/users?limit=200&offset=0");
    const tbody = document.getElementById("usersTbody");
    tbody.innerHTML = "";
    data.forEach(u=>{
      const badge = u.is_active ? "<span class='badge badge-soft'>ACTIVE</span>" : "<span class='badge badge-soft-red'>DISABLED</span>";
      tbody.insertAdjacentHTML("beforeend", `
        <tr>
          <td>${u.id}</td>
          <td>${u.full_name || ""}</td>
          <td>${u.email}</td>
          <td>${badge}</td>
        </tr>
      `);
    });
  }catch(e){
    toast("Users page requires OWNER (demo: account id=1). " + e.message, "warning");
  }
}

async function createUser(){
  const email = document.getElementById("uEmail").value.trim();
  const password = document.getElementById("uPassword").value;
  const full_name = document.getElementById("uName").value.trim();
  const is_active = document.getElementById("uActive").checked;

  try{
    await apiFetch("/api/users", {
      method:"POST",
      body: JSON.stringify({ email, password, full_name, is_active })
    });
    toast("Created user", "success");
    bootstrap.Modal.getInstance(document.getElementById("userModal")).hide();
    await renderUsers();
  }catch(e){
    toast(e.message, "danger");
  }
}