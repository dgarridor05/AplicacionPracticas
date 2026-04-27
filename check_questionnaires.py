from quizzes.models import Questionnaire
questionnaires = Questionnaire.objects.all()
for q in questionnaires:
    print(f'ID: {q.id}, Title: "{q.title}"')