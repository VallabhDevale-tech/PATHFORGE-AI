/**
 * PATHFORGE AI - Client-Side Supabase Authentication Controller
 * Handles session verification, Sign In, Sign Up, password toggles, and route redirection.
 */

document.addEventListener("DOMContentLoaded", async () => {
  // Initialize Supabase Client
  const config = window.PATHFORGE_CONFIG || {};
  let supabase = null;

  if (config.supabaseUrl && config.supabaseKey && window.supabase) {
    try {
      supabase = window.supabase.createClient(config.supabaseUrl, config.supabaseKey);
    } catch (e) {
      console.error("Failed to initialize Supabase client:", e);
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
  // 1. Check for Active Authenticated Session
  // ---------------------------------------------------------------------------
  if (supabase) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (session && session.access_token) {
        localStorage.setItem("pathforge_auth_token", session.access_token);
        // Already authenticated -> redirect to Resume Analysis
        window.location.replace("/resume-analysis");
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
  // 3. Sign In Submission
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

    if (!supabase) {
      showAlert("Authentication service is unavailable. Please check configuration.", "danger");
      return;
    }

    // Set Loading State
    btnSignInSubmit.disabled = true;
    signInSpinner.classList.remove("d-none");
    signInBtnText.textContent = "Signing In...";

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email,
        password: password
      });

      if (error) {
        let msg = error.message || "Authentication failed.";
        if (msg.toLowerCase().includes("invalid login credentials")) {
          msg = "Invalid email or password. Please verify your credentials and try again.";
        } else if (msg.toLowerCase().includes("email not confirmed")) {
          msg = "Your email address has not been confirmed yet. Please check your inbox.";
        }
        showAlert(msg, "danger");
        btnSignInSubmit.disabled = false;
        signInSpinner.classList.add("d-none");
        signInBtnText.textContent = "Sign In to PATHFORGE";
        return;
      }

      if (data && data.session) {
        localStorage.setItem("pathforge_auth_token", data.session.access_token);
        showAlert("Signed in successfully! Redirecting to Resume Analyzer...", "success");
        setTimeout(() => {
          window.location.replace("/resume-analysis");
        }, 500);
      } else {
        showAlert("Unexpected response from authentication provider.", "danger");
        btnSignInSubmit.disabled = false;
        signInSpinner.classList.add("d-none");
        signInBtnText.textContent = "Sign In to PATHFORGE";
      }

    } catch (err) {
      showAlert(`Sign in error: ${err.message || err}`, "danger");
      btnSignInSubmit.disabled = false;
      signInSpinner.classList.add("d-none");
      signInBtnText.textContent = "Sign In to PATHFORGE";
    }
  });

  // ---------------------------------------------------------------------------
  // 4. Sign Up Submission
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

    if (!supabase) {
      showAlert("Authentication service is unavailable. Please check configuration.", "danger");
      return;
    }

    // Set Loading State
    btnSignUpSubmit.disabled = true;
    signUpSpinner.classList.remove("d-none");
    signUpBtnText.textContent = "Creating Account...";

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
        let msg = error.message || "Registration failed.";
        if (msg.toLowerCase().includes("user already registered") || msg.toLowerCase().includes("already exists")) {
          msg = "An account with this email address already exists. Please sign in instead.";
        }
        showAlert(msg, "danger");
        btnSignUpSubmit.disabled = false;
        signUpSpinner.classList.add("d-none");
        signUpBtnText.textContent = "Create My Account";
        return;
      }

      // Check if session was granted immediately (email confirmation disabled or auto-confirm)
      if (data && data.session) {
        localStorage.setItem("pathforge_auth_token", data.session.access_token);
        showAlert("Account created successfully! Redirecting to Resume Analyzer...", "success");
        setTimeout(() => {
          window.location.replace("/resume-analysis");
        }, 600);
      } else {
        // Confirmation email sent
        showAlert("Account registered! If confirmation is required, please check your email inbox. You can now sign in.", "info");
        btnSignUpSubmit.disabled = false;
        signUpSpinner.classList.add("d-none");
        signUpBtnText.textContent = "Create My Account";
        
        // Switch to Sign In tab and prepopulate email
        signInEmail.value = email;
        signInPassword.value = "";
        setTimeout(() => {
          new bootstrap.Tab(tabSignInBtn).show();
          signInPassword.focus();
        }, 1200);
      }

    } catch (err) {
      showAlert(`Registration error: ${err.message || err}`, "danger");
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
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: window.location.origin
      });

      if (error) {
        showAlert(error.message, "danger");
      } else {
        showAlert(`Password reset email sent to ${email}. Please check your inbox.`, "success");
      }
    } catch (err) {
      showAlert(`Reset error: ${err.message || err}`, "danger");
    }
  });
});

