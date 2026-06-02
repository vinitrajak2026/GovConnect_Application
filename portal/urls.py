from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.global_search, name='global_search'),
    
    # Exams
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/<int:pk>/', views.exam_detail, name='exam_detail'),
    
    # Jobs
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    
    # Schemes
    path('schemes/', views.scheme_list, name='scheme_list'),
    path('schemes/<int:pk>/', views.scheme_detail, name='scheme_detail'),
    path('schemes/<int:pk>/check/', views.scheme_eligibility_check, name='scheme_eligibility_check'),
    
    # Scholarships
    path('scholarships/', views.scholarship_list, name='scholarship_list'),
    
    # Results & Admit Cards
    path('results/', views.results_list, name='results_list'),
    path('admit-cards/', views.admit_cards_list, name='admit_cards_list'),
    
    # Current Affairs & Quizzes
    path('current-affairs/', views.current_affairs_list, name='current_affairs_list'),
    path('current-affairs/<int:pk>/', views.current_affairs_detail, name='current_affairs_detail'),
    path('quiz/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:pk>/submit/', views.quiz_submit, name='quiz_submit'),
    
    # Services
    path('services/', views.services_list, name='services_list'),
    
    # Forum
    path('forum/', views.forum_list, name='forum_list'),
    path('forum/<int:pk>/', views.forum_detail, name='forum_detail'),
    path('forum/post/create/', views.create_forum_post, name='create_forum_post'),
    path('forum/comment/create/<int:pk>/', views.create_forum_comment, name='create_forum_comment'),
    path('forum/post/upvote/<int:pk>/', views.toggle_post_upvote, name='toggle_post_upvote'),
    
    # Bookmarks
    path('bookmark/toggle/', views.toggle_bookmark, name='toggle_bookmark'),
    
    # Analytics
    path('admin-dashboard/', views.admin_analytics_dashboard, name='admin_dashboard'),
    path('admin-dashboard/data/', views.admin_analytics_data, name='admin_analytics_data'),
]
