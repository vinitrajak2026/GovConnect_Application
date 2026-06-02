from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    RegisterAPIView, ExamViewSet, JobViewSet, SchemeViewSet,
    ScholarshipViewSet, ResultViewSet, NotificationViewSet, ForumPostViewSet
)

router = DefaultRouter()
router.register(r'exams', ExamViewSet, basename='api_exams')
router.register(r'jobs', JobViewSet, basename='api_jobs')
router.register(r'schemes', SchemeViewSet, basename='api_schemes')
router.register(r'scholarships', ScholarshipViewSet, basename='api_scholarships')
router.register(r'results', ResultViewSet, basename='api_results')
router.register(r'notifications', NotificationViewSet, basename='api_notifications')
router.register(r'forum', ForumPostViewSet, basename='api_forum')

urlpatterns = [
    # Router endpoints
    path('', include(router.urls)),
    
    # Custom JWT Authentication endpoints
    path('auth/register/', RegisterAPIView.as_view(), name='api_register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
