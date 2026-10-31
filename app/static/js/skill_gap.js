/**
 * PATHFORGE AI - AI Skill Gap Analyzer Client Script
 * Handles target career selection, comparing profile skills, rendering
 * the 3-category classification dashboard, prioritized gap table, and project suggestions.
 */

document.addEventListener("DOMContentLoaded", () => {
  let currentToken = localStorage.getItem("pathforge_auth_token") || "";
  let supabaseClient = null;
  let catalogue = [];
  let currentTargetSlug = null;

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

  const targetCareerSelect = document.getElementById("targetCareerSelect");
  const runSkillGapBtn = document.getElementById("runSkillGapBtn");
  const gapSpinner = document.getElementById("gapSpinner");
  const gapLoadingPlaceholder = document.getElementById("gapLoadingPlaceholder");

  const skillGapReportSection = document.getElementById("skillGapReportSection");
  const overallMatchNumber = document.getElementById("overallMatchNumber");
  const targetCareerBadge = document.getElementById("targetCareerBadge");
  const matchProgressBar = document.getElementById("matchProgressBar");
  const matchVerdictText = document.getElementById("matchVerdictText");

  const countSkillsHave = document.getElementById("countSkillsHave");
  const countSkillsImprove = document.getElementById("countSkillsImprove");
  const countSkillsMissing = document.getElementById("countSkillsMissing");

  const badgeHaveCount = document.getElementById("badgeHaveCount");
  const badgeImproveCount = document.getElementById("badgeImproveCount");
  const badgeMissingCount = document.getElementById("badgeMissingCount");

  const skillsHaveList = document.getElementById("skillsHaveList");
  const skillsImproveList = document.getElementById("skillsImproveList");
  const skillsMissingList = document.getElementById("skillsMissingList");

  const mentorAdviceCard = document.getElementById("mentorAdviceCard");
  const mentorAdviceText = document.getElementById("mentorAdviceText");

  const priorityGapsTableBody = document.getElementById("priorityGapsTableBody");
  const learningRoadmapContainer = document.getElementById("learningRoadmapContainer");
  const recommendedProjectsContainer = document.getElementById("recommendedProjectsContainer");

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

    initializeSkillGapWorkflow();
  }

  logoutBtn?.addEventListener("click", async () => {
    if (supabaseClient) {
      try { await supabaseClient.auth.signOut(); } catch (e) {}
    }
    localStorage.removeItem("pathforge_auth_token");
    window.location.replace("/");
  });

  // ---------------------------------------------------------------------------
  // Workflow Initialization
  // ---------------------------------------------------------------------------
  async function initializeSkillGapWorkflow() {
    await loadCatalogue();
    await loadUserSelectedCareer();
  }

  async function loadCatalogue() {
    try {
      const res = await fetch("/careers/catalogue");
      const data = await res.json();
      if (res.ok && data.data) {
        catalogue = data.data;
        targetCareerSelect.innerHTML = catalogue.map(role =>
          `<option value="${role.slug}">${role.title} (${role.category})</option>`
        ).join("");
      }
    } catch (e) {
      console.warn("Could not load career catalogue:", e);
    }
  }

  async function loadUserSelectedCareer() {
    if (!currentToken) return;

    try {
      const res = await fetch("/careers/selected", {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();

      if (res.ok && data.has_selection && data.data) {
        currentTargetSlug = data.data.career_slug;
        targetCareerSelect.value = currentTargetSlug;
        // Automatically run or fetch analysis
        executeSkillGapAnalysis(currentTargetSlug);
      } else {
        // Fallback default: select first role or prompt user
        if (catalogue.length > 0) {
          targetCareerSelect.value = catalogue[0].slug;
          showAlert("No target career selected yet. You can pick any career below or select one from the Career Recommender.", "info");
        }
      }
    } catch (e) {
      console.warn("Could not load user selection:", e);
    }
  }

  // ---------------------------------------------------------------------------
  // Run Skill Gap Analysis
  // ---------------------------------------------------------------------------
  runSkillGapBtn?.addEventListener("click", () => {
    const selectedSlug = targetCareerSelect.value;
    if (!selectedSlug) {
      showAlert("Please choose a target career to analyze.", "warning");
      return;
    }
    executeSkillGapAnalysis(selectedSlug);
  });

  async function executeSkillGapAnalysis(careerSlug) {
    hideAlert();
    skillGapReportSection.classList.add("d-none");
    gapLoadingPlaceholder.classList.remove("d-none");
    runSkillGapBtn.disabled = true;
    gapSpinner.classList.remove("d-none");

    try {
      const res = await fetch("/skills/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${currentToken}`
        },
        body: JSON.stringify({ career_slug: careerSlug })
      });

      const data = await res.json();
      gapLoadingPlaceholder.classList.add("d-none");
      runSkillGapBtn.disabled = false;
      gapSpinner.classList.add("d-none");

      if (!res.ok) {
        if (res.status === 400 && data.detail?.includes("No resume")) {
          showAlert("Please upload a resume first on the Resume Analyzer page before running skill gap analysis.", "warning");
          return;
        }
        throw new Error(data.detail || "Skill gap analysis failed.");
      }

      renderSkillGapReport(data.data);
      showAlert(`Skill gap report for ${data.data.career_title} generated successfully!`, "success");

    } catch (err) {
      gapLoadingPlaceholder.classList.add("d-none");
      runSkillGapBtn.disabled = false;
      gapSpinner.classList.add("d-none");
      showAlert(err.message, "danger");
    }
  }

  // ---------------------------------------------------------------------------
  // Render Skill Gap Dashboard
  // ---------------------------------------------------------------------------
  function renderSkillGapReport(report) {
    skillGapReportSection.classList.remove("d-none");
    skillGapReportSection.scrollIntoView({ behavior: "smooth" });

    // Overall Score
    const matchPct = report.overall_match_percentage || 0;
    overallMatchNumber.textContent = `${Math.round(matchPct)}%`;
    matchProgressBar.style.width = `${matchPct}%`;
    targetCareerBadge.textContent = report.career_title;

    if (matchPct >= 75) {
      matchVerdictText.textContent = "High Compatibility: Minor specific bridges needed.";
    } else if (matchPct >= 50) {
      matchVerdictText.textContent = "Moderate Compatibility: Clear path to role readiness.";
    } else {
      matchVerdictText.textContent = "Foundational Stage: Comprehensive learning plan recommended.";
    }

    // Counts
    const have = report.skills_have || [];
    const improve = report.skills_improve || [];
    const missing = report.skills_missing || [];

    countSkillsHave.textContent = have.length;
    countSkillsImprove.textContent = improve.length;
    countSkillsMissing.textContent = missing.length;

    badgeHaveCount.textContent = have.length;
    badgeImproveCount.textContent = improve.length;
    badgeMissingCount.textContent = missing.length;

    // Mentor Advice
    if (report.mentor_advice) {
      mentorAdviceText.textContent = report.mentor_advice;
      mentorAdviceCard.classList.remove("d-none");
    } else {
      mentorAdviceCard.classList.add("d-none");
    }

    // A. Skills You Have
    if (have.length > 0) {
      skillsHaveList.innerHTML = have.map(item => `
        <div class="p-3 rounded-3" style="background: rgba(16, 185, 129, 0.15); border: 1.5px solid rgba(52, 211, 153, 0.55);">
          <div class="d-flex align-items-center justify-content-between mb-1">
            <span class="fw-bold text-white fs-6">${item.skill}</span>
            <span class="badge bg-success text-white small" style="font-size: 0.72rem;"><i class="bi bi-check-circle-fill me-1"></i> Verified</span>
          </div>
          <div class="text-white small" style="font-size: 0.82rem; opacity: 0.95;">${item.evidence}</div>
        </div>
      `).join("");
    } else {
      skillsHaveList.innerHTML = '<div style="color: #94a3b8;" class="small py-2">No matching skills identified for this role in resume.</div>';
    }

    // B. Skills to Improve
    if (improve.length > 0) {
      skillsImproveList.innerHTML = improve.map(item => `
        <div class="p-3 rounded-3" style="background: rgba(245, 158, 11, 0.15); border: 1.5px solid rgba(251, 191, 36, 0.55);">
          <div class="d-flex align-items-center justify-content-between mb-1">
            <span class="fw-bold text-white fs-6">${item.skill}</span>
            <span class="badge ${item.priority === 'High' ? 'bg-danger text-white' : 'bg-warning text-dark'} small" style="font-size: 0.72rem;">${item.priority} Priority</span>
          </div>
          <div class="text-white mb-2" style="font-size: 0.85rem; line-height: 1.4;">${item.why_matters}</div>
          <div class="small fw-semibold" style="color: #fef08a; font-size: 0.78rem;"><strong>Action:</strong> ${item.learning_direction}</div>
        </div>
      `).join("");
    } else {
      skillsImproveList.innerHTML = '<div style="color: #94a3b8;" class="small py-2">No secondary improvement skills flagged.</div>';
    }

    // C. Missing or Not Found in Profile
    if (missing.length > 0) {
      skillsMissingList.innerHTML = missing.map(item => `
        <div class="p-3 rounded-3" style="background: rgba(239, 68, 68, 0.14); border: 1.5px solid rgba(248, 113, 113, 0.55);">
          <div class="d-flex align-items-center justify-content-between mb-1">
            <span class="fw-bold text-white fs-6">${item.skill}</span>
            <span class="badge ${item.priority === 'High' ? 'bg-danger text-white' : 'bg-secondary text-white'} small" style="font-size: 0.72rem;">${item.priority} Priority</span>
          </div>
          <div class="badge bg-dark border border-secondary text-white small mb-2" style="font-size: 0.72rem;">Not found in profile</div>
          <div class="text-white mb-2" style="font-size: 0.85rem; line-height: 1.4;">${item.why_matters}</div>
          <div class="small fw-semibold" style="color: #fecdd3; font-size: 0.78rem;"><strong>Roadmap:</strong> ${item.learning_direction}</div>
        </div>
      `).join("");
    } else {
      skillsMissingList.innerHTML = '<div class="text-success small py-2"><i class="bi bi-check-all"></i> All required skills are documented!</div>';
    }

    // D. Priority Gaps Table
    const priorityGaps = report.priority_gaps || [];
    if (priorityGaps.length > 0) {
      priorityGapsTableBody.innerHTML = priorityGaps.map(gap => {
        let priorityBadge = '<span class="badge bg-danger text-white border border-danger">High</span>';
        if (gap.priority === "Medium") {
          priorityBadge = '<span class="badge bg-warning text-dark border border-warning">Medium</span>';
        } else if (gap.priority === "Low") {
          priorityBadge = '<span class="badge bg-info text-dark border border-info">Low</span>';
        }

        return `
          <tr>
            <td class="fw-bold text-white fs-6">${gap.skill}</td>
            <td>${priorityBadge}</td>
            <td><span class="badge bg-dark border border-secondary text-white small">${gap.status}</span></td>
            <td class="text-white small" style="font-size: 0.88rem;">${gap.why_matters}</td>
            <td class="text-white small fw-medium" style="color: #cbd5e1 !important; font-size: 0.88rem;">${gap.action}</td>
          </tr>
        `;
      }).join("");
    } else {
      priorityGapsTableBody.innerHTML = '<tr><td colspan="5" class="text-center py-3 text-white">No high-priority skill gaps identified.</td></tr>';
    }

    // E. Phased Learning Roadmap
    const roadmap = report.learning_path || [];
    learningRoadmapContainer.innerHTML = roadmap.map(phase => `
      <div class="col-md-4">
        <div class="roadmap-phase-card h-100">
          <div class="small fw-bold text-uppercase mb-1" style="color: #818cf8; letter-spacing: 0.05em;">${phase.phase}</div>
          <h5 class="fw-bold text-white mb-2">${phase.goal}</h5>
          <div class="d-flex flex-wrap gap-1 mb-2">
            ${(phase.skills || []).map(s => `<span class="badge bg-dark border border-secondary text-white px-2 py-1" style="font-size: 0.78rem;">${s}</span>`).join("")}
          </div>
          <p class="text-white small mb-0" style="font-size: 0.85rem; line-height: 1.5;">${phase.action}</p>
        </div>
      </div>
    `).join("");

    // F. Recommended Portfolio Projects
    const projects = report.recommended_projects || [];
    recommendedProjectsContainer.innerHTML = projects.map(proj => `
      <div class="col-md-6">
        <div class="p-4 rounded-3 h-100" style="background: rgba(255, 255, 255, 0.05); border: 1.5px solid rgba(148, 163, 184, 0.25);">
          <div class="d-flex align-items-center justify-content-between mb-2">
            <span class="badge bg-primary bg-opacity-25 text-white border border-primary small fw-semibold">${proj.difficulty || 'Intermediate'}</span>
            <span class="text-white small"><i class="bi bi-clock me-1 text-primary"></i> ${proj.estimated_hours || '20-30 hours'}</span>
          </div>
          <h5 class="fw-bold text-white mb-2">${proj.title}</h5>
          <p class="text-white small mb-3" style="line-height: 1.6; font-size: 0.9rem;">${proj.description}</p>
          
          <div class="small fw-bold text-uppercase mb-1" style="color: #cbd5e1;">Key Technologies Applied:</div>
          <div class="d-flex flex-wrap gap-1 mb-3">
            ${(proj.skills_applied || []).map(t => `<span class="skill-badge py-1 px-2" style="font-size: 0.78rem;">${t}</span>`).join("")}
          </div>

          <div class="p-3 rounded bg-dark border border-secondary text-white small" style="font-size: 0.85rem;">
            <i class="bi bi-trophy-fill text-warning me-1"></i> <strong>Showcase Outcome:</strong> ${proj.outcome}
          </div>
        </div>
      </div>
    `).join("");
  }

  // Initial Auth Check
  initAuth();
});

