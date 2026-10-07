/* === MarketPilot AI - Dynamic What-If Scenario Simulator Controller === */

let scenarioChart = null;
let currentBudgetTotal = 1000000;
let baseAllocation = {};
let recommendedAllocation = {};
let activeChannels = [];

document.addEventListener('DOMContentLoaded', async () => {
    await initializeScenarioSimulator();
});

async function initializeScenarioSimulator() {
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

        setupSimulatorWithJobData(job, results);
    } catch (e) {
        console.warn("Failed to load scenario data:", e);
    }
}

function setupSimulatorWithJobData(job, results) {
    const budgetData = results.budget || {};
    const campaign = job.campaign || {};
    currentBudgetTotal = Number(budgetData.total_budget || campaign.budget || 1000000);

    baseAllocation = budgetData.current_allocation || {
        "Google Ads": Math.round(currentBudgetTotal * 0.25),
        "Instagram": Math.round(currentBudgetTotal * 0.24),
        "YouTube": Math.round(currentBudgetTotal * 0.20),
        "Snapchat": Math.round(currentBudgetTotal * 0.11),
        "Facebook": Math.round(currentBudgetTotal * 0.12),
        "Twitter": Math.round(currentBudgetTotal * 0.08)
    };

    recommendedAllocation = budgetData.mathematical_recommendation || {
        "Google Ads": Math.round(currentBudgetTotal * 0.32),
        "Instagram": Math.round(currentBudgetTotal * 0.28),
        "YouTube": Math.round(currentBudgetTotal * 0.18),
        "Snapchat": Math.round(currentBudgetTotal * 0.13),
        "Facebook": Math.round(currentBudgetTotal * 0.06),
        "Twitter": Math.round(currentBudgetTotal * 0.03)
    };

    activeChannels = Array.from(new Set([...Object.keys(baseAllocation), ...Object.keys(recommendedAllocation)]));

    renderSliders();
    initComparisonChart();
    executeSimulation();
}

function renderSliders() {
    const container = document.getElementById('scenario-sliders-container');
    if (!container) return;

    let html = '';
    const step = Math.max(1000, Math.round(currentBudgetTotal / 100));
    const maxVal = Math.round(currentBudgetTotal * 0.7);

    activeChannels.forEach(ch => {
        const initVal = recommendedAllocation[ch] !== undefined ? recommendedAllocation[ch] : baseAllocation[ch] || 0;
        const slug = ch.toLowerCase().replace(/[^a-z0-9]/g, '-');
        html += `
            <div class="slider-group">
                <div class="slider-header">
                    <span>${ch}</span>
                    <span id="val-${slug}" style="color:var(--accent-light);">₹${Math.round(initVal).toLocaleString('en-IN')}</span>
                </div>
                <input type="range" class="slider-control" id="slider-${slug}" 
                       data-channel="${ch}"
                       min="0" max="${maxVal}" step="${step}" value="${initVal}" 
                       oninput="onSliderChange('${slug}')">
            </div>
        `;
    });

    container.innerHTML = html;
    updateTotalBadge();
}

function onSliderChange(slug) {
    const slider = document.getElementById(`slider-${slug}`);
    const valSpan = document.getElementById(`val-${slug}`);
    if (slider && valSpan) {
        const val = parseInt(slider.value);
        valSpan.textContent = `₹${val.toLocaleString('en-IN')}`;
    }
    updateTotalBadge();
}

function updateTotalBadge() {
    let total = 0;
    activeChannels.forEach(ch => {
        const slug = ch.toLowerCase().replace(/[^a-z0-9]/g, '-');
        const slider = document.getElementById(`slider-${slug}`);
        if (slider) {
            total += parseInt(slider.value) || 0;
        }
    });

    const badge = document.getElementById('total-allocated-badge');
    if (badge) {
        badge.textContent = `Total: ₹${total.toLocaleString('en-IN')}`;
        const upper = currentBudgetTotal * 1.05;
        const lower = currentBudgetTotal * 0.95;
        badge.className = total > upper ? 'badge badge-error' : (total < lower ? 'badge badge-warning' : 'badge badge-success');
    }
}

async function executeSimulation() {
    const proposed = {};
    activeChannels.forEach(ch => {
        const slug = ch.toLowerCase().replace(/[^a-z0-9]/g, '-');
        const slider = document.getElementById(`slider-${slug}`);
        if (slider) {
            proposed[ch] = parseInt(slider.value) || 0;
        } else {
            proposed[ch] = recommendedAllocation[ch] || baseAllocation[ch] || 0;
        }
    });

    try {
        const resp = await fetch('/api/scenario', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                current_allocation: baseAllocation,
                proposed_allocation: proposed,
                total_budget: currentBudgetTotal
            })
        });

        if (resp.ok) {
            const data = await resp.json();
            renderSimulationResults(data);
        } else {
            simulateLocally(baseAllocation, proposed);
        }
    } catch (e) {
        simulateLocally(baseAllocation, proposed);
    }
}

function simulateLocally(current, proposed) {
    const benchmarks = {'Google Ads': 4.1, 'Instagram': 3.2, 'YouTube': 2.7, 'Snapchat': 2.5, 'Facebook': 1.8, 'Twitter': 1.6};
    let cRev = 0, pRev = 0, cSpend = 0, pSpend = 0;
    for (let ch of activeChannels) {
        const r = benchmarks[ch] || 2.5;
        const cs = current[ch] || 0;
        const ps = proposed[ch] || 0;
        cRev += cs * r;
        pRev += ps * r;
        cSpend += cs;
        pSpend += ps;
    }

    renderSimulationResults({
        scenario_a: {estimated_revenue: cRev, estimated_roas: (cSpend > 0 ? (cRev/cSpend).toFixed(2) : 0)},
        scenario_b: {estimated_revenue: pRev, estimated_roas: (pSpend > 0 ? (pRev/pSpend).toFixed(2) : 0)},
        comparison: {
            revenue_change: pRev - cRev,
            roas_change: ((pSpend > 0 ? pRev/pSpend : 0) - (cSpend > 0 ? cRev/cSpend : 0)).toFixed(2)
        },
        risk: {
            level: pSpend > currentBudgetTotal * 1.05 ? 'high' : 'low',
            factors: pSpend > currentBudgetTotal * 1.05 ? ['Spend exceeds budget envelope'] : []
        }
    });
}

function renderSimulationResults(data) {
    const pRev = data.scenario_b.estimated_revenue;
    const pRoas = data.scenario_b.estimated_roas;
    const diffRev = data.comparison.revenue_change;
    const diffRoas = data.comparison.roas_change;

    const elRev = document.getElementById('proj-rev');
    const elRoas = document.getElementById('proj-roas');
    const elRevLift = document.getElementById('proj-rev-lift');
    const elRoasLift = document.getElementById('proj-roas-lift');

    if (elRev) elRev.textContent = `₹${Math.round(pRev).toLocaleString('en-IN')}`;
    if (elRoas) elRoas.textContent = `${pRoas}x`;
    if (elRevLift) elRevLift.textContent = `${diffRev >= 0 ? '+' : ''}₹${Math.round(diffRev).toLocaleString('en-IN')}`;
    if (elRoasLift) elRoasLift.textContent = `${diffRoas >= 0 ? '+' : ''}${diffRoas}x vs Baseline`;

    const card = document.getElementById('scenario-verdict-card');
    const verdictTitle = document.getElementById('verdict-title');
    const verdictDesc = document.getElementById('verdict-desc');

    if (card && verdictTitle && verdictDesc) {
        if (data.risk && data.risk.level === 'high') {
            card.style.borderLeftColor = 'var(--error)';
            verdictTitle.textContent = '⚠️ Risk Alert: Budget or Concentration Warning';
            verdictDesc.textContent = (data.risk.factors && data.risk.factors.length > 0)
                ? data.risk.factors.join(', ')
                : 'Proposed spend exceeds budget constraint cap or violates single-channel concentration limits.';
        } else {
            card.style.borderLeftColor = 'var(--success)';
            verdictTitle.textContent = '✅ Scenario Validated by Governance Engine';
            verdictDesc.textContent = `Estimated revenue shift: ${diffRev >= 0 ? '+' : ''}₹${Math.round(diffRev).toLocaleString('en-IN')}. Portfolio risk metrics within optimal safety boundaries.`;
        }
    }

    if (scenarioChart) {
        scenarioChart.data.datasets[0].data = [
            Math.round(data.scenario_a.estimated_revenue),
            Math.round(data.scenario_b.estimated_revenue)
        ];
        scenarioChart.update();
    }
}

function resetSliders() {
    activeChannels.forEach(ch => {
        const slug = ch.toLowerCase().replace(/[^a-z0-9]/g, '-');
        const slider = document.getElementById(`slider-${slug}`);
        const valSpan = document.getElementById(`val-${slug}`);
        const rec = recommendedAllocation[ch] !== undefined ? recommendedAllocation[ch] : baseAllocation[ch] || 0;
        if (slider) slider.value = rec;
        if (valSpan) valSpan.textContent = `₹${Math.round(rec).toLocaleString('en-IN')}`;
    });
    updateTotalBadge();
    executeSimulation();
}

function initComparisonChart() {
    const ctx = document.getElementById('scenarioComparisonChart')?.getContext('2d');
    if (ctx) {
        if (scenarioChart) scenarioChart.destroy();
        scenarioChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Baseline (Scenario A)', 'Simulated (Scenario B)'],
                datasets: [{
                    label: 'Estimated Revenue (₹)',
                    data: [Math.round(currentBudgetTotal * 2.68), Math.round(currentBudgetTotal * 3.24)],
                    backgroundColor: ['rgba(160, 160, 192, 0.4)', '#06d6a0'],
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
}
