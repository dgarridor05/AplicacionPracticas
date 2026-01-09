from django.shortcuts import render, get_object_or_404
from accounts.models import UserProfile
from teachers.models import ClassGroup
from quizzes.models import UserResult, Questionnaire
from django.contrib.auth.decorators import login_required
import random
from django.contrib import messages
from django.shortcuts import redirect
from datetime import datetime

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

    # Inicializar contadores si no existen en la sesión
    if 'face_guess_correct' not in request.session:
        request.session['face_guess_correct'] = 0
    if 'face_guess_total' not in request.session:
        request.session['face_guess_total'] = 0

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        answer = request.POST.get('answer', '').strip().lower()

        try:
            student = UserProfile.objects.get(id=student_id)
        except UserProfile.DoesNotExist:
            messages.error(request, "Alumno no encontrado.")
            return redirect('face_guess_game')

        correct_names = [student.username.lower()]
        if student.nickname:
            correct_names.append(student.nickname.lower())

        request.session['face_guess_total'] += 1
        if answer in correct_names:
            request.session['face_guess_correct'] += 1
            messages.success(request, "¡Correcto!")
        else:
            messages.error(request, f"Incorrecto. Era: {student.nickname or student.username}")

        return redirect('face_guess_game')

    student = random.choice(students)

    return render(request, 'minigames/face_guess_game.html', {
        'student': student,
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
        messages.warning(request, "Se necesitan al menos 4 alumnos con foto de perfil para jugar.")
        return render(request, 'minigames/not_enough_students.html')

    # Inicializar contadores si no existen
    if 'name_to_face_correct' not in request.session:
        request.session['name_to_face_correct'] = 0
    if 'name_to_face_total' not in request.session:
        request.session['name_to_face_total'] = 0

    if request.method == 'POST':
        selected_id = request.POST.get('selected_id')
        target_id = request.POST.get('target_id')
        option_ids = request.POST.getlist('option_ids')

        request.session['name_to_face_total'] += 1
        if selected_id == target_id:
            request.session['name_to_face_correct'] += 1
            messages.success(request, "¡Correcto!")
        else:
            try:
                correct_index = option_ids.index(target_id)
                position = int(correct_index) + 1
                messages.error(request, f"Incorrecto. La respuesta correcta era la opción {position}.")
            except ValueError:
                messages.error(request, "Error al identificar la opción correcta.")

        return redirect('name_to_face_game')

    target = random.choice(students)
    options = random.sample(list(students.exclude(id=target.id)), 3)
    options.append(target)
    random.shuffle(options)

    return render(request, 'minigames/name_to_face_game.html', {
        'target_name': target.nickname or target.username,
        'target_id': str(target.id),
        'options': options,
        'option_ids': [str(option.id) for option in options],
        'correct': request.session['name_to_face_correct'],
        'total': request.session['name_to_face_total']
    })

@login_required
def student_interests_game(request):
    """
    Juego donde el profesor ve la foto y nombre de un estudiante,
    y debe adivinar cuáles son sus gustos personales entre 4 opciones.
    """
    groups = ClassGroup.objects.filter(teacher=request.user)
    
    # Filtrar estudiantes que tengan todos los campos necesarios
    students = UserProfile.objects.filter(
        role='student',
        student_groups__in=groups,
        profile_picture__isnull=False,
        favorite_artist__isnull=False,
        favorite_movie__isnull=False,
        favorite_song__isnull=False,
        motivation__isnull=False,
        date_of_birth__isnull=False
    ).exclude(
        profile_picture='',
        favorite_artist='',
        favorite_movie='',
        favorite_song='',
        motivation=''
    ).distinct()

    if students.count() < 4:
        messages.warning(request, "Se necesitan al menos 4 alumnos con información completa de gustos para jugar.")
        return render(request, 'minigames/not_enough_students.html')

    # Inicializar contadores si no existen
    if 'interests_correct' not in request.session:
        request.session['interests_correct'] = 0
    if 'interests_total' not in request.session:
        request.session['interests_total'] = 0

    if request.method == 'POST':
        selected_option = request.POST.get('selected_option')
        target_id = request.POST.get('target_id')
        correct_option = request.POST.get('correct_option')

        request.session['interests_total'] += 1
        if selected_option == correct_option:
            request.session['interests_correct'] += 1
            messages.success(request, "¡Correcto! Has identificado bien los gustos del estudiante.")
        else:
            messages.error(request, f"Incorrecto. La respuesta correcta era la opción {correct_option}.")

        return redirect('student_interests_game')

    # Seleccionar estudiante objetivo
    target = random.choice(students)
    
    # Crear la descripción correcta
    def create_interest_description(student):
        """Crea una descripción narrativa de los gustos del estudiante"""
        age = calculate_age(student.date_of_birth) if student.date_of_birth else "edad desconocida"
        
        description = f"Tiene {age} años y su motivación es: {student.motivation}. "
        description += f"Le encanta escuchar '{student.favorite_song}', "
        description += f"su artista favorito es {student.favorite_artist} y su película favorita es '{student.favorite_movie}'."
        
        return description
    
    def calculate_age(birth_date):
        """Calcula la edad a partir de la fecha de nacimiento"""
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    # Crear descripciones falsas mezclando datos de otros estudiantes
    def create_fake_descriptions(target_student, all_students):
        """Crea 3 descripciones falsas mezclando datos reales de otros estudiantes"""
        fake_descriptions = []
        other_students = list(all_students.exclude(id=target_student.id))
        
        for i in range(3):
            # Seleccionar datos aleatorios de diferentes estudiantes
            song_student = random.choice(other_students)
            artist_student = random.choice(other_students)
            movie_student = random.choice(other_students)
            motivation_student = random.choice(other_students)
            birth_student = random.choice(other_students)
            
            age = calculate_age(birth_student.date_of_birth) if birth_student.date_of_birth else "edad desconocida"
            
            fake_desc = f"Tiene {age} años y su motivación es: {motivation_student.motivation}. "
            fake_desc += f"Le encanta escuchar '{song_student.favorite_song}', "
            fake_desc += f"su artista favorito es {artist_student.favorite_artist} y su película favorita es '{movie_student.favorite_movie}'."
            
            fake_descriptions.append(fake_desc)
        
        return fake_descriptions
    
    # Crear todas las opciones
    correct_description = create_interest_description(target)
    fake_descriptions = create_fake_descriptions(target, students)
    
    # Combinar y mezclar opciones
    all_options = fake_descriptions + [correct_description]
    random.shuffle(all_options)
    
    # Encontrar la posición de la opción correcta
    correct_position = all_options.index(correct_description) + 1
    
    return render(request, 'minigames/student_interests_game.html', {
        'target_student': target,
        'target_name': target.nickname or target.username,
        'target_id': str(target.id),
        'options': all_options,
        'correct_option': str(correct_position),
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

@login_required
def hangman_game(request):
    """
    Juego tipo ahorcado donde se ve la foto del estudiante y hay que adivinar su nombre.
    Se permiten máximo 4 letras incorrectas antes de perder.
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
        # Nuevo juego
        student = random.choice(students)
        # Usar full_name si existe, sino username
        target_name = (student.full_name or student.username).upper()
        
        request.session['hangman_current_student'] = student.id
        request.session['hangman_target_name'] = target_name
        request.session['hangman_guessed_letters'] = []
        request.session['hangman_incorrect_letters'] = []
        request.session['hangman_game_over'] = False
        request.session['hangman_won'] = False

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'new_game':
            # Reiniciar para nuevo juego
            del request.session['hangman_current_student']
            return redirect('hangman_game')
        
        elif action == 'guess_letter':
            letter = request.POST.get('letter', '').upper()
            
            if letter and len(letter) == 1 and letter.isalpha():
                target_name = request.session['hangman_target_name']
                guessed_letters = request.session['hangman_guessed_letters']
                incorrect_letters = request.session['hangman_incorrect_letters']
                
                if letter not in guessed_letters and letter not in incorrect_letters:
                    if letter in target_name:
                        guessed_letters.append(letter)
                        request.session['hangman_guessed_letters'] = guessed_letters
                        
                        # Verificar si se ha completado la palabra
                        if all(char in guessed_letters or not char.isalpha() for char in target_name):
                            request.session['hangman_won'] = True
                            request.session['hangman_game_over'] = True
                            request.session['hangman_correct'] += 1
                            request.session['hangman_total'] += 1
                            messages.success(request, f"¡Felicidades! Has adivinado: {target_name}")
                    else:
                        incorrect_letters.append(letter)
                        request.session['hangman_incorrect_letters'] = incorrect_letters
                        
                        # Verificar si se perdió (4 letras incorrectas)
                        if len(incorrect_letters) >= 4:
                            request.session['hangman_game_over'] = True
                            request.session['hangman_won'] = False
                            request.session['hangman_total'] += 1
                            messages.error(request, f"¡Has perdido! La respuesta era: {target_name}")
                else:
                    messages.warning(request, "Ya has probado esa letra.")
            else:
                messages.error(request, "Por favor, introduce una letra válida.")

    # Obtener datos actuales del juego
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

    # Crear la palabra con guiones y letras adivinadas
    displayed_name = ''.join(
        char if char in guessed_letters or not char.isalpha() else '_'
        for char in target_name
    )

    # Generar alphabet para mostrar botones
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    used_letters = set(guessed_letters + incorrect_letters)

    return render(request, 'minigames/hangman_game.html', {
        'current_student': current_student,
        'target_name': target_name,
        'displayed_name': displayed_name,
        'guessed_letters': guessed_letters,
        'incorrect_letters': incorrect_letters,
        'incorrect_count': len(incorrect_letters),
        'max_incorrect': 4,
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

    # Inicializar contadores si no existen en la sesión
    if 'complete_profile_correct' not in request.session:
        request.session['complete_profile_correct'] = 0
    if 'complete_profile_total' not in request.session:
        request.session['complete_profile_total'] = 0

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        selected_option = request.POST.get('selected_option')

        try:
            correct_student = UserProfile.objects.get(id=student_id)
        except UserProfile.DoesNotExist:
            messages.error(request, "Alumno no encontrado.")
            return redirect('student_complete_profile_game')

        request.session['complete_profile_total'] += 1
        
        if selected_option == '0':  # La opción correcta siempre será la 0
            request.session['complete_profile_correct'] += 1
            messages.success(request, "¡Correcto! Has identificado todos los datos del alumno.")
        else:
            messages.error(request, f"Incorrecto. Los datos correctos eran del estudiante: {correct_student.full_name or correct_student.username}")

        return redirect('student_complete_profile_game')

    # Seleccionar estudiante objetivo
    target_student = random.choice(students)
    
    # Obtener resultados de tests del estudiante objetivo
    target_results = UserResult.objects.filter(user=target_student)
    
    # Crear datos completos del estudiante objetivo
    def get_student_complete_data(student):
        results = UserResult.objects.filter(user=student)
        
        # Obtener resultados de tests
        chapman_result = "No realizado"
        vark_result = "No realizado"
        
        for result in results:
            if "Chapman" in result.questionnaire.title:
                chapman_result = result.get_dominant_category_display()
            elif "VARK" in result.questionnaire.title:
                vark_result = result.get_dominant_category_display()
        
        # Calcular edad a partir de fecha de nacimiento
        age = "No especificada"
        if student.date_of_birth:
            from datetime import date
            today = date.today()
            age = today.year - student.date_of_birth.year - ((today.month, today.day) < (student.date_of_birth.month, student.date_of_birth.day))
        
        return {
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

    # Datos correctos del estudiante objetivo
    correct_data = get_student_complete_data(target_student)

    # Obtener otros 3 estudiantes para crear opciones incorrectas
    other_students = students.exclude(id=target_student.id)
    decoy_students = random.sample(list(other_students), min(3, len(other_students)))

    # Crear 4 opciones mezclando datos
    options = []
    
    # Opción correcta (posición 0)
    options.append(correct_data)
    
    # Opciones incorrectas (mezclar datos de otros estudiantes)
    for i, decoy in enumerate(decoy_students):
        decoy_data = get_student_complete_data(decoy)
        
        # Mezclar algunos datos correctos con incorrectos para hacer más difícil
        mixed_data = correct_data.copy()
        
        # Cambiar algunos campos por datos incorrectos
        if i == 0:  # Cambiar nombre y tests
            mixed_data['full_name'] = decoy_data['full_name']
            mixed_data['username'] = decoy_data['username']
            mixed_data['chapman_result'] = decoy_data['chapman_result']
            mixed_data['vark_result'] = decoy_data['vark_result']
        elif i == 1:  # Cambiar datos personales
            mixed_data['age'] = decoy_data['age']
            mixed_data['gender'] = decoy_data['gender']
            mixed_data['date_of_birth'] = decoy_data['date_of_birth']
            mixed_data['emotional_reinforcement'] = decoy_data['emotional_reinforcement']
        else:  # Cambiar gustos y preferencias
            mixed_data['nickname'] = decoy_data['nickname']
            mixed_data['favorite_artist'] = decoy_data['favorite_artist']
            mixed_data['favorite_movie'] = decoy_data['favorite_movie']
            mixed_data['favorite_song'] = decoy_data['favorite_song']
            mixed_data['learning_style'] = decoy_data['learning_style']
            mixed_data['motivation'] = decoy_data['motivation']
            
        options.append(mixed_data)

    # Mezclar las opciones (excepto la primera que debe mantenerse como correcta)
    incorrect_options = options[1:]
    random.shuffle(incorrect_options)
    options = [options[0]] + incorrect_options

    return render(request, 'minigames/student_complete_profile_game.html', {
        'target_student': target_student,
        'options': options,
        'correct': request.session['complete_profile_correct'],
        'total': request.session['complete_profile_total']
    })