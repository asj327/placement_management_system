let currentRole = 'student';

function switchRole(role) {
    currentRole = role;
    // Update Toggle Buttons
    document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    // Show/Hide relevant sections
    document.getElementById('student-fields').style.display = (role === 'student') ? 'block' : 'none';
    document.getElementById('company-fields').style.display = (role === 'company') ? 'block' : 'none';
}

document.getElementById('signup-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const statusMsg = document.getElementById('status-msg');
    
    // Gather common data
    const payload = {
        role: currentRole,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

    // Gather role-specific data based on the DB schema
    if (currentRole === 'student') {
        payload.first_name = document.getElementById('first_name').value;
        payload.last_name = document.getElementById('last_name').value;
        payload.department = document.getElementById('department').value;
        payload.cgpa = document.getElementById('cgpa').value;
        payload.phone = document.getElementById('phone').value;
    } else {
        payload.company_name = document.getElementById('company_name').value;
        payload.location = document.getElementById('location').value;
        payload.website = document.getElementById('website').value;
        payload.description = document.getElementById('description').value;
    }

    try {
        statusMsg.innerText = "Processing registration...";
        
        const response = await fetch('https://api.example.com/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            statusMsg.style.color = "green";
            statusMsg.innerText = "Account created! Redirecting to login...";
            setTimeout(() => window.location.href = 'login.html', 2000);
        } else {
            const err = await response.json();
            throw new Error(err.message || "Registration failed");
        }
    } catch (error) {
        statusMsg.style.color = "red";
        statusMsg.innerText = error.message;
    }
});