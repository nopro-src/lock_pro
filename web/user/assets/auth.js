async function userLogin() {
  const email = document.getElementById("email")?.value.trim();
  const password = document.getElementById("password")?.value || "";

  try {
    if (!email || !password) {
      toast("Vui lòng nhập email và mật khẩu", "warning");
      return;
    }

    const out = await apiFetch("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });

    if (!out.access_token) {
      throw new Error("Login response missing access_token");
    }

    setToken(out.access_token);

    const me = await apiFetch("/api/auth/me");

    if (me.global_role !== "USER") {
      clearToken();
      toast("This account is not USER", "danger");
      return;
    }

    toast("Đăng nhập thành công", "success");
    location.href = "/user/verify.html";
  } catch (e) {
    toast("Login failed: " + e.message, "danger");
  }
}

function logout() {
  clearToken();
  location.href = "/user/login.html";
}

window.userLogin = userLogin;
window.logout = logout;