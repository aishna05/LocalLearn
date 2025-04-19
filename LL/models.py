from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.hashers import make_password, check_password


# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=150, unique=True, default='default_username')
    password = models.CharField(max_length=128, default='default_password')
    email = models.EmailField(unique=True, default='default@example.com')
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_username(self):
        return self.username

    @property
    def is_staff(self):
        return False

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True, default='default_subject')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return self.name


class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name='notes',
        null=True,  # Add this temporarily
        blank=True  # Add this temporarily
    )
    title = models.CharField(max_length=255, default='default_title')
    content = models.TextField(default='default_content')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shared_with = models.ManyToManyField(
        User,
        through='SharedNote',
        through_fields=('note', 'recipient'),
        related_name='shared_notes'
    )

    def __str__(self):
        return self.title


class Media(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media')
    note_id = models.ForeignKey(Notes, on_delete=models.CASCADE, related_name='media')
    title = models.CharField(max_length=255, default='default_media_title')
    file = models.FileField(upload_to='media/', validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class SharedNote(models.Model):
    note = models.ForeignKey(Notes, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes_shared')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes_received')
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['note', 'recipient']
