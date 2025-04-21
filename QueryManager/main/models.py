from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager
from simple_history.models import HistoricalRecords

# Custom User Model
class CustomUser(AbstractUser):
    region = models.CharField(max_length=200)
    email = models.EmailField(blank=False, null=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    history = HistoricalRecords()

# Question Model
class Question(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, blank=True, null=True) #Changes 14/2/2025
    issue = models.CharField(max_length=300)
    detail = models.TextField()
    status = models.BooleanField(default=False)
    referenceform = models.TextField(blank=True) #Changes
    tags = TaggableManager(blank=True) #Changes
    add_time = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    def __str__(self):
        return self.issue

# Answer Model
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    solution = models.TextField(default='')
    mark_solution = models.BooleanField(default=False) #Changes
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    def __str__(self):
        return self.solution

# Comment
class Comment(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comment_user')
    comment = models.TextField(default='')
    add_time = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    def __str__(self):
        return self.comment

# Attachment Model
class QuestionAttachment(models.Model):
    question = models.ForeignKey(Question, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')

    def is_image(self):
        return self.file.url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
    
class AnswerAttachment(models.Model):
    answer = models.ForeignKey(Answer, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')

    def is_image(self):
        return self.file.url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))

class CommentAttachment(models.Model):
    comment = models.ForeignKey(Comment, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')

    def is_image(self):
        return self.file.url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))

# UpVotes
class UpVote(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='upvote_user')

# DownVotes
class DownVote(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='downvote_user')
