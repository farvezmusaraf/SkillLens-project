-- ==========================================================
-- SkillLens Hackathon MVP Database Schema (Supabase PostgreSQL)
-- ==========================================================

-- 1. PROFILES TABLE (Linked with Supabase Auth)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT NOT NULL,
    target_role TEXT DEFAULT 'AI & ML Intern',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. SKILLS MASTER CATALOG
CREATE TABLE IF NOT EXISTS public.skills (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL, -- 'Programming', 'AI & ML', 'Web Development', 'Data & Database', 'Tools & DevOps'
    description TEXT
);

-- 3. USER SKILLS TABLE (Student Selected Skills)
CREATE TABLE IF NOT EXISTS public.user_skills (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    proficiency TEXT DEFAULT 'Beginner', -- 'Beginner', 'Intermediate', 'Advanced'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, skill_name)
);

-- 4. ROLE REQUIREMENTS BENCHMARK
CREATE TABLE IF NOT EXISTS public.role_requirements (
    id SERIAL PRIMARY KEY,
    role_name TEXT NOT NULL,
    skill_name TEXT NOT NULL,
    importance TEXT DEFAULT 'Required', -- 'Required' or 'Preferred'
    UNIQUE(role_name, skill_name)
);

-- 5. PRACTICAL TASKS CATALOG (What can I build right now?)
CREATE TABLE IF NOT EXISTS public.tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT[] NOT NULL,
    difficulty TEXT DEFAULT 'Beginner',
    estimated_time TEXT DEFAULT '2-4 hours'
);

-- 6. USER PROJECTS & EVIDENCE SUBMISSION
CREATE TABLE IF NOT EXISTS public.user_projects_evidence (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    project_title TEXT NOT NULL,
    target_skill TEXT NOT NULL,
    description TEXT,
    github_url TEXT NOT NULL,
    live_url TEXT,
    status TEXT DEFAULT 'Submitted', -- 'In Progress', 'Submitted', 'Verified'
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. READINESS REPORTS
CREATE TABLE IF NOT EXISTS public.readiness_reports (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    role_name TEXT NOT NULL,
    readiness_score INTEGER NOT NULL,
    missing_skills TEXT[] DEFAULT '{}',
    plan_json JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================================
-- SEED DATA: Pre-populate Skills Catalog
-- ==========================================================
INSERT INTO public.skills (name, category, description) VALUES
('Python', 'Programming', 'Core general-purpose programming language for AI and scripting'),
('C++', 'Programming', 'Fast compiled language for systems and low-level algorithms'),
('Java', 'Programming', 'Object-oriented programming language'),
('JavaScript', 'Web Development', 'Interactive scripting for web frontend and backends'),
('HTML/CSS', 'Web Development', 'Foundational markup and styling for web applications'),
('Flask', 'Web Development', 'Lightweight WSGI Python web framework'),
('FastAPI', 'Web Development', 'Modern, fast web framework for building APIs with Python'),
('NumPy', 'AI & ML', 'Scientific computing and multidimensional array operations'),
('Pandas', 'Data & Database', 'Data analysis, cleaning, and tabular data manipulation'),
('Matplotlib & Seaborn', 'Data & Database', 'Data visualization and statistical plotting'),
('Scikit-Learn', 'AI & ML', 'Machine learning algorithms for classification and regression'),
('TensorFlow', 'AI & ML', 'Deep learning framework for building neural networks'),
('PyTorch', 'AI & ML', 'Dynamic deep learning framework popular in research'),
('OpenCV', 'AI & ML', 'Computer vision and image processing library'),
('Natural Language Processing (NLP)', 'AI & ML', 'Text processing, tokenization, and language models'),
('SQL', 'Data & Database', 'Relational database query language'),
('PostgreSQL', 'Data & Database', 'Powerful open-source object-relational database system'),
('Git & GitHub', 'Tools & DevOps', 'Version control and collaboration platform'),
('Docker', 'Tools & DevOps', 'Containerization platform for software packaging')
ON CONFLICT (name) DO NOTHING;

-- ==========================================================
-- SEED DATA: Role Requirements
-- ==========================================================
INSERT INTO public.role_requirements (role_name, skill_name, importance) VALUES
-- AI & ML Intern
('AI & ML Intern', 'Python', 'Required'),
('AI & ML Intern', 'NumPy', 'Required'),
('AI & ML Intern', 'Pandas', 'Required'),
('AI & ML Intern', 'Scikit-Learn', 'Required'),
('AI & ML Intern', 'Git & GitHub', 'Required'),
('AI & ML Intern', 'Matplotlib & Seaborn', 'Preferred'),
('AI & ML Intern', 'PyTorch', 'Preferred'),
('AI & ML Intern', 'SQL', 'Preferred'),

-- Data Analyst Intern
('Data Analyst Intern', 'Python', 'Required'),
('Data Analyst Intern', 'Pandas', 'Required'),
('Data Analyst Intern', 'SQL', 'Required'),
('Data Analyst Intern', 'Matplotlib & Seaborn', 'Required'),
('Data Analyst Intern', 'Git & GitHub', 'Preferred'),
('Data Analyst Intern', 'Scikit-Learn', 'Preferred'),

-- Python Backend Intern
('Python Backend Intern', 'Python', 'Required'),
('Python Backend Intern', 'Flask', 'Required'),
('Python Backend Intern', 'SQL', 'Required'),
('Python Backend Intern', 'Git & GitHub', 'Required'),
('Python Backend Intern', 'PostgreSQL', 'Preferred'),
('Python Backend Intern', 'Docker', 'Preferred'),

-- Frontend Developer Intern
('Frontend Developer Intern', 'HTML/CSS', 'Required'),
('Frontend Developer Intern', 'JavaScript', 'Required'),
('Frontend Developer Intern', 'Git & GitHub', 'Required'),

-- Full Stack Intern
('Full Stack Intern', 'Python', 'Required'),
('Full Stack Intern', 'Flask', 'Required'),
('Full Stack Intern', 'HTML/CSS', 'Required'),
('Full Stack Intern', 'JavaScript', 'Required'),
('Full Stack Intern', 'SQL', 'Required'),
('Full Stack Intern', 'Git & GitHub', 'Required')
ON CONFLICT (role_name, skill_name) DO NOTHING;

-- ==========================================================
-- SEED DATA: Practical Tasks (Feature 2)
-- ==========================================================
INSERT INTO public.tasks (title, category, description, required_skills, difficulty, estimated_time) VALUES
('Automated CSV Cleaner & Formatter', 'Data & Scripting', 'Write a Python script that parses messy CSV datasets, strips null values, fixes datatypes, and exports a clean summary.', ARRAY['Python', 'Pandas'], 'Beginner', '2 hours'),
('Interactive Weather Web Widget', 'Web Development', 'Build a frontend widget that takes a city name, fetches mock or real weather data, and renders animated weather cards.', ARRAY['HTML/CSS', 'JavaScript'], 'Beginner', '3 hours'),
('CLI Student Grade Calculator', 'Programming', 'A command-line tool with clean menu navigation to add students, record marks, and compute GPA with file persistence.', ARRAY['Python'], 'Beginner', '1-2 hours'),
('House Price Predictor with Linear Regression', 'AI & Machine Learning', 'Train a supervised regression model on housing dataset to predict prices, complete with error metrics (RMSE, R2).', ARRAY['Python', 'NumPy', 'Pandas', 'Scikit-Learn'], 'Intermediate', '4 hours'),
('Lightweight REST API for a Note-Taking App', 'Web Backend', 'Create CRUD endpoints (Create, Read, Update, Delete) for notes with input validation and JSON responses.', ARRAY['Python', 'Flask'], 'Beginner', '3 hours'),
('Exploratory Data Analysis (EDA) on Titanic Dataset', 'Data Science', 'Analyze passenger demographics, plot correlation heatmaps, and discover survival drivers.', ARRAY['Python', 'Pandas', 'Matplotlib & Seaborn'], 'Beginner', '2.5 hours'),
('Image Filter & Face Detection Script', 'Computer Vision', 'Use Haar cascades in OpenCV to detect faces and apply custom filters to photos automatically.', ARRAY['Python', 'OpenCV'], 'Intermediate', '3 hours'),
('Full-Stack Task Board with SQLite', 'Full Stack', 'Build a mini-Trello clone with a Flask backend, SQLite database, and HTML/CSS/JS frontend.', ARRAY['Python', 'Flask', 'HTML/CSS', 'JavaScript', 'SQL'], 'Intermediate', '6 hours')
ON CONFLICT DO NOTHING;
