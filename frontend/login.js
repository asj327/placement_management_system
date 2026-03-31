let currentRole = 'student'; // Default role

const studentTab = document.getElementById('student-tab');
const companyTab = document.getElementById('company-tab');
const submitBtn = document.getElementById('submit-btn');
const loginForm = document.getElementById('login-form');
const messageDisplay = document.getElementById('message');

// Switch to Student mode
studentTab.addEventListener('click', () => {
    currentRole = 'student';
    studentTab.classList.add('active');
    companyTab.classList.remove('active');
    submitBtn.innerText = 'Login as Student';
});

// Switch to Company mode
companyTab.addEventListener('click', () => {
    currentRole = 'company';
    companyTab.classList.add('active');
    studentTab.classList.remove('active');
    submitBtn.innerText = 'Login as Company';
});

// Handle Form Submission
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Show a loading state
    submitBtn.innerText = "Authenticating...";
    submitBtn.disabled = true;

    try {
        // --- API CONNECTION ---
        // Replace 'https://api.yourproject.com/login' with your real URL
        const response = await fetch('https://api.example.com/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: email,
                password: password,
                role: currentRole // Sends whether it's 'student' or 'company'
            })
        });

        const data = await response.json();

        if (response.ok) {
    messageDisplay.style.color = "green";
    messageDisplay.innerText = "Login Successful! Redirecting...";

    // 1. Store the user's role and ID (optional but helpful for the dashboard)
    localStorage.setItem('userRole', currentRole);
    localStorage.setItem('userId', data.userId); // Assuming your teammate sends the ID

    // 2. Redirect based on the role
    setTimeout(() => {
        if (currentRole === 'student') {
            window.location.href = 'student.html';
        } else {
            window.location.href = 'company.html';
        }
    }, 1500); // 1.5 second delay so the user sees the success message
} else {
            throw new Error(data.message || "Invalid credentials");
        }
    } catch (error) {
        messageDisplay.style.color = "red";
        messageDisplay.innerText = error.message;
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = `Login as ${currentRole.charAt(0).toUpperCase() + currentRole.slice(1)}`;
    }
});