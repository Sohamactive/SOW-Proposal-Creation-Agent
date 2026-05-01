const API_BASE = window.location.origin;
const JOB_POLL_INTERVAL_MS = 1600;
const JOB_POLL_MAX_RETRIES = 20;
const JOB_MAX_WAIT_MS = 10 * 60 * 1000;

let extractedProjectText = "";

const projectInput = document.getElementById("project_input");
const projectDocInput = document.getElementById("projectDoc");
const knowledgeDocInput = document.getElementById("knowledgeDoc");
const uploadProjectDocBtn = document.getElementById("uploadProjectDocBtn");
const uploadKnowledgeDocBtn = document.getElementById("uploadKnowledgeDocBtn");
const generateProposalBtn = document.getElementById("generateProposalBtn");
const projectDocStatus = document.getElementById("projectDocStatus");
const knowledgeDocStatus = document.getElementById("knowledgeDocStatus");
const proposalOutput = document.getElementById("proposal_output");
const messageBanner = document.getElementById("messageBanner");
const loader = document.getElementById("loader");
const reviewStatus = document.getElementById("reviewStatus");
const projectDocExtracted = document.getElementById("projectDocExtracted");
const downloadDocxLink = document.getElementById("downloadDocxLink");
const reviewSummary = document.getElementById("reviewSummary");
const pipelineProgress = document.getElementById("pipelineProgress");
const pipelineTrack = loader.querySelector(".pipeline-track");
const pipelineSteps = Array.from(document.querySelectorAll(".pipeline-step"));
const themeToggle = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");
const htmlRoot = document.documentElement;

const proposalEmptyStateMarkup = `
    <div class="empty-state-art" role="img" aria-label="Document placeholder">
        <svg viewBox="0 0 64 64" width="64" height="64" aria-hidden="true" focusable="false">
            <path d="M18 6h20l12 12v40H18z" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"></path>
            <path d="M38 6v12h12" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"></path>
            <path d="M26 32h16M26 40h16M26 48h10" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"></path>
        </svg>
    </div>
    <h3>Your proposal will appear here</h3>
    <p>Fill in the details and click Generate to begin.</p>
`;

const reviewEmptyStateMarkup = `
    <div class="empty-review">
        <p class="empty-review-title">QA summary pending</p>
        <p class="empty-review-copy">Review checks appear after generation.</p>
    </div>
`;


function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}


function formatLabel(key) {
    return key
        .replaceAll("_", " ")
        .replace(/\b\w/g, (match) => match.toUpperCase());
}


function normalizeStatusClass(status) {
    return String(status || "pending")
        .toLowerCase()
        .trim()
        .replaceAll(" ", "_");
}


function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}


function setBusy(active) {
    uploadProjectDocBtn.disabled = active;
    uploadKnowledgeDocBtn.disabled = active;
    generateProposalBtn.disabled = active;
}


function applyPipelineStep(stepIndex) {
    const maxIndex = Math.max(0, pipelineSteps.length - 1);
    const boundedIndex = Math.max(0, Math.min(stepIndex, maxIndex));

    pipelineSteps.forEach((stepNode, index) => {
        stepNode.classList.remove("active", "completed");

        if (index < boundedIndex) {
            stepNode.classList.add("completed");
        } else if (index === boundedIndex) {
            stepNode.classList.add("active");
        }
    });

    const progress = maxIndex === 0 ? 0 : (boundedIndex / maxIndex) * 100;
    pipelineProgress.style.width = `${progress}%`;
    pipelineTrack.setAttribute("aria-valuenow", String(Math.round(progress)));
}


function startPipeline() {
    loader.classList.remove("hidden");
    applyPipelineStep(0);
}


function stopPipeline() {
    loader.classList.add("hidden");
    applyPipelineStep(0);
}


function updatePipelineFromJob(jobPayload) {
    const stepIndex = Number(jobPayload.step_index || 0);
    applyPipelineStep(stepIndex);

    if (jobPayload.status === "running" && jobPayload.step_label) {
        reviewStatus.textContent = `Running: ${jobPayload.step_label}`;
    }
}


function showMessage(text, tone = "info") {
    const icons = {
        info: "&#9432;",
        success: "&#10003;",
        error: "&#10005;"
    };

    const safeTone = ["info", "success", "error"].includes(tone) ? tone : "info";
    messageBanner.className = `message-banner ${safeTone}`;
    messageBanner.innerHTML = `
        <span class="banner-icon" role="img" aria-label="${safeTone}">${icons[safeTone]}</span>
        <span>${escapeHtml(text)}</span>
    `;
}


function clearMessage() {
    messageBanner.textContent = "";
    messageBanner.className = "message-banner hidden";
}


function renderValue(value, depth = 0) {
    if (value === null || value === undefined || value === "") {
        return '<p class="value-empty">Not provided.</p>';
    }

    if (typeof value === "string") {
        const paragraphs = value
            .split(/\n{2,}/)
            .map((chunk) => chunk.trim())
            .filter(Boolean)
            .map((chunk) => `<p>${escapeHtml(chunk)}</p>`)
            .join("");

        return paragraphs || `<p>${escapeHtml(value)}</p>`;
    }

    if (Array.isArray(value)) {
        if (!value.length) {
            return '<p class="value-empty">Not provided.</p>';
        }

        const items = value.map((item) => {
            if (typeof item === "object" && item !== null) {
                return `<li>${renderObject(item, depth + 1, true)}</li>`;
            }

            return `<li>${escapeHtml(item)}</li>`;
        }).join("");

        return `<ul class="proposal-list">${items}</ul>`;
    }

    if (typeof value === "object") {
        return renderObject(value, depth + 1);
    }

    return `<p>${escapeHtml(value)}</p>`;
}


function renderObject(objectValue, depth = 0, compact = false) {
    const entries = Object.entries(objectValue);

    if (!entries.length) {
        return '<p class="value-empty">Not provided.</p>';
    }

    const tag = depth <= 1 ? "h3" : "h4";
    const className = compact ? "nested-grid compact" : "nested-grid";

    return `
        <div class="${className}">
            ${entries.map(([key, value]) => `
                <section class="nested-section">
                    <${tag}>${escapeHtml(formatLabel(key))}</${tag}>
                    ${renderValue(value, depth)}
                </section>
            `).join("")}
        </div>
    `;
}


function setProposalEmptyState() {
    proposalOutput.className = "proposal-preview empty-state-panel";
    proposalOutput.innerHTML = proposalEmptyStateMarkup;
}


function setReviewEmptyState() {
    reviewSummary.className = "review-summary empty-state-panel";
    reviewSummary.innerHTML = reviewEmptyStateMarkup;
}


function renderProposal(proposal) {
    if (!proposal || typeof proposal !== "object") {
        setProposalEmptyState();
        return;
    }

    const sections = Object.entries(proposal).map(([section, content]) => `
        <article class="proposal-section">
            <h3>${escapeHtml(formatLabel(section))}</h3>
            <div class="proposal-section-body">
                ${renderValue(content)}
            </div>
        </article>
    `).join("");

    proposalOutput.className = "proposal-preview";
    proposalOutput.innerHTML = sections;
}


function renderReview(review) {
    if (!review || typeof review !== "object") {
        setReviewEmptyState();
        return;
    }

    const issues = Array.isArray(review.issues) ? review.issues : [];
    const suggestions = Array.isArray(review.suggestions) ? review.suggestions : [];
    const rawStatus = review.status ? escapeHtml(review.status) : "pending";
    const normalizedStatus = normalizeStatusClass(rawStatus);

    reviewSummary.className = "review-summary";
    reviewSummary.innerHTML = `
        <div class="review-pill ${normalizedStatus}">${rawStatus}</div>
        <div class="review-grid">
            <section>
                <h3>Issues</h3>
                ${issues.length ? `<ul class="proposal-list">${issues.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : '<p class="value-empty">No issues reported.</p>'}
            </section>
            <section>
                <h3>Suggestions</h3>
                ${suggestions.length ? `<ul class="proposal-list">${suggestions.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : '<p class="value-empty">No suggestions reported.</p>'}
            </section>
        </div>
    `;
}


async function parseResponse(response) {
    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
        const detail = payload.detail || payload.error || "Request failed";
        throw new Error(detail);
    }

    return payload;
}


function setTheme(theme) {
    const nextTheme = theme === "dark" ? "dark" : "light";
    htmlRoot.setAttribute("data-theme", nextTheme);
    themeToggle.setAttribute("aria-label", nextTheme === "dark" ? "Switch to light mode" : "Switch to dark mode");
    themeIcon.textContent = nextTheme === "dark" ? "\u2600" : "\u263D";
    localStorage.setItem("sow-theme", nextTheme);
}


function initializeTheme() {
    const savedTheme = localStorage.getItem("sow-theme");

    if (savedTheme === "dark" || savedTheme === "light") {
        setTheme(savedTheme);
        return;
    }

    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    setTheme(prefersDark ? "dark" : "light");
}


async function uploadProjectDoc() {
    const file = projectDocInput.files[0];

    if (!file) {
        showMessage("Choose a project document before uploading.", "error");
        return;
    }

    clearMessage();
    setBusy(true);

    try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_BASE}/upload-project-doc`, {
            method: "POST",
            body: formData
        });

        const result = await parseResponse(response);
        extractedProjectText = result.text || "";
        projectDocStatus.textContent = `${file.name} processed successfully.`;
        projectDocStatus.className = "status-text success";
        projectDocExtracted.textContent = extractedProjectText ? "Yes" : "No";
        showMessage("Project document processed and ready to be used in proposal generation.", "success");
    } catch (error) {
        extractedProjectText = "";
        projectDocExtracted.textContent = "No";
        projectDocStatus.textContent = "Project document upload failed.";
        projectDocStatus.className = "status-text error";
        showMessage(error.message, "error");
    } finally {
        setBusy(false);
    }
}


async function uploadKnowledgeDoc() {
    const file = knowledgeDocInput.files[0];

    if (!file) {
        showMessage("Choose a knowledge-base document before uploading.", "error");
        return;
    }

    clearMessage();
    setBusy(true);

    try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_BASE}/upload-knowledge-doc`, {
            method: "POST",
            body: formData
        });

        const result = await parseResponse(response);
        knowledgeDocStatus.textContent = `${file.name} indexed with ${result.chunks} chunks.`;
        knowledgeDocStatus.className = "status-text success";
        showMessage("Knowledge-base document indexed successfully.", "success");
    } catch (error) {
        knowledgeDocStatus.textContent = "Knowledge document upload failed.";
        knowledgeDocStatus.className = "status-text error";
        showMessage(error.message, "error");
    } finally {
        setBusy(false);
    }
}


async function createProposalJob(description) {
    const response = await fetch(`${API_BASE}/generate-proposal-job`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            description,
            project_docs: extractedProjectText
        })
    });

    return parseResponse(response);
}


async function fetchProposalJob(jobId) {
    const response = await fetch(`${API_BASE}/proposal-job/${jobId}`, {
        method: "GET"
    });

    return parseResponse(response);
}


async function waitForProposalJob(jobId) {
    let consecutiveFailures = 0;
    const startedAt = Date.now();

    for (;;) {
        if (Date.now() - startedAt > JOB_MAX_WAIT_MS) {
            throw new Error("Generation exceeded max wait time. Please retry.");
        }

        try {
            const job = await fetchProposalJob(jobId);
            if (consecutiveFailures > 0) {
                clearMessage();
            }
            consecutiveFailures = 0;
            updatePipelineFromJob(job);

            if (job.status === "completed") {
                return job.result;
            }

            if (job.status === "failed") {
                throw new Error(job.error || "Proposal generation failed");
            }

            await sleep(JOB_POLL_INTERVAL_MS);
        } catch (error) {
            consecutiveFailures += 1;

            if (consecutiveFailures >= JOB_POLL_MAX_RETRIES) {
                throw error;
            }

            showMessage(
                `Network unstable while tracking job. Retrying (${consecutiveFailures}/${JOB_POLL_MAX_RETRIES})...`,
                "info"
            );
            await sleep(Math.min(5000, JOB_POLL_INTERVAL_MS * consecutiveFailures));
        }
    }
}


async function generateProposal() {
    const description = projectInput.value.trim();

    if (!description && !extractedProjectText) {
        showMessage("Provide a project description or upload a project document first.", "error");
        return;
    }

    clearMessage();
    setBusy(true);
    startPipeline();
    downloadDocxLink.classList.add("hidden");
    reviewStatus.textContent = "Generating";
    setReviewEmptyState();
    setProposalEmptyState();

    try {
        const createdJob = await createProposalJob(description);
        const data = await waitForProposalJob(createdJob.job_id);

        reviewStatus.textContent = data.review?.status || "Generated";
        renderReview(data.review);
        renderProposal(data.proposal);

        if (data.files?.docx_download_url) {
            downloadDocxLink.href = `${API_BASE}${data.files.docx_download_url}`;
            downloadDocxLink.download = data.files.docx_name || "proposal.docx";
            downloadDocxLink.classList.remove("hidden");
        }

        showMessage("Proposal generated successfully. The DOCX download is ready.", "success");
    } catch (error) {
        reviewStatus.textContent = "Failed";
        setReviewEmptyState();
        setProposalEmptyState();
        showMessage(error.message, "error");
    } finally {
        stopPipeline();
        setBusy(false);
    }
}


function onProjectDocSelected() {
    const file = projectDocInput.files[0];
    if (!file) {
        projectDocStatus.textContent = "No project document uploaded.";
        projectDocStatus.className = "status-text muted";
        return;
    }

    projectDocStatus.textContent = `${file.name} selected.`;
    projectDocStatus.className = "status-text muted";
}


function onKnowledgeDocSelected() {
    const file = knowledgeDocInput.files[0];
    if (!file) {
        knowledgeDocStatus.textContent = "No knowledge-base document uploaded.";
        knowledgeDocStatus.className = "status-text muted";
        return;
    }

    knowledgeDocStatus.textContent = `${file.name} selected.`;
    knowledgeDocStatus.className = "status-text muted";
}


uploadProjectDocBtn.addEventListener("click", uploadProjectDoc);
uploadKnowledgeDocBtn.addEventListener("click", uploadKnowledgeDoc);
generateProposalBtn.addEventListener("click", generateProposal);
projectDocInput.addEventListener("change", onProjectDocSelected);
knowledgeDocInput.addEventListener("change", onKnowledgeDocSelected);
themeToggle.addEventListener("click", () => {
    const activeTheme = htmlRoot.getAttribute("data-theme") === "dark" ? "dark" : "light";
    setTheme(activeTheme === "dark" ? "light" : "dark");
});

initializeTheme();
setProposalEmptyState();
setReviewEmptyState();
