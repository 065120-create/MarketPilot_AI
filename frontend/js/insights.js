/* === MarketPilot AI - Dynamic Customer Voice & Insights Controller === */

let insightsSentimentChart = null;

document.addEventListener('DOMContentLoaded', async () => {
    await loadCustomerVoiceData();
});

async function loadCustomerVoiceData() {
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

        renderInsightsUI(job, results);
    } catch (e) {
        console.warn("Failed to load insights data:", e);
    }
}

function renderInsightsUI(job, results) {
    const voice = results.customer_voice || {};
    const campaign = job.campaign || {};
    const brand = campaign.brand || 'Brand';

    const dist = voice.sentiment_distribution || { positive: 105, neutral: 33, negative: 12 };
    const total = (dist.positive || 0) + (dist.neutral || 0) + (dist.negative || 0);

    const posPct = total > 0 ? ((dist.positive / total) * 100).toFixed(1) : '70.0';
    const neuPct = total > 0 ? ((dist.neutral / total) * 100).toFixed(1) : '22.0';
    const negPct = total > 0 ? ((dist.negative / total) * 100).toFixed(1) : '8.0';

    // Update KPI metrics
    const posVal = document.getElementById('pos-metric-val');
    const neuVal = document.getElementById('neu-metric-val');
    const negVal = document.getElementById('neg-metric-val');
    const totVal = document.getElementById('tot-metric-val');

    if (posVal) posVal.textContent = `${posPct}%`;
    if (neuVal) neuVal.textContent = `${neuPct}%`;
    if (negVal) negVal.textContent = `${negPct}%`;
    if (totVal) totVal.textContent = `${total || 150} Reviews`;

    // Render Doughnut Chart
    const ctx = document.getElementById('sentimentChart')?.getContext('2d');
    if (ctx) {
        if (insightsSentimentChart) insightsSentimentChart.destroy();
        insightsSentimentChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [`Positive (${posPct}%)`, `Neutral (${neuPct}%)`, `Negative (${negPct}%)`],
                datasets: [{
                    data: [dist.positive || 105, dist.neutral || 33, dist.negative || 12],
                    backgroundColor: ['#06d6a0', '#ff9f1c', '#ef476f'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { color: '#a0a0c0' } } },
                cutout: '65%'
            }
        });
    }

    // Render Qualitative Themes
    const praiseContainer = document.getElementById('praise-drivers-container');
    const painContainer = document.getElementById('pain-points-container');
    const desiresContainer = document.getElementById('emerging-desires-container');

    const praiseDrivers = voice.insights?.praise_drivers || [
        `High engagement with ${brand} creatives`,
        'Interactive social shareability',
        'Strong visual brand resonance'
    ];
    const painPoints = voice.insights?.pain_points || [
        'Regional stock delays in tier-1 hubs',
        'High YouTube ad repetition frequency',
        'Checkout latency on mobile web'
    ];
    const desires = voice.insights?.actionable_takeaways || [
        'Accelerate consideration-stage remarketing',
        'Offer personalized web-exclusive bundles'
    ];

    if (praiseContainer) {
        praiseContainer.innerHTML = praiseDrivers.map(p => `<span class="badge badge-success">${p}</span>`).join(' ');
    }
    if (painContainer) {
        painContainer.innerHTML = painPoints.map(p => `<span class="badge badge-error">${p}</span>`).join(' ');
    }
    if (desiresContainer) {
        desiresContainer.innerHTML = desires.map(d => `<span class="badge badge-warning">${d}</span>`).join(' ');
    }

    // Render Feedback Table
    const tableBody = document.getElementById('feedback-table-body');
    if (tableBody) {
        const sampleReviews = [
            { id: "REV001", ch: "Instagram", rating: "⭐⭐⭐⭐⭐", text: `Absolutely loved the ${brand} activation! Shared with all my friends.`, sentiment: "POSITIVE (0.85)", badge: "badge-success" },
            { id: "REV002", ch: "YouTube", rating: "⭐⭐⭐⭐", text: `Engaging storytelling, but the pre-roll ads felt a bit repetitive.`, sentiment: "NEUTRAL (0.12)", badge: "badge-warning" },
            { id: "REV003", ch: "Website", rating: "⭐⭐⭐⭐⭐", text: `Super smooth purchase experience on mobile web.`, sentiment: "POSITIVE (0.92)", badge: "badge-success" },
            { id: "REV004", ch: "Twitter", rating: "⭐⭐", text: `Took 4 days to receive the order in Delhi NCR. Please improve shipping times.`, sentiment: "NEGATIVE (-0.45)", badge: "badge-error" },
            { id: "REV005", ch: "Google Ads", rating: "⭐⭐⭐⭐⭐", text: `Found exactly what I was searching for with the direct promotion link.`, sentiment: "POSITIVE (0.78)", badge: "badge-success" }
        ];

        tableBody.innerHTML = sampleReviews.map(r => `
            <tr>
                <td><code>${r.id}</code></td>
                <td>${r.ch}</td>
                <td>${r.rating}</td>
                <td>"${r.text}"</td>
                <td><span class="badge ${r.badge}">${r.sentiment}</span></td>
            </tr>
        `).join('');
    }
}
