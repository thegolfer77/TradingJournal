const statusEl = document.getElementById('status');
const platformList = document.getElementById('platform-list');
const tradeBody = document.getElementById('trade-body');

async function fetchPlatforms() {
  const res = await fetch('/api/platforms');
  const data = await res.json();
  platformList.innerHTML = '';

  data.forEach((p) => {
    const li = document.createElement('li');
    const btn = document.createElement('button');
    btn.innerText = `Sync ${p.name}`;
    btn.onclick = async () => {
      const syncRes = await fetch(`/api/platforms/${p.id}/sync`, { method: 'POST' });
      const syncData = await syncRes.json();
      if (!syncRes.ok) {
        statusEl.innerText = syncData.detail || 'Sync fehlgeschlagen';
        return;
      }
      statusEl.innerText = `Sync: ${syncData.imported} importiert, ${syncData.skipped} übersprungen`;
      await fetchTrades();
    };
    li.innerText = `${p.name} (${p.platform_type}) `;
    li.appendChild(btn);
    platformList.appendChild(li);
  });
}

async function fetchTrades() {
  const res = await fetch('/api/trades');
  const data = await res.json();
  tradeBody.innerHTML = '';
  data.forEach((t) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${t.symbol}</td><td>${t.direction}</td><td>${t.quantity}</td><td>${t.entry_price}</td><td>${t.exit_price}</td><td>${t.pnl}</td><td>${new Date(t.closed_at).toLocaleString()}</td>`;
    tradeBody.appendChild(tr);
  });
}

document.getElementById('platform-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const payload = {
    name: formData.get('name'),
    platform_type: formData.get('platform_type'),
    api_key: formData.get('api_key') || null,
    identifier: formData.get('identifier') || null,
    password: formData.get('password') || null,
    demo_mode: formData.get('demo_mode') === 'on',
  };

  const res = await fetch('/api/platforms', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json();
    statusEl.innerText = err.detail || 'Speichern fehlgeschlagen';
    return;
  }

  statusEl.innerText = 'Plattform gespeichert';
  e.target.reset();
  await fetchPlatforms();
});

fetchPlatforms();
fetchTrades();
