"""
AI Recommendation Service.
Uses Google Gemini API or intelligent algorithmic templates to generate:
1. Tailored project recommendations targeting missing skills.
2. A structured 30-day learning and proof-building roadmap.
"""
import json
from typing import List, Dict, Any
from .config import GEMINI_API_KEY, is_gemini_configured

# Try importing google-genai
GENAI_AVAILABLE = False
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def generate_project_recommendations(target_role: str, missing_skills: List[str], user_skills: List[str]) -> List[Dict[str, Any]]:
    """
    Generates 2-3 project recommendations specifically designed to help the student learn
    missing skills and build portfolio evidence.
    """
    # If Gemini is configured and client available, attempt dynamic AI generation
    if is_gemini_configured() and GENAI_AVAILABLE:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            prompt = f"""
You are an expert AI career mentor for university students.
The student is aiming for the role of: "{target_role}".
They currently know: {', '.join(user_skills) if user_skills else 'Basic programming'}.
Their skill gaps to bridge are: {', '.join(missing_skills) if missing_skills else 'Advanced best practices'}.

Generate exactly 3 hands-on, realistic, portfolio-worthy project ideas that bridge these gaps.
Return ONLY valid JSON matching this schema:
[
  {{
    "title": "Project Title",
    "target_skill": "Primary missing skill addressed",
    "difficulty": "Beginner | Intermediate",
    "description": "2-3 sentences explaining what the project does.",
    "deliverables": ["Step 1", "Step 2", "Step 3"],
    "portfolio_value": "Why recruiters will love this on GitHub"
  }}
]
Do not include markdown code block markers like ```json, just raw JSON.
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
            # Fall back gracefully to curated template generator
            print(f"[AI Service] Gemini call fallback: {e}")

    # Curated Smart Algorithmic Generator
    return _generate_curated_projects(target_role, missing_skills, user_skills)


def generate_30_day_plan(target_role: str, missing_skills: List[str], user_skills: List[str], readiness_score: int) -> Dict[str, Any]:
    """
    Generates a structured 30-day (4-week) learning and evidence roadmap.
    """
    if is_gemini_configured() and GENAI_AVAILABLE:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            prompt = f"""
You are a senior tech mentor for university students.
Role: "{target_role}".
Readiness Score: {readiness_score}%.
Current Skills: {', '.join(user_skills) if user_skills else 'None specified'}.
Missing Skills: {', '.join(missing_skills) if missing_skills else 'Deepening practical projects'}.

Create a 30-day learning & portfolio sprint broken into 4 weeks.
Return ONLY valid JSON with this exact structure:
{{
  "overview": "Encouraging summary for the 30-day journey.",
  "weeks": [
    {{
      "week_number": 1,
      "theme": "Week 1 Theme Title",
      "goal": "Clear objective",
      "days": [
        {{"day_range": "Days 1-3", "task": "Actionable task"}},
        {{"day_range": "Days 4-7", "task": "Actionable task"}}
      ],
      "milestone": "End of week proof / deliverable"
    }},
    {{
      "week_number": 2,
      "theme": "Week 2 Theme Title",
      "goal": "Clear objective",
      "days": [
        {{"day_range": "Days 8-11", "task": "Actionable task"}},
        {{"day_range": "Days 12-14", "task": "Actionable task"}}
      ],
      "milestone": "End of week proof / deliverable"
    }},
    {{
      "week_number": 3,
      "theme": "Week 3 Theme Title",
      "goal": "Clear objective",
      "days": [
        {{"day_range": "Days 15-18", "task": "Actionable task"}},
        {{"day_range": "Days 19-21", "task": "Actionable task"}}
      ],
      "milestone": "End of week proof / deliverable"
    }},
    {{
      "week_number": 4,
      "theme": "Week 4 Theme Title",
      "goal": "Clear objective",
      "days": [
        {{"day_range": "Days 22-25", "task": "Actionable task"}},
        {{"day_range": "Days 26-30", "task": "Actionable task"}}
      ],
      "milestone": "End of week proof / deliverable"
    }}
  ]
}}
Do not include markdown code block markers.
"""
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            text = response.text.strip()
            if text.startswith("```"):
                text = text.strip("`").replace("json\n", "", 1).strip()
            plan = json.loads(text)
            if isinstance(plan, dict) and 'weeks' in plan:
                return plan
        except Exception as e:
            print(f"[AI Service] Gemini plan fallback: {e}")

    # Curated Smart Algorithmic Generator
    return _generate_curated_plan(target_role, missing_skills, user_skills, readiness_score)


# -------------------------------------------------------------
# Curated High-Quality Fallbacks (Ensures 100% Offline Hackathon Reliability)
# -------------------------------------------------------------

def _generate_curated_projects(target_role: str, missing_skills: List[str], user_skills: List[str]) -> List[Dict[str, Any]]:
    primary_gap = missing_skills[0] if missing_skills else "End-to-End Integration"
    secondary_gap = missing_skills[1] if len(missing_skills) > 1 else "Automated Testing & Deployment"
    
    return [
        {
            "title": f"{primary_gap} Practical Showcase Application",
            "target_skill": primary_gap,
            "difficulty": "Beginner to Intermediate",
            "description": f"Build a focused, standalone application demonstrating clean {primary_gap} concepts integrated into a real-world scenario.",
            "deliverables": [
                f"Implement core logic utilizing {primary_gap}",
                "Write comprehensive README with architectural diagrams and run instructions",
                "Push modular code to a public GitHub repository with informative commits"
            ],
            "portfolio_value": f"Proves to hiring managers that you understand real {primary_gap} workflows beyond textbook theory."
        },
        {
            "title": f"Automated {target_role} Pipeline & Dashboard",
            "target_skill": secondary_gap,
            "difficulty": "Intermediate",
            "description": f"Create an end-to-end prototype combining your existing skills with {secondary_gap} to solve a mock industry task.",
            "deliverables": [
                f"Combine current foundation with {secondary_gap}",
                "Include clean input validation and error handling",
                "Host live on a free platform (GitHub Pages / Render) or record a 60-sec demo GIF"
            ],
            "portfolio_value": "Demonstrates product thinking, end-to-end delivery, and documentation skills."
        },
        {
            "title": f"Production-Style Case Study: {target_role} Toolkit",
            "target_skill": "Full Stack & Documentation",
            "difficulty": "Beginner",
            "description": "Construct a curated CLI or web utility that automates a daily pain point for developers or analysts.",
            "deliverables": [
                "Modular code structure with separation of concerns",
                "Unit tests or sample verification scripts",
                "Well-formatted LICENSE and requirements configuration"
            ],
            "portfolio_value": "Shows professional software engineering hygiene, which stands out above 90% of student applicants."
        }
    ]


def _generate_curated_plan(target_role: str, missing_skills: List[str], user_skills: List[str], readiness_score: int) -> Dict[str, Any]:
    skill_a = missing_skills[0] if len(missing_skills) > 0 else "Advanced Concepts"
    skill_b = missing_skills[1] if len(missing_skills) > 1 else "System Design"
    
    return {
        "overview": f"Your personalized 30-day roadmap to reach 90%+ readiness for '{target_role}'. Focused on hands-on building and public GitHub proof.",
        "weeks": [
            {
                "week_number": 1,
                "theme": f"Foundation Sprint: Mastering {skill_a}",
                "goal": f"Gain solid theoretical grasp and code 3 mini-exercises in {skill_a}.",
                "days": [
                    {"day_range": "Days 1-3", "task": f"Learn core syntax, data models, and standard libraries for {skill_a}."},
                    {"day_range": "Days 4-7", "task": f"Build 2 small standalone scripts testing edge cases in {skill_a}."}
                ],
                "milestone": f"A clean public GitHub repo containing documented {skill_a} practice code."
            },
            {
                "week_number": 2,
                "theme": f"Skill Integration: Tackling {skill_b}",
                "goal": f"Connect your existing foundation with {skill_b}.",
                "days": [
                    {"day_range": "Days 8-11", "task": f"Complete targeted exercises and official tutorials for {skill_b}."},
                    {"day_range": "Days 12-14", "task": "Integrate {skill_a} and {skill_b} into a unified workflow."}
                ],
                "milestone": "A functional prototype showing both skills working together."
            },
            {
                "week_number": 3,
                "theme": "Capstone Project Build: Portfolio Flagship",
                "goal": f"Build an impressive project specifically targeted at the {target_role} role.",
                "days": [
                    {"day_range": "Days 15-18", "task": "Architect the project, set up GitHub repository, and code the core engine."},
                    {"day_range": "Days 19-21", "task": "Add input validation, clean UI/CLI, and clear logging."}
                ],
                "milestone": "Complete working version of your flagship project submitted on SkillLens."
            },
            {
                "week_number": 4,
                "theme": "Polish, Documentation & Internship Applications",
                "goal": "Transform raw code into a recruiter-ready portfolio presentation.",
                "days": [
                    {"day_range": "Days 22-25", "task": "Write an awesome README with demo GIFs, badges, and problem statements."},
                    {"day_range": "Days 26-30", "task": "Update your LinkedIn / Resume with your evidence links and apply to 5 targeted internships."}
                ],
                "milestone": "100% Internship Readiness report with verified evidence links."
            }
        ]
    }
