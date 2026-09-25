import uuid
from django.db import models

class EventUser(models.Model):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    answers = models.JSONField(default=dict)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.user_id}"

class Question(models.Model):
    question_id = models.CharField(max_length=50, unique=True)
    text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=50) # single, dropdown, scale

    def __str__(self):
        return self.text

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.text} ({self.score})"
