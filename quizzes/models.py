from django.db import models
from accounts.models import UserProfile
from .constants import ALL_CATEGORIES  


class Questionnaire(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    category = models.CharField(max_length=1, choices=ALL_CATEGORIES)
    value = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.text} ({self.get_category_display()})"


class UserAnswer(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.question.id}"


class UserResult(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    dominant_category = models.CharField(max_length=1, choices=ALL_CATEGORIES) 

    class Meta:
        unique_together = ('user', 'questionnaire')

    def __str__(self):
        return f"{self.user.username} - {self.get_dominant_category_display()}"