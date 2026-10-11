// ═══════════════════════════════════════════════════════════════
//  OTP IVA SMS - ADMIN DASHBOARD CLIENT JAVASCRIPT
// ═══════════════════════════════════════════════════════════════

let currentPage = 'dashboard';
let currentSmsPage = 1;
let autoAddInterval = null;
let logPollInterval = null;
let statusPollInterval = null;

// ────────────────────────────────────────────
//  UI UTILS & TOASTS
// ────────────────────────────────────────────

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';

    toast.innerHTML = `
        <div class="toast-icon"><i class="fas fa-${icon}"></i></div>
        <div class="toast-body">
            <div class="toast-msg">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 400);
    }, 4500);
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const main = document.getElementById('mainContent');
    if (sidebar) sidebar.classList.toggle('collapsed');
    if (main) main.classList.toggle('expanded');
}

function updateClock() {
    const clockEl = document.getElementById('currentTime');
    if (clockEl) {
        const now = new Date();
        clockEl.textContent = now.toLocaleTimeString('id-ID', { hour12: false }) + ' WIB';
    }
}
setInterval(updateClock, 1000);
updateClock();

// ────────────────────────────────────────────
//  PAGE INITIALIZATION
// ────────────────────────────────────────────

function initPage(page) {
    currentPage = page;
    checkGlobalConnection();
    statusPollInterval = setInterval(checkGlobalConnection, 15000);

    if (page === 'dashboard') {
        loadDashboard();
        refreshLogs();
        setInterval(loadDashboard, 8000);
        setInterval(refreshLogs, 6000);
    } else if (page === 'sms-log') {
        loadSmsLog(1);
    } else if (page === 'auto-add') {
        checkAutoAddStatus();
        autoAddInterval = setInterval(checkAutoAddStatus, 3000);
    } else if (page === 'bot-control') {
        loadBotControl();
        refreshLogs();
        setInterval(loadBotControl, 5000);
        setInterval(refreshLogs, 4000);
    } else if (page === 'settings') {
        loadSettings();
    }
}

// ────────────────────────────────────────────
//  GLOBAL STATUS
// ────────────────────────────────────────────

async function checkGlobalConnection() {
    try {
        const res = await fetch('/api/dashboard');
        const data = await res.json();
        const indicator = document.getElementById('connectionStatus');
        if (!indicator) return;

        const isOnline = data.stats && (data.stats.bot_running || data.stats.ivasms_connected);
        const dot = indicator.querySelector('.status-dot');
        const span = indicator.querySelector('span');

        if (dot && span) {
            if (data.stats.bot_running) {
                dot.className = 'status-dot online';
                span.textContent = 'Bot Running';
            } else if (data.stats.ivasms_connected) {
                dot.className = 'status-dot online';
                span.textContent = 'IVASMS Ready';
            } else {
                dot.className = 'status-dot offline';
                span.textContent = 'Bot Offline';
            }
        }
    } catch (e) {
        const indicator = document.getElementById('connectionStatus');
        if (indicator) {
            const dot = indicator.querySelector('.status-dot');
            const span = indicator.querySelector('span');
            if (dot && span) {
                dot.className = 'status-dot offline';
                span.textContent = 'Server Offline';
            }
        }
    }
}

// ────────────────────────────────────────────
//  DASHBOARD
// ────────────────────────────────────────────

async function loadDashboard() {
    try {
        const res = await fetch('/api/dashboard');
        const data = await res.json();

        // Stats
        const statOtp = document.getElementById('statOtp');
        const statBot = document.getElementById('statBot');
        const statBotBadge = document.getElementById('statBotBadge');
        const statIvasms = document.getElementById('statIvasms');
        const statIvasmsBadge = document.getElementById('statIvasmsBadge');
        const statErrors = document.getElementById('statErrors');

        if (statOtp) statOtp.textContent = data.stats.otp_received || 0;
        if (statErrors) statErrors.textContent = data.stats.errors || 0;

        if (statBot) statBot.textContent = data.stats.bot_running ? 'Online' : 'Offline';
        if (statBotBadge) {
            statBotBadge.textContent = data.stats.bot_running ? 'Running' : 'Stopped';
            statBotBadge.className = `stat-badge ${data.stats.bot_running ? 'active' : 'inactive'}`;
        }

        if (statIvasms) statIvasms.textContent = data.stats.ivasms_connected ? 'Connected' : 'Disconnected';
        if (statIvasmsBadge) {
            statIvasmsBadge.textContent = data.stats.ivasms_connected ? 'Session OK' : 'Needs Sync';
            statIvasmsBadge.className = `stat-badge ${data.stats.ivasms_connected ? 'active' : 'inactive'}`;
        }

        // Recent Activity
        const activityList = document.getElementById('recentActivity');
        if (activityList && data.recent_logs) {
            if (data.recent_logs.length === 0) {
                activityList.innerHTML = '<div class="empty-state">No recent activity detected.</div>';
            } else {
                activityList.innerHTML = data.recent_logs.map(item => `
                    <div class="activity-item">
                        <div class="activity-badge badge-${item.type || 'info'}">
                            <i class="fas fa-${item.type === 'otp' ? 'key' : item.type === 'error' ? 'exclamation' : 'info'}"></i>
                        </div>
                        <div class="activity-content">
                            <div class="activity-msg">${escapeHtml(item.message)}</div>
                            <div class="activity-time">${item.timestamp || 'Just now'}</div>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (e) {
        console.error('Failed to load dashboard:', e);
    }
}

function refreshDashboard() {
    loadDashboard();
    refreshLogs();
    showToast('Dashboard refreshed', 'info');
}

// ────────────────────────────────────────────
//  LOG TERMINAL
// ────────────────────────────────────────────

async function refreshLogs() {
    try {
        const res = await fetch('/api/logs/tail?n=40');
        const data = await res.json();
        
        const terminals = [
            document.getElementById('logTerminal'),
            document.getElementById('logTerminalBot')
        ];

        terminals.forEach(term => {
            if (!term) return;
            if (!data.lines || data.lines.length === 0) {
                term.innerHTML = '<div class="log-line text-muted">No log output yet...</div>';
                return;
            }

            term.innerHTML = data.lines.map(line => {
                let cls = 'log-line';
                if (line.includes('ERROR') || line.includes('error')) cls += ' log-error';
                else if (line.includes('WARNING') || line.includes('warn')) cls += ' log-warn';
                else if (line.includes('New OTP') || line.includes('Forwarded')) cls += ' log-success';
                return `<div class="${cls}">${escapeHtml(line)}</div>`;
            }).join('');

            const autoScrollCheckbox = document.getElementById('autoScroll');
            if (!autoScrollCheckbox || autoScrollCheckbox.checked) {
                term.scrollTop = term.scrollHeight;
            }
        });
    } catch (e) {
        console.error('Error fetching logs:', e);
    }
}

// ────────────────────────────────────────────
//  SMS LOG
// ────────────────────────────────────────────

let allSmsEntries = [];

async function loadSmsLog(page = 1) {
    currentSmsPage = page;
    const tbody = document.getElementById('smsTableBody');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="3" class="text-center"><i class="fas fa-circle-notch fa-spin"></i> Loading entries...</td></tr>';

    try {
        const res = await fetch(`/api/sms-log?page=${page}&per_page=20`);
        const data = await res.json();

        allSmsEntries = data.entries || [];
        renderSmsTable(allSmsEntries);
        renderPagination(data.total_pages, data.page);
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="3" class="text-center text-danger">Gagal memuat log SMS: ${e.message}</td></tr>`;
    }
}

function renderSmsTable(entries) {
    const tbody = document.getElementById('smsTableBody');
    if (!tbody) return;

    if (entries.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">Tidak ada SMS tercatat.</td></tr>';
        return;
    }

    tbody.innerHTML = entries.map(item => {
        let typeBadge = `<span class="badge badge-info">${item.type}</span>`;
        if (item.type === 'otp') typeBadge = `<span class="badge badge-success">OTP</span>`;
        if (item.type === 'error') typeBadge = `<span class="badge badge-danger">ERROR</span>`;

        return `
            <tr>
                <td class="mono text-muted">${escapeHtml(item.timestamp || '-')}</td>
                <td>${typeBadge}</td>
                <td class="selectable">${formatSmsMessage(item.message)}</td>
            </tr>
        `;
    }).join('');
}

function formatSmsMessage(msg) {
    const escaped = escapeHtml(msg);
    // Highlight codes if found
    return escaped.replace(/(\b\d{4,8}\b)/g, '<mark class="code-highlight" title="Click to copy" onclick="copyText(\'$1\')">$1</mark>');
}

function filterSmsLog() {
    const query = (document.getElementById('smsSearch')?.value || '').toLowerCase();
    if (!query) {
        renderSmsTable(allSmsEntries);
        return;
    }

    const filtered = allSmsEntries.filter(e => 
        (e.message && e.message.toLowerCase().includes(query)) ||
        (e.timestamp && e.timestamp.toLowerCase().includes(query)) ||
        (e.type && e.type.toLowerCase().includes(query))
    );
    renderSmsTable(filtered);
}

function renderPagination(totalPages, page) {
    const pagContainer = document.getElementById('smsPagination');
    if (!pagContainer) return;

    if (!totalPages || totalPages <= 1) {
        pagContainer.innerHTML = '';
        return;
    }

    let html = '';
    if (page > 1) {
        html += `<button class="page-btn" onclick="loadSmsLog(${page - 1})"><i class="fas fa-chevron-left"></i> Prev</button>`;
    }
    html += `<span class="page-info">Halaman ${page} dari ${totalPages}</span>`;
    if (page < totalPages) {
        html += `<button class="page-btn" onclick="loadSmsLog(${page + 1})">Next <i class="fas fa-chevron-right"></i></button>`;
    }

    pagContainer.innerHTML = html;
}

function copyText(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast(`Disalin: ${text}`, 'success');
    }).catch(() => {
        showToast('Gagal menyalin', 'error');
    });
}

// ────────────────────────────────────────────
//  AUTO-ADD NUMBERS
// ────────────────────────────────────────────

async function startAutoAdd() {
    const rangeName = document.getElementById('addRangeName')?.value.trim();
    const maxAdd = parseInt(document.getElementById('addMaxAdd')?.value || '0', 10);
    const delay = parseInt(document.getElementById('addDelay')?.value || '60', 10);

    if (!rangeName) {
        showToast('Harap masukkan Range Name!', 'warning');
        return;
    }

    const btnStart = document.getElementById('btnStartAdd');
    const btnStop = document.getElementById('btnStopAdd');
    if (btnStart) btnStart.disabled = true;

    try {
        const res = await fetch('/api/auto-add/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ range_name: rangeName, max_add: maxAdd, delay: delay })
        });
        const data = await res.json();

        if (data.success) {
            showToast(data.message, 'success');
            if (btnStart) btnStart.style.display = 'none';
            if (btnStop) btnStop.style.display = 'inline-flex';
            checkAutoAddStatus();
        } else {
            showToast(data.message, 'error');
            if (btnStart) btnStart.disabled = false;
        }
    } catch (e) {
        showToast(`Error: ${e.message}`, 'error');
        if (btnStart) btnStart.disabled = false;
    }
}

async function stopAutoAdd() {
    const btnStop = document.getElementById('btnStopAdd');
    if (btnStop) btnStop.disabled = true;

    try {
        const res = await fetch('/api/auto-add/stop', { method: 'POST' });
        const data = await res.json();
        showToast(data.message, 'info');
        checkAutoAddStatus();
    } catch (e) {
        showToast(`Error: ${e.message}`, 'error');
    } finally {
        if (btnStop) btnStop.disabled = false;
    }
}

async function checkAutoAddStatus() {
    try {
        const res = await fetch('/api/auto-add/status');
        const state = await res.json();

        const btnStart = document.getElementById('btnStartAdd');
        const btnStop = document.getElementById('btnStopAdd');
        const badge = document.getElementById('autoAddStatus');
        const statAdded = document.getElementById('addStatAdded');
        const statFailed = document.getElementById('addStatFailed');
        const statSkipped = document.getElementById('addStatSkipped');
        const statTotal = document.getElementById('addStatTotal');
        const bar = document.getElementById('addProgressBar');
        const msg = document.getElementById('addLastMessage');

        if (state.running) {
            if (btnStart) { btnStart.style.display = 'none'; btnStart.disabled = false; }
            if (btnStop) { btnStop.style.display = 'inline-flex'; }
            if (badge) { badge.textContent = 'Running'; badge.className = 'status-badge active'; }
        } else {
            if (btnStart) { btnStart.style.display = 'inline-flex'; btnStart.disabled = false; }
            if (btnStop) { btnStop.style.display = 'none'; }
            if (badge) { badge.textContent = 'Idle'; badge.className = 'status-badge'; }
        }

        if (statAdded) statAdded.textContent = state.added || 0;
        if (statFailed) statFailed.textContent = state.failed || 0;
        if (statSkipped) statSkipped.textContent = state.skipped || 0;
        if (statTotal) statTotal.textContent = state.total_found || 0;

        if (msg && state.last_message) {
            msg.innerHTML = `<i class="fas fa-terminal"></i> ${escapeHtml(state.last_message)}`;
        }

        if (bar) {
            const target = state.max_add > 0 ? state.max_add : state.total_found;
            if (target > 0) {
                const pct = Math.min(100, Math.round(((state.added + state.skipped) / target) * 100));
                bar.style.width = `${pct}%`;
            } else {
                bar.style.width = state.running ? '50%' : '0%';
            }
        }
    } catch (e) {
        console.error('Failed to get auto-add status:', e);
    }
}

// ────────────────────────────────────────────
//  BOT CONTROL
// ────────────────────────────────────────────

async function loadBotControl() {
    try {
        const res = await fetch('/api/bot/status');
        const status = await res.json();

        const icon = document.getElementById('botIcon');
        const text = document.getElementById('botStatusText');
        const desc = document.getElementById('botStatusDesc');
        const btnStart = document.getElementById('btnStartBot');
        const btnStop = document.getElementById('btnStopBot');

        if (status.running) {
            if (icon) icon.className = 'bot-icon online';
            if (text) text.textContent = 'Bot Sedang Berjalan';
            if (desc) desc.textContent = `PID: ${status.pid} • Aktif sejak ${status.started_at || 'sekarang'}`;
            if (btnStart) btnStart.disabled = true;
            if (btnStop) btnStop.disabled = false;
        } else {
            if (icon) icon.className = 'bot-icon offline';
            if (text) text.textContent = 'Bot Berhenti';
            if (desc) desc.textContent = 'Proses bot.py tidak sedang berjalan.';
            if (btnStart) btnStart.disabled = false;
            if (btnStop) btnStop.disabled = true;
        }
    } catch (e) {
        console.error('Error fetching bot status:', e);
    }
}

async function startBot() {
    const btn = document.getElementById('btnStartBot');
    if (btn) btn.disabled = true;

    try {
        const res = await fetch('/api/bot/start', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'error');
        }
        loadBotControl();
    } catch (e) {
        showToast(`Error: ${e.message}`, 'error');
        if (btn) btn.disabled = false;
    }
}

async function stopBot() {
    const btn = document.getElementById('btnStopBot');
    if (btn) btn.disabled = true;

    try {
        const res = await fetch('/api/bot/stop', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'error');
        }
        loadBotControl();
    } catch (e) {
        showToast(`Error: ${e.message}`, 'error');
        if (btn) btn.disabled = false;
    }
}

async function checkIvasms() {
    const text = document.getElementById('ivasmsStatusText');
    const desc = document.getElementById('ivasmsStatusDesc');
    const icon = document.getElementById('ivasmsIcon');

    if (text) text.textContent = 'Memeriksa...';
    if (desc) desc.textContent = 'Membuka browser & mengambil cookies sesi...';

    try {
        const res = await fetch('/api/ivasms/check', { method: 'POST' });
        const data = await res.json();

        if (data.success && data.status && data.status.connected) {
            if (icon) icon.className = 'bot-icon online';
            if (text) text.textContent = 'IVASMS Terhubung';
            if (desc) desc.textContent = `Cookies valid • Dicek: ${data.status.last_check}`;
            showToast('Koneksi IVASMS valid & aktif!', 'success');
        } else {
            if (icon) icon.className = 'bot-icon offline';
            if (text) text.textContent = 'IVASMS Terputus';
            if (desc) desc.textContent = 'Sesi expired atau kredensial salah.';
            showToast('Sesi IVASMS tidak terhubung!', 'warning');
        }
    } catch (e) {
        showToast(`Gagal cek IVASMS: ${e.message}`, 'error');
    }
}

// ────────────────────────────────────────────
//  SETTINGS
// ────────────────────────────────────────────

async function loadSettings() {
    try {
        const res = await fetch('/api/config');
        const cfg = await res.json();

        if (document.getElementById('cfgBotToken')) document.getElementById('cfgBotToken').value = cfg.BOT_TOKEN || '';
        if (document.getElementById('cfgGroupChatId')) document.getElementById('cfgGroupChatId').value = cfg.GROUP_CHAT_ID || '';
        if (document.getElementById('cfgGroupLink')) document.getElementById('cfgGroupLink').value = cfg.GROUP_LINK || '';
        if (document.getElementById('cfgBotName')) document.getElementById('cfgBotName').value = cfg.BOT_NAME || '';
        if (document.getElementById('cfgPollInterval')) document.getElementById('cfgPollInterval').value = cfg.POLL_INTERVAL || '10';
        if (document.getElementById('cfgEmail')) document.getElementById('cfgEmail').value = cfg.IVASMS_EMAIL || '';
        if (document.getElementById('cfgPassword')) document.getElementById('cfgPassword').value = cfg.IVASMS_PASSWORD || '';
        if (document.getElementById('cfgNumberLink')) document.getElementById('cfgNumberLink').value = cfg.NUMBER_LINK || '';
        if (document.getElementById('cfgOwnerLink')) document.getElementById('cfgOwnerLink').value = cfg.OWNER_LINK || '';
    } catch (e) {
        showToast('Gagal memuat konfigurasi: ' + e.message, 'error');
    }
}

async function saveSettings() {
    const payload = {
        BOT_TOKEN: document.getElementById('cfgBotToken')?.value.trim(),
        GROUP_CHAT_ID: document.getElementById('cfgGroupChatId')?.value.trim(),
        GROUP_LINK: document.getElementById('cfgGroupLink')?.value.trim(),
        BOT_NAME: document.getElementById('cfgBotName')?.value.trim(),
        POLL_INTERVAL: parseInt(document.getElementById('cfgPollInterval')?.value || '10', 10),
        IVASMS_EMAIL: document.getElementById('cfgEmail')?.value.trim(),
        IVASMS_PASSWORD: document.getElementById('cfgPassword')?.value.trim(),
        NUMBER_LINK: document.getElementById('cfgNumberLink')?.value.trim(),
        OWNER_LINK: document.getElementById('cfgOwnerLink')?.value.trim(),
    };

    try {
        const res = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.success) {
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'error');
        }
    } catch (e) {
        showToast('Gagal menyimpan: ' + e.message, 'error');
    }
}

function togglePasswordVisibility() {
    const input = document.getElementById('cfgPassword');
    const icon = document.getElementById('pwdToggleIcon');
    if (!input || !icon) return;

    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

// ────────────────────────────────────────────
//  HELPERS
// ────────────────────────────────────────────

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
