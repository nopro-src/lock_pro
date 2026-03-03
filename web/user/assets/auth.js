// user/assets/auth.js
async function userLogin(){
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  try{
    const out = await apiFetch("/api/auth/login", {
      method:"POST",
      body: JSON.stringify({email, password})
    });

    if(out.global_role !== "USER"){
      toast("This account is not USER", "danger");
      return;
    }

    setToken(out.access_token);
    location.href = "/user/verify.html";
  }catch(e){
    toast("Login failed: " + e.message, "danger");
  }
}

function logout(){
  clearToken();
  location.href = "/user/login.html";
}