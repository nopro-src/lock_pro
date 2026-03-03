// owner/assets/auth.js
async function ownerLogin(){
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  try{
    const out = await apiFetch("/api/auth/login", {
      method:"POST",
      body: JSON.stringify({email, password})
    });

    if(out.global_role !== "OWNER"){
      toast("This account is not OWNER", "danger");
      return;
    }

    setToken(out.access_token);
    location.href = "/owner/dashboard.html";
  }catch(e){
    toast("Login failed: " + e.message, "danger");
  }
}

function logout(){
  clearToken();
  location.href = "/owner/login.html";
}