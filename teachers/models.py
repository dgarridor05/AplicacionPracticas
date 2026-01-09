from django.db import models
from accounts.models import UserProfile

class ClassGroup(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='teaching_groups'
    )
    students = models.ManyToManyField(
        UserProfile,
        related_name='student_groups',
        limit_choices_to={'role': 'student'}
    )

    def __str__(self):
        return f"{self.name} ({self.teacher.username})"
