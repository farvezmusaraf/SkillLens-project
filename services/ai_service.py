"""
AI Recommendation Service for SkillLens.
Uses Google Gemini API or intelligent curated fallback templates to generate:
1. Beginner project ideas tailored strictly to the student's skills.
2. A structured, realistic 30-day learning roadmap for first-year engineers.
"""
import json
from typing import List, Dict, Any
from .config import GEMINI_API_KEY, is_gemini_configured

GENAI_AVAILABLE = False
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def generate_project_recommendations(target_role: str, missing_skills: List[str], user_skills: List[str]) -> List[Dict[str, Any]]:
    """
    Returns beginner-friendly projects based on the user's selected skills.
    """
    if is_gemini_configured() and GENAI_AVAILABLE:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            prompt = f"""
You are a friendly computer science mentor for a first-year BTech student.
The student knows these beginner skills: {', '.join(user_skills) if user_skills else 'Beginner coding'}.
Their target track is: "{target_role}".
Suggest 2-3 small, beginner-friendly projects they can build right now using their skills.
Return ONLY valid JSON matching this schema:
[
  {{
    "title": "Project Title",
    "target_skill": "Primary skill used",
    "difficulty": "Beginner",
    "description": "Short 1-2 sentence description.",
    "deliverables": ["Step 1", "Step 2", "Step 3"],
    "portfolio_value": "Why this is great for a beginner GitHub portfolio"
  }}
]
Do not include markdown code block markers.
"""
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            text = response.text.strip()
            if text.startswith("```"):
                text = text.strip("`").replace("json\n", "", 1).strip()
            projects = json.loads(text)
            if isinstance(projects, list) and len(projects) > 0:
                return projects
        except Exception as e:
            print(f"[AI Service] Gemini call fallback: {e}")

    return _generate_curated_projects(user_skills)


def generate_30_day_plan(target_role: str, missing_skills: List[str], user_skills: List[str], readiness_score: int) -> Dict[str, Any]:
    """
    Generates a beginner-friendly 30-day sprint plan.
    """
    next_focus = missing_skills[0] if missing_skills else "Building Multi-Skill Projects"
    
    return {
        "overview": f"A simple, manageable 30-day learning roadmap tailored for first-year students preparing for '{target_role}'. Spend 45 minutes a day practicing code.",
        "weeks": [
            {
                "week_number": 1,
                "theme": f"Foundation Sprint: {next_focus}",
                "goal": f"Master basic concepts in {next_focus} with hands-on practice.",
                "days": [
                    {"day_range": "Days 1-3", "task": f"Learn the basic syntax and core building blocks of {next_focus}."},
                    {"day_range": "Days 4-7", "task": f"Code 2 small practice tasks and verify them locally."}
                ],
                "milestone": f"A working folder with your first {next_focus} practice scripts."
            },
            {
                "week_number": 2,
                "theme": "Small Project Build",
                "goal": "Build your first standalone mini-project from scratch.",
                "days": [
                    {"day_range": "Days 8-11", "task": "Plan the project steps, write the initial code, and test simple inputs."},
                    {"day_range": "Days 12-14", "task": "Add input validation, clean formatting, and test edge cases."}
                ],
                "milestone": "A functional project (like a calculator or basic webpage)."
            },
            {
                "week_number": 3,
                "theme": "Portfolio Presentation & Git",
                "goal": "Learn basic Git commands and publish your project on GitHub.",
                "days": [
                    {"day_range": "Days 15-18", "task": "Initialize a Git repository and make your first commit with a clear message."},
                    {"day_range": "Days 19-21", "task": "Write a clean README.md explaining what your project does and how to run it."}
                ],
                "milestone": "A public GitHub repository link submitted on SkillLens."
            },
            {
                "week_number": 4,
                "theme": "Review & Next Steps",
                "goal": "Review your progress and explore how your skills connect together.",
                "days": [
                    {"day_range": "Days 22-25", "task": "Connect your skills (e.g. style your HTML with CSS or connect Python logic)."},
                    {"day_range": "Days 26-30", "task": "Submit your evidence link and review your updated readiness score."}
                ],
                "milestone": "Full beginner project portfolio completed!"
            }
        ]
    }


def _generate_curated_projects(user_skills: List[str]) -> List[Dict[str, Any]]:
    user_skill_set = set(user_skills)
    projects = []
    
    if 'Python' in user_skill_set:
        projects.append({
            "title": "Simple Calculator Application",
            "target_skill": "Python",
            "difficulty": "Beginner",
            "description": "An interactive calculator that takes two numbers and performs addition, subtraction, multiplication, or division with error checks.",
            "deliverables": [
                "Prompt user for numbers and operation (+, -, *, /)",
                "Use if/elif/else conditions to perform math",
                "Prevent crash on division by zero",
                "Print clean results on screen"
            ],
            "portfolio_value": "Shows you understand basic programming logic, variable conversion, and conditional error handling."
        })
        projects.append({
            "title": "Basic Quiz Application",
            "target_skill": "Python",
            "difficulty": "Beginner",
            "description": "A fun command-line quiz that asks 3-5 multiple-choice questions, verifies user answers, and calculates a final score.",
            "deliverables": [
                "Store questions and answer choices in a structured list",
                "Loop through questions and accept user choices",
                "Keep score of correct answers",
                "Display final score and a congratulatory message"
            ],
            "portfolio_value": "Demonstrates lists, loops, user input handling, and score tallying."
        })

    if 'HTML' in user_skill_set and 'CSS' in user_skill_set:
        projects.append({
            "title": "Personal Portfolio Webpage",
            "target_skill": "HTML & CSS",
            "difficulty": "Beginner",
            "description": "A clean, modern single-page website to introduce yourself, showcase your hobby projects, and share social links.",
            "deliverables": [
                "Create index.html with Header, About Me, Skills, and Contact",
                "Add your photo and social links using <img> and <a> tags",
                "Style with CSS colors, fonts, rounded cards, and padding",
                "Use CSS Flexbox to align buttons and cards neatly"
            ],
            "portfolio_value": "Gives you a live digital business card you can share with recruiters and peers."
        })
        projects.append({
            "title": "Simple Registration Form Card",
            "target_skill": "HTML & CSS",
            "difficulty": "Beginner",
            "description": "A clean sign-up card collecting Name, Email, Password, and Role with styled inputs and hover effects.",
            "deliverables": [
                "Build form with input fields for Name, Email, Password",
                "Center form card using CSS Flexbox",
                "Add button hover effect and input focus outlines",
                "Enforce HTML5 required fields"
            ],
            "portfolio_value": "Demonstrates practical CSS box model, form elements, and UI styling."
        })

    if 'JavaScript' in user_skill_set and 'HTML' in user_skill_set:
        projects.append({
            "title": "Interactive To-Do List",
            "target_skill": "JavaScript",
            "difficulty": "Beginner",
            "description": "A browser app where users can type a task, click 'Add Task', and see it appear in a list with the ability to mark it done.",
            "deliverables": [
                "HTML input field and 'Add Task' button",
                "CSS styling for task items and checkmarks",
                "JavaScript event listener on button click",
                "DOM manipulation to add new tasks dynamically"
            ],
            "portfolio_value": "The classic, must-have proof that you understand JavaScript events and DOM manipulation."
        })

    # If no specific match found, provide default starter project
    if not projects:
        projects.append({
            "title": "Personal Bio & Hobbies Webpage",
            "target_skill": "HTML",
            "difficulty": "Beginner",
            "description": "Create your first web page with headings, paragraphs, and a list of your favorite learning topics.",
            "deliverables": [
                "Create an index.html file",
                "Use <h1>, <h2>, and <p> tags for structure",
                "Add a bulleted list of your favorite hobbies"
            ],
            "portfolio_value": "Your very first step into web development!"
        })

    return projects
