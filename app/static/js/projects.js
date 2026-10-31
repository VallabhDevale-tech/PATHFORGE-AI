/**
 * PATHFORGE AI - Project Recommendations & Portfolio Client Script (Feature 5)
 * Handles project recommendation generation from skill gaps, architecture guide modals,
 * saving projects to portfolio, tracking progress, and recording live GitHub/demo links.
 */

document.addEventListener("DOMContentLoaded", () => {
  let currentToken = localStorage.getItem("pathforge_auth_token") || "";
  let supabaseClient = null;
  let allProjects = [];
  let selectedModalProject = null;

  if (window.PATHFORGE_CONFIG && window.PATHFORGE_CONFIG.supabaseUrl && window.PATHFORGE_CONFIG.supabaseKey) {
    try {
      supabaseClient = window.supabase.createClient(
        window.PATHFORGE_CONFIG.supabaseUrl,
        window.PATHFORGE_CONFIG.supabaseKey
      );
    } catch (e) {}
  }

  // DOM Elements
  const userEmailBadge = document.getElementById("userEmailBadge");
  const userEmailText = document.getElementById("userEmailText");
  const logoutBtn = document.getElementById("logoutBtn");

  const alertBox = document.getElementById("alertBox");
  const alertIcon = document.getElementById("alertIcon");
  const alertMessage = document.getElementById("alertMessage");

  const refreshProjectsBtn = document.getElementById("refreshProjectsBtn");
  const projSpinner = document.getElementById("projSpinner");
  const recommendedProjectsList = document.getElementById("recommendedProjectsList");
  const portfolioProjectsList = document.getElementById("portfolioProjectsList");
  const portfolioCountBadge = document.getElementById("portfolioCountBadge");

  // Modals
  const architectureModal = new bootstrap.Modal(document.getElementById("architectureModal"));
  const modalProjectTitle = document.getElementById("modalProjectTitle");
  const modalProjectDifficulty = document.getElementById("modalProjectDifficulty");
  const architectureModalBody = document.getElementById("architectureModalBody");
  const modalSaveProjectBtn = document.getElementById("modalSaveProjectBtn");

  const updateLinksModal = new bootstrap.Modal(document.getElementById("updateLinksModal"));
  const editProjectId = document.getElementById("editProjectId");
  const editProjectStatus = document.getElementById("editProjectStatus");
  const editProjectGithub = document.getElementById("editProjectGithub");
  const editProjectDemo = document.getElementById("editProjectDemo");
  const editProjectNotes = document.getElementById("editProjectNotes");
  const saveProjectLinksBtn = document.getElementById("saveProjectLinksBtn");

  function showAlert(message, type = "info") {
    alertBox.className = `alert alert-${type} mb-4 glass-card border-0 d-block`;
    alertMessage.textContent = message;
    alertIcon.className = type === "danger" ? "bi bi-exclamation-triangle-fill text-danger fs-4" : "bi bi-check-circle-fill text-success fs-4";
  }

  function hideAlert() {
    alertBox.className = "alert d-none mb-4 glass-card border-0";
  }

  async function initAuth() {
    // 1. Instant auth verification from localStorage (0ms UI render)
    if (currentToken) {
      try {
        const payload = JSON.parse(atob(currentToken.split(".")[1]));
        if (!payload.exp || (payload.exp * 1000 > Date.now())) {
          setAuthenticatedState(currentToken, payload.email || "Authenticated User");

          // Verify & refresh silently in background without blocking UI
          if (supabaseClient) {
            supabaseClient.auth.getSession().then(({ data }) => {
              if (data && data.session && data.session.access_token) {
                currentToken = data.session.access_token;
                localStorage.setItem("pathforge_auth_token", currentToken);
              }
            }).catch(() => {});
          }
          return;
        }
      } catch (e) {
        localStorage.removeItem("pathforge_auth_token");
      }
    }

    // 2. Fallback to Supabase getSession if token was missing
    if (supabaseClient) {
      try {
        const { data } = await supabaseClient.auth.getSession();
        if (data && data.session && data.session.access_token) {
          setAuthenticatedState(data.session.access_token, data.session.user.email);
          return;
        }
      } catch (err) {}
    }

    window.location.replace("/");
  }

  function setAuthenticatedState(token, email) {
    currentToken = token;
    localStorage.setItem("pathforge_auth_token", token);
    if (userEmailText) userEmailText.textContent = email;
    loadProjects();
  }

  logoutBtn?.addEventListener("click", async () => {
    if (supabaseClient) try { await supabaseClient.auth.signOut(); } catch (e) {}
    localStorage.removeItem("pathforge_auth_token");
    window.location.replace("/");
  });

  // Load Projects
  async function loadProjects(forceRefresh = false) {
    if (!currentToken) return;

    if (!forceRefresh) {
      try {
        const res = await fetch("/projects", {
          headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const data = await res.json();
        if (res.ok && data.data && data.data.length > 0) {
          allProjects = data.data;
          renderProjectPanes();
          return;
        }
      } catch (e) {}
    }

    // Otherwise generate fresh recommendations
    triggerProjectGeneration();
  }

  async function triggerProjectGeneration() {
    hideAlert();
    refreshProjectsBtn.disabled = true;
    projSpinner.classList.remove("d-none");

    try {
      const res = await fetch("/projects/recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${currentToken}`
        },
        body: JSON.stringify({})
      });
      const data = await res.json();
      refreshProjectsBtn.disabled = false;
      projSpinner.classList.add("d-none");

      if (!res.ok) {
        if (data.detail && data.detail.includes("No Skill Gap Report")) {
          showAlert("Please run the Skill Gap Analyzer first to tailor projects to your skill gaps.", "warning");
          recommendedProjectsList.innerHTML = `
            <div class="col-12 text-center py-5 glass-card">
              <i class="bi bi-bar-chart-steps fs-1 text-primary d-block mb-3"></i>
              <h4 class="fw-bold text-white">No Skill Gap Report Found</h4>
              <p class="text-muted mb-4">PATHFORGE needs your skill gap analysis results to recommend targeted portfolio projects.</p>
              <a href="/skill-gap-analyzer" class="btn btn-primary-gradient rounded-pill px-4 py-2">
                <i class="bi bi-lightning-charge me-1"></i> Go to Skill Gap Analyzer
              </a>
            </div>
          `;
          return;
        }
        throw new Error(data.detail || "Failed to generate project recommendations.");
      }

      allProjects = data.data || [];
      renderProjectPanes();
      showAlert("Recommended projects generated successfully based on your skill gaps!", "success");
    } catch (err) {
      refreshProjectsBtn.disabled = false;
      projSpinner.classList.add("d-none");
      showAlert(err.message, "danger");
    }
  }

  refreshProjectsBtn?.addEventListener("click", () => {
    triggerProjectGeneration();
  });

  // Render Both Panes (Recommended & Portfolio)
  function renderProjectPanes() {
    // 1. Recommended Pane
    const recommended = allProjects.filter(p => p.status === "recommended" || !p.status);
    if (recommended.length === 0) {
      recommendedProjectsList.innerHTML = '<div class="col-12 text-center py-4 text-muted">All recommended projects have been saved to your portfolio!</div>';
    } else {
      recommendedProjectsList.innerHTML = recommended.map(p => renderProjectCardHtml(p, false)).join("");
    }

    // 2. Portfolio Pane
    const portfolio = allProjects.filter(p => ["saved", "in_progress", "completed"].includes(p.status));
    portfolioCountBadge.textContent = portfolio.length;

    if (portfolio.length === 0) {
      portfolioProjectsList.innerHTML = `
        <div class="col-12 text-center py-5">
          <i class="bi bi-briefcase fs-1 text-primary d-block mb-2"></i>
          <h5 class="fw-bold text-white">Your Portfolio is Currently Empty</h5>
          <p class="text-muted small mb-0">Browse 'Recommended Projects' and click 'Save to Portfolio' to start building verifiable showcase proof.</p>
        </div>
      `;
    } else {
      portfolioProjectsList.innerHTML = portfolio.map(p => renderProjectCardHtml(p, true)).join("");
    }

    attachCardEventListeners();
  }

  function renderProjectCardHtml(p, isPortfolio) {
    const diffColor = p.difficulty === "Beginner" ? "success" : (p.difficulty === "Intermediate" ? "warning" : "danger");
    const skillsHtml = (p.skills_addressed || []).map(s =>
      `<span class="badge bg-dark border border-secondary text-info px-2 py-1" style="font-size: 0.75rem;">${s}</span>`
    ).join("");

    let statusBadge = '<span class="badge bg-dark border border-secondary text-light small">Recommended</span>';
    if (p.status === "saved") {
      statusBadge = '<span class="badge bg-info bg-opacity-25 text-info border border-info small">Planning</span>';
    } else if (p.status === "in_progress") {
      statusBadge = '<span class="badge bg-warning bg-opacity-25 text-warning border border-warning small">In Progress</span>';
    } else if (p.status === "completed") {
      statusBadge = '<span class="badge bg-success text-white small"><i class="bi bi-check-circle-fill me-1"></i> Completed & Deployed</span>';
    }

    return `
      <div class="col-lg-6">
        <div class="glass-card project-card h-100 p-4">
          <div class="d-flex align-items-center justify-content-between mb-2 flex-wrap gap-2">
            <span class="badge bg-${diffColor} text-white small">${p.difficulty}</span>
            <div class="d-flex align-items-center gap-2">
              <span class="text-white small"><i class="bi bi-clock me-1 text-primary"></i> ${p.estimated_hours}</span>
              ${statusBadge}
            </div>
          </div>

          <h5 class="fw-bold text-white mb-2">${p.title}</h5>
          <p class="text-white small mb-3" style="line-height: 1.55; font-size: 0.88rem;">${p.problem_statement}</p>

          <div class="mb-3">
            <div class="small fw-bold text-uppercase mb-1" style="color: #cbd5e1; font-size: 0.75rem;">Skills Addressed:</div>
            <div class="d-flex flex-wrap gap-1">${skillsHtml}</div>
          </div>

          ${p.prerequisites ? `
            <div class="small text-light mb-3 p-2 rounded" style="background: rgba(255,255,255,0.03); font-size: 0.78rem;">
              <strong>Prerequisites:</strong> ${p.prerequisites}
            </div>
          ` : ''}

          <!-- Portfolio Links If Added -->
          ${(p.github_url || p.demo_url) ? `
            <div class="p-2 mb-3 rounded bg-dark border border-secondary d-flex flex-wrap gap-2">
              ${p.github_url ? `<a href="${p.github_url}" target="_blank" class="btn btn-outline-custom btn-sm rounded-pill"><i class="bi bi-github me-1"></i> Repository</a>` : ''}
              ${p.demo_url ? `<a href="${p.demo_url}" target="_blank" class="btn btn-success btn-sm rounded-pill"><i class="bi bi-box-arrow-up-right me-1"></i> Live Demo</a>` : ''}
            </div>
          ` : ''}

          <div class="mt-auto pt-3 border-top border-secondary border-opacity-50 d-flex align-items-center justify-content-between flex-wrap gap-2">
            <button class="btn btn-outline-custom btn-sm rounded-pill px-3 view-architecture-btn" data-id="${p.id}">
              <i class="bi bi-diagram-3 me-1"></i> View Architecture Guide
            </button>

            ${!isPortfolio ? `
              <button class="btn btn-primary-gradient btn-sm rounded-pill px-3 save-project-btn" data-id="${p.id}">
                <i class="bi bi-bookmark-plus me-1"></i> Save to Portfolio
              </button>
            ` : `
              <button class="btn btn-outline-custom btn-sm rounded-pill px-3 update-links-btn" data-id="${p.id}">
                <i class="bi bi-pencil me-1"></i> Update Progress & Links
              </button>
            `}
          </div>
        </div>
      </div>
    `;
  }

  function attachCardEventListeners() {
    // 1. View Architecture Guide Modal
    document.querySelectorAll(".view-architecture-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const pId = btn.dataset.id;
        const proj = allProjects.find(p => p.id === pId);
        if (!proj) return;

        selectedModalProject = proj;
        modalProjectTitle.textContent = proj.title;
        modalProjectDifficulty.textContent = `${proj.difficulty} &bull; ${proj.estimated_hours}`;
        modalProjectDifficulty.className = `badge bg-${proj.difficulty === 'Beginner' ? 'success' : (proj.difficulty === 'Intermediate' ? 'warning' : 'danger')} mb-1`;

        const reqsHtml = (proj.functional_requirements || []).map(r => `<li class="small text-white mb-1">${r}</li>`).join("");
        const milestonesHtml = (proj.milestones || []).map(m => `<li class="small text-white mb-2"><i class="bi bi-check2-circle text-primary me-2"></i>${m}</li>`).join("");

        architectureModalBody.innerHTML = `
          <div class="mb-4">
            <h6 class="fw-bold text-primary text-uppercase small"><i class="bi bi-bullseye me-1"></i> Problem Statement & Objectives</h6>
            <p class="text-white small" style="line-height: 1.6;">${proj.problem_statement}</p>
          </div>

          <div class="mb-4">
            <h6 class="fw-bold text-primary text-uppercase small"><i class="bi bi-diagram-2 me-1"></i> Architectural Blueprint</h6>
            <div class="p-3 rounded bg-dark border border-secondary text-white small" style="font-family: monospace; line-height: 1.5;">
              ${proj.architecture_guide}
            </div>
          </div>

          <div class="row g-4 mb-4">
            <div class="col-md-6">
              <h6 class="fw-bold text-primary text-uppercase small"><i class="bi bi-list-task me-1"></i> Functional Requirements</h6>
              <ul class="ps-3 mb-0">${reqsHtml}</ul>
            </div>
            <div class="col-md-6">
              <h6 class="fw-bold text-primary text-uppercase small"><i class="bi bi-calendar-check me-1"></i> Development Milestones</h6>
              <ul class="list-unstyled mb-0">${milestonesHtml}</ul>
            </div>
          </div>

          <div class="row g-4 mb-3">
            <div class="col-md-6">
              <h6 class="fw-bold text-primary text-uppercase small"><i class="bi bi-shield-check me-1"></i> Testing Requirements</h6>
              <p class="text-white small mb-0">${proj.testing_requirements}</p>
            </div>
            <div class="col-md-6">
              <h6 class="fw-bold text-primary text-uppercase small"><i class="bi bi-cloud-arrow-up me-1"></i> Deployment Recommendations</h6>
              <p class="text-white small mb-0">${proj.deployment_suggestions}</p>
            </div>
          </div>

          <div class="p-3 rounded-3" style="background: rgba(99, 102, 241, 0.12); border-left: 4px solid #818cf8;">
            <div class="fw-bold text-white small mb-1"><i class="bi bi-github me-1"></i> Recruiter-Ready Portfolio Guidance:</div>
            <div class="text-white small" style="font-size: 0.85rem;">${proj.github_portfolio_guidance}</div>
          </div>
        `;

        architectureModal.show();
      });
    });

    // 2. Save Project to Portfolio
    document.querySelectorAll(".save-project-btn").forEach(btn => {
      btn.addEventListener("click", async () => {
        const pId = btn.dataset.id;
        await updateProjectStatusOnServer(pId, "saved");
      });
    });

    // 3. Open Update Links Modal
    document.querySelectorAll(".update-links-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const pId = btn.dataset.id;
        const proj = allProjects.find(p => p.id === pId);
        if (!proj) return;

        editProjectId.value = proj.id;
        editProjectStatus.value = proj.status || "saved";
        editProjectGithub.value = proj.github_url || "";
        editProjectDemo.value = proj.demo_url || "";
        editProjectNotes.value = proj.user_notes || "";

        updateLinksModal.show();
      });
    });
  }

  modalSaveProjectBtn?.addEventListener("click", async () => {
    if (selectedModalProject) {
      await updateProjectStatusOnServer(selectedModalProject.id, "saved");
      architectureModal.hide();
    }
  });

  saveProjectLinksBtn?.addEventListener("click", async () => {
    const pId = editProjectId.value;
    const status = editProjectStatus.value;
    const gh = editProjectGithub.value.trim();
    const demo = editProjectDemo.value.trim();
    const notes = editProjectNotes.value.trim();

    try {
      const res = await fetch(`/projects/${pId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${currentToken}`
        },
        body: JSON.stringify({
          status: status,
          github_url: gh,
          demo_url: demo,
          user_notes: notes
        })
      });

      if (res.ok) {
        updateLinksModal.hide();
        showAlert("Project progress and live links updated successfully!", "success");
        await loadProjects(true);
      }
    } catch (e) {
      showAlert("Failed to update project links.", "danger");
    }
  });

  async function updateProjectStatusOnServer(projectId, newStatus) {
    try {
      const res = await fetch(`/projects/${projectId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${currentToken}`
        },
        body: JSON.stringify({ status: newStatus })
      });
      if (res.ok) {
        showAlert(`Project saved to portfolio (${newStatus})!`, "success");
        await loadProjects(true);
      }
    } catch (e) {
      showAlert("Failed to save project.", "danger");
    }
  }

  initAuth();
});

