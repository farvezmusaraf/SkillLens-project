-- ==========================================================
-- SkillLens Hackathon MVP Database Schema (Supabase PostgreSQL)
-- Refocused for Beginners: 4 Core Skills (Python, HTML, CSS, JavaScript)
-- Designed for Supabase with Row Level Security (RLS) & Seed Data
-- ==========================================================

-- ==========================================================
-- SECTION 1: CREATE TABLES (9 CORE TABLES)
-- ==========================================================

-- 1. PROFILES (Linked with Supabase Auth users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    college_name TEXT DEFAULT '',
    course TEXT DEFAULT 'B.Tech CSE (AI & ML)',
    year_of_study TEXT DEFAULT '1st Year',
    target_role TEXT DEFAULT 'Junior Full-Stack Starter',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. SKILLS (The 4 Core Beginner Skills Catalog)
CREATE TABLE IF NOT EXISTS public.skills (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    subtopics TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. ROLES (Beginner Target Tracks)
CREATE TABLE IF NOT EXISTS public.roles (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. ROLE_SKILLS (Mapping Required/Preferred Skills to Roles)
CREATE TABLE IF NOT EXISTS public.role_skills (
    id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES public.skills(id) ON DELETE CASCADE,
    importance TEXT NOT NULL DEFAULT 'Required',
    UNIQUE(role_id, skill_id)
);

-- 5. STUDENT_SKILLS (Skills selected by each student)
CREATE TABLE IF NOT EXISTS public.student_skills (
    id SERIAL PRIMARY KEY,
    student_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES public.skills(id) ON DELETE CASCADE,
    proficiency_level TEXT NOT NULL DEFAULT 'Beginner',
    progress_status TEXT NOT NULL DEFAULT 'Learning',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_id, skill_id)
);

-- 6. TASKS (Small, Practical Micro-Tasks)
CREATE TABLE IF NOT EXISTS public.tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    required_skill TEXT NOT NULL,
    required_skills TEXT[] NOT NULL DEFAULT '{}',
    difficulty TEXT NOT NULL DEFAULT 'Beginner',
    estimated_time TEXT NOT NULL DEFAULT '15-30 mins',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. PROJECTS (Small Beginner Projects)
CREATE TABLE IF NOT EXISTS public.projects (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    required_skills TEXT[] NOT NULL DEFAULT '{}',
    difficulty TEXT NOT NULL DEFAULT 'Beginner',
    implementation_steps TEXT[] NOT NULL DEFAULT '{}',
    expected_outcome TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. PROJECT_EVIDENCE (Student Proof of Work & GitHub URLs)
CREATE TABLE IF NOT EXISTS public.project_evidence (
    id SERIAL PRIMARY KEY,
    student_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    project_id INTEGER REFERENCES public.projects(id) ON DELETE SET NULL,
    project_title TEXT NOT NULL,
    github_url TEXT NOT NULL,
    submission_description TEXT DEFAULT '',
    submission_status TEXT NOT NULL DEFAULT 'Submitted',
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. LEARNING_PROGRESS (Student Progress Tracking)
CREATE TABLE IF NOT EXISTS public.learning_progress (
    id SERIAL PRIMARY KEY,
    student_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES public.skills(id) ON DELETE CASCADE,
    completed_tasks INTEGER NOT NULL DEFAULT 0,
    progress_status TEXT NOT NULL DEFAULT 'In Progress',
    updated_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_id, skill_id)
);

-- Create helpful indexes for foreign keys
CREATE INDEX IF NOT EXISTS idx_student_skills_student_id ON public.student_skills(student_id);
CREATE INDEX IF NOT EXISTS idx_project_evidence_student_id ON public.project_evidence(student_id);
CREATE INDEX IF NOT EXISTS idx_learning_progress_student_id ON public.learning_progress(student_id);
CREATE INDEX IF NOT EXISTS idx_role_skills_role_id ON public.role_skills(role_id);

-- ==========================================================
-- SECTION 2: ROW LEVEL SECURITY (RLS) POLICIES
-- ==========================================================

-- Enable Row Level Security on all 9 tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.role_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.student_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_progress ENABLE ROW LEVEL SECURITY;

-- 1. Profiles Policies (Students access only their own profile)
DROP POLICY IF EXISTS "Students can view own profile" ON public.profiles;
CREATE POLICY "Students can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Students can insert own profile" ON public.profiles;
CREATE POLICY "Students can insert own profile" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Students can update own profile" ON public.profiles;
CREATE POLICY "Students can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- 2. Student Skills Policies (Students manage only their own skill selections)
DROP POLICY IF EXISTS "Students can view own skills" ON public.student_skills;
CREATE POLICY "Students can view own skills" ON public.student_skills
    FOR SELECT USING (auth.uid() = student_id);

DROP POLICY IF EXISTS "Students can insert own skills" ON public.student_skills;
CREATE POLICY "Students can insert own skills" ON public.student_skills
    FOR INSERT WITH CHECK (auth.uid() = student_id);

DROP POLICY IF EXISTS "Students can update own skills" ON public.student_skills;
CREATE POLICY "Students can update own skills" ON public.student_skills
    FOR UPDATE USING (auth.uid() = student_id);

DROP POLICY IF EXISTS "Students can delete own skills" ON public.student_skills;
CREATE POLICY "Students can delete own skills" ON public.student_skills
    FOR DELETE USING (auth.uid() = student_id);

-- 3. Project Evidence Policies (Students access only their own submissions)
DROP POLICY IF EXISTS "Students can view own evidence" ON public.project_evidence;
CREATE POLICY "Students can view own evidence" ON public.project_evidence
    FOR SELECT USING (auth.uid() = student_id);

DROP POLICY IF EXISTS "Students can submit own evidence" ON public.project_evidence;
CREATE POLICY "Students can submit own evidence" ON public.project_evidence
    FOR INSERT WITH CHECK (auth.uid() = student_id);

DROP POLICY IF EXISTS "Students can update own evidence" ON public.project_evidence;
CREATE POLICY "Students can update own evidence" ON public.project_evidence
    FOR UPDATE USING (auth.uid() = student_id);

-- 4. Learning Progress Policies (Students access only their own progress)
DROP POLICY IF EXISTS "Students can view own learning progress" ON public.learning_progress;
CREATE POLICY "Students can view own learning progress" ON public.learning_progress
    FOR SELECT USING (auth.uid() = student_id);

DROP POLICY IF EXISTS "Students can update own learning progress" ON public.learning_progress;
CREATE POLICY "Students can update own learning progress" ON public.learning_progress
    FOR ALL USING (auth.uid() = student_id);

-- 5. Public Catalogs Policies (Readable by anyone; modifications restricted)
DROP POLICY IF EXISTS "Public can view skills catalog" ON public.skills;
CREATE POLICY "Public can view skills catalog" ON public.skills
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Public can view roles catalog" ON public.roles;
CREATE POLICY "Public can view roles catalog" ON public.roles
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Public can view role_skills catalog" ON public.role_skills;
CREATE POLICY "Public can view role_skills catalog" ON public.role_skills
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Public can view tasks catalog" ON public.tasks;
CREATE POLICY "Public can view tasks catalog" ON public.tasks
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Public can view projects catalog" ON public.projects;
CREATE POLICY "Public can view projects catalog" ON public.projects
    FOR SELECT USING (true);


-- ==========================================================
-- SECTION 3: SEED DATA (REPEATABLE & SAFE WITH ON CONFLICT)
-- ==========================================================

-- 1. Insert 4 Core Beginner Skills
INSERT INTO public.skills (name, category, description, subtopics) VALUES
(
    'Python',
    'Programming Logic',
    'A clean, beginner-friendly language great for logic, problem solving, and automation.',
    ARRAY['Variables', 'Data types', 'Conditions', 'Loops', 'Functions']
),
(
    'HTML',
    'Web Structure',
    'The foundational skeleton of every website. Used to display headings, paragraphs, and forms.',
    ARRAY['Headings', 'Paragraphs', 'Links', 'Images', 'Forms']
),
(
    'CSS',
    'Web Styling',
    'Adds visual style, colors, fonts, margins, and modern layouts to HTML pages.',
    ARRAY['Colors', 'Fonts', 'Margins', 'Padding', 'Flexbox']
),
(
    'JavaScript',
    'Web Interactivity',
    'Brings web pages to life with interactive buttons, clicks, alerts, and live updates.',
    ARRAY['Variables', 'Functions', 'Events', 'Basic DOM manipulation']
)
ON CONFLICT (name) DO UPDATE SET
    category = EXCLUDED.category,
    description = EXCLUDED.description,
    subtopics = EXCLUDED.subtopics;

-- 2. Insert Beginner Roles
INSERT INTO public.roles (name, description) VALUES
(
    'Junior Full-Stack Starter',
    'Builds basic full-stack applications combining Python programming logic with HTML, CSS, and JavaScript interfaces.'
),
(
    'Frontend Web Developer (Beginner)',
    'Specializes in crafting responsive, styled, and interactive user interfaces using HTML, CSS, and JavaScript.'
),
(
    'Junior Python Developer',
    'Focuses on writing clean Python scripts, algorithms, data calculations, and simple automated programs.'
)
ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description;

-- 3. Insert Role-Skill Requirements
DO $$
DECLARE
    r_fullstack INTEGER;
    r_frontend INTEGER;
    r_python INTEGER;
    s_python INTEGER;
    s_html INTEGER;
    s_css INTEGER;
    s_js INTEGER;
BEGIN
    SELECT id INTO r_fullstack FROM public.roles WHERE name = 'Junior Full-Stack Starter';
    SELECT id INTO r_frontend FROM public.roles WHERE name = 'Frontend Web Developer (Beginner)';
    SELECT id INTO r_python FROM public.roles WHERE name = 'Junior Python Developer';

    SELECT id INTO s_python FROM public.skills WHERE name = 'Python';
    SELECT id INTO s_html FROM public.skills WHERE name = 'HTML';
    SELECT id INTO s_css FROM public.skills WHERE name = 'CSS';
    SELECT id INTO s_js FROM public.skills WHERE name = 'JavaScript';

    -- Junior Full-Stack Starter Requirements
    INSERT INTO public.role_skills (role_id, skill_id, importance) VALUES
        (r_fullstack, s_python, 'Required'),
        (r_fullstack, s_html, 'Required'),
        (r_fullstack, s_css, 'Required'),
        (r_fullstack, s_js, 'Required')
    ON CONFLICT (role_id, skill_id) DO UPDATE SET importance = EXCLUDED.importance;

    -- Frontend Web Developer Requirements
    INSERT INTO public.role_skills (role_id, skill_id, importance) VALUES
        (r_frontend, s_html, 'Required'),
        (r_frontend, s_css, 'Required'),
        (r_frontend, s_js, 'Required'),
        (r_frontend, s_python, 'Preferred')
    ON CONFLICT (role_id, skill_id) DO UPDATE SET importance = EXCLUDED.importance;

    -- Junior Python Developer Requirements
    INSERT INTO public.role_skills (role_id, skill_id, importance) VALUES
        (r_python, s_python, 'Required'),
        (r_python, s_html, 'Preferred'),
        (r_python, s_css, 'Preferred')
    ON CONFLICT (role_id, skill_id) DO UPDATE SET importance = EXCLUDED.importance;
END $$;

-- 4. Insert 14 Beginner Practical Tasks
INSERT INTO public.tasks (title, category, description, required_skill, required_skills, difficulty, estimated_time) VALUES
-- Python Tasks
(
    'Print Your Name and Bio',
    'Python Logic',
    'Write a Python script using variables and print() to display your name, college, and a short bio.',
    'Python',
    ARRAY['Python'],
    'Beginner',
    '15 mins'
),
(
    'Create a Simple Calculator',
    'Python Logic',
    'Build a script that takes two numbers and performs addition, subtraction, multiplication, or division using conditions.',
    'Python',
    ARRAY['Python'],
    'Beginner',
    '25 mins'
),
(
    'Check Even or Odd Number',
    'Python Logic',
    'Write a program that takes an integer input from the user and checks if it is even or odd using the modulo (%) operator.',
    'Python',
    ARRAY['Python'],
    'Beginner',
    '15 mins'
),
-- HTML Tasks
(
    'Create a Basic Webpage',
    'HTML Markup',
    'Create an HTML page featuring an <h1> title, introduction paragraphs, and a bulleted list of your favorite topics.',
    'HTML',
    ARRAY['HTML'],
    'Beginner',
    '20 mins'
),
(
    'Add an Image and Clickable Links',
    'HTML Markup',
    'Add your profile picture using the <img> tag and create clickable links to your favorite websites using <a>.',
    'HTML',
    ARRAY['HTML'],
    'Beginner',
    '15 mins'
),
(
    'Create a Simple Contact Form',
    'HTML Markup',
    'Build an HTML <form> with input fields for Name, Email, and Message, complete with a submit button.',
    'HTML',
    ARRAY['HTML'],
    'Beginner',
    '20 mins'
),
-- CSS Tasks
(
    'Change Background & Text Colors',
    'CSS Styling',
    'Style a webpage with a custom background color, high-contrast dark text, and modern font families.',
    'CSS',
    ARRAY['CSS'],
    'Beginner',
    '15 mins'
),
(
    'Style a Modern Button with Hover',
    'CSS Styling',
    'Create a rounded button with custom padding, background color, and a smooth hover transition effect.',
    'CSS',
    ARRAY['CSS'],
    'Beginner',
    '20 mins'
),
(
    'Create a Simple Card with Flexbox',
    'CSS Styling',
    'Design a clean card container with borders, padding, and centered content using display: flex.',
    'CSS',
    ARRAY['CSS'],
    'Beginner',
    '25 mins'
),
-- JavaScript Tasks
(
    'Display a Welcome Alert Pop-up',
    'JavaScript Basics',
    'Write a simple JavaScript function that shows a welcome alert dialog when the webpage is opened.',
    'JavaScript',
    ARRAY['JavaScript'],
    'Beginner',
    '15 mins'
),
(
    'Create a Button Click Counter',
    'JavaScript Basics',
    'Add a button on your webpage and write an event listener that counts and displays how many times it was clicked.',
    'JavaScript',
    ARRAY['JavaScript'],
    'Beginner',
    '20 mins'
),
(
    'Validate a Simple Form Input',
    'JavaScript Basics',
    'Use JavaScript to check if an input field is empty before form submission, and show a helpful warning message.',
    'JavaScript',
    ARRAY['JavaScript'],
    'Beginner',
    '25 mins'
),
-- Multi-Skill Tasks
(
    'Style an HTML Profile Card',
    'HTML & CSS',
    'Combine HTML structure and CSS styling to build a responsive profile card with a picture, bio, and social button.',
    'HTML, CSS',
    ARRAY['HTML', 'CSS'],
    'Beginner',
    '30 mins'
),
(
    'Interactive Color Switcher Button',
    'Frontend Web',
    'Build a button that changes the webpage background color dynamically between light and dark modes when clicked.',
    'HTML, CSS, JavaScript',
    ARRAY['HTML', 'CSS', 'JavaScript'],
    'Beginner',
    '30 mins'
)
ON CONFLICT (title) DO UPDATE SET
    category = EXCLUDED.category,
    description = EXCLUDED.description,
    required_skill = EXCLUDED.required_skill,
    required_skills = EXCLUDED.required_skills,
    difficulty = EXCLUDED.difficulty,
    estimated_time = EXCLUDED.estimated_time;

-- 5. Insert 5 Beginner Projects
INSERT INTO public.projects (title, description, required_skills, difficulty, implementation_steps, expected_outcome) VALUES
(
    'Personal Portfolio Webpage',
    'A clean, modern single-page website to introduce yourself, highlight your skills, and share your contact links.',
    ARRAY['HTML', 'CSS'],
    'Beginner',
    ARRAY[
        'Create index.html with sections: Header, About Me, Skills, and Contact Info.',
        'Add your profile picture and clickable links to your social profiles.',
        'Create style.css to add colors, clean fonts, card borders, and padding.',
        'Use CSS Flexbox to organize your skills and social buttons neatly.'
    ],
    'A responsive personal website that you can share with friends and recruiters.'
),
(
    'Simple Calculator',
    'An easy-to-use calculator program that accepts two numbers and performs basic arithmetic operations (+, -, *, /).',
    ARRAY['Python'],
    'Beginner',
    ARRAY[
        'Prompt the user for input: first number, arithmetic operator, and second number.',
        'Convert string inputs into numbers (float or int).',
        'Use if, elif, and else conditions to perform the chosen calculation.',
        'Handle division by zero with a friendly error message.',
        'Print the calculation result clearly on the screen.'
    ],
    'A working calculator that accurately computes math operations and handles errors gracefully.'
),
(
    'To-Do List',
    'An interactive task organizer where students can add daily study tasks, mark them done, or delete them.',
    ARRAY['HTML', 'CSS', 'JavaScript'],
    'Beginner',
    ARRAY[
        'Build the HTML layout with an <input> text box and an "Add Task" <button>.',
        'Style the task container, input box, and list items with clean padding and rounded corners in CSS.',
        'Add a JavaScript event listener to the button to read the input value when clicked.',
        'Use JavaScript DOM manipulation (document.createElement) to append the new task to the list.',
        'Allow users to click on a task item to mark it completed or remove it.'
    ],
    'A functional to-do application running in your browser that dynamically creates and manages tasks.'
),
(
    'Basic Quiz Application',
    'A fun multiple-choice quiz that presents questions one by one, verifies answers, and displays your final score.',
    ARRAY['Python'],
    'Beginner',
    ARRAY[
        'Define a list of 3-5 beginner computer questions with options and answer keys.',
        'Loop through the questions and display them sequentially to the user.',
        'Collect user choices and check them against the answer key using conditions.',
        'Track the score count for each correct answer.',
        'Print the final score at the end with a personalized feedback message.'
    ],
    'An interactive quiz game that tests knowledge and displays a final percentage score.'
),
(
    'Simple Registration Form',
    'A user-friendly registration card with inputs for student name, email, password, and target role.',
    ARRAY['HTML', 'CSS'],
    'Beginner',
    ARRAY[
        'Construct an HTML form with <label> and <input> tags for Name, Email, Password, and a dropdown for Student Year.',
        'Center the form on the screen using CSS Flexbox.',
        'Add subtle borders, padding, focus outlines, and a stylish submit button with hover effects.',
        'Use HTML5 validation attributes (required, type="email") to ensure clean input.'
    ],
    'A polished, modern registration form card that looks like a real SaaS sign-up page.'
)
ON CONFLICT (title) DO UPDATE SET
    description = EXCLUDED.description,
    required_skills = EXCLUDED.required_skills,
    difficulty = EXCLUDED.difficulty,
    implementation_steps = EXCLUDED.implementation_steps,
    expected_outcome = EXCLUDED.expected_outcome;
