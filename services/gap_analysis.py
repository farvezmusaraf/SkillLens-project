"""
Skill Gap Analysis & Recommendation Service.
Refocused strictly on 4 Core Beginner Skills: Python, HTML, CSS, JavaScript.
Provides:
1. Exact gap analysis against beginner career tracks.
2. Filtered tasks & projects strictly for selected skills.
3. Dynamic 'Recommended Next Skills to Learn' engine.
"""
from typing import List, Dict, Any

# Master definition of the 4 beginner skills with details
CORE_SKILLS_INFO = {
    'Python': {
        'name': 'Python',
        'category': 'Programming Logic',
        'why_useful': 'Python is the easiest programming language for beginners. It teaches you variables, loops, and logic that apply to all programming, and lets you build scripts, calculators, and backends.',
        'subtopics': ['Variables', 'Data Types', 'Conditions', 'Loops', 'Functions']
    },
    'HTML': {
        'name': 'HTML',
        'category': 'Web Structure',
        'why_useful': 'HTML is the essential skeleton of every website. Knowing HTML allows you to build real web pages that anyone can view in their browser.',
        'subtopics': ['Headings', 'Paragraphs', 'Links', 'Images', 'Forms']
    },
    'CSS': {
        'name': 'CSS',
        'category': 'Web Styling',
        'why_useful': 'CSS brings your HTML pages to life with colors, custom fonts, buttons, cards, and mobile-friendly layouts using Flexbox.',
        'subtopics': ['Colors', 'Fonts', 'Margins', 'Padding', 'Flexbox']
    },
    'JavaScript': {
        'name': 'JavaScript',
        'category': 'Web Interactivity',
        'why_useful': 'JavaScript turns static web pages into interactive apps. It lets you respond to button clicks, calculate user input on the fly, and build dynamic apps like to-do lists.',
        'subtopics': ['Variables', 'Functions', 'Events', 'DOM Manipulation']
    }
}


def analyze_skill_gap(user_skills: List[str], role_requirements: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Compares beginner user skills against target role requirements.
    """
    user_skill_set = set(s.strip().lower() for s in user_skills)
    
    acquired_skills = []
    missing_required = []
    missing_preferred = []
    
    total_weight = 0
    acquired_weight = 0
    
    for req in role_requirements:
        name = req.get('skill_name', '')
        importance = req.get('importance', 'Required')
        
        weight = 2 if importance.lower() == 'required' else 1
        total_weight += weight
        
        if name.strip().lower() in user_skill_set:
            acquired_skills.append({'name': name, 'importance': importance})
            acquired_weight += weight
        else:
            if importance.lower() == 'required':
                missing_required.append(name)
            else:
                missing_preferred.append(name)
                
    if total_weight > 0:
        match_percentage = int(round((acquired_weight / total_weight) * 100))
    else:
        match_percentage = 0
        
    if match_percentage >= 80:
        status_label = "Ready to Build Projects"
        status_color = "#10b981" # Green
        status_summary = "Fantastic! You have almost all core skills for this track. Focus on completing beginner projects."
    elif match_percentage >= 50:
        status_label = "Good Foundation"
        status_color = "#f59e0b" # Amber
        status_summary = "Great start. Learning 1 more skill will unlock multi-skill projects like full websites and interactive apps."
    else:
        status_label = "Getting Started"
        status_color = "#ef4444" # Red
        status_summary = "Welcome to programming! Start with small beginner tasks to build confidence."
        
    return {
        'match_percentage': match_percentage,
        'acquired_skills': acquired_skills,
        'missing_required': missing_required,
        'missing_preferred': missing_preferred,
        'status_label': status_label,
        'status_color': status_color,
        'status_summary': status_summary
    }


def match_practical_tasks(user_skills: List[str], all_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Returns tasks that require ONLY the skills the student currently has.
    """
    user_skill_set = set(s.strip().lower() for s in user_skills)
    matched = []
    
    for task in all_tasks:
        reqs = task.get('required_skills', [])
        req_set = set(r.strip().lower() for r in reqs)
        
        # Only show task if all its required skills are possessed by user
        if req_set and req_set.issubset(user_skill_set):
            matched.append({
                **task,
                'skills_have': reqs,
                'skills_missing': [],
                'is_ready_now': True,
                'coverage_pct': 100
            })
            
    return matched


def get_next_skills_recommendations(user_skills: List[str]) -> Dict[str, Any]:
    """
    Dynamic 'Recommended Next Skills' engine based on user's selected skills.
    
    Returns:
    - primary_next_skill: Main skill or next milestone to learn
    - why_useful: Clear explanation in simple beginner language
    - basic_topics: Subtopics to focus on
    - learning_order: Step-by-step path from where they are now
    - unselected_skills: Other unselected skills from the 4 core
    """
    user_skill_set = set(user_skills)
    all_core = ['HTML', 'CSS', 'JavaScript', 'Python']
    unselected = [s for s in all_core if s not in user_skill_set]
    
    # Case 0: No skills selected yet
    if not user_skills:
        return {
            'is_all_completed': False,
            'primary_next_skill': 'Python or HTML',
            'why_useful': 'Start with Python to master basic computer logic and math calculations, or start with HTML to build your very first web page!',
            'basic_topics': ['Variables & Print Statements (Python)', 'Headings, Paragraphs & Links (HTML)'],
            'learning_order': [
                '1. Pick your first skill: Python (Logic) or HTML (Web)',
                '2. Practice 2-3 mini-tasks (e.g. Print your name or Create a webpage)',
                '3. Add CSS for styling or Python conditions for calculators'
            ],
            'unselected_skills': all_core
        }
        
    # Case 1: User selected ALL 4 skills
    if len(user_skill_set) >= 4:
        return {
            'is_all_completed': True,
            'primary_next_skill': 'Full-Stack Connection & Git',
            'why_useful': 'Congratulations! You know all 4 core beginner building blocks. The next step is connecting them together and learning basic developer tools.',
            'basic_topics': [
                'Connecting HTML forms to a Python backend (Flask basics)',
                'Git & GitHub basics (git add, git commit, git push)',
                'DOM Fetch API (Updating webpage data with JavaScript without reload)'
            ],
            'learning_order': [
                '1. Core 4 Fundamentals (Complete! ✓)',
                '2. Build the To-Do List and Personal Portfolio projects',
                '3. Learn basic Git to save and showcase your code on GitHub',
                '4. Connect a Python backend to your HTML & JavaScript pages'
            ],
            'unselected_skills': []
        }
        
    # Case 2: User selected ONLY Python
    if user_skill_set == {'Python'}:
        next_info = CORE_SKILLS_INFO['HTML']
        return {
            'is_all_completed': False,
            'primary_next_skill': 'HTML',
            'why_useful': 'You know Python logic! Learning HTML is the ideal next step so you can build user interfaces in a web browser for people to interact with your Python code.',
            'basic_topics': next_info['subtopics'],
            'learning_order': [
                '1. Python (Current - Keep practicing functions & logic)',
                '2. HTML (Next - Learn headings, paragraphs, and forms)',
                '3. CSS (After HTML - Style your web pages with colors)',
                '4. JavaScript (Final - Add interactive buttons)'
            ],
            'unselected_skills': unselected
        }
        
    # Case 3: User selected HTML and CSS
    if user_skill_set == {'HTML', 'CSS'}:
        next_info = CORE_SKILLS_INFO['JavaScript']
        return {
            'is_all_completed': False,
            'primary_next_skill': 'JavaScript',
            'why_useful': 'You can now create and style beautiful static web pages! JavaScript is the natural next skill to make your pages interactive with buttons, alerts, and dynamic calculations.',
            'basic_topics': next_info['subtopics'],
            'learning_order': [
                '1. HTML & CSS (Current - Web structure & styling mastered! ✓)',
                '2. JavaScript (Next - Add button clicks & DOM manipulation)',
                '3. Python (After JS - Learn backend data processing and automation)'
            ],
            'unselected_skills': unselected
        }
        
    # Case 4: User selected ONLY HTML
    if user_skill_set == {'HTML'}:
        next_info = CORE_SKILLS_INFO['CSS']
        return {
            'is_all_completed': False,
            'primary_next_skill': 'CSS',
            'why_useful': 'HTML provides the skeleton of your page, but CSS makes it look modern and visually appealing with colors, clean fonts, rounded cards, and flexbox layouts.',
            'basic_topics': next_info['subtopics'],
            'learning_order': [
                '1. HTML (Current - Basic skeleton ready)',
                '2. CSS (Next - Style with colors, fonts & flexbox)',
                '3. JavaScript (After CSS - Add buttons & interactivity)',
                '4. Python (Final - Add backend logic)'
            ],
            'unselected_skills': unselected
        }

    # Case 5: User selected HTML, CSS, and JavaScript (Frontend Trio)
    if user_skill_set == {'HTML', 'CSS', 'JavaScript'}:
        next_info = CORE_SKILLS_INFO['Python']
        return {
            'is_all_completed': False,
            'primary_next_skill': 'Python',
            'why_useful': 'You have mastered the complete frontend web trio! Learning Python gives you backend superpowers to write scripts, calculate complex data, and save information to databases.',
            'basic_topics': next_info['subtopics'],
            'learning_order': [
                '1. HTML, CSS & JavaScript (Current - Frontend Web Stack Complete! ✓)',
                '2. Python (Next - Learn backend programming and algorithms)',
                '3. Build full-stack projects combining Python with HTML/JS'
            ],
            'unselected_skills': unselected
        }

    # Default / General fallback recommendation based on what is missing
    target_next = unselected[0]
    next_info = CORE_SKILLS_INFO[target_next]
    
    order = []
    for s in user_skills:
        order.append(f"{s} (Current ✓)")
    order.append(f"{target_next} (Next recommended)")
    for s in unselected[1:]:
        order.append(f"{s} (Later)")
        
    return {
        'is_all_completed': False,
        'primary_next_skill': target_next,
        'why_useful': next_info['why_useful'],
        'basic_topics': next_info['subtopics'],
        'learning_order': [f"{i+1}. {step}" for i, step in enumerate(order)],
        'unselected_skills': unselected
    }
