const ws = new WebSocket(`ws://${location.host}/ws`);

// DOM Elements
const brokerDot    = document.getElementById('brokerDot');
const brokerLabel  = document.getElementById('brokerLabel');
const btnReconnect = document.getElementById('btnReconnect');
const logContainer = document.getElementById('logContainer');
const logCount     = document.getElementById('logCount');

const rrCount = document.getElementById('rrCount');
const rrMsgs  = document.getElementById('rrMsgs');
const rrLat   = document.getElementById('rrLat');
const rrTput  = document.getElementById('rrTput');

const psCount = document.getElementById('psCount');
const psMsgs  = document.getElementById('psMsgs');
const psLat   = document.getElementById('psLat');
const psTput  = document.getElementById('psTput');

const modelRadios      = document.getElementsByName('modelType');
const topicGroup       = document.getElementById('topicGroup');
const topicSelect      = document.getElementById('topicSelect');
const delaySlider      = document.getElementById('delaySlider');
const delayVal         = document.getElementById('delayVal');
const countSlider      = document.getElementById('countSlider');
const countVal         = document.getElementById('countVal');
const activeModelLabel = document.getElementById('activeModelLabel');
const scenarioTitle    = document.getElementById('scenarioTitle');
const scenarioDesc     = document.getElementById('scenarioDesc');
const scenarioFlow     = document.getElementById('scenarioFlow');

// Canvas Setup
const canvas = document.getElementById('topologyCanvas');
const ctx    = canvas.getContext('2d');

// HD Canvas Scaling Fix
const dpr = window.devicePixelRatio || 1;
const logicalWidth = canvas.width;
const logicalHeight = canvas.height;
canvas.style.width = logicalWidth + 'px';
canvas.style.height = logicalHeight + 'px';
canvas.width = logicalWidth * dpr;
canvas.height = logicalHeight * dpr;
ctx.scale(dpr, dpr);

let particles = [];
let animId;
let totalLogs = 0;
// We store logical dimensions for clearRect
const CANVAS_LOGICAL_W = logicalWidth;
const CANVAS_LOGICAL_H = logicalHeight;

// State simulasi
let currentModel = 'rr';
let clientIdx    = 0;
let pubIdx       = 0;

// ─── Warna ───────────────────────────────────────────────────────────────────
const COLORS = {
    node:         '#111111',
    nodeBorder:   '#333333',
    text:         '#EDEDED',
    line:         '#1f1f1f',
    particle_req: '#3b82f6',   // biru  — order dikirim
    particle_res: '#10b981',   // hijau — konfirmasi balik
    particle_pub: '#f59e0b',   // kuning-oranye — siaran BMKG
    particle_sub: '#a78bfa',   // ungu  — diterima subscriber
    label_rr:     '#3b82f6',
    label_ps:     '#10b981',
    label_broker: '#f59e0b',
};

// ─── SVG Icons ───────────────────────────────────────────────────────────────
const SVG_DEFS = {
    // Smartphone (pelanggan)
    phone: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#EDEDED"><path d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/></svg>`,
    // Restaurant (server makanan)
    restaurant: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#EDEDED"><path d="M11 9H9V2H7v7H5V2H3v7c0 2.12 1.66 3.84 3.75 3.97V22h2.5v-9.03C11.34 12.84 13 11.12 13 9V2h-2v7zm5-3v8h2.5v8H21V2c-2.76 0-5 2.24-5 4z"/></svg>`,
    // Antenna (BMKG publisher)
    antenna: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#EDEDED"><path d="M12 11c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm6-4v2c2.76 0 5 2.24 5 5h2c0-3.87-3.13-7-7-7zm-4 2v2c1.66 0 3 1.34 3 3h2c0-2.76-2.24-5-5-5zm-8-2C2.13 7 -1 10.13 -1 14h2c0-2.76 2.24-5 5-5V9zm4 2c-2.76 0-5 2.24-5 5h2c1.66 0 3-1.34 3-3V11z"/></svg>`,
    // Broker / hub
    broker: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#EDEDED"><path d="M17 16l-4-4V8.82C14.16 8.4 15 7.3 15 6c0-1.66-1.34-3-3-3S9 4.34 9 6c0 1.3.84 2.4 2 2.82V12l-4 4H3v5h5v-3.05l4-4.2 4 4.2V21h5v-5h-4z"/></svg>`,
    // TV / media
    tv: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#EDEDED"><path d="M21 3H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h5v2h8v-2h5c1.1 0 1.99-.9 1.99-2L23 5c0-1.1-.9-2-2-2zm0 14H3V5h18v12z"/></svg>`,
    // Radio
    radio: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#EDEDED"><path d="M20 6h-8.586L13.5 3.914 12.086 2.5 8.5 6.086 4.914 2.5 3.5 3.914 5.586 6H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 14H4V8h16v12zM6.5 17h3v-2H8v-2h1.5v-2h-3v6zM18 11h-4v2h4v-2zm0 4h-4v2h4v-2z"/></svg>`,
    // Phone/app (AplikasiWarga)
    app: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#EDEDED"><path d="M4 8h4V4H4v4zm6 12h4v-4h-4v4zm-6 0h4v-4H4v4zm0-6h4v-4H4v4zm6 0h4v-4h-4v4zm6-10v4h4V4h-4zm-6 4h4V4h-4v4zm6 6h4v-4h-4v4zm0 6h4v-4h-4v4z"/></svg>`,
};

const IMAGES = {};
for (const [key, svg] of Object.entries(SVG_DEFS)) {
    const img  = new Image();
    img.src    = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
    IMAGES[key] = img;
}

// ─── Posisi Node Dunia Nyata ──────────────────────────────────────────────────
const RR_POS = {
    'pelanggan-A':   { x: 160, y: 150, imgKey: 'phone',      label: 'Pelanggan A',  sublabel: '(Pesan via App)',   color: COLORS.label_rr },
    'pelanggan-B':   { x: 160, y: 310, imgKey: 'phone',      label: 'Pelanggan B',  sublabel: '(Pesan via App)',   color: COLORS.label_rr },
    'restoran-padang': { x: 610, y: 230, imgKey: 'restaurant', label: 'Restoran Padang', sublabel: '(Server Penerima)', color: '#f59e0b' },
};

const PS_POS = {
    'bmkg-pusat':      { x: 120, y: 140, imgKey: 'antenna',  label: 'BMKG Pusat',      sublabel: '(Publisher)',       color: COLORS.label_ps },
    'sensor-lapangan': { x: 120, y: 320, imgKey: 'antenna',  label: 'Sensor Lapangan', sublabel: '(Publisher)',       color: COLORS.label_ps },
    'broker-mqtt':     { x: 390, y: 230, imgKey: 'broker',   label: 'MQTT Broker',     sublabel: '(Mosquitto)',       color: COLORS.label_broker },
    'MetroTV':         { x: 650, y: 100, imgKey: 'tv',        label: 'MetroTV',         sublabel: '(Subscriber)',      color: COLORS.label_ps },
    'RRI-Radio':       { x: 650, y: 230, imgKey: 'radio',     label: 'RRI Radio',       sublabel: '(Subscriber)',      color: COLORS.label_ps },
    'AplikasiWarga':   { x: 650, y: 360, imgKey: 'app',       label: 'Aplikasi Warga',  sublabel: '(Subscriber)',      color: COLORS.label_ps },
};

// ─── Skenario Info ────────────────────────────────────────────────────────────
const SCENARIOS = {
    rr: {
        title: 'Skenario: Aplikasi Pesan Makanan (seperti GoFood)',
        desc:  '<strong>Pelanggan-A</strong> & <strong>Pelanggan-B</strong> mengirim order ke <strong>Restoran Padang</strong>. Restoran memproses lalu membalas konfirmasi — sama persis seperti kamu pesan online!',
        flow:  [
            { step: 'Pelanggan kirim order', arrow: '→' },
            { step: 'Restoran proses pesanan', arrow: '→' },
            { step: 'Konfirmasi + ETA dikirim balik', arrow: null },
        ]
    },
    ps: {
        title: 'Skenario: Siaran Peringatan Bencana (seperti BMKG)',
        desc:  '<strong>BMKG Pusat</strong> & <strong>Sensor Lapangan</strong> mengirim data ke <strong>MQTT Broker</strong>. Broker meneruskan ke <strong>MetroTV, RRI Radio, & Aplikasi Warga</strong> sekaligus — seperti notif peringatan di HP-mu!',
        flow:  [
            { step: 'BMKG deteksi bencana', arrow: '→' },
            { step: 'Broker terima & sebarkan', arrow: '→' },
            { step: 'Media & Warga terima', arrow: null },
        ]
    }
};

function updateScenarioBanner(model) {
    const s = SCENARIOS[model];
    scenarioTitle.textContent  = s.title;
    scenarioDesc.innerHTML     = s.desc;
    // Buat flow steps
    scenarioFlow.innerHTML = s.flow.map(f =>
        `<span class="flow-step">${f.step}</span>` +
        (f.arrow ? `<span class="flow-arrow">${f.arrow}</span>` : '')
    ).join('');
}

// ─── WebSocket Handlers ───────────────────────────────────────────────────────
ws.onopen = () => {
    addLog('SYS', '🔌 Terhubung ke server simulasi...', 'sys');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'broker_status') {
        updateBrokerStatus(data);
    } else if (data.type === 'metric_update') {
        updateMetrics(data.summary);
        if (data.log) {
            const isRR = data.log.includes('[RR]');
            addLog(isRR ? 'RR' : 'PS', data.log, isRR ? 'rr' : 'ps');
        }
    } else if (data.type === 'animation') {
        spawnParticle(data);
        if (data.log) addLog(data.model.toUpperCase(), data.log, data.model);
    }
};

ws.onclose = () => {
    updateBrokerStatus({ is_connected: false, message: 'Koneksi ke server terputus.' });
};

// ─── GUI Updates ──────────────────────────────────────────────────────────────
function updateBrokerStatus(data) {
    brokerLabel.innerText  = data.message;
    brokerDot.className    = `status-indicator ${data.is_connected ? 'green' : 'red'}`;
    
    const disabled = !data.is_connected;
    ['btnSingle', 'btnStress'].forEach(id => {
        const btn = document.getElementById(id);
        btn.disabled       = disabled;
        btn.style.opacity  = disabled ? '0.4' : '1';
        btn.style.cursor   = disabled ? 'not-allowed' : 'pointer';
    });
}

let logEntryCount = 0;
function addLog(source, message, typeClass) {
    // Hapus placeholder
    const empty = logContainer.querySelector('.log-empty');
    if (empty) empty.remove();

    const el   = document.createElement('div');
    el.className = 'log-entry';
    const time = new Date().toLocaleTimeString('id-ID', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    el.innerHTML = `<span class="log-time">${time}</span> <span class="log-tag ${typeClass}">[${source}]</span> <span class="log-msg">${message}</span>`;
    logContainer.prepend(el);

    logEntryCount++;
    logCount.textContent = `${logEntryCount} pesan`;
    if (logContainer.children.length > 120) logContainer.removeChild(logContainer.lastChild);
}

function updateMetrics(summary) {
    const rr = summary.rr;
    rrCount.innerText = rr.count;
    rrMsgs.innerText  = rr.total_msgs;
    rrLat.innerText   = rr.avg_lat.toFixed(1);
    rrTput.innerText  = rr.throughput.toFixed(1);

    const ps = summary.ps;
    psCount.innerText = ps.count;
    psMsgs.innerText  = ps.total_msgs;
    psLat.innerText   = ps.avg_lat.toFixed(1);
    psTput.innerText  = ps.throughput.toFixed(1);
}

// ─── Control Listeners ────────────────────────────────────────────────────────
delaySlider.addEventListener('input', e => delayVal.innerText = e.target.value);
countSlider.addEventListener('input', e => countVal.innerText = e.target.value);

for (let r of modelRadios) {
    r.addEventListener('change', e => {
        currentModel = e.target.value;
        topicGroup.style.display    = currentModel === 'ps' ? 'block' : 'none';
        activeModelLabel.innerText  = currentModel === 'rr' ? 'Request-Response' : 'Publish-Subscribe';
        updateScenarioBanner(currentModel);
        drawTopology();
    });
}

document.getElementById('btnSingle').addEventListener('click', () => {
    if (currentModel === 'rr') {
        ws.send(JSON.stringify({
            action:     'trigger_rr',
            client_idx: clientIdx++,
            delay:      delaySlider.value,
            payload:    ''  // backend akan pilih payload realistis
        }));
    } else {
        ws.send(JSON.stringify({
            action:   'trigger_ps',
            pub_idx:  pubIdx++,
            delay:    delaySlider.value,
            topic:    topicSelect.value,
            payload:  ''  // backend akan pilih payload realistis
        }));
    }
});

document.getElementById('btnStress').addEventListener('click', () => {
    ws.send(JSON.stringify({
        action: 'stress_test',
        model:  currentModel,
        count:  countSlider.value,
        delay:  delaySlider.value
    }));
});

document.getElementById('btnReset').addEventListener('click', () => {
    ws.send(JSON.stringify({ action: 'reset' }));
    logContainer.innerHTML = '<div class="log-empty">Semua data direset. Siap memulai ulang.</div>';
    logEntryCount = 0;
    logCount.textContent = '0 pesan';
});

btnReconnect.addEventListener('click', () => {
    ws.send(JSON.stringify({ action: 'reconnect' }));
});

// ─── Canvas Drawing ───────────────────────────────────────────────────────────
function drawNode(x, y, imgKey, label, sublabel, accentColor) {
    const R = 28;

    // Halo glow sesuai accent
    ctx.beginPath();
    ctx.arc(x, y, R + 4, 0, Math.PI * 2);
    ctx.fillStyle = (accentColor + '18') || 'rgba(255,255,255,0.05)';
    ctx.fill();

    // Node circle
    ctx.beginPath();
    ctx.arc(x, y, R, 0, Math.PI * 2);
    ctx.fillStyle = '#111111';
    ctx.fill();
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = accentColor || COLORS.nodeBorder;
    ctx.stroke();

    // Icon
    const img = IMAGES[imgKey];
    if (img && img.complete) ctx.drawImage(img, x - 13, y - 13, 26, 26);

    // Label
    ctx.textAlign = 'center';
    ctx.font = '600 11px "Inter", sans-serif';
    ctx.fillStyle = '#EDEDED';
    ctx.fillText(label, x, y + R + 16);

    // Sublabel
    if (sublabel) {
        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.fillStyle = '#555555';
        ctx.fillText(sublabel, x, y + R + 29);
    }
}

function drawLine(x1, y1, x2, y2, dashed = false) {
    ctx.beginPath();
    ctx.setLineDash(dashed ? [4, 6] : []);
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.strokeStyle = '#222222';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.setLineDash([]);
}

function drawTopology() {
    ctx.clearRect(0, 0, CANVAS_LOGICAL_W, CANVAS_LOGICAL_H);
    const pos = currentModel === 'rr' ? RR_POS : PS_POS;

    // Draw Lines (dashed untuk PS menunjukkan "subscribe")
    if (currentModel === 'rr') {
        const s = pos['restoran-padang'];
        ['pelanggan-A', 'pelanggan-B'].forEach(id => drawLine(pos[id].x, pos[id].y, s.x, s.y));
    } else {
        const b = pos['broker-mqtt'];
        ['bmkg-pusat', 'sensor-lapangan'].forEach(id => drawLine(pos[id].x, pos[id].y, b.x, b.y));
        ['MetroTV', 'RRI-Radio', 'AplikasiWarga'].forEach(id => drawLine(b.x, b.y, pos[id].x, pos[id].y, true));
    }

    // Draw Nodes
    for (const id in pos) {
        const n = pos[id];
        drawNode(n.x, n.y, n.imgKey, n.label, n.sublabel, n.color);
    }

    // Legend
    drawLegend();
}

function drawLegend() {
    const items = currentModel === 'rr'
        ? [
            { color: COLORS.particle_req, label: 'Order dikirim (request)' },
            { color: COLORS.particle_res, label: 'Konfirmasi balik (response)' },
          ]
        : [
            { color: COLORS.particle_pub, label: 'Data dikirim ke Broker' },
            { color: COLORS.particle_sub, label: 'Siaran ke Subscriber' },
          ];

    let lx = 16, ly = CANVAS_LOGICAL_H - 30;
    ctx.font = '10px "JetBrains Mono", monospace';
    items.forEach(item => {
        ctx.beginPath();
        ctx.arc(lx + 5, ly + 5, 4, 0, Math.PI * 2);
        ctx.fillStyle = item.color;
        ctx.fill();
        ctx.fillStyle = '#555555';
        ctx.textAlign = 'left';
        ctx.fillText(item.label, lx + 14, ly + 9);
        lx += ctx.measureText(item.label).width + 30;
    });
}

function spawnParticle(data) {
    const pos = currentModel === 'rr' ? RR_POS : PS_POS;
    const src = pos[data.src];
    const dst = pos[data.dst];
    if (!src || !dst) return;

    let color = COLORS.particle_req;
    if (data.event_type.includes('res'))       color = COLORS.particle_res;
    else if (data.event_type.includes('pub'))  color = COLORS.particle_pub;
    else if (data.event_type.includes('broadcast')) color = COLORS.particle_sub;

    particles.push({
        sx: src.x, sy: src.y,
        tx: dst.x, ty: dst.y,
        color,
        start:    performance.now(),
        duration: Math.max(400, parseInt(delaySlider.value)),
        label:    data.msg ? data.msg.substring(0, 22) + (data.msg.length > 22 ? '…' : '') : '',
    });
}

function animateParticles(time) {
    drawTopology();

    for (let i = particles.length - 1; i >= 0; i--) {
        const p        = particles[i];
        const progress = (time - p.start) / p.duration;

        if (progress >= 1) { particles.splice(i, 1); continue; }

        // Ease in-out
        const t  = progress < 0.5 ? 2 * progress * progress : -1 + (4 - 2 * progress) * progress;
        const cx = p.sx + (p.tx - p.sx) * t;
        const cy = p.sy + (p.ty - p.sy) * t;

        // Trail
        const t2 = Math.max(0, progress - 0.12);
        const te = t2 < 0.5 ? 2 * t2 * t2 : -1 + (4 - 2 * t2) * t2;
        const tx2 = p.sx + (p.tx - p.sx) * te;
        const ty2 = p.sy + (p.ty - p.sy) * te;

        ctx.beginPath();
        ctx.moveTo(tx2, ty2);
        ctx.lineTo(cx, cy);
        const grad = ctx.createLinearGradient(tx2, ty2, cx, cy);
        grad.addColorStop(0, 'transparent');
        grad.addColorStop(1, p.color);
        ctx.strokeStyle = grad;
        ctx.lineWidth   = 2.5;
        ctx.lineCap     = 'round';
        ctx.stroke();

        // Head
        ctx.beginPath();
        ctx.arc(cx, cy, 4, 0, Math.PI * 2);
        ctx.fillStyle   = p.color;
        ctx.shadowBlur  = 12;
        ctx.shadowColor = p.color;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Payload label on particle (muncul di tengah perjalanan)
        if (progress > 0.3 && progress < 0.75 && p.label) {
            ctx.font = '9px "JetBrains Mono", monospace';
            ctx.fillStyle = '#AAAAAA';
            ctx.textAlign = 'center';
            ctx.fillText(p.label, cx, cy - 12);
        }
    }

    animId = requestAnimationFrame(animateParticles);
}

// ─── Init ─────────────────────────────────────────────────────────────────────
updateScenarioBanner('rr');
drawTopology();
animId = requestAnimationFrame(animateParticles);
