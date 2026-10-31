/**
 * PATHFORGE AI - Career Path Recommender Client Script
 * Handles authentication, fetching recommendations, target career selection,
 * preferences submission, and catalogue exploration.
 */

document.addEventListener("DOMContentLoaded", () => {
  let currentToken = localStorage.getItem("pathforge_auth_token") || "";
  let supabaseClient = null;
  let activeTargetSlug = null;

  // Initialize Supabase JS client
  if (window.PATHFORGE_CONFIG && window.PATHFORGE_CONFIG.supabaseUrl && window.PATHFORGE_CONFIG.supabaseKey) {
    try {
      supabaseClient = window.supabase.createClient(
        window.PATHFORGE_CONFIG.supabaseUrl,
        window.PATHFORGE_CONFIG.supabaseKey
      );
    } catch (e) {
      console.warn("Could not initialize Supabase JS client:", e);
    }
  }

  // DOM Elements
  const userEmailBadge = document.getElementById("userEmailBadge");
  const userEmailText = document.getElementById("userEmailText");
  const logoutBtn = document.getElementById("logoutBtn");

  const alertBox = document.getElementById("alertBox");
  const alertIcon = document.getElementById("alertIcon");
  const alertMessage = document.getElementById("alertMessage");

  const activeTargetBanner = document.getElementById("activeTargetBanner");
  const activeTargetTitle = document.getElementById("activeTargetTitle");

  const prefRolesInput = document.getElementById("prefRolesInput");
  const prefWorkMode = document.getElementById("prefWorkMode");
  const generateRecsBtn = document.getElementById("generateRecsBtn");
  const recsSpinner = document.getElementById("recsSpinner");

  const loadingPlaceholder = document.getElementById("loadingPlaceholder");
  const recommendationsList = document.getElementById("recommendationsList");
  const catalogueModalBody = document.getElementById("catalogueModalBody");

  // ---------------------------------------------------------------------------
  // Alert Helper
  // ---------------------------------------------------------------------------
  function showAlert(message, type = "info") {
    alertBox.className = `alert alert-${type} mb-4 glass-card border-0 d-block`;
    alertMessage.textContent = message;

    if (type === "danger") {
      alertIcon.className = "bi bi-exclamation-triangle-fill text-danger fs-4";
    } else if (type === "success") {
      alertIcon.className = "bi bi-check-circle-fill text-success fs-4";
    } else if (type === "warning") {
      alertIcon.className = "bi bi-exclamation-circle-fill text-warning fs-4";
    } else {
      alertIcon.className = "bi bi-info-circle-fill text-primary fs-4";
    }

    alertBox.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function hideAlert() {
    alertBox.className = "alert d-none mb-4 glass-card border-0";
  }

  // ---------------------------------------------------------------------------
  // Auth Verification
  // ---------------------------------------------------------------------------
  async function initAuth() {
    let session = null;
    if (supabaseClient) {
      try {
        const { data } = await supabaseClient.auth.getSession();
        session = data ? data.session : null;
      } catch (err) {
        console.warn("Session check error:", err);
      }
    }

    if (session && session.access_token) {
      setAuthenticatedState(session.access_token, session.user.email);
      return;
    }

    if (currentToken) {
      try {
        const payload = JSON.parse(atob(currentToken.split(".")[1]));
        const isExpired = payload.exp && (payload.exp * 1000 < Date.now());
        if (isExpired) {
          localStorage.removeItem("pathforge_auth_token");
          window.location.replace("/");
          return;
        }
        const email = payload.email || "Authenticated User";
        setAuthenticatedState(currentToken, email);
        return;
      } catch (e) {
        localStorage.removeItem("pathforge_auth_token");
        window.location.replace("/");
        return;
      }
    }

    window.location.replace("/");
  }

  function setAuthenticatedState(token, email) {
    currentToken = token;
    localStorage.setItem("pathforge_auth_token", token);
    if (userEmailText) userEmailText.textContent = email;
    if (userEmailBadge) userEmailBadge.classList.remove("d-none");
    if (logoutBtn) logoutBtn.classList.remove("d-none");

    loadActiveTargetCareer();
    loadCareerRecommendations();
    loadCatalogueModal();
  }

  logoutBtn?.addEventListener("click", async () => {
    if (supabaseClient) {
      try { await supabaseClient.auth.signOut(); } catch (e) {}
    }
    localStorage.removeItem("pathforge_auth_token");
    window.location.replace("/");
  });

  // ---------------------------------------------------------------------------
  // 1. Load User's Active Selected Target Career
  // ---------------------------------------------------------------------------
  async function loadActiveTargetCareer() {
    if (!currentToken) return;
    try {
      const res = await fetch("/careers/selected", {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();
      if (res.ok && data.has_selection && data.data) {
        activeTargetSlug = data.data.career_slug;
        activeTargetTitle.textContent = data.data.career_title;
        activeTargetBanner.classList.remove("d-none");
      }
    } catch (e) {
      console.warn("Could not load active target career:", e);
    }
  }

  // ---------------------------------------------------------------------------
  // 2. Load or Generate Recommendations
  // ---------------------------------------------------------------------------
  async function loadCareerRecommendations(forceRefresh = false) {
    if (!currentToken) return;

    if (!forceRefresh) {
      // First check if user already has saved recommendations
      try {
        const res = await fetch("/careers/recommendations", {
          headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const data = await res.json();
        if (res.ok && data.has_recommendations && data.data && data.data.recommendations?.length > 0) {
          renderRecommendations(data.data.recommendations);
          return;
        }
      } catch (e) {
        console.debug("Checking saved recommendations note:", e);
      }
    }

    // Otherwise generate fresh recommendations
    triggerRecommendationGeneration();
  }

  async function triggerRecommendationGeneration() {
    hideAlert();
    loadingPlaceholder.classList.remove("d-none");
    recommendationsList.innerHTML = "";
    generateRecsBtn.disabled = true;
    recsSpinner.classList.remove("d-none");

    const preferredRoles = prefRolesInput.value
      .split(",")
      .map(s => s.trim())
      .filter(s => s.length > 0);

    const payload = {
      preferred_roles: preferredRoles,
      preferred_work_mode: prefWorkMode.value,
      career_goals: `Transition into modern technology roles.`
    };

    try {
      const res = await fetch("/careers/recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${currentToken}`
        },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      loadingPlaceholder.classList.add("d-none");
      generateRecsBtn.disabled = false;
      recsSpinner.classList.add("d-none");

      if (!res.ok) {
        if (res.status === 400 && data.detail?.includes("No resume")) {
          showAlert("Please upload a resume first on the Resume Analyzer page before matching careers.", "warning");
          recommendationsList.innerHTML = `
            <div class="col-12 text-center py-5 glass-card">
              <i class="bi bi-file-earmark-arrow-up fs-1 text-primary d-block mb-3"></i>
              <h4 class="fw-bold text-white">No Resume Uploaded Yet</h4>
              <p class="text-muted mb-4">PATHFORGE needs your resume data to generate personalized career recommendations.</p>
              <a href="/resume-analysis" class="btn btn-primary-gradient rounded-pill px-4 py-2">
                <i class="bi bi-upload me-1"></i> Go to Resume Analyzer
              </a>
            </div>
          `;
          return;
        }
        throw new Error(data.detail || "Failed to generate career recommendations.");
      }

      renderRecommendations(data.recommendations);
      showAlert("Career recommendations generated successfully based on your profile!", "success");

    } catch (err) {
      loadingPlaceholder.classList.add("d-none");
      generateRecsBtn.disabled = false;
      recsSpinner.classList.add("d-none");
      showAlert(err.message, "danger");
    }
  }

  generateRecsBtn?.addEventListener("click", () => {
    triggerRecommendationGeneration();
  });

  // ---------------------------------------------------------------------------
  // 3. Render Top 5 Career Recommendation Cards
  // ---------------------------------------------------------------------------
  function renderRecommendations(recommendations) {
    if (!recommendations || recommendations.length === 0) {
      recommendationsList.innerHTML = '<div class="col-12 text-center py-4 text-muted">No recommendations generated.</div>';
      return;
    }

    recommendationsList.innerHTML = recommendations.map((rec, index) => {
      const isSelected = activeTargetSlug === rec.career_slug;
      const isHigh = rec.compatibility_score >= 75;
      const scoreClass = isHigh ? "match-score-badge high-match" : "match-score-badge";

      const existingSkillsHtml = (rec.existing_skills || []).map(s =>
        `<span class="skill-tag-have"><i class="bi bi-check2"></i> ${s}</span>`
      ).join("") || '<span class="text-dim small">None explicitly recorded</span>';

      const missingSkillsHtml = (rec.missing_skills || []).map(s =>
        `<span class="skill-tag-missing"><i class="bi bi-circle"></i> ${s}</span>`
      ).join("") || '<span class="text-success small"><i class="bi bi-check-all"></i> All core skills present!</span>';

      const nextStepsHtml = (rec.recommended_next_steps || []).map(step =>
        `<li class="mb-2 text-light small d-flex align-items-start gap-2">
          <i class="bi bi-arrow-right-circle text-primary mt-1" style="font-size: 0.85rem;"></i>
          <span>${step}</span>
        </li>`
      ).join("");

      return `
        <div class="col-lg-6">
          <div class="glass-card career-card h-100 p-4 ${isSelected ? 'active-target' : ''}">
            
            <!-- Card Header -->
            <div class="d-flex align-items-start justify-content-between gap-3 mb-3">
              <div>
                <div class="d-flex align-items-center gap-2 mb-1">
                  <span class="badge bg-dark border border-secondary text-light small">${rec.category}</span>
                  <span class="badge bg-primary bg-opacity-25 text-primary border border-primary border-opacity-50 small">
                    <i class="bi bi-graph-up me-1"></i> Demand: ${rec.market_demand || 'High'}
                  </span>
                  ${isSelected ? '<span class="badge bg-success text-white small"><i class="bi bi-check-circle-fill me-1"></i> Selected Target</span>' : ''}
                </div>
                <h4 class="fw-bold text-white mb-1">#${index + 1} ${rec.career_title}</h4>
              </div>
              <div class="text-center">
                <div class="${scoreClass}">
                  ${rec.compatibility_score}%
                </div>
                <div class="text-muted" style="font-size: 0.7rem; margin-top: 2px;">Match Score</div>
              </div>
            </div>

            <!-- Role Description -->
            <p class="text-white small mb-3" style="line-height: 1.6; font-size: 0.92rem;">${rec.description}</p>

            <!-- Why This Matches You (Explainability) -->
            <div class="p-3 mb-3 rounded-3" style="background: rgba(99, 102, 241, 0.12); border-left: 4px solid #818cf8; border-top: 1px solid rgba(129, 140, 248, 0.2); border-right: 1px solid rgba(129, 140, 248, 0.2); border-bottom: 1px solid rgba(129, 140, 248, 0.2);">
              <div class="fw-bold text-primary small mb-1" style="font-size: 0.82rem; letter-spacing: 0.04em;">
                <i class="bi bi-lightbulb-fill me-1"></i> WHY THIS CAREER MATCHES YOUR PROFILE:
              </div>
              <div class="text-white small" style="line-height: 1.55; font-size: 0.88rem;">${rec.why_matched}</div>
            </div>

            <!-- Relevant Existing Skills -->
            <div class="mb-3">
              <div class="small fw-bold text-uppercase mb-2" style="color: #cbd5e1; letter-spacing: 0.05em;">
                <i class="bi bi-check-circle-fill text-success me-1"></i> Relevant Existing Skills You Have:
              </div>
              <div class="d-flex flex-wrap gap-1">
                ${existingSkillsHtml}
              </div>
            </div>

            <!-- Skills to Acquire / Missing -->
            <div class="mb-3">
              <div class="small fw-bold text-uppercase mb-2" style="color: #cbd5e1; letter-spacing: 0.05em;">
                <i class="bi bi-exclamation-circle-fill text-danger me-1"></i> Missing / Unverified Skills:
              </div>
              <div class="d-flex flex-wrap gap-1">
                ${missingSkillsHtml}
              </div>
            </div>

            <!-- Actionable Next Steps -->
            <div class="mb-4">
              <div class="small fw-bold text-uppercase mb-2" style="color: #cbd5e1; letter-spacing: 0.05em;">
                <i class="bi bi-signpost-split-fill text-info me-1"></i> Recommended Next Steps:
              </div>
              <ul class="list-unstyled mb-0">
                ${nextStepsHtml}
              </ul>
            </div>

            <!-- Select Action Button -->
            <div class="mt-auto pt-3 border-top border-secondary border-opacity-50 d-flex align-items-center justify-content-between flex-wrap gap-2">
              <button class="btn ${isSelected ? 'btn-success' : 'btn-outline-custom'} rounded-pill px-4 select-career-btn"
                data-slug="${rec.career_slug}"
                data-title="${rec.career_title}">
                <i class="bi ${isSelected ? 'bi-check2-circle' : 'bi-plus-circle'} me-1"></i>
                ${isSelected ? 'Active Target Career' : 'Select Target Career'}
              </button>
              
              <a href="/skill-gap-analyzer" class="btn btn-outline-custom btn-sm rounded-pill px-3">
                <i class="bi bi-bar-chart-steps me-1"></i> View Skill Gap
              </a>
            </div>

          </div>
        </div>
      `;
    }).join("");

    // Attach Selection Handlers
    document.querySelectorAll(".select-career-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        selectCareer(btn.dataset.slug, btn.dataset.title);
      });
    });
  }

  // ---------------------------------------------------------------------------
  // 4. Select Target Career Action
  // ---------------------------------------------------------------------------
  async function selectCareer(slug, title) {
    if (!currentToken) return;

    try {
      showAlert(`Setting '${title}' as your target career...`, "info");
      const res = await fetch("/careers/select", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${currentToken}`
        },
        body: JSON.stringify({
          career_slug: slug,
          career_title: title,
          career_data: { selected_at: new Date().toISOString() }
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to select career.");

      activeTargetSlug = slug;
      activeTargetTitle.textContent = title;
      activeTargetBanner.classList.remove("d-none");

      showAlert(`'${title}' is now your selected target career! You can now analyze skill gaps.`, "success");
      loadCareerRecommendations(false);

    } catch (err) {
      showAlert(err.message, "danger");
    }
  }

  // ---------------------------------------------------------------------------
  // 5. Populate Catalogue Modal (13 Industry Roles)
  // ---------------------------------------------------------------------------
  async function loadCatalogueModal() {
    try {
      const res = await fetch("/careers/catalogue");
      const data = await res.json();
      if (res.ok && data.data) {
        catalogueModalBody.innerHTML = `
          <div class="row g-4">
            ${data.data.map(role => `
              <div class="col-md-6 col-lg-4">
                <div class="p-3 rounded-3 h-100" style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-subtle);">
                  <div class="badge bg-dark border border-secondary text-light small mb-2">${role.category}</div>
                  <h5 class="fw-bold text-white mb-2">${role.title}</h5>
                  <p class="text-light small mb-3" style="font-size: 0.8rem; line-height: 1.4;">${role.description}</p>
                  
                  <div class="small text-muted fw-semibold mb-1">Required Skills:</div>
                  <div class="d-flex flex-wrap gap-1 mb-3">
                    ${role.required_skills.map(s => `<span class="badge bg-dark text-info border border-secondary px-2 py-1" style="font-size: 0.72rem;">${s}</span>`).join("")}
                  </div>

                  <button class="btn btn-outline-custom btn-sm rounded-pill w-100 select-from-modal-btn"
                    data-slug="${role.slug}"
                    data-title="${role.title}"
                    data-bs-dismiss="modal">
                    <i class="bi bi-check-circle me-1"></i> Choose as Target
                  </button>
                </div>
              </div>
            `).join("")}
          </div>
        `;

        document.querySelectorAll(".select-from-modal-btn").forEach(btn => {
          btn.addEventListener("click", () => {
            selectCareer(btn.dataset.slug, btn.dataset.title);
          });
        });
      }
    } catch (e) {
      console.warn("Could not load catalogue:", e);
    }
  }

  // Initial Auth Check
  initAuth();
});

