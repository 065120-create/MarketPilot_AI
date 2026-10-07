/* ============================================================
   MarketPilot AI - Main Application JavaScript
   ============================================================ */

const API_BASE = '/api';

// ============================================================
// STATE MANAGEMENT
// ============================================================
const AppState = {
    currentJob: null,
    campaign: null,
    datasets: {},
    corrections: [],
    results: null,
    agentLogs: [],
    theme: localStorage.getItem('mp-theme') || 'dark',
    pollInterval: null,
};

// ============================================================
// API CLIENT
// ============================================================
const API = {
    async post(endpoint, data = {}) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                const err = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(err.detail || 'Request failed');
            }
            return await response.json();
        } catch (error) {
            console.error(`API POST ${endpoint}:`, error);
            showNotification(error.message, 'error');
            throw error;
        }
    },
    
    async get(endpoint) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`);
            if (!response.ok) {
                const err = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(err.detail || 'Request failed');
            }
            return await response.json();
        } catch (error) {
            console.error(`API GET ${endpoint}:`, error);
            throw error;
        }
    },
    
    async upload(endpoint, formData) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                body: formData
            });
            if (!response.ok) throw new Error('Upload failed');
            return await response.json();
        } catch (error) {
            console.error(`API Upload ${endpoint}:`, error);
            showNotification(error.message, 'error');
            throw error;
        }
    }
};

// ============================================================
// THEME MANAGEMENT
// ============================================================
function initTheme() {
    document.documentElement.setAttribute('data-theme', AppState.theme);
    const toggleBtn = document.querySelector('.theme-toggle');
    if (toggleBtn) {
        toggleBtn.textContent = AppState.theme === 'dark' ? '☀️' : '🌙';
    }
}

function toggleTheme() {
    AppState.theme = AppState.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', AppState.theme);
    localStorage.setItem('mp-theme', AppState.theme);
    const toggleBtn = document.querySelector('.theme-toggle');
    if (toggleBtn) {
        toggleBtn.textContent = AppState.theme === 'dark' ? '☀️' : '🌙';
    }
}

// ============================================================
// NOTIFICATIONS
// ============================================================
function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notification-container') || createNotificationContainer();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    container.appendChild(toast);
    
    requestAnimationFrame(() => toast.classList.add('toast-visible'));
    
    if (duration > 0) {
        setTimeout(() => {
            toast.classList.remove('toast-visible');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

function createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'notification-container';
    container.style.cssText = 'position:fixed;top:20px;right:20px;z-index:10000;display:flex;flex-direction:column;gap:8px;';
    document.body.appendChild(container);
    return container;
}

// ============================================================
// FORMATTING UTILITIES
// ============================================================
function formatCurrency(amount, symbol = '₹') {
    if (amount === null || amount === undefined) return `${symbol}0`;
    const num = Number(amount);
    if (num >= 10000000) return `${symbol}${(num/10000000).toFixed(2)} Cr`;
    if (num >= 100000) return `${symbol}${(num/100000).toFixed(2)} L`;
    if (num >= 1000) return `${symbol}${(num/1000).toFixed(1)}K`;
    return `${symbol}${num.toLocaleString('en-IN')}`;
}

function formatPercent(value) {
    if (value === null || value === undefined) return '0%';
    return `${Number(value).toFixed(1)}%`;
}

function formatNumber(n) {
    if (n === null || n === undefined) return '0';
    const num = Number(n);
    if (num >= 10000000) return `${(num/10000000).toFixed(1)}Cr`;
    if (num >= 100000) return `${(num/100000).toFixed(1)}L`;
    if (num >= 1000) return `${(num/1000).toFixed(1)}K`;
    return num.toLocaleString('en-IN');
}

function timeAgo(dateStr) {
    const now = new Date();
    const date = new Date(dateStr);
    const diff = Math.floor((now - date) / 1000);
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
    return `${Math.floor(diff/86400)}d ago`;
}

// ============================================================
// CAMPAIGN CREATION
// ============================================================
async function createCampaign(event) {
    if (event) event.preventDefault();
    
    const form = document.getElementById('campaign-form');
    if (!form) return;
    
    const formData = {
        brand: form.querySelector('#brand')?.value || '',
        campaign_name: form.querySelector('#campaign-name')?.value || '',
        industry: form.querySelector('#industry')?.value || '',
        objective: form.querySelector('#objective')?.value || '',
        target_audience: form.querySelector('#audience')?.value || '',
        geography: form.querySelector('#geography')?.value || '',
        duration: form.querySelector('#duration')?.value || '',
        budget: parseFloat(form.querySelector('#budget')?.value) || 0,
        channels: (form.querySelector('#channels')?.value || '').split(',').map(s => s.trim()).filter(Boolean),
        description: form.querySelector('#description')?.value || '',
        goals: (form.querySelector('#goals')?.value || '').split('\n').filter(Boolean),
        kpis: (form.querySelector('#kpis')?.value || '').split(',').map(s => s.trim()).filter(Boolean),
        constraints: form.querySelector('#constraints')?.value || '',
        competitors: (form.querySelector('#competitors')?.value || '').split(',').map(s => s.trim()).filter(Boolean),
    };
    
    showLoading('Creating campaign...');
    
    try {
        const result = await API.post('/campaigns', formData);
        AppState.currentJob = result.job_id;
        AppState.campaign = formData;
        AppState.corrections = result.corrections || [];
        
        hideLoading();
        
        if (AppState.corrections.length > 0) {
            displayCorrections(AppState.corrections);
            showNotification(`${AppState.corrections.length} spelling suggestions found`, 'info');
        } else {
            showNotification('Campaign created successfully!', 'success');
            showCampaignPreview(formData, result.job_id);
        }
    } catch (error) {
        hideLoading();
        showNotification('Failed to create campaign: ' + error.message, 'error');
    }
}

function displayCorrections(corrections) {
    const container = document.getElementById('corrections-container');
    if (!container) return;
    
    container.innerHTML = '';
    container.style.display = 'block';
    
    corrections.forEach((correction, index) => {
        const card = document.createElement('div');
        card.className = 'correction-card';
        card.id = `correction-${index}`;
        card.innerHTML = `
            <div class="correction-header">
                <span class="correction-field">${correction.field || 'Input'}</span>
                <span class="badge badge-info">${correction.confidence || 95}% confidence</span>
            </div>
            <div class="correction-body">
                <div class="correction-original">
                    <span class="correction-label">Original:</span>
                    <span class="correction-value">${correction.original}</span>
                </div>
                <div class="correction-arrow">→</div>
                <div class="correction-suggested">
                    <span class="correction-label">Suggested:</span>
                    <span class="correction-value correction-highlight" id="suggested-${index}">${correction.corrected}</span>
                </div>
            </div>
            <div class="correction-actions">
                <button class="btn btn-success btn-sm" onclick="acceptCorrection(${index})">✓ Accept</button>
                <button class="btn btn-ghost btn-sm" onclick="editCorrection(${index})">✏️ Edit</button>
                <button class="btn btn-ghost btn-sm" onclick="keepOriginal(${index})">Keep Original</button>
            </div>
        `;
        container.appendChild(card);
    });
}

function acceptCorrection(index) {
    const card = document.getElementById(`correction-${index}`);
    if(card) {
        card.innerHTML = `<div style="padding: 10px; color: var(--success); font-weight: bold;">✅ Correction accepted.</div>`;
        setTimeout(() => card.remove(), 1500);
    }
    showNotification('Correction accepted.', 'success', 2000);
    checkAllCorrectionsResolved();
}

function editCorrection(index) {
    const el = document.getElementById(`suggested-${index}`);
    if(el) {
        const current = el.innerText;
        const edited = prompt("Edit suggested value:", current);
        if(edited !== null && edited.trim() !== '') {
            el.innerText = edited;
        }
    }
}

function keepOriginal(index) {
    const card = document.getElementById(`correction-${index}`);
    if(card) {
        card.innerHTML = `<div style="padding: 10px; color: var(--text-muted); font-weight: bold;">Original kept.</div>`;
        setTimeout(() => card.remove(), 1500);
    }
    checkAllCorrectionsResolved();
}

function checkAllCorrectionsResolved() {
    setTimeout(() => {
        const container = document.getElementById('corrections-container');
        if(container && container.children.length === 0) {
            container.style.display = 'none';
            if(AppState.campaign) {
                showCampaignPreview(AppState.campaign, AppState.currentJob);
            }
        }
    }, 1600);
}

function showCampaignPreview(campaign, jobId) {
    const preview = document.getElementById('campaign-preview');
    if(!preview) return;
    preview.style.display = 'block';
    preview.innerHTML = `
        <div class="card">
            <div class="card-header"><h3 class="card-title">Campaign Created: ${campaign.campaign_name || 'Untitled'}</h3></div>
            <div class="card-body">
                <p><strong>Brand:</strong> ${campaign.brand}</p>
                <p><strong>Budget:</strong> ${formatCurrency(campaign.budget)}</p>
                <p><strong>Target Audience:</strong> ${campaign.target_audience}</p>
                <div class="mt-3">
                    <button class="btn btn-primary" onclick="window.location.href='/dashboard.html'">Go to Dashboard</button>
                </div>
            </div>
        </div>
    `;
}

// ============================================================
// FILE UPLOAD
// ============================================================
function initUploadZone() {
    const zone = document.getElementById('upload-zone');
    if (!zone) return;
    
    zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('upload-zone-active'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('upload-zone-active'));
    zone.addEventListener('drop', handleFileDrop);
    
    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.addEventListener('change', handleFileSelect);
}

async function handleFileDrop(e) {
    e.preventDefault();
    const zone = document.getElementById('upload-zone');
    if(zone) zone.classList.remove('upload-zone-active');
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        await uploadDataset(e.dataTransfer.files[0]);
    }
}

async function handleFileSelect(e) {
    if (e.target.files && e.target.files.length > 0) {
        await uploadDataset(e.target.files[0]);
    }
}

async function uploadDataset(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_id', AppState.currentJob || 'temp');
    
    showLoading('Uploading and analyzing dataset...');
    try {
        const result = await API.upload('/upload', formData);
        hideLoading();
        displayUploadResult(result);
        if(result.quality_report) displayDataQuality(result.quality_report);
        showNotification('Dataset uploaded successfully!', 'success');
    } catch (error) {
        hideLoading();
    }
}

function displayUploadResult(result) {
    const container = document.getElementById('upload-results');
    if(!container) return;
    container.style.display = 'block';
    container.innerHTML = `
        <div class="card mt-3">
            <div class="card-body">
                <h4>Upload Successful</h4>
                <p>Rows: ${result.rows || 0}</p>
                <p>Columns: ${(result.columns || []).join(', ')}</p>
            </div>
        </div>
    `;
}

function displayDataQuality(report) {
    const container = document.getElementById('quality-report');
    if(!container) return;
    container.style.display = 'block';
    let issuesHtml = (report.issues || []).map(i => `<div class="issue-item"><span class="issue-severity">${i.severity}</span> ${i.description}</div>`).join('');
    container.innerHTML = `
        <div class="quality-meter mt-3">
            <div class="quality-score">${report.score || 100}%</div>
            <div class="mt-2 text-center">Data Quality Score</div>
            <div class="issues-list mt-3">${issuesHtml}</div>
        </div>
    `;
}

function displayColumnMappings(mappings) {
    console.log("Column mappings:", mappings);
}

// ============================================================
// DEMO MODE & ACTIVE JOB RESOLUTION
// ============================================================
async function getActiveJobId() {
    const params = new URLSearchParams(window.location.search);
    let id = params.get('job_id') || localStorage.getItem('mp-current-job');
    if (!id) {
        try {
            const resp = await fetch('/api/jobs/latest');
            if (resp.ok) {
                const j = await resp.json();
                id = j.job_id;
            }
        } catch (e) {}
    }
    if (id) {
        localStorage.setItem('mp-current-job', id);
    }
    return id;
}

async function startDemo() {
    showLoading('Starting Coca-Cola Share a Coke Demo...');
    try {
        const result = await API.post('/demo');
        const jobId = result.job_id;
        AppState.currentJob = jobId;
        localStorage.setItem('mp-current-job', jobId);
        hideLoading();
        showNotification('Demo analysis started! Redirecting to dashboard...', 'success');
        
        setTimeout(() => {
            window.location.href = `dashboard.html?job_id=${jobId}`;
        }, 1000);
    } catch (error) {
        hideLoading();
    }
}

// ============================================================
// JOB POLLING
// ============================================================
function startPolling(jobId) {
    if (AppState.pollInterval) clearInterval(AppState.pollInterval);
    localStorage.setItem('mp-current-job', jobId);
    
    AppState.pollInterval = setInterval(async () => {
        try {
            const status = await API.get(`/jobs/${jobId}/status`);
            updateJobProgress(status);
            
            if (status.status === 'completed' || status.status === 'failed') {
                clearInterval(AppState.pollInterval);
                AppState.pollInterval = null;
                
                if (status.status === 'completed') {
                    showNotification('Analysis complete!', 'success');
                    const results = await API.get(`/jobs/${jobId}/results`);
                    AppState.results = results;
                    if (typeof renderDashboard === 'function') renderDashboard(results);
                } else {
                    showNotification('Analysis failed. Check logs.', 'error');
                }
            }
        } catch (e) {
            console.warn('Polling error:', e);
        }
    }, 3000);
}

function updateJobProgress(status) {
    const progressBar = document.getElementById('job-progress-fill');
    if(progressBar) {
        progressBar.style.width = \`\${status.progress || 0}%\`;
    }
    const statusText = document.getElementById('job-status-text');
    if(statusText) {
        statusText.innerText = status.message || status.status;
    }
}

// ============================================================
// APPROVAL WORKFLOW
// ============================================================
async function approveRecommendations() {
    const jobId = AppState.currentJob || localStorage.getItem("mp-current-job");
    if (!jobId) {
        showNotification("No active campaign selected.", "warning");
        return;
    }
    
    showLoading("Approving and dispatching to n8n automation...");
    try {
        const res = await API.post(`/jobs/${jobId}/approve`, { approved_by: "Authorized Lead" });
        hideLoading();
        const n8nStatus = res?.n8n_status || "";
        showNotification(`Recommendations approved! n8n: ${n8nStatus}`, "success");
        document.querySelectorAll(".approval-btn").forEach(btn => {
            btn.disabled = true;
            btn.textContent = "✅ Approved & Dispatched to n8n";
            btn.classList.remove("btn-primary");
            btn.classList.add("btn-success");
        });
    } catch (error) {
        hideLoading();
        showNotification(`Approval error: ${error.message}`, "error");
    }
}

async function requestRevision() {
    const feedback = prompt('What changes would you like?\\n\\nExample: "Keep budget below ₹8 lakh" or "Focus more on Instagram"');
    if (!feedback) return;
    
    showLoading('Processing revision...');
    try {
        await API.post(`/jobs/${AppState.currentJob}/revise`, { feedback });
        hideLoading();
        showNotification('Revision started. Relevant agents re-running...', 'info');
        startPolling(AppState.currentJob);
    } catch (error) {
        hideLoading();
    }
}

// ============================================================
// SCENARIO SIMULATOR
// ============================================================
async function runScenario() {
    const channels = ['Instagram', 'YouTube', 'Facebook', 'Google Ads', 'Twitter', 'Snapchat', 'Influencer'];
    const currentAllocation = {};
    const proposedAllocation = {};
    
    channels.forEach(ch => {
        const chKey = ch.replace(/\s+/g, '-').toLowerCase();
        const currentInput = document.getElementById(`current-${chKey}`);
        const proposedInput = document.getElementById(`proposed-${chKey}`);
        if (currentInput) currentAllocation[ch] = parseFloat(currentInput.value) || 0;
        if (proposedInput) proposedAllocation[ch] = parseFloat(proposedInput.value) || 0;
    });
    
    const totalBudget = parseFloat(document.getElementById('scenario-budget')?.value) || 1000000;
    
    showLoading('Simulating scenario...');
    try {
        const result = await API.post('/scenario', {
            current_allocation: currentAllocation,
            proposed_allocation: proposedAllocation,
            total_budget: totalBudget
        });
        hideLoading();
        displayScenarioResults(result);
    } catch (error) {
        hideLoading();
    }
}

function displayScenarioResults(result) {
    const container = document.getElementById('scenario-results');
    if(!container) return;
    container.style.display = 'block';
    container.innerHTML = `
        <div class="card mt-3">
            <div class="card-header"><h4>Simulation Results</h4></div>
            <div class="card-body">
                <p>Expected ROAS: ${result.roas || 'N/A'}</p>
                <p>Estimated Conversions: ${result.conversions || 'N/A'}</p>
            </div>
        </div>
    `;
}

// ============================================================
// RAG SEARCH
// ============================================================
async function searchRAG() {
    const query = document.getElementById('rag-query')?.value;
    if (!query) return;
    
    showLoading('Searching knowledge base...');
    try {
        const result = await API.post('/rag/search', { query });
        hideLoading();
        displayRAGResults(result.results);
    } catch (error) {
        hideLoading();
    }
}

function displayRAGResults(results) {
    const container = document.getElementById('rag-results');
    if(!container) return;
    container.style.display = 'block';
    
    if(!results || results.length === 0) {
        container.innerHTML = '<p>No results found.</p>';
        return;
    }
    
    let html = '<ul>';
    results.forEach(r => {
        html += `<li><strong>Score: ${r.score}</strong> - ${r.text}</li>`;
    });
    html += '</ul>';
    container.innerHTML = html;
}

// ============================================================
// LOADING STATES
// ============================================================
function showLoading(message = 'Loading...') {
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        document.body.appendChild(overlay);
    }
    overlay.innerHTML = `
        <div class="loading-content" style="text-align: center; z-index: 10001; position: relative;">
            <div class="spinner" style="margin: 0 auto;"></div>
            <p class="loading-message">${message}</p>
        </div>
    `;
    overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'none';
}

// ============================================================
// SIDEBAR NAVIGATION
// ============================================================
function initSidebar() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-item').forEach(item => {
        const href = item.getAttribute('href');
        if (href && (currentPath.includes(href) || (currentPath === '/' && href === 'index.html'))) {
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            item.classList.add('active');
        }
    });
}

// ============================================================
// INITIALIZATION
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initSidebar();
    initUploadZone();
    
    const activeJob = localStorage.getItem('mp-current-job');
    if (activeJob) {
        AppState.currentJob = activeJob;
    }
    
    const page = window.location.pathname;
    if (page.includes('dashboard') && AppState.currentJob) {
        loadDashboardData();
    }
});

async function loadDashboardData() {
    if (!AppState.currentJob) return;
    try {
        const job = await API.get(`/jobs/${AppState.currentJob}`);
        if (job.status === 'completed' && job.results) {
            AppState.results = job.results;
            if (typeof renderDashboard === 'function') renderDashboard(job.results);
        } else if (job.status === 'running') {
            startPolling(AppState.currentJob);
        }
    } catch (e) {
        console.warn('Failed to load dashboard data:', e);
    }
}
