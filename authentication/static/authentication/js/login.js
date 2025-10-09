const form = document.getElementById("loginForm");
const submitBtn = document.getElementById("submitBtn");
const tooltip = document.getElementById("errorTooltip");


// Validation state object
const validationState = {
 email: false,
 password: false,
};


// Utility functions for validation
const validators = {
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
       // Less strict validation for login - just check basic requirements
       if (value.length > 128) {
         errors.push("Password is too long");
       }
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
   email: { fieldId: "email", iconId: "email-icon", errorId: "email-error" },
   password: {
     fieldId: "password",
     iconId: "password-icon",
     errorId: "password-error",
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
 const allFieldsFilled = ["email", "password"].every((field) => {
   const input = document.getElementById(field);
   return input && input.value.trim() !== "";
 });


 submitBtn.disabled = !(allValid && allFieldsFilled);


 if (allValid && allFieldsFilled) {
   submitBtn.style.backgroundColor = "#007bff";
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
const debouncedValidateEmail = debounce((value) => {
 const errors = validators.email.validate(value);
 displayErrors("email", errors);
}, 300);


const debouncedValidatePassword = debounce((value) => {
 const errors = validators.password.validate(value);
 displayErrors("password", errors);
}, 300);


// Real-time validation event listeners
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
 const errors = validators.password.validate(this.value);
 displayErrors("password", errors);
});


// Enhanced form submission with loading state and validation
form.addEventListener("submit", function (e) {
 // Validate all fields before submission
 const email = document.getElementById("email").value;
 const password = document.getElementById("password").value;


 const emailErrors = validators.email.validate(email);
 const passwordErrors = validators.password.validate(password);


 displayErrors("email", emailErrors);
 displayErrors("password", passwordErrors);


 // If any validation fails, prevent submission
 if (emailErrors.length > 0 || passwordErrors.length > 0) {
   e.preventDefault();


   // Scroll to first error
   const firstError = document.querySelector(".error-message.show");
   if (firstError) {
     firstError.scrollIntoView({ behavior: "smooth", block: "center" });
   }


   // Shake animation for invalid form
   form.style.animation = "shake 0.5s ease-in-out";
   setTimeout(() => {
     form.style.animation = "";
   }, 500);


   return false;
 }


 // Show loading state
 const originalText = submitBtn.innerHTML;
 submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Signing In...';
 submitBtn.disabled = true;


 // Add timeout for better UX (remove in production if using real backend)
 setTimeout(() => {
   // Reset button if form doesn't redirect (for demo purposes)
   // In real app, this won't be needed as page will redirect
   if (document.contains(submitBtn)) {
     submitBtn.innerHTML = originalText;
     submitBtn.disabled = false;
   }
 }, 3000);


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


// Enter key handling for better UX
document.addEventListener("keydown", function (e) {
 if (e.key === "Enter" && e.target.tagName === "INPUT") {
   const inputs = Array.from(form.querySelectorAll("input[required]"));
   const currentIndex = inputs.indexOf(e.target);


   if (currentIndex < inputs.length - 1) {
     e.preventDefault();
     inputs[currentIndex + 1].focus();
   } else {
     // Last field, try to submit if valid
     if (!submitBtn.disabled) {
       form.requestSubmit();
     }
   }
 }
});


// Auto-focus first empty field on page load
document.addEventListener("DOMContentLoaded", function () {
 const firstInput = document.getElementById("email");
 if (firstInput && !firstInput.value) {
   firstInput.focus();
 }
});


// Add shake animation for form errors
const shakeCSS = `
@keyframes shake {
   0%, 100% { transform: translateX(0); }
   10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
   20%, 40%, 60%, 80% { transform: translateX(5px); }
}
`;


// Inject shake animation CSS
const style = document.createElement("style");
style.textContent = shakeCSS;
document.head.appendChild(style);


// Remember email functionality (optional)
function rememberEmail() {
 const emailInput = document.getElementById("email");
 const savedEmail = localStorage.getItem("loginEmail");


 if (savedEmail && !emailInput.value) {
   emailInput.value = savedEmail;
   emailInput.dispatchEvent(new Event("input"));
 }


 emailInput.addEventListener("blur", function () {
   if (this.value && validators.email.validate(this.value).length === 0) {
     localStorage.setItem("loginEmail", this.value);
   }
 });
}


// Initialize remember email functionality
rememberEmail();


// Debug function to check if all elements exist
function debugElements() {
 const elements = [
   "email",
   "password",
   "email-icon",
   "password-icon",
   "email-error",
   "password-error",
   "loginForm",
   "submitBtn",
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

