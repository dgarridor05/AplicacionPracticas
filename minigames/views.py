from django.shortcuts import render, get_object_or_404
from accounts.models import UserProfile
from teachers.models import ClassGroup
from quizzes.models import UserResult, Questionnaire
from django.contrib.auth.decorators import login_required
import random
from django.contrib import messages
from django.shortcuts import redirect
from datetime import datetime
import unicodedata
from django.shortcuts import render, redirect
from datetime import date

def normalize_text(text):
    """Elimina tildes, espacios extra y lo pasa a minúsculas."""
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text)
    text = "".join([c for c in text if unicodedata.category(c) != 'Mn'])
    return text.lower().strip()

@login_required
def face_guess_game(request):
    groups = ClassGroup.objects.filter(teacher=request.user)
    students = UserProfile.objects.filter(
        role='student',
        student_groups__in=groups,
        profile_picture__isnull=False
    ).exclude(profile_picture='').distinct()

    if not students.exists():
        return render(request, 'minigames/no_students.html')

    # Inicializar contadores
    if 'face_guess_correct' not in request.session:
        request.session['face_guess_correct'] = 0
    if 'face_guess_total' not in request.session:
        request.session['face_guess_total'] = 0

    if request.method == 'POST':
        # Recuperamos el ID que guardamos en la sesión al cargar la página
        target_id = request.session.get('face_guess_target_id')
        answer = normalize_text(request.POST.get('answer', ''))

        try:
            student = UserProfile.objects.get(id=target_id)
        except UserProfile.DoesNotExist:
            messages.error(request, "Error al recuperar el alumno.")
            return redirect('face_guess_game')

        # Creamos una lista de posibles respuestas válidas normalizadas
        valid_answers = [
            normalize_text(student.username),
            normalize_text(student.first_name),
            normalize_text(student.last_name),
            normalize_text(student.full_name),
            normalize_text(student.nickname),
        ]
        # Eliminamos valores vacíos de la lista
        valid_answers = [a for a in valid_answers if a]

        request.session['face_guess_total'] += 1
        
        if answer in valid_answers:
            request.session['face_guess_correct'] += 1
            messages.success(request, f"¡Correcto! Es {student.full_name or student.username}")
        else:
            messages.error(request, f"Incorrecto. Era: {student.full_name or student.username}")

        return redirect('face_guess_game')

    # --- Lógica para seleccionar alumno (Anti-repetición) ---
    last_id = request.session.get('face_guess_last_id')
    available_students = students.exclude(id=last_id) if last_id and students.count() > 1 else students
    target_student = random.choice(available_students)

    # Guardamos en sesión tanto para el POST como para la siguiente ronda
    request.session['face_guess_target_id'] = target_student.id
    request.session['face_guess_last_id'] = target_student.id

    return render(request, 'minigames/face_guess_game.html', {
        'student': target_student,
        'correct': request.session['face_guess_correct'],
        'total': request.session['face_guess_total']
    })

@login_required
def name_to_face_game(request):
    groups = ClassGroup.objects.filter(teacher=request.user)
    students = UserProfile.objects.filter(
        role='student',
        student_groups__in=groups,
        profile_picture__isnull=False
    ).exclude(profile_picture='').distinct()

    if students.count() < 4:
        messages.warning(request, "Se necesitan al menos 4 alumnos con foto para jugar.")
        return render(request, 'minigames/not_enough_students.html')

    if 'name_to_face_correct' not in request.session:
        request.session['name_to_face_correct'] = 0
    if 'name_to_face_total' not in request.session:
        request.session['name_to_face_total'] = 0

    if request.method == 'POST':
        selected_id = request.POST.get('selected_id')
        # MEJORA: Obtenemos el ID correcto de la sesión (Seguridad)
        target_id = request.session.get('name_to_face_target_id')

        request.session['name_to_face_total'] += 1
        
        if str(selected_id) == str(target_id):
            request.session['name_to_face_correct'] += 1
            messages.success(request, "¡Correcto! Has reconocido al alumno.")
        else:
            try:
                target_student = UserProfile.objects.get(id=target_id)
                wrong_student = UserProfile.objects.get(id=selected_id)
                messages.error(request, f"Incorrecto. Elegiste a {wrong_student.full_name or wrong_student.username}, pero buscábamos a {target_student.full_name or target_student.username}.")
            except:
                messages.error(request, "Incorrecto. No era ese alumno.")

        return redirect('name_to_face_game')

    # MEJORA: Sistema anti-repetición
    last_id = request.session.get('name_to_face_last_id')
    available_students = students.exclude(id=last_id) if last_id and students.count() > 1 else students
    
    target = random.choice(available_students)
    
    # Guardamos en sesión el objetivo para validar en el POST
    request.session['name_to_face_target_id'] = target.id
    request.session['name_to_face_last_id'] = target.id

    # Seleccionamos 3 señuelos
    decoys = students.exclude(id=target.id)
    options = random.sample(list(decoys), 3)
    options.append(target)
    random.shuffle(options)

    return render(request, 'minigames/name_to_face_game.html', {
        # MEJORA: Priorizamos nombre completo para un lenguaje más natural
        'target_name': target.full_name or target.nickname or target.username,
        'options': options,
        'correct': request.session['name_to_face_correct'],
        'total': request.session['name_to_face_total']
    })

def calculate_age(birth_date):
    if not birth_date: return "desconocida"
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

@login_required
def student_interests_game(request):
    groups = ClassGroup.objects.filter(teacher=request.user)
    
    # Estudiantes con perfil completo
    students = UserProfile.objects.filter(
        role='student',
        student_groups__in=groups,
        profile_picture__isnull=False,
        favorite_artist__isnull=False,
        favorite_movie__isnull=False,
        favorite_song__isnull=False,
        motivation__isnull=False,
        date_of_birth__isnull=False
    ).exclude(profile_picture='', favorite_artist='', favorite_movie='', favorite_song='', motivation='').distinct()

    if students.count() < 4:
        messages.warning(request, "Necesitas al menos 4 alumnos con el perfil completo.")
        return render(request, 'minigames/not_enough_students.html')

    if 'interests_correct' not in request.session:
        request.session['interests_correct'] = 0
    if 'interests_total' not in request.session:
        request.session['interests_total'] = 0

    if request.method == 'POST':
        selected_option = request.POST.get('selected_option')
        # Seguridad: Recuperamos la respuesta correcta de la sesión
        correct_option = request.session.get('interests_correct_pos')

        request.session['interests_total'] += 1
        if str(selected_option) == str(correct_option):
            request.session['interests_correct'] += 1
            messages.success(request, "¡Increíble! Conoces muy bien sus intereses.")
        else:
            messages.error(request, f"Esa no era. La opción correcta era la {correct_option}.")
        
        return redirect('student_interests_game')

    # Anti-repetición
    last_id = request.session.get('interests_last_id')
    available = students.exclude(id=last_id) if last_id else students
    target = random.choice(available)
    request.session['interests_last_id'] = target.id

    # Función para crear descripción
    def get_desc(s):
        age = calculate_age(s.date_of_birth)
        return (f"Tiene {age} años. Su motivación es: {s.motivation}. "
                f"Le encanta '{s.favorite_song}', su artista es {s.favorite_artist} "
                f"y su película favorita es '{s.favorite_movie}'.")

    # Crear la opción correcta
    correct_description = get_desc(target)
    
    # Crear 3 opciones falsas (mentiras mezcladas)
    other_students = list(students.exclude(id=target.id))
    fake_options = []
    
    while len(fake_options) < 3:
        # Mezclamos datos de otros para crear una descripción falsa
        s1, s2, s3, s4 = random.sample(other_students, 4) if len(other_students) >= 4 else random.choices(other_students, k=4)
        
        age = calculate_age(s1.date_of_birth)
        f_desc = (f"Tiene {age} años. Su motivación es: {s2.motivation}. "
                  f"Le encanta '{s3.favorite_song}', su artista es {s4.favorite_artist} "
                  f"y su película favorita es '{s1.favorite_movie}'.")
        
        if f_desc not in fake_options and f_desc != correct_description:
            fake_options.append(f_desc)

    # Mezclar todo
    all_options = fake_options + [correct_description]
    random.shuffle(all_options)
    
    # Guardar posición correcta en sesión (del 1 al 4)
    request.session['interests_correct_pos'] = all_options.index(correct_description) + 1

    return render(request, 'minigames/student_interests_game.html', {
        'target_student': target,
        'target_name': target.full_name or target.nickname or target.username,
        'options': all_options,
        'correct': request.session['interests_correct'],
        'total': request.session['interests_total']
    })

@login_required
def quiz_results_game(request):
    """
    Juego donde el profesor ve la foto y nombre de un estudiante,
    y debe adivinar cuáles son sus resultados en los tests VARK y Chapman entre 4 opciones.
    """
    groups = ClassGroup.objects.filter(teacher=request.user)

    # Obtener los cuestionarios
    try:
        vark_q = Questionnaire.objects.get(title="VARK")
        chapman_q = Questionnaire.objects.get(title="Chapman")
    except Questionnaire.DoesNotExist:
        messages.error(request, "No se encontraron los cuestionarios VARK o Chapman.")
        return redirect('teacher_home')  # o cambia a una vista válida

    # Filtrar estudiantes con foto
    students_with_photo = UserProfile.objects.filter(
        role='student',
        student_groups__in=groups,
        profile_picture__isnull=False
    ).exclude(profile_picture='').distinct()

    # Verificar que tengan resultados de ambos tests
    students_with_tests = []
    for student in students_with_photo:
        vark_result = UserResult.objects.filter(user=student, questionnaire=vark_q).first()
        chapman_result = UserResult.objects.filter(user=student, questionnaire=chapman_q).first()

        if vark_result and chapman_result:
            students_with_tests.append(student)

    if len(students_with_tests) < 4:
        messages.warning(request, "Se necesitan al menos 4 alumnos con resultados completos de ambos tests para jugar.")
        return render(request, 'minigames/not_enough_students.html')

    # Inicializar contadores si no existen
    if 'quiz_results_correct' not in request.session:
        request.session['quiz_results_correct'] = 0
    if 'quiz_results_total' not in request.session:
        request.session['quiz_results_total'] = 0

    if request.method == 'POST':
        selected_option = request.POST.get('selected_option')
        target_id = request.POST.get('target_id')
        correct_option = request.POST.get('correct_option')

        request.session['quiz_results_total'] += 1
        if selected_option == correct_option:
            request.session['quiz_results_correct'] += 1
            messages.success(request, "¡Correcto! Has identificado bien los resultados del estudiante.")
        else:
            messages.error(request, f"Incorrecto. La respuesta correcta era la opción {correct_option}.")

        return redirect('quiz_results_game')

    # Seleccionar estudiante objetivo
    target = random.choice(students_with_tests)

    def get_quiz_results_description(student):
        vark_result = UserResult.objects.filter(user=student, questionnaire=vark_q).first()
        chapman_result = UserResult.objects.filter(user=student, questionnaire=chapman_q).first()

        vark_text = vark_result.dominant_category if vark_result else "No disponible"
        chapman_text = chapman_result.dominant_category if chapman_result else "No disponible"

        return f"Test VARK: {vark_text}. Test Chapman: {chapman_text}."

    def create_fake_quiz_descriptions(target_student, all_students):
        fake_descriptions = []
        other_students = [s for s in all_students if s.id != target_student.id]

        for _ in range(3):
            vark_student = random.choice(other_students)
            chapman_student = random.choice(other_students)

            vark_result = UserResult.objects.filter(user=vark_student, questionnaire=vark_q).first()
            chapman_result = UserResult.objects.filter(user=chapman_student, questionnaire=chapman_q).first()

            vark_text = vark_result.dominant_category if vark_result else "No disponible"
            chapman_text = chapman_result.dominant_category if chapman_result else "No disponible"

            fake_descriptions.append(f"Test VARK: {vark_text}. Test Chapman: {chapman_text}.")

        return fake_descriptions

    correct_description = get_quiz_results_description(target)
    fake_descriptions = create_fake_quiz_descriptions(target, students_with_tests)
    all_options = fake_descriptions + [correct_description]
    random.shuffle(all_options)
    correct_position = all_options.index(correct_description) + 1

    return render(request, 'minigames/quiz_results_game.html', {
        'target_student': target,
        'target_name': target.nickname or target.username,
        'target_id': str(target.id),
        'options': all_options,
        'correct_option': str(correct_position),
        'correct': request.session['quiz_results_correct'],
        'total': request.session['quiz_results_total']
    })

def normalize_char(char):
    """Convierte caracteres con tilde en su versión base (ej: Á -> A)"""
    if not char:
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', char)
                  if unicodedata.category(c) != 'Mn').upper()

@login_required
def hangman_game(request):
    """
    Juego tipo ahorcado donde se ve la foto del estudiante y hay que adivinar su nombre.
    Soporta tildes y permite máximo 6 letras incorrectas.
    """
    groups = ClassGroup.objects.filter(teacher=request.user)
    students = UserProfile.objects.filter(
        role='student',
        student_groups__in=groups,
        profile_picture__isnull=False
    ).exclude(profile_picture='').distinct()

    if not students.exists():
        return render(request, 'minigames/no_students.html')

    # Inicializar contadores si no existen en la sesión
    if 'hangman_correct' not in request.session:
        request.session['hangman_correct'] = 0
    if 'hangman_total' not in request.session:
        request.session['hangman_total'] = 0

    # Inicializar estado del juego si no existe
    if 'hangman_current_student' not in request.session:
        last_student_id = request.session.get('hangman_last_student_id')
        available_students = students.exclude(id=last_student_id) if last_student_id else students
        
        if not available_students.exists():
            available_students = students

        student = random.choice(available_students)
        target_name = (student.full_name or student.username).upper()
        
        request.session['hangman_current_student'] = student.id
        request.session['hangman_last_student_id'] = student.id
        request.session['hangman_target_name'] = target_name
        request.session['hangman_guessed_letters'] = []
        request.session['hangman_incorrect_letters'] = []
        request.session['hangman_game_over'] = False
        request.session['hangman_won'] = False

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'new_game':
            del request.session['hangman_current_student']
            return redirect('hangman_game')
        
        elif action == 'guess_letter':
            letter = request.POST.get('letter', '').upper()
            
            if letter and len(letter) == 1 and letter.isalpha():
                target_name = request.session['hangman_target_name']
                guessed_letters = request.session['hangman_guessed_letters']
                incorrect_letters = request.session['hangman_incorrect_letters']
                
                if letter not in guessed_letters and letter not in incorrect_letters:
                    # Comprobamos contra la versión sin tildes del nombre
                    if letter in normalize_char(target_name):
                        guessed_letters.append(letter)
                        request.session['hangman_guessed_letters'] = guessed_letters
                        
                        # Verificación de victoria ignorando tildes
                        if all(normalize_char(char) in guessed_letters or not char.isalpha() for char in target_name):
                            request.session['hangman_won'] = True
                            request.session['hangman_game_over'] = True
                            request.session['hangman_correct'] += 1
                            request.session['hangman_total'] += 1
                            messages.success(request, f"¡Felicidades! Has adivinado: {target_name}")
                    else:
                        incorrect_letters.append(letter)
                        request.session['hangman_incorrect_letters'] = incorrect_letters
                        
                        if len(incorrect_letters) >= 6:
                            request.session['hangman_game_over'] = True
                            request.session['hangman_won'] = False
                            request.session['hangman_total'] += 1
                            messages.error(request, f"¡Has perdido! La respuesta era: {target_name}")
                else:
                    messages.warning(request, "Ya has probado esa letra.")
            else:
                messages.error(request, "Por favor, introduce una letra válida.")

    try:
        current_student = UserProfile.objects.get(id=request.session['hangman_current_student'])
    except UserProfile.DoesNotExist:
        del request.session['hangman_current_student']
        return redirect('hangman_game')

    target_name = request.session['hangman_target_name']
    guessed_letters = request.session['hangman_guessed_letters']
    incorrect_letters = request.session['hangman_incorrect_letters']
    game_over = request.session['hangman_game_over']
    won = request.session['hangman_won']

    # Mostramos la letra con su tilde original si la versión base ha sido adivinada
    displayed_name = ''.join(
        char if normalize_char(char) in guessed_letters or not char.isalpha() else '_'
        for char in target_name
    )

    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    used_letters = set(guessed_letters + incorrect_letters)

    return render(request, 'minigames/hangman_game.html', {
        'current_student': current_student,
        'target_name': target_name,
        'displayed_name': displayed_name,
        'guessed_letters': guessed_letters,
        'incorrect_letters': incorrect_letters,
        'incorrect_count': len(incorrect_letters),
        'max_incorrect': 6,
        'game_over': game_over,
        'won': won,
        'alphabet': alphabet,
        'used_letters': used_letters,
        'correct': request.session['hangman_correct'],
        'total': request.session['hangman_total']
    })

@login_required
def student_complete_profile_game(request):
    groups = ClassGroup.objects.filter(teacher=request.user)
    students = UserProfile.objects.filter(
        role='student',
        student_groups__in=groups,
        profile_picture__isnull=False
    ).exclude(profile_picture='').distinct()

    if students.count() < 4:
        return render(request, 'minigames/not_enough_students.html')

    # Inicializar contadores en la sesión
    if 'complete_profile_correct' not in request.session:
        request.session['complete_profile_correct'] = 0
    if 'complete_profile_total' not in request.session:
        request.session['complete_profile_total'] = 0

    if request.method == 'POST':
        # Obtenemos el ID del estudiante que el profesor ha seleccionado como correcto
        selected_student_id = request.POST.get('selected_student_id')
        # Obtenemos el ID que el servidor guardó como el correcto en este turno
        target_id = request.session.get('complete_profile_target_id')

        request.session['complete_profile_total'] += 1
        
        if str(selected_student_id) == str(target_id):
            request.session['complete_profile_correct'] += 1
            messages.success(request, "¡Correcto! Has identificado todos los datos del alumno.")
        else:
            try:
                correct_obj = UserProfile.objects.get(id=target_id)
                nombre_correcto = correct_obj.full_name or correct_obj.username
            except:
                nombre_correcto = "el alumno indicado"
            messages.error(request, f"Incorrecto. Los datos pertenecían a: {nombre_correcto}")

        return redirect('student_complete_profile_game')

    # --- MEJORA 1: ANTI-REPETICIÓN ---
    last_id = request.session.get('complete_profile_last_id')
    available_students = students.exclude(id=last_id) if last_id and students.count() > 1 else students
    target_student = random.choice(available_students)
    
    # Guardamos el ID correcto en la sesión para validarlo en el POST
    request.session['complete_profile_target_id'] = target_student.id
    request.session['complete_profile_last_id'] = target_student.id

    def get_student_complete_data(student):
        results = UserResult.objects.filter(user=student)
        chapman_result = "No realizado"
        vark_result = "No realizado"
        
        for result in results:
            if "Chapman" in result.questionnaire.title:
                chapman_result = result.get_dominant_category_display()
            elif "VARK" in result.questionnaire.title:
                vark_result = result.get_dominant_category_display()
        
        age = "No especificada"
        if student.date_of_birth:
            today = date.today()
            age = today.year - student.date_of_birth.year - ((today.month, today.day) < (student.date_of_birth.month, student.date_of_birth.day))
        
        return {
            'student_id': student.id, # IMPORTANTE: Guardamos el ID para identificar la opción
            'full_name': student.full_name or f"{student.first_name} {student.last_name}",
            'username': student.username,
            'nickname': student.nickname or "Sin apodo",
            'age': str(age),
            'date_of_birth': student.date_of_birth.strftime("%d/%m/%Y") if student.date_of_birth else "No especificada",
            'gender': student.get_gender_display() if student.gender else "No especificado",
            'emotional_reinforcement': student.emotional_reinforcement or "No especificado",
            'favorite_artist': student.favorite_artist or "No especificado",
            'favorite_movie': student.favorite_movie or "No especificada",
            'favorite_song': student.favorite_song or "No especificada",
            'learning_style': student.learning_style or "No especificado",
            'chapman_result': chapman_result,
            'vark_result': vark_result,
            'motivation': student.motivation or "No especificada"
        }

    # Datos correctos
    correct_data = get_student_complete_data(target_student)

    # Generar opciones incorrectas (Decoys)
    other_students = students.exclude(id=target_student.id)
    decoy_students = random.sample(list(other_students), min(3, len(other_students)))

    options = []
    # Añadimos la opción correcta
    options.append(correct_data)
    
    # Añadimos las incorrectas mezclando datos para subir la dificultad
    for i, decoy in enumerate(decoy_students):
        decoy_data = get_student_complete_data(decoy)
        mixed_data = correct_data.copy()
        
        # El ID de la opción DEBE ser el del decoy para que sea incorrecto al comparar
        mixed_data['student_id'] = decoy.id 
        
        if i == 0:
            mixed_data['full_name'] = decoy_data['full_name']
            mixed_data['username'] = decoy_data['username']
        elif i == 1:
            mixed_data['age'] = decoy_data['age']
            mixed_data['favorite_movie'] = decoy_data['favorite_movie']
        else:
            mixed_data['favorite_artist'] = decoy_data['favorite_artist']
            mixed_data['vark_result'] = decoy_data['vark_result']
            
        options.append(mixed_data)

    # --- MEJORA 2: ALEATORIEDAD REAL ---
    # Mezclamos TODAS las opciones para que la correcta no esté siempre arriba
    random.shuffle(options)

    return render(request, 'minigames/student_complete_profile_game.html', {
        'target_student': target_student,
        'options': options,
        'correct': request.session['complete_profile_correct'],
        'total': request.session['complete_profile_total']
    })