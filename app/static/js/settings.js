/**
 * PATHFORGE AI - Platform Settings Client Controller
 * Manages study schedule parameters, notification preferences, and local cache controls.
 */

document.addEventListener("DOMContentLoaded", () => {
  const currentToken = localStorage.getItem("pathforge_auth_token") || "";

  if (!currentToken) {
    window.location.replace("/login");
    return;
  }

  // Load saved preferences from localStorage
  const savedHours = localStorage.getItem("pathforge_study_hours") || "10";
  const savedDuration = localStorage.getItem("pathforge_roadmap_weeks") || "8";
  const savedWorkMode = localStorage.getItem("pathforge_work_mode") || "Any";

  const settingHours = document.getElementById("settingHoursPerWeek");
  const settingDuration = document.getElementById("settingRoadmapDuration");
  const settingWorkMode = document.getElementById("settingWorkMode");

  if (settingHours) settingHours.value = savedHours;
  if (settingDuration) settingDuration.value = savedDuration;
  if (settingWorkMode) settingWorkMode.value = savedWorkMode;

  // Handle Form Submission
  const form = document.getElementById("learningScheduleForm");
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      localStorage.setItem("pathforge_study_hours", settingHours.value);
      localStorage.setItem("pathforge_roadmap_weeks", settingDuration.value);
      localStorage.setItem("pathforge_work_mode", settingWorkMode.value);

      if (window.PathForgeUI) {
        window.PathForgeUI.showToast("Learning preferences saved successfully!", "success");
      } else {
        alert("Learning preferences saved successfully!");
      }
    });
  }

  // Clear Local Cache
  const clearBtn = document.getElementById("clearLocalCacheBtn");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      const confirmClear = confirm("This will reset your temporary local skill overrides and cache. Your verified database records will remain secure. Proceed?");
      if (confirmClear) {
        const token = localStorage.getItem("pathforge_auth_token");
        localStorage.clear();
        if (token) localStorage.setItem("pathforge_auth_token", token);
        if (window.PathForgeUI) {
          window.PathForgeUI.showToast("Local cache cleared.", "info");
        }
        setTimeout(() => window.location.reload(), 500);
      }
    });
  }

  // Sign out button
  const signOutBtn = document.getElementById("settingsSignOutBtn");
  if (signOutBtn) {
    signOutBtn.addEventListener("click", () => {
      const logoutBtn = document.getElementById("logoutBtn");
      if (logoutBtn) logoutBtn.click();
    });
  }
});
