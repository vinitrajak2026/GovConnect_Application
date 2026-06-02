from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.contrib import messages
from decimal import Decimal
import json

from .models import (
    State, Category, Exam, Job, Scheme, Scholarship, Result, AdmitCard,
    CurrentAffairs, Quiz, QuizQuestion, GovService, Notification, ForumPost,
    ForumComment, UserBookmark
)
from users.models import User, UserProfile, UserActivityLog
from .recommendation import check_scheme_eligibility, recommend_schemes, recommend_exams

# --- 1. HOME INDEX VIEW ---
def index(request):
    """
    Main portal home screen with breaking news notifications, fast searches, and counts.
    """
    breaking_news = Notification.objects.order_by('-created_at')[:4]
    
    context = {
        'breaking_news': breaking_news,
        'exam_count': Exam.objects.filter(is_deleted=False).count(),
        'job_count': Job.objects.filter(is_deleted=False).count(),
        'scheme_count': Scheme.objects.filter(is_deleted=False).count(),
        'scholarship_count': Scholarship.objects.filter(is_deleted=False).count(),
    }
    return render(request, 'portal/index.html', context)

# --- 2. GLOBAL SEARCH SYSTEM ---
def global_search(request):
    """
    Unified global search with autocomplete suggestions and combined database results.
    """
    query = request.GET.get('q', '').strip()
    suggest = request.GET.get('suggest', 'false') == 'true'

    if suggest:
        # Autocomplete suggestions (AJAX)
        suggestions = []
        if query:
            exams = Exam.objects.filter(name__icontains=query, is_deleted=False)[:3]
            jobs = Job.objects.filter(post_name__icontains=query, is_deleted=False)[:3]
            schemes = Scheme.objects.filter(name__icontains=query, is_deleted=False)[:3]
            
            for e in exams:
                suggestions.append({'title': e.name, 'type': 'Exam', 'url': f'/exams/{e.id}/'})
            for j in jobs:
                suggestions.append({'title': f"{j.post_name} ({j.department})", 'type': 'Job', 'url': f'/jobs/{j.id}/'})
            for s in schemes:
                suggestions.append({'title': s.name, 'type': 'Scheme', 'url': f'/schemes/{s.id}/'})
        return JsonResponse({'suggestions': suggestions})

    # Render full search page
    exams_res = Exam.objects.filter(Q(name__icontains=query) | Q(conducting_authority__icontains=query), is_deleted=False) if query else []
    jobs_res = Job.objects.filter(Q(post_name__icontains=query) | Q(department__icontains=query), is_deleted=False) if query else []
    schemes_res = Scheme.objects.filter(Q(name__icontains=query) | Q(eligibility_criteria__icontains=query), is_deleted=False) if query else []

    return render(request, 'portal/search_results.html', {
        'query': query,
        'exams': exams_res,
        'jobs': jobs_res,
        'schemes': schemes_res,
    })

# --- 3. EXAMS DIRECTORY MODULE ---
def exam_list(request):
    """
    Listing exams with advanced multi-select filtering and ordering parameters.
    """
    exams = Exam.objects.filter(is_deleted=False)
    categories = Category.objects.all()

    # Search & filters
    q = request.GET.get('q')
    category_id = request.GET.get('category')
    qualification = request.GET.get('qualification')
    sort_by = request.GET.get('sort_by', 'name')

    if q:
        exams = exams.filter(name__icontains=q)
    if category_id:
        exams = exams.filter(category_id=category_id)
    if qualification:
        exams = exams.filter(qualification__icontains=qualification)

    if sort_by == 'vacancy':
        exams = exams.order_by('-vacancy_count')
    else:
        exams = exams.order_by('name')

    return render(request, 'portal/exam_list.html', {
        'exams': exams,
        'categories': categories,
        'q': q,
        'category_id': category_id,
        'qualification': qualification,
        'sort_by': sort_by
    })

def exam_detail(request, pk):
    exam = get_object_or_404(Exam, id=pk, is_deleted=False)
    dates = []
    try:
        dates = json.loads(exam.important_dates)
    except:
        # Fallback if text format is written instead of raw JSON
        dates = exam.important_dates.split('\n')

    # Check if bookmarked
    is_bookmarked = False
    if request.user.is_authenticated:
        ct = ContentType.objects.get_for_model(Exam)
        is_bookmarked = UserBookmark.objects.filter(user=request.user, content_type=ct, object_id=exam.id).exists()

    return render(request, 'portal/exam_detail.html', {
        'exam': exam,
        'dates': dates,
        'is_bookmarked': is_bookmarked
    })

# --- 4. JOBS DIRECTORY MODULE ---
def job_list(request):
    jobs = Job.objects.filter(is_deleted=False)
    states = State.objects.all()

    q = request.GET.get('q')
    state_id = request.GET.get('state')
    qualification = request.GET.get('qualification')

    if q:
        jobs = jobs.filter(Q(post_name__icontains=q) | Q(department__icontains=q))
    if state_id:
        jobs = jobs.filter(state_id=state_id)
    if qualification:
        jobs = jobs.filter(qualification__icontains=qualification)

    jobs = jobs.order_by('last_date')

    return render(request, 'portal/job_list.html', {
        'jobs': jobs,
        'states': states,
        'q': q,
        'state_id': state_id,
        'qualification': qualification
    })

def job_detail(request, pk):
    job = get_object_or_404(Job, id=pk, is_deleted=False)
    is_bookmarked = False
    if request.user.is_authenticated:
        ct = ContentType.objects.get_for_model(Job)
        is_bookmarked = UserBookmark.objects.filter(user=request.user, content_type=ct, object_id=job.id).exists()

    return render(request, 'portal/job_detail.html', {
        'job': job,
        'is_bookmarked': is_bookmarked
    })

# --- 5. SCHEMES & ELIGIBILITY CALCULATOR MODULE ---
def scheme_list(request):
    schemes = Scheme.objects.filter(is_deleted=False)
    states = State.objects.all()
    categories = [cat[0] for cat in Scheme.SCHEME_CATEGORY_CHOICES]

    cat = request.GET.get('category')
    state_id = request.GET.get('state')
    q = request.GET.get('q')

    if q:
        schemes = schemes.filter(name__icontains=q)
    if cat:
        schemes = schemes.filter(category=cat)
    if state_id:
        schemes = schemes.filter(state_id=state_id)

    return render(request, 'portal/scheme_list.html', {
        'schemes': schemes,
        'states': states,
        'categories': categories,
        'cat': cat,
        'state_id': state_id,
        'q': q
    })

def scheme_detail(request, pk):
    scheme = get_object_or_404(Scheme, id=pk, is_deleted=False)
    is_bookmarked = False
    if request.user.is_authenticated:
        ct = ContentType.objects.get_for_model(Scheme)
        is_bookmarked = UserBookmark.objects.filter(user=request.user, content_type=ct, object_id=scheme.id).exists()

    return render(request, 'portal/scheme_detail.html', {
        'scheme': scheme,
        'is_bookmarked': is_bookmarked
    })

def scheme_eligibility_check(request, pk):
    """
    API endpoint/AJAX action to calculate eligibility for a specific scheme based on user criteria.
    """
    scheme = get_object_or_404(Scheme, id=pk, is_deleted=False)
    
    if request.method == 'POST':
        try:
            age = int(request.POST.get('age', 0))
            gender = request.POST.get('gender', 'Any')
            income = float(request.POST.get('income', 0))
            occupation = request.POST.get('occupation', 'Student')
            
            state_id = request.POST.get('state')
            state_obj = State.objects.filter(id=state_id).first() if state_id else None

            res = check_scheme_eligibility(scheme, age, gender, state_obj, income, occupation)
            # convert decimal for JSON serialization
            res['benefit_amount'] = float(res['benefit_amount'])
            
            return JsonResponse({'success': True, 'result': res})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'POST method required.'})

# --- 6. SCHOLARSHIPS DIRECTORY MODULE ---
def scholarship_list(request):
    scholarships = Scholarship.objects.filter(is_deleted=False)
    states = State.objects.all()

    q = request.GET.get('q')
    state_id = request.GET.get('state')
    class_level = request.GET.get('class_level')

    if q:
        scholarships = scholarships.filter(name__icontains=q)
    if state_id:
        scholarships = scholarships.filter(state_id=state_id)
    if class_level:
        scholarships = scholarships.filter(class_level__icontains=class_level)

    return render(request, 'portal/scholarship_list.html', {
        'scholarships': scholarships,
        'states': states,
        'q': q,
        'state_id': state_id,
        'class_level': class_level
    })

# --- 7. RESULTS & ADMIT CARDS ---
def results_list(request):
    results = Result.objects.filter(active=True).order_by('-result_date')
    return render(request, 'portal/results_list.html', {'results': results})

def admit_cards_list(request):
    cards = AdmitCard.objects.filter(active=True).order_by('-release_date')
    return render(request, 'portal/admit_cards_list.html', {'cards': cards})

# --- 8. CURRENT AFFAIRS & QUIZZES MODULE ---
def current_affairs_list(request):
    articles = CurrentAffairs.objects.all().order_by('-pub_date')
    categories = [cat[0] for cat in CurrentAffairs.CA_CATEGORY_CHOICES]

    cat = request.GET.get('category')
    if cat:
        articles = articles.filter(category=cat)

    quizzes = Quiz.objects.all().order_by('-created_at')

    return render(request, 'portal/current_affairs_list.html', {
        'articles': articles,
        'categories': categories,
        'cat': cat,
        'quizzes': quizzes
    })

def current_affairs_detail(request, pk):
    article = get_object_or_404(CurrentAffairs, id=pk)
    return render(request, 'portal/current_affairs_detail.html', {'article': article})

def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, id=pk)
    return render(request, 'portal/quiz_detail.html', {'quiz': quiz})

def quiz_submit(request, pk):
    """
    Submits and grades quiz results via AJAX.
    """
    quiz = get_object_or_404(Quiz, id=pk)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            answers = data.get('answers', {}) # Dict like { "question_id": "A" }
            
            score = 0
            total_questions = quiz.questions.count()
            results = []

            for q in quiz.questions.all():
                user_ans = answers.get(str(q.id))
                correct = q.correct_answer
                is_correct = (user_ans == correct)
                if is_correct:
                    score += 1
                
                results.append({
                    'question_id': q.id,
                    'user_answer': user_ans,
                    'correct_answer': correct,
                    'is_correct': is_correct
                })

            percentage = (score / total_questions) * 100 if total_questions > 0 else 0
            
            # Log citizen test interaction
            if request.user.is_authenticated:
                UserActivityLog.objects.create(
                    user=request.user,
                    action="Completed Quiz",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    details=f"Scored {score}/{total_questions} ({percentage:.1f}%) on Quiz: {quiz.title}"
                )

            return JsonResponse({
                'success': True,
                'score': score,
                'total': total_questions,
                'percentage': percentage,
                'results': results
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'POST method needed.'})

# --- 9. GOVERNMENT SERVICES DIRECTORY ---
def services_list(request):
    services = GovService.objects.all().order_by('name')
    return render(request, 'portal/services_list.html', {'services': services})

# --- 10. DISCUSSION FORUM MODULE ---
def forum_list(request):
    posts = ForumPost.objects.all().annotate(
        comment_count=Count('comments'),
        upvote_count=Count('upvotes')
    ).order_by('-created_at')
    
    return render(request, 'portal/forum_list.html', {'posts': posts})

def forum_detail(request, pk):
    post = get_object_or_404(ForumPost, id=pk)
    comments = post.comments.all().annotate(upvote_count=Count('upvotes')).order_by('created_at')
    
    return render(request, 'portal/forum_detail.html', {
        'post': post,
        'comments': comments
    })

@login_required
def create_forum_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            post = ForumPost.objects.create(
                title=title,
                content=content,
                author=request.user
            )
            UserActivityLog.objects.create(
                user=request.user,
                action="Created Forum Post",
                ip_address=request.META.get('REMOTE_ADDR'),
                details=f"Posted topic: {title}"
            )
            messages.success(request, "Forum post created successfully!")
            return redirect('portal:forum_detail', pk=post.id)
    return redirect('portal:forum_list')

@login_required
def create_forum_comment(request, pk):
    post = get_object_or_404(ForumPost, id=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            ForumComment.objects.create(
                post=post,
                content=content,
                author=request.user
            )
            UserActivityLog.objects.create(
                user=request.user,
                action="Created Forum Comment",
                ip_address=request.META.get('REMOTE_ADDR'),
                details=f"Commented on post: {post.title}"
            )
            messages.success(request, "Comment posted successfully!")
    return redirect('portal:forum_detail', pk=post.id)

@login_required
def toggle_post_upvote(request, pk):
    post = get_object_or_404(ForumPost, id=pk)
    user = request.user
    if post.upvotes.filter(id=user.id).exists():
        post.upvotes.remove(user)
        upvoted = False
    else:
        post.upvotes.add(user)
        post.downvotes.remove(user) # remove downvote if exists
        upvoted = True
    return JsonResponse({'upvoted': upvoted, 'count': post.upvotes.count()})

# --- 11. GENERIC BOOKMARK TOGGLER ---
@login_required
def toggle_bookmark(request):
    """
    AJAX endpoint to save or unsave any portal item (Exam, Job, Scheme) generically.
    """
    model_name = request.POST.get('model')  # 'exam', 'job', 'scheme'
    object_id = request.POST.get('id')

    if not model_name or not object_id:
        return JsonResponse({'success': False, 'error': 'Missing parameters.'})

    # Resolve content type
    model_mapping = {
        'exam': Exam,
        'job': Job,
        'scheme': Scheme
    }
    model_cls = model_mapping.get(model_name.lower())
    if not model_cls:
        return JsonResponse({'success': False, 'error': 'Invalid model type.'})

    obj = get_object_or_404(model_cls, id=object_id)
    ct = ContentType.objects.get_for_model(model_cls)

    bookmark = UserBookmark.objects.filter(user=request.user, content_type=ct, object_id=obj.id)
    if bookmark.exists():
        bookmark.delete()
        action = "removed"
    else:
        UserBookmark.objects.create(user=request.user, content_type=ct, object_id=obj.id)
        action = "added"

    # Log action
    UserActivityLog.objects.create(
        user=request.user,
        action=f"Toggled Bookmark ({model_name})",
        ip_address=request.META.get('REMOTE_ADDR'),
        details=f"Set bookmark status of {obj} to {action}"
    )

    return JsonResponse({'success': True, 'action': action})

# --- 12. ADMIN ANALYTICS DASHBOARD ---
@login_required
@user_passes_test(lambda u: u.is_staff or u.is_admin_user or u.is_moderator)
def admin_analytics_dashboard(request):
    """
    Moderator / Admin statistics page powered by Chart.js.
    """
    return render(request, 'portal/admin_dashboard.html')

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_admin_user or u.is_moderator)
def admin_analytics_data(request):
    """
    JSON API for Chart.js dashboard loading.
    """
    # 1. Total Counts
    total_citizens = User.objects.filter(is_citizen=True).count()
    total_moderators = User.objects.filter(is_moderator=True).count()
    total_exams = Exam.objects.filter(is_deleted=False).count()
    total_jobs = Job.objects.filter(is_deleted=False).count()
    total_schemes = Scheme.objects.filter(is_deleted=False).count()

    # 2. Popular Exams by Bookmark count
    exam_ct = ContentType.objects.get_for_model(Exam)
    popular_exams = UserBookmark.objects.filter(content_type=exam_ct).values('object_id').annotate(
        count=Count('object_id')
    ).order_by('-count')[:5]
    
    exam_data = []
    for pe in popular_exams:
        exam_obj = Exam.objects.filter(id=pe['object_id']).first()
        if exam_obj:
            exam_data.append({'name': exam_obj.name, 'bookmarks': pe['count']})

    # 3. Popular Schemes by Bookmark count
    scheme_ct = ContentType.objects.get_for_model(Scheme)
    popular_schemes = UserBookmark.objects.filter(content_type=scheme_ct).values('object_id').annotate(
        count=Count('object_id')
    ).order_by('-count')[:5]

    scheme_data = []
    for ps in popular_schemes:
        scheme_obj = Scheme.objects.filter(id=ps['object_id']).first()
        if scheme_obj:
            scheme_data.append({'name': scheme_obj.name, 'bookmarks': ps['count']})

    # 4. User Registrations growth trend (by date joined)
    registrations = User.objects.extra(select={'date': "date(date_joined)"}).values('date').annotate(
        count=Count('id')
    ).order_by('date')[:15]
    # format date serialization
    reg_data = []
    for r in registrations:
        reg_data.append({'date': str(r['date']), 'count': r['count']})

    return JsonResponse({
        'counts': {
            'citizens': total_citizens,
            'moderators': total_moderators,
            'exams': total_exams,
            'jobs': total_jobs,
            'schemes': total_schemes
        },
        'popular_exams': exam_data,
        'popular_schemes': scheme_data,
        'registrations_trend': reg_data
    })
