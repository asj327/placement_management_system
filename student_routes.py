from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import datetime
from functools import wraps
from db import get_connection

student_bp = Blueprint('student', __name__)

SECRET_KEY = 'your-secret-key-change-this'  # must match app.py


# ─────────────────────────────────────────────
# JWT HELPER
# ─────────────────────────────────────────────

def generate_token(student_id):
    payload = {
        'student_id': student_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def token_required(f):
    """Decorator to protect routes that need login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            # Expect header format: "Bearer <token>"
            token = token.split(' ')[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.student_id = data['student_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired, please login again'}), 401
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────
# ROUTE 1: STUDENT REGISTRATION
# POST /student/register
# ─────────────────────────────────────────────

@student_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validate required fields
    required = ['first_name', 'last_name', 'email', 'password', 'department', 'cgpa']
    for field in required:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400

    # Validate CGPA range
    try:
        cgpa = float(data['cgpa'])
        if not (0 <= cgpa <= 10):
            return jsonify({'error': 'CGPA must be between 0 and 10'}), 400
    except ValueError:
        return jsonify({'error': 'CGPA must be a number'}), 400

    # Hash the password
    password_hash = bcrypt.hashpw(
        data['password'].encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO students
                (first_name, last_name, email, password_hash, department, cgpa, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['first_name'],
            data['last_name'],
            data['email'],
            password_hash,
            data['department'],
            cgpa,
            data.get('phone', None)
        ))
        conn.commit()
        return jsonify({'message': 'Registration successful!'}), 201

    except Exception as e:
        # Duplicate email triggers this
        if 'Duplicate entry' in str(e):
            return jsonify({'error': 'Email already registered'}), 409
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
# ROUTE 2: STUDENT LOGIN
# POST /student/login
# ─────────────────────────────────────────────

@student_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT * FROM students WHERE email = %s', (data['email'],)
        )
        student = cursor.fetchone()

        if not student:
            return jsonify({'error': 'Invalid email or password'}), 401

        # Check password against hash
        password_matches = bcrypt.checkpw(
            data['password'].encode('utf-8'),
            student['password_hash'].encode('utf-8')
        )

        if not password_matches:
            return jsonify({'error': 'Invalid email or password'}), 401

        token = generate_token(student['student_id'])

        return jsonify({
            'message': 'Login successful!',
            'token': token,
            'student': {
                'student_id': student['student_id'],
                'name': f"{student['first_name']} {student['last_name']}",
                'email': student['email'],
                'department': student['department'],
                'cgpa': float(student['cgpa'])
            }
        }), 200

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
# ROUTE 3: VIEW JOBS
# GET /student/jobs
# Optional query param: ?type=Internship
# ─────────────────────────────────────────────

@student_bp.route('/jobs', methods=['GET'])
@token_required
def view_jobs():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Get this student's CGPA to filter eligible jobs
        cursor.execute(
            'SELECT cgpa FROM students WHERE student_id = %s',
            (request.student_id,)
        )
        student = cursor.fetchone()
        student_cgpa = float(student['cgpa'])

        # Optional filter by job type
        job_type = request.args.get('type')  # e.g. ?type=Internship

        query = '''
            SELECT
                j.job_id,
                j.job_title,
                j.location,
                j.salary,
                j.eligibility_cgpa,
                j.job_type,
                j.deadline,
                j.job_description,
                c.company_name,
                c.website
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            WHERE j.deadline >= CURDATE()
              AND (j.eligibility_cgpa IS NULL OR j.eligibility_cgpa <= %s)
        '''
        params = [student_cgpa]

        if job_type:
            query += ' AND j.job_type = %s'
            params.append(job_type)

        query += ' ORDER BY j.deadline ASC'

        cursor.execute(query, params)
        jobs = cursor.fetchall()

        # Convert Decimal and Date to serializable types
        for job in jobs:
            job['salary'] = float(job['salary']) if job['salary'] else None
            job['eligibility_cgpa'] = float(job['eligibility_cgpa']) if job['eligibility_cgpa'] else None
            job['deadline'] = str(job['deadline'])

        return jsonify({'jobs': jobs, 'count': len(jobs)}), 200

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
# ROUTE 4: APPLY FOR A JOB
# POST /student/apply
# Body: { "job_id": 3 }
# ─────────────────────────────────────────────

@student_bp.route('/apply', methods=['POST'])
@token_required
def apply_job():
    data = request.get_json()

    if not data.get('job_id'):
        return jsonify({'error': 'job_id is required'}), 400

    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Check job exists and deadline hasn't passed
        cursor.execute(
            'SELECT * FROM jobs WHERE job_id = %s AND deadline >= CURDATE()',
            (data['job_id'],)
        )
        job = cursor.fetchone()
        if not job:
            return jsonify({'error': 'Job not found or deadline has passed'}), 404

        # Check student CGPA meets eligibility
        cursor.execute(
            'SELECT cgpa FROM students WHERE student_id = %s',
            (request.student_id,)
        )
        student = cursor.fetchone()
        if job['eligibility_cgpa'] and float(student['cgpa']) < float(job['eligibility_cgpa']):
            return jsonify({'error': 'You do not meet the CGPA requirement for this job'}), 403

        # Insert application
        cursor.execute('''
            INSERT INTO applications (student_id, job_id)
            VALUES (%s, %s)
        ''', (request.student_id, data['job_id']))
        conn.commit()

        return jsonify({'message': 'Application submitted successfully!'}), 201

    except Exception as e:
        if 'Duplicate entry' in str(e):
            return jsonify({'error': 'You have already applied for this job'}), 409
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
# BONUS: VIEW MY APPLICATIONS
# GET /student/my-applications
# ─────────────────────────────────────────────

@student_bp.route('/my-applications', methods=['GET'])
@token_required
def my_applications():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT
                a.application_id,
                a.applied_date,
                a.status,
                j.job_title,
                j.job_type,
                j.location,
                j.salary,
                c.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN companies c ON j.company_id = c.company_id
            WHERE a.student_id = %s
            ORDER BY a.applied_date DESC
        ''', (request.student_id,))

        applications = cursor.fetchall()
        for app in applications:
            app['salary'] = float(app['salary']) if app['salary'] else None
            app['applied_date'] = str(app['applied_date'])

        return jsonify({'applications': applications}), 200

    finally:
        cursor.close()
        conn.close()
