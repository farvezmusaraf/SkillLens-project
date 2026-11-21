"""
SkillLens - Hackathon MVP Main Application Entry Point
Flask Backend coordinating routes, gap analysis, AI services, and data storage.
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import json

from services.config import FLASK_SECRET_KEY, FLASK_DEBUG
from services import supabase_service as db
from services.gap_analysis import analyze_skill_gap, match_practical_tasks
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
            flash('Please log in or try the demo account to access SkillLens.', 'info')
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
    """Provides current user and roles globally across all templates."""
    user = get_current_user()
    roles = db.get_target_roles()
    return dict(current_user=user, available_roles=roles)


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
    """Quick one-click login for hackathon judges & instant testing."""
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
    target_role = request.form.get('target_role', 'AI & ML Intern')
    
    if not full_name or not email or not password:
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('login'))
        
    result = db.register_user(email, password, full_name, target_role)
    if result.get('success'):
        user = result['user']
        session['user_id'] = user['id']
        session['user_name'] = user['full_name']
        session['user_role'] = user['target_role']
        flash('Account created successfully! Start by selecting the skills you know.', 'success')
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
    
    # Practical tasks count
    all_tasks = db.get_all_tasks()
    matched_tasks = match_practical_tasks(user_skills, all_tasks)
    ready_tasks_count = len([t for t in matched_tasks if t['is_ready_now']])
    
    # Evidence submitted
    evidence_list = db.get_user_evidence(user['id'])
    
    return render_template(
        'dashboard.html',
        user=user,
        user_skills=user_skills,
        gap=gap_result,
        ready_tasks_count=ready_tasks_count,
        evidence_count=len(evidence_list),
        evidence_list=evidence_list[:3] # Show recent 3
    )


# --- FEATURE 1: Student Skill Selection ---
@app.route('/skills', methods=['GET', 'POST'])
@login_required
def skills():
    user = get_current_user()
    all_skills = db.get_all_skills()
    user_skills = db.get_user_skills(user['id'])
    
    if request.method == 'POST':
        # Selected skills from form
        selected = request.form.getlist('selected_skills')
        
        # Handle custom skill if typed in
        custom_skill = request.form.get('custom_skill', '').strip()
        if custom_skill and custom_skill not in selected:
            selected.append(custom_skill)
            
        db.save_user_skills(user['id'], selected)
        flash('Your skills have been saved! Check out practical tasks you can build right now.', 'success')
        return redirect(url_for('tasks'))
        
    # Group skills by category for clean UI
    categories = {}
    for s in all_skills:
        cat = s['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(s)
        
    return render_template('skills.html', categories=categories, user_skills=user_skills)


# --- FEATURE 2: Practical Tasks with Existing Skills ---
@app.route('/tasks')
@login_required
def tasks():
    user = get_current_user()
    user_skills = db.get_user_skills(user['id'])
    all_tasks = db.get_all_tasks()
    
    matched_tasks = match_practical_tasks(user_skills, all_tasks)
    
    return render_template(
        'tasks.html',
        user_skills=user_skills,
        matched_tasks=matched_tasks
    )


# --- FEATURE 3: Skill Gap Analysis Based on Target Role ---
@app.route('/gap-analysis', methods=['GET', 'POST'])
@login_required
def gap_analysis():
    user = get_current_user()
    roles = db.get_target_roles()
    
    # If user changed target role via dropdown form
    if request.method == 'POST':
        new_role = request.form.get('target_role')
        if new_role and new_role in roles:
            db.update_user_target_role(user['id'], new_role)
            user['target_role'] = new_role
            flash(f"Updated your target internship role to '{new_role}'!", 'success')
            
    current_role = user['target_role']
    user_skills = db.get_user_skills(user['id'])
    role_reqs = db.get_role_requirements(current_role)
    gap_result = analyze_skill_gap(user_skills, role_reqs)
    
    return render_template(
        'gap_analysis.html',
        current_role=current_role,
        roles=roles,
        user_skills=user_skills,
        gap=gap_result
    )


# --- FEATURE 4: AI Project Recommendations & Evidence Submission ---
@app.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    user = get_current_user()
    user_skills = db.get_user_skills(user['id'])
    role_reqs = db.get_role_requirements(user['target_role'])
    gap_result = analyze_skill_gap(user_skills, role_reqs)
    
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
            
    # Combine missing skills (required + preferred)
    all_missing = gap_result['missing_required'] + gap_result['missing_preferred']
    recommended_projects = generate_project_recommendations(user['target_role'], all_missing, user_skills)
    submitted_evidence = db.get_user_evidence(user['id'])
    
    return render_template(
        'projects.html',
        target_role=user['target_role'],
        recommended_projects=recommended_projects,
        submitted_evidence=submitted_evidence,
        missing_skills=all_missing
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
    
    # Calculate composite readiness score:
    # Base match score from skills (up to 75%) + Evidence Bonus (up to 25%, 10% per completed project)
    base_score = gap_result['match_percentage']
    evidence_bonus = min(25, len(evidence_list) * 10)
    composite_score = min(100, int(round((base_score * 0.75) + evidence_bonus)))
    
    all_missing = gap_result['missing_required'] + gap_result['missing_preferred']
    
    # Retrieve or generate 30-day plan
    plan = generate_30_day_plan(user['target_role'], all_missing, user_skills, composite_score)
    
    # Save the report snapshot
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
        plan=plan
    )


if __name__ == '__main__':
    print("=" * 60)
    print("Starting SkillLens Hackathon MVP Server")
    print("Open your browser and navigate to: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=FLASK_DEBUG)
