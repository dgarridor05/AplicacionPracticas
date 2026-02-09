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
        {'tema': 'Evaluación', 'p': 'Competencia', 'i': 'Capacidad'}
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