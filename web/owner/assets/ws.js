// owner/assets/ws.js
let ws = null;

function wsConnect(lockId){
  const token = getToken();
  if(!token) return;

  if(ws && (ws.readyState===0 || ws.readyState===1)) ws.close();

  ws = new WebSocket(`${location.origin.replace("http","ws")}/ws?token=${encodeURIComponent(token)}`);
  ws.onopen = () => {
    ws.send(JSON.stringify({action:"join", lock_id: lockId}));
    addEvent("INFO", {msg:`connected, joining lock ${lockId}`});
  };
  ws.onmessage = (ev) => {
    try{
      const e = JSON.parse(ev.data);
      addEvent(e.type || "INFO", e.payload || e);
    }catch(_){
      addEvent("INFO", {raw: ev.data});
    }
  };
  ws.onclose = () => addEvent("ERROR", {msg:"ws closed"});
}

function addEvent(type, payload){
  const panel = document.getElementById("realtimePanel");
  if(!panel) return;
  const badge = type==="ERROR" ? "bg-rose-100 text-rose-700" :
                type==="VERIFY" ? "bg-emerald-100 text-emerald-700" :
                type==="ENROLL" ? "bg-blue-100 text-blue-700" :
                "bg-slate-100 text-slate-700";

  const t = new Date().toLocaleTimeString();
  const div = document.createElement("div");
  div.className = "flex gap-2 items-start py-2 border-b border-slate-100";
  div.innerHTML = `
    <span class="text-xs px-2 py-1 rounded-lg ${badge} font-medium">${type}</span>
    <div class="text-sm text-slate-700">
      <div class="text-xs text-slate-400">${t}</div>
      <pre class="text-xs whitespace-pre-wrap">${escapeHtml(JSON.stringify(payload, null, 2))}</pre>
    </div>
  `;
  panel.prepend(div);
}

function escapeHtml(s){
  return s.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
}