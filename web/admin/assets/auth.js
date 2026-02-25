async function doLogin(){
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  try{
    const data = await apiFetch("/api/auth/login", {
      method:"POST",
      body: JSON.stringify({ email, password })
    });
    setToken(data.access_token);
    location.href = "/admin/dashboard.html";
  }catch(e){
    toast(e.message, "danger");
  }
}

async function loadMe(){
  const me = await apiFetch("/api/auth/me");
  document.querySelectorAll("[data-me]").forEach(el=>{
    const k = el.getAttribute("data-me");
    el.textContent = me[k];
  });
  return me;
}

function logout(){
  clearToken();
  location.href = "/admin/login.html";
}