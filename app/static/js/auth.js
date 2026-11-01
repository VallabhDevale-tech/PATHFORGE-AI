/**
 * PATHFORGE AI - Production Authentication Controller
 * Handles session verification, Sign In, Sign Up, password toggles, and route redirection.
 * Communicates with the FastAPI backend (/api/auth) with Supabase SDK fallback.
 */

document.addEventListener("DOMContentLoaded", async () => {
  // Initialize Supabase Client (optional client-side instance)
  const config = window.PATHFORGE_CONFIG || {};
  let supabase = null;

  if (config.supabaseUrl && config.supabaseKey && window.supabase) {
    try {
      supabase = window.supabase.createClient(config.supabaseUrl, config.supabaseKey);
    } catch (e) {
      console.warn("Client-side Supabase SDK initialization skipped:", e);
    }
  }

  // DOM Elements
  const authAlert = document.getElementById("authAlert");
  const authAlertIcon = document.getElementById("authAlertIcon");
  const authAlertMessage = document.getElementById("authAlertMessage");

  const tabSignInBtn = document.getElementById("tabSignInBtn");
  const tabSignUpBtn = document.getElementById("tabSignUpBtn");
  const switchToSignUp = document.getElementById("switchToSignUp");
  const switchToSignIn = document.getElementById("switchToSignIn");

  const signInForm = document.getElementById("signInForm");
  const signInEmail = document.getElementById("signInEmail");
  const signInPassword = document.getElementById("signInPassword");
  const btnSignInSubmit = document.getElementById("btnSignInSubmit");
  const signInSpinner = document.getElementById("signInSpinner");
  const signInBtnText = document.getElementById("signInBtnText");
  const toggleSignInPassword = document.getElementById("toggleSignInPassword");
  const forgotPasswordLink = document.getElementById("forgotPasswordLink");

  const signUpForm = document.getElementById("signUpForm");
  const signUpFullName = document.getElementById("signUpFullName");
  const signUpEmail = document.getElementById("signUpEmail");
  const signUpPassword = document.getElementById("signUpPassword");
  const signUpConfirmPassword = document.getElementById("signUpConfirmPassword");
  const btnSignUpSubmit = document.getElementById("btnSignUpSubmit");
  const signUpSpinner = document.getElementById("signUpSpinner");
  const signUpBtnText = document.getElementById("signUpBtnText");
  const toggleSignUpPassword = document.getElementById("toggleSignUpPassword");
  const toggleSignUpConfirmPassword = document.getElementById("toggleSignUpConfirmPassword");

  // ---------------------------------------------------------------------------
  // Alert Notification Helper
  // ---------------------------------------------------------------------------
  function showAlert(message, type = "danger") {
    authAlert.className = `auth-alert auth-alert-${type} d-block`;
    authAlertMessage.textContent = message;

    if (type === "danger") {
      authAlertIcon.className = "bi bi-exclamation-triangle-fill text-danger";
    } else if (type === "success") {
      authAlertIcon.className = "bi bi-check-circle-fill text-success";
    } else {
      authAlertIcon.className = "bi bi-info-circle-fill text-info";
    }
  }

  function hideAlert() {
    authAlert.className = "auth-alert d-none";
    authAlertMessage.textContent = "";
  }

  // ---------------------------------------------------------------------------
  // 1. Check for Active Authenticated Session (Fast-path from localStorage)
  // ---------------------------------------------------------------------------
  const storedToken = localStorage.getItem("pathforge_auth_token");
  if (storedToken) {
    try {
      const payload = JSON.parse(atob(storedToken.split(".")[1]));
      if (payload.exp && payload.exp * 1000 > Date.now()) {
        window.location.replace("/dashboard");
        return;
      }
    } catch (e) {
      localStorage.removeItem("pathforge_auth_token");
    }
  }

  if (supabase) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (session && session.access_token) {
        localStorage.setItem("pathforge_auth_token", session.access_token);
        window.location.replace("/dashboard");
        return;
      }
    } catch (err) {
      console.warn("Session check error:", err);
    }
  }

  // ---------------------------------------------------------------------------
  // 2. Password Visibility Toggles
  // ---------------------------------------------------------------------------
  function setupPasswordToggle(button, input) {
    if (!button || !input) return;
    button.addEventListener("click", () => {
      const isPassword = input.type === "password";
      input.type = isPassword ? "text" : "password";
      button.innerHTML = isPassword 
        ? '<i class="bi bi-eye-slash text-light"></i>' 
        : '<i class="bi bi-eye"></i>';
    });
  }

  setupPasswordToggle(toggleSignInPassword, signInPassword);
  setupPasswordToggle(toggleSignUpPassword, signUpPassword);
  setupPasswordToggle(toggleSignUpConfirmPassword, signUpConfirmPassword);

  // Switch between tabs via footer links
  switchToSignUp?.addEventListener("click", (e) => {
    e.preventDefault();
    hideAlert();
    new bootstrap.Tab(tabSignUpBtn).show();
  });

  switchToSignIn?.addEventListener("click", (e) => {
    e.preventDefault();
    hideAlert();
    new bootstrap.Tab(tabSignInBtn).show();
  });

  // ---------------------------------------------------------------------------
  // 3. Sign In Submission (Communicates with /api/auth/login)
  // ---------------------------------------------------------------------------
  signInForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert();

    const email = signInEmail.value.trim();
    const password = signInPassword.value;

    if (!email || !password) {
      showAlert("Please enter both email address and password.", "danger");
      return;
    }

    // Set Loading State
    btnSignInSubmit.disabled = true;
    signInSpinner.classList.remove("d-none");
    signInBtnText.textContent = "Signing In...";

    try {
      // 1. Primary: FastAPI Backend endpoint
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
      });

      const result = await response.json().catch(() => ({}));

      if (!response.ok) {
        const errorDetail = result.detail || result.message || "Invalid credentials. Please try again.";
        showAlert(errorDetail, "danger");
        btnSignInSubmit.disabled = false;
        signInSpinner.classList.add("d-none");
        signInBtnText.textContent = "Sign In to PATHFORGE";
        return;
      }

      if (result.access_token) {
        localStorage.setItem("pathforge_auth_token", result.access_token);
        showAlert("Signed in successfully! Redirecting to Dashboard...", "success");
        setTimeout(() => {
          window.location.replace("/dashboard");
        }, 500);
        return;
      }

      throw new Error("No authorization token received.");

    } catch (err) {
      console.warn("Backend login error, attempting client-side fallback:", err);

      // 2. Secondary Fallback: Direct Supabase client if backend fetch failed
      if (supabase) {
        try {
          const { data, error } = await supabase.auth.signInWithPassword({
            email: email,
            password: password
          });

          if (error) {
            showAlert(error.message || "Authentication failed.", "danger");
          } else if (data && data.session) {
            localStorage.setItem("pathforge_auth_token", data.session.access_token);
            showAlert("Signed in successfully! Redirecting to Dashboard...", "success");
            setTimeout(() => {
              window.location.replace("/dashboard");
            }, 500);
            return;
          }
        } catch (sbErr) {
          showAlert(`Authentication failed: ${sbErr.message || sbErr}`, "danger");
        }
      } else {
        showAlert(`Sign in failed: ${err.message || "Network error. Please try again."}`, "danger");
      }

      btnSignInSubmit.disabled = false;
      signInSpinner.classList.add("d-none");
      signInBtnText.textContent = "Sign In to PATHFORGE";
    }
  });

  // ---------------------------------------------------------------------------
  // 4. Sign Up Submission (Communicates with /api/auth/signup)
  // ---------------------------------------------------------------------------
  signUpForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert();

    const fullName = signUpFullName.value.trim();
    const email = signUpEmail.value.trim();
    const password = signUpPassword.value;
    const confirmPassword = signUpConfirmPassword.value;

    if (!fullName) {
      showAlert("Please enter your full name.", "danger");
      signUpFullName.focus();
      return;
    }

    if (!email) {
      showAlert("Please enter a valid email address.", "danger");
      signUpEmail.focus();
      return;
    }

    if (password.length < 6) {
      showAlert("Password must be at least 6 characters long.", "danger");
      signUpPassword.focus();
      return;
    }

    if (password !== confirmPassword) {
      showAlert("Passwords do not match. Please re-enter.", "danger");
      signUpConfirmPassword.focus();
      return;
    }

    // Set Loading State
    btnSignUpSubmit.disabled = true;
    signUpSpinner.classList.remove("d-none");
    signUpBtnText.textContent = "Creating Account...";

    try {
      // 1. Primary: FastAPI Backend endpoint
      const response = await fetch("/api/auth/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          email: email,
          password: password,
          full_name: fullName
        })
      });

      const result = await response.json().catch(() => ({}));

      if (!response.ok) {
        const errorDetail = result.detail || result.message || "Registration failed. Please try again.";
        showAlert(errorDetail, "danger");
        btnSignUpSubmit.disabled = false;
        signUpSpinner.classList.add("d-none");
        signUpBtnText.textContent = "Create My Account";
        return;
      }

      // Check for immediate session
      if (result.access_token) {
        localStorage.setItem("pathforge_auth_token", result.access_token);
        showAlert("Account created successfully! Redirecting to Dashboard...", "success");
        setTimeout(() => {
          window.location.replace("/dashboard");
        }, 500);
        return;
      }

      // If confirmation email was dispatched
      showAlert("Account registered! Please check your email inbox to verify your account, then sign in.", "info");
      btnSignUpSubmit.disabled = false;
      signUpSpinner.classList.add("d-none");
      signUpBtnText.textContent = "Create My Account";

      signInEmail.value = email;
      signInPassword.value = "";
      setTimeout(() => {
        new bootstrap.Tab(tabSignInBtn).show();
        signInPassword.focus();
      }, 1200);

    } catch (err) {
      console.warn("Backend signup error, attempting client-side fallback:", err);

      // 2. Secondary Fallback: Direct Supabase client if backend fetch failed
      if (supabase) {
        try {
          const { data, error } = await supabase.auth.signUp({
            email: email,
            password: password,
            options: {
              data: {
                full_name: fullName
              }
            }
          });

          if (error) {
            showAlert(error.message || "Registration failed.", "danger");
          } else if (data && data.session) {
            localStorage.setItem("pathforge_auth_token", data.session.access_token);
            showAlert("Account created successfully! Redirecting to Dashboard...", "success");
            setTimeout(() => {
              window.location.replace("/dashboard");
            }, 500);
            return;
          } else {
            showAlert("Account registered! Please check your email to confirm, then sign in.", "info");
            setTimeout(() => {
              new bootstrap.Tab(tabSignInBtn).show();
              signInPassword.focus();
            }, 1200);
          }
        } catch (sbErr) {
          showAlert(`Registration error: ${sbErr.message || sbErr}`, "danger");
        }
      } else {
        showAlert(`Registration failed: ${err.message || "Network error. Please try again."}`, "danger");
      }

      btnSignUpSubmit.disabled = false;
      signUpSpinner.classList.add("d-none");
      signUpBtnText.textContent = "Create My Account";
    }
  });

  // ---------------------------------------------------------------------------
  // 5. Forgot Password Handler
  // ---------------------------------------------------------------------------
  forgotPasswordLink?.addEventListener("click", async (e) => {
    e.preventDefault();
    hideAlert();

    const email = signInEmail.value.trim() || prompt("Enter your account email address to receive password reset instructions:");
    if (!email) return;

    try {
      showAlert("Sending password reset instructions...", "info");
      const res = await fetch("/api/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email })
      });
      const data = await res.json().catch(() => ({}));
      showAlert(data.message || `Password reset instructions sent to ${email}.`, "success");
    } catch (err) {
      showAlert(`Reset error: ${err.message || err}`, "danger");
    }
  });
});
