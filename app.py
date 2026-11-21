"""
SkillLens - Hackathon MVP Main Application Entry Point
Flask Backend coordinating routes, gap analysis, AI services, and data storage.
Refocused strictly on 4 Core Beginner Skills: Python, HTML, CSS, JavaScript.
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import json

from services.config import FLASK_SECRET_KEY, FLASK_DEBUG
from services import supabase_service as db
from services.gap_analysis import analyze_skill_gap, match_practical_tasks, get_next_skills_recommendations
from services.ai_service import generate_project_recommendations, generate_30_day_plan

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# -------------------------------------------------------------
# Authentication Helper / Decorator
# -------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in or try the instant demo account to access SkillLens.', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return db.get_user_profile(user_id)
    return None

@app.context_processor
def inject_global_data():
    """Provides current user, roles, skills, and recommendations globally across all templates."""
    user = get_current_user()
    roles = db.get_target_roles()
    user_skills = db.get_user_skills(user['id']) if user else []
    try:
        next_skills = get_next_skills_recommendations(user_skills)
    except Exception:
        next_skills = {
            'primary_next_skill': 'HTML',
            'why_useful': 'Learn HTML to turn your code into real web pages.',
            'basic_topics': ['Headings', 'Paragraphs', 'Links', 'Images', 'Forms'],
            'learning_order': ['1. HTML', '2. CSS', '3. JavaScript', '4. Python'],
            'is_all_completed': False,
            'unselected_skills': ['HTML', 'CSS', 'JavaScript']
        }
    return dict(current_user=user, available_roles=roles, next_skills=next_skills, user_skills=user_skills)


# -------------------------------------------------------------
# Public & Auth Routes
# -------------------------------------------------------------
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        user = db.authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_role'] = user['target_role']
            flash(f"Welcome back, {user['full_name']}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. You can also use the Instant Demo button below.', 'danger')
            
    return render_template('login.html')


@app.route('/login-demo')
@app.route('/login_demo')
def login_demo():
    """Quick one-click login for hackathon judges & instant student testing."""
    demo_user_id = '00000000-0000-0000-0000-000000000001'
    user = db.get_user_profile(demo_user_id)
    if user:
        session['user_id'] = user['id']
        session['user_name'] = user['full_name']
        session['user_role'] = user['target_role']
        flash("Logged in as Demo Student (Alex Chen)!", 'success')
    return redirect(url_for('dashboard'))


@app.route('/register', methods=['POST'])
def register():
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    target_role = request.form.get('target_role', 'Junior Full-Stack Starter')
    
    if not full_name or not email or not password:
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('login'))
        
    result = db.register_user(email, password, full_name, target_role)
    if result.get('success'):
        user = result['user']
        session['user_id'] = user['id']
        session['user_name'] = user['full_name']
        session['user_role'] = user['target_role']
        flash('Account created successfully! Start by selecting your beginner skills.', 'success')
        return redirect(url_for('skills'))
    else:
        flash(result.get('error', 'Registration failed.'), 'danger')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# -------------------------------------------------------------
# Main Application Views (Features 1 to 5)
# -------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    user_skills = db.get_user_skills(user['id'])
    role_reqs = db.get_role_requirements(user['target_role'])
    gap_result = analyze_skill_gap(user_skills, role_reqs)
    
    # Practical tasks matching selected skills
    matched_tasks = db.get_tasks_for_skills(user_skills)
    matched_projects = db.get_projects_for_skills(user_skills)
    
    # Dynamic next skills recommendation
    next_skills = get_next_skills_recommendations(user_skills)
    
    # Evidence submitted
    evidence_list = db.get_user_evidence(user['id'])
    
    return render_template(
        'dashboard.html',
        user=user,
        user_skills=user_skills,
        gap=gap_result,
        tasks_count=len(matched_tasks),
        projects_count=len(matched_projects),
        next_skills=next_skills,
        evidence_count=len(evidence_list),
        evidence_list=evidence_list[:3]
    )


# --- FEATURE 1: Student Skill Selection (4 Beginner Skills) ---
@app.route('/skills', methods=['GET', 'POST'])
@login_required
def skills():
    user = get_current_user()
    all_skills = db.get_all_skills()
    user_skills = db.get_user_skills(user['id'])
    
    if request.method == 'POST':
        selected = request.form.getlist('selected_skills')
        db.save_user_skills(user['id'], selected)
        flash('Your skills have been saved! Here are the practical tasks you can build right now.', 'success')
        return redirect(url_for('tasks'))
        
    return render_template('skills.html', skills=all_skills, user_skills=user_skills)


# --- FEATURE 2: Practical Tasks with Existing Skills ---
@app.route('/tasks')
@login_required
def tasks():
    user = get_current_user()
    user_skills = db.get_user_skills(user['id'])
    
    # ONLY show tasks that require skills the student currently has
    matched_tasks = db.get_tasks_for_skills(user_skills)
    
    # Dynamic recommended next skills
    next_skills = get_next_skills_recommendations(user_skills)
    
    return render_template(
        'tasks.html',
        user_skills=user_skills,
        matched_tasks=matched_tasks,
        next_skills=next_skills
    )


# --- FEATURE 3: Skill Gap Analysis Based on Target Role ---
@app.route('/gap-analysis', methods=['GET', 'POST'])
@login_required
def gap_analysis():
    user = get_current_user()
    roles = db.get_target_roles()
    
    if request.method == 'POST':
        new_role = request.form.get('target_role')
        if new_role and new_role in roles:
            db.update_user_target_role(user['id'], new_role)
            user['target_role'] = new_role
            flash(f"Updated your target track to '{new_role}'!", 'success')
            
    current_role = user['target_role']
    user_skills = db.get_user_skills(user['id'])
    role_reqs = db.get_role_requirements(current_role)
    gap_result = analyze_skill_gap(user_skills, role_reqs)
    next_skills = get_next_skills_recommendations(user_skills)
    
    return render_template(
        'gap_analysis.html',
        current_role=current_role,
        roles=roles,
        user_skills=user_skills,
        gap=gap_result,
        next_skills=next_skills
    )


# --- FEATURE 4: Beginner Projects & Evidence Submission ---
@app.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    user = get_current_user()
    user_skills = db.get_user_skills(user['id'])
    
    # Handle new evidence submission (GitHub link)
    if request.method == 'POST':
        project_title = request.form.get('project_title', '').strip()
        target_skill = request.form.get('target_skill', '').strip()
        description = request.form.get('description', '').strip()
        github_url = request.form.get('github_url', '').strip()
        live_url = request.form.get('live_url', '').strip()
        
        if not project_title or not github_url:
            flash('Project title and GitHub repository URL are required.', 'danger')
        else:
            db.save_user_evidence(user['id'], project_title, target_skill, description, github_url, live_url)
            flash('Project evidence submitted successfully! It counts towards your internship readiness.', 'success')
            return redirect(url_for('projects'))
            
    # ONLY show projects matching the user's selected skills
    matched_projects = db.get_projects_for_skills(user_skills)
    next_skills = get_next_skills_recommendations(user_skills)
    submitted_evidence = db.get_user_evidence(user['id'])
    
    return render_template(
        'projects.html',
        target_role=user['target_role'],
        user_skills=user_skills,
        projects=matched_projects,
        submitted_evidence=submitted_evidence,
        next_skills=next_skills
    )


# --- FEATURE 5: Readiness Report & 30-Day Learning Plan ---
@app.route('/readiness')
@login_required
def readiness():
    user = get_current_user()
    user_skills = db.get_user_skills(user['id'])
    role_reqs = db.get_role_requirements(user['target_role'])
    gap_result = analyze_skill_gap(user_skills, role_reqs)
    evidence_list = db.get_user_evidence(user['id'])
    next_skills = get_next_skills_recommendations(user_skills)
    
    # Calculate composite readiness score:
    # Base match score from skills (up to 75%) + Evidence Bonus (up to 25%, 12.5% per completed project)
    base_score = gap_result['match_percentage']
    evidence_bonus = min(25, len(evidence_list) * 12)
    composite_score = min(100, int(round((base_score * 0.75) + evidence_bonus)))
    
    all_missing = gap_result['missing_required'] + gap_result['missing_preferred']
    plan = generate_30_day_plan(user['target_role'], all_missing, user_skills, composite_score)
    
    db.save_readiness_report(user['id'], user['target_role'], composite_score, all_missing, plan)
    
    return render_template(
        'readiness.html',
        user=user,
        target_role=user['target_role'],
        composite_score=composite_score,
        base_score=base_score,
        evidence_bonus=evidence_bonus,
        gap=gap_result,
        evidence_list=evidence_list,
        plan=plan,
        next_skills=next_skills
    )


if __name__ == '__main__':
    print("=" * 60)
    print("Starting SkillLens Beginner-Focused Platform")
    print("Open your browser: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=FLASK_DEBUG)
