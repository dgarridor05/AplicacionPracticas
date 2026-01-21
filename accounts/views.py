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
    return render(request, 'accounts/student_home.html')

@login_required
def teacher_home(request):
    return render(request, 'accounts/teacher_home.html')

@login_required
def edit_student_profile(request):
    if request.user.role != 'student':
        return redirect('login')

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
        return redirect('login')

    # Enviamos 'student' para que la plantilla sea compatible con la del profesor
    return render(request, 'accounts/view_profile.html', {
        'user': request.user,
        'student': request.user
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
    # Lógica mejorada: Si es profesor, ve el perfil aunque share_with_class sea False
    if request.user.role == 'teacher':
        student = get_object_or_404(UserProfile, id=student_id, role='student')
    else:
        student = get_object_or_404(UserProfile, id=student_id, role='student', share_with_class=True)

    return render(request, 'accounts/public_student_profile.html', {
        'student': student
    })

@login_required
def view_profile(request):
    # Redirigimos a la vista detallada que ya tiene la lógica
    return redirect('view_student_profile')