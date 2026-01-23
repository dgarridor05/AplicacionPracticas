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
    if not text: return ""
    text = unicodedata.normalize('NFD', text)
    text = "".join([c for c in text if unicodedata.category(c) != 'Mn'])
    return text.lower().strip()

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

# --- VISTAS DE JUEGOS ---

@login_required
def face_guess_game(request):
    groups = ClassGroup.objects.filter(teacher=request.user)
    students = UserProfile.objects.filter(role='student', student_groups__in=groups, profile_picture__isnull=False).exclude(profile_picture='').distinct()
    if not students.exists(): return render(request, 'minigames/no_students.html')
    if 'face_guess_correct' not in request.session: request.session['face_guess_correct'] = 0
    if 'face_guess_total' not in request.session: request.session['face_guess_total'] = 0
    if request.method == 'POST':
        target_id = request.session.get('face_guess_target_id')
        answer = normalize_text(request.POST.get('answer', ''))
        student = get_object_or_404(UserProfile, id=target_id)
        valid_answers = [normalize_text(getattr(student, f)) for f in ['username', 'first_name', 'last_name', 'full_name', 'nickname'] if getattr(student, f)]
        request.session['face_guess_total'] += 1
        is_correct = answer in valid_answers
        if is_correct: request.session['face_guess_correct'] += 1
        msg = f"¡Correcto! Es {student.full_name or student.username}" if is_correct else f"Incorrecto. Era: {student.full_name or student.username}"
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': return get_ajax_response(request, is_correct, msg, 'face_guess')
        return redirect('face_guess_game')
    target_student = random.choice(students.exclude(id=request.session.get('face_guess_last_id')) if students.count() > 1 else students)
    request.session['face_guess_target_id'] = target_student.id
    request.session['face_guess_last_id'] = target_student.id
    return render(request, 'minigames/face_guess_game.html', {'student': target_student, 'correct': request.session['face_guess_correct'], 'total': request.session['face_guess_total']})

@login_required
def name_to_face_game(request):
    groups = ClassGroup.objects.filter(teacher=request.user)
    students = UserProfile.objects.filter(role='student', student_groups__in=groups, profile_picture__isnull=False).exclude(profile_picture='').distinct()
    if students.count() < 4: return render(request, 'minigames/not_enough_students.html')
    if 'name_to_face_correct' not in request.session: request.session['name_to_face_correct'] = 0
    if 'name_to_face_total' not in request.session: request.session['name_to_face_total'] = 0
    if request.method == 'POST':
        is_correct = str(request.POST.get('selected_id')) == str(request.session.get('name_to_face_target_id'))
        request.session['name_to_face_total'] += 1
        if is_correct: request.session['name_to_face_correct'] += 1
        msg = "¡Correcto!" if is_correct else "Incorrecto."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': return get_ajax_response(request, is_correct, msg, 'name_to_face')
        return redirect('name_to_face_game')
    target = random.choice(students.exclude(id=request.session.get('name_to_face_last_id')) if students.count() > 1 else students)
    request.session['name_to_face_target_id'] = target.id
    request.session['name_to_face_last_id'] = target.id
    options = list(random.sample(list(students.exclude(id=target.id)), 3)) + [target]
    random.shuffle(options)
    return render(request, 'minigames/name_to_face_game.html', {'target_name': target.full_name or target.username, 'options': options, 'correct': request.session['name_to_face_correct'], 'total': request.session['name_to_face_total']})

@login_required
def student_interests_game(request):
    groups = ClassGroup.objects.filter(teacher=request.user)
    students = UserProfile.objects.filter(role='student', student_groups__in=groups).distinct()
    if students.count() < 4: return render(request, 'minigames/not_enough_students.html')
    if 'interests_correct' not in request.session: request.session['interests_correct'] = 0
    if 'interests_total' not in request.session: request.session['interests_total'] = 0
    if request.method == 'POST':
        is_correct = str(request.POST.get('selected_id')) == str(request.session.get('interests_target_id'))
        request.session['interests_total'] += 1
        if is_correct: request.session['interests_correct'] += 1
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': return get_ajax_response(request, is_correct, "¡Correcto!" if is_correct else "Incorrecto", 'interests')
        return redirect('student_interests_game')
    target = random.choice(students)
    request.session['interests_target_id'] = target.id
    options = list(random.sample(list(students.exclude(id=target.id)), 3)) + [target]
    random.shuffle(options)
    return render(request, 'minigames/student_interests_game.html', {'target_student': target, 'options': options, 'correct': request.session['interests_correct'], 'total': request.session['interests_total']})

@login_required
def quiz_results_game(request):
    groups = ClassGroup.objects.filter(teacher=request.user)
    students = UserProfile.objects.filter(role='student', student_groups__in=groups).distinct()
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
    return render(request, 'minigames/quiz_results_game.html', {'target_student': target, 'options': options, 'correct': request.session['quiz_correct'], 'total': request.session['quiz_total']})

@login_required
def hangman_game(request):
    groups = ClassGroup.objects.filter(teacher=request.user)
    students = UserProfile.objects.filter(role='student', student_groups__in=groups, profile_picture__isnull=False).distinct()
    if not students.exists(): return render(request, 'minigames/no_students.html')
    if 'hangman_correct' not in request.session: request.session['hangman_correct'] = 0
    if 'hangman_total' not in request.session: request.session['hangman_total'] = 0
    if request.method == 'POST' and request.POST.get('action') == 'new_game' or 'hangman_target_id' not in request.session:
        student = random.choice(students)
        request.session['hangman_target_id'] = student.id
        request.session['hangman_target_name'] = normalize_text(student.full_name or student.username).upper()
        request.session['hangman_guessed_letters'] = []
        request.session['hangman_incorrect_count'] = 0
        request.session['hangman_game_over'] = False
        if request.POST.get('action') == 'new_game': return redirect('hangman_game')
    target_name = request.session['hangman_target_name']
    if request.method == 'POST' and request.POST.get('action') == 'guess_letter':
        letter = request.POST.get('letter', '').upper()
        if not request.session['hangman_game_over'] and letter not in request.session['hangman_guessed_letters']:
            request.session['hangman_guessed_letters'].append(letter)
            if letter not in target_name: request.session['hangman_incorrect_count'] += 1
            displayed = "".join([c if c in request.session['hangman_guessed_letters'] or not c.isalpha() else "_" for c in target_name])
            won, lost = "_" not in displayed, request.session['hangman_incorrect_count'] >= 6
            if won or lost:
                request.session['hangman_game_over'] = True
                request.session['hangman_total'] += 1
                if won: request.session['hangman_correct'] += 1
            request.session.modified = True
            return get_ajax_response(request, True, "", 'hangman', extra_data={'displayed_name': displayed, 'incorrect_count': request.session['hangman_incorrect_count'], 'game_over': request.session['hangman_game_over'], 'won': won, 'target_name': target_name})
    student = UserProfile.objects.get(id=request.session['hangman_target_id'])
    displayed_name = "".join([c if c in request.session['hangman_guessed_letters'] or not c.isalpha() else "_" for c in target_name])
    return render(request, 'minigames/hangman_game.html', {'current_student': student, 'displayed_name': displayed_name, 'incorrect_count': request.session['hangman_incorrect_count'], 'alphabet': "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ", 'used_letters': request.session['hangman_guessed_letters'], 'game_over': request.session['hangman_game_over'], 'correct': request.session['hangman_correct'], 'total': request.session['hangman_total']})

@login_required
def student_complete_profile_game(request):
    groups = ClassGroup.objects.filter(teacher=request.user)
    vark_q = Questionnaire.objects.filter(title="VARK").first()
    chapman_q = Questionnaire.objects.filter(title="Chapman").first()
    students = UserProfile.objects.filter(role='student', student_groups__in=groups, profile_picture__isnull=False).distinct()
    if students.count() < 4: return render(request, 'minigames/not_enough_students.html')
    if 'complete_profile_correct' not in request.session: request.session['complete_profile_correct'] = 0
    if 'complete_profile_total' not in request.session: request.session['complete_profile_total'] = 0
    if request.method == 'POST':
        is_correct = str(request.POST.get('selected_student_id')) == str(request.session.get('complete_profile_target_id'))
        request.session['complete_profile_total'] += 1
        if is_correct: request.session['complete_profile_correct'] += 1
        return get_ajax_response(request, is_correct, "¡Listo!", 'complete_profile')
    target = random.choice(students)
    request.session['complete_profile_target_id'] = target.id
    raw_options = list(students.exclude(id=target.id).order_by('?')[:3]) + [target]
    random.shuffle(raw_options)
    options_data = []
    for s in raw_options:
        vark = UserResult.objects.filter(user=s, questionnaire=vark_q).first()
        chapman = UserResult.objects.filter(user=s, questionnaire=chapman_q).first()
        options_data.append({
            'student_id': s.id, 'full_name': s.full_name or s.username, 'age': calculate_age(s.date_of_birth),
            'favorite_artist': s.favorite_artist or "N/A", 'vark_result': vark.dominant_category if vark else "Pte",
            'chapman_result': chapman.dominant_category if chapman else "Pte", 'motivation': s.motivation or "N/A"
        })
    return render(request, 'minigames/student_complete_profile_game.html', {'target_student': target, 'options': options_data, 'correct': request.session['complete_profile_correct'], 'total': request.session['complete_profile_total']})