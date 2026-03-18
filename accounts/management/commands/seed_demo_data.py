import os

import cloudinary.uploader
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.conf import settings

from accounts.models import UserProfile
from teachers.models import ClassGroup


class Command(BaseCommand):
    help = 'Crea datos de prueba (profesor, alumnos, imágenes y un grupo) sin borrar lo que ya exista.'

    def handle(self, *args, **options):
        # 1) Profesor de ejemplo
        teacher_username = 'prof_demo'
        teacher_email = 'prof_demo@example.com'
        teacher_password = 'demo1234'

        teacher, created = UserProfile.objects.get_or_create(
            username=teacher_username,
            defaults={
                'email': teacher_email,
                'role': 'teacher',
                'is_staff': True,
                'is_active': True,
                'password': make_password(teacher_password),
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Profesor creado: {teacher_username} (clave: {teacher_password})'))
        else:
            self.stdout.write(self.style.WARNING(f'Profesor existente: {teacher_username}'))

        # 2) Alumnos de ejemplo
        alumnos = []
        imagenes = [
            'imagen_prueba_1.jpg',
            'imagen_prueba_2.jpg',
            'imagen_prueba_3.jpg',
            'imagen_prueba_4.jpg',
            'imagen_prueba_5.jpg',
            'imagen_prueba_6.jpg',
            'imagen_prueba_7.jpg',
        ]

        for i in range(1, 7):
            username = f'alumno{i}'
            email = f'alumno{i}@example.com'
            password = 'demo1234'

            alumno, created = UserProfile.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'role': 'student',
                    'is_staff': False,
                    'is_active': True,
                    'password': make_password(password),
                    'share_with_class': True,
                    'nickname': f'Alumno {i}',
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Alumno creado: {username} (clave: {password})'))
            else:
                self.stdout.write(self.style.WARNING(f'Alumno existente: {username}'))

            # 2.b) Si hay imagenes disponibles, se la asignamos (solo si no tiene ya una)
            if not alumno.profile_picture:
                imagen_nombre = imagenes[(i - 1) % len(imagenes)]
                imagen_ruta = os.path.join(settings.BASE_DIR, 'profile_pics', imagen_nombre)
                if os.path.exists(imagen_ruta):
                    with open(imagen_ruta, 'rb') as f:
                        result = cloudinary.uploader.upload(f)
                        public_id = result.get('public_id')
                        if public_id:
                            alumno.profile_picture = public_id
                            alumno.save()
                            self.stdout.write(self.style.SUCCESS(f'  → Foto subida a Cloudinary: {public_id}'))
                        else:
                            self.stdout.write(self.style.ERROR('  → Error al subir la imagen a Cloudinary.'))
                else:
                    self.stdout.write(self.style.WARNING(f'  → No se encontró imagen: {imagen_nombre}'))

            alumnos.append(alumno)

        # 3) Grupo de prueba con código fijo para poder unirse mediante el formulario
        group_name = 'Grupo Demo'
        invite_code = 'DEMO123'

        group, created = ClassGroup.objects.get_or_create(
            invite_code=invite_code,
            defaults={
                'name': group_name,
                'teacher': teacher,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Grupo creado: {group_name} (código: {group.invite_code})'))
        else:
            # Si ya existía, nos aseguramos de que el profesor sea el correcto
            if group.teacher != teacher:
                group.teacher = teacher
                group.save(update_fields=['teacher'])
            self.stdout.write(self.style.WARNING(f'Grupo existente: {group_name} (código: {group.invite_code})'))

        # 4) Añadimos los alumnos al grupo (no repite)
        for alumno in alumnos:
            if not group.students.filter(id=alumno.id).exists():
                group.students.add(alumno)

        self.stdout.write(self.style.SUCCESS(f'Alumnos añadidos al grupo: {group.students.count()} alumnos'))
        self.stdout.write(self.style.SUCCESS('✅ Seed completado.'))
