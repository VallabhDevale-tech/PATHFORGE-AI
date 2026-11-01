/**
 * PATHFORGE AI - Quizzes & Assessments Client Controller
 * Manages full assessment lifecycle: Topic Selection -> Introduction Screen ->
 * Stepper-based Question Taking -> Live Evaluation & Results Breakdown.
 */

document.addEventListener("DOMContentLoaded", () => {
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
  if (!currentToken) {
    window.location.replace("/login");
    return;
  }

  // State
  let currentSkill = "Python";
  let currentQuizData = null;
  let currentQuestionIndex = 0;
  let userAnswers = {}; // map question_id -> selected_index

  // Views
  const catalogView = document.getElementById("quizCatalogView");
  const introView = document.getElementById("quizIntroView");
  const takingView = document.getElementById("quizTakingView");
  const resultsView = document.getElementById("quizResultsView");

  // Alert
  const quizAlert = document.getElementById("quizAlert");
  const quizAlertIcon = document.getElementById("quizAlertIcon");
  const quizAlertMessage = document.getElementById("quizAlertMessage");

  // Intro Elements
  const introQuizTitle = document.getElementById("introQuizTitle");
  const introQuizDesc = document.getElementById("introQuizDesc");
  const introTotalQuestions = document.getElementById("introTotalQuestions");
  const introBackBtn = document.getElementById("introBackBtn");
  const beginQuizTakingBtn = document.getElementById("beginQuizTakingBtn");

  // Taking Elements
  const takingSkillBadge = document.getElementById("takingSkillBadge");
  const questionCounterText = document.getElementById("questionCounterText");
  const quizProgressBar = document.getElementById("quizProgressBar");
  const currentQuestionTitle = document.getElementById("currentQuestionTitle");
  const optionsContainer = document.getElementById("optionsContainer");
  const prevQuestionBtn = document.getElementById("prevQuestionBtn");
  const nextQuestionBtn = document.getElementById("nextQuestionBtn");
  const submitAssessmentBtn = document.getElementById("submitAssessmentBtn");
  const submitQuizSpinner = document.getElementById("submitQuizSpinner");

  // Results Elements
  const resultStatusBadgeContainer = document.getElementById("resultStatusBadgeContainer");
  const resultStatusHeading = document.getElementById("resultStatusHeading");
  const resultStatusSubheading = document.getElementById("resultStatusSubheading");
  const resultScoreRing = document.getElementById("resultScoreRing");
  const resultScorePercentage = document.getElementById("resultScorePercentage");
  const resultRatioText = document.getElementById("resultRatioText");
  const detailedReviewContainer = document.getElementById("detailedReviewContainer");
  const retakeQuizBtn = document.getElementById("retakeQuizBtn");
  const exploreOtherQuizzesBtn = document.getElementById("exploreOtherQuizzesBtn");

  function showAlert(msg, type = "info") {
    if (!quizAlert) return;
    quizAlert.className = `alert alert-${type} mb-4 glass-card border d-block`;
    quizAlertMessage.textContent = msg;
    quizAlertIcon.className = type === "danger" 
      ? "bi bi-exclamation-triangle-fill text-danger fs-5" 
      : type === "warning" 
        ? "bi bi-exclamation-circle-fill text-warning fs-5" 
        : "bi bi-check-circle-fill text-success fs-5";
  }

  function hideAlert() {
    if (quizAlert) quizAlert.className = "alert d-none";
  }

  function switchView(target) {
    hideAlert();
    [catalogView, introView, takingView, resultsView].forEach(v => {
      if (v) v.classList.add("d-none");
    });
    if (target) target.classList.remove("d-none");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // Bind Start Topic Buttons in Catalog
  document.querySelectorAll(".start-topic-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const skill = btn.getAttribute("data-skill") || "Python";
      loadQuizIntro(skill);
    });
  });

  // Check URL parameters for ?skill=...
  const urlParams = new URLSearchParams(window.location.search);
  const paramSkill = urlParams.get("skill");
  if (paramSkill) {
    loadQuizIntro(paramSkill);
  }

  // =========================================================================
  // STAGE 1: INTRO
  // =========================================================================
  async function loadQuizIntro(skillName) {
    currentSkill = skillName;
    userAnswers = {};
    currentQuestionIndex = 0;

    switchView(introView);

    introQuizTitle.textContent = `${skillName} Skill Diagnostic`;
    introQuizDesc.textContent = `Verify your practical knowledge in ${skillName}. Score 70% or higher to demonstrate verified proficiency.`;
    introTotalQuestions.textContent = "Loading...";

    try {
      const res = await fetch(`/adaptive/quiz?skill=${encodeURIComponent(skillName)}`, {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();
      if (res.ok && data.status === "success" && data.data) {
        currentQuizData = data.data;
        const count = (currentQuizData.questions || []).length;
        introTotalQuestions.textContent = `${count} Questions`;
      } else {
        showAlert(data.detail || "Unable to generate assessment questions.", "danger");
      }
    } catch (e) {
      showAlert("Network error connecting to assessment engine.", "danger");
    }
  }

  if (introBackBtn) {
    introBackBtn.addEventListener("click", () => {
      switchView(catalogView);
    });
  }

  if (beginQuizTakingBtn) {
    beginQuizTakingBtn.addEventListener("click", () => {
      if (!currentQuizData || !currentQuizData.questions || currentQuizData.questions.length === 0) {
        showAlert("Assessment questions are still preparing. Please wait...", "warning");
        return;
      }
      startQuizTaking();
    });
  }

  // =========================================================================
  // STAGE 2: TAKING (STEPPER)
  // =========================================================================
  function startQuizTaking() {
    currentQuestionIndex = 0;
    userAnswers = {};
    switchView(takingView);
    renderActiveQuestion();
  }

  function renderActiveQuestion() {
    const questions = currentQuizData.questions || [];
    const total = questions.length;
    const q = questions[currentQuestionIndex];

    takingSkillBadge.textContent = currentSkill;
    questionCounterText.textContent = `Question ${currentQuestionIndex + 1} of ${total}`;

    // Progress Bar
    const progressPct = ((currentQuestionIndex + 1) / total) * 100;
    quizProgressBar.style.width = `${progressPct}%`;

    // Question Title
    currentQuestionTitle.textContent = q.question;

    // Render Options
    optionsContainer.innerHTML = "";
    (q.options || []).forEach((optText, optIdx) => {
      const optionCard = document.createElement("div");
      const isSelected = userAnswers[q.id] === optIdx;

      optionCard.className = `quiz-option-card ${isSelected ? 'selected' : ''}`;
      optionCard.innerHTML = `
        <div class="quiz-option-letter">${String.fromCharCode(65 + optIdx)}</div>
        <div class="small fw-medium text-dark flex-grow-1">${escapeHtml(optText)}</div>
        <input type="radio" name="opt_${q.id}" value="${optIdx}" ${isSelected ? 'checked' : ''} class="form-check-input mt-0 d-none">
      `;

      optionCard.addEventListener("click", () => {
        userAnswers[q.id] = optIdx;
        renderActiveQuestion();
      });

      optionsContainer.appendChild(optionCard);
    });

    // Button states
    prevQuestionBtn.disabled = currentQuestionIndex === 0;

    const isLast = currentQuestionIndex === total - 1;
    if (isLast) {
      nextQuestionBtn.classList.add("d-none");
      submitAssessmentBtn.classList.remove("d-none");
    } else {
      nextQuestionBtn.classList.remove("d-none");
      submitAssessmentBtn.classList.add("d-none");
    }
  }

  if (prevQuestionBtn) {
    prevQuestionBtn.addEventListener("click", () => {
      if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        renderActiveQuestion();
      }
    });
  }

  if (nextQuestionBtn) {
    nextQuestionBtn.addEventListener("click", () => {
      const questions = currentQuizData.questions || [];
      if (currentQuestionIndex < questions.length - 1) {
        currentQuestionIndex++;
        renderActiveQuestion();
      }
    });
  }

  if (submitAssessmentBtn) {
    submitAssessmentBtn.addEventListener("click", async () => {
      const questions = currentQuizData.questions || [];
      const answeredCount = Object.keys(userAnswers).length;

      if (answeredCount < questions.length) {
        const confirmSubmit = confirm(`You have answered ${answeredCount} of ${questions.length} questions. Unanswered questions will be scored as incorrect. Do you want to submit anyway?`);
        if (!confirmSubmit) return;
      }

      submitAssessmentBtn.disabled = true;
      if (submitQuizSpinner) submitQuizSpinner.classList.remove("d-none");

      try {
        const payload = {
          quiz_id: currentQuizData.quiz_id,
          skill_name: currentQuizData.skill_name || currentSkill,
          answers: userAnswers
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
          if (window.PathForgeUI) {
            window.PathForgeUI.showToast("Assessment scored successfully!", "success");
          }
          renderQuizResults(data.data);
        } else {
          showAlert(data.detail || "Error evaluating assessment answers.", "danger");
          submitAssessmentBtn.disabled = false;
          if (submitQuizSpinner) submitQuizSpinner.classList.add("d-none");
        }
      } catch (err) {
        showAlert("Failed to submit assessment answers. Check network connection.", "danger");
        submitAssessmentBtn.disabled = false;
        if (submitQuizSpinner) submitQuizSpinner.classList.add("d-none");
      }
    });
  }

  // =========================================================================
  // STAGE 3: RESULTS SCREEN
  // =========================================================================
  function renderQuizResults(result) {
    switchView(resultsView);

    const isPassed = result.is_passed;
    const scorePct = result.score_percentage || 0;
    const correctCount = result.correct_count || 0;
    const totalCount = result.total_questions || 3;

    // Status Banner Badge
    if (isPassed) {
      resultStatusBadgeContainer.innerHTML = `
        <span class="badge bg-success bg-opacity-10 text-success border border-success px-4 py-2 rounded-pill fs-6">
          <i class="bi bi-patch-check-fill me-1"></i> Proficiency Verified
        </span>
      `;
      resultStatusHeading.textContent = "Congratulations! You Passed!";
      resultStatusSubheading.textContent = `You demonstrated strong competencies in ${currentSkill}. This achievement has been recorded in your career diagnostics radar.`;
      resultScoreRing.style.borderColor = "var(--success)";
      resultScorePercentage.className = "display-5 fw-bold text-success";
    } else {
      resultStatusBadgeContainer.innerHTML = `
        <span class="badge bg-warning bg-opacity-10 text-warning border border-warning px-4 py-2 rounded-pill fs-6">
          <i class="bi bi-arrow-repeat me-1"></i> Practice Recommended
        </span>
      `;
      resultStatusHeading.textContent = "Keep Practicing!";
      resultStatusSubheading.textContent = `You scored ${scorePct}%. 70% is required to verify mastery. Review the concepts below and retake the quiz when ready.`;
      resultScoreRing.style.borderColor = "var(--warning)";
      resultScorePercentage.className = "display-5 fw-bold text-warning";
    }

    resultScorePercentage.textContent = `${scorePct}%`;
    resultRatioText.textContent = `${correctCount} of ${totalCount} Questions Correct`;

    // Detailed Question Explanations Review
    detailedReviewContainer.innerHTML = "";
    const feedbackList = result.feedback || [];

    feedbackList.forEach((fb, idx) => {
      const qCard = document.createElement("div");
      const isCorrect = fb.is_correct;

      qCard.className = `p-4 rounded-3 border ${isCorrect ? 'border-success bg-success bg-opacity-10' : 'border-danger bg-danger bg-opacity-10'}`;
      qCard.innerHTML = `
        <div class="d-flex align-items-start justify-content-between mb-2">
          <span class="fw-bold small text-muted">Question ${idx + 1}</span>
          <span class="badge ${isCorrect ? 'bg-success' : 'bg-danger'}">
            <i class="bi ${isCorrect ? 'bi-check-lg' : 'bi-x-lg'} me-1"></i> ${isCorrect ? 'Correct' : 'Incorrect'}
          </span>
        </div>
        <h6 class="fw-bold text-dark mb-2">${escapeHtml(fb.question)}</h6>
        <div class="small text-muted mb-3">
          <span class="fw-semibold text-dark">Verified Explanation:</span> ${escapeHtml(fb.explanation)}
        </div>
      `;

      detailedReviewContainer.appendChild(qCard);
    });
  }

  if (retakeQuizBtn) {
    retakeQuizBtn.addEventListener("click", () => {
      loadQuizIntro(currentSkill);
    });
  }

  if (exploreOtherQuizzesBtn) {
    exploreOtherQuizzesBtn.addEventListener("click", () => {
      switchView(catalogView);
    });
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
