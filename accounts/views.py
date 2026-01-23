from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, StudentProfileForm
from .models import UserProfile
from django.db.models import Q

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario registrado correctamente. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'student':
                return redirect('student_home')
            elif user.role == 'teacher':
                return redirect('teacher_home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def student_home(request):
    # SEGURIDAD: Si un profesor intenta entrar aquí, lo mandamos a su panel
    if request.user.role != 'student':
        return redirect('teacher_home')
    return render(request, 'accounts/student_home.html')

@login_required
def teacher_home(request):
    # SEGURIDAD: Si un alumno intenta entrar aquí, lo mandamos a su panel
    if request.user.role != 'teacher':
        return redirect('student_home')
    return render(request, 'accounts/teacher_home.html')

@login_required
def edit_student_profile(request):
    # SEGURIDAD: Solo alumnos pueden editar su perfil de alumno
    if request.user.role != 'student':
        return redirect('teacher_home')

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('student_home')
    else:
        form = StudentProfileForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def view_student_profile(request):
    # SEGURIDAD: Si es profesor, lo redirigimos a su inicio (o puedes dejar que lo vea si quieres)
    if request.user.role != 'student':
        return redirect('teacher_home')

    return render(request, 'accounts/view_profile.html', {
        'user': request.user,
        'student': request.user
    })

@login_required
def public_classmates_list(request):
    if request.user.role != 'student':
        return redirect('teacher_home')

    classmates = UserProfile.objects.filter(
        role='student',
        share_with_class=True
    ).exclude(id=request.user.id)

    return render(request, 'accounts/classmates_list.html', {
        'classmates': classmates
    })

@login_required
def public_student_profile(request, student_id):
    # Los profesores pueden ver cualquier perfil de alumno. 
    # Los alumnos solo los que tengan share_with_class=True.
    if request.user.role == 'teacher':
        student = get_object_or_404(UserProfile, id=student_id, role='student')
    else:
        student = get_object_or_404(UserProfile, id=student_id, role='student', share_with_class=True)

    return render(request, 'accounts/public_student_profile.html', {
        'student': student
    })

@login_required
def view_profile(request):
    # Si es profesor, al pinchar en "Ver perfil" lo mandamos a su home
    if request.user.role == 'teacher':
        return redirect('teacher_home')
    return redirect('view_student_profile')