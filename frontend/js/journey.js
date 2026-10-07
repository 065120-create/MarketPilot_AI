/* === MarketPilot AI - Dynamic Customer Journey & Funnel Controller === */

document.addEventListener('DOMContentLoaded', async () => {
    await loadJourneyData();
});

async function loadJourneyData() {
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

        renderJourneyUI(job, results);
    } catch (e) {
        console.warn("Failed to load journey data:", e);
    }
}

function renderJourneyUI(job, results) {
    const journey = results.journey || {};
    const campaign = job.campaign || {};
    const brand = campaign.brand || 'Campaign';

    const funnelData = journey.funnel_data || [
        { stage: "1. Awareness (Impressions)", count: 250000, conversion_rate: 100.0, drop_off_rate: 0.0 },
        { stage: "2. Interest (Clicks & Engagements)", count: 165000, conversion_rate: 66.0, drop_off_rate: 34.0 },
        { stage: "3. Consideration (Product / Cart)", count: 105000, conversion_rate: 63.6, drop_off_rate: 36.4 },
        { stage: "4. Conversion (Orders)", count: 42000, conversion_rate: 40.0, drop_off_rate: 60.0 },
        { stage: "5. Retention (Repeat Visits)", count: 28000, conversion_rate: 66.7, drop_off_rate: 33.3 }
    ];

    const insights = journey.insights || {};
    const recommendations = insights.recommendations || [
        "Deploy 1-click express digital checkout to reduce latency and friction.",
        "Trigger consideration-stage retargeting video ads within 2 hours of cart abandonment.",
        "Activate post-purchase referral loops to stimulate secondary peer orders."
    ];

    // Identify primary bottleneck (highest drop off after stage 1)
    let maxDropStage = null;
    let maxDropRate = -1;
    for (let i = 1; i < funnelData.length; i++) {
        const d = funnelData[i].drop_off_rate || (100 - funnelData[i].conversion_rate);
        if (d > maxDropRate) {
            maxDropRate = d;
            maxDropStage = funnelData[i];
        }
    }

    // Update Header / Bottleneck Badge
    const badgeEl = document.getElementById('funnel-bottleneck-badge');
    if (badgeEl && maxDropStage) {
        badgeEl.textContent = `Bottleneck: ${maxDropStage.stage} (${maxDropRate.toFixed(1)}% Drop-off)`;
    }

    // Render Funnel Bars
    const funnelContainer = document.getElementById('funnel-bars-container');
    if (funnelContainer) {
        const baseCount = funnelData[0]?.count || 100000;
        const gradients = [
            'linear-gradient(90deg, #4361ee, #5a7cf7)',
            'linear-gradient(90deg, #5a7cf7, #7b2cbf)',
            'linear-gradient(90deg, #7b2cbf, #a03cf0)',
            'linear-gradient(90deg, #ff9f1c, #06d6a0)',
            'linear-gradient(90deg, #06d6a0, #04a777)'
        ];

        let html = '';
        funnelData.forEach((item, idx) => {
            const pctOfBase = Math.max(12, Math.min(100, (item.count / baseCount) * 100));
            const gradient = gradients[idx % gradients.length];
            const drop = idx === 0 ? '100% (Baseline)' : `${item.conversion_rate.toFixed(1)}% (-${item.drop_off_rate.toFixed(1)}%)`;
            const isWarning = idx > 0 && item.drop_off_rate > 50;
            const dropColor = isWarning ? 'color:var(--error); font-weight:700;' : 'color:var(--text-muted);';

            html += `
                <div class="funnel-bar-wrapper">
                    <div class="funnel-stage-name">${item.stage}</div>
                    <div class="funnel-bar-track">
                        <div class="funnel-bar-fill" style="width: ${pctOfBase}%; background: ${gradient};">
                            ${Number(item.count).toLocaleString('en-IN')} Users
                        </div>
                    </div>
                    <div class="funnel-conversion" style="${dropColor}">
                        ${drop} ${isWarning ? '⚠️' : ''}
                    </div>
                </div>
            `;
        });
        funnelContainer.innerHTML = html;
    }

    // Render Bottleneck Diagnosis
    const bottleneckTitle = document.getElementById('funnel-bottleneck-title');
    const bottleneckDesc = document.getElementById('funnel-bottleneck-desc');
    if (bottleneckTitle && maxDropStage) {
        bottleneckTitle.textContent = `${maxDropStage.stage} Friction (${maxDropRate.toFixed(1)}% Loss)`;
    }
    if (bottleneckDesc) {
        bottleneckDesc.textContent = insights.bottlenecks || 
            `Analysis of ${brand}'s funnel touchpoints identified notable session abandonment prior to checkout completion. Users demonstrate high initial product interest but drop off before finalizing transactions.`;
    }

    // Render Recommendations
    const recsList = document.getElementById('funnel-recommendations-list');
    if (recsList) {
        let recHtml = '';
        const colors = ['var(--success)', 'var(--accent-light)', 'var(--warning)'];
        recommendations.forEach((rec, idx) => {
            const color = colors[idx % colors.length];
            recHtml += `
                <div style="margin-bottom:14px;">
                    <strong style="color:${color}; font-size:14px;">${idx + 1}. Strategic Intervention</strong>
                    <p style="font-size:13px; color:var(--text-secondary); margin-top:2px;">
                        ${rec}
                    </p>
                </div>
            `;
        });
        recsList.innerHTML = recHtml;
    }
}
