# 🎯 SkillLens - AI Internship Readiness Engine
> **A Hackathon MVP built for First-Year CSE AI & ML Students**

SkillLens bridges the gap between early university engineering coursework and real-world tech internships. It reveals what students can build *right now* with the skills they possess, performs an exact gap analysis against target internship roles, generates tailored AI project recommendations, and compiles a comprehensive 30-day learning roadmap with proof-of-work tracking.

---

## 🌟 The 5 Core Features

1. **Student Skill Selection:** Filterable multi-category skill picker (Programming, AI/ML, Web, Databases, Tools) with custom skill addition.
2. **Discover Practical Tasks:** Instant confidence booster showing real mini-projects students can build today with zero extra studying.
3. **Skill Gap Analysis:** Interactive role benchmark (*AI & ML Intern*, *Data Analyst Intern*, *Python Backend Intern*, etc.) highlighting acquired skills in Green vs missing skills in Red/Amber with real-time match percentages.
4. **AI Project Recommendations & Evidence Submission:** AI suggests tailored portfolio projects bridging missing competencies; students paste their public GitHub repository link as proof of work.
5. **Internship Readiness Report & 30-Day Plan:** Calculates a composite Readiness Index ($0-100\%$) and generates a 4-week structured sprint roadmap with printable/exportable PDF layout for hackathon judges and recruiters.

---

## 🏗️ Architecture & Tech Stack

- **Backend:** Python Flask 3.1
- **Frontend:** Responsive HTML5, Modern CSS, Vanilla JavaScript (Jinja2 Templates)
- **Database & Auth:** Supabase (PostgreSQL schema in `database/schema.sql`) with seamless automatic local fallback for 100% offline hackathon demos.
- **AI Integration:** Google Gemini API (`google-genai`) with curated algorithmic fallbacks.
- **Version Control:** Git & GitHub

---

## 🚀 Quick Start (Running Locally)

Link :- https://skilllens-project.onrender.com/


> [!TIP]
> **Hackathon 1-Click Demo:** Click the **"Instant Student Demo"** button on the home or login page to instantly sign in as **Alex Chen** with pre-seeded skills, tasks, and evidence!

---

## ☁️ Connecting Supabase (Optional for Cloud Mode)

SkillLens works out-of-the-box offline using local storage. To connect your cloud Supabase database:

1. Create a free account at [supabase.com](https://supabase.com) and create a new project.
2. Go to **SQL Editor** in your Supabase dashboard.
3. Open `database/schema.sql` from this project, copy all its contents, paste it into the Supabase SQL editor, and click **Run**.
4. In your Supabase dashboard, go to **Project Settings -> API** and copy:
   - **Project URL**
   - **anon / public key**
5. Open your `.env` file in `d:\SkillLens-projects` and paste them:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   ```
6. Restart the Flask app (`python app.py`).

---

## 🤖 Adding Google Gemini AI Key (Optional)

To enable live generative AI for project suggestions and custom 30-day plan prompts:
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Add it to your `.env` file:
   ```env
   GEMINI_API_KEY=AIzaSy...your-gemini-key
   ```
*(If no key is provided, SkillLens uses its built-in smart algorithmic engine so your demo never fails!)*

---

## 📂 Project Structure

```text
SkillLens-projects/
├── app.py                      # Flask routes and application controller
├── run.bat                     # Windows quick start script
├── requirements.txt            # Python dependencies
├── .env                        # Private environment variables (ignored by git)
├── .gitignore                  # Git ignore rules
│
├── database/
│   ├── schema.sql              # Supabase PostgreSQL schema & seed data
│   └── skilllens_local.db      # Auto-generated offline database fallback
│
├── services/
│   ├── config.py               # Environment configuration loader
│   ├── gap_analysis.py         # Skill matching & gap calculation engine
│   ├── ai_service.py           # Gemini AI & smart roadmap generator
│   └── supabase_service.py     # Database service (Supabase + Local fallback)
│
├── static/
│   ├── css/
│   │   └── style.css           # Clean modern UI styling & print stylesheet
│   └── js/
│       └── main.js             # Live search, auto-dismiss alerts, print logic
│
└── templates/
    ├── base.html               # Main layout & navigation
    ├── index.html              # Landing hero page
    ├── login.html              # Login & Register with 1-click demo
    ├── dashboard.html          # Student status overview
    ├── skills.html             # Feature 1: Skill selection
    ├── tasks.html              # Feature 2: Practical tasks
    ├── gap_analysis.html       # Feature 3: Internship gap analysis
    ├── projects.html           # Feature 4: AI project recommendations & proof
    └── readiness.html          # Feature 5: 30-Day plan & readiness report
```

---

## 🐙 Git & GitHub Setup for Hackathon Teams

To push this codebase to your hackathon GitHub repository:

```bash
git init
git add .
git commit -m "feat: complete SkillLens hackathon MVP with all 5 core features"
git branch -M main
git remote add origin https://github.com/your-username/SkillLens.git
git push -u origin main
```
