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
    if request.user.role != 'student':
        return redirect('teacher_home')

    from teachers.models import ClassGroup
    from django.db.models import Q

    # 1. Buscamos los grupos donde está metido el alumno actual
    mis_grupos = ClassGroup.objects.filter(students=request.user)

    if not mis_grupos.exists():
        return render(request, 'accounts/classmates_list.html', {'classmates': [], 'no_group': True})

    # 2. Obtenemos los perfiles que pertenecen a esos grupos directamente
    # Filtramos UserProfile que estén en la relación 'students' de mis_grupos
    classmates = UserProfile.objects.filter(
        student_groups__in=mis_grupos,
        share_with_class=True
    ).exclude(id=request.user.id).distinct()

    # 3. Lógica de buscador
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
    from teachers.models import ClassGroup
    
    # 1. Obtenemos al estudiante (si existe y quiere compartir)
    student = get_object_or_404(UserProfile, id=student_id, role='student', share_with_class=True)
    
    # 2. Verificación de seguridad
    if request.user.role == 'teacher':
        # El profesor puede verlo si es su alumno
        pass 
    else:
        # Si es alumno, verificamos que compartan al menos un grupo
        comparten_grupo = ClassGroup.objects.filter(
            students=request.user
        ).filter(
            students=student
        ).exists()
        
        if not comparten_grupo:
            messages.error(request, "No tienes permiso para ver este perfil.")
            return redirect('classmates_list')

    return render(request, 'accounts/public_student_profile.html', {
        'student': student
    })

@login_required
def view_profile(request):
    if request.user.role == 'teacher':
        return redirect('teacher_home')
    return redirect('view_student_profile')

# --- NUEVA VISTA PARA UNIRSE POR CÓDIGO ---
@login_required
def join_group_by_code(request):
    if request.user.role != 'student':
        return redirect('teacher_home')

    if request.method == 'POST':
        code = request.POST.get('invite_code', '').strip().upper()
        from teachers.models import ClassGroup
        
        try:
            # Buscamos el grupo que tenga ese código único
            group = ClassGroup.objects.get(invite_code=code)
            
            # Si el alumno ya está en el grupo, avisamos
            if group.students.filter(id=request.user.id).exists():
                messages.info(request, f"Ya eres miembro del grupo: {group.name}")
            else:
                group.students.add(request.user)
                messages.success(request, f"Te has unido con éxito al grupo: {group.name}")
            
            return redirect('classmates_list')
            
        except ClassGroup.DoesNotExist:
            messages.error(request, "El código introducido no es válido.")
            
    return render(request, 'accounts/join_group.html')