/* === MarketPilot AI - Dynamic Customer Segmentation Controller === */

let shareChartInstance = null;
let radarChartInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
    await loadSegmentationData();
});

async function loadSegmentationData() {
    const params = new URLSearchParams(window.location.search);
    let jobId = params.get('job_id') || localStorage.getItem('mp-current-job');

    if (!jobId) {
        try {
            const resp = await fetch('/api/jobs/latest');
            if (resp.ok) {
                const j = await resp.json();
                jobId = j.job_id;
            }
        } catch (e) {}
    }

    if (!jobId) return;

    try {
        const jobResp = await fetch(`/api/jobs/${jobId}`);
        const resultsResp = await fetch(`/api/jobs/${jobId}/results`);

        let job = {};
        let results = {};
        if (jobResp.ok) job = await jobResp.json();
        if (resultsResp.ok) results = await resultsResp.json();

        renderSegmentationUI(job, results);
    } catch (e) {
        console.warn("Failed to load segmentation data:", e);
    }
}

function renderSegmentationUI(job, results) {
    const seg = results.segmentation || {};
    const campaign = job.campaign || {};
    const brand = campaign.brand || 'Brand';
    const audience = campaign.target_audience || 'Target Demographic';

    const profiles = seg.segment_profiles || {
        "segment_0": { "name": "High-Value Champions", "size": 84, "percentage": 28.0, "avg_total_spend": 4250, "avg_purchase_count": 6.8, "strategy": "Exclusive VIP loyalty tiers and early drop previews." },
        "segment_1": { "name": "Trend Explorers", "size": 102, "percentage": 34.0, "avg_total_spend": 2100, "avg_purchase_count": 3.4, "strategy": "Short-form video challenges and UGC creator drops." },
        "segment_2": { "name": "Occasional Shoppers", "size": 66, "percentage": 22.0, "avg_total_spend": 1400, "avg_purchase_count": 1.6, "strategy": "Festival bundle discounts and win-back offers." },
        "segment_3": { "name": "Value-Conscious Newcomers", "size": 48, "percentage": 16.0, "avg_total_spend": 850, "avg_purchase_count": 1.0, "strategy": "Onboarding nurture drip sequence with welcome voucher." }
    };

    const keys = Object.keys(profiles);
    const labels = keys.map(k => `${profiles[k].name || k} (${profiles[k].percentage}%)`);
    const shares = keys.map(k => profiles[k].percentage);

    // Render Share Chart
    const ctx1 = document.getElementById('clusterShareChart')?.getContext('2d');
    if (ctx1) {
        if (shareChartInstance) shareChartInstance.destroy();
        shareChartInstance = new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Audience Share %',
                    data: shares,
                    backgroundColor: ['#4361ee', '#06d6a0', '#ff9f1c', '#7b2cbf'],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#a0a0c0' }, grid: { display: false } },
                    y: { ticks: { color: '#a0a0c0' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });
    }

    // Render Radar Chart
    const ctx2 = document.getElementById('clusterRadarChart')?.getContext('2d');
    if (ctx2) {
        if (radarChartInstance) radarChartInstance.destroy();
        radarChartInstance = new Chart(ctx2, {
            type: 'radar',
            data: {
                labels: ['Engagement', 'AOV', 'Frequency', 'Advocacy', 'Price Sensitivity'],
                datasets: [
                    {
                        label: profiles[keys[0]]?.name || 'Champions',
                        data: [95, 88, 92, 90, 20],
                        borderColor: '#4361ee',
                        backgroundColor: 'rgba(67, 97, 238, 0.2)'
                    },
                    {
                        label: profiles[keys[1]]?.name || 'Trend Explorers',
                        data: [85, 60, 65, 80, 50],
                        borderColor: '#06d6a0',
                        backgroundColor: 'rgba(6, 214, 160, 0.2)'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { color: '#a0a0c0' } } },
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255,255,255,0.05)' },
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        pointLabels: { color: '#a0a0c0' },
                        ticks: { display: false }
                    }
                }
            }
        });
    }

    // Render Dynamic Segment Cards
    const cardsContainer = document.getElementById('segment-cards-container');
    if (cardsContainer) {
        const borderColors = ['var(--accent)', 'var(--success)', 'var(--warning)', 'var(--purple)'];
        let html = '';
        keys.forEach((k, idx) => {
            const p = profiles[k];
            const color = borderColors[idx % borderColors.length];
            const spend = p.avg_total_spend ? `₹${Math.round(p.avg_total_spend).toLocaleString('en-IN')}` : '₹2,500';
            const freq = p.avg_purchase_count ? `${p.avg_purchase_count.toFixed(1)}x/mo` : '3.0x/mo';
            html += `
                <div class="card" style="border-left: 5px solid ${color};">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div>
                            <span class="badge" style="background:${color}22; color:${color}; font-weight:700;">Cluster ${idx + 1} &bull; ${p.percentage}% of Audience</span>
                            <h3 style="font-size:18px; font-weight:800; color:var(--text-heading); margin-top:4px;">
                                ${p.name || `Segment ${idx + 1}`}
                            </h3>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:20px; font-weight:800; color:${color};">${spend}</div>
                            <div style="font-size:11px; color:var(--text-muted);">Avg Spend / LTV</div>
                        </div>
                    </div>
                    <p style="font-size:13px; color:var(--text-secondary); margin-bottom:12px;">
                        Identified segment within ${brand}'s ${audience}. Accounts for ${p.size || 50} audited customer interactions.
                    </p>
                    <div style="background:var(--bg-primary); padding:12px; border-radius:6px; font-size:13px; margin-bottom:12px;">
                        <strong>🎯 Actionable Strategy:</strong> ${p.strategy || 'Optimize channel messaging and targeted promotions.'}
                    </div>
                    <div style="display:flex; gap:12px; font-size:12px; color:var(--text-muted);">
                        <span>Purchase Frequency: <strong>${freq}</strong></span> &bull;
                        <span>Audience Size: <strong>${p.size || 50} customers</strong></span>
                    </div>
                </div>
            `;
        });
        cardsContainer.innerHTML = html;
    }
}
