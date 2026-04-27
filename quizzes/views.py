from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Questionnaire, Question, Option, UserAnswer, UserResult
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q

@login_required
def take_vark_quiz(request):
    if request.user.role != 'student':
        return redirect('login')

    questionnaire = get_object_or_404(Questionnaire, title__iexact="VARK")
    questions = questionnaire.question_set.prefetch_related('options')

    if request.method == "POST":
        UserAnswer.objects.filter(user=request.user, question__in=questions).delete()

        scores = {'V': 0, 'A': 0, 'R': 0, 'K': 0}

        for question in questions:
            selected_id = request.POST.get(f"question_{question.id}")
            if selected_id:
                option = Option.objects.get(id=selected_id)
                UserAnswer.objects.create(
                    user=request.user,
                    question=question,
                    selected_option=option
                )
                scores[option.category] += option.value

        dominant = max(scores, key=scores.get)

        UserResult.objects.update_or_create(
            user=request.user,
            questionnaire=questionnaire,
            defaults={"dominant_category": dominant}
        )

        return redirect("vark_result")

    return render(request, "quizzes/vark_quiz.html", {
        "questionnaire": questionnaire,
        "questions": questions
    })

@login_required
def vark_result(request):
    try:
        result = UserResult.objects.get(user=request.user, questionnaire__title="VARK")
    except UserResult.DoesNotExist:
        messages.warning(request, "Primero debes realizar el test VARK para ver tus resultados.")
        return redirect('take_vark_quiz')

    category = result.dominant_category

    messages_dict = {
        'V': {
            'label': 'Visual',
            'description': "Aprendes mejor con esquemas, gráficos, colores y mapas mentales.",
            'tips': [
                "Usa colores para resaltar ideas importantes.",
                "Dibuja esquemas o mapas conceptuales.",
                "Convierte la información en gráficos o símbolos."
            ]
        },
        'A': {
            'label': 'Aural (Auditivo)',
            'description': "Retienes mejor la información escuchando y hablando.",
            'tips': [
                "Graba las explicaciones en audio y escúchalas.",
                "Estudia en voz alta o en grupo.",
                "Participa en debates o explicaciones orales."
            ]
        },
        'R': {
            'label': 'Read/Write (Lectura-Escritura)',
            'description': "Prefieres leer y escribir para aprender.",
            'tips': [
                "Haz resúmenes y escribe listas de conceptos.",
                "Utiliza libros, apuntes y textos detallados.",
                "Vuelve a escribir lo aprendido para recordarlo."
            ]
        },
        'K': {
            'label': 'Kinestésico',
            'description': "Aprendes haciendo, manipulando y moviéndote.",
            'tips': [
                "Realiza actividades prácticas o simulaciones.",
                "Estudia caminando o usando gestos.",
                "Relaciona lo que aprendes con experiencias reales."
            ]
        }
    }

    context = messages_dict[category]
    context['category'] = category

    return render(request, "quizzes/vark_result.html", context)

@login_required
def take_chapman_quiz(request):
    questionnaire = get_object_or_404(Questionnaire, title__iexact="Chapman")
    questions = questionnaire.question_set.prefetch_related('options')

    if request.method == "POST":
        UserAnswer.objects.filter(user=request.user, question__in=questions).delete()

        # Nuevo mapeo para las categorías del test adaptado
        CATEGORY_MAP = {
            'A': 'Palabras de Afirmación',
            'B': 'Tiempo de Calidad',
            'C': 'Recibir Detalles o Regalos',
            'D': 'Actos de Servicio',
            'E': 'Contacto o Presencia Física y Emocional',
        }

        REVERSE_CATEGORY_MAP = {v: k for k, v in CATEGORY_MAP.items()}

        scores = {
            'Palabras de Afirmación': 0,
            'Tiempo de Calidad': 0,
            'Recibir Detalles o Regalos': 0,
            'Actos de Servicio': 0,
            'Contacto o Presencia Física y Emocional': 0,
        }

        for question in questions:
            selected_id = request.POST.get(f"question_{question.id}")
            if selected_id:
                option = Option.objects.get(id=selected_id)
                UserAnswer.objects.create(
                    user=request.user,
                    question=question,
                    selected_option=option
                )
                # Mapear la categoría directamente ya que las opciones usan A, B, C, D, E
                translated_category = CATEGORY_MAP.get(option.category, option.category)
                scores[translated_category] += option.value

        dominant = max(scores, key=scores.get)  # Dominante en forma larga

        UserResult.objects.filter(user=request.user, questionnaire=questionnaire).delete()

        UserResult.objects.create(
            user=request.user,
            questionnaire=questionnaire,
            dominant_category=REVERSE_CATEGORY_MAP[dominant]  # Guardamos solo 'A', 'B', etc.
        )

        return redirect("chapman_result")

    return render(request, "quizzes/chapman_quiz.html", {
        "questionnaire": questionnaire,
        "questions": questions
    })

    
@login_required
def chapman_result(request):
    try:
        result = UserResult.objects.get(user=request.user, questionnaire__title__iexact="Chapman")
    except UserResult.DoesNotExist:
        messages.warning(request, "Primero debes realizar el test de Chapman para ver tus resultados.")
        return redirect('take_chapman_quiz')

    # Mapeo de clave corta a nombre largo para el nuevo test
    CATEGORY_MAP = {
        'A': 'Palabras de Afirmación',
        'B': 'Tiempo de Calidad',
        'C': 'Recibir Detalles o Regalos',
        'D': 'Actos de Servicio',
        'E': 'Contacto o Presencia Física y Emocional',
    }

    full_category = CATEGORY_MAP.get(result.dominant_category)

    messages_dict = {
        'Palabras de Afirmación': {
            'label': 'Palabras de Afirmación',
            'description': "Para ti, las palabras importan. Te sientes motivado/a y valorado/a cuando tu profesor/a te felicita, te reconoce verbalmente o te anima con mensajes positivos. Las expresiones sinceras marcan una gran diferencia en tu rendimiento y bienestar.",
            'emoji': '🅰️'
        },
        'Tiempo de Calidad': {
            'label': 'Tiempo de Calidad',
            'description': "Lo que más valoras es que tu profesor/a te dedique tiempo exclusivo. Las conversaciones profundas, las tutorías personales o el simple hecho de sentir que te escucha con atención te hace sentir importante.",
            'emoji': '🅱️'
        },
        'Recibir Detalles o Regalos': {
            'label': 'Recibir Detalles o Regalos',
            'description': "Los pequeños gestos materiales, como un punto extra, un mensaje de felicitación o un pequeño detalle simbólico, te hacen sentir reconocido/a. No se trata del valor económico, sino del gesto y la intención detrás.",
            'emoji': '🅲'
        },
        'Actos de Servicio': {
            'label': 'Actos de Servicio',
            'description': "Te sientes cuidado/a cuando tu profesor/a hace cosas concretas para ayudarte: explicarte un tema difícil, responder con paciencia a tus dudas o ayudarte a organizarte. Lo que hace por ti habla más fuerte que lo que dice.",
            'emoji': '🅳'
        },
        'Contacto o Presencia Física y Emocional': {
            'label': 'Contacto o Presencia Física y Emocional',
            'description': "Para ti es importante el lenguaje no verbal y la cercanía. Puede ser un gesto afectuoso como un toque en el hombro, un saludo espontáneo, una sonrisa o simplemente sentir su presencia atenta y cercana en el aula.",
            'emoji': '🅴'
        },
    }

    context = messages_dict[full_category]
    context['category'] = full_category

    return render(request, "quizzes/chapman_result.html", context)


@login_required
def take_social_quiz(request):
    if request.user.role != 'student':
        return redirect('login')

    questionnaire = get_object_or_404(Questionnaire, title__iexact="Estilos de Interacción Social")
    questions = questionnaire.question_set.prefetch_related('options')

    if request.method == "POST":
        UserAnswer.objects.filter(user=request.user, question__in=questions).delete()

        # Get all unique categories from the questionnaire's options
        categories = set()
        for question in questions:
            for option in question.options.all():
                categories.add(option.category)
        scores = {cat: 0 for cat in categories}

        for question in questions:
            selected_id = request.POST.get(f"question_{question.id}")
            if selected_id:
                option = Option.objects.get(id=selected_id)
                UserAnswer.objects.create(
                    user=request.user,
                    question=question,
                    selected_option=option
                )
                scores[option.category] += option.value

        dominant = max(scores, key=scores.get)

        UserResult.objects.update_or_create(
            user=request.user,
            questionnaire=questionnaire,
            defaults={"dominant_category": dominant}
        )

        return redirect("social_result")

    return render(request, "quizzes/social_quiz.html", {
        "questionnaire": questionnaire,
        "questions": questions
    })


@login_required
def social_result(request):
    try:
        result = UserResult.objects.get(user=request.user, questionnaire__title="Estilos de Interacción Social")
    except UserResult.DoesNotExist:
        messages.warning(request, "Primero debes realizar el test de Estilos de Interacción Social para ver tus resultados.")
        return redirect('take_social_quiz')

    category = result.dominant_category

    messages_dict = {
        'C': {
            'label': 'Colaborativo',
            'description': "Te sientes cómodo/a trabajando en equipo y aprendiendo a través de la interacción con otros. Disfrutas de las discusiones grupales, los debates y el aprendizaje colaborativo. Te motiva compartir ideas y aprender de las perspectivas de tus compañeros.",
            'tips': [
                "Participa activamente en grupos de estudio.",
                "Busca oportunidades para debatir y discutir temas.",
                "Comparte tus conocimientos con otros estudiantes."
            ]
        },
        'I': {
            'label': 'Independiente',
            'description': "Prefieres estudiar y aprender por tu cuenta, sin distracciones externas. Te concentras mejor en entornos tranquilos y valoras la autonomía en tu proceso de aprendizaje. Te sientes cómodo/a resolviendo problemas individualmente.",
            'tips': [
                "Estudia en lugares tranquilos y sin interrupciones.",
                "Desarrolla técnicas de estudio personales.",
                "Toma decisiones de aprendizaje de forma autónoma."
            ]
        },
        'P': {
            'label': 'Práctico',
            'description': "Aprendes mejor cuando puedes aplicar los conceptos a situaciones reales y concretas. Te motivan las actividades prácticas, los experimentos y los proyectos que tienen un resultado tangible. Valoras el aprendizaje hands-on.",
            'tips': [
                "Busca oportunidades para aplicar lo que aprendes.",
                "Participa en proyectos prácticos y experimentos.",
                "Relaciona los conceptos teóricos con situaciones reales."
            ]
        },
        'R': {
            'label': 'Reflexivo',
            'description': "Disfrutas analizando ideas profundas y abstractas. Te gusta pensar críticamente sobre los conceptos, explorar diferentes perspectivas y reflexionar sobre el significado más amplio de lo que aprendes. Valoras el pensamiento profundo.",
            'tips': [
                "Dedica tiempo a reflexionar sobre los temas estudiados.",
                "Analiza diferentes perspectivas de un mismo concepto.",
                "Escribe diarios de aprendizaje o reflexiones personales."
            ]
        }
    }

    context = messages_dict[category]
    context['category'] = category

    return render(request, "quizzes/social_result.html", context)
