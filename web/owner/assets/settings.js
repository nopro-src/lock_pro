// owner/assets/settings.js
async function settingsInit(){
  guardAuth();
  setActiveNav("settings");
  await loadMe();
  const info = await apiFetch("/api/system/info");
  document.getElementById("sysInfo").textContent = JSON.stringify(info, null, 2);
}