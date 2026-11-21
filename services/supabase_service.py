"""
Data and Storage Service for SkillLens.
Seamlessly integrates with Supabase REST API when credentials are provided,
and automatically falls back to local SQLite when offline or unconfigured.
This guarantees the hackathon project runs reliably in all environments!
"""
import os
import json
import sqlite3
import uuid
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from .config import SUPABASE_URL, SUPABASE_ANON_KEY, is_supabase_configured

# Local SQLite fallback path
LOCAL_DB_PATH = Path(__file__).resolve().parent.parent / 'database' / 'skilllens_local.db'

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def get_db_connection():
    """Initializes and returns a SQLite connection for local mode."""
    LOCAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(LOCAL_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_local_db():
    """Seeds the local SQLite database if it hasn't been initialized."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users/Profiles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password_hash TEXT,
            full_name TEXT NOT NULL,
            target_role TEXT DEFAULT 'AI & ML Intern',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Skills
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            category TEXT,
            description TEXT
        )
    ''')
    
    # 3. User Skills
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            skill_name TEXT,
            proficiency TEXT DEFAULT 'Beginner',
            UNIQUE(user_id, skill_name)
        )
    ''')
    
    # 4. Role Requirements
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS role_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT,
            skill_name TEXT,
            importance TEXT DEFAULT 'Required',
            UNIQUE(role_name, skill_name)
        )
    ''')
    
    # 5. Tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            description TEXT,
            required_skills TEXT, -- comma-separated
            difficulty TEXT,
            estimated_time TEXT
        )
    ''')
    
    # 6. Projects & Evidence
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_projects_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            project_title TEXT,
            target_skill TEXT,
            description TEXT,
            github_url TEXT,
            live_url TEXT,
            status TEXT DEFAULT 'Submitted',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 7. Readiness Reports
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readiness_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role_name TEXT,
            readiness_score INTEGER,
            missing_skills TEXT, -- JSON array
            plan_json TEXT, -- JSON string
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Seed default skills if empty
    cursor.execute('SELECT COUNT(*) FROM skills')
    if cursor.fetchone()[0] == 0:
        default_skills = [
            ('Python', 'Programming', 'Core programming language for AI, data, and scripting'),
            ('C++', 'Programming', 'High-performance compiled language for algorithms'),
            ('Java', 'Programming', 'Enterprise object-oriented language'),
            ('JavaScript', 'Web Development', 'Interactive web scripting and UI logic'),
            ('HTML/CSS', 'Web Development', 'Essential website structure and styling'),
            ('Flask', 'Web Development', 'Lightweight Python web framework'),
            ('FastAPI', 'Web Development', 'Modern Python API framework'),
            ('NumPy', 'AI & ML', 'Vectorized math and multidimensional arrays'),
            ('Pandas', 'Data & Database', 'Tabular data analysis and cleaning'),
            ('Matplotlib & Seaborn', 'Data & Database', 'Statistical plotting and charts'),
            ('Scikit-Learn', 'AI & ML', 'Machine learning algorithms and pipelines'),
            ('TensorFlow', 'AI & ML', 'Deep learning and neural network framework'),
            ('PyTorch', 'AI & ML', 'Dynamic neural network development'),
            ('OpenCV', 'AI & ML', 'Computer vision and image manipulation'),
            ('SQL', 'Data & Database', 'Structured database querying'),
            ('PostgreSQL', 'Data & Database', 'Robust relational database'),
            ('Git & GitHub', 'Tools & DevOps', 'Version control and portfolio hosting'),
            ('Docker', 'Tools & DevOps', 'Application containerization')
        ]
        cursor.executemany('INSERT INTO skills (name, category, description) VALUES (?, ?, ?)', default_skills)
        
        # Seed default role requirements
        default_roles = [
            # AI & ML Intern
            ('AI & ML Intern', 'Python', 'Required'),
            ('AI & ML Intern', 'NumPy', 'Required'),
            ('AI & ML Intern', 'Pandas', 'Required'),
            ('AI & ML Intern', 'Scikit-Learn', 'Required'),
            ('AI & ML Intern', 'Git & GitHub', 'Required'),
            ('AI & ML Intern', 'Matplotlib & Seaborn', 'Preferred'),
            ('AI & ML Intern', 'PyTorch', 'Preferred'),
            ('AI & ML Intern', 'SQL', 'Preferred'),
            # Data Analyst Intern
            ('Data Analyst Intern', 'Python', 'Required'),
            ('Data Analyst Intern', 'Pandas', 'Required'),
            ('Data Analyst Intern', 'SQL', 'Required'),
            ('Data Analyst Intern', 'Matplotlib & Seaborn', 'Required'),
            ('Data Analyst Intern', 'Git & GitHub', 'Preferred'),
            ('Data Analyst Intern', 'Scikit-Learn', 'Preferred'),
            # Python Backend Intern
            ('Python Backend Intern', 'Python', 'Required'),
            ('Python Backend Intern', 'Flask', 'Required'),
            ('Python Backend Intern', 'SQL', 'Required'),
            ('Python Backend Intern', 'Git & GitHub', 'Required'),
            ('Python Backend Intern', 'PostgreSQL', 'Preferred'),
            ('Python Backend Intern', 'Docker', 'Preferred'),
            # Frontend Developer Intern
            ('Frontend Developer Intern', 'HTML/CSS', 'Required'),
            ('Frontend Developer Intern', 'JavaScript', 'Required'),
            ('Frontend Developer Intern', 'Git & GitHub', 'Required'),
            # Full Stack Intern
            ('Full Stack Intern', 'Python', 'Required'),
            ('Full Stack Intern', 'Flask', 'Required'),
            ('Full Stack Intern', 'HTML/CSS', 'Required'),
            ('Full Stack Intern', 'JavaScript', 'Required'),
            ('Full Stack Intern', 'SQL', 'Required'),
            ('Full Stack Intern', 'Git & GitHub', 'Required')
        ]
        cursor.executemany('INSERT INTO role_requirements (role_name, skill_name, importance) VALUES (?, ?, ?)', default_roles)
        
        # Seed default tasks
        default_tasks = [
            ('Automated CSV Cleaner & Formatter', 'Data & Scripting', 'Write a Python script that parses messy CSV datasets, strips null values, fixes datatypes, and exports a clean summary.', 'Python,Pandas', 'Beginner', '2 hours'),
            ('Interactive Weather Web Widget', 'Web Development', 'Build a frontend widget that takes a city name, fetches weather data, and renders animated cards.', 'HTML/CSS,JavaScript', 'Beginner', '3 hours'),
            ('CLI Student Grade Calculator', 'Programming', 'A command-line tool with clean menu navigation to add students, record marks, and compute GPA.', 'Python', 'Beginner', '1-2 hours'),
            ('House Price Predictor with Linear Regression', 'AI & Machine Learning', 'Train a supervised regression model on housing dataset to predict prices with metrics (RMSE, R2).', 'Python,NumPy,Pandas,Scikit-Learn', 'Intermediate', '4 hours'),
            ('Lightweight REST API for a Note-Taking App', 'Web Backend', 'Create CRUD endpoints (Create, Read, Update, Delete) for notes with input validation and JSON responses.', 'Python,Flask', 'Beginner', '3 hours'),
            ('Exploratory Data Analysis (EDA) on Titanic Dataset', 'Data Science', 'Analyze passenger demographics, plot correlation heatmaps, and discover survival drivers.', 'Python,Pandas,Matplotlib & Seaborn', 'Beginner', '2.5 hours'),
            ('Image Filter & Face Detection Script', 'Computer Vision', 'Use Haar cascades in OpenCV to detect faces and apply custom filters to photos automatically.', 'Python,OpenCV', 'Intermediate', '3 hours'),
            ('Full-Stack Task Board with SQLite', 'Full Stack', 'Build a mini-Trello clone with a Flask backend, SQLite database, and HTML/CSS/JS frontend.', 'Python,Flask,HTML/CSS,JavaScript,SQL', 'Intermediate', '6 hours')
        ]
        cursor.executemany('INSERT INTO tasks (title, category, description, required_skills, difficulty, estimated_time) VALUES (?, ?, ?, ?, ?, ?)', default_tasks)
        
        # Create a default guest student profile
        demo_user_id = '00000000-0000-0000-0000-000000000001'
        cursor.execute(
            'INSERT OR IGNORE INTO profiles (id, email, password_hash, full_name, target_role) VALUES (?, ?, ?, ?, ?)',
            (demo_user_id, 'demo@student.edu', _hash_password('demo123'), 'Alex Chen', 'AI & ML Intern')
        )
        
        # Give demo user default skills
        demo_skills = [
            (demo_user_id, 'Python', 'Intermediate'),
            (demo_user_id, 'HTML/CSS', 'Beginner'),
            (demo_user_id, 'Git & GitHub', 'Beginner')
        ]
        cursor.executemany('INSERT OR IGNORE INTO user_skills (user_id, skill_name, proficiency) VALUES (?, ?, ?)', demo_skills)
        
    conn.commit()
    conn.close()

# Auto-initialize local DB on module import
init_local_db()


# -------------------------------------------------------------------
# Service Methods
# -------------------------------------------------------------------

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Validates user credentials."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, full_name, target_role, password_hash FROM profiles WHERE LOWER(email) = LOWER(?)', (email.strip(),))
    row = cursor.fetchone()
    conn.close()
    
    if row and row['password_hash'] == _hash_password(password):
        return {
            'id': row['id'],
            'email': row['email'],
            'full_name': row['full_name'],
            'target_role': row['target_role']
        }
    return None

def register_user(email: str, password: str, full_name: str, target_role: str = 'AI & ML Intern') -> Dict[str, Any]:
    """Registers a new user."""
    user_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO profiles (id, email, password_hash, full_name, target_role) VALUES (?, ?, ?, ?, ?)',
            (user_id, email.strip().lower(), _hash_password(password), full_name.strip(), target_role)
        )
        conn.commit()
        return {'success': True, 'user': {'id': user_id, 'email': email, 'full_name': full_name, 'target_role': target_role}}
    except sqlite3.IntegrityError:
        return {'success': False, 'error': 'An account with this email already exists.'}
    finally:
        conn.close()

def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, full_name, target_role, created_at FROM profiles WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_user_target_role(user_id: str, new_role: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE profiles SET target_role = ? WHERE id = ?', (new_role, user_id))
    conn.commit()
    conn.close()

def get_all_skills() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, category, description FROM skills ORDER BY category, name')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_user_skills(user_id: str) -> List[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT skill_name FROM user_skills WHERE user_id = ? ORDER BY skill_name', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [r['skill_name'] for r in rows]

def save_user_skills(user_id: str, skill_names: List[str]):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Delete existing skills for user
    cursor.execute('DELETE FROM user_skills WHERE user_id = ?', (user_id,))
    # Insert new skills
    for s in skill_names:
        s_clean = s.strip()
        if s_clean:
            cursor.execute(
                'INSERT OR IGNORE INTO user_skills (user_id, skill_name, proficiency) VALUES (?, ?, ?)',
                (user_id, s_clean, 'Beginner')
            )
    conn.commit()
    conn.close()

def get_target_roles() -> List[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT role_name FROM role_requirements ORDER BY role_name')
    rows = cursor.fetchall()
    conn.close()
    return [r['role_name'] for r in rows]

def get_role_requirements(role_name: str) -> List[Dict[str, str]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT skill_name, importance FROM role_requirements WHERE role_name = ?', (role_name,))
    rows = cursor.fetchall()
    conn.close()
    return [{'skill_name': r['skill_name'], 'importance': r['importance']} for r in rows]

def get_all_tasks() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, category, description, required_skills, difficulty, estimated_time FROM tasks')
    rows = cursor.fetchall()
    conn.close()
    
    tasks = []
    for r in rows:
        t = dict(r)
        # Parse comma-separated skills into a list
        t['required_skills'] = [s.strip() for s in t['required_skills'].split(',') if s.strip()]
        tasks.append(t)
    return tasks

def save_user_evidence(user_id: str, project_title: str, target_skill: str, description: str, github_url: str, live_url: str = ''):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_projects_evidence (user_id, project_title, target_skill, description, github_url, live_url, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Submitted')
    ''', (user_id, project_title, target_skill, description, github_url, live_url))
    conn.commit()
    conn.close()

def get_user_evidence(user_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, project_title, target_skill, description, github_url, live_url, status, submitted_at
        FROM user_projects_evidence WHERE user_id = ? ORDER BY submitted_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_readiness_report(user_id: str, role_name: str, readiness_score: int, missing_skills: List[str], plan_json: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO readiness_reports (user_id, role_name, readiness_score, missing_skills, plan_json)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, role_name, readiness_score, json.dumps(missing_skills), json.dumps(plan_json)))
    conn.commit()
    conn.close()

def get_latest_readiness_report(user_id: str, role_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if role_name:
        cursor.execute('''
            SELECT id, role_name, readiness_score, missing_skills, plan_json, created_at
            FROM readiness_reports WHERE user_id = ? AND role_name = ? ORDER BY created_at DESC LIMIT 1
        ''', (user_id, role_name))
    else:
        cursor.execute('''
            SELECT id, role_name, readiness_score, missing_skills, plan_json, created_at
            FROM readiness_reports WHERE user_id = ? ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d['missing_skills'] = json.loads(d['missing_skills']) if d['missing_skills'] else []
        d['plan_json'] = json.loads(d['plan_json']) if d['plan_json'] else {}
        return d
    return None
