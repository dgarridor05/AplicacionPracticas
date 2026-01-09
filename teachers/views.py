from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ClassGroupForm
from .models import ClassGroup
from django.shortcuts import get_object_or_404
from accounts.models import UserProfile
from quizzes.models import UserResult
from django.contrib import messages
import json

@login_required
def create_group(request):
    if request.user.role != 'teacher':
        return redirect('login')

    if request.method == 'POST':
        form = ClassGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.teacher = request.user
            group.save()
            form.save_m2m()  # guardar estudiantes
            return redirect('view_groups')
    else:
        form = ClassGroupForm()

    return render(request, 'teachers/create_group.html', {'form': form})


@login_required
def view_groups(request):
    if request.user.role != 'teacher':
        return redirect('login')

    groups = ClassGroup.objects.filter(teacher=request.user)
    return render(request, 'teachers/view_groups.html', {'groups': groups})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(ClassGroup, id=group_id, teacher=request.user)
    students = group.students.all()

    style_labels = {
        'V': 'Visual',
        'A': 'Auditivo',
        'R': 'Lectura/Escritura',
        'K': 'Kinestésico',
    }

    student_styles = {}
    for student in students:
        result = UserResult.objects.filter(user=student, questionnaire__title="VARK").first()
        style_code = result.dominant_category if result else None
        student_styles[student.id] = style_labels.get(style_code) if style_code else None

    return render(request, 'teachers/group_detail.html', {
        'group': group,
        'students': students,
        'student_styles': student_styles,
    })

@login_required
def group_statistics(request, group_id):
    group = get_object_or_404(ClassGroup, id=group_id, teacher=request.user)

    students = group.students.all()
    results = UserResult.objects.filter(user__in=students, questionnaire__title="VARK")

    counts = {'V': 0, 'A': 0, 'R': 0, 'K': 0}
    for r in results:
        counts[r.dominant_category] += 1

    labels = ['Visual', 'Auditivo', 'Lectura/Escritura', 'Kinestésico']
    data = [counts['V'], counts['A'], counts['R'], counts['K']]
    has_data = any(data)

    return render(request, 'teachers/group_statistics.html', {
    'group': group,
    'labels': json.dumps(labels),
    'data': json.dumps(data),
    'vark_data': has_data,
})

@login_required
def edit_group(request, group_id):
    group = get_object_or_404(ClassGroup, id=group_id, teacher=request.user)

    if request.method == 'POST':
        form = ClassGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grupo actualizado correctamente.')
            return redirect('group_detail', group_id=group.id)
    else:
        form = ClassGroupForm(instance=group)

    return render(request, 'teachers/edit_group.html', {
        'form': form,
        'group': group
    })

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(ClassGroup, id=group_id, teacher=request.user)

    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Grupo eliminado correctamente.')
        return redirect('view_groups')  

    return render(request, 'teachers/delete_group.html', {'group': group})

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(UserProfile, id=student_id, role='student')

    vark_result = UserResult.objects.filter(
        user=student,
        questionnaire__title="VARK"
    ).first()

    group = ClassGroup.objects.filter(students=student, teacher=request.user).first()

    return render(request, 'teachers/student_detail.html', {
        'student': student,
        'vark_result': vark_result,
        'group': group,
    })