# MarketPilot AI — Executive Academic Presentation Slides

**Title:** MarketPilot AI: A Multi-Agent Marketing Campaign Optimization and Customer Response Automation System  
**Course:** MBA / PGDM in Agentic AI for Business Automation (2025–2026)  
**Presented by:** Group 6  
- Aditya Mishra  
- Aman Kumar Singh  
- Hardik Srivastava  
- Rohit Kumar Jha  
- Shouvik Das  
- Satyam Raj  

---

## Slide 1: Title & Overview
- **Header:** MarketPilot AI: Production-Grade Multi-Agent Marketing Decision Support
- **Subtitle:** Autonomous Campaign Analytics, Grounded RAG Optimization, and Enterprise Workflow Automation
- **Presenter Notes:** Good morning, members of the evaluation panel. We are Group 6, presenting MarketPilot AI—a comprehensive enterprise solution designed to bridge the gap between complex multi-channel marketing data and strategic executive decisions using an autonomous swarm of 10 specialized AI agents.

---

## Slide 2: The Business Problem
- **Header:** The Fragmented Reality of Modern Digital Marketing
- **Core Pain Points:**
  - **Siloed Multichannel Data:** Performance logs, social sentiment, and user journeys reside in disconnected tools.
  - **The Reporting Delay:** Traditional BI tools report historical outcomes weeks late without prescribing corrective actions.
  - **Budget Allocation Inertia:** Media spend is adjusted by intuition rather than marginal ROAS elasticity curves.
  - **Arithmetic Fragility:** Manual calculations often lead to over-budget violations or channel starvation.
- **Presenter Notes:** Marketing managers are overwhelmed by data silos. While dashboards visualize historical drops in conversion, they cannot diagnose whether the issue stems from creative fatigue, pricing friction, or channel misallocation.

---

## Slide 3: The MarketPilot AI Solution
- **Header:** An AI Marketing Department in a Single Platform
- **Key Capabilities:**
  - **10 Autonomous Specialized Agents:** Replicating the functions of data scientists, media planners, copywriters, and compliance officers.
  - **Deterministic-AI Separation:** Mathematical calculations handled via pure Python (`pandas`/`numpy`); strategic reasoning and narrative handled via LLMs (Google Gemini / OpenAI).
  - **Fuzzy Input Normalization:** Intelligent pre-flight spellcheck and entity resolution with human confirmation.
  - **Agentic RAG:** Recommendations grounded in 10 authoritative marketing strategy frameworks.
  - **Enterprise n8n Automation:** Outbound webhook dispatch to Google Sheets, Google Drive, and Gmail.
- **Presenter Notes:** MarketPilot AI acts like an agile marketing team. It ingests data, normalizes inputs, computes empirical KPIs, retrieves marketing frameworks, and formulates auditable, budget-conserving recommendations.

---

## Slide 4: System Architecture
- **Header:** Layered, Decoupled Production Architecture
- **Components:**
  - **Frontend:** Semantic SPA (Dark/Light mode) with interactive Chart.js visualizations.
  - **API Engine:** Asynchronous FastAPI backend providing RESTful endpoints and state management.
  - **Analytical Core:** Pure Python scientific pipeline (`pandas`, `numpy`, `scikit-learn`).
  - **Semantic Layer:** Dual-engine RAG (ChromaDB + zero-dependency TF-IDF fallback) with LLM abstractions.
  - **Automation:** Outbound HTTPS webhooks connected to n8n Cloud and Google Workspace.
- **Presenter Notes:** Our system architecture strictly isolates concerns. The frontend communicates with FastAPI REST endpoints, while heavy analytical computations are executed deterministically before prompting LLMs for strategic synthesis.

---

## Slide 5: The 10-Agent Swarm Hierarchy
- **Header:** Autonomous Specialization & Dependency-Aware Orchestration
- **Agent Roles:**
  1. **Orchestrator Agent:** Dynamic pipeline planning and failure recovery.
  2. **Campaign Performance Agent:** Empirical KPI calculations (ROAS, CPA, CTR, CPC).
  3. **Customer Voice Agent:** Lexicon-based polarity scoring and qualitative pain-point extraction.
  4. **Segmentation Agent:** RFM analysis and $k$-means clustering across customer cohorts.
  5. **Customer Journey Agent:** Funnel transition mapping and drop-off identification.
  6. **Optimization Agent:** Cross-functional synthesis and opportunity prioritization.
  7. **Budget Allocation Agent:** Performance-weighted mathematical spend optimization.
  8. **Content Recommendation Agent:** Audience-tailored messaging, creative hooks, and CTAs.
  9. **Quality Governance Agent:** Automated audit of budget limits, math consistency, and data grounding.
  10. **Final Synthesis Agent:** Executive summary, 30-day tactical roadmap, and confidence scorecard.
- **Presenter Notes:** Rather than using a single monolithic prompt, we deploy 10 specialized agents organized by clear dependencies. Data-analysis agents run first, followed by strategy agents, quality governance, and executive synthesis.

---

## Slide 6: Agentic RAG (Retrieval-Augmented Generation)
- **Header:** Grounding Strategic Decisions in Marketing Science
- **Knowledge Base Composition:**
  - 10 curated markdown frameworks covering KPI metrics, budget allocation models, customer journey funnels, A/B testing, and retention economics.
  - Documents chunked into 500-token semantic segments with 50-token overlaps.
- **Agentic Decision Heuristics:**
  - Agents evaluate `should_retrieve()` before triggering vector searches.
  - ChromaDB vector retrieval returns top $k=5$ most relevant chunks with cosine similarity ranking.
- **Presenter Notes:** To eliminate AI hallucinations, all recommendations cite validated marketing literature. When our Budget Agent reallocates spend, it retrieves our *Marketing Budget Allocation Framework* to apply marginal diminishing returns.

---

## Slide 7: Input Normalization & State Machine
- **Header:** Pre-Flight Data Quality & User Verification
- **Workflow:**
  - User submits campaign parameters (e.g., `cocacola`, `Share a cok`, `delhi ncr`).
  - SequenceMatcher fuzzy matching detects brand/channel entities against known registries.
  - System presents interactive verification modal: Accept Suggestion, Keep Original, or Edit Manually.
  - Hard state gate: `INPUT_VERIFICATION = COMPLETE` must be reached before swarm execution can be triggered.
- **Presenter Notes:** Bad input ruins automated pipelines. MarketPilot AI catches spelling mistakes and entity variations upfront, presenting an audit trail for user confirmation before starting the multi-agent pipeline.

---

## Slide 8: What-If Scenario Simulator
- **Header:** Real-Time Interactive Budget Simulation
- **Features:**
  - Interactive channel spend sliders with instant client-side recalculation.
  - Deterministic simulation model calculating projected revenue, blended ROAS, and incremental gains.
  - Automated Portfolio Risk Scoring: Flags channel over-concentration exceeding 40% threshold.
  - Strict Budget Enforcement: Validates that total simulated spend matches available capital.
- **Presenter Notes:** Marketing leadership constantly evaluates hypothetical spend adjustments. Our Scenario Simulator enables executives to model channel shifts in real-time with instant risk and revenue projections.

---

## Slide 9: Quality Governance & Error Recovery Loop
- **Header:** Zero-Hallucination Financial & Logical Governance
- **Automated Validation Rules:**
  - **Budget Conservation Law:** Total recommended spend must match campaign budget within 0.1% tolerance ($\sum B_{\text{proposed}} = B_{\text{total}}$).
  - **Arithmetic Consistency:** Revenue claims must align with empirical ROAS ratios.
  - **Evidence Grounding:** Recommendations must cite observed data or RAG knowledge chunks.
- **Self-Correction:**
  - If Quality Governance detects an anomaly, it rejects the output and triggers a targeted retry with feedback context (maximum 2 retries).
- **Presenter Notes:** Trust in AI requires ironclad guardrails. The Quality Governance Agent mathematically verifies that proposed budgets do not exceed total capital, automatically re-running agents if discrepancies occur.

---

## Slide 10: Human-in-the-Loop & n8n Enterprise Automation
- **Header:** From Strategic Approval to Enterprise Execution
- **Approval Gateway:**
  - Executive inspects dashboard findings, budget shifts, and quality certifications.
  - Outbound actions require explicit **[Approve Recommendations]** authorization.
- **n8n Cloud Webhook Workflow:**
  - Webhook receives structured JSON payload (`POST /webhook/marketpilot`).
  - Appends campaign metrics into **Google Sheets** (*MarketPilot Campaign Insights*).
  - Archives executive summary report in **Google Drive** (*MarketPilot Reports*).
  - Dispatches executive email summary via **Gmail**.
- **Presenter Notes:** The AI proposes, but the human decides. Once an executive approves, MarketPilot AI triggers n8n Cloud webhooks to automatically log results across Google Workspace.

---

## Slide 11: Production Verification & Cloud Deployment
- **Header:** Production Readiness, Test Coverage & Cloud Architecture
- **Automated Testing:**
  - **69 automated pytest tests** covering normalization, validation, agent logic, RAG retrieval, scenarios, and API endpoints.
  - **100% test pass rate** with zero errors or warnings.
- **Cloud Deployment:**
  - Cloud-native packaging on **Render** using native Python runtime and dynamic `$PORT` binding.
  - Version controlled on **GitHub** with clean CI/CD auto-deploy capability.
- **Presenter Notes:** MarketPilot AI is not a prototype mockup. All 69 automated tests pass with 100% accuracy, and the application is fully deployable to Render with zero local state dependencies.

---

## Slide 12: Summary, Academic Impact & Q&A
- **Header:** Key Takeaways & Questions
- **Summary of Contributions:**
  - Replaced slow, fragmented analysis with an integrated 10-agent autonomous workflow.
  - Proved the necessity of separating deterministic mathematical calculations from LLM qualitative reasoning.
  - Delivered end-to-end enterprise automation from fuzzy data entry to Google Workspace logging.
- **Thank you! We invite questions from the panel.**
