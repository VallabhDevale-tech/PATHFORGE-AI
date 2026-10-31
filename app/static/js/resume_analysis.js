/**
 * PATHFORGE AI - Resume Analysis Client Script
 * Handles authentication, drag-and-drop file uploads, 4-stage processing,
 * structured dashboard visualization, and resume history management.
 */

document.addEventListener("DOMContentLoaded", () => {
  // ---------------------------------------------------------------------------
  // State & Elements
  // ---------------------------------------------------------------------------
  let currentToken = localStorage.getItem("pathforge_auth_token") || "";
  let selectedFile = null;
  let supabaseClient = null;

  // Initialize Supabase client if config is provided
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

  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("resumeFileInput");
  const filePreviewCard = document.getElementById("filePreviewCard");
  const selectedFileName = document.getElementById("selectedFileName");
  const selectedFileSize = document.getElementById("selectedFileSize");
  const fileTypeIcon = document.getElementById("fileTypeIcon");
  const clearFileBtn = document.getElementById("clearFileBtn");
  const startUploadBtn = document.getElementById("startUploadBtn");

  const uploadSection = document.getElementById("uploadSection");
  const processingSection = document.getElementById("processingSection");
  const processingProgressBar = document.getElementById("processingProgressBar");
  const processingStatusTitle = document.getElementById("processingStatusTitle");
  const processingStatusSubtitle = document.getElementById("processingStatusSubtitle");

  const resultsSection = document.getElementById("resultsSection");
  const historyTableBody = document.getElementById("resumeHistoryTableBody");
  const refreshHistoryBtn = document.getElementById("refreshHistoryBtn");

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
  // Authentication & Route Protection
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

    // Unauthenticated user -> redirect to login page (/)
    window.location.replace("/");
  }

  function setAuthenticatedState(token, email) {
    currentToken = token;
    localStorage.setItem("pathforge_auth_token", token);
    if (userEmailText) userEmailText.textContent = email;
    if (userEmailBadge) userEmailBadge.classList.remove("d-none");
    if (logoutBtn) logoutBtn.classList.remove("d-none");
    loadResumeHistory();
  }

  // Logout Handler
  logoutBtn?.addEventListener("click", async () => {
    if (supabaseClient) {
      try {
        await supabaseClient.auth.signOut();
      } catch (e) {
        console.warn("SignOut error:", e);
      }
    }
    localStorage.removeItem("pathforge_auth_token");
    window.location.replace("/");
  });

  // ---------------------------------------------------------------------------
  // File Selection & Drag-and-Drop
  // ---------------------------------------------------------------------------
  dropZone?.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-active");
  });

  dropZone?.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-active");
  });

  dropZone?.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-active");
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput?.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  function handleFileSelected(file) {
    hideAlert();
    const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
    if (ext !== ".pdf" && ext !== ".docx") {
      showAlert(`Unsupported file extension '${ext}'. Only .pdf and .docx are supported.`, "danger");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      showAlert(`File exceeds maximum size limit of 5 MB (Current size: ${(file.size / (1024 * 1024)).toFixed(2)} MB).`, "danger");
      return;
    }

    selectedFile = file;
    selectedFileName.textContent = file.name;
    selectedFileSize.textContent = formatBytes(file.size);

    if (ext === ".pdf") {
      fileTypeIcon.className = "bi bi-file-earmark-pdf fs-4 text-danger";
    } else {
      fileTypeIcon.className = "bi bi-file-earmark-word fs-4 text-primary";
    }

    filePreviewCard.classList.remove("d-none");
  }

  clearFileBtn?.addEventListener("click", () => {
    selectedFile = null;
    fileInput.value = "";
    filePreviewCard.classList.add("d-none");
  });

  function formatBytes(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }

  // ---------------------------------------------------------------------------
  // Upload & 4-Stage Stepper Simulation
  // ---------------------------------------------------------------------------
  startUploadBtn?.addEventListener("click", async () => {
    if (!selectedFile) {
      showAlert("Please choose a resume file to analyze.", "warning");
      return;
    }

    if (!currentToken) {
      window.location.replace("/");
      return;
    }

    hideAlert();
    uploadSection.classList.add("d-none");
    processingSection.classList.remove("d-none");
    resultsSection.classList.add("d-none");

    setStepperStage(1);

    const formData = new FormData();
    formData.append("file", selectedFile);

    // Simulate stage 2 after upload begins
    const timer1 = setTimeout(() => setStepperStage(2), 1200);
    const timer2 = setTimeout(() => setStepperStage(3), 2800);

    try {
      const response = await fetch("/resumes/upload", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${currentToken}`
        },
        body: formData
      });

      clearTimeout(timer1);
      clearTimeout(timer2);

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Resume upload and analysis failed.");
      }

      setStepperStage(4);
      setTimeout(() => {
        completeProcessing(result.data);
      }, 800);

    } catch (err) {
      clearTimeout(timer1);
      clearTimeout(timer2);
      processingSection.classList.add("d-none");
      uploadSection.classList.remove("d-none");

      let errorMsg = err.message || "An unexpected error occurred.";
      if (errorMsg.includes("OCR")) {
        showAlert(errorMsg, "warning");
      } else {
        showAlert(errorMsg, "danger");
      }
    }
  });

  function setStepperStage(stage) {
    const stages = [1, 2, 3, 4];
    stages.forEach(s => {
      const item = document.getElementById(`step${s}`);
      const circle = document.getElementById(`step${s}Circle`);
      if (s < stage) {
        item.className = "step-item completed";
        circle.innerHTML = '<i class="bi bi-check"></i>';
      } else if (s === stage) {
        item.className = "step-item active";
        circle.innerHTML = `${s}`;
      } else {
        item.className = "step-item";
        circle.innerHTML = `${s}`;
      }
    });

    const progressPercent = stage * 25;
    processingProgressBar.style.width = `${progressPercent}%`;

    if (stage === 1) {
      processingStatusTitle.textContent = "Stage 1: Uploading Resume...";
      processingStatusSubtitle.textContent = "Storing candidate document safely into private Supabase Storage.";
    } else if (stage === 2) {
      processingStatusTitle.textContent = "Stage 2: Extracting Text...";
      processingStatusSubtitle.textContent = "Parsing document pages, tables, and headers using PyMuPDF / python-docx.";
    } else if (stage === 3) {
      processingStatusTitle.textContent = "Stage 3: AI Information Extraction...";
      processingStatusSubtitle.textContent = "Extracting verified skills, education, and career experience.";
    } else if (stage === 4) {
      processingStatusTitle.textContent = "Stage 4: Saving Structured Intelligence...";
      processingStatusSubtitle.textContent = "Persisting structured analysis to Supabase PostgreSQL.";
    }
  }

  function completeProcessing(data) {
    processingSection.classList.add("d-none");
    uploadSection.classList.remove("d-none");
    selectedFile = null;
    fileInput.value = "";
    filePreviewCard.classList.add("d-none");

    const analysis = data.analysis;
    renderAnalysisDashboard(analysis, data.resume?.file_name);
    loadResumeHistory();
  }

  // ---------------------------------------------------------------------------
  // Render Structured Results Dashboard
  // ---------------------------------------------------------------------------
  function renderAnalysisDashboard(analysis, fileName = "Resume Analysis") {
    resultsSection.classList.remove("d-none");
    resultsSection.scrollIntoView({ behavior: "smooth" });

    const pInfo = analysis.personal_information || {};
    const pSummary = analysis.professional_summary || {};
    const techSkills = analysis.technical_skills || [];
    const softSkills = analysis.soft_skills || [];
    const workExp = analysis.work_experience || [];
    const education = analysis.education || [];
    const projects = analysis.projects || [];
    const certs = analysis.certifications || [];
    const addlInfo = analysis.additional_information || [];

    // Header Candidate Name
    document.getElementById("resultCandidateName").textContent =
      pInfo.full_name ? `${pInfo.full_name}'s Analysis Report` : fileName;

    // A. Personal Info
    const personalInfoContainer = document.getElementById("personalInfoContainer");
    personalInfoContainer.innerHTML = `
      <div class="row g-3">
        <div class="col-sm-6">
          <div class="small fw-bold text-uppercase" style="color: #cbd5e1; letter-spacing: 0.05em;">Full Name</div>
          <div class="fw-semibold text-white fs-6 mt-1">${pInfo.full_name || '<span style="color: #94a3b8;">Not provided</span>'}</div>
        </div>
        <div class="col-sm-6">
          <div class="small fw-bold text-uppercase" style="color: #cbd5e1; letter-spacing: 0.05em;">Email Address</div>
          <div class="fw-semibold text-white fs-6 mt-1">${pInfo.email ? `<a href="mailto:${pInfo.email}" class="text-primary text-decoration-none">${pInfo.email}</a>` : '<span style="color: #94a3b8;">Not provided</span>'}</div>
        </div>
        <div class="col-sm-6">
          <div class="small fw-bold text-uppercase" style="color: #cbd5e1; letter-spacing: 0.05em;">Phone Number</div>
          <div class="fw-semibold text-white fs-6 mt-1">${pInfo.phone_number || '<span style="color: #94a3b8;">Not provided</span>'}</div>
        </div>
        <div class="col-sm-6">
          <div class="small fw-bold text-uppercase" style="color: #cbd5e1; letter-spacing: 0.05em;">Location</div>
          <div class="fw-semibold text-white fs-6 mt-1">${pInfo.location || '<span style="color: #94a3b8;">Not provided</span>'}</div>
        </div>
        <div class="col-12 border-top border-secondary border-opacity-50 pt-3 mt-3 d-flex flex-wrap gap-3">
          ${pInfo.linkedin_url ? `<a href="${pInfo.linkedin_url}" target="_blank" class="btn btn-outline-custom btn-sm rounded-pill"><i class="bi bi-linkedin text-primary me-1"></i> LinkedIn</a>` : ''}
          ${pInfo.github_url ? `<a href="${pInfo.github_url}" target="_blank" class="btn btn-outline-custom btn-sm rounded-pill"><i class="bi bi-github me-1"></i> GitHub</a>` : ''}
          ${pInfo.portfolio_url ? `<a href="${pInfo.portfolio_url}" target="_blank" class="btn btn-outline-custom btn-sm rounded-pill"><i class="bi bi-globe2 text-info me-1"></i> Portfolio</a>` : ''}
          ${!pInfo.linkedin_url && !pInfo.github_url && !pInfo.portfolio_url ? '<span style="color: #94a3b8;" class="small">No professional links detected in resume.</span>' : ''}
        </div>
      </div>
    `;

    // B. Professional Summary
    const summaryContainer = document.getElementById("professionalSummaryContainer");
    let strengthsHtml = (pSummary.main_strengths || []).map(s => `<li class="mb-1 text-white"><i class="bi bi-shield-check text-primary me-2"></i>${s}</li>`).join("");
    let areasHtml = (pSummary.primary_areas_of_experience || []).map(a => `<span class="badge bg-dark border border-secondary text-white me-1 mb-1 px-3 py-1" style="font-size: 0.82rem;">${a}</span>`).join("");

    summaryContainer.innerHTML = `
      <p class="text-white mb-3" style="line-height: 1.6; font-size: 0.95rem;">${pSummary.existing_summary || '<span style="color: #94a3b8;">No explicit summary found in candidate resume.</span>'}</p>
      ${strengthsHtml ? `<div class="mt-3"><div class="small fw-bold uppercase mb-2" style="color: #cbd5e1; letter-spacing: 0.05em;">Core Strengths</div><ul class="list-unstyled mb-3">${strengthsHtml}</ul></div>` : ''}
      ${areasHtml ? `<div class="mt-2"><div class="small fw-bold uppercase mb-2" style="color: #cbd5e1; letter-spacing: 0.05em;">Primary Domains</div><div class="d-flex flex-wrap">${areasHtml}</div></div>` : ''}
    `;

    // C. Technical Skills
    document.getElementById("techSkillsCount").textContent = `${techSkills.length} Skills`;
    const techContainer = document.getElementById("technicalSkillsList");
    if (techSkills.length > 0) {
      techContainer.innerHTML = techSkills.map(skill => `<span class="skill-badge">${skill}</span>`).join("");
    } else {
      techContainer.innerHTML = '<span style="color: #94a3b8;" class="small">No explicit technical skills identified.</span>';
    }

    // D. Soft Skills
    document.getElementById("softSkillsCount").textContent = `${softSkills.length} Skills`;
    const softContainer = document.getElementById("softSkillsList");
    if (softSkills.length > 0) {
      softContainer.innerHTML = softSkills.map(skill => `<span class="skill-badge soft-skill">${skill}</span>`).join("");
    } else {
      softContainer.innerHTML = '<span style="color: #94a3b8;" class="small">No explicit soft skills identified.</span>';
    }

    // E. Work Experience
    const workContainer = document.getElementById("workExperienceContainer");
    if (workExp.length > 0) {
      workContainer.innerHTML = workExp.map(exp => `
        <div class="timeline-item">
          <div class="timeline-title">${exp.job_title || 'Position'} <span style="color: #94a3b8;">at</span> <span class="text-primary">${exp.company || 'Organization'}</span></div>
          <div class="timeline-meta" style="color: #cbd5e1;"><i class="bi bi-calendar3 me-1"></i> ${exp.start_date || 'Start'} - ${exp.end_date || 'Present'}</div>
          ${(exp.responsibilities && exp.responsibilities.length > 0) ? `
            <div class="small fw-bold text-uppercase mb-1" style="color: #cbd5e1;">Responsibilities:</div>
            <ul class="text-white small mb-2 ps-3">
              ${exp.responsibilities.map(r => `<li class="mb-1">${r}</li>`).join("")}
            </ul>
          ` : ''}
          ${(exp.achievements && exp.achievements.length > 0) ? `
            <div class="small text-primary fw-bold text-uppercase mb-1">Key Achievements:</div>
            <ul class="text-white small mb-0 ps-3">
              ${exp.achievements.map(a => `<li class="mb-1">${a}</li>`).join("")}
            </ul>
          ` : ''}
        </div>
      `).join("");
    } else {
      workContainer.innerHTML = '<div style="color: #94a3b8;" class="small">No work experience entries recorded in resume.</div>';
    }

    // F. Education
    const eduContainer = document.getElementById("educationContainer");
    if (education.length > 0) {
      eduContainer.innerHTML = education.map(edu => `
        <div class="p-3 mb-3 rounded-3" style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(148, 163, 184, 0.25);">
          <div class="fw-bold text-white fs-6">${edu.degree || 'Degree'}</div>
          <div class="text-primary fw-semibold small mb-1">${edu.institution || 'Institution'}</div>
          <div class="small mb-2" style="color: #cbd5e1;"><i class="bi bi-mortarboard me-1"></i> Class of ${edu.graduation_year || 'N/A'}</div>
          ${(edu.relevant_coursework && edu.relevant_coursework.length > 0) ? `
            <div class="small fw-bold text-uppercase mb-1" style="color: #cbd5e1;">Coursework:</div>
            <div class="d-flex flex-wrap gap-1">
              ${edu.relevant_coursework.map(c => `<span class="badge bg-dark text-white border border-secondary px-2 py-1">${c}</span>`).join("")}
            </div>
          ` : ''}
        </div>
      `).join("");
    } else {
      eduContainer.innerHTML = '<div style="color: #94a3b8;" class="small">No education entries recorded in resume.</div>';
    }

    // G. Projects
    const projectsContainer = document.getElementById("projectsContainer");
    if (projects.length > 0) {
      projectsContainer.innerHTML = projects.map(proj => `
        <div class="p-3 mb-3 rounded-3" style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(148, 163, 184, 0.25);">
          <div class="fw-bold text-white fs-6 mb-1">${proj.project_title || 'Project'}</div>
          <div class="text-white small mb-2" style="line-height: 1.5;">${proj.description || ''}</div>
          ${(proj.technologies_used && proj.technologies_used.length > 0) ? `
            <div class="d-flex flex-wrap gap-1 mb-2">
              ${proj.technologies_used.map(t => `<span class="skill-badge py-1 px-2" style="font-size: 0.78rem;">${t}</span>`).join("")}
            </div>
          ` : ''}
          ${(proj.contributions && proj.contributions.length > 0) ? `
            <ul class="text-white small mb-0 ps-3">
              ${proj.contributions.map(c => `<li class="mb-1">${c}</li>`).join("")}
            </ul>
          ` : ''}
        </div>
      `).join("");
    } else {
      projectsContainer.innerHTML = '<div style="color: #94a3b8;" class="small">No project entries recorded in resume.</div>';
    }

    // H. Certifications
    const certsContainer = document.getElementById("certificationsContainer");
    if (certs.length > 0) {
      certsContainer.innerHTML = certs.map(cert => `
        <div class="p-3 mb-3 rounded-3 d-flex align-items-center justify-content-between" style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(148, 163, 184, 0.25);">
          <div>
            <div class="fw-bold text-white">${cert.certification_name || 'Certification'}</div>
            <div class="small fw-medium" style="color: #cbd5e1;">${cert.issuing_organization || 'Issuer'}</div>
          </div>
          <div class="badge bg-dark border border-secondary text-white">${cert.date || 'Active'}</div>
        </div>
      `).join("");
    } else {
      certsContainer.innerHTML = '<div style="color: #94a3b8;" class="small">No certifications recorded in resume.</div>';
    }

    // I. Additional Information
    const addlContainer = document.getElementById("additionalInfoContainer");
    if (addlInfo.length > 0) {
      addlContainer.innerHTML = `
        <ul class="list-unstyled mb-0">
          ${addlInfo.map(item => `
            <li class="mb-2 text-white small d-flex align-items-start gap-2">
              <i class="bi bi-star-fill text-warning mt-1" style="font-size: 0.85rem;"></i>
              <span>${item}</span>
            </li>
          `).join("")}
        </ul>
      `;
    } else {
      addlContainer.innerHTML = '<div style="color: #94a3b8;" class="small">No additional achievements or awards noted.</div>';
    }
  }

  // ---------------------------------------------------------------------------
  // Resume History Management
  // ---------------------------------------------------------------------------
  async function loadResumeHistory() {
    if (!currentToken) return;

    try {
      const response = await fetch("/resumes", {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });

      if (!response.ok) {
        throw new Error("Failed to load resume history.");
      }

      const resumes = await response.json();
      renderHistoryTable(resumes);
    } catch (err) {
      console.warn("Could not load history:", err);
    }
  }

  function renderHistoryTable(resumes) {
    if (!resumes || resumes.length === 0) {
      historyTableBody.innerHTML = `
        <tr>
          <td colspan="4" class="text-center py-4 text-muted">
            <i class="bi bi-folder-x fs-2 d-block mb-2"></i>
            No resumes uploaded yet. Upload a resume above to get started.
          </td>
        </tr>
      `;
      return;
    }

    historyTableBody.innerHTML = resumes.map(r => {
      let statusBadge = '<span class="badge bg-success bg-opacity-25 text-success border border-success">Completed</span>';
      if (r.processing_status === "processing") {
        statusBadge = '<span class="badge bg-warning bg-opacity-25 text-warning border border-warning">Processing</span>';
      } else if (r.processing_status === "failed") {
        statusBadge = '<span class="badge bg-danger bg-opacity-25 text-danger border border-danger">Failed</span>';
      }

      const dateStr = r.created_at ? new Date(r.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'N/A';

      return `
        <tr>
          <td>
            <div class="d-flex align-items-center gap-2">
              <i class="bi bi-file-earmark-text text-primary fs-5"></i>
              <span class="fw-semibold text-white">${r.file_name}</span>
            </div>
          </td>
          <td>${statusBadge}</td>
          <td class="text-muted small">${dateStr}</td>
          <td class="text-end">
            <div class="btn-group">
              <button class="btn btn-outline-custom btn-sm view-analysis-btn" data-id="${r.id}" title="View Analysis">
                <i class="bi bi-eye text-primary"></i> View
              </button>
              <button class="btn btn-outline-custom btn-sm delete-resume-btn" data-id="${r.id}" title="Delete Resume">
                <i class="bi bi-trash text-danger"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join("");

    // Attach row action listeners
    document.querySelectorAll(".view-analysis-btn").forEach(btn => {
      btn.addEventListener("click", () => viewResumeAnalysis(btn.dataset.id));
    });

    document.querySelectorAll(".delete-resume-btn").forEach(btn => {
      btn.addEventListener("click", () => deleteResume(btn.dataset.id));
    });
  }

  async function viewResumeAnalysis(resumeId) {
    if (!currentToken) return;
    try {
      showAlert("Loading structured analysis...", "info");
      const response = await fetch(`/resumes/${resumeId}/analysis`, {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Could not retrieve analysis.");

      hideAlert();
      renderAnalysisDashboard(data.data.analysis, `Resume #${resumeId.substring(0, 8)}`);
    } catch (err) {
      showAlert(err.message, "danger");
    }
  }

  async function deleteResume(resumeId) {
    if (!confirm("Are you sure you want to permanently delete this resume and its analysis?")) {
      return;
    }

    try {
      const response = await fetch(`/resumes/${resumeId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Delete operation failed.");

      showAlert("Resume and associated analysis successfully deleted.", "success");
      loadResumeHistory();
      resultsSection.classList.add("d-none");
    } catch (err) {
      showAlert(err.message, "danger");
    }
  }

  refreshHistoryBtn?.addEventListener("click", () => {
    loadResumeHistory();
    showAlert("Resume history refreshed.", "info");
  });

  // Initial Auth Check
  initAuth();
});

