from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class AuditModel(models.Model):
    """
    Abstract base model to provide audit timestamps and soft delete capabilities.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        hard = kwargs.pop('hard', False)
        if hard:
            super().delete(*args, **kwargs)
        else:
            self.is_deleted = True
            self.save()

class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Exam(AuditModel):
    name = models.CharField(max_length=255)
    conducting_authority = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='exams')
    qualification = models.CharField(max_length=100) # e.g. "Graduate", "12th Pass"
    age_limit = models.IntegerField(default=30)
    fees = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    important_dates = models.TextField(help_text="JSON format or list of key dates")
    eligibility = models.TextField()
    exam_pattern = models.TextField()
    syllabus = models.TextField()
    vacancy_count = models.IntegerField(default=0)
    admit_card_link = models.URLField(blank=True, null=True)
    result_link = models.URLField(blank=True, null=True)
    official_website = models.URLField()

    def __str__(self):
        return self.name

class Job(AuditModel):
    department = models.CharField(max_length=255)
    post_name = models.CharField(max_length=255)
    vacancies = models.IntegerField(default=1)
    salary_range = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    last_date = models.DateField()
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    official_notification = models.URLField()

    def __str__(self):
        return f"{self.post_name} - {self.department}"

class Scheme(AuditModel):
    SCHEME_CATEGORY_CHOICES = [
        ('Farmers', 'Farmers'),
        ('Women', 'Women'),
        ('Students', 'Students'),
        ('Senior Citizens', 'Senior Citizens'),
        ('Startups', 'Startups'),
        ('Businesses', 'Businesses'),
        ('Healthcare', 'Healthcare'),
        ('General', 'General'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=SCHEME_CATEGORY_CHOICES, default='General')
    eligibility_criteria = models.TextField(help_text="Detailed text or JSON criteria")
    income_limit = models.DecimalField(max_digits=12, decimal_places=2, default=300000.00)
    min_age = models.IntegerField(default=0)
    max_age = models.IntegerField(default=100)
    gender_requirement = models.CharField(max_length=10, choices=[('Any', 'Any'), ('Male', 'Male'), ('Female', 'Female')], default='Any')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='schemes')
    benefit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Amount in Rs.")
    documents_required = models.TextField()
    application_process = models.TextField()
    official_website = models.URLField()

    def __str__(self):
        return self.name

class Scholarship(AuditModel):
    name = models.CharField(max_length=255)
    eligibility = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_date = models.DateField()
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='scholarships')
    class_level = models.CharField(max_length=50) # e.g. "Class 10", "Undergraduate"
    degree = models.CharField(max_length=100, blank=True, null=True)
    official_website = models.URLField()

    def __str__(self):
        return self.name

class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    result_date = models.DateField()
    download_link = models.URLField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.exam.name}"

class AdmitCard(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='admit_cards')
    release_date = models.DateField()
    download_link = models.URLField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Admit Card for {self.exam.name}"

class CurrentAffairs(models.Model):
    CA_CATEGORY_CHOICES = [
        ('National', 'National'),
        ('International', 'International'),
        ('Economy', 'Economy'),
        ('Science', 'Science'),
        ('Sports', 'Sports'),
        ('Politics', 'Politics'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=30, choices=CA_CATEGORY_CHOICES, default='National')
    pub_date = models.DateField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='current_affairs_pdfs/', blank=True, null=True)

    def __str__(self):
        return self.title

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])

    def __str__(self):
        return self.question_text[:50]

class GovService(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    documents_required = models.TextField()
    fees = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    process = models.TextField()
    official_link = models.URLField()

    def __str__(self):
        return self.name

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('Job', 'New Job Alert'),
        ('Exam', 'Exam Alert'),
        ('Scheme', 'Scheme Update'),
        ('Result', 'Result Released'),
        ('AdmitCard', 'Admit Card Available'),
        ('General', 'General Announcement'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='General')
    url = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title}"

class ForumPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    upvotes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='upvoted_posts', blank=True)
    downvotes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='downvoted_posts', blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class ForumComment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    upvotes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='upvoted_comments', blank=True)

    def __str__(self):
        return f"Comment by {self.author.email} on {self.post.title}"

class UserBookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

    def __str__(self):
        return f"{self.user.email} saved {self.content_object}"
