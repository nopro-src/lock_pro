let ws = null;

function wsConnect(lockId){
  const token = getToken();
  if(!token) return;

  const url = (location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws?token=" + encodeURIComponent(token);
  ws = new WebSocket(url);

  ws.onopen = ()=> {
    ws.send(JSON.stringify({ action:"join", lock_id: lockId }));
    addEventLine("INFO", "Connected WS, joined lock " + lockId);
  };

  ws.onmessage = (ev)=> {
    try{
      const msg = JSON.parse(ev.data);
      handleWsEvent(msg);
    }catch(e){}
  };

  ws.onclose = ()=> addEventLine("ERROR", "WS disconnected");
}

function addEventLine(type, text){
  const el = document.getElementById("realtimePanel");
  if(!el) return;
  const time = new Date().toLocaleTimeString();
  const badge = type === "ERROR" ? "badge-soft-red" : "badge-soft";
  el.insertAdjacentHTML("afterbegin",
    `<div class="d-flex gap-2 align-items-start mb-2">
      <span class="badge ${badge}">${type}</span>
      <div class="small"><div>${text}</div><div class="small-muted">${time}</div></div>
    </div>`
  );
}

function handleWsEvent(evt){
  addEventLine(evt.type, JSON.stringify(evt.payload));
}