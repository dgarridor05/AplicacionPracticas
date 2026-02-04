import string
import random
from django.db import models
from accounts.models import UserProfile

def generate_invite_code():
    """Genera un código aleatorio único de 6 caracteres."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

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
    
    # Campo nuevo con null=True para proteger tus datos actuales
    invite_code = models.CharField(
        max_length=10, 
        unique=True, 
        null=True, 
        blank=True,
        verbose_name="Código de invitación"
    )

    def save(self, *args, **kwargs):
        # Si el grupo no tiene código (es nuevo o se está creando), le asignamos uno
        if not self.invite_code:
            self.invite_code = generate_invite_code()
            # Verificación de unicidad
            while ClassGroup.objects.filter(invite_code=self.invite_code).exists():
                self.invite_code = generate_invite_code()
        super().save(*args, **kwargs)

    def __str__(self):
        # He añadido el código al str para que lo veas fácil en el Admin de Django
        return f"{self.name} - {self.invite_code} ({self.teacher.username})"