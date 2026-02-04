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
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'teacher':
                return redirect('teacher_home')
            return redirect('student_home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def student_home(request):
    if request.user.role != 'student':
        return redirect('teacher_home')
    return render(request, 'accounts/student_home.html')

@login_required
def teacher_home(request):
    if request.user.role != 'teacher':
        return redirect('student_home')
    return render(request, 'accounts/teacher_home.html')

@login_required
def edit_student_profile(request):
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
    if request.user.role != 'student':
        return redirect('teacher_home')
    return render(request, 'accounts/view_profile.html', {
        'user': request.user,
        'student': request.user
    })

@login_required
def public_classmates_list(request):
    """
    Lista solo a los alumnos que comparten grupo con el usuario.
    Incluye buscador por nickname o nombre.
    """
    if request.user.role != 'student':
        return redirect('teacher_home')

    # Obtenemos grupos del usuario actual
    mis_grupos_ids = request.user.student_groups.values_list('id', flat=True)

    # Si el usuario no tiene grupo, no mostramos a nadie para evitar fugas de datos
    if not mis_grupos_ids:
        return render(request, 'accounts/classmates_list.html', {'classmates': []})

    # Filtro base: mismo grupo, rol estudiante y que quieran compartir
    classmates = UserProfile.objects.filter(
        role='student',
        share_with_class=True,
        student_groups__id__in=mis_grupos_ids
    ).exclude(id=request.user.id).distinct()

    # --- Lógica de Búsqueda Avanzada ---
    query = request.GET.get('q')
    if query:
        classmates = classmates.filter(
            Q(nickname__icontains=query) | 
            Q(full_name__icontains=query) |
            Q(residence_area__icontains=query)
        )

    return render(request, 'accounts/classmates_list.html', {
        'classmates': classmates,
        'query': query
    })

@login_required
def public_student_profile(request, student_id):
    """
    Muestra el perfil. Si es alumno, verifica que compartan grupo.
    Usa get_object_or_404 para evitar Error 500 si el ID no existe.
    """
    if request.user.role == 'teacher':
        student = get_object_or_404(UserProfile, id=student_id, role='student')
    else:
        mis_grupos_ids = request.user.student_groups.values_list('id', flat=True)
        
        # Filtro de seguridad: debe compartir grupo
        student = get_object_or_404(
            UserProfile, 
            id=student_id, 
            role='student', 
            share_with_class=True,
            student_groups__id__in=mis_grupos_ids
        )

    return render(request, 'accounts/public_student_profile.html', {
        'student': student
    })

@login_required
def view_profile(request):
    if request.user.role == 'teacher':
        return redirect('teacher_home')
    return redirect('view_student_profile')