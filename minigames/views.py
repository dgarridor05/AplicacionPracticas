from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile
from teachers.models import ClassGroup
from quizzes.models import UserResult, Questionnaire
import random
import unicodedata
from datetime import date

# --- UTILIDADES ---
def normalize_text(text):
    """Elimina tildes y convierte a mayúsculas."""
    if not text: return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).upper()

def calculate_age(birth_date):
    if not birth_date: return "desconocida"
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def get_ajax_response(request, success, message, prefix, extra_data=None):
    data = {
        'success': success, 'message': message,
        'correct': request.session.get(f'{prefix}_correct', 0),
        'total': request.session.get(f'{prefix}_total', 0),
    }
    if extra_data: data.update(extra_data)
    return JsonResponse(data)

# --- SELECTOR DE GRUPO ---
@login_required
def select_group_for_game(request, game_name):
    """ Pantalla intermedia para elegir qué clase va a jugar """
    if request.user.role == 'student':
        mi_grupo = request.user.student_groups.first()
        if not mi_grupo:
            return render(request, 'minigames/no_students.html')
        return redirect(game_name, group_id=mi_grupo.id)

    groups = ClassGroup.objects.filter(teacher=request.user)
    return render(request, 'minigames/select_group.html', {
        'groups': groups,
        'game_name': game_name
    })

# --- VISTAS DE JUEGOS ---

@login_required
def face_guess_game(request, group_id=None):
    # Mejora: Detección automática para alumnos
    if request.user.role == 'student':
        group = request.user.student_groups.first()
        if not group: 
            return render(request, 'minigames/no_students.html')
        group_id = group.id
    elif not group_id: 
        return select_group_for_game(request, 'face_guess_game')
    
    group = get_object_or_404(ClassGroup, id=group_id)
    # Mejora: Excluir al propio usuario si es alumno
    students = group.students.filter(profile_picture__isnull=False).exclude(id=request.user.id).distinct()
    
    if not students.exists(): 
        return render(request, 'minigames/no_students.html')
    
    if 'face_guess_correct' not in request.session: request.session['face_guess_correct'] = 0
    if 'face_guess_total' not in request.session: request.session['face_guess_total'] = 0
    
    if request.method == 'POST':
        target_id = request.session.get('face_guess_target_id')
        # Normalizamos y limpiamos espacios de la respuesta del usuario
        answer = normalize_text(request.POST.get('answer', '')).strip()
        student = get_object_or_404(UserProfile, id=target_id)
        
        # Recogemos todos los campos posibles para validar
        fields = ['username', 'first_name', 'last_name', 'full_name', 'nickname']
        valid_answers = [normalize_text(getattr(student, f)).strip() for f in fields if getattr(student, f)]
        
        request.session['face_guess_total'] += 1
        
        # --- Lógica de validación mejorada ---
        is_correct = False
        if answer:  # Evitar procesar respuestas vacías
            if answer in valid_answers:
                is_correct = True
            else:
                # Comprobación parcial (ej. "Juan" coincide con "Juan Alberto")
                for valid in valid_answers:
                    if len(answer) > 2 and (answer in valid or valid in answer):
                        is_correct = True
                        break
        # -------------------------------------

        if is_correct: 
            request.session['face_guess_correct'] += 1
            
        msg = f"¡Correcto! Es {student.full_name or student.username}" if is_correct else f"Incorrecto. Era: {student.full_name or student.username}"
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
            return get_ajax_response(request, is_correct, msg, 'face_guess')
        
        return redirect('face_guess_game', group_id=group_id)

    # Selección del siguiente alumno evitando repetir el último visto
    last_id = request.session.get('face_guess_last_id')
    available_students = students.exclude(id=last_id) if students.count() > 1 else students
    target_student = random.choice(available_students)
    
    request.session['face_guess_target_id'] = target_student.id
    request.session['face_guess_last_id'] = target_student.id
    
    return render(request, 'minigames/face_guess_game.html', {
        'student': target_student, 
        'group': group,
        'correct': request.session['face_guess_correct'], 
        'total': request.session['face_guess_total']
    })

@login_required
def name_to_face_game(request, group_id=None):
    if request.user.role == 'student':
        group = request.user.student_groups.first()
        if not group: return render(request, 'minigames/no_students.html')
        group_id = group.id
    elif not group_id: 
        return select_group_for_game(request, 'name_to_face_game')
    
    group = get_object_or_404(ClassGroup, id=group_id)
    # Mejora: Excluir al propio usuario
    students = group.students.filter(profile_picture__isnull=False).exclude(id=request.user.id).distinct()
    
    if students.count() < 4: return render(request, 'minigames/not_enough_students.html')
    
    if 'name_to_face_correct' not in request.session: request.session['name_to_face_correct'] = 0
    if 'name_to_face_total' not in request.session: request.session['name_to_face_total'] = 0
    
    if request.method == 'POST':
        is_correct = str(request.POST.get('selected_id')) == str(request.session.get('name_to_face_target_id'))
        request.session['name_to_face_total'] += 1
        if is_correct: request.session['name_to_face_correct'] += 1
        msg = "¡Correcto!" if is_correct else "Incorrecto."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': return get_ajax_response(request, is_correct, msg, 'name_to_face')
        return redirect('name_to_face_game', group_id=group_id)

    target = random.choice(students.exclude(id=request.session.get('name_to_face_last_id')) if students.count() > 1 else students)
    request.session['name_to_face_target_id'] = target.id
    request.session['name_to_face_last_id'] = target.id
    options = list(random.sample(list(students.exclude(id=target.id)), 3)) + [target]
    random.shuffle(options)
    return render(request, 'minigames/name_to_face_game.html', {
        'target_name': target.full_name or target.username, 
        'options': options, 
        'group': group,
        'correct': request.session['name_to_face_correct'], 
        'total': request.session['name_to_face_total']
    })

@login_required
def hangman_game(request, group_id=None):
    if request.user.role == 'student':
        group = request.user.student_groups.first()
        if not group: return render(request, 'minigames/no_students.html')
        group_id = group.id
    elif not group_id:
        return select_group_for_game(request, 'hangman_game')
    
    group = get_object_or_404(ClassGroup, id=group_id)
    # Mejora: Excluir al propio usuario
    students = group.students.filter(profile_picture__isnull=False).exclude(id=request.user.id).distinct()
    
    if not students.exists():
        return render(request, 'minigames/no_students.html')
    
    if request.session.get('hangman_game_over', False) and request.method == 'GET':
        keys_to_reset = [
            'hangman_target_id', 'hangman_target_name', 
            'hangman_guessed_letters', 'hangman_incorrect_count', 
            'hangman_game_over'
        ]
        for key in keys_to_reset:
            request.session.pop(key, None)
        request.session.modified = True

    if 'hangman_target_id' not in request.session:
        last_id = request.session.get('hangman_last_id')
        possible_students = students.exclude(id=last_id) if students.count() > 1 else students
        student = random.choice(possible_students)
        
        request.session['hangman_target_id'] = student.id
        request.session['hangman_last_id'] = student.id
        raw_name = student.full_name or student.username
        request.session['hangman_target_name'] = normalize_text(raw_name)
        request.session['hangman_guessed_letters'] = []
        request.session['hangman_incorrect_count'] = 0
        request.session['hangman_game_over'] = False
        request.session.modified = True

    if 'hangman_correct' not in request.session: request.session['hangman_correct'] = 0
    if 'hangman_total' not in request.session: request.session['hangman_total'] = 0

    target_name = request.session['hangman_target_name']

    if request.method == 'POST' and request.POST.get('action') == 'guess_letter':
        letter = request.POST.get('letter', '').upper()
        
        if not request.session['hangman_game_over'] and letter not in request.session['hangman_guessed_letters']:
            request.session['hangman_guessed_letters'].append(letter)
            
            if letter not in target_name:
                request.session['hangman_incorrect_count'] += 1
            
            displayed = "".join([c if c in request.session['hangman_guessed_letters'] or not c.isalpha() else "_" for c in target_name])
            won = all(c in request.session['hangman_guessed_letters'] or not c.isalpha() for c in target_name)
            lost = request.session['hangman_incorrect_count'] >= 6
            
            if won or lost:
                request.session['hangman_game_over'] = True
                request.session['hangman_total'] += 1
                if won: request.session['hangman_correct'] += 1
            
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'displayed_name': displayed,
                'incorrect_count': request.session['hangman_incorrect_count'],
                'max_incorrect': 6,
                'game_over': request.session['hangman_game_over'],
                'won': won,
                'target_name': target_name,
                'correct': request.session['hangman_correct'],
                'total': request.session['hangman_total']
            })

    current_student = get_object_or_404(UserProfile, id=request.session['hangman_target_id'])
    displayed_name = "".join([c if c in request.session['hangman_guessed_letters'] or not c.isalpha() else "_" for c in target_name])
    
    context = {
        'current_student': current_student,
        'group': group,
        'displayed_name': displayed_name,
        'incorrect_count': request.session['hangman_incorrect_count'],
        'max_incorrect': 6,
        'alphabet': "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ",
        'used_letters': request.session['hangman_guessed_letters'],
        'game_over': request.session['hangman_game_over'],
        'correct': request.session['hangman_correct'],
        'total': request.session['hangman_total'],
        'target_name': target_name,
    }
    return render(request, 'minigames/hangman_game.html', context)

@login_required
def student_interests_game(request, group_id=None):
    if request.user.role == 'student':
        group = request.user.student_groups.first()
        if not group: return render(request, 'minigames/no_students.html')
        group_id = group.id
    elif not group_id: 
        return select_group_for_game(request, 'student_interests_game')
    
    group = get_object_or_404(ClassGroup, id=group_id)
    # Mejora: Excluir al propio usuario
    students = group.students.all().exclude(id=request.user.id).distinct()
    
    if students.count() < 4: return render(request, 'minigames/not_enough_students.html')

    if 'interests_correct' not in request.session: request.session['interests_correct'] = 0
    if 'interests_total' not in request.session: request.session['interests_total'] = 0

    if request.method == 'POST' and 'selected_option' in request.POST:
        selected_index = request.POST.get('selected_option') 
        correct_index = request.session.get('interests_correct_pos')
        request.session['interests_total'] += 1
        is_correct = str(selected_index) == str(correct_index)
        if is_correct: request.session['interests_correct'] += 1
        request.session.modified = True
        return get_ajax_response(request, is_correct, "¡Correcto!" if is_correct else "¡No! Esa no era su descripción", 'interests')

    target = random.choice(students)
    def get_desc(s):
        return f"Tiene {calculate_age(s.date_of_birth)} años. Su artista favorito es {s.favorite_artist or 'desconocido'} y le motiva: {s.motivation or 'aprender'}."
    
    correct_desc = get_desc(target)
    others = random.sample(list(students.exclude(id=target.id)), 3)
    options = [get_desc(s) for s in others] + [correct_desc]
    random.shuffle(options)
    request.session['interests_correct_pos'] = options.index(correct_desc) + 1
    
    return render(request, 'minigames/student_interests_game.html', {
        'target_student': target, 'group': group, 'options': options, 
        'correct': request.session['interests_correct'], 'total': request.session['interests_total']
    })

@login_required
def quiz_results_game(request, group_id=None):
    if request.user.role == 'student':
        group = request.user.student_groups.first()
        if not group: return render(request, 'minigames/no_students.html')
        group_id = group.id
    elif not group_id: 
        return select_group_for_game(request, 'quiz_results_game')
    
    group = get_object_or_404(ClassGroup, id=group_id)
    # Mejora: Excluir al propio usuario
    students = group.students.all().exclude(id=request.user.id).distinct()
    
    if students.count() < 4: return render(request, 'minigames/not_enough_students.html')
    
    if 'quiz_correct' not in request.session: request.session['quiz_correct'] = 0
    if 'quiz_total' not in request.session: request.session['quiz_total'] = 0
    
    if request.method == 'POST':
        is_correct = str(request.POST.get('selected_id')) == str(request.session.get('quiz_target_id'))
        request.session['quiz_total'] += 1
        if is_correct: request.session['quiz_correct'] += 1
        return get_ajax_response(request, is_correct, "¡Resultado!", 'quiz')

    target = random.choice(students)
    request.session['quiz_target_id'] = target.id
    options = list(random.sample(list(students.exclude(id=target.id)), 3)) + [target]
    random.shuffle(options)
    
    return render(request, 'minigames/quiz_results_game.html', {
        'target_student': target, 
        'options': options, 
        'group': group,
        'correct': request.session['quiz_correct'], 
        'total': request.session['quiz_total']
    })

@login_required
def student_complete_profile_game(request, group_id=None):
    if request.user.role == 'student':
        group = request.user.student_groups.first()
        if not group: return render(request, 'minigames/no_students.html')
        group_id = group.id
    elif not group_id: 
        return select_group_for_game(request, 'student_complete_profile_game')
        
    group = get_object_or_404(ClassGroup, id=group_id)
    # Mejora: Excluir al propio usuario
    students = group.students.filter(profile_picture__isnull=False).exclude(id=request.user.id).distinct()
    
    if students.count() < 4: return render(request, 'minigames/not_enough_students.html')
    
    if 'complete_profile_correct' not in request.session: request.session['complete_profile_correct'] = 0
    if 'complete_profile_total' not in request.session: request.session['complete_profile_total'] = 0
    
    if request.method == 'POST' and 'selected_student_id' in request.POST:
        is_correct = str(request.POST.get('selected_student_id')) == str(request.session.get('complete_profile_target_id'))
        request.session['complete_profile_total'] += 1
        if is_correct: request.session['complete_profile_correct'] += 1
        request.session.modified = True
        return get_ajax_response(request, is_correct, "¡Listo!", 'complete_profile')
    
    vark_q = Questionnaire.objects.filter(title="VARK").first()
    chapman_q = Questionnaire.objects.filter(title="Chapman").first()
    target = random.choice(students)
    request.session['complete_profile_target_id'] = target.id
    
    raw_options = list(students.exclude(id=target.id).order_by('?')[:3]) + [target]
    random.shuffle(raw_options)
    
    options_data = []
    for s in raw_options:
        vark = UserResult.objects.filter(user=s, questionnaire=vark_q).first()
        chapman = UserResult.objects.filter(user=s, questionnaire=chapman_q).first()
        options_data.append({
            'student_id': s.id,
            'full_name': s.full_name or s.username,
            'age': calculate_age(s.date_of_birth),
            'favorite_artist': s.favorite_artist or "N/A",
            'vark_result': vark.dominant_category if vark else "Pte",
            'chapman_result': chapman.dominant_category if chapman else "Pte",
            'motivation': s.motivation or "N/A"
        })
        
    return render(request, 'minigames/student_complete_profile_game.html', {
        'target_student': target, 'options': options_data, 'group': group,
        'correct': request.session['complete_profile_correct'], 'total': request.session['complete_profile_total']
    })

@login_required
def spotify_guess_game(request, group_id=None):
    if request.user.role == 'student':
        group = request.user.student_groups.first()
        if not group: return render(request, 'minigames/no_students.html')
        group_id = group.id
    elif not group_id: 
        return select_group_for_game(request, 'spotify_guess_game')
    
    group = get_object_or_404(ClassGroup, id=group_id)
    # Mejora: Excluir al propio usuario
    students = group.students.exclude(spotify_link__isnull=True).exclude(spotify_link='').exclude(id=request.user.id).distinct()
    
    if students.count() < 4:
        return render(request, 'minigames/not_enough_students.html', {
            'message': "Se necesitan al menos 4 compañeros con su canción de Spotify configurada."
        })
    
    if 'spotify_correct' not in request.session: request.session['spotify_correct'] = 0
    if 'spotify_total' not in request.session: request.session['spotify_total'] = 0
    
    if request.method == 'POST':
        is_correct = str(request.POST.get('selected_id')) == str(request.session.get('spotify_target_id'))
        request.session['spotify_total'] += 1
        if is_correct: request.session['spotify_correct'] += 1
        
        target = UserProfile.objects.get(id=request.session.get('spotify_target_id'))
        msg = f"¡Correcto! Es la canción de {target.full_name or target.username}" if is_correct else "¡Ups! No es de ese compañero."
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return get_ajax_response(request, is_correct, msg, 'spotify')
        return redirect('spotify_guess_game', group_id=group_id)

    last_id = request.session.get('spotify_last_id')
    possible_targets = students.exclude(id=last_id) if students.count() > 1 else students
    target = random.choice(possible_targets)
    
    request.session['spotify_target_id'] = target.id
    request.session['spotify_last_id'] = target.id
    
    options = list(random.sample(list(students.exclude(id=target.id)), 3)) + [target]
    random.shuffle(options)
    
    return render(request, 'minigames/spotify_guess_game.html', {
        'target_embed': target.spotify_embed_url,
        'options': options,
        'group': group,
        'correct': request.session['spotify_correct'],
        'total': request.session['spotify_total']
    })

@login_required
def dino_game(request):
    """
    Lógica para el juego del Dino. 
    Mantiene la coherencia con el resto de vistas del proyecto.
    """
    # En tus otras vistas usas request.user.student_groups.first() 
    # Vamos a usar lo mismo para evitar errores de atributo.
    group = None
    if request.user.role == 'student':
        group = request.user.student_groups.first()
    
    # Si quieres que el juego también tenga un contador de "Sesión" 
    # como tus otros juegos, podemos inicializarlo aquí:
    if 'dino_total' not in request.session:
        request.session['dino_total'] = 0

    return render(request, 'minigames/dino_game.html', {
        'group': group,
    })

@login_required
def impostor_game(request, group_id=None):
    """
    Juego del Impostor con control de historial para no repetir temas.
    """
    biblioteca_palabras = [
        {'tema': 'Futuro', 'p': 'Calidad de Vida', 'i': 'Estabilidad Económica'},
        {'tema': 'Pedagogía', 'p': 'Bosque-Escuela', 'i': 'Pedagogía Verde'},
        {'tema': 'Metodología', 'p': 'Pedagogía del Flow', 'i': 'Gamificación'},
        {'tema': 'EF Especializada', 'p': 'Aprendizaje de Aventura', 'i': 'Pedagogía Experidencial'},
        {'tema': 'Filosofía Educativa', 'p': 'Pedagogía Crítica', 'i': 'Transformación Social'},
        {'tema': 'Ocio', 'p': 'Pedagogía del Ocio', 'i': 'Recreación Deportiva'},
        {'tema': 'Inclusión', 'p': 'Interculturalidad', 'i': 'Pedagogía Social'},
        {'tema': 'Evaluación', 'p': 'Competencia', 'i': 'Capacidad'},
        # Enseñanza e Iniciación
    {'tema': 'Modelos', 'p': 'Modelo Técnico', 'i': 'Modelo Comprensivo'},
    {'tema': 'Iniciación', 'p': 'Deporte Escolar', 'i': 'Deporte Federado'},
    {'tema': 'Estructura', 'p': 'Táctica', 'i': 'Estrategia'},
    {'tema': 'Feedback', 'p': 'Conocimiento de los Resultados', 'i': 'Conocimiento de la Ejecución'},
    {'tema': 'Aprendizaje', 'p': 'Práctica Global', 'i': 'Práctica Analítica'},
    {'tema': 'Diseño', 'p': 'Tarea Jugada', 'i': 'Ejercicio'},

    # Historia y Epistemología
    {'tema': 'Grecia', 'p': 'Gimnasio', 'i': 'Palestra'},
    {'tema': 'Grecia', 'p': 'Esparta', 'i': 'Atenas'},
    {'tema': 'Edad Media', 'p': 'Justa', 'i': 'Torneo'},
    {'tema': 'Profesión', 'p': 'Colegiación', 'i': 'Asociacionismo'},
    {'tema': 'Roma', 'p': 'Circo Romano', 'i': 'Anfiteatro'},
    {'tema': 'Valores', 'p': 'Juego Limpio', 'i': 'Deportividad'},

    # Psicología del Deporte
    {'tema': 'Cognición', 'p': 'Atención', 'i': 'Concentración'},
    {'tema': 'Estado', 'p': 'Ansiedad', 'i': 'Estrés'},
    {'tema': 'Motivación', 'p': 'Intrínseca', 'i': 'Extrínseca'},
    {'tema': 'Conducta', 'p': 'Refuerzo', 'i': 'Castigo'},
    {'tema': 'Personalidad', 'p': 'Rasgo', 'i': 'Estado'},
    {'tema': 'Social', 'p': 'Liderazgo Autocrático', 'i': 'Liderazgo Democrático'},

    # Danza y Expresión
    {'tema': 'Laban', 'p': 'Espacio', 'i': 'Tiempo'},
    {'tema': 'Arte', 'p': 'Coreografía', 'i': 'Improvisación'},
    {'tema': 'Ritmo', 'p': 'Pulso', 'i': 'Acento'},
    {'tema': 'Composición', 'p': 'Canon', 'i': 'Unísono'},
    {'tema': 'Cuerpo', 'p': 'Esquema Corporal', 'i': 'Imagen Corporal'},

    # Atletismo
    {'tema': 'Carreras', 'p': 'Velocidad', 'i': 'Resistencia'},
    {'tema': 'Saltos', 'p': 'Longitud', 'i': 'Triple Salto'},
    {'tema': 'Vallas', 'p': 'Pierna de Ataque', 'i': 'Pierna de Recobro'},
    {'tema': 'Lanzamientos', 'p': 'Peso', 'i': 'Disco'},
    {'tema': 'Medición', 'p': 'Anemómetro', 'i': 'Cronómetro'},
    {'tema': 'Velocidad', 'p': 'Amplitud de Zancada', 'i': 'Frecuencia de Zancada'},

    # Vida Universitaria UEx
    {'tema': 'Evaluación', 'p': 'Examen Parcial', 'i': 'Examen Final'},
    {'tema': 'Título', 'p': 'CAFYD', 'i': 'Magisterio EF'}
    ]

    # 1. Recuperar el historial de la sesión
    historial = request.session.get('impostor_history', [])

    # 2. Filtrar palabras disponibles
    opciones_disponibles = [p for p in biblioteca_palabras if p['tema'] not in historial]

    # 3. Si no quedan opciones (o es la primera vez), reseteamos
    if not opciones_disponibles:
        opciones_disponibles = biblioteca_palabras
        historial = []

    # 4. Elegir palabra y actualizar historial en la sesión
    pack = random.choice(opciones_disponibles)
    historial.append(pack['tema'])
    
    request.session['impostor_history'] = historial
    request.session.modified = True  # Asegura que Django guarde los cambios

    context = {
        'palabra_correcta': pack['p'],
        'pista_impostor': pack['i'],
        'tema': pack['tema'].upper(),
        'group_id': group_id,
    }

    return render(request, 'minigames/impostor_game.html', context)

@login_required
def charadas_game(request, group_id=None):
    """
    Juego de mímica y charadas (tipo Heads Up).
    """
    biblioteca_charadas = {
        'ENSEÑANZA E INICIACIÓN': [
    # --- De los Temas 1 y 2 (Estructura y Habilidades) ---
    'Habilidad Motriz', 'Deporte Individual', 'Deporte de Equipo', 'Adversario', 
    'Blanco y Diana', 'Cancha Dividida', 'Incertidumbre', 'Espacio Común', 
    'Reglamento', 'Falta Técnica', 'Fuera de Juego',

    # --- De los Temas 3 y 4 (Modelos y Pericia) ---
    'Talento Deportivo', 'Modelo Técnico', 'Modelo Comprensivo', 'Creatividad', 
    'Gesto Deportivo', 'Repetición', 'Toma de Decisiones', 'Estrategia', 
    'Rendimiento Experto', 'Novato',

    # --- De los Temas 5, 6, 7 y 8 (Iniciación y Entrenador) ---
    'Iniciación Deportiva', 'Deporte Escolar', 'Competición', 'Victoria', 
    'Derrota', 'Juego Limpio', 'Entrenador', 'Silbato', 'Pizarra Táctica', 
    'Cronómetro', 'Sustitución', 'Tiempo Muerto', 'Edad Madurativa', 'Estímulo'
],

        'EPISTEMOLOGÍA E HISTORIA': [
    # --- Bloque Epistemología (Ciencia y Profesión) ---
    'Método Científico', 'Investigación', 'Laboratorio', 'Profesor de EF', 
    'Entrenador', 'Gestión Deportiva', 'Recreación', 'Director Deportivo',
    'Código Ético', 'Juego Limpio', 'Colegio Profesional', 'Pre-colegiación',
    'Igualdad', 'Diversidad', 'Deporte Espectáculo', 'Violencia Deportiva',

    # --- Bloque Historia (Antigüedad y Medievo) ---
    'Prehistoria', 'Caza y Supervivencia', 'Grecia Antigua', 'Juegos Olímpicos', 
    'Lucha Canaria', 'Maratón', 'Ilíada y Odisea', 'Platón', 'Aristóteles', 
    'Gladiador', 'Caballero Medieval', 'Torneo', 'Justa', 'Artes Guerreras',

    # --- Bloque Historia (Moderna y Contemporánea) ---
    'Renacimiento', 'Humanismo', 'Inglaterra', 'Burguesía', 'Reglamento', 
    'Pierre de Coubertin', 'Anillos Olímpicos', 'Antorcha', 'Ideología Política', 
    'Capitalismo', 'Dopaje'
],
    
        'PSICOLOGÍA DEL DEPORTE': [
    # --- Tema 1 y 2 (Introducción y Procesos Cognitivos) ---
    'Psicólogo del Deporte', 'Atención', 'Concentración', 'Percepción', 
    'Sensación', 'Memoria', 'Procesamiento de Información', 'Falso Recuerdo',

    # --- Tema 3 y 4 (Aprendizaje e Intervención) ---
    'Condicionamiento Clásico', 'Recompensa', 'Castigo', 'Observación', 
    'Imitación', 'Modificación de Conducta', 'Evaluación', 'Hábito de Sueño',

    # --- Tema 5 y 6 (Emoción, Personalidad y Motivación) ---
    'Personalidad', 'Emoción', 'Ansiedad', 'Estrés', 'Activación', 
    'Afrontamiento', 'Relajación', 'Autocontrol', 'Motivación', 
    'Abandono Deportivo', 'Éxito', 'Fracaso',

    # --- Tema 7 y 8 (Social y Ciclo Vital) ---
    'Liderazgo', 'Cohesión de Grupo', 'Comunicación', 'Role-playing', 
    'Dinámica de Grupo', 'Infancia', 'Tercera Edad', 'Retirada Deportiva'
],

        'DANZA Y EXPRESIÓN CORPORAL': [
    # --- Tema 1 y 2 (Fundamentos y Factores) ---
    'Danza', 'Técnica de Estilo', 'Técnica Creativa', 'Cuerpo', 'Espacio', 
    'Tiempo', 'Energía', 'Fluidez', 'Dimensión Expresiva', 'Comunicación',

    # --- Tema 3, 4 y 5 (Creación y Proyectos) ---
    'Proyecto Artístico', 'Simbolización', 'Feminismo', 'Identidad', 
    'Inventiva', 'Comparación', 'Combinación', 'Observador', 
    'Impresionismo', 'Análisis', 'Contexto',

    # --- Tema 6 y 7 (Didáctica y AFA) ---
    'Actividades Físico Artísticas', 'Docente Mediador', 'Escenario', 
    'Recursos Musicales', 'Dinámica de Grupo', 'Reflexión', 
    'Evaluación', 'Coreografía', 'Puesta en Escena', 'Inclusión'
],

        'INICIACIÓN AL ATLETISMO': [
    # --- Bloque I y II (Generalidades y Carreras) ---
    'Pista Cubierta', 'Aire Libre', 'Juez de Pista', 'Técnica de Carrera', 
    'Salida de Tacos', 'Foto-finish', 'Carrera de Velocidad', 'Maratón', 
    'Testigo', 'Zona de Transferencia', 'Paso de Valla', 'Descalificación',

    # --- Bloque III (Saltos) ---
    'Salto de Longitud', 'Triple Salto', 'Salto de Altura', 'Fosbury Flop', 
    'Tabla de Batida', 'Foso de Arena', 'Listón', 'Nulo', 'Viento a Favor',

    # --- Bloque IV (Lanzamientos y Otros) ---
    'Lanzamiento de Peso', 'Artefacto', 'Círculo de Lanzamiento', 'Parada', 
    'Lanzamiento Nulo', 'Fase de Impulso', 'Fase de Vuelo', 'Cronómetro', 
    'Educación Física', 'Escuela Deportiva'
],

        'PRESENTACIÓN': [
    # --- Personajes y Gente ---
    'Profesor', 'Delegado', 'Subdelegado', 'Bedel', 'Conserje', 'Alumno de Tercero', 
    'Novato', 'Graduado', 'Decano', 'Rector', 'Secretaria', 'Personal de Limpieza',

    # --- Lugares del Campus y alrededores ---
    'Cafetería', 'Gimnasio', 'Pabellón', 'Piscina', 'Pistas de Tenis', 'Laboratorio', 
    'Biblioteca', 'Reprografía', 'Salón de Actos', 'Despacho', 'Parking', 'Parada de Bus', 
    'Residencia', 'Césped', 'Cantina', 'Vestuarios',

    # --- Objetos y Material ---
    'Mochila', 'Carnet Universitario', 'Apuntes', 'Silbato', 'Cronómetro', 
    'Ordenador', 'Proyector', 'Pizarra', 'Tupper', 'Café', 'Botella de Agua', 
    'Chándal', 'Zapatillas', 'Cascos', 'Examen',

    # --- Situaciones y Vida Universitaria ---
    'Prácticas', 'Matrícula', 'Beca', 'Fiesta Universitaria', 'TFG', 'Erasmus', 
    'Exposición Oral', 'Trabajo en Grupo', 'Nota de Corte', 'Suspenso', 'Aprobado', 
    'Matrícula de Honor', 'Revisión de Examen'
],
        'DEPORTES': [
    # --- Deportes de Equipo (Clásicos y sala) ---
    'Baloncesto', 'Fútbol', 'Voleibol', 'Balonmano', 'Rugby', 'Waterpolo', 
    'Fútbol Sala', 'Hockey Hierba', 'Hockey Patines', 'Béisbol', 'Softbol',

    # --- Deportes de Raqueta y Implemento ---
    'Tenis', 'Pádel', 'Bádminton', 'Tenis de Mesa', 'Squash', 'Pickleball',

    # --- Deportes Individuales y Gimnásticos ---
    'Atletismo', 'Natación', 'Gimnasia Rítmica', 'Gimnasia Artística', 
    'Halterofilia', 'Ciclismo', 'Triatlón', 'Patinaje', 'Esgrima',

    # --- Deportes de Combate ---
    'Boxeo', 'Judo', 'Karate', 'Taekwondo', 'Lucha Libre', 'Kickboxing',

    # --- Deportes de Naturaleza y Aventura ---
    'Escalada', 'Senderismo', 'Piragüismo', 'Surf', 'Snowboard', 'Esquí', 
    'Orientación', 'Barranquismo', 'Vela', 'Equitación',

    # --- Deportes Alternativos y Nuevas Tendencias ---
    'Yoga', 'Pilates', 'Crossfit', 'Ultimate Frisbee', 'Parkour', 
    'Skateboarding', 'Golf', 'Tiro con Arco', 'Ajedrez Deportivo'
],
    }
    
    # Convertimos a JSON para pasarlo a JavaScript fácilmente
    import json
    context = {
        'biblioteca_json': json.dumps(biblioteca_charadas),
        'categorias': biblioteca_charadas.keys(),
        'group_id': group_id,
    }
    
    return render(request, 'minigames/charadas_game.html', context)