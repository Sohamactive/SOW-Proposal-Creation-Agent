const API_BASE = window.location.origin;

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
const loaderTitle = document.getElementById("loaderTitle");
const loaderText = document.getElementById("loaderText");
const reviewStatus = document.getElementById("reviewStatus");
const projectDocExtracted = document.getElementById("projectDocExtracted");
const downloadDocxLink = document.getElementById("downloadDocxLink");
const reviewSummary = document.getElementById("reviewSummary");


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


function renderProposal(proposal) {
    if (!proposal || typeof proposal !== "object") {
        proposalOutput.className = "proposal-preview empty-state";
        proposalOutput.innerHTML = "Proposal output will appear here.";
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
        reviewSummary.className = "review-summary empty-state";
        reviewSummary.textContent = "Review feedback will appear here.";
        return;
    }

    const issues = Array.isArray(review.issues) ? review.issues : [];
    const suggestions = Array.isArray(review.suggestions) ? review.suggestions : [];
    const status = review.status ? escapeHtml(review.status) : "generated";

    reviewSummary.className = "review-summary";
    reviewSummary.innerHTML = `
        <div class="review-pill ${status.toLowerCase()}">${status}</div>
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


function setLoading(active, title = "Working...", description = "The backend is processing your request.") {
    loaderTitle.textContent = title;
    loaderText.textContent = description;
    loader.classList.toggle("hidden", !active);

    uploadProjectDocBtn.disabled = active;
    uploadKnowledgeDocBtn.disabled = active;
    generateProposalBtn.disabled = active;
}


function showMessage(text, tone = "info") {
    messageBanner.textContent = text;
    messageBanner.className = `message-banner ${tone}`;
}


function clearMessage() {
    messageBanner.textContent = "";
    messageBanner.className = "message-banner hidden";
}


async function parseResponse(response) {
    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
        const detail = payload.detail || "Request failed";
        throw new Error(detail);
    }

    return payload;
}


async function uploadProjectDoc() {
    const file = projectDocInput.files[0];

    if (!file) {
        showMessage("Choose a project document before uploading.", "error");
        return;
    }

    clearMessage();
    setLoading(true, "Uploading project document", "Extracting text from the uploaded project file.");

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
        setLoading(false);
    }
}


async function uploadKnowledgeDoc() {
    const file = knowledgeDocInput.files[0];

    if (!file) {
        showMessage("Choose a knowledge-base document before uploading.", "error");
        return;
    }

    clearMessage();
    setLoading(true, "Indexing knowledge document", "Creating chunks, embeddings, and vector records.");

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
        setLoading(false);
    }
}


async function generateProposal() {
    const description = projectInput.value.trim();

    if (!description && !extractedProjectText) {
        showMessage("Provide a project description or upload a project document first.", "error");
        return;
    }

    clearMessage();
    downloadDocxLink.classList.add("hidden");
    reviewStatus.textContent = "Generating...";
    reviewSummary.className = "review-summary empty-state";
    reviewSummary.textContent = "Review feedback will appear here.";
    proposalOutput.className = "proposal-preview empty-state";
    proposalOutput.textContent = "Generating proposal...";
    setLoading(true, "Generating proposal", "Running the agent pipeline and preparing the DOCX file.");

    try {
        const response = await fetch(`${API_BASE}/generate-proposal`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                description,
                project_docs: extractedProjectText
            })
        });

        const data = await parseResponse(response);
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
        reviewSummary.className = "review-summary empty-state";
        reviewSummary.textContent = "Review feedback unavailable because generation failed.";
        proposalOutput.className = "proposal-preview empty-state";
        proposalOutput.textContent = "Proposal generation failed.";
        showMessage(error.message, "error");
    } finally {
        setLoading(false);
    }
}


uploadProjectDocBtn.addEventListener("click", uploadProjectDoc);
uploadKnowledgeDocBtn.addEventListener("click", uploadKnowledgeDoc);
generateProposalBtn.addEventListener("click", generateProposal);