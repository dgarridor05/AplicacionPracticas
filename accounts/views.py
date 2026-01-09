from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import StudentProfileForm
from django.db.models import Q
from .models import UserProfile
from django.shortcuts import get_object_or_404

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
            # Redirigir según el rol
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
    return render(request, 'accounts/student_home.html')

@login_required
def teacher_home(request):
    return render(request, 'accounts/teacher_home.html')

@login_required
def edit_student_profile(request):
    if request.user.role != 'student':
        return redirect('login')  # o mostrar error

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
    if request.user.role != 'student':
        return redirect('login')  # o redirigir a otro sitio si no es alumno, cambiar mas adelante

    return render(request, 'accounts/view_profile.html', {
        'user': request.user
    })

@login_required
def public_classmates_list(request):
    if request.user.role != 'student':
        return redirect('login')

    classmates = UserProfile.objects.filter(
        role='student',
        share_with_class=True
    ).exclude(id=request.user.id)

    return render(request, 'accounts/classmates_list.html', {
        'classmates': classmates
    })

@login_required
def public_student_profile(request, student_id):
    student = get_object_or_404(UserProfile, id=student_id, role='student', share_with_class=True)

    return render(request, 'accounts/public_student_profile.html', {
        'student': student
    })

@login_required
def view_profile(request):
    return render(request, 'accounts/view_profile.html')