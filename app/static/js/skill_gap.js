/**
 * PATHFORGE AI - AI Skill Gap Analyzer Client Script (Feature 3 Corrected)
 * Implements the complete 8-step workflow:
 * Resume selection / upload -> Profile preview & level adjustments -> Target career selection
 * -> Deterministic skill gap comparison -> Comprehensive report with transparent coverage metrics.
 */

document.addEventListener("DOMContentLoaded", () => {
  let currentToken = localStorage.getItem("pathforge_auth_token") || "";
  let supabaseClient = null;
  let catalogue = [];
  let userResumes = [];
  let currentResumeId = null;
  let currentTargetSlug = null;
  let activeOverrides = {};

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

  // Step 1: Resume elements
  const resumeSelect = document.getElementById("resumeSelect");
  const resumeStatusBadge = document.getElementById("resumeStatusBadge");
  const directResumeInput = document.getElementById("directResumeInput");
  const directUploadSpinner = document.getElementById("directUploadSpinner");

  // Step 2: Career elements
  const targetCareerSelect = document.getElementById("targetCareerSelect");
  const selectedRoleTitle = document.getElementById("selectedRoleTitle");
  const selectedRoleDesc = document.getElementById("selectedRoleDesc");
  const runSkillGapBtn = document.getElementById("runSkillGapBtn");
  const gapSpinner = document.getElementById("gapSpinner");
  const gapLoadingPlaceholder = document.getElementById("gapLoadingPlaceholder");

  // Step 3 & 4: Profile Review elements
  const previewCandidateName = document.getElementById("previewCandidateName");
  const previewCandidateEmail = document.getElementById("previewCandidateEmail");
  const previewEducationList = document.getElementById("previewEducationList");
  const previewProjectsList = document.getElementById("previewProjectsList");
  const profileSkillsChipContainer = document.getElementById("profileSkillsChipContainer");
  const saveOverridesBtn = document.getElementById("saveOverridesBtn");
  const addCustomSkillBtn = document.getElementById("addCustomSkillBtn");

  // Step 8: Report elements
  const skillGapReportSection = document.getElementById("skillGapReportSection");
  const overallMatchNumber = document.getElementById("overallMatchNumber");
  const targetCareerBadge = document.getElementById("targetCareerBadge");
  const matchProgressBar = document.getElementById("matchProgressBar");
  const matchVerdictText = document.getElementById("matchVerdictText");
  const downloadReportBtn = document.getElementById("downloadReportBtn");

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
  const categoryBreakdownContainer = document.getElementById("categoryBreakdownContainer");

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
    // 1. Instant auth verification from localStorage (0ms UI render)
    if (currentToken) {
      try {
        const payload = JSON.parse(atob(currentToken.split(".")[1]));
        const isExpired = payload.exp && (payload.exp * 1000 < Date.now());
        if (!isExpired) {
          const email = payload.email || "Authenticated User";
          setAuthenticatedState(currentToken, email);
          
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

    // 2. Fallback to Supabase getSession if localStorage token was missing
    if (supabaseClient) {
      try {
        const { data } = await supabaseClient.auth.getSession();
        if (data && data.session && data.session.access_token) {
          setAuthenticatedState(data.session.access_token, data.session.user.email);
          return;
        }
      } catch (err) {
        console.warn("Session check error:", err);
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
  // Complete Workflow Initialization
  // ---------------------------------------------------------------------------
  async function initializeSkillGapWorkflow() {
    await loadCatalogue();
    await loadUserResumes();
    await loadUserSelectedCareer();
  }

  // 1. Load Career Catalogue
  async function loadCatalogue() {
    try {
      const res = await fetch("/careers/catalogue");
      const data = await res.json();
      if (res.ok && data.data) {
        catalogue = data.data;
        targetCareerSelect.innerHTML = catalogue.map(role =>
          `<option value="${role.slug}">${role.title} (${role.category})</option>`
        ).join("");

        updateCareerDetailsPreview(targetCareerSelect.value);
      }
    } catch (e) {
      console.warn("Could not load career catalogue:", e);
    }
  }

  targetCareerSelect?.addEventListener("change", () => {
    updateCareerDetailsPreview(targetCareerSelect.value);
  });

  function updateCareerDetailsPreview(slug) {
    const role = catalogue.find(r => r.slug === slug);
    if (role) {
      selectedRoleTitle.textContent = `${role.title} (${role.category})`;
      selectedRoleDesc.textContent = role.description;
    }
  }

  // 2. Load User's Analyzed Resumes History
  async function loadUserResumes() {
    if (!currentToken) return;

    try {
      const res = await fetch("/resumes", {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();

      if (res.ok && Array.isArray(data) && data.length > 0) {
        userResumes = data;
        resumeStatusBadge.textContent = `${userResumes.length} Resume(s) Found`;
        resumeStatusBadge.className = "badge bg-success text-white small";

        resumeSelect.innerHTML = userResumes.map(r => {
          const dt = r.created_at ? new Date(r.created_at).toLocaleDateString() : "";
          return `<option value="${r.id}">${r.file_name} (${dt})</option>`;
        }).join("");

        currentResumeId = userResumes[0].id;
        loadProfilePreview(currentResumeId);
      } else {
        resumeStatusBadge.textContent = "No Resume Yet";
        resumeStatusBadge.className = "badge bg-warning text-dark small";
        resumeSelect.innerHTML = '<option value="" disabled selected>No resume uploaded yet. Please upload above.</option>';
        showAlert("Please upload your resume to start the Skill Gap Analysis.", "warning");
      }
    } catch (e) {
      console.warn("Could not fetch user resumes:", e);
    }
  }

  resumeSelect?.addEventListener("change", () => {
    currentResumeId = resumeSelect.value;
    loadProfilePreview(currentResumeId);
  });

  // Direct Resume Upload Handler (Step 2 Upload alternative)
  directResumeInput?.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    hideAlert();
    directUploadSpinner.classList.remove("d-none");
    showAlert(`Uploading and analyzing ${file.name}...`, "info");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/resumes/upload", {
        method: "POST",
        headers: { "Authorization": `Bearer ${currentToken}` },
        body: formData
      });

      directUploadSpinner.classList.add("d-none");
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Failed to process resume file.");
      }

      showAlert(`Resume '${file.name}' processed and verified successfully!`, "success");
      await loadUserResumes();
      if (data.resume?.id) {
        currentResumeId = data.resume.id;
        resumeSelect.value = currentResumeId;
        loadProfilePreview(currentResumeId);
      }
    } catch (err) {
      directUploadSpinner.classList.add("d-none");
      showAlert(err.message, "danger");
    }
  });

  // 3. Load Candidate Extracted Profile Preview (Step 4)
  async function loadProfilePreview(resumeId) {
    if (!currentToken) return;

    try {
      const url = resumeId ? `/skills/preview-profile?resume_id=${resumeId}` : `/skills/preview-profile`;
      const res = await fetch(url, {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();

      if (res.ok && data.has_resume) {
        previewCandidateName.textContent = data.candidate_name || "Verified Candidate";
        previewCandidateEmail.textContent = data.email || "";

        // Education
        const edu = data.education || [];
        if (edu.length > 0) {
          previewEducationList.innerHTML = edu.map(e => `<div><strong>${e.degree || 'Degree'}</strong>, ${e.institution || 'University'} (${e.graduation_year || ''})</div>`).join("");
        } else {
          previewEducationList.textContent = "None explicitly documented in resume.";
        }

        // Projects & Experience
        const projs = data.projects || [];
        const exp = data.work_experience || [];
        let summaryList = [];
        if (exp.length > 0) summaryList.push(`${exp.length} Work Experience position(s)`);
        if (projs.length > 0) summaryList.push(`${projs.length} Practical Project(s)`);
        previewProjectsList.innerHTML = summaryList.length > 0 ? summaryList.join(" &bull; ") : "No explicit items found.";

        // Skill Chips with Level Selector (1-4)
        activeOverrides = data.overrides || {};
        renderSkillsReviewChips(data.profile_skills || []);
      }
    } catch (e) {
      console.warn("Could not preview profile:", e);
    }
  }

  function renderSkillsReviewChips(skills) {
    if (!skills || skills.length === 0) {
      profileSkillsChipContainer.innerHTML = '<span class="text-muted small">No technical skills detected yet in this resume. Click "+ Add Missing Skill" to add your skills.</span>';
      return;
    }

    const levelNames = { 1: "1: Beg", 2: "2: Int", 3: "3: Adv", 4: "4: Exp" };

    profileSkillsChipContainer.innerHTML = skills.map(s => {
      const currentLevel = activeOverrides[s.name] || s.level || 1;
      return `
        <div class="skill-level-chip">
          <span class="text-dark small fw-bold">${s.name}</span>
          <select class="skill-level-select" data-skill="${s.name}">
            <option value="1" ${currentLevel === 1 ? 'selected' : ''}>${levelNames[1]}</option>
            <option value="2" ${currentLevel === 2 ? 'selected' : ''}>${levelNames[2]}</option>
            <option value="3" ${currentLevel === 3 ? 'selected' : ''}>${levelNames[3]}</option>
            <option value="4" ${currentLevel === 4 ? 'selected' : ''}>${levelNames[4]}</option>
          </select>
        </div>
      `;
    }).join("");

    // Attach level change listeners
    document.querySelectorAll(".skill-level-select").forEach(sel => {
      sel.addEventListener("change", (e) => {
        const skill = e.target.dataset.skill;
        const lvl = parseInt(e.target.value);
        activeOverrides[skill] = lvl;
      });
    });
  }

  // Save Overrides Action with double-click prevention
  saveOverridesBtn?.addEventListener("click", async () => {
    if (!currentToken) return;
    saveOverridesBtn.disabled = true;
    saveOverridesBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span> Saving...';
    try {
      const res = await fetch("/skills/override", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${currentToken}`
        },
        body: JSON.stringify(activeOverrides)
      });
      if (res.ok) {
        showAlert("Skill level self-assessments saved successfully!", "success");
      }
    } catch (e) {
      showAlert("Failed to save skill level adjustments.", "danger");
    } finally {
      saveOverridesBtn.disabled = false;
      saveOverridesBtn.innerHTML = '<i class="bi bi-save me-1"></i> Save Level Adjustments';
    }
  });

  // Add Custom Skill Action
  addCustomSkillBtn?.addEventListener("click", () => {
    const newSkill = prompt("Enter the skill name to add to your profile:");
    if (!newSkill || !newSkill.trim()) return;

    const trimmed = newSkill.trim();
    activeOverrides[trimmed] = 2; // Default Intermediate
    // Re-render
    showAlert(`Added '${trimmed}' (Level 2: Intermediate). Click 'Save Level Adjustments' to preserve.`, "info");
    const currentChips = Array.from(document.querySelectorAll(".skill-level-select")).map(sel => ({
      name: sel.dataset.skill,
      level: parseInt(sel.value)
    }));
    currentChips.push({ name: trimmed, level: 2 });
    renderSkillsReviewChips(currentChips);
  });

  // 4. Load User Selected Target Career (from Feature 2)
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
        updateCareerDetailsPreview(currentTargetSlug);
      }
    } catch (e) {
      console.warn("Could not load user selection:", e);
    }
  }

  // 5. Execute Deterministic Skill Gap Analysis (Step 6 & 7)
  runSkillGapBtn?.addEventListener("click", () => {
    const selectedSlug = targetCareerSelect.value;
    if (!selectedSlug) {
      showAlert("Please choose a target career to analyze against.", "warning");
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

    const payload = {
      career_slug: careerSlug,
      resume_id: currentResumeId || null,
      user_skill_overrides: activeOverrides
    };

    try {
      const res = await fetch("/skills/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${currentToken}`
        },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      gapLoadingPlaceholder.classList.add("d-none");
      runSkillGapBtn.disabled = false;
      gapSpinner.classList.add("d-none");

      if (!res.ok) {
        throw new Error(data.detail || "Skill gap analysis failed.");
      }

      renderSkillGapReport(data.data);
      showAlert(`Skill gap report for ${data.data.target_career} computed successfully!`, "success");

    } catch (err) {
      gapLoadingPlaceholder.classList.add("d-none");
      runSkillGapBtn.disabled = false;
      gapSpinner.classList.add("d-none");
      showAlert(err.message, "danger");
    }
  }

  // 6. Render Comprehensive Skill Gap Report Dashboard (Step 8)
  function renderSkillGapReport(report) {
    skillGapReportSection.classList.remove("d-none");
    skillGapReportSection.scrollIntoView({ behavior: "smooth" });

    // Download button link
    downloadReportBtn.href = `/skills/download?career_slug=${report.career_slug}`;

    // Score & Badges
    const coveragePct = report.coverage_percentage || 0;
    overallMatchNumber.textContent = `${Math.round(coveragePct)}%`;
    matchProgressBar.style.width = `${coveragePct}%`;
    targetCareerBadge.textContent = `${report.target_career} (${report.category})`;

    if (coveragePct >= 65) {
      matchVerdictText.textContent = "High Skill Alignment: Minor specific depth bridges needed.";
    } else if (coveragePct >= 35) {
      matchVerdictText.textContent = "Moderate Skill Alignment: Clear actionable path to production competency.";
    } else {
      matchVerdictText.textContent = "Foundational Stage: Comprehensive sequential learning roadmap recommended.";
    }

    // Counts
    const matched = report.matched_skills || [];
    const improve = report.improvement_skills || [];
    const missing = report.missing_skills || [];

    countSkillsHave.textContent = matched.length;
    countSkillsImprove.textContent = improve.length;
    countSkillsMissing.textContent = missing.length;

    badgeHaveCount.textContent = matched.length;
    badgeImproveCount.textContent = improve.length;
    badgeMissingCount.textContent = missing.length;

    // Mentor Advice
    if (report.mentor_advice) {
      mentorAdviceText.textContent = report.mentor_advice;
      mentorAdviceCard.classList.remove("d-none");
    } else {
      mentorAdviceCard.classList.add("d-none");
    }

    // A. Matched Skills (Green)
    if (matched.length > 0) {
      skillsHaveList.innerHTML = matched.map(item => `
        <div class="p-3 rounded-3" style="background: rgba(16, 185, 129, 0.14); border: 1.5px solid rgba(52, 211, 153, 0.55);">
          <div class="d-flex align-items-center justify-content-between mb-1">
            <span class="fw-bold text-dark fs-6">${item.name}</span>
            <span class="badge bg-success text-white small" style="font-size: 0.72rem;">
              <i class="bi bi-check-circle-fill me-1"></i> Meets Req (${item.current_level_name})
            </span>
          </div>
          <div class="text-muted small" style="font-size: 0.82rem; line-height: 1.4;">${item.evidence}</div>
        </div>
      `).join("");
    } else {
      skillsHaveList.innerHTML = '<div style="color: #94a3b8;" class="small py-2">No matching skills identified at required proficiency level.</div>';
    }

    // B. Skills to Improve (Amber)
    if (improve.length > 0) {
      skillsImproveList.innerHTML = improve.map(item => `
        <div class="p-3 rounded-3" style="background: rgba(245, 158, 11, 0.14); border: 1.5px solid rgba(251, 191, 36, 0.55);">
          <div class="d-flex align-items-center justify-content-between mb-1">
            <span class="fw-bold text-dark fs-6">${item.name}</span>
            <span class="badge ${item.priority === 'High' ? 'bg-danger text-white' : 'bg-warning text-dark'} small" style="font-size: 0.72rem;">
              ${item.priority} Priority &bull; Gap: +${item.gap}
            </span>
          </div>
          <div class="small mb-1 text-muted">Current: <strong>${item.current_level_name}</strong> &rarr; Target: <strong>${item.required_level_name}</strong></div>
          <div class="text-muted mb-2" style="font-size: 0.84rem; line-height: 1.4;">${item.why_matters}</div>
          <div class="small fw-semibold text-warning" style="font-size: 0.78rem;"><strong>Action:</strong> ${item.action}</div>
        </div>
      `).join("");
    } else {
      skillsImproveList.innerHTML = '<div style="color: #94a3b8;" class="small py-2">No secondary improvement skills flagged.</div>';
    }

    // C. Missing / Not Found in Profile (Rose)
    if (missing.length > 0) {
      skillsMissingList.innerHTML = missing.map(item => `
        <div class="p-3 rounded-3" style="background: rgba(239, 68, 68, 0.14); border: 1.5px solid rgba(248, 113, 113, 0.55);">
          <div class="d-flex align-items-center justify-content-between mb-1">
            <span class="fw-bold text-dark fs-6">${item.name}</span>
            <span class="badge ${item.priority === 'High' ? 'bg-danger text-white' : 'bg-secondary text-white'} small" style="font-size: 0.72rem;">
              ${item.priority} Priority &bull; Target: ${item.required_level_name}
            </span>
          </div>
          <div class="badge bg-light border text-danger small mb-2" style="font-size: 0.72rem;">Unverified in profile</div>
          <div class="text-muted mb-2" style="font-size: 0.84rem; line-height: 1.4;">${item.why_matters}</div>
          <div class="small fw-semibold text-danger" style="font-size: 0.78rem;"><strong>Roadmap:</strong> ${item.action}</div>
        </div>
      `).join("");
    } else {
      skillsMissingList.innerHTML = '<div class="text-success small py-2"><i class="bi bi-check-all"></i> All required skills are documented in profile!</div>';
    }

    // Priority Gaps Table
    const priorityGaps = report.priority_gaps || [];
    if (priorityGaps.length > 0) {
      priorityGapsTableBody.innerHTML = priorityGaps.map(gap => {
        let priorityBadge = '<span class="badge bg-danger text-white">High</span>';
        if (gap.priority === "Medium") {
          priorityBadge = '<span class="badge bg-warning text-dark">Medium</span>';
        } else if (gap.priority === "Low") {
          priorityBadge = '<span class="badge bg-info text-dark">Low</span>';
        }

        return `
          <tr>
            <td class="fw-bold text-dark fs-6">${gap.skill}</td>
            <td><span class="badge bg-light border text-muted small">${gap.category}</span></td>
            <td>${priorityBadge}</td>
            <td class="text-dark small">${gap.current_level}</td>
            <td class="text-primary fw-semibold small">${gap.required_level}</td>
            <td><span class="badge bg-light border text-muted small">${gap.status}</span></td>
            <td class="text-muted small" style="font-size: 0.85rem;">${gap.action}</td>
          </tr>
        `;
      }).join("");
    } else {
      priorityGapsTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-3 text-muted">No priority skill gaps identified.</td></tr>';
    }

    // Category Breakdown Radar/Cards
    const categories = report.category_breakdown || {};
    categoryBreakdownContainer.innerHTML = Object.entries(categories).map(([catName, stats]) => {
      const catTotal = stats.total || 1;
      const catMatched = stats.matched || 0;
      const pct = Math.round((catMatched / catTotal) * 100);

      return `
        <div class="col-md-6 col-lg-3">
          <div class="p-3 rounded-3 h-100 bg-white border shadow-xs">
            <div class="fw-semibold text-dark small mb-1">${catName}</div>
            <div class="d-flex align-items-center justify-content-between mb-2">
              <span class="fs-5 fw-bold text-primary">${pct}%</span>
              <span class="text-muted small">${catMatched} / ${catTotal} Met</span>
            </div>
            <div class="progress bg-light" style="height: 6px; border-radius: 9999px;">
              <div class="progress-bar bg-primary" style="width: ${pct}%"></div>
            </div>
          </div>
        </div>
      `;
    }).join("");
  }

  // Initial Auth Check
  initAuth();
});
