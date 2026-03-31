// Add this to the very top of student.js and company.js
if (!localStorage.getItem('userRole')) {
    window.location.href = 'login.html';
}

// Function to switch between Dashboard tabs
function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabId).classList.add('active');
    // Use event.currentTarget safely
    if (event) event.currentTarget.classList.add('active');
}

// 1. Fetch Profile Data
async function fetchProfile() {
    try {
        /* --- MOCK DATA FOR TESTING --- */
        const student = {
            first_name: "Jane",
            department: "Computer Science",
            cgpa: "9.2",
            email: "jane.doe@university.edu",
            phone: "+1 987-654-3210"
        };

        // When your teammate provides the URL, uncomment the lines below:
        /*
        const response = await fetch('https://api.example.com/student/profile', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
        });
        const student = await response.json();
        */

        document.getElementById('student-name').innerText = student.first_name;
        document.getElementById('p-dept').innerText = student.department;
        document.getElementById('p-cgpa').innerText = student.cgpa;
        document.getElementById('p-email').innerText = student.email;
        document.getElementById('p-phone').innerText = student.phone || 'Not provided';
    } catch (err) { 
        console.error("Error fetching profile:", err); 
    }
}

// 2. Fetch All Jobs
async function fetchJobs() {
    try {
        /* --- MOCK DATA FOR TESTING --- */
        const jobs = [
            { job_id: 101, job_title: "Frontend Intern", job_type: "Internship", location: "Remote", eligibility_cgpa: 7.5 },
            { job_id: 102, job_title: "Backend Engineer", job_type: "Full-Time", location: "New York", eligibility_cgpa: 8.5 }
        ];

        const container = document.getElementById('jobs-list');
        container.innerHTML = jobs.map(job => `
            <div class="job-card">
                <h3>${job.job_title}</h3>
                <span class="job-tag">${job.job_type}</span>
                <span class="job-tag">📍 ${job.location}</span>
                <p style="margin: 10px 0; font-size: 0.9rem;">Min CGPA: ${job.eligibility_cgpa}</p>
                <button class="apply-btn" onclick="applyForJob(${job.job_id})">Apply Now</button>
            </div>
        `).join('');
    } catch (err) { console.error("Error fetching jobs"); }
}

// 3. Fetch My Applications
async function fetchMyApplications() {
    try {
        /* --- MOCK DATA FOR TESTING --- */
        const apps = [
            { job_title: "UX Designer", applied_date: "2023-10-25", status: "Pending" },
            { job_title: "System Admin", applied_date: "2023-10-20", status: "Selected" }
        ];

        const list = document.getElementById('applied-list');
        list.innerHTML = apps.map(app => `
            <tr>
                <td><strong>${app.job_title}</strong></td>
                <td>${app.applied_date}</td>
                <td><span class="status-${app.status}">${app.status}</span></td>
            </tr>
        `).join('');
    } catch (err) { console.error("Error fetching applications"); }
}

// 4. Submit New Application
async function applyForJob(jobId) {
    console.log("Applying for job ID:", jobId);
    alert("Application Submitted for Job #" + jobId);
    // In real use, this will send a POST request to the API
}

// Initial Load
window.onload = () => {
    fetchProfile();
    fetchJobs();
    fetchMyApplications();
};



function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}