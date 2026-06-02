import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from portal.models import (
    State, Category, Exam, Job, Scheme, Scholarship, Result, AdmitCard,
    CurrentAffairs, Quiz, QuizQuestion, GovService, Notification, ForumPost,
    ForumComment, UserBookmark
)
from users.models import UserProfile, UserActivityLog

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with real-world Indian government exams, jobs, schemes, scholarships, and services.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting premium database seeding with real-world records..."))

        # Flush old records of core entities to ensure clean state and no duplicates or key clashes
        self.stdout.write("Cleaning up existing portal data...")
        AdmitCard.objects.all().delete()
        Result.objects.all().delete()
        Exam.objects.all().delete()
        Job.objects.all().delete()
        Scheme.objects.all().delete()
        Scholarship.objects.all().delete()
        CurrentAffairs.objects.all().delete()
        QuizQuestion.objects.all().delete()
        Quiz.objects.all().delete()
        GovService.objects.all().delete()
        Notification.objects.all().delete()
        Category.objects.all().delete()

        # 1. Create States & UTs
        self.stdout.write("Populating real States & UTs...")
        states_data = [
            ("Maharashtra", "MH"),
            ("Karnataka", "KA"),
            ("Delhi", "DL"),
            ("Tamil Nadu", "TN"),
            ("Gujarat", "GJ"),
            ("Uttar Pradesh", "UP"),
            ("West Bengal", "WB"),
            ("Rajasthan", "RJ"),
            ("Telangana", "TG"),
            ("Kerala", "KL"),
            ("Madhya Pradesh", "MP"),
            ("Punjab", "PB"),
            ("Andhra Pradesh", "AP"),
            ("Bihar", "BR"),
        ]
        states_map = {}
        for name, code in states_data:
            state, _ = State.objects.get_or_create(name=name, defaults={"code": code})
            states_map[code] = state

        # 2. Create Categories
        self.stdout.write("Populating real Categories...")
        categories_data = [
            ("Civil Services", "civil-services", "Recruitment exams for premium administration roles including IAS, IPS, and IFS."),
            ("Banking & Finance", "banking-finance", "Nationalized and public sector bank recruitments (SBI, IBPS, RBI)."),
            ("Defense & Police", "defense-police", "Armed forces entrance exams, NDA, CDS, police sub-inspectors, and constables."),
            ("Engineering & Technology", "engineering-tech", "Technical officer positions, PSUs, ISRO, DRDO, and railway technical roles."),
            ("Staff & Administrative", "staff-admin", "General clerical, multi-tasking staff, stenographers, and executive assistants (SSC)."),
        ]
        categories_map = {}
        for name, slug, desc in categories_data:
            cat, _ = Category.objects.get_or_create(name=name, defaults={"slug": slug, "description": desc})
            categories_map[slug] = cat

        # 3. Create Exams
        self.stdout.write("Populating real Exams...")
        exams_data = [
            {
                "name": "UPSC Civil Services Examination",
                "conducting_authority": "Union Public Service Commission (UPSC)",
                "category": categories_map["civil-services"],
                "qualification": "Graduate",
                "age_limit": 32,
                "fees": 100.00,
                "important_dates": "Prelims: June 2026, Mains: September 2026, Interview: Dec 2026",
                "eligibility": "Must hold a Bachelor's Degree in any discipline from a recognized university. Age must be between 21 and 32 years with relaxation up to 5 years for SC/ST and 3 years for OBC.",
                "exam_pattern": "Three stages: 1. Prelims (MCQs - General Studies & CSAT), 2. Mains (9 written essay papers), 3. Personality Test (Interview).",
                "syllabus": "History, Geography, Polity, Economics, Environment, Science & Tech, International Relations, Ethics, and optional descriptive subjects.",
                "vacancy_count": 1056,
                "official_website": "https://upsc.gov.in"
            },
            {
                "name": "SBI Probationary Officer (PO) Examination",
                "conducting_authority": "State Bank of India (SBI)",
                "category": categories_map["banking-finance"],
                "qualification": "Graduate",
                "age_limit": 30,
                "fees": 750.00,
                "important_dates": "Registration: September 2026, Prelims: November 2026, Mains: December 2026",
                "eligibility": "Graduation in any discipline from a recognized University or any equivalent qualification recognized as such by the Central Government.",
                "exam_pattern": "Phase I: Preliminary Exam (Objective - English, Quant, Reasoning), Phase II: Main Exam (Objective + Descriptive), Phase III: Psychometric Test & Interview.",
                "syllabus": "Data Analysis & Interpretation, Reasoning & Computer Aptitude, General/Economy/Banking Awareness, English Language.",
                "vacancy_count": 2000,
                "official_website": "https://sbi.co.in"
            },
            {
                "name": "SSC Combined Graduate Level (CGL) Exam",
                "conducting_authority": "Staff Selection Commission (SSC)",
                "category": categories_map["staff-admin"],
                "qualification": "Graduate",
                "age_limit": 30,
                "fees": 100.00,
                "important_dates": "Registration: June 2026, Tier-I Exam: September 2026, Tier-II: December 2026",
                "eligibility": "Bachelor's Degree from a recognized University or equivalent. Special posts like JSAs require specific Math/Stats subjects.",
                "exam_pattern": "Computer Based Examinations conducted in two Tiers (Tier-I and Tier-II).",
                "syllabus": "Quantitative Aptitude, General Intelligence & Reasoning, English Comprehension, General Awareness, and basic computer proficiency.",
                "vacancy_count": 7500,
                "official_website": "https://ssc.gov.in"
            },
            {
                "name": "GATE (Graduate Aptitude Test in Engineering)",
                "conducting_authority": "Indian Institute of Technology (IIT) Roorkee",
                "category": categories_map["engineering-tech"],
                "qualification": "Graduate",
                "age_limit": 99,
                "fees": 1800.00,
                "important_dates": "Registration: Sept 2026, Exam: Feb 2027",
                "eligibility": "Candidates currently in 3rd year or higher of any undergraduate degree program in Engineering / Technology / Architecture / Science / Commerce / Arts.",
                "exam_pattern": "Computer-based test (CBT) consisting of Multiple Choice Questions (MCQ), Multiple Select Questions (MSQ), and Numerical Answer Type (NAT) questions.",
                "syllabus": "Engineering Mathematics, General Aptitude, and specific technical core subject papers (CS, EE, ME, EC, CE, etc.).",
                "vacancy_count": 0,
                "official_website": "https://gate.iitr.ac.in"
            },
            {
                "name": "NDA & NA Entrance Examination",
                "conducting_authority": "Union Public Service Commission (UPSC)",
                "category": categories_map["defense-police"],
                "qualification": "12th Pass",
                "age_limit": 19,
                "fees": 100.00,
                "important_dates": "NDA I Exam: April 2026, NDA II Exam: September 2026",
                "eligibility": "For Army Wing: 12th Class pass. For Air Force and Navy Wings: 12th Class pass with Physics and Mathematics. Candidates must be unmarried males or females aged between 16.5 and 19.5.",
                "exam_pattern": "Written Exam (Paper-I: Mathematics, Paper-II: General Ability Test) followed by Services Selection Board (SSB) Interviews.",
                "syllabus": "Algebra, Trigonometry, Calculus, English, Physics, Chemistry, General Science, History, Geography, and Current Events.",
                "vacancy_count": 400,
                "official_website": "https://upsc.gov.in"
            },
            {
                "name": "RBI Grade B Officer Exam",
                "conducting_authority": "Reserve Bank of India Services Board",
                "category": categories_map["banking-finance"],
                "qualification": "Graduate",
                "age_limit": 30,
                "fees": 850.00,
                "important_dates": "Phase-I: July 2026, Phase-II: August 2026",
                "eligibility": "Graduation with minimum 60% marks (50% for SC/ST/PwBD) or equivalent grade. Age limit is 21 to 30 years.",
                "exam_pattern": "Phase I (Objective MCQs), Phase II (Three papers: Economic & Social Issues, English, Finance & Management), Phase III (Interview).",
                "syllabus": "Growth & Development, Indian Economy, Global Financial System, Finance Markets, Management Principles, General Awareness.",
                "vacancy_count": 291,
                "official_website": "https://rbi.org.in"
            }
        ]
        exams_map = {}
        for ex in exams_data:
            exam = Exam.objects.create(**ex)
            exams_map[ex["name"]] = exam

        # 4. Create Jobs
        self.stdout.write("Populating real Job openings...")
        jobs_data = [
            {
                "department": "State Bank of India (SBI)",
                "post_name": "Probationary Officer (PO)",
                "vacancies": 2000,
                "salary_range": "₹41,960 - ₹63,840 per month",
                "qualification": "Graduate",
                "last_date": datetime.date(2026, 10, 15),
                "state": None,
                "official_notification": "https://sbi.co.in/careers"
            },
            {
                "department": "Ministry of Home Affairs - Intelligence Bureau",
                "post_name": "Assistant Central Intelligence Officer (ACIO) Grade-II",
                "vacancies": 995,
                "salary_range": "₹44,900 - ₹1,42,400 (Level 7)",
                "qualification": "Graduate",
                "last_date": datetime.date(2026, 9, 5),
                "state": None,
                "official_notification": "https://mha.gov.in"
            },
            {
                "department": "Indian Space Research Organisation (ISRO)",
                "post_name": "Scientist / Engineer 'SC' (Electronics/Mechanical/Computer Science)",
                "vacancies": 80,
                "salary_range": "₹56,100 - ₹1,77,500 (Level 10)",
                "qualification": "Graduate",
                "last_date": datetime.date(2026, 12, 15),
                "state": states_map["KA"], # Karnataka (HQ is Bangalore)
                "official_notification": "https://isro.gov.in"
            },
            {
                "department": "Delhi Police Force",
                "post_name": "Sub-Inspector (SI) of Police",
                "vacancies": 1800,
                "salary_range": "₹35,400 - ₹1,12,400 (Level 6)",
                "qualification": "Graduate",
                "last_date": datetime.date(2026, 8, 30),
                "state": states_map["DL"], # Delhi
                "official_notification": "https://ssc.gov.in"
            },
            {
                "department": "Maharashtra Revenue & Forest Department",
                "post_name": "Talathi (Revenue Officer)",
                "vacancies": 4644,
                "salary_range": "₹25,500 - ₹81,100 (S-8)",
                "qualification": "Graduate",
                "last_date": datetime.date(2026, 7, 25),
                "state": states_map["MH"], # Maharashtra
                "official_notification": "https://mahabhumi.gov.in"
            },
            {
                "department": "Railway Recruitment Board (RRB)",
                "post_name": "Assistant Station Master (ASM)",
                "vacancies": 4030,
                "salary_range": "₹35,400 - ₹1,12,400",
                "qualification": "Graduate",
                "last_date": datetime.date(2026, 10, 10),
                "state": None,
                "official_notification": "https://rrcb.gov.in"
            }
        ]
        for jb in jobs_data:
            Job.objects.create(**jb)

        # 5. Create Schemes
        self.stdout.write("Populating real Welfare Schemes...")
        schemes_data = [
            {
                "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
                "category": "Farmers",
                "eligibility_criteria": "All landholder farmer families who have cultivable landholding in their names are eligible. Excludes institutional landholders and professional taxpayers.",
                "income_limit": 9999999.00,
                "min_age": 18,
                "max_age": 100,
                "gender_requirement": "Any",
                "state": None,
                "benefit_amount": 6000.00,
                "documents_required": "Aadhaar Card, Landholding Patta papers, verified Bank Account linked with Aadhaar.",
                "application_process": "Register online via PM-KISAN portal, or visit local Common Service Centers (CSCs) for processing.",
                "official_website": "https://pmkisan.gov.in"
            },
            {
                "name": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PM-JAY)",
                "category": "Healthcare",
                "eligibility_criteria": "Families listed in SECC-2011 database under active rural indicators (kutcha house, landless, casual labor) or specific urban occupational categories.",
                "income_limit": 180000.00,
                "min_age": 0,
                "max_age": 100,
                "gender_requirement": "Any",
                "state": None,
                "benefit_amount": 500000.00,
                "documents_required": "Aadhaar Card, Ration Card, PM-JAY letter, Mobile Number.",
                "application_process": "Verify eligibility online on Mera PM-JAY. Visit any empaneled government or private hospital to issue golden e-card.",
                "official_website": "https://pmjay.gov.in"
            },
            {
                "name": "Pradhan Mantri Awas Yojana (PMAY-U / Gramin)",
                "category": "General",
                "eligibility_criteria": "Families that do not own a pucca house in any part of the country. Household income must match Economically Weaker Section (EWS) or Low Income Group (LIG) bands.",
                "income_limit": 300000.00,
                "min_age": 18,
                "max_age": 75,
                "gender_requirement": "Any",
                "state": None,
                "benefit_amount": 267000.00,
                "documents_required": "Income certificate, Aadhaar card, PAN card, Affidavit stating non-ownership of permanent houses.",
                "application_process": "Submit online request via PMAY portal or register via municipality council desks.",
                "official_website": "https://pmaymis.gov.in"
            },
            {
                "name": "Sukanya Samriddhi Yojana (SSY)",
                "category": "Women",
                "eligibility_criteria": "A savings account opened by parents/legal guardians in the name of a girl child aged 10 years or below. Maximum of two accounts per household.",
                "income_limit": 9999999.00,
                "min_age": 0,
                "max_age": 10,
                "gender_requirement": "Female",
                "state": None,
                "benefit_amount": 150000.00,
                "documents_required": "Birth Certificate of the girl child, ID proof of parents (Aadhaar, PAN), Address verification proof.",
                "application_process": "Visit any nationalized bank or India Post office branch to open Sukanya Samriddhi account and start deposits.",
                "official_website": "https://indiapost.gov.in"
            },
            {
                "name": "Pradhan Mantri Mudra Yojana (PMMY)",
                "category": "Businesses",
                "eligibility_criteria": "Non-corporate, non-farm small/micro enterprises. Loans provided in three categories: Shishu (up to ₹50k), Kishore (₹50k-₹5L), and Tarun (₹5L-₹10L).",
                "income_limit": 9999999.00,
                "min_age": 18,
                "max_age": 65,
                "gender_requirement": "Any",
                "state": None,
                "benefit_amount": 1000000.00,
                "documents_required": "Mudra application form, Business proof, Machinery quotes, Identity & address validation.",
                "application_process": "Apply online via Udyam Mitra portal or approach public sector banks, NBFCs, or MFIs directly.",
                "official_website": "https://mudra.org.in"
            },
            {
                "name": "Sanjay Gandhi Niradhar Anudan Yojana",
                "category": "Senior Citizens",
                "eligibility_criteria": "Destitute, elderly, blind, or disabled citizens residing in Maharashtra who do not have any regular sources of livelihood.",
                "income_limit": 50000.00,
                "min_age": 65,
                "max_age": 100,
                "gender_requirement": "Any",
                "state": states_map["MH"], # Maharashtra
                "benefit_amount": 12000.00,
                "documents_required": "Maharashtra Domicile Certificate, Disability certificate (if applicable), Income certificate, Age proof.",
                "application_process": "Submit physical application forms at Tehsildar or Collector office in local district blocks.",
                "official_website": "https://maharashtra.gov.in"
            }
        ]
        for sc in schemes_data:
            Scheme.objects.create(**sc)

        # 6. Create Scholarships
        self.stdout.write("Populating real Scholarships...")
        scholarships_data = [
            {
                "name": "Central Sector Scheme of Scholarship for College and University Students",
                "eligibility": "Regular college students who are above the 80th percentile of successful candidates in the relevant stream from the respective Board of Examination in Class XII.",
                "amount": 20000.00,
                "last_date": datetime.date(2026, 10, 31),
                "state": None,
                "class_level": "Undergraduate",
                "degree": "Professional Graduation (BE, MBBS, BTech, BCom, BSc)",
                "official_website": "https://scholarships.gov.in"
            },
            {
                "name": "INSPIRE Scholarship for Higher Education (SHE)",
                "eligibility": "Students within top 1% in Class XII Board examinations and pursuing courses in Natural and Basic Sciences at BSc, BS, or Integrated MS level.",
                "amount": 80000.00,
                "last_date": datetime.date(2026, 11, 30),
                "state": None,
                "class_level": "Undergraduate",
                "degree": "BSc / Integrated MSc",
                "official_website": "https://online-inspire.gov.in"
            },
            {
                "name": "Post-Matric Scholarship Scheme for SC Students",
                "eligibility": "Students belonging to Scheduled Castes studying in class XI and above courses with parents' annual family income not exceeding ₹2.5 Lakhs.",
                "amount": 12000.00,
                "last_date": datetime.date(2026, 11, 15),
                "state": None,
                "class_level": "Post-Matric",
                "degree": "All Streams",
                "official_website": "https://scholarships.gov.in"
            },
            {
                "name": "Karnataka Vidyasiri Scholarship (Pratibha Puraskar)",
                "eligibility": "OBC category meritorious candidates pursuing postgraduate or degree professional courses in Karnataka.",
                "amount": 15000.00,
                "last_date": datetime.date(2026, 9, 30),
                "state": states_map["KA"], # Karnataka
                "class_level": "Undergraduate",
                "degree": "BA, BSc, BCom, BCA",
                "official_website": "https://bcwd.karnataka.gov.in"
            }
        ]
        for sh in scholarships_data:
            Scholarship.objects.create(**sh)

        # 7. Results and Admit Cards
        self.stdout.write("Populating real Results & Admit Cards...")
        Result.objects.create(
            exam=exams_map["UPSC Civil Services Examination"],
            result_date=datetime.date(2026, 5, 20),
            download_link="https://upsc.gov.in/written-results"
        )
        Result.objects.create(
            exam=exams_map["SSC Combined Graduate Level (CGL) Exam"],
            result_date=datetime.date(2026, 4, 15),
            download_link="https://ssc.nic.in/results"
        )
        AdmitCard.objects.create(
            exam=exams_map["SBI Probationary Officer (PO) Examination"],
            release_date=datetime.date(2026, 11, 1),
            download_link="https://sbi.co.in/careers/admit-card"
        )
        AdmitCard.objects.create(
            exam=exams_map["NDA & NA Entrance Examination"],
            release_date=datetime.date(2026, 8, 20),
            download_link="https://upsc.gov.in/e-admit-cards"
        )

        # 8. Current Affairs
        self.stdout.write("Populating real Current Affairs updates...")
        ca_data = [
            {
                "title": "Cabinet Approves Quantum Mission Allocation of ₹6,003 Crore",
                "content": "The Union Cabinet chaired by the Prime Minister has approved the National Quantum Mission (NQM) with a total budget layout of ₹6,003.65 Crore. The mission aims to seed, nurture and scale up scientific and industrial R&D in Quantum Technology and associate applications over the next 8 years. India will become the sixth country worldwide to have an active research framework on high-level quantum systems.",
                "category": "Science"
            },
            {
                "title": "RBI Monetary Committee Retains Repo Rate at 6.50% in June Policy Review",
                "content": "The Reserve Bank of India (RBI) Monetary Policy Committee (MPC) has decided to keep the policy Repo Rate unchanged at 6.50% to align with consumer inflation parameters. RBI Governor Shaktikanta Das mentioned that structural GDP projections remain buoyant, standing at 7.2% for the current financial cycle, while core CPI projections are set at 4.5%.",
                "category": "Economy"
            },
            {
                "title": "India Finishes with Record 107 Medals in Hangzhou Asian Games",
                "content": "In an unprecedented sporting campaign, the Indian contingent crossed the landmark 'Abki Baar, 100 Paar' target to finish with 107 medals (28 Gold, 38 Silver, 41 Bronze). The historic performance was driven by record-breaking sprints in athletics, archery dominance, and exceptional precision in shooting.",
                "category": "Sports"
            },
            {
                "title": "Parliament Approves Digital Personal Data Protection (DPDP) Bill",
                "content": "The Digital Personal Data Protection (DPDP) Bill was officially enacted by Parliament. The framework defines secure data collection practices for online corporations, mandates explicit consent handles for citizens, and introduces severe penalties (up to ₹250 Crore) for systemic security leaks and unauthorized metadata processing.",
                "category": "Politics"
            }
        ]
        for ca in ca_data:
            CurrentAffairs.objects.create(**ca)

        # 9. Quizzes and Questions
        self.stdout.write("Populating real Quizzes...")
        quiz1, _ = Quiz.objects.get_or_create(
            title="June 2026 Policy & Economy Quiz",
            defaults={"description": "Assess your understanding of recent cabinet approvals, fiscal policies, and national allocations."}
        )
        QuizQuestion.objects.create(
            quiz=quiz1,
            question_text="What is the total budget allocation approved by the Union Cabinet for the National Quantum Mission?",
            option_a="₹4,000 Crore",
            option_b="₹5,000 Crore",
            option_c="₹6,003 Crore",
            option_d="₹8,500 Crore",
            correct_answer="C"
        )
        QuizQuestion.objects.create(
            quiz=quiz1,
            question_text="Who is the current Governor of the Reserve Bank of India (RBI) as of 2026?",
            option_a="Urjit Patel",
            option_b="Shaktikanta Das",
            option_c="Raghuram Rajan",
            option_d="Duvvuri Subbarao",
            correct_answer="B"
        )
        
        quiz2, _ = Quiz.objects.get_or_create(
            title="General Science & Indian Geography",
            defaults={"description": "Static GK preparation quiz based on basic syllabus guidelines for UPSC & SSC exams."}
        )
        QuizQuestion.objects.create(
            quiz=quiz2,
            question_text="Which state of India shares border boundaries with the maximum number of other Indian states?",
            option_a="Madhya Pradesh",
            option_b="Uttar Pradesh",
            option_c="Maharashtra",
            option_d="Assam",
            correct_answer="B"
        )
        QuizQuestion.objects.create(
            quiz=quiz2,
            question_text="Which layer of the atmosphere contains the ozone layer that protects Earth from harmful UV rays?",
            option_a="Troposphere",
            option_b="Mesosphere",
            option_c="Stratosphere",
            option_d="Thermosphere",
            correct_answer="C"
        )

        # 10. Gov Services
        self.stdout.write("Populating real Gov Services...")
        services_data = [
            {
                "name": "Issuance of PAN Card (Permanent Account Number)",
                "description": "Get your ten-digit unique alphanumeric identifier issued by the Income Tax Department.",
                "documents_required": "Proof of Identity (Aadhaar, Passport), Proof of Address, Date of Birth Proof, Passport-size photographs.",
                "fees": 110.00,
                "process": "1. Submit online application on NSDL/UTIITSL portal. 2. Verify identity via Aadhaar OTP e-KYC. 3. Physical PAN delivered via post.",
                "official_link": "https://www.onlineservices.nsdl.com"
            },
            {
                "name": "Indian Passport Application & Renewal",
                "description": "Secure a new travel document or renew expiring passport booklets through computerized consular offices.",
                "documents_required": "Address verification proof (Bank passbook, Utility bill), Birth verification proof (Birth cert, Matriculation cert), Aadhaar Card.",
                "fees": 1500.00,
                "process": "1. Fill registration online at Passport Seva Portal. 2. Pay fees & secure slot booking. 3. Visit Passport Seva Kendra center for biometrics. 4. Police verification.",
                "official_link": "https://www.passportindia.gov.in"
            },
            {
                "name": "Aadhaar Card Enrollment / Update",
                "description": "Enroll for the 12-digit unique identity number issued by UIDAI, or update your registered biometrics, phone number, and address.",
                "documents_required": "Identity Proof (Voter ID, Passport), Address Proof, Date of birth verification certificate.",
                "fees": 50.00,
                "process": "1. Locate nearest Aadhaar Enrolment Center. 2. Book appointment online. 3. Submit biometrics (fingerprints, iris scan) and documents at center. 4. Check status online.",
                "official_link": "https://uidai.gov.in"
            },
            {
                "name": "NVSP Voter ID Card Registration",
                "description": "Submit applications for registration as a new elector, transfer coordinates, or request corrections in electoral roll cards.",
                "documents_required": "Address proof, Age proof (class 10 certificate or birth certificate), Passport size photo.",
                "fees": 0.00,
                "process": "1. Register on Voter Service Portal. 2. Fill Form 6 for new enrollment. 3. Upload photo and files. 4. Physical EPIC voter card dispatched by post post-BLO verification.",
                "official_link": "https://voters.eci.gov.in"
            }
        ]
        for sv in services_data:
            GovService.objects.create(**sv)

        # 11. Notifications
        self.stdout.write("Populating real Live Notifications...")
        notifications_data = [
            ("UPSC Civil Services 2026 Mains Syllabus Clarified", "UPSC issued minor category rules for the optional subjects papers. Check details.", "Exam"),
            ("SBI PO 2026 Active Vacancies Registration Open", "Interested graduates may register on State Bank career pages until October 15.", "Job"),
            ("Ayushman Bharat Golden Card Drive Launched", "Free health cards to be distributed via all gram panchayats from next week.", "Scheme"),
            ("SSC Combined Graduate Level Tier-I Scorecard Published", "Candidates can access score sheets using registration IDs.", "Result")
        ]
        for title, content, n_type in notifications_data:
            Notification.objects.create(title=title, content=content, notification_type=n_type)

        # 12. Dummy Users & Citizen Profiles
        self.stdout.write("Creating/Verifying Citizen Account...")
        citizen_email = "citizen@example.com"
        citizen, created = User.objects.get_or_create(
            email=citizen_email,
            defaults={
                "username": "citizen",
                "is_citizen": True,
                "is_active": True
            }
        )
        if created:
            citizen.set_password("password123")
            citizen.save()
            
        profile, _ = UserProfile.objects.get_or_create(
            user=citizen,
            defaults={
                "phone": "+91 9876543210",
                "qualification": "Graduate",
                "occupation": "Student",
                "gender": "Male",
                "age": 22,
                "annual_income": 150000.00,
                "state": states_map["MH"], # MH
            }
        )

        # Log active seeding operation
        UserActivityLog.objects.create(
            user=citizen,
            action="Premium Database Seeding",
            details="Successfully cleared legacy records and seeded authentic, real-world Indian government portal assets."
        )

        self.stdout.write(self.style.SUCCESS("Real-world Indian government database populated successfully! Ready to test!"))
