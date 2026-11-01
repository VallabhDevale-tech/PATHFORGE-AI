/**
 * PATHFORGE AI - Central Command Center Dashboard Client Script
 * Fetches real candidate telemetry from backend APIs:
 * Target career, roadmap velocity, project count, quiz metrics, and next steps.
 */

document.addEventListener("DOMContentLoaded", async () => {
  let currentToken = localStorage.getItem("pathforge_auth_token") || "";
  let supabaseClient = null;

  if (window.PATHFORGE_CONFIG && window.PATHFORGE_CONFIG.supabaseUrl && window.PATHFORGE_CONFIG.supabaseKey && window.supabase) {
    try {
      supabaseClient = window.supabase.createClient(
        window.PATHFORGE_CONFIG.supabaseUrl,
        window.PATHFORGE_CONFIG.supabaseKey
      );
    } catch (e) {}
  }

  // Auth Protection
  if (!currentToken && supabaseClient) {
    try {
      const { data } = await supabaseClient.auth.getSession();
      if (data && data.session && data.session.access_token) {
        currentToken = data.session.access_token;
        localStorage.setItem("pathforge_auth_token", currentToken);
      }
    } catch (err) {}
  }

  if (!currentToken) {
    window.location.replace("/login");
    return;
  }

  // Parse User Name from token
  try {
    const payload = JSON.parse(atob(currentToken.split(".")[1]));
    const email = payload.email || "Candidate";
    const name = email.split("@")[0];
    const capitalized = name.charAt(0).toUpperCase() + name.slice(1);
    const welcomeUserName = document.getElementById("welcomeUserName");
    if (welcomeUserName) welcomeUserName.textContent = capitalized;
  } catch (err) {}

  // Load Dashboard Data
  loadDashboardData();

  async function loadDashboardData() {
    await Promise.allSettled([
      fetchTargetCareer(),
      fetchLearningOverview(),
      fetchWhatToLearnNext()
    ]);
  }

  // 1. Target Career
  async function fetchTargetCareer() {
    try {
      const res = await fetch("/careers/selected", {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();
      const titleEl = document.getElementById("dashTargetCareerTitle");
      if (res.ok && data.status === "success" && data.has_selection && data.data) {
        if (titleEl) titleEl.textContent = data.data.career_title || "Target Career";
      } else {
        if (titleEl) titleEl.textContent = "Full Stack Developer (Default)";
      }
    } catch (e) {
      console.debug("Target career note:", e);
    }
  }

  // 2. Learning Overview Velocity Metrics
  async function fetchLearningOverview() {
    try {
      const res = await fetch("/adaptive/overview", {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();
      if (res.ok && data.status === "success" && data.data) {
        const m = data.data;

        // Roadmap %
        const pct = m.roadmap_completion_pct || m.roadmap_progress_percentage || 0;
        const pctEl = document.getElementById("dashRoadmapPct");
        const barEl = document.getElementById("dashRoadmapBar");
        const actLabel = document.getElementById("dashActivitiesCompleted");

        if (pctEl) pctEl.textContent = `${pct}%`;
        if (barEl) barEl.style.width = `${pct}%`;
        if (actLabel) {
          actLabel.textContent = `${m.completed_activities || 0} of ${m.total_activities || 0} Activities`;
        }

        // In Progress
        const inProgEl = document.getElementById("dashInProgressCount");
        if (inProgEl) inProgEl.textContent = m.in_progress_activities || 0;

        // Projects
        const projEl = document.getElementById("dashProjectsCount");
        if (projEl) projEl.textContent = m.completed_projects_count || m.completed_projects || 0;

        // Quizzes
        const quizAvgEl = document.getElementById("dashQuizAvg");
        const quizCountLabel = document.getElementById("dashQuizCountLabel");
        if (quizAvgEl) quizAvgEl.textContent = `${m.average_assessment_score || m.assessment_average_score || 0}%`;
        if (quizCountLabel) {
          quizCountLabel.textContent = `${m.assessments_completed_count || m.total_assessments_taken || 0} topic assessments taken.`;
        }
      }
    } catch (e) {
      console.debug("Overview metric note:", e);
    }
  }

  // 3. What Should I Learn Next?
  async function fetchWhatToLearnNext() {
    try {
      const res = await fetch("/adaptive/next", {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();
      if (res.ok && data.status === "success" && data.data) {
        const next = data.data;
        const titleEl = document.getElementById("dashNextActionTitle");
        const whyEl = document.getElementById("dashNextActionWhy");
        const skillEl = document.getElementById("dashNextSkillBadge");
        const timeEl = document.getElementById("dashNextTimeBadge");
        const btn = document.getElementById("dashStartNextActionBtn");

        if (titleEl) titleEl.textContent = next.title || "Continue Your Learning Journey";
        if (whyEl) whyEl.textContent = next.why || next.why_recommended || "Recommended based on your target skills.";
        if (skillEl) skillEl.innerHTML = `<i class="bi bi-tag-fill text-primary me-1"></i> Skill: ${next.skill || next.skill_improved || 'General'}`;
        if (timeEl) timeEl.innerHTML = `<i class="bi bi-clock me-1 text-primary"></i> Est. ${next.estimated_time || '~45 mins'}`;

        if (btn) {
          btn.addEventListener("click", () => {
            if (next.action_type === "quiz") {
              window.location.href = `/quizzes?skill=${encodeURIComponent(next.skill || 'Python')}`;
            } else if (next.action_type === "roadmap_activity") {
              window.location.href = "/personalized-roadmap";
            } else {
              window.location.href = "/adaptive-learning";
            }
          });
        }
      }
    } catch (e) {
      console.debug("Next action note:", e);
    }
  }
});
