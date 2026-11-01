/**
 * PATHFORGE AI - Candidate Profile Client Script
 * Fetches verified profile facts, skills, education, and career alignment.
 */

document.addEventListener("DOMContentLoaded", async () => {
  const currentToken = localStorage.getItem("pathforge_auth_token") || "";

  if (!currentToken) {
    window.location.replace("/login");
    return;
  }

  // Populate basic user info from JWT
  try {
    const payload = JSON.parse(atob(currentToken.split(".")[1]));
    const email = payload.email || "Candidate";
    const name = email.split("@")[0];
    const capitalized = name.charAt(0).toUpperCase() + name.slice(1);

    const emailEl = document.getElementById("profEmail");
    const nameEl = document.getElementById("profFullName");
    const avatarEl = document.getElementById("profAvatar");

    if (emailEl) emailEl.textContent = email;
    if (nameEl) nameEl.textContent = capitalized;
    if (avatarEl) avatarEl.textContent = capitalized.charAt(0);
  } catch (e) {}

  // Fetch telemetry
  fetchTargetRole();
  fetchCandidateProfile();
  fetchOverviewMetrics();

  async function fetchTargetRole() {
    try {
      const res = await fetch("/careers/selected", {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();
      const el = document.getElementById("profTargetCareer");
      if (res.ok && data.status === "success" && data.has_selection && data.data) {
        if (el) el.textContent = data.data.career_title || "Full Stack Developer";
      } else {
        if (el) el.textContent = "Full Stack Developer (Default)";
      }
    } catch (e) {}
  }

  async function fetchOverviewMetrics() {
    try {
      const res = await fetch("/adaptive/overview", {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();
      if (res.ok && data.status === "success" && data.data) {
        const m = data.data;
        const roadPct = document.getElementById("profRoadmapPct");
        const projCount = document.getElementById("profProjectsCount");
        const quizScore = document.getElementById("profQuizScore");

        if (roadPct) roadPct.textContent = `${m.roadmap_completion_pct || m.roadmap_progress_percentage || 0}%`;
        if (projCount) projCount.textContent = m.completed_projects_count || m.completed_projects || 0;
        if (quizScore) quizScore.textContent = `${m.average_assessment_score || m.assessment_average_score || 0}%`;
      }
    } catch (e) {}
  }

  async function fetchCandidateProfile() {
    try {
      const res = await fetch("/skills/preview-profile", {
        headers: { "Authorization": `Bearer ${currentToken}` }
      });
      const data = await res.json();

      const skillsContainer = document.getElementById("profSkillsChipsContainer");
      const eduContainer = document.getElementById("profEducationContainer");
      const projContainer = document.getElementById("profProjectsContainer");

      if (res.ok && data.status === "success" && data.has_resume) {
        const profile = data.profile || data;

        // Skills
        const skills = profile.profile_skills || [];
        if (skillsContainer) {
          if (skills.length > 0) {
            skillsContainer.innerHTML = skills.map(s => `
              <div class="d-inline-flex align-items-center gap-2 p-2 px-3 rounded-pill bg-white border shadow-xs">
                <span class="fw-bold small text-dark">${escapeHtml(s.name)}</span>
                <span class="badge bg-primary-subtle text-primary" style="font-size: 0.72rem;">Level ${s.level}</span>
              </div>
            `).join("");
          } else {
            skillsContainer.innerHTML = `<span class="text-muted small">No verified skills found. Upload a resume to populate your profile.</span>`;
          }
        }

        // Education
        const edu = profile.education || [];
        if (eduContainer) {
          if (edu.length > 0) {
            eduContainer.innerHTML = edu.map(e => `
              <div class="p-3 rounded-3 bg-light border">
                <div class="fw-bold text-dark">${escapeHtml(e.degree || 'Degree Program')}</div>
                <div class="text-muted small">${escapeHtml(e.institution || 'University')} &bull; ${escapeHtml(e.graduation_year || '')}</div>
                ${e.relevant_coursework ? `<div class="text-muted small mt-1"><span class="fw-semibold">Coursework:</span> ${escapeHtml(Array.isArray(e.relevant_coursework) ? e.relevant_coursework.join(', ') : e.relevant_coursework)}</div>` : ''}
              </div>
            `).join("");
          } else {
            eduContainer.innerHTML = `<span class="text-muted small">No formal education records parsed.</span>`;
          }
        }

        // Projects
        const projs = profile.projects || [];
        if (projContainer) {
          if (projs.length > 0) {
            projContainer.innerHTML = projs.map(p => `
              <div class="p-3 rounded-3 bg-light border">
                <div class="fw-bold text-dark">${escapeHtml(p.project_title || 'Project')}</div>
                <div class="text-muted small mt-1">${escapeHtml(p.description || '')}</div>
                ${p.technologies_used ? `
                  <div class="d-flex flex-wrap gap-1 mt-2">
                    ${(Array.isArray(p.technologies_used) ? p.technologies_used : []).map(t => `<span class="badge bg-white border text-dark">${escapeHtml(t)}</span>`).join('')}
                  </div>
                ` : ''}
              </div>
            `).join("");
          } else {
            projContainer.innerHTML = `<span class="text-muted small">No projects found in resume.</span>`;
          }
        }

      } else {
        if (skillsContainer) skillsContainer.innerHTML = `<span class="text-muted small">No analyzed resume found. <a href="/resume-analysis" class="text-primary fw-semibold">Upload your resume</a> to unlock your verified profile.</span>`;
        if (eduContainer) eduContainer.innerHTML = `<span class="text-muted small">Awaiting resume upload.</span>`;
        if (projContainer) projContainer.innerHTML = `<span class="text-muted small">Awaiting resume upload.</span>`;
      }
    } catch (e) {
      console.debug("Profile fetch error:", e);
    }
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
