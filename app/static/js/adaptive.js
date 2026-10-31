/**
 * PATHFORGE AI - Adaptive Learning & Continuous Intelligence Client Script (Feature 6)
 * Handles learning velocity metrics, "What Should I Learn Next?" guidance,
 * weak area diagnostics, interactive topic quizzes, and non-destructive roadmap adjustments.
 */

document.addEventListener("DOMContentLoaded", () => {
  let currentToken = localStorage.getItem("pathforge_auth_token") || "";
  let supabaseClient = null;
  let currentAdjustmentId = null;
  let currentQuizData = null;
  let currentNextAction = null;

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

  // Next Action
  const nextActionTitle = document.getElementById("nextActionTitle");
  const nextActionWhy = document.getElementById("nextActionWhy");
  const nextActionSkillBadge = document.getElementById("nextActionSkillBadge");
  const nextActionTimeBadge = document.getElementById("nextActionTimeBadge");
  const launchNextActionBtn = document.getElementById("launchNextActionBtn");

  // Velocity Metrics
  const statRoadmapPct = document.getElementById("statRoadmapPct");
  const statActivitiesCount = document.getElementById("statActivitiesCount");
  const statInProgressCount = document.getElementById("statInProgressCount");
  const statProjectsCount = document.getElementById("statProjectsCount");
  const statQuizAvg = document.getElementById("statQuizAvg");
  const statQuizCount = document.getElementById("statQuizCount");

  // Proposed Adjustments
  const adjustmentNoticeCard = document.getElementById("adjustmentNoticeCard");
  const adjustmentReasonText = document.getElementById("adjustmentReasonText");
  const adjustmentChangesList = document.getElementById("adjustmentChangesList");
  const rejectAdjustmentBtn = document.getElementById("rejectAdjustmentBtn");
  const acceptAdjustmentBtn = document.getElementById("acceptAdjustmentBtn");
  const checkAdjustmentsBtn = document.getElementById("checkAdjustmentsBtn");

  // Diagnostics Lists
  const countDemonstratedBadge = document.getElementById("countDemonstratedBadge");
  const demonstratedList = document.getElementById("demonstratedList");
  const countNeedsPracticeBadge = document.getElementById("countNeedsPracticeBadge");
  const needsPracticeList = document.getElementById("needsPracticeList");

  // Modal Elements
  const quizModalEl = document.getElementById("quizModal");
  const quizModalTitle = document.getElementById("quizModalTitle");
  const quizModalBody = document.getElementById("quizModalBody");
  const submitQuizBtn = document.getElementById("submitQuizBtn");

  let quizModalInstance = null;
  if (quizModalEl) {
    quizModalInstance = new bootstrap.Modal(quizModalEl);
  }

  function showAlert(message, type = "info") {
    alertBox.className = `alert alert-${type} mb-4 glass-card border-0 d-block`;
    alertMessage.textContent = message;
    alertIcon.className = type === "danger" 
      ? "bi bi-exclamation-triangle-fill text-danger fs-4" 
      : type === "warning"
        ? "bi bi-exclamation-circle-fill text-warning fs-4"
        : "bi bi-check-circle-fill text-success fs-4";
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

    loadAdaptiveDashboard();
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      if (supabaseClient) {
        try { await supabaseClient.auth.signOut(); } catch (e) {}
      }
      localStorage.removeItem("pathforge_auth_token");
      window.location.replace("/");
    });
  }

  // =========================================================================
  // DASHBOARD DATA LOADERS
  // =========================================================================
  async function loadAdaptiveDashboard() {
    hideAlert();
    await Promise.all([
      loadOverviewMetrics(),
      loadNextRecommendation(),
      loadWeakAreaDiagnostics()
    ]);
  }

  async function loadOverviewMetrics() {
    try {
      const res = await fetch("/adaptive/overview", {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        const m = data.data;
        if (statRoadmapPct) statRoadmapPct.textContent = `${m.roadmap_completion_pct || 0}%`;
        if (statActivitiesCount) statActivitiesCount.textContent = `${m.completed_activities || 0} / ${m.total_activities || 0} Activities`;
        if (statInProgressCount) statInProgressCount.textContent = m.in_progress_activities || 0;
        if (statProjectsCount) statProjectsCount.textContent = m.completed_projects || 0;
        if (statQuizAvg) statQuizAvg.textContent = `${m.assessment_average_score || 0}%`;
        if (statQuizCount) statQuizCount.textContent = `${m.total_assessments_taken || 0} Quizzes Taken`;
      }
    } catch (e) {
      console.warn("Failed to load adaptive metrics:", e);
    }
  }

  async function loadNextRecommendation() {
    try {
      const res = await fetch("/adaptive/next", {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();
      if (res.ok && data.status === "success" && data.data) {
        currentNextAction = data.data;
        if (nextActionTitle) nextActionTitle.textContent = currentNextAction.title || "Continue Career Roadmap";
        if (nextActionWhy) nextActionWhy.textContent = currentNextAction.why || "High leverage activity for your current skill targets.";
        if (nextActionSkillBadge) nextActionSkillBadge.textContent = `Skill: ${currentNextAction.skill || 'General'}`;
        if (nextActionTimeBadge) nextActionTimeBadge.innerHTML = `<i class="bi bi-clock me-1 text-primary"></i> Est. ~${currentNextAction.estimated_time_minutes || 45} mins`;
      }
    } catch (e) {
      console.warn("Failed to load next recommendation:", e);
    }
  }

  async function loadWeakAreaDiagnostics() {
    try {
      const res = await fetch("/adaptive/weak-areas", {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();
      if (res.ok && data.status === "success" && data.data) {
        renderDiagnostics(data.data);
      }
    } catch (e) {
      console.warn("Failed to load weak areas:", e);
    }
  }

  function renderDiagnostics(diagnostics) {
    const demonstrated = diagnostics.demonstrated_proficiency || [];
    const needsPractice = diagnostics.needs_more_practice || [];

    if (countDemonstratedBadge) countDemonstratedBadge.textContent = demonstrated.length;
    if (countNeedsPracticeBadge) countNeedsPracticeBadge.textContent = needsPractice.length;

    // 1. Demonstrated List
    if (demonstratedList) {
      if (demonstrated.length === 0) {
        demonstratedList.innerHTML = `
          <div class="text-center py-4 text-muted small">
            <i class="bi bi-info-circle me-1"></i> No skills fully verified yet. Complete roadmap milestones or take a topic quiz to demonstrate mastery.
          </div>
        `;
      } else {
        demonstratedList.innerHTML = demonstrated.map(item => `
          <div class="p-3 rounded-2 bg-dark bg-opacity-50 border border-success border-opacity-25 d-flex align-items-center justify-content-between flex-wrap gap-2">
            <div>
              <div class="d-flex align-items-center gap-2 mb-1">
                <span class="fw-bold text-white fs-6">${escapeHtml(item.skill)}</span>
                <span class="badge bg-success bg-opacity-25 text-success border border-success border-opacity-50 small">
                  ${escapeHtml(item.level || "Proficient")}
                </span>
              </div>
              <p class="text-white small mb-0 opacity-75">${escapeHtml(item.reason || "Validated through assessments and practical work.")}</p>
            </div>
            <button class="btn btn-outline-success btn-sm rounded-pill px-3 test-skill-btn" data-skill="${escapeHtml(item.skill)}">
              <i class="bi bi-arrow-repeat me-1"></i> Test Again
            </button>
          </div>
        `).join("");
      }
    }

    // 2. Needs Practice List
    if (needsPracticeList) {
      if (needsPractice.length === 0) {
        needsPracticeList.innerHTML = `
          <div class="text-center py-4 text-muted small">
            <i class="bi bi-check2-circle text-success me-1"></i> Great work! No flagged skill deficiencies detected.
          </div>
        `;
      } else {
        needsPracticeList.innerHTML = needsPractice.map(item => `
          <div class="p-3 rounded-2 bg-dark bg-opacity-50 border border-warning border-opacity-25 d-flex align-items-center justify-content-between flex-wrap gap-2">
            <div style="max-width: 70%;">
              <div class="d-flex align-items-center gap-2 mb-1">
                <span class="fw-bold text-white fs-6">${escapeHtml(item.skill)}</span>
                <span class="badge bg-warning bg-opacity-25 text-warning border border-warning border-opacity-50 small">
                  Priority Focus
                </span>
              </div>
              <p class="text-white small mb-1">${escapeHtml(item.reason || "Requires additional reinforcement.")}</p>
              <p class="text-muted small mb-0" style="font-size: 0.75rem;">
                <i class="bi bi-lightbulb text-warning me-1"></i> ${escapeHtml(item.recommendation || "Complete targeted exercises.")}
              </p>
            </div>
            <button class="btn btn-warning btn-sm text-dark fw-semibold rounded-pill px-3 test-skill-btn" data-skill="${escapeHtml(item.skill)}">
              <i class="bi bi-patch-question me-1"></i> Take Quiz
            </button>
          </div>
        `).join("");
      }
    }

    // Attach quiz trigger handlers
    document.querySelectorAll(".test-skill-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const skill = btn.getAttribute("data-skill");
        if (skill) openTopicQuiz(skill);
      });
    });
  }

  // =========================================================================
  // NEXT ACTION BUTTON HANDLER
  // =========================================================================
  if (launchNextActionBtn) {
    launchNextActionBtn.addEventListener("click", () => {
      if (!currentNextAction) {
        window.location.href = "/personalized-roadmap";
        return;
      }
      const type = currentNextAction.type;
      if (type === "quiz") {
        openTopicQuiz(currentNextAction.skill || "Python");
      } else if (type === "project") {
        window.location.href = "/project-recommendations";
      } else {
        window.location.href = "/personalized-roadmap";
      }
    });
  }

  // =========================================================================
  // PROPOSE & RESOLVE ROADMAP ADJUSTMENTS
  // =========================================================================
  if (checkAdjustmentsBtn) {
    checkAdjustmentsBtn.addEventListener("click", async () => {
      checkAdjustmentsBtn.disabled = true;
      checkAdjustmentsBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Analyzing...`;
      try {
        const res = await fetch("/adaptive/propose-adjustments", {
          method: "POST",
          headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const data = await res.json();
        if (res.ok && data.status === "success") {
          if (data.has_adjustment && data.data) {
            displayProposedAdjustment(data.data);
            showAlert("Curriculum adjustment proposed based on your diagnostic metrics.", "warning");
          } else {
            if (adjustmentNoticeCard) adjustmentNoticeCard.classList.add("d-none");
            showAlert(data.message || "Learning pace is on track! No adjustments recommended at this time.", "success");
          }
        } else {
          showAlert(data.detail || "Unable to analyze roadmap adjustments. Ensure a roadmap has been generated first.", "info");
        }
      } catch (err) {
        showAlert("Failed to evaluate curriculum adjustments. Please check your network.", "danger");
      } finally {
        checkAdjustmentsBtn.disabled = false;
        checkAdjustmentsBtn.innerHTML = `<i class="bi bi-cpu me-1"></i> Analyze for Roadmap Adjustments`;
      }
    });
  }

  function displayProposedAdjustment(adj) {
    currentAdjustmentId = adj.id;
    if (adjustmentReasonText) adjustmentReasonText.textContent = adj.reason || "Adaptive changes proposed to accelerate target skill mastery.";
    if (adjustmentChangesList) {
      const changes = adj.proposed_changes || [];
      adjustmentChangesList.innerHTML = changes.map(c => `<li>${escapeHtml(c)}</li>`).join("");
    }
    if (adjustmentNoticeCard) {
      adjustmentNoticeCard.classList.remove("d-none");
      adjustmentNoticeCard.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }

  if (acceptAdjustmentBtn) {
    acceptAdjustmentBtn.addEventListener("click", () => resolveAdjustment("accept"));
  }

  if (rejectAdjustmentBtn) {
    rejectAdjustmentBtn.addEventListener("click", () => resolveAdjustment("reject"));
  }

  async function resolveAdjustment(action) {
    if (!currentAdjustmentId) return;

    try {
      const res = await fetch(`/adaptive/adjustment/resolve?adjustment_id=${encodeURIComponent(currentAdjustmentId)}&action=${action}`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        if (adjustmentNoticeCard) adjustmentNoticeCard.classList.add("d-none");
        currentAdjustmentId = null;
        showAlert(
          action === "accept" 
            ? "Roadmap successfully updated with your targeted reinforcement activities." 
            : "Adjustment declined. Current curriculum preserved intact.",
          "success"
        );
        loadAdaptiveDashboard();
      } else {
        showAlert(data.detail || "Failed to resolve curriculum adjustment.", "danger");
      }
    } catch (e) {
      showAlert("Error updating curriculum adjustment.", "danger");
    }
  }

  // =========================================================================
  // INTERACTIVE TOPIC QUIZ ENGINE
  // =========================================================================
  async function openTopicQuiz(skillName) {
    if (!quizModalInstance) return;

    if (quizModalTitle) quizModalTitle.textContent = `${skillName} Skill Assessment`;
    if (quizModalBody) {
      quizModalBody.innerHTML = `
        <div class="text-center py-5">
          <div class="spinner-border text-primary mb-3" role="status"></div>
          <p class="text-muted">Generating 3 verified assessment questions for ${escapeHtml(skillName)}...</p>
        </div>
      `;
    }
    if (submitQuizBtn) {
      submitQuizBtn.disabled = true;
      submitQuizBtn.classList.remove("d-none");
    }

    quizModalInstance.show();

    try {
      const res = await fetch(`/adaptive/quiz?skill=${encodeURIComponent(skillName)}`, {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();
      if (res.ok && data.status === "success" && data.data) {
        currentQuizData = data.data;
        renderQuizQuestions(currentQuizData);
        if (submitQuizBtn) submitQuizBtn.disabled = false;
      } else {
        quizModalBody.innerHTML = `
          <div class="alert alert-danger glass-card border-0">
            Failed to load quiz questions: ${escapeHtml(data.detail || "Unknown error")}
          </div>
        `;
      }
    } catch (e) {
      quizModalBody.innerHTML = `
        <div class="alert alert-danger glass-card border-0">
          Network error loading assessment questions.
        </div>
      `;
    }
  }

  function renderQuizQuestions(quiz) {
    const questions = quiz.questions || [];
    quizModalBody.innerHTML = `
      <div class="mb-3 text-muted small">
        <i class="bi bi-info-circle me-1"></i> Select the best answer for each question. 70% or higher is required to demonstrate proficiency.
      </div>
      <form id="quizForm" class="d-flex flex-column gap-4">
        ${questions.map((q, idx) => `
          <div class="p-3 rounded-3 bg-dark bg-opacity-50 border border-secondary border-opacity-50">
            <h6 class="fw-bold text-white mb-3">
              <span class="badge bg-primary me-2">${idx + 1}</span> ${escapeHtml(q.question)}
            </h6>
            <div class="d-flex flex-column gap-2">
              ${q.options.map((opt, optIdx) => `
                <label class="p-2 px-3 rounded-2 border border-secondary border-opacity-25 d-flex align-items-center gap-2 cursor-pointer hover-bg-subtle" style="background: rgba(15, 23, 42, 0.6); cursor: pointer;">
                  <input type="radio" name="question_${q.id}" value="${optIdx}" class="form-check-input mt-0 me-1">
                  <span class="text-white small">${escapeHtml(opt)}</span>
                </label>
              `).join("")}
            </div>
            <div id="feedback_${q.id}" class="mt-2 d-none"></div>
          </div>
        `).join("")}
      </form>
    `;
  }

  if (submitQuizBtn) {
    submitQuizBtn.addEventListener("click", async () => {
      if (!currentQuizData) return;

      const form = document.getElementById("quizForm");
      if (!form) return;

      const questions = currentQuizData.questions || [];
      const answers = {};
      let unanswered = 0;

      questions.forEach(q => {
        const checked = form.querySelector(`input[name="question_${q.id}"]:checked`);
        if (checked) {
          answers[q.id] = parseInt(checked.value, 10);
        } else {
          unanswered++;
        }
      });

      if (unanswered > 0) {
        alert(`Please answer all ${questions.length} questions before submitting.`);
        return;
      }

      submitQuizBtn.disabled = true;
      submitQuizBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Scoring...`;

      try {
        const payload = {
          quiz_id: currentQuizData.quiz_id,
          skill_name: currentQuizData.skill_name,
          answers: answers
        };

        const res = await fetch("/adaptive/quiz/submit", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${currentToken}`
          },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (res.ok && data.status === "success" && data.data) {
          renderQuizResults(data.data);
          loadAdaptiveDashboard();
        } else {
          alert(`Submission error: ${data.detail || "Unable to score assessment."}`);
          submitQuizBtn.disabled = false;
          submitQuizBtn.innerHTML = `<i class="bi bi-send-check me-1"></i> Submit Assessment`;
        }
      } catch (err) {
        alert("Failed to submit assessment answers.");
        submitQuizBtn.disabled = false;
        submitQuizBtn.innerHTML = `<i class="bi bi-send-check me-1"></i> Submit Assessment`;
      }
    });
  }

  function renderQuizResults(result) {
    const isPassed = result.is_passed;
    const scorePct = result.score_percentage;
    const feedbackList = result.feedback || [];

    // Hide submit button now that it's submitted
    if (submitQuizBtn) submitQuizBtn.classList.add("d-none");

    // Display banner at top of body
    const banner = `
      <div class="alert ${isPassed ? 'alert-success border-success' : 'alert-warning border-warning'} glass-card p-3 mb-4">
        <div class="d-flex align-items-center justify-content-between">
          <div class="d-flex align-items-center gap-2">
            <i class="bi ${isPassed ? 'bi-check-circle-fill text-success fs-3' : 'bi-exclamation-triangle-fill text-warning fs-3'}"></i>
            <div>
              <h5 class="fw-bold mb-0 text-white">${isPassed ? 'Proficiency Verified!' : 'Needs Reinforcement'}</h5>
              <div class="small text-white opacity-75">${result.correct_count} of ${result.total_questions} questions correct</div>
            </div>
          </div>
          <div class="fs-2 fw-bold ${isPassed ? 'text-success' : 'text-warning'}">${scorePct}%</div>
        </div>
      </div>
    `;

    // Render detailed question breakdowns
    feedbackList.forEach(fb => {
      const container = document.getElementById(`feedback_${fb.question_id}`);
      if (container) {
        container.className = `mt-2 p-2 px-3 rounded-2 border ${fb.is_correct ? 'border-success bg-success' : 'border-danger bg-danger'} bg-opacity-10 d-block`;
        container.innerHTML = `
          <div class="d-flex align-items-start gap-2">
            <i class="bi ${fb.is_correct ? 'bi-check-circle text-success' : 'bi-x-circle text-danger'} mt-1"></i>
            <div class="small text-white">
              <span class="fw-bold">${fb.is_correct ? 'Correct!' : 'Incorrect.'}</span> ${escapeHtml(fb.explanation)}
            </div>
          </div>
        `;
      }
    });

    quizModalBody.insertAdjacentHTML("afterbegin", banner);
  }

  // Helper
  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Initialize Auth
  initAuth();
});

