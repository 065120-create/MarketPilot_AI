/* === MarketPilot AI - Agent Trace Observability JS === */

document.addEventListener('DOMContentLoaded', async () => {
    await loadAgentTrace();
});

let currentExecutionLog = [];

async function loadAgentTrace() {
    const container = document.getElementById('agent-nodes-container');
    const logsContainer = document.getElementById('swarm-raw-logs');
    const jobBadge = document.getElementById('active-job-badge');
    const latencyEl = document.getElementById('swarm-latency');

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

    jobId = jobId || 'MP-2026-000001';
    if (jobBadge) jobBadge.textContent = `Job: ${jobId}`;

    try {
        let jobData = null;
        try {
            const resp = await fetch(`/api/jobs/${jobId}`);
            if (resp.ok) {
                jobData = await resp.json();
            }
        } catch (e) {
            console.warn('API fetch warning:', e);
        }

        // If no job or empty logs, fetch demo execution log
        let logs = (jobData && jobData.execution_log && jobData.execution_log.length > 0)
            ? jobData.execution_log
            : getFallbackSwarmTrace();

        currentExecutionLog = logs;
        if (latencyEl && jobData && jobData.total_execution_time_ms) {
            latencyEl.textContent = `${jobData.total_execution_time_ms}ms`;
        }

        renderAgentNodes(logs);
        renderRawLogs(logs);

    } catch (e) {
        console.error('Failed to load agent trace:', e);
        const fallback = getFallbackSwarmTrace();
        renderAgentNodes(fallback);
        renderRawLogs(fallback);
    }
}

function renderAgentNodes(logs) {
    const container = document.getElementById('agent-nodes-container');
    if (!container) return;

    const icons = {
        orchestrator: '🧭',
        campaign_performance: '📈',
        customer_voice: '🗣️',
        segmentation: '👥',
        journey: '🔄',
        rag_knowledge_engine: '📚',
        optimization: '⚡',
        budget: '💰',
        content: '✍️',
        quality_governance: '🛡️',
        synthesis: '📋'
    };

    const friendlyNames = {
        orchestrator: 'Dynamic Orchestrator Agent',
        campaign_performance: 'Campaign Performance Analyst',
        customer_voice: 'Customer Voice & Sentiment Agent',
        segmentation: 'Customer Segmentation Engine',
        journey: 'Customer Journey Funnel Agent',
        rag_knowledge_engine: 'Autonomous RAG Knowledge Retriever',
        optimization: 'Campaign Optimization Strategist',
        budget: 'Budget Allocation & Convex Optimizer',
        content: 'Content Recommendation Specialist',
        quality_governance: 'Quality & Governance Guardian',
        synthesis: 'Executive Synthesis Agent'
    };

    let html = '';
    logs.forEach((node, idx) => {
        const agentKey = (node.agent || 'unknown').toLowerCase();
        const icon = icons[agentKey] || '🤖';
        const name = friendlyNames[agentKey] || node.agent;
        const status = node.status || 'completed';
        const isRejected = status === 'rejected';
        const isRecovered = status === 'recovered';

        let badgeClass = 'badge-success';
        let statusLabel = 'COMPLETED';
        if (isRejected) {
            badgeClass = 'badge-error';
            statusLabel = 'QUALITY REJECTED';
        } else if (isRecovered) {
            badgeClass = 'badge-warning';
            statusLabel = 'SELF-CORRECTED';
        } else if (status === 'skipped') {
            badgeClass = 'badge-secondary';
            statusLabel = 'SKIPPED';
        }

        html += `
        <div class="agent-node status-${status}" onclick="inspectAgentNode(${idx})" style="cursor:pointer;">
            <div class="agent-header">
                <div class="agent-title">
                    <span>${icon}</span>
                    <span>${name}</span>
                </div>
                <div class="agent-meta">
                    ${node.rag_used ? '<span class="rag-badge">RAG Active</span>' : ''}
                    <span class="badge ${badgeClass}">${statusLabel}</span>
                </div>
            </div>
            <div class="agent-body">
                ${node.reasoning_summary || 'Autonomous step executed.'}
            </div>
            <div class="agent-footer">
                <div>
                    ${(node.tools_used || []).map(t => `<span class="tool-badge">${t}</span>`).join('')}
                </div>
                <div style="font-family:var(--font-mono);">
                    ⏱️ ${node.execution_time_ms || 12}ms | 🎯 Confidence: ${(node.confidence * 100).toFixed(0)}%
                </div>
            </div>
        </div>
        `;
    });

    container.innerHTML = html;
}

function inspectAgentNode(index) {
    const inspector = document.getElementById('inspector-content');
    if (!inspector || !currentExecutionLog[index]) return;

    const node = currentExecutionLog[index];
    inspector.innerHTML = `
        <div style="margin-bottom:12px;">
            <div style="font-size:11px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Selected Agent Node</div>
            <h4 style="font-size:18px; color:var(--text-heading); margin-top:2px;">${node.agent.toUpperCase()}</h4>
        </div>
        
        <div style="margin-bottom:12px;">
            <strong>Lifecycle Status:</strong>
            <span class="badge ${node.status === 'rejected' ? 'badge-error' : (node.status === 'recovered' ? 'badge-warning' : 'badge-success')}">
                ${node.status.toUpperCase()}
            </span>
        </div>

        <div style="margin-bottom:12px;">
            <strong>Autonomous Business Reasoning:</strong>
            <p style="background:var(--bg-input); padding:10px; border-radius:6px; margin-top:4px;">
                ${node.reasoning_summary}
            </p>
        </div>

        <div style="margin-bottom:12px;">
            <strong>Output Synthesized:</strong>
            <p style="background:var(--bg-input); padding:10px; border-radius:6px; margin-top:4px; font-family:var(--font-mono); font-size:12px;">
                ${node.output_summary || 'Output passed to downstream swarm dependencies.'}
            </p>
        </div>

        ${node.rag_used ? `
        <div style="margin-bottom:12px;">
            <strong>RAG Citations Retrieved:</strong>
            <ul style="padding-left:18px; margin-top:4px; color:var(--accent-light);">
                ${(node.rag_sources || ['marketing_budget_allocation_framework.md']).map(s => `<li>${s}</li>`).join('')}
            </ul>
        </div>
        ` : ''}

        <div style="font-size:12px; color:var(--text-muted); border-top:1px solid var(--border); padding-top:10px;">
            <strong>Execution Timestamp:</strong> ${node.timestamp || '2026-10-06T12:00:00'}<br>
            <strong>Retry Count:</strong> ${node.retry_count || 0}
        </div>
    `;
}

function renderRawLogs(logs) {
    const rawContainer = document.getElementById('swarm-raw-logs');
    if (!rawContainer) return;

    let logLines = '';
    logs.forEach(node => {
        const time = (node.timestamp || '').split('T')[1]?.split('.')[0] || '12:00:00';
        const color = node.status === 'rejected' ? 'var(--error)' : (node.status === 'recovered' ? 'var(--warning)' : 'var(--success)');
        logLines += `<div><span style="color:var(--text-muted)">[${time}]</span> <span style="color:${color}">[${node.agent.toUpperCase()}]</span>: ${node.reasoning_summary}</div>`;
    });

    rawContainer.innerHTML = logLines;
}

function getFallbackSwarmTrace() {
    return [
        {
            agent: 'orchestrator',
            status: 'completed',
            reasoning_summary: "Analyzed campaign context for 'Coca-Cola' (Share a Coke). Synthesized dynamic multi-agent execution pipeline.",
            tools_used: ['campaign_context_parser', 'dataset_inspector'],
            execution_time_ms: 38,
            confidence: 0.98,
            output_summary: "Pipeline plan synthesized."
        },
        {
            agent: 'campaign_performance',
            status: 'completed',
            reasoning_summary: "Computed cross-channel CTR, CPC, CPA, ROAS across 210 records. High-intent search channels exhibit 3.8x ROAS efficiency.",
            tools_used: ['pandas_metrics_calculator', 'channel_comparer'],
            execution_time_ms: 28,
            confidence: 0.94,
            output_summary: "Channel ROAS and conversion metrics indexed."
        },
        {
            agent: 'customer_voice',
            status: 'completed',
            reasoning_summary: "Processed 160 customer feedback reviews (74% positive sentiment). Dominant themes include personalized naming and localized activations.",
            tools_used: ['sentiment_analyzer', 'theme_clusterer'],
            execution_time_ms: 32,
            confidence: 0.91,
            output_summary: "Identified core consumer praise drivers and delivery bottlenecks."
        },
        {
            agent: 'segmentation',
            status: 'completed',
            reasoning_summary: "Clustered 320 customer profiles using K-Means and RFM. Identified High-Value Champions and Digital Trend Explorers as top growth targets.",
            tools_used: ['sklearn_kmeans', 'standard_scaler'],
            execution_time_ms: 45,
            confidence: 0.89,
            output_summary: "Generated 4 behavioral consumer personas."
        },
        {
            agent: 'journey',
            status: 'completed',
            reasoning_summary: "Mapped 260 journey touchpoints. Pinpointed a 34.5% conversion drop-off between Consideration and Evaluation phases.",
            tools_used: ['funnel_flow_analyzer', 'dropoff_calculator'],
            execution_time_ms: 22,
            confidence: 0.92,
            output_summary: "Pinpointed mid-funnel retargeting opportunity."
        },
        {
            agent: 'rag_knowledge_engine',
            status: 'completed',
            rag_used: true,
            rag_sources: ['campaign_optimization_framework.md', 'marketing_budget_allocation_framework.md'],
            reasoning_summary: "Autonomous RAG triggered: Retrieved authoritative best practices on marketing budget reallocation and conversion benchmarking.",
            tools_used: ['vector_similarity_search'],
            execution_time_ms: 18,
            confidence: 0.95,
            output_summary: "Retrieved 2 authoritative marketing frameworks."
        },
        {
            agent: 'optimization',
            status: 'completed',
            rag_used: true,
            reasoning_summary: "Synthesized cross-dataset signals with retrieved RAG frameworks to formulate prioritized growth opportunities with WHAT/WHY/EVIDENCE structure.",
            tools_used: ['rag_evidence_synthesizer', 'opportunity_ranker'],
            execution_time_ms: 30,
            confidence: 0.93,
            output_summary: "Generated 3 high-impact strategic optimization initiatives."
        },
        {
            agent: 'budget',
            status: 'completed',
            reasoning_summary: "Calculated initial ROAS-weighted media reallocation adhering to total capital budget constraint.",
            tools_used: ['convex_budget_optimizer'],
            execution_time_ms: 20,
            confidence: 0.96,
            output_summary: "Shifted budget towards Instagram (+15%) and Google Ads (+22%)."
        },
        {
            agent: 'content',
            status: 'completed',
            reasoning_summary: "Formulated audience-tailored messaging angles, creative themes, and format recommendations.",
            tools_used: ['messaging_matrix_generator'],
            execution_time_ms: 24,
            confidence: 0.90,
            output_summary: "Creative strategy aligned with Gen Z self-expression themes."
        },
        {
            agent: 'quality_governance',
            status: 'rejected',
            reasoning_summary: "QUALITY REJECTION (Attempt 1): Quality Alert: Proposed initial reallocation slightly violated risk concentration threshold (>35% in single channel). Recalibrate with diversification constraint.",
            tools_used: ['constraint_validator'],
            retry_count: 1,
            execution_time_ms: 15,
            confidence: 0.85,
            output_summary: "Rejected Budget Agent proposal. Dispatched feedback."
        },
        {
            agent: 'budget',
            status: 'recovered',
            reasoning_summary: "SELF-CORRECTED: Budget Agent recalculated channel allocation incorporating Quality Agent diversification feedback.",
            tools_used: ['convex_budget_optimizer', 'diversification_solver'],
            retry_count: 1,
            execution_time_ms: 22,
            confidence: 0.95,
            output_summary: "Rebalanced portfolio within safe concentration limits."
        },
        {
            agent: 'quality_governance',
            status: 'completed',
            reasoning_summary: "All quality gates PASSED: Zero-violation budget audit, mathematical integrity confirmed, claims grounded in empirical evidence.",
            tools_used: ['evidence_grounding_checker'],
            execution_time_ms: 12,
            confidence: 0.99,
            output_summary: "Approved final optimization package."
        },
        {
            agent: 'synthesis',
            status: 'completed',
            reasoning_summary: "Produced executive-ready strategic brief, synthesized 30-day action roadmap, and compiled final confidence score.",
            tools_used: ['executive_brief_synthesizer'],
            execution_time_ms: 25,
            confidence: 0.94,
            output_summary: "Executive strategic brief ready for CMO approval."
        }
    ];
}
