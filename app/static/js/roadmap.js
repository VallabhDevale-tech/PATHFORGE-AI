/**
 * PATHFORGE AI - Personalized Learning Roadmap Client Script (Feature 4)
 * Handles roadmap generation from skill gap results, week-wise curriculum rendering,
 * real-time activity status toggling, and completion progress metrics.
 */

document.addEventListener("DOMContentLoaded", () => {
  let currentToken = localStorage.getItem("pathforge_auth_token") || "";
  let supabaseClient = null;
  let activeRoadmap = null;
  let activeFilter = "all";
  let activeCareerSlug = null;

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

  const targetCareerDisplay = document.getElementById("targetCareerDisplay");
  const roadmapDurationSelect = document.getElementById("roadmapDurationSelect");
  const studyHoursSelect = document.getElementById("studyHoursSelect");
  const generateRoadmapBtn = document.getElementById("generateRoadmapBtn");
  const roadmapSpinner = document.getElementById("roadmapSpinner");

  const roadmapDashboardSection = document.getElementById("roadmapDashboardSection");
  const roadmapEmptyState = document.getElementById("roadmapEmptyState");
  const roadmapProgressPct = document.getElementById("roadmapProgressPct");
  const roadmapProgressBar = document.getElementById("roadmapProgressBar");
  const activityCountLabel = document.getElementById("activityCountLabel");
  const pedagogicalOverviewText = document.getElementById("pedagogicalOverviewText");
  const roadmapWeeksContainer = document.getElementById("roadmapWeeksContainer");

  function showAlert(message, type = "info") {
    alertBox.className = `alert alert-${type} mb-4 glass-card border-0 d-block`;
    alertMessage.textContent = message;
    alertIcon.className = type === "danger" ? "bi bi-exclamation-triangle-fill text-danger fs-4" : "bi bi-check-circle-fill text-success fs-4";
  }

  function hideAlert() {
    alertBox.className = "alert d-none mb-4 glass-card border-0";
  }

  async function initAuth() {
    let session = null;
    if (supabaseClient) {
      try {
        const { data } = await supabaseClient.auth.getSession();
        session = data ? data.session : null;
      } catch (err) {}
    }

    if (session && session.access_token) {
      setAuthenticatedState(session.access_token, session.user.email);
      return;
    }

    if (currentToken) {
      try {
        const payload = JSON.parse(atob(currentToken.split(".")[1]));
        if (!payload.exp || (payload.exp * 1000 > Date.now())) {
          setAuthenticatedState(currentToken, payload.email || "Authenticated User");
          return;
        }
      } catch (e) {}
    }
    window.location.replace("/");
  }

  function setAuthenticatedState(token, email) {
    currentToken = token;
    localStorage.setItem("pathforge_auth_token", token);
    if (userEmailText) userEmailText.textContent = email;
    loadActiveTargetAndRoadmap();
  }

  logoutBtn?.addEventListener("click", async () => {
    if (supabaseClient) try { await supabaseClient.auth.signOut(); } catch (e) {}
    localStorage.removeItem("pathforge_auth_token");
    window.location.replace("/");
  });

  async function loadActiveTargetAndRoadmap() {
    // 1. Get active selected career
    try {
      const res = await fetch("/careers/selected", {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();
      if (res.ok && data.has_selection && data.data) {
        activeCareerSlug = data.data.career_slug;
        targetCareerDisplay.value = data.data.career_title;
      } else {
        // Fallback to skill gap report
        const repRes = await fetch("/skills/report", {
          headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const repData = await repRes.json();
        if (repRes.ok && repData.has_report) {
          activeCareerSlug = repData.data.career_slug;
          targetCareerDisplay.value = repData.data.target_career;
        } else {
          targetCareerDisplay.value = "Software Developer (Default)";
          activeCareerSlug = "software-developer";
        }
      }
    } catch (e) {
      targetCareerDisplay.value = "Software Developer";
      activeCareerSlug = "software-developer";
    }

    // 2. Fetch current roadmap
    try {
      const res = await fetch(`/roadmap/current?career_slug=${activeCareerSlug}`, {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();
      if (res.ok && data.has_roadmap && data.data) {
        activeRoadmap = data.data;
        renderRoadmap(activeRoadmap);
      }
    } catch (e) {
      console.warn("Could not load current roadmap:", e);
    }
  }

  // Generate Roadmap Action
  generateRoadmapBtn?.addEventListener("click", async () => {
    hideAlert();
    generateRoadmapBtn.disabled = true;
    roadmapSpinner.classList.remove("d-none");

    const payload = {
      career_slug: activeCareerSlug,
      duration_weeks: parseInt(roadmapDurationSelect.value),
      hours_per_week: parseInt(studyHoursSelect.value)
    };

    try {
      const res = await fetch("/roadmap/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${currentToken}`
        },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      generateRoadmapBtn.disabled = false;
      roadmapSpinner.classList.add("d-none");

      if (!res.ok) {
        throw new Error(data.detail || "Failed to generate roadmap.");
      }

      activeRoadmap = data.data;
      renderRoadmap(activeRoadmap);
      showAlert(`Personalized ${payload.duration_weeks}-week curriculum generated successfully!`, "success");
    } catch (err) {
      generateRoadmapBtn.disabled = false;
      roadmapSpinner.classList.add("d-none");
      showAlert(err.message, "danger");
    }
  });

  // Render Roadmap Dashboard
  function renderRoadmap(roadmap) {
    if (!roadmap || !roadmap.weeks || roadmap.weeks.length === 0) {
      roadmapDashboardSection.classList.add("d-none");
      roadmapEmptyState.classList.remove("d-none");
      return;
    }

    roadmapEmptyState.classList.add("d-none");
    roadmapDashboardSection.classList.remove("d-none");

    // Metrics
    const pct = Math.round(roadmap.progress_percentage || 0);
    roadmapProgressPct.textContent = `${pct}%`;
    roadmapProgressBar.style.width = `${pct}%`;
    activityCountLabel.textContent = `${roadmap.completed_activities || 0} / ${roadmap.total_activities || 0} Activities Completed`;
    pedagogicalOverviewText.textContent = roadmap.pedagogical_strategy || "";

    // Render Weeks
    renderWeeksList();
  }

  function renderWeeksList() {
    const weeks = activeRoadmap.weeks || [];

    roadmapWeeksContainer.innerHTML = weeks.map(w => {
      // Filter activities based on active filter
      const filteredActs = (w.activities || []).filter(a => {
        if (activeFilter === "all") return true;
        return a.status === activeFilter;
      });

      if (filteredActs.length === 0 && activeFilter !== "all") {
        return "";
      }

      const resourcesHtml = (w.resources || []).map(r => `
        <a href="${r.url}" target="_blank" class="badge bg-dark border border-secondary text-info text-decoration-none px-2 py-1">
          <i class="bi bi-box-arrow-up-right me-1"></i> ${r.name} (${r.type})
        </a>
      `).join("");

      const exercisesHtml = (w.practical_exercises || []).map(ex => `
        <li class="small text-white mb-1"><i class="bi bi-code-slash text-primary me-2"></i>${ex}</li>
      `).join("");

      return `
        <div class="glass-card p-4">
          <div class="d-flex align-items-center justify-content-between mb-3 border-bottom border-secondary border-opacity-50 pb-2 flex-wrap gap-2">
            <div>
              <span class="badge bg-primary me-2">Week ${w.week_number}</span>
              <span class="badge bg-dark border border-secondary text-light small me-2">${w.stage}</span>
              <span class="fw-bold text-white fs-5">${w.skill}</span>
            </div>
            <div class="d-flex align-items-center gap-2">
              <span class="text-white small"><i class="bi bi-clock me-1 text-primary"></i> ${w.estimated_hours} hrs/week</span>
              ${w.is_completed ? '<span class="badge bg-success text-white small"><i class="bi bi-check-circle-fill me-1"></i> Completed</span>' : ''}
            </div>
          </div>

          <p class="text-white small mb-3" style="line-height: 1.5;"><strong>Objective:</strong> ${w.learning_objective}</p>

          <!-- Resources -->
          <div class="mb-3">
            <div class="small fw-bold text-uppercase mb-1" style="color: #cbd5e1; font-size: 0.78rem;">Verified Learning Resources:</div>
            <div class="d-flex flex-wrap gap-1">${resourcesHtml || '<span class="text-muted small">Official documentation</span>'}</div>
          </div>

          <!-- Exercises -->
          <div class="mb-3">
            <div class="small fw-bold text-uppercase mb-1" style="color: #cbd5e1; font-size: 0.78rem;">Hands-on Milestone Deliverables:</div>
            <ul class="list-unstyled mb-0">${exercisesHtml}</ul>
          </div>

          <!-- Activities Checklist -->
          <div class="mt-3 pt-3 border-top border-secondary border-opacity-50">
            <div class="small fw-bold text-uppercase mb-2 text-light">Track Weekly Activities:</div>
            <div class="d-flex flex-column gap-2">
              ${filteredActs.map(act => {
                const isDone = act.status === "completed";
                const isInProg = act.status === "in_progress";
                const borderClass = isDone ? "completed" : (isInProg ? "in-progress" : "pending");

                return `
                  <div class="activity-item ${borderClass} d-flex align-items-center justify-content-between flex-wrap gap-2">
                    <div class="d-flex align-items-center gap-3">
                      <input type="checkbox" class="form-check-input activity-check" style="transform: scale(1.3); cursor: pointer;"
                        data-id="${act.id}" ${isDone ? 'checked' : ''}>
                      <div>
                        <div class="fw-semibold text-white small">${act.title}</div>
                        <div class="text-muted" style="font-size: 0.75rem;">${act.type} &bull; ~${act.estimated_hours} hours</div>
                      </div>
                    </div>
                    <div>
                      <select class="form-select form-select-sm bg-dark text-white border-secondary activity-status-select" data-id="${act.id}" style="width: 140px; font-size: 0.78rem;">
                        <option value="pending" ${act.status === 'pending' ? 'selected' : ''}>Pending</option>
                        <option value="in_progress" ${act.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                        <option value="completed" ${act.status === 'completed' ? 'selected' : ''}>Completed</option>
                      </select>
                    </div>
                  </div>
                `;
              }).join("")}
            </div>
          </div>
        </div>
      `;
    }).join("");

    // Attach Activity Status Listeners
    document.querySelectorAll(".activity-check").forEach(chk => {
      chk.addEventListener("change", async (e) => {
        const actId = e.target.dataset.id;
        const newStatus = e.target.checked ? "completed" : "pending";
        await updateActivityStatus(actId, newStatus);
      });
    });

    document.querySelectorAll(".activity-status-select").forEach(sel => {
      sel.addEventListener("change", async (e) => {
        const actId = e.target.dataset.id;
        await updateActivityStatus(actId, e.target.value);
      });
    });
  }

  async function updateActivityStatus(activityId, status) {
    try {
      const res = await fetch(`/roadmap/activities/${activityId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${currentToken}`
        },
        body: JSON.stringify({ status })
      });
      const data = await res.json();
      if (res.ok && data.data) {
        activeRoadmap = data.data;
        renderRoadmap(activeRoadmap);
      }
    } catch (e) {
      console.warn("Failed to update activity status:", e);
    }
  }

  // Filter Buttons
  document.querySelectorAll(".filter-roadmap-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-roadmap-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeFilter = btn.dataset.filter;
      renderWeeksList();
    });
  });

  initAuth();
});

