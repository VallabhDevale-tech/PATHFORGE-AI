/**
 * PATHFORGE AI - Application Shell & 3D Interactive Controller
 * Handles global session, unified sidebar, mobile drawers, 3D card tilt physics,
 * and seamless navigation.
 */

(function () {
  'use strict';

  document.addEventListener("DOMContentLoaded", () => {
    initAppShell();
    init3DTilt();
  });

  function initAppShell() {
    const config = window.PATHFORGE_CONFIG || {};
    let supabaseClient = null;

    if (config.supabaseUrl && config.supabaseKey && window.supabase) {
      try {
        supabaseClient = window.supabase.createClient(config.supabaseUrl, config.supabaseKey);
      } catch (e) {
        console.warn("Supabase init note:", e);
      }
    }

    // Sidebar Mobile Controls
    const sidebar = document.getElementById("appSidebar");
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebarCloseBtn = document.getElementById("sidebarCloseBtn");
    const sidebarBackdrop = document.getElementById("sidebarBackdrop");

    if (sidebarToggle && sidebar && sidebarBackdrop) {
      sidebarToggle.addEventListener("click", () => {
        sidebar.classList.toggle("show");
        sidebarBackdrop.classList.toggle("show");
      });

      const closeSidebar = () => {
        sidebar.classList.remove("show");
        sidebarBackdrop.classList.remove("show");
      };

      if (sidebarCloseBtn) sidebarCloseBtn.addEventListener("click", closeSidebar);
      sidebarBackdrop.addEventListener("click", closeSidebar);
    }

    // User State Sync
    const currentToken = localStorage.getItem("pathforge_auth_token");
    const topbarUserEmail = document.getElementById("topbarUserEmail");
    const topbarUserAvatar = document.getElementById("topbarUserAvatar");
    const sidebarUserEmail = document.getElementById("sidebarUserEmail");
    const userEmailText = document.getElementById("userEmailText");
    const logoutButtons = document.querySelectorAll("#logoutBtn, .action-logout");

    if (currentToken) {
      try {
        const payload = JSON.parse(atob(currentToken.split(".")[1]));
        const email = payload.email || "Candidate";
        const initial = (email.charAt(0) || "P").toUpperCase();

        if (topbarUserEmail) topbarUserEmail.textContent = email;
        if (sidebarUserEmail) sidebarUserEmail.textContent = email;
        if (userEmailText) userEmailText.textContent = email;
        if (topbarUserAvatar) topbarUserAvatar.textContent = initial;
      } catch (err) {
        console.debug("Token parsing fallback:", err);
      }
    }

    // Logout Handler across all pages
    logoutButtons.forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.preventDefault();
        try {
          if (supabaseClient) {
            await supabaseClient.auth.signOut();
          }
        } catch (err) {}
        localStorage.removeItem("pathforge_auth_token");
        window.location.replace("/");
      });
    });
  }

  // ---------------------------------------------------------------------------
  // Premium 3D Perspective Tilt Physics (Zero-dependency requestAnimationFrame)
  // ---------------------------------------------------------------------------
  function init3DTilt() {
    // Check if user prefers reduced motion
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return;
    }

    const cards = document.querySelectorAll(".card-3d, .glass-card-elevated, .feature-card-3d");

    cards.forEach(card => {
      let isHovered = false;

      card.addEventListener("mouseenter", () => {
        isHovered = true;
      });

      card.addEventListener("mousemove", (e) => {
        if (!isHovered) return;
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const deltaX = (x - centerX) / centerX; // -1 to 1
        const deltaY = (y - centerY) / centerY; // -1 to 1

        const maxTilt = 6; // Max 6 degrees tilt
        const rotateY = deltaX * maxTilt;
        const rotateX = -deltaY * maxTilt;

        requestAnimationFrame(() => {
          card.style.transform = `perspective(1000px) translateY(-5px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg)`;
        });
      });

      card.addEventListener("mouseleave", () => {
        isHovered = false;
        requestAnimationFrame(() => {
          card.style.transform = "";
        });
      });
    });
  }

  // Expose global notification toast helper
  window.PathForgeUI = {
    showToast: function (message, type = "info") {
      let toastContainer = document.getElementById("pathforgeToastContainer");
      if (!toastContainer) {
        toastContainer = document.createElement("div");
        toastContainer.id = "pathforgeToastContainer";
        toastContainer.style.cssText = "position: fixed; top: 20px; right: 20px; z-index: 1090; display: flex; flex-direction: column; gap: 10px; max-width: 360px;";
        document.body.appendChild(toastContainer);
      }

      const toast = document.createElement("div");
      const iconClass = type === "success" 
        ? "bi-check-circle-fill text-success" 
        : type === "danger" 
          ? "bi-exclamation-triangle-fill text-danger" 
          : "bi-info-circle-fill text-primary";

      toast.className = "glass-card p-3 d-flex align-items-center gap-3 shadow-lg border";
      toast.style.cssText = "background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(12px); border-radius: 12px; animation: slideInRight 0.3s cubic-bezier(0.16, 1, 0.3, 1);";
      toast.innerHTML = `
        <i class="bi ${iconClass} fs-4"></i>
        <div class="small fw-medium text-dark flex-grow-1">${message}</div>
        <button type="button" class="btn-close btn-close-sm" aria-label="Close"></button>
      `;

      toast.querySelector(".btn-close").addEventListener("click", () => {
        toast.remove();
      });

      toastContainer.appendChild(toast);
      setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(20px)";
        toast.style.transition = "all 0.3s ease";
        setTimeout(() => toast.remove(), 300);
      }, 4000);
    }
  };

})();
