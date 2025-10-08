let users = []; // Temporarily store users

form.addEventListener('submit', function(e) {
    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const email = document.getElementById('email').value.trim();

    const errors = [];

    if (!username) errors.push("Username required.");
    if (password.length < 6) errors.push("Password too short.");
    if (password !== confirmPassword) errors.push("Passwords do not match.");

    const errorDiv = document.getElementById('errors');
    errorDiv.innerHTML = '';
    if (errors.length > 0) {
        errors.forEach(err => {
            const p = document.createElement('p');
            p.textContent = err;
            errorDiv.appendChild(p);
        });
        return;
    }

    // Frontend-only signup success
    users.push({ username, email, password }); // Store temporarily
    alert("Signup successful!");
    form.reset();
});