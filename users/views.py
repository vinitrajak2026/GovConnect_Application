from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import User, UserProfile, UserActivityLog
from portal.models import State, Scheme, Exam, Job, UserBookmark
from portal.recommendation import recommend_schemes, recommend_exams

def citizen_register(request):
    """
    Handle citizen registration including demographic details.
    """
    if request.user.is_authenticated:
        return redirect('users:dashboard')

    states = State.objects.all()
    qualifications = UserProfile.QUALIFICATION_CHOICES
    occupations = UserProfile.OCCUPATION_CHOICES
    genders = UserProfile.GENDER_CHOICES

    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username') or email.split('@')[0]
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'users/register.html', locals())

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'users/register.html', locals())

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_citizen=True
        )

        # Create profile
        state_id = request.POST.get('state')
        state_obj = State.objects.filter(id=state_id).first() if state_id else None

        profile = UserProfile.objects.create(
            user=user,
            phone=request.POST.get('phone'),
            qualification=request.POST.get('qualification', 'Graduate'),
            state=state_obj,
            occupation=request.POST.get('occupation', 'Student'),
            gender=request.POST.get('gender', 'Male'),
            age=int(request.POST.get('age', 22)),
            annual_income=float(request.POST.get('annual_income', 150000))
        )

        # Log Activity
        UserActivityLog.objects.create(
            user=user,
            action="Registration",
            ip_address=request.META.get('REMOTE_ADDR'),
            details="New citizen profile created successfully."
        )

        # Immediate login & redirect to dashboard for seamless experience
        auth_login(request, user)
        messages.success(request, f"Welcome to GovConnect! Account created successfully.")
        return redirect('users:dashboard')

    return render(request, 'users/register.html', {
        'states': states,
        'qualifications': qualifications,
        'occupations': occupations,
        'genders': genders
    })

def citizen_login(request):
    """
    Handle user login with secondary OTP security verification.
    """
    if request.user.is_authenticated:
        return redirect('users:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Django authenticate uses username, so we search by email
        user_obj = User.objects.filter(email=email).first()
        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
            if user:
                # Mock OTP Verification Step
                profile, created = UserProfile.objects.get_or_create(user=user)
                otp = profile.generate_otp()
                
                # Store authenticated user ID in session temporarily
                request.session['pre_otp_user_id'] = user.id
                messages.info(request, f"[MOCK OTP SENT VIA EMAIL]: Your verification OTP is {otp}")
                return redirect('users:verify_otp')
            else:
                messages.error(request, "Invalid password credentials.")
        else:
            messages.error(request, "No account matches that email address.")

    return render(request, 'users/login.html')

def verify_otp(request):
    """
    Verify OTP before completing user session login.
    """
    user_id = request.session.get('pre_otp_user_id')
    if not user_id:
        return redirect('users:login')

    user = get_object_or_404(User, id=user_id)
    profile = user.profile

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if profile.verify_otp(entered_otp):
            # Complete Login
            auth_login(request, user)
            del request.session['pre_otp_user_id']
            
            # Log Activity
            UserActivityLog.objects.create(
                user=user,
                action="Login (with OTP)",
                ip_address=request.META.get('REMOTE_ADDR'),
                details="Logged in securely via OTP."
            )
            
            messages.success(request, f"Welcome back, {user.email}!")
            return redirect('users:dashboard')
        else:
            messages.error(request, "Invalid or expired OTP code.")

    return render(request, 'users/verify_otp.html', {'email': user.email})

@login_required
def citizen_logout(request):
    UserActivityLog.objects.create(
        user=request.user,
        action="Logout",
        ip_address=request.META.get('REMOTE_ADDR'),
        details="Logged out of system."
    )
    auth_logout(request)
    messages.success(request, "Successfully logged out.")
    return redirect('portal:index')

@login_required
def dashboard(request):
    """
    Personalized citizen dashboard showing recommendations, bookmarks, and activities.
    """
    user = request.user
    profile = getattr(user, 'profile', None)

    # 1. Fetch Bookmark items
    bookmarks = UserBookmark.objects.filter(user=user)
    saved_exams = []
    saved_schemes = []
    saved_jobs = []

    for bm in bookmarks:
        obj = bm.content_object
        if isinstance(obj, Exam):
            saved_exams.append(obj)
        elif isinstance(obj, Scheme):
            saved_schemes.append(obj)
        elif isinstance(obj, Job):
            saved_jobs.append(obj)

    # 2. Get recommendations
    recommended_schemes_list = recommend_schemes(profile)[:5] if profile else []
    recommended_exams_list = recommend_exams(profile)[:5] if profile else []

    # 3. Activity logs
    activities = UserActivityLog.objects.filter(user=user).order_selection = '-timestamp'[:10]
    
    # Workaround for ordered activity fetch
    activities = UserActivityLog.objects.filter(user=user).order_by('-timestamp')[:5]

    return render(request, 'users/dashboard.html', {
        'profile': profile,
        'saved_exams': saved_exams,
        'saved_schemes': saved_schemes,
        'saved_jobs': saved_jobs,
        'recommended_schemes': recommended_schemes_list,
        'recommended_exams': recommended_exams_list,
        'activities': activities
    })

@login_required
def update_profile(request):
    """
    Update profile details for better matching parameters.
    """
    profile = request.user.profile
    states = State.objects.all()

    if request.method == 'POST':
        profile.phone = request.POST.get('phone')
        profile.qualification = request.POST.get('qualification')
        
        state_id = request.POST.get('state')
        profile.state = State.objects.filter(id=state_id).first() if state_id else None
        
        profile.occupation = request.POST.get('occupation')
        profile.gender = request.POST.get('gender')
        profile.age = int(request.POST.get('age', 22))
        profile.annual_income = float(request.POST.get('annual_income', 150000))
        
        profile.notification_email = 'notification_email' in request.POST
        profile.notification_browser = 'notification_browser' in request.POST
        profile.notification_sms = 'notification_sms' in request.POST
        profile.save()

        UserActivityLog.objects.create(
            user=request.user,
            action="Profile Update",
            ip_address=request.META.get('REMOTE_ADDR'),
            details="Updated profiling parameters for AI recommends."
        )

        messages.success(request, "Profile updated successfully! AI Recommendations refreshed.")
        return redirect('users:dashboard')

    return render(request, 'users/update_profile.html', {
        'profile': profile,
        'states': states,
        'qualifications': UserProfile.QUALIFICATION_CHOICES,
        'occupations': UserProfile.OCCUPATION_CHOICES,
        'genders': UserProfile.GENDER_CHOICES
    })
