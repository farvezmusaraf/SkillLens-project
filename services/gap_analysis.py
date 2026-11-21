"""
Skill Gap Analysis Service.
Calculates skill matches, gaps, and readiness indices for target internship roles.
"""
from typing import List, Dict, Any

def analyze_skill_gap(user_skills: List[str], role_requirements: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Compares a list of user skills against a target role's requirements.
    
    :param user_skills: List of skill names student possesses, e.g. ['Python', 'Git & GitHub']
    :param role_requirements: List of dicts, e.g. [{'skill_name': 'Python', 'importance': 'Required'}, ...]
    :return: Detailed gap analysis dictionary
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
        
        # Weighting: Required skills count double compared to preferred
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
        
    # Readiness Tier
    if match_percentage >= 80:
        status_label = "Internship Ready"
        status_color = "#10b981" # Green
        status_summary = "You have nearly all essential skills! Focus on building high-impact portfolio proof."
    elif match_percentage >= 50:
        status_label = "Moderate Readiness"
        status_color = "#f59e0b" # Amber
        status_summary = "Great foundational base. Closing 1 or 2 critical gaps will make your profile stand out."
    else:
        status_label = "Early Preparation"
        status_color = "#ef4444" # Red
        status_summary = "High potential to grow. Follow the 30-day plan to master the core prerequisites step-by-step."
        
    return {
        'match_percentage': match_percentage,
        'acquired_skills': acquired_skills,
        'missing_required': missing_required,
        'missing_preferred': missing_preferred,
        'total_required_count': len([r for r in role_requirements if r.get('importance', '').lower() == 'required']),
        'total_preferred_count': len([r for r in role_requirements if r.get('importance', '').lower() == 'preferred']),
        'status_label': status_label,
        'status_color': status_color,
        'status_summary': status_summary
    }

def match_practical_tasks(user_skills: List[str], all_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Finds practical mini-projects the student can complete right now with their existing skills.
    Returns tasks sorted by highest skill coverage.
    """
    user_skill_set = set(s.strip().lower() for s in user_skills)
    matched_tasks = []
    
    for task in all_tasks:
        reqs = task.get('required_skills', [])
        req_set = set(r.strip().lower() for r in reqs)
        
        # Calculate how many of the task's required skills the student has
        have = req_set.intersection(user_skill_set)
        missing = req_set.difference(user_skill_set)
        
        coverage = len(have) / len(req_set) if req_set else 0
        
        # Include task if student has at least 50% of the skills or at least 1 skill
        if len(have) > 0:
            matched_tasks.append({
                **task,
                'skills_have': [r for r in reqs if r.strip().lower() in have],
                'skills_missing': [r for r in reqs if r.strip().lower() in missing],
                'is_ready_now': len(missing) == 0,
                'coverage_pct': int(round(coverage * 100))
            })
            
    # Sort: 100% ready first, then by coverage percentage descending
    matched_tasks.sort(key=lambda t: (t['is_ready_now'], t['coverage_pct']), reverse=True)
    return matched_tasks
