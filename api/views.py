from rest_framework import viewsets, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Q

from portal.models import (
    Category, Exam, Job, Scheme, Scholarship, Result, Notification,
    ForumPost, ForumComment, State
)
from users.models import UserProfile, UserActivityLog
from portal.recommendation import check_scheme_eligibility
from .serializers import (
    UserSerializer, ExamSerializer, JobSerializer, SchemeSerializer,
    ScholarshipSerializer, ResultSerializer, NotificationSerializer,
    ForumPostSerializer, ForumCommentSerializer
)

User = get_user_model()

class RegisterAPIView(APIView):
    """
    Endpoint for new user registration that outputs a JWT token.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        username = data.get('username') or (email.split('@')[0] if email else None)

        if not email or not password:
            return Response({'error': 'Email and password required.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already registered.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_citizen=True
            )
            
            # Create default profile
            state_id = data.get('state')
            state_obj = State.objects.filter(id=state_id).first() if state_id else None
            
            UserProfile.objects.create(
                user=user,
                phone=data.get('phone', ''),
                qualification=data.get('qualification', 'Graduate'),
                state=state_obj,
                occupation=data.get('occupation', 'Student'),
                gender=data.get('gender', 'Male'),
                age=int(data.get('age', 22)),
                annual_income=float(data.get('annual_income', 150000))
            )

            # Log activity
            UserActivityLog.objects.create(
                user=user,
                action="API Registration",
                ip_address=request.META.get('REMOTE_ADDR'),
                details="Citizen registered via REST API."
            )

            # Generate JWT
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.filter(is_deleted=False)
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'conducting_authority', 'qualification']
    ordering_fields = ['vacancy_count', 'name', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        qualification = self.request.query_params.get('qualification')
        if category:
            qs = qs.filter(category_id=category)
        if qualification:
            qs = qs.filter(qualification__icontains=qualification)
        return qs

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.filter(is_deleted=False)
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['post_name', 'department', 'qualification']
    ordering_fields = ['last_date', 'vacancies']

    def get_queryset(self):
        qs = super().get_queryset()
        state = self.request.query_params.get('state')
        qualification = self.request.query_params.get('qualification')
        if state:
            qs = qs.filter(state_id=state)
        if qualification:
            qs = qs.filter(qualification__icontains=qualification)
        return qs

class SchemeViewSet(viewsets.ModelViewSet):
    queryset = Scheme.objects.filter(is_deleted=False)
    serializer_class = SchemeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'category', 'eligibility_criteria']

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        state = self.request.query_params.get('state')
        if category:
            qs = qs.filter(category=category)
        if state:
            qs = qs.filter(state_id=state)
        return qs

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def check_eligibility(self, request, pk=None):
        """
        Exposes Scheme Eligibility Calculations via REST.
        """
        scheme = self.get_object()
        data = request.data
        try:
            age = int(data.get('age', 22))
            gender = data.get('gender', 'Male')
            income = float(data.get('income', 150000))
            occupation = data.get('occupation', 'Student')
            state_id = data.get('state')
            state_obj = State.objects.filter(id=state_id).first() if state_id else None

            res = check_scheme_eligibility(scheme, age, gender, state_obj, income, occupation)
            res['benefit_amount'] = float(res['benefit_amount'])
            
            return Response({'eligibility': res})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.filter(is_deleted=False)
    serializer_class = ScholarshipSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'class_level', 'degree']

    def get_queryset(self):
        qs = super().get_queryset()
        state = self.request.query_params.get('state')
        class_level = self.request.query_params.get('class_level')
        if state:
            qs = qs.filter(state_id=state)
        if class_level:
            qs = qs.filter(class_level__icontains=class_level)
        return qs

class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Result.objects.filter(active=True).order_by('-result_date')
    serializer_class = ResultSerializer
    permission_classes = [permissions.AllowAny]

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = [permissions.AllowAny]

class ForumPostViewSet(viewsets.ModelViewSet):
    queryset = ForumPost.objects.all().order_by('-created_at')
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        UserActivityLog.objects.create(
            user=self.request.user,
            action="API Created Forum Post",
            ip_address=self.request.META.get('REMOTE_ADDR'),
            details=f"Posted topic: {post.title}"
        )
