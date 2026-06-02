from decimal import Decimal
from django.db.models import Q
from .models import Scheme, Exam

# Hierarchy of qualifications to check eligibility
QUALIFICATION_LEVELS = {
    '10th': 1,
    '12th': 2,
    'Graduate': 3,
    'PostGraduate': 4,
    'Doctorate': 5
}

def get_qualification_level(qual_str):
    """Normalize and get rank of qualification."""
    if not qual_str:
        return 1
    # Simple normalizations
    clean = qual_str.strip().lower()
    if '10' in clean:
        return 1
    if '12' in clean:
        return 2
    if 'post' in clean:
        return 4
    if 'doc' in clean or 'phd' in clean:
        return 5
    if 'grad' in clean:
        return 3
    return 1

def recommend_schemes(user_profile):
    """
    Recommends schemes to a citizen based on their profile.
    Returns a list of dictionaries with 'scheme' and 'score'.
    """
    if not user_profile:
        return []

    age = user_profile.age
    gender = user_profile.gender
    income = user_profile.annual_income
    occupation = user_profile.occupation
    state = user_profile.state

    schemes = Scheme.objects.filter(is_deleted=False)
    recommendations = []

    for scheme in schemes:
        score = 0
        reasons = []
        is_eligible = True

        # 1. State Filter (Hard Exclusion)
        if scheme.state:
            if state and scheme.state.id == state.id:
                score += 50
                reasons.append("State matching matches regional benefits.")
            else:
                is_eligible = False
                reasons.append("Scheme restricted to another state.")
        else:
            score += 30  # Central schemes are universally open
            reasons.append("Central scheme available nationwide.")

        # 2. Income Limit Check (Hard Exclusion)
        if income > scheme.income_limit:
            is_eligible = False
            reasons.append(f"Income Rs. {income:,.2f} exceeds threshold Rs. {scheme.income_limit:,.2f}.")
        else:
            score += 30
            reasons.append("Income within eligible bracket.")

        # 3. Age Limit Check (Hard Exclusion)
        if age < scheme.min_age or age > scheme.max_age:
            is_eligible = False
            reasons.append(f"Age {age} outside required range of {scheme.min_age}-{scheme.max_age} years.")
        else:
            score += 30
            reasons.append("Age within required parameters.")

        # 4. Gender Requirement (Hard Exclusion)
        if scheme.gender_requirement != 'Any':
            if scheme.gender_requirement.lower() == gender.lower():
                score += 30
                reasons.append(f"Targeted gender program for {gender}s.")
            else:
                is_eligible = False
                reasons.append(f"Program intended for {scheme.gender_requirement} applicants.")
        else:
            score += 15
            reasons.append("Universal gender accessibility.")

        # 5. Occupation Alignment (Soft Boost)
        # Map occupation to category
        occupation_to_category = {
            'Farmer': 'Farmers',
            'Student': 'Students',
            'SeniorCitizen': 'Senior Citizens',
            'Business': 'Businesses',
            'SelfEmployed': 'Startups',
        }
        target_cat = occupation_to_category.get(occupation)
        if target_cat and scheme.category == target_cat:
            score += 45
            reasons.append(f"Direct match for your profile as a {occupation}.")
        elif scheme.category == 'General':
            score += 10
            reasons.append("General public program.")

        if is_eligible and score > 0:
            recommendations.append({
                'scheme': scheme,
                'score': score,
                'reasons': reasons,
                'benefit': scheme.benefit_amount
            })

    # Sort by descending recommendation score
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations

def recommend_exams(user_profile):
    """
    Recommends government exams based on qualification and age limitations.
    """
    if not user_profile:
        return []

    age = user_profile.age
    qualification = user_profile.qualification
    user_level = QUALIFICATION_LEVELS.get(qualification, 3)

    exams = Exam.objects.filter(is_deleted=False)
    recommendations = []

    for exam in exams:
        score = 0
        reasons = []
        is_eligible = True

        # 1. Age Limit Check (Hard Exclusion)
        if age > exam.age_limit:
            is_eligible = False
            reasons.append(f"Age {age} exceeds the maximum allowed age of {exam.age_limit}.")
        else:
            score += 40
            reasons.append(f"Age {age} is within the limit (Max: {exam.age_limit}).")

        # 2. Qualification Check (Hard Exclusion)
        exam_req_level = get_qualification_level(exam.qualification)
        if user_level < exam_req_level:
            is_eligible = False
            reasons.append(f"Requires {exam.qualification}, but your profile lists {user_profile.get_qualification_display()}.")
        else:
            score += 40
            reasons.append("Meet or exceed minimum qualification criteria.")
            # Boost score if it is a perfect match
            if user_level == exam_req_level:
                score += 20
                reasons.append("Perfect qualification alignment.")

        if is_eligible:
            recommendations.append({
                'exam': exam,
                'score': score,
                'reasons': reasons
            })

    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations

def check_scheme_eligibility(scheme, age, gender, state, income, occupation):
    """
    Calculates detailed eligibility percentage and benefit estimation for custom user input.
    """
    score = 0
    reasons = []
    is_eligible = True
    max_score = 150  # Max score representing 100% eligibility score

    # 1. State Filter
    if scheme.state:
        if state and scheme.state.id == state.id:
            score += 50
            reasons.append("State of residence matches state requirements.")
        else:
            is_eligible = False
            reasons.append(f"Required: {scheme.state.name}. Your location does not match.")
    else:
        score += 30
        reasons.append("Central government scheme; open to all states.")

    # 2. Income Check
    if income > scheme.income_limit:
        is_eligible = False
        reasons.append(f"Income Rs. {income:,.2f} exceeds ceiling of Rs. {scheme.income_limit:,.2f}.")
    else:
        score += 30
        reasons.append(f"Annual income is within ceiling (ceiling: Rs. {scheme.income_limit:,.2f}).")

    # 3. Age Check
    if age < scheme.min_age or age > scheme.max_age:
        is_eligible = False
        reasons.append(f"Age {age} lies outside eligible criteria of {scheme.min_age}-{scheme.max_age} years.")
    else:
        score += 30
        reasons.append(f"Age {age} falls inside the target range of {scheme.min_age}-{scheme.max_age} years.")

    # 4. Gender Requirement
    if scheme.gender_requirement != 'Any':
        if scheme.gender_requirement.lower() == gender.lower():
            score += 20
            reasons.append(f"Targeted program for {gender} gender group.")
        else:
            is_eligible = False
            reasons.append(f"Required gender: {scheme.gender_requirement}.")
    else:
        score += 10
        reasons.append("Universal accessibility for all gender identities.")

    # 5. Occupation Match
    occupation_to_category = {
        'Farmer': 'Farmers',
        'Student': 'Students',
        'SeniorCitizen': 'Senior Citizens',
        'Business': 'Businesses',
        'SelfEmployed': 'Startups',
    }
    target_cat = occupation_to_category.get(occupation)
    if target_cat and scheme.category == target_cat:
        score += 20
        reasons.append(f"Direct match for occupation: {occupation}.")
    elif scheme.category == 'General':
        score += 10
        reasons.append("Universal citizen program.")

    match_percent = min(100.0, float((score / max_score) * 100)) if is_eligible else 0.0

    return {
        'eligible': is_eligible,
        'match_percentage': round(match_percent, 1),
        'reasons': reasons,
        'benefit_amount': scheme.benefit_amount if is_eligible else Decimal('0.00')
    }
