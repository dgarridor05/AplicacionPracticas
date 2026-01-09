import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from quizzes.models import Questionnaire, Question, Option

class Command(BaseCommand):
    help = 'Carga el test de Chapman desde el archivo JSON'

    def handle(self, *args, **kwargs):
        # Ruta al archivo JSON
        json_file = os.path.join(settings.BASE_DIR, 'chapman_fixture_complete.json')
        
        if not os.path.exists(json_file):
            self.stdout.write(
                self.style.ERROR(f'Archivo {json_file} no encontrado.')
            )
            return

        # FORZAR REEMPLAZO: Eliminar Chapman existente si existe
        existing_chapman = Questionnaire.objects.filter(title__iexact="Chapman")
        if existing_chapman.exists():
            self.stdout.write(
                self.style.WARNING('🗑️  Eliminando Chapman existente para cargar la versión actualizada...')
            )
            existing_chapman.delete()
            self.stdout.write(
                self.style.SUCCESS('✅ Chapman anterior eliminado correctamente.')
            )

        try:
            self.stdout.write(
                self.style.SUCCESS('📝 Cargando Chapman educativo desde chapman_fixture_complete.json...')
            )
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            questionnaire_obj = None
            old_q_pk_to_new = {}

            # Primera pasada: crear Questionnaire
            for item in data:
                if item['model'] == 'quizzes.questionnaire':
                    fields = item['fields']
                    if fields['title'] == 'Chapman':
                        questionnaire_obj = Questionnaire.objects.create(
                            title=fields['title'],
                            description=fields['description']
                        )
                        self.stdout.write(f'✅ Cuestionario creado: {questionnaire_obj.title}')
                        self.stdout.write(f'📋 Descripción: {questionnaire_obj.description}')
                        break

            if not questionnaire_obj:
                self.stdout.write(
                    self.style.ERROR('No se encontró el cuestionario Chapman en el fixture')
                )
                return

            # Segunda pasada: crear Questions
            for item in data:
                if item['model'] == 'quizzes.question':
                    fields = item['fields']
                    question = Question.objects.create(
                        questionnaire=questionnaire_obj,
                        text=fields['text']
                    )
                    old_q_pk_to_new[item['pk']] = question

            # Tercera pasada: crear Options
            options_created = 0
            for item in data:
                if item['model'] == 'quizzes.option':
                    fields = item['fields']
                    old_question_pk = fields['question']
                    question = old_q_pk_to_new.get(old_question_pk)
                    if question:
                        Option.objects.create(
                            question=question,
                            text=fields['text'],
                            category=fields['category'],
                            value=fields['value']
                        )
                        options_created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 ¡Test de Chapman EDUCATIVO cargado exitosamente desde JSON!'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'📊 Estadísticas: {len(old_q_pk_to_new)} preguntas, {options_created} opciones'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎓 Contexto: Lenguajes del amor adaptados al ámbito universitario'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al cargar datos: {str(e)}')
            )
