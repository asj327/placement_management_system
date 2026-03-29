/*/ Add this to the very top of student.js and company.js
if (!localStorage.getItem('userRole')) {
    window.location.href = 'login.html';
}*/

function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    if (event) event.currentTarget.classList.add('active');
}

// 1. Handle Job Posting
document.getElementById('job-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Prepare data based on the 'jobs' table schema
    const jobData = {
        job_title: document.getElementById('job_title').value,
        job_type: document.getElementById('job_type').value,
        location: document.getElementById('location').value,
        salary: document.getElementById('salary').value,
        eligibility_cgpa: document.getElementById('eligibility_cgpa').value,
        deadline: document.getElementById('deadline').value,
        job_description: document.getElementById('job_description').value
    };

    console.log("Sending Job Data to API:", jobData);
    alert("Job Posted Successfully! (Mocked)");
    e.target.reset(); // Clear form
});

// 2. Fetch Applicants (Dummy Data)
async function fetchApplicants() {
    // This dummy data joins Student info with Application status
    const dummyApplicants = [
        { 
            app_id: 1, 
            name: "Jane Doe", 
            job: "Frontend Intern", 
            cgpa: 9.2, 
            resume: "resume1.pdf", 
            status: "Pending" 
        },
        { 
            app_id: 2, 
            name: "John Smith", 
            job: "Backend Engineer", 
            cgpa: 8.8, 
            resume: "resume2.pdf", 
            status: "Selected" 
        }
    ];

    const list = document.getElementById('applicant-list');
    list.innerHTML = dummyApplicants.map(app => `
        <tr>
            <td><strong>${app.name}</strong></td>
            <td>${app.job}</td>
            <td>${app.cgpa}</td>
            <td><a href="#" class="resume-link">View PDF</a></td>
            <td><span class="status-${app.status}">${app.status}</span></td>
            <td>
                <select class="status-select" onchange="updateStatus(${app.app_id}, this.value)">
                    <option value="Pending" ${app.status === 'Pending' ? 'selected' : ''}>Pending</option>
                    <option value="Selected" ${app.status === 'Selected' ? 'selected' : ''}>Selected</option>
                    <option value="Rejected" ${app.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
                </select>
            </td>
        </tr>
    `).join('');
}

// 3. Update Status Logic
async function updateStatus(applicationId, newStatus) {
    console.log(`Updating Application #${applicationId} to ${newStatus}`);
    
    // API Call would go here:
    // await fetch(`/api/applications/${applicationId}`, { method: 'PATCH', body: { status: newStatus } });
    
    alert(`Status changed to ${newStatus}`);
    fetchApplicants(); // Refresh UI
}

// 1. Fetch only jobs posted by this company
async function fetchCompanyJobs() {
    try {
        /* --- MOCK DATA FOR TESTING --- */
        const myJobs = [
            { job_id: 101, job_title: "Frontend Intern", deadline: "2023-12-01", status: "Active" },
            { job_id: 102, job_title: "Backend Engineer", deadline: "2023-11-15", status: "Expired" }
        ];

        // Real API call would look like: 
        // const response = await fetch(`${CONFIG.BASE_URL}/company/my-jobs`, { headers: getAuthHeaders() });
        // const myJobs = await response.json();

        const container = document.getElementById('company-jobs-list');
        container.innerHTML = myJobs.map(job => `
            <div class="job-card">
                <h3>${job.job_title}</h3>
                <p><strong>Deadline:</strong> ${job.deadline}</p>
                <p><strong>Status:</strong> <span class="job-status-${job.status.toLowerCase()}">${job.status}</span></p>
                <div style="margin-top: 10px;">
                    <button class="btn-secondary" onclick="deleteJob(${job.job_id})">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error("Error fetching company jobs", err);
    }
}

// 2. Delete Job Function
async function deleteJob(jobId) {
    if(confirm("Are you sure you want to remove this job listing?")) {
        console.log("Deleting job ID:", jobId);
        alert("Job deleted!");
        fetchCompanyJobs(); // Refresh list
    }
}

// Update your window.onload to include this
window.onload = () => {
    fetchApplicants();
    fetchCompanyJobs();
};

window.onload = () => {
    fetchApplicants();
};

function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}