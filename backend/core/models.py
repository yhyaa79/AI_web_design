from django.db import models
from django.utils import timezone

class User(models.Model):
    ip_address = models.CharField(max_length=45, unique=True)
    username = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    message_count = models.IntegerField(default=0)
    last_message_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

class Message(models.Model):
    ROLE_CHOICES = [('user', 'user'), ('assistant', 'assistant')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['timestamp']