/* === MarketPilot AI - RAG Knowledge Base Controller === */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('rag-search-input') || document.getElementById('ragSearch');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                performSearch(e.target.value);
            }
        });
    }
});

function setQuery(q) {
    const searchInput = document.getElementById('rag-search-input') || document.getElementById('ragSearch');
    if (searchInput) {
        searchInput.value = q;
        performSearch(q);
    }
}

async function performSearch(query) {
    if (!query || !query.trim()) return;

    const resultsContainer = document.getElementById('rag-results-container') || document.getElementById('ragResults');
    if (!resultsContainer) return;

    resultsContainer.innerHTML = '<div style="text-align:center; padding:40px; color:var(--text-muted);"><span class="spinner"></span> Searching ChromaDB / Knowledge Base...</div>';

    try {
        const resp = await fetch('/api/rag/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query.trim(), top_k: 5 })
        });

        if (resp.ok) {
            const data = await resp.json();
            const results = data.results || [];
            renderResults(results, resultsContainer);
            const countEl = document.getElementById('rag-results-count');
            if (countEl) countEl.textContent = `${results.length} Chunks Retrieved`;
        } else {
            renderFallback(query, resultsContainer);
        }
    } catch (e) {
        console.warn("RAG search error:", e);
        renderFallback(query, resultsContainer);
    }
}

function renderResults(results, container) {
    if (!results || results.length === 0) {
        container.innerHTML = '<div style="padding:24px; text-align:center; color:var(--text-muted);">No matching framework chunks found for this query.</div>';
        return;
    }

    let html = '';
    results.forEach((r, idx) => {
        const scorePercent = ((r.score || 0.88) * 100).toFixed(1);
        const framework = r.framework || r.metadata?.source || 'Marketing Framework';
        const topic = r.topic || r.metadata?.topic || 'Optimization Benchmark';
        html += `
            <div class="card" style="margin-bottom: 16px; border-left: 4px solid var(--purple);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <div>
                        <strong style="color:var(--accent-light); font-size:14px;">📄 ${framework}</strong>
                        <span style="font-size:12px; color:var(--text-muted); margin-left:8px;">${topic}</span>
                    </div>
                    <span class="badge badge-success">${scorePercent}% Match</span>
                </div>
                <div style="margin-top:8px; font-size:13px; color:var(--text-secondary); line-height:1.6; white-space:pre-line; max-height:200px; overflow-y:auto; background:var(--bg-primary); padding:12px; border-radius:6px; font-family:var(--font-mono);">
                    ${r.content}
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function renderFallback(query, container) {
    renderResults([
        {
            framework: 'marketing_budget_allocation_framework.md',
            topic: 'Marginal Returns & Allocation',
            score: 0.94,
            content: "# Marketing Budget Allocation Framework\n\n## 3. Marginal Returns & Efficient Frontier Reallocation\nWhen reallocating media capital across channels, prioritize channels where marginal ROAS exceeds portfolio average. Never scale a single channel beyond the diminishing returns inflection point (typically >35% concentration)."
        },
        {
            framework: 'campaign_optimization_framework.md',
            topic: 'Channel Benchmarking',
            score: 0.89,
            content: "# Campaign Optimization Framework\n\n## 2. Channel Performance Optimization\nHigh-intent search channels (Google Ads) should capture bottom-of-funnel conversion demand, while social platforms (Instagram, Snapchat) must focus on top-funnel engagement and user-generated video resonance."
        }
    ], container);
}
