async function loadDashboard() {
  try {
    const response = await fetch('/api/dashboard', { cache: 'no-store' });
    if (!response.ok) throw new Error('API error');
    const data = await response.json();

    const set = (id, value) => { const el = document.getElementById(id); if (el) el.textContent = value; };
    set('totalStudents', data.total_students);
    set('presentToday', data.present_today);
    set('attendance', data.attendance + '%');
    set('onlineCameras', `${data.online_cameras}/25`);
    set('attention', data.attention + '%');
    set('onlineCount', data.online_cameras);
    set('offlineCount', data.offline_cameras);
    set('lastRefresh', new Date().toLocaleTimeString());

    const status = document.getElementById('systemStatus');
    if (status) status.textContent = data.online_cameras > 0 ? '● AI WORKER ONLINE' : '● WAITING FOR CAMERAS';

    const grid = document.getElementById('cameraGrid');
    if (grid) {
      grid.innerHTML = data.cameras.map(camera => {
        const preview = camera.stream_url
          ? `<img src="${camera.stream_url}" alt="Camera ${camera.id}" loading="lazy">`
          : `<div class="camera-preview">📷</div>`;
        return `<article class="camera-card">
          <div class="camera-preview">${preview}</div>
          <div class="camera-info">
            <h3>Camera ${camera.id} · ${camera.name}</h3>
            <div class="row"><span>Students</span><b>${camera.students}</b></div>
            <div class="row"><span>Attention</span><b>${camera.attention}%</b></div>
            <div class="row"><span>Activity</span><b>${camera.activity}</b></div>
            <div class="row"><span>Status</span><span class="status ${camera.status}">${camera.status}</span></div>
          </div>
        </article>`;
      }).join('');
    }
  } catch (error) {
    const status = document.getElementById('systemStatus');
    if (status) status.textContent = '● API ERROR';
    console.error(error);
  }
}

loadDashboard();
setInterval(loadDashboard, 5000);
