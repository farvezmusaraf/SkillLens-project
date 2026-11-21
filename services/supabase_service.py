"""
Data and Storage Service for SkillLens.
Seamlessly integrates with Supabase REST API when credentials are provided,
and automatically falls back to local SQLite when offline or unconfigured.
Refocused strictly on 4 Core Beginner Skills: Python, HTML, CSS, and JavaScript.
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
    """Seeds and updates the local SQLite database for beginner-focused skills, tasks, and projects."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users/Profiles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password_hash TEXT,
            full_name TEXT NOT NULL,
            target_role TEXT DEFAULT 'Junior Full-Stack Starter',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Skills
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            category TEXT,
            description TEXT,
            subtopics TEXT
        )
    ''')
    
    # Check if subtopics column exists, add if missing
    cursor.execute("PRAGMA table_info(skills)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'subtopics' not in columns:
        cursor.execute("ALTER TABLE skills ADD COLUMN subtopics TEXT")
    
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
            title TEXT UNIQUE,
            category TEXT,
            description TEXT,
            required_skills TEXT, -- comma-separated
            difficulty TEXT,
            estimated_time TEXT
        )
    ''')
    
    # 6. Projects Catalog (Beginner)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            description TEXT,
            required_skills TEXT, -- comma-separated
            difficulty TEXT,
            steps TEXT, -- JSON list of steps
            expected_outcome TEXT
        )
    ''')
    
    # 7. Projects & Evidence
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
    
    # 8. Readiness Reports
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

    # Seed or Refresh 4 Core Beginner Skills
    beginner_skills = [
        ('Python', 'Programming Logic', 'A clean, beginner-friendly language great for logic, problem solving, and automation.',
         json.dumps(['Variables', 'Data Types', 'Conditions', 'Loops', 'Functions'])),
        ('HTML', 'Web Structure', 'The foundational skeleton of every website. Used to display headings, paragraphs, and forms.',
         json.dumps(['Headings', 'Paragraphs', 'Links', 'Images', 'Forms'])),
        ('CSS', 'Web Styling', 'Adds visual style, colors, fonts, margins, and modern layouts to HTML pages.',
         json.dumps(['Colors', 'Fonts', 'Margins', 'Padding', 'Flexbox'])),
        ('JavaScript', 'Web Interactivity', 'Brings web pages to life with interactive buttons, clicks, alerts, and live updates.',
         json.dumps(['Variables', 'Functions', 'Events', 'DOM Manipulation']))
    ]
    
    # Clear advanced skills and insert ONLY the 4 beginner skills
    cursor.execute("DELETE FROM skills WHERE name NOT IN ('Python', 'HTML', 'CSS', 'JavaScript')")
    for s_name, s_cat, s_desc, s_subs in beginner_skills:
        cursor.execute('''
            INSERT INTO skills (name, category, description, subtopics)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                category=excluded.category,
                description=excluded.description,
                subtopics=excluded.subtopics
        ''', (s_name, s_cat, s_desc, s_subs))

    # Seed Role Requirements
    default_roles = [
        ('Junior Full-Stack Starter', 'Python', 'Required'),
        ('Junior Full-Stack Starter', 'HTML', 'Required'),
        ('Junior Full-Stack Starter', 'CSS', 'Required'),
        ('Junior Full-Stack Starter', 'JavaScript', 'Required'),
        ('Frontend Web Developer (Beginner)', 'HTML', 'Required'),
        ('Frontend Web Developer (Beginner)', 'CSS', 'Required'),
        ('Frontend Web Developer (Beginner)', 'JavaScript', 'Required'),
        ('Frontend Web Developer (Beginner)', 'Python', 'Preferred'),
        ('Junior Python Developer', 'Python', 'Required'),
        ('Junior Python Developer', 'HTML', 'Preferred'),
        ('Junior Python Developer', 'CSS', 'Preferred')
    ]
    cursor.execute('DELETE FROM role_requirements')
    cursor.executemany('INSERT INTO role_requirements (role_name, skill_name, importance) VALUES (?, ?, ?)', default_roles)

    # Seed Small Beginner Tasks
    beginner_tasks = [
        # Python Tasks
        ('Print Your Name and Bio', 'Python Logic', 'Write a Python script using variables and print() to display your name, college, and a short bio.', 'Python', 'Beginner', '15 mins'),
        ('Create a Simple Calculator', 'Python Logic', 'Build a script that takes two numbers and performs addition, subtraction, multiplication, or division using conditions.', 'Python', 'Beginner', '25 mins'),
        ('Check Even or Odd Number', 'Python Logic', 'Write a program that takes an integer input from the user and checks if it is even or odd using the modulo (%) operator.', 'Python', 'Beginner', '15 mins'),
        # HTML Tasks
        ('Create a Basic Webpage', 'HTML Markup', 'Create an HTML page featuring an <h1> title, introduction paragraphs, and a bulleted list of your favorite topics.', 'HTML', 'Beginner', '20 mins'),
        ('Add an Image and Clickable Links', 'HTML Markup', 'Add your profile picture using the <img> tag and create clickable links to your favorite websites using <a>.', 'HTML', 'Beginner', '15 mins'),
        ('Create a Simple Contact Form', 'HTML Markup', 'Build an HTML <form> with input fields for Name, Email, and Message, complete with a submit button.', 'HTML', 'Beginner', '20 mins'),
        # CSS Tasks
        ('Change Background & Text Colors', 'CSS Styling', 'Style a webpage with a custom background color, high-contrast dark text, and modern font families.', 'CSS', 'Beginner', '15 mins'),
        ('Style a Modern Button with Hover', 'CSS Styling', 'Create a rounded button with custom padding, background color, and a smooth hover transition effect.', 'CSS', 'Beginner', '20 mins'),
        ('Create a Simple Card with Flexbox', 'CSS Styling', 'Design a clean card container with borders, padding, and centered content using display: flex.', 'CSS', 'Beginner', '25 mins'),
        # JavaScript Tasks
        ('Display a Welcome Alert Pop-up', 'JavaScript Basics', 'Write a simple JavaScript function that shows a welcome alert dialog when the webpage is opened.', 'JavaScript', 'Beginner', '15 mins'),
        ('Create a Button Click Counter', 'JavaScript Basics', 'Add a button on your webpage and write an event listener that counts and displays how many times it was clicked.', 'JavaScript', 'Beginner', '20 mins'),
        ('Validate a Simple Form Input', 'JavaScript Basics', 'Use JavaScript to check if an input field is empty before form submission, and show a helpful warning message.', 'JavaScript', 'Beginner', '25 mins'),
        # Combination Tasks
        ('Style an HTML Profile Card', 'HTML & CSS', 'Combine HTML structure and CSS styling to build a responsive profile card with a picture, bio, and social button.', 'HTML,CSS', 'Beginner', '30 mins'),
        ('Interactive Color Switcher Button', 'Frontend Web', 'Build a button that changes the webpage background color dynamically between light and dark modes when clicked.', 'HTML,CSS,JavaScript', 'Beginner', '30 mins')
    ]
    cursor.execute('DELETE FROM tasks')
    cursor.executemany('INSERT INTO tasks (title, category, description, required_skills, difficulty, estimated_time) VALUES (?, ?, ?, ?, ?, ?)', beginner_tasks)

    # Seed 5 Beginner Projects
    beginner_projects = [
        (
            'Personal Portfolio Webpage',
            'A clean, modern single-page website to introduce yourself, highlight your skills, and share your contact links.',
            'HTML,CSS',
            'Beginner',
            json.dumps([
                'Create index.html with sections: Header, About Me, Skills, and Contact Info.',
                'Add your profile picture and clickable links to your social profiles.',
                'Create style.css to add colors, clean fonts, card borders, and padding.',
                'Use CSS Flexbox to organize your skills and social buttons neatly.'
            ]),
            'A responsive personal website that you can share with friends and recruiters.'
        ),
        (
            'Simple Calculator',
            'An easy-to-use calculator program that accepts two numbers and performs basic arithmetic operations (+, -, *, /).',
            'Python',
            'Beginner',
            json.dumps([
                'Prompt the user for input: first number, arithmetic operator, and second number.',
                'Convert string inputs into numbers (float or int).',
                'Use if, elif, and else conditions to perform the chosen calculation.',
                'Handle division by zero with a friendly error message.',
                'Print the calculation result clearly on the screen.'
            ]),
            'A working calculator that accurately computes math operations and handles errors gracefully.'
        ),
        (
            'To-Do List',
            'An interactive task organizer where students can add daily study tasks, mark them done, or delete them.',
            'HTML,CSS,JavaScript',
            'Beginner',
            json.dumps([
                'Build the HTML layout with an <input> text box and an "Add Task" <button>.',
                'Style the task container, input box, and list items with clean padding and rounded corners in CSS.',
                'Add a JavaScript event listener to the button to read the input value when clicked.',
                'Use JavaScript DOM manipulation (document.createElement) to append the new task to the list.',
                'Allow users to click on a task item to mark it completed or remove it.'
            ]),
            'A functional to-do application running in your browser that dynamically creates and manages tasks.'
        ),
        (
            'Basic Quiz Application',
            'A fun multiple-choice quiz that presents questions one by one, verifies answers, and displays your final score.',
            'Python',
            'Beginner',
            json.dumps([
                'Define a list of 3-5 beginner computer questions with options and answer keys.',
                'Loop through the questions and display them sequentially to the user.',
                'Collect user choices and check them against the answer key using conditions.',
                'Track the score count for each correct answer.',
                'Print the final score at the end with a personalized feedback message.'
            ]),
            'An interactive quiz game that tests knowledge and displays a final percentage score.'
        ),
        (
            'Simple Registration Form',
            'A user-friendly registration card with inputs for student name, email, password, and target role.',
            'HTML,CSS',
            'Beginner',
            json.dumps([
                'Construct an HTML form with <label> and <input> tags for Name, Email, Password, and a dropdown for Student Year.',
                'Center the form on the screen using CSS Flexbox.',
                'Add subtle borders, padding, focus outlines, and a stylish submit button with hover effects.',
                'Use HTML5 validation attributes (required, type="email") to ensure clean input.'
            ]),
            'A polished, modern registration form card that looks like a real SaaS sign-up page.'
        )
    ]
    cursor.execute('DELETE FROM projects')
    cursor.executemany('INSERT INTO projects (title, description, required_skills, difficulty, steps, expected_outcome) VALUES (?, ?, ?, ?, ?, ?)', beginner_projects)

    # Ensure default guest student exists
    demo_user_id = '00000000-0000-0000-0000-000000000001'
    cursor.execute(
        'INSERT OR IGNORE INTO profiles (id, email, password_hash, full_name, target_role) VALUES (?, ?, ?, ?, ?)',
        (demo_user_id, 'demo@student.edu', _hash_password('demo123'), 'Alex Chen', 'Junior Full-Stack Starter')
    )
    # Ensure demo user has beginner skills
    cursor.execute("DELETE FROM user_skills WHERE user_id = ? AND skill_name NOT IN ('Python', 'HTML', 'CSS', 'JavaScript')", (demo_user_id,))
    cursor.execute('SELECT COUNT(*) FROM user_skills WHERE user_id = ?', (demo_user_id,))
    if cursor.fetchone()[0] == 0:
        demo_skills = [
            (demo_user_id, 'Python', 'Beginner'),
            (demo_user_id, 'HTML', 'Beginner')
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

def register_user(email: str, password: str, full_name: str, target_role: str = 'Junior Full-Stack Starter') -> Dict[str, Any]:
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
    """Returns the 4 core beginner skills with their subtopics parsed in logical order."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, category, description, subtopics FROM skills 
        ORDER BY CASE name 
            WHEN 'Python' THEN 1 
            WHEN 'HTML' THEN 2 
            WHEN 'CSS' THEN 3 
            WHEN 'JavaScript' THEN 4 
            ELSE 5 
        END
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        d['subtopics'] = json.loads(d['subtopics']) if d['subtopics'] else []
        result.append(d)
    return result

def get_user_skills(user_id: str) -> List[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT skill_name FROM user_skills WHERE user_id = ? ORDER BY skill_name', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [r['skill_name'] for r in rows if r['skill_name'] in ['Python', 'HTML', 'CSS', 'JavaScript']]

def save_user_skills(user_id: str, skill_names: List[str]):
    valid_skills = {'Python', 'HTML', 'CSS', 'JavaScript'}
    filtered_skills = [s for s in skill_names if s in valid_skills]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_skills WHERE user_id = ?', (user_id,))
    for s in filtered_skills:
        cursor.execute(
            'INSERT INTO user_skills (user_id, skill_name, proficiency) VALUES (?, ?, ?)',
            (user_id, s, 'Beginner')
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
        t['required_skills'] = [s.strip() for s in t['required_skills'].split(',') if s.strip()]
        tasks.append(t)
    return tasks

def get_tasks_for_skills(user_skills: List[str]) -> List[Dict[str, Any]]:
    """
    Returns tasks that require ONLY skills the user has selected.
    If a task requires 'HTML,CSS', user must have both HTML and CSS.
    """
    all_tasks = get_all_tasks()
    user_skill_set = set(user_skills)
    
    matched = []
    for t in all_tasks:
        req_set = set(t['required_skills'])
        if req_set.issubset(user_skill_set):
            matched.append(t)
    return matched

def get_all_projects() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, required_skills, difficulty, steps, expected_outcome FROM projects')
    rows = cursor.fetchall()
    conn.close()
    
    projects = []
    for r in rows:
        p = dict(r)
        p['required_skills'] = [s.strip() for s in p['required_skills'].split(',') if s.strip()]
        p['steps'] = json.loads(p['steps']) if p['steps'] else []
        projects.append(p)
    return projects

def get_projects_for_skills(user_skills: List[str]) -> List[Dict[str, Any]]:
    """
    Returns beginner projects that require ONLY skills the user has selected.
    """
    all_projects = get_all_projects()
    user_skill_set = set(user_skills)
    
    matched = []
    for p in all_projects:
        req_set = set(p['required_skills'])
        if req_set.issubset(user_skill_set):
            matched.append(p)
    return matched

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
