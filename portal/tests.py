from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import UserProfile
from .models import State, Category, Scheme, Exam, UserBookmark
from .recommendation import recommend_schemes, recommend_exams, check_scheme_eligibility

User = get_user_model()

class AIRecommendationsTestCase(TestCase):
    def setUp(self):
        # States & Categories
        self.state_ka = State.objects.create(name="Karnataka", code="KA")
        self.state_mh = State.objects.create(name="Maharashtra", code="MH")
        self.category = Category.objects.create(name="Central Jobs", slug="central-jobs")

        # Create Citizen
        self.user = User.objects.create_user(
            username="student_user",
            email="stud@univ.edu",
            password="testpassword"
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            qualification="Graduate",
            state=self.state_ka,
            occupation="Student",
            gender="Male",
            age=22,
            annual_income=120000.00
        )

        # Create Scheme 1: Matching
        self.scheme_match = Scheme.objects.create(
            name="Free Books for Karnataka Students",
            category="Students",
            eligibility_criteria="Karnataka student with income under 2L",
            income_limit=200000.00,
            min_age=15,
            max_age=25,
            gender_requirement="Any",
            state=self.state_ka,
            benefit_amount=5000.00
        )

        # Create Scheme 2: Non-matching State
        self.scheme_no_match_state = Scheme.objects.create(
            name="Free Books for Maharashtra Students",
            category="Students",
            eligibility_criteria="Maharashtra student",
            income_limit=200000.00,
            min_age=15,
            max_age=25,
            gender_requirement="Any",
            state=self.state_mh,
            benefit_amount=6000.00
        )

        # Create Scheme 3: Non-matching Income
        self.scheme_no_match_income = Scheme.objects.create(
            name="Elite Graduate Allowance",
            category="Students",
            eligibility_criteria="Low income limits only",
            income_limit=50000.00,
            min_age=15,
            max_age=25,
            gender_requirement="Any",
            state=self.state_ka,
            benefit_amount=10000.00
        )

        # Create Exam
        self.exam = Exam.objects.create(
            name="State Clerk Recruitment Exam",
            conducting_authority="KPSC",
            category=self.category,
            qualification="Graduate",
            age_limit=28,
            fees=100.00,
            important_dates="[]",
            eligibility="Clean record",
            exam_pattern="MCQ",
            syllabus="GK, Math",
            vacancy_count=150,
            official_website="https://kpsc.gov"
        )

    def test_scheme_matching_engine(self):
        recs = recommend_schemes(self.profile)
        # Should only recommend scheme_match (as others have state/income exclusion)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]['scheme'].id, self.scheme_match.id)
        self.assertEqual(recs[0]['benefit'], 5000.00)

    def test_exam_matching_engine(self):
        recs = recommend_exams(self.profile)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]['exam'].id, self.exam.id)

    def test_custom_demographics_checker(self):
        # Eligible check
        res = check_scheme_eligibility(
            self.scheme_match, age=21, gender="Male", state=self.state_ka,
            income=100000.00, occupation="Student"
        )
        self.assertTrue(res['eligible'])
        self.assertEqual(res['benefit_amount'], 5000.00)

        # Excluded state check
        res_fail = check_scheme_eligibility(
            self.scheme_match, age=21, gender="Male", state=self.state_mh,
            income=100000.00, occupation="Student"
        )
        self.assertFalse(res_fail['eligible'])
