const form = document.getElementById("signupForm");
const submitBtn = document.getElementById("submitBtn");
const tooltip = document.getElementById("errorTooltip");

// Validation state object - using actual field names
const validationState = {
  full_name: false,
  email: false,
  password: false,
  confirm_password: false, // Changed to match actual field ID
};

// Utility functions for validation
const validators = {
  full_name: {
    validate: (value) => {
      const errors = [];
      if (!value.trim()) {
        errors.push("Full Name is required");
      }
      return errors;
    },
  },

  email: {
    validate: (value) => {
      const errors = [];
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

      if (!value.trim()) {
        errors.push("Email is required");
      } else {
        if (!emailRegex.test(value)) {
          errors.push("Please enter a valid email address");
        }
        if (value.length > 254) {
          errors.push("Email address is too long");
        }
      }

      return errors;
    },
  },

  password: {
    validate: (value) => {
      const errors = [];

      if (!value) {
        errors.push("Password is required");
      } else {
        if (value.length < 8) {
          errors.push("Password must be at least 8 characters long");
        }
        if (!/(?=.*[a-z])/.test(value)) {
          errors.push("Password must contain at least one lowercase letter");
        }
        if (!/(?=.*[A-Z])/.test(value)) {
          errors.push("Password must contain at least one uppercase letter");
        }
        if (!/(?=.*\d)/.test(value)) {
          errors.push("Password must contain at least one number");
        }
        if (!/(?=.*[@$!%*?&])/.test(value)) {
          errors.push(
            "Password must contain at least one special character (@$!%*?&)"
          );
        }
        if (/\s/.test(value)) {
          errors.push("Password cannot contain spaces");
        }
      }

      return errors;
    },
  },

  confirm_password: {
    // Changed to match field ID
    validate: (value, originalPassword) => {
      const errors = [];

      if (!value) {
        errors.push("Please confirm your password");
      } else if (value !== originalPassword) {
        errors.push("Passwords do not match");
      }

      return errors;
    },
  },
};

// Function to show/hide tooltip
function showTooltip(element, message) {
  const rect = element.getBoundingClientRect();
  tooltip.innerHTML = message;
  tooltip.style.left = rect.left + "px";
  tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + "px";
  tooltip.classList.add("show");
}

function hideTooltip() {
  tooltip.classList.remove("show");
}

// Function to get the correct field ID and icon ID mapping
function getFieldMapping(fieldName) {
  const mapping = {
    full_name: {
      fieldId: "full_name",
      iconId: "full-name-icon",
      errorId: "full-name-error",
    },
    email: { fieldId: "email", iconId: "email-icon", errorId: "email-error" },
    password: {
      fieldId: "password",
      iconId: "password-icon",
      errorId: "password-error",
    },
    confirm_password: {
      fieldId: "confirm_password",
      iconId: "confirm-password-icon",
      errorId: "confirm-password-error",
    },
  };
  return mapping[fieldName];
}

// Function to update validation icon
function updateValidationIcon(fieldName, isValid, errors = []) {
  const fieldMapping = getFieldMapping(fieldName);
  if (!fieldMapping) return;

  const icon = document.getElementById(fieldMapping.iconId);
  const input = document.getElementById(fieldMapping.fieldId);

  if (!icon || !input) return;

  // Clear existing classes and content
  icon.className = "validation-icon";
  icon.innerHTML = "";

  if (input.value.trim() === "") {
    // No input, no icon
    input.classList.remove("valid", "invalid");
    return;
  }

  if (isValid) {
    icon.classList.add("valid");
    icon.innerHTML = '<i class="fa fa-check-circle"></i>';
    input.classList.remove("invalid");
    input.classList.add("valid");

    // Remove tooltip event listeners for valid fields
    if (icon.showTooltipHandler) {
      icon.removeEventListener("mouseenter", icon.showTooltipHandler);
      icon.removeEventListener("mouseleave", hideTooltip);
    }
  } else {
    icon.classList.add("invalid");
    icon.innerHTML = '<i class="fa fa-exclamation-circle"></i>';
    input.classList.remove("valid");
    input.classList.add("invalid");

    // Add tooltip for errors
    const errorMessage = errors.join("<br>");
    icon.showTooltipHandler = () => showTooltip(icon, errorMessage);

    icon.addEventListener("mouseenter", icon.showTooltipHandler);
    icon.addEventListener("mouseleave", hideTooltip);
  }
}

// Function to display errors
function displayErrors(fieldName, errors) {
  const fieldMapping = getFieldMapping(fieldName);
  if (!fieldMapping) return;

  const errorDiv = document.getElementById(fieldMapping.errorId);
  if (!errorDiv) return;

  const isValid = errors.length === 0;

  // Update validation state
  validationState[fieldName] = isValid;

  // Update validation icon
  updateValidationIcon(fieldName, isValid, errors);

  // Clear existing errors
  errorDiv.innerHTML = "";
  errorDiv.classList.remove("show");

  if (errors.length > 0) {
    // Show errors with animation
    errorDiv.innerHTML = errors
      .map((error) => `<span class="error-text">${error}</span>`)
      .join("");
    setTimeout(() => {
      errorDiv.classList.add("show");
    }, 10);
  }

  updateSubmitButton();
}

// Function to update submit button state
function updateSubmitButton() {
  const allValid = Object.values(validationState).every(
    (state) => state === true
  );
  const allFieldsFilled = [
    "full_name",
    "email",
    "password",
    "confirm_password",
  ].every((field) => {
    const input = document.getElementById(field);
    return input && input.value.trim() !== "";
  });

  submitBtn.disabled = !(allValid && allFieldsFilled);

  if (allValid && allFieldsFilled) {
    submitBtn.style.backgroundColor = "#28a745";
    submitBtn.style.cursor = "pointer";
    submitBtn.style.opacity = "1";
  } else {
    submitBtn.style.backgroundColor = "#6c757d";
    submitBtn.style.cursor = "not-allowed";
    submitBtn.style.opacity = "0.6";
  }
}

// Debounce function for better performance
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Create debounced validation functions
const debouncedValidateFullName = debounce((value) => {
  const errors = validators.full_name.validate(value);
  displayErrors("full_name", errors);
}, 300);

const debouncedValidateEmail = debounce((value) => {
  const errors = validators.email.validate(value);
  displayErrors("email", errors);
}, 300);

const debouncedValidatePassword = debounce((value) => {
  const passwordErrors = validators.password.validate(value);
  displayErrors("password", passwordErrors);

  // Re-validate confirm password if it has a value
  const confirmPasswordValue =
    document.getElementById("confirm_password").value;
  if (confirmPasswordValue) {
    const confirmErrors = validators.confirm_password.validate(
      confirmPasswordValue,
      value
    );
    displayErrors("confirm_password", confirmErrors);
  }
}, 300);

const debouncedValidateConfirmPassword = debounce((value, originalPassword) => {
  const errors = validators.confirm_password.validate(value, originalPassword);
  displayErrors("confirm_password", errors);
}, 300);

// Real-time validation event listeners
document.getElementById("full_name").addEventListener("input", function () {
  debouncedValidateFullName(this.value);
});

document.getElementById("full_name").addEventListener("blur", function () {
  const errors = validators.full_name.validate(this.value);
  displayErrors("full_name", errors);
});

document.getElementById("email").addEventListener("input", function () {
  debouncedValidateEmail(this.value);
});

document.getElementById("email").addEventListener("blur", function () {
  const errors = validators.email.validate(this.value);
  displayErrors("email", errors);
});

document.getElementById("password").addEventListener("input", function () {
  debouncedValidatePassword(this.value);
});

document.getElementById("password").addEventListener("blur", function () {
  const passwordValue = this.value;
  const confirmPasswordValue =
    document.getElementById("confirm_password").value;

  // Validate password
  const passwordErrors = validators.password.validate(passwordValue);
  displayErrors("password", passwordErrors);

  // Re-validate confirm password if it has a value
  if (confirmPasswordValue) {
    const confirmErrors = validators.confirm_password.validate(
      confirmPasswordValue,
      passwordValue
    );
    displayErrors("confirm_password", confirmErrors);
  }
});

document
  .getElementById("confirm_password")
  .addEventListener("input", function () {
    const passwordValue = document.getElementById("password").value;
    debouncedValidateConfirmPassword(this.value, passwordValue);
  });

document
  .getElementById("confirm_password")
  .addEventListener("blur", function () {
    const passwordValue = document.getElementById("password").value;
    const errors = validators.confirm_password.validate(
      this.value,
      passwordValue
    );
    displayErrors("confirm_password", errors);
  });

// Form submission handler
form.addEventListener("submit", function (e) {
  // Validate all fields before submission
  const fullName = document.getElementById("full_name").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirm_password").value;

  const fullNameErrors = validators.full_name.validate(fullName);
  const emailErrors = validators.email.validate(email);
  const passwordErrors = validators.password.validate(password);
  const confirmPasswordErrors = validators.confirm_password.validate(
    confirmPassword,
    password
  );

  displayErrors("full_name", fullNameErrors);
  displayErrors("email", emailErrors);
  displayErrors("password", passwordErrors);
  displayErrors("confirm_password", confirmPasswordErrors);

  // If any validation fails, prevent submission
  if (
    fullNameErrors.length > 0 ||
    emailErrors.length > 0 ||
    passwordErrors.length > 0 ||
    confirmPasswordErrors.length > 0
  ) {
    e.preventDefault();

    // Scroll to first error
    const firstError = document.querySelector(".error-message.show");
    if (firstError) {
      firstError.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    return false;
  }

  // Show loading state
  submitBtn.innerHTML =
    '<i class="fa fa-spinner fa-spin"></i> Creating Account...';
  submitBtn.disabled = true;

  // If all validations pass, allow form submission to backend
  return true;
});

// Hide tooltip when clicking elsewhere
document.addEventListener("click", function (e) {
  if (!e.target.closest(".validation-icon")) {
    hideTooltip();
  }
});

// Initialize button state
updateSubmitButton();

// Clear validation when form is reset
form.addEventListener("reset", function () {
  Object.keys(validationState).forEach((key) => {
    validationState[key] = false;
    displayErrors(key, []);
  });
  updateSubmitButton();
});

// Debug function to check if all elements exist
function debugElements() {
  const elements = [
    "full_name",
    "email",
    "password",
    "confirm_password",
    "full-name-icon",
    "email-icon",
    "password-icon",
    "confirm-password-icon",
    "full-name-error",
    "email-error",
    "password-error",
    "confirm-password-error",
  ];

  elements.forEach((id) => {
    const element = document.getElementById(id);
    if (!element) {
      console.error(`Element with ID '${id}' not found`);
    } else {
      console.log(`Element '${id}' found`);
    }
  });
}