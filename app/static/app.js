const statusEl = document.getElementById('status');
const platformList = document.getElementById('platform-list');
const tradeBody = document.getElementById('trade-body');
const openBody = document.getElementById('open-body');
const statsBody = document.getElementById('stats-body');
const calendar = document.getElementById('calendar');
let selectedPeriod = 'day';

async function fetchPlatforms() {
  const res = await fetch('/api/platforms');
  const data = await res.json();
  platformList.innerHTML = '';

  data.forEach((p) => {
    const li = document.createElement('li');

    const syncBtn = document.createElement('button');
    syncBtn.innerText = `Sync Closed ${p.name}`;
    syncBtn.onclick = async () => {
      syncBtn.disabled = true;
      syncBtn.innerText = `Sync läuft...`;
      const syncRes = await fetch(`/api/platforms/${p.id}/sync`, { method: 'POST' });
      const syncData = await syncRes.json();
      if (!syncRes.ok) {
        statusEl.innerText = syncData.detail || 'Sync fehlgeschlagen';
        syncBtn.disabled = false;
        syncBtn.innerText = `Sync Closed ${p.name}`;
        return;
      }
      statusEl.innerText = `Closed Sync: fetched=${syncData.fetched}, normalized=${syncData.normalized}, importiert=${syncData.imported}, übersprungen=${syncData.skipped}`;
      await fetchTrades();
      await fetchStats(selectedPeriod);
      syncBtn.disabled = false;
      syncBtn.innerText = `Sync Closed ${p.name}`;
    };

    const openBtn = document.createElement('button');
    openBtn.innerText = `Load Open ${p.name}`;
    openBtn.onclick = async () => {
      const resOpen = await fetch(`/api/platforms/${p.id}/open-positions`);
      const dataOpen = await resOpen.json();
      if (!resOpen.ok) {
        statusEl.innerText = dataOpen.detail || 'Open-Positionen Laden fehlgeschlagen';
        return;
      }
      renderOpenPositions(dataOpen, p.name);
    };

    li.innerText = `${p.name} (${p.platform_type}, ${p.demo_mode ? 'Demo' : 'Live'}) `;
    li.appendChild(syncBtn);
    li.appendChild(openBtn);
    platformList.appendChild(li);
  });
}

function renderOpenPositions(rows, platformName) {
  openBody.innerHTML = '';
  rows.forEach((r) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${platformName}</td><td>${r.symbol}</td><td>${r.direction}</td><td>${r.quantity}</td><td>${r.entry_price}</td><td>${r.current_price}</td><td>${r.unrealized_pnl}</td><td>${new Date(r.opened_at).toLocaleString()}</td>`;
    openBody.appendChild(tr);
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

async function fetchStats(period) {
  selectedPeriod = period;
  const res = await fetch(`/api/stats?period=${period}`);
  const data = await res.json();
  statsBody.innerHTML = '';
  calendar.innerHTML = '';

  data.forEach((s) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${s.period}</td><td>${s.pnl_money}</td><td>${s.pnl_percent}</td><td>${s.trades}</td><td>${s.winrate_percent}</td><td>${s.profit_factor}</td>`;
    statsBody.appendChild(tr);

    const card = document.createElement('div');
    card.className = `cell ${s.pnl_money >= 0 ? 'pos' : 'neg'}`;
    card.innerHTML = `<strong>${s.period}</strong><br/>${s.pnl_money} €`;
    calendar.appendChild(card);
  });
}

document.getElementById('period-day').onclick = () => fetchStats('day');
document.getElementById('period-month').onclick = () => fetchStats('month');
document.getElementById('period-year').onclick = () => fetchStats('year');

document.getElementById('platform-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const payload = {
    name: formData.get('name'),
    platform_type: formData.get('platform_type'),
    api_base_url: formData.get('api_base_url') || null,
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
fetchStats('day');
