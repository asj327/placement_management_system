-- =====================================================
-- Placement Management System Database Schema
-- =====================================================

-- Drop database if exists (for testing)
DROP DATABASE IF EXISTS placement_management;

-- Create database
CREATE DATABASE placement_management;
USE placement_management;

-- =====================================================
-- TABLE: students
-- =====================================================

CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    cgpa DECIMAL(3,2) CHECK (cgpa BETWEEN 0 AND 10),
    phone VARCHAR(15),
    resume_path VARCHAR(255)
);

-- =====================================================
-- TABLE: companies
-- =====================================================

CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    location VARCHAR(150),
    website VARCHAR(255),
    description TEXT
);

-- =====================================================
-- TABLE: admins
-- =====================================================

CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

-- =====================================================
-- TABLE: jobs
-- =====================================================

CREATE TABLE jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    job_title VARCHAR(150) NOT NULL,
    job_description TEXT NOT NULL,
    location VARCHAR(150),
    salary DECIMAL(10,2),
    eligibility_cgpa DECIMAL(3,2) CHECK (eligibility_cgpa BETWEEN 0 AND 10),
    job_type ENUM('Full-Time', 'Part-Time', 'Internship') DEFAULT 'Full-Time',
    deadline DATE NOT NULL

    CONSTRAINT fk_company_job
        FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Index for faster searching
CREATE INDEX idx_jobs_company_id ON jobs(company_id);

-- =====================================================
-- TABLE: applications
-- =====================================================

CREATE TABLE applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    job_id INT NOT NULL,
    applied_date DATE DEFAULT CURRENT_DATE,
    status ENUM('Pending', 'Selected', 'Rejected') DEFAULT 'Pending'

    CONSTRAINT fk_application_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_application_job
        FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT unique_application UNIQUE (student_id, job_id)
);

-- Indexes for performance
CREATE INDEX idx_application_student ON applications(student_id);
CREATE INDEX idx_application_job ON applications(job_id);

-- =====================================================
-- END OF SCHEMA
-- =====================================================

