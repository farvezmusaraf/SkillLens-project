-- ==========================================================
-- SkillLens Hackathon MVP Database Schema (Supabase PostgreSQL)
-- Refocused for Beginners: 4 Core Skills (Python, HTML, CSS, JS)
-- ==========================================================

-- 1. PROFILES TABLE (Linked with Supabase Auth)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT NOT NULL,
    target_role TEXT DEFAULT 'Junior Full-Stack Starter',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. SKILLS MASTER CATALOG (4 Core Beginner Skills)
CREATE TABLE IF NOT EXISTS public.skills (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    description TEXT,
    subtopics TEXT[] NOT NULL DEFAULT '{}'
);

-- 3. USER SKILLS TABLE (Student Selected Skills)
CREATE TABLE IF NOT EXISTS public.user_skills (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    proficiency TEXT DEFAULT 'Beginner',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, skill_name)
);

-- 4. ROLE REQUIREMENTS BENCHMARK (Beginner Friendly Tracks)
CREATE TABLE IF NOT EXISTS public.role_requirements (
    id SERIAL PRIMARY KEY,
    role_name TEXT NOT NULL,
    skill_name TEXT NOT NULL,
    importance TEXT DEFAULT 'Required',
    UNIQUE(role_name, skill_name)
);

-- 5. PRACTICAL TASKS CATALOG (Short & Practical)
CREATE TABLE IF NOT EXISTS public.tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT[] NOT NULL,
    difficulty TEXT DEFAULT 'Beginner',
    estimated_time TEXT DEFAULT '15-30 mins'
);

-- 6. BEGINNER PROJECTS CATALOG (Small & Practical)
CREATE TABLE IF NOT EXISTS public.projects (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    required_skills TEXT[] NOT NULL,
    difficulty TEXT DEFAULT 'Beginner',
    implementation_steps TEXT[] NOT NULL,
    expected_outcome TEXT NOT NULL
);

-- 7. USER PROJECTS & EVIDENCE SUBMISSION
CREATE TABLE IF NOT EXISTS public.user_projects_evidence (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    project_title TEXT NOT NULL,
    target_skill TEXT NOT NULL,
    description TEXT,
    github_url TEXT NOT NULL,
    live_url TEXT,
    status TEXT DEFAULT 'Submitted',
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. READINESS REPORTS
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
-- SEED DATA: 4 Core Beginner Skills with Subtopics
-- ==========================================================
INSERT INTO public.skills (name, category, description, subtopics) VALUES
('Python', 'Programming Logic', 'A clean, beginner-friendly language great for logic, problem solving, and scripting.', ARRAY['Variables', 'Data Types', 'Conditions', 'Loops', 'Functions']),
('HTML', 'Web Structure', 'The foundational skeleton of every website. Used to display headings, paragraphs, and forms.', ARRAY['Headings', 'Paragraphs', 'Links', 'Images', 'Forms']),
('CSS', 'Web Styling', 'Adds visual style, colors, fonts, margins, and modern layouts to HTML pages.', ARRAY['Colors', 'Fonts', 'Margins', 'Padding', 'Flexbox']),
('JavaScript', 'Web Interactivity', 'Brings web pages to life with interactive buttons, clicks, alerts, and live updates.', ARRAY['Variables', 'Functions', 'Events', 'DOM Manipulation'])
ON CONFLICT (name) DO UPDATE SET
    category = EXCLUDED.category,
    description = EXCLUDED.description,
    subtopics = EXCLUDED.subtopics;

-- ==========================================================
-- SEED DATA: Role Requirements (Beginner Career Paths)
-- ==========================================================
INSERT INTO public.role_requirements (role_name, skill_name, importance) VALUES
-- Junior Full-Stack Starter
('Junior Full-Stack Starter', 'Python', 'Required'),
('Junior Full-Stack Starter', 'HTML', 'Required'),
('Junior Full-Stack Starter', 'CSS', 'Required'),
('Junior Full-Stack Starter', 'JavaScript', 'Required'),

-- Frontend Web Developer (Beginner)
('Frontend Web Developer (Beginner)', 'HTML', 'Required'),
('Frontend Web Developer (Beginner)', 'CSS', 'Required'),
('Frontend Web Developer (Beginner)', 'JavaScript', 'Required'),
('Frontend Web Developer (Beginner)', 'Python', 'Preferred'),

-- Junior Python Developer
('Junior Python Developer', 'Python', 'Required'),
('Junior Python Developer', 'HTML', 'Preferred'),
('Junior Python Developer', 'CSS', 'Preferred')
ON CONFLICT (role_name, skill_name) DO NOTHING;

-- ==========================================================
-- SEED DATA: Small & Practical Beginner Tasks
-- ==========================================================
INSERT INTO public.tasks (title, category, description, required_skills, difficulty, estimated_time) VALUES
-- Python Tasks
('Print Your Name and Bio', 'Python Logic', 'Write a Python script using variables and print() to display your name, college, and a short bio.', ARRAY['Python'], 'Beginner', '15 mins'),
('Create a Simple Calculator', 'Python Logic', 'Build a script that takes two numbers and performs addition, subtraction, multiplication, or division using conditions.', ARRAY['Python'], 'Beginner', '25 mins'),
('Check Even or Odd Number', 'Python Logic', 'Write a program that takes an integer input from the user and checks if it is even or odd using the modulo (%) operator.', ARRAY['Python'], 'Beginner', '15 mins'),

-- HTML Tasks
('Create a Basic Webpage', 'HTML Markup', 'Create an HTML page featuring an <h1> title, introduction paragraphs, and a bulleted list of your favorite topics.', ARRAY['HTML'], 'Beginner', '20 mins'),
('Add an Image and Clickable Links', 'HTML Markup', 'Add your profile picture using the <img> tag and create clickable links to your favorite websites using <a>.', ARRAY['HTML'], 'Beginner', '15 mins'),
('Create a Simple Contact Form', 'HTML Markup', 'Build an HTML <form> with input fields for Name, Email, and Message, complete with a submit button.', ARRAY['HTML'], 'Beginner', '20 mins'),

-- CSS Tasks
('Change Background & Text Colors', 'CSS Styling', 'Style a webpage with a custom background color, high-contrast dark text, and modern font families.', ARRAY['CSS'], 'Beginner', '15 mins'),
('Style a Modern Button with Hover', 'CSS Styling', 'Create a rounded button with custom padding, background color, and a smooth hover transition effect.', ARRAY['CSS'], 'Beginner', '20 mins'),
('Create a Simple Card with Flexbox', 'CSS Styling', 'Design a clean card container with borders, padding, and centered content using display: flex.', ARRAY['CSS'], 'Beginner', '25 mins'),

-- JavaScript Tasks
('Display a Welcome Alert Pop-up', 'JavaScript Basics', 'Write a simple JavaScript function that shows a welcome alert dialog when the webpage is opened.', ARRAY['JavaScript'], 'Beginner', '15 mins'),
('Create a Button Click Counter', 'JavaScript Basics', 'Add a button on your webpage and write an event listener that counts and displays how many times it was clicked.', ARRAY['JavaScript'], 'Beginner', '20 mins'),
('Validate a Simple Form Input', 'JavaScript Basics', 'Use JavaScript to check if an input field is empty before form submission, and show a helpful warning message.', ARRAY['JavaScript'], 'Beginner', '25 mins'),

-- Multi-skill Tasks
('Style an HTML Profile Card', 'HTML & CSS', 'Combine HTML structure and CSS styling to build a responsive profile card with a picture, bio, and social button.', ARRAY['HTML', 'CSS'], 'Beginner', '30 mins'),
('Interactive Color Switcher Button', 'Frontend Web', 'Build a button that changes the webpage background color dynamically between light and dark modes when clicked.', ARRAY['HTML', 'CSS', 'JavaScript'], 'Beginner', '30 mins')
ON CONFLICT DO NOTHING;

-- ==========================================================
-- SEED DATA: Small & Practical Beginner Projects
-- ==========================================================
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
ON CONFLICT (title) DO NOTHING;
