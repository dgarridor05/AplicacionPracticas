🎮 Gamificación Escolar: Suite de Minijuegos con Django
Este módulo es una extensión interactiva para plataformas educativas basada en Django, diseñada para fomentar el reconocimiento y la cohesión entre alumnos y profesores mediante juegos dinámicos que utilizan los perfiles de los estudiantes.

🚀 Características Principales
Lógica basada en Sesiones: Seguimiento de puntuación y estado de juego (victoria/derrota) persistente por sesión de usuario.

Normalización de Texto: Algoritmos para ignorar tildes y mayúsculas, garantizando una experiencia de juego fluida.

Selección Dinámica de Grupos: Flujo de trabajo inteligente que redirige al usuario para seleccionar un grupo si no se especifica uno.

Protección contra Repeticiones: Sistema que evita mostrar el mismo perfil de alumno de forma consecutiva.

Interfaz AJAX: Respuestas rápidas en juegos de respuesta única sin necesidad de recargar la página completa.

🕹️ Juegos Incluidos
Ahorcado (Hangman): Adivina el nombre del compañero letra a letra.

Adivina Quién es: Identifica al alumno a partir de su foto de perfil.

Adivina la Imagen: Se da un nombre y hay que elegir la foto correcta.

Adivina Gustos: Basado en los intereses personales registrados en los perfiles.

Adivina Tests: Preguntas basadas en resultados de cuestionarios previos.

Spotify Mystery: El desafío musical para adivinar las canciones favoritas de los alumnos.

Perfil Completo: El desafío final que combina múltiples datos del estudiante.

🛠️ Tecnologías Utilizadas
Backend: Python 3.x, Django Framework.

Base de Datos: PostgreSQL / SQLite (compatible).

Frontend: JavaScript (AJAX/Fetch API), HTML5, CSS3 (Tailwind CSS recomendado).

Procesamiento de Datos: Unidecode para normalización de caracteres.

📂 Estructura de URLs
El sistema utiliza un enrutamiento dual para máxima flexibilidad:

Python
# Acceso directo (requiere selección de grupo)
path('ahorcado/', views.hangman_game, name='hangman_game'),

# Acceso directo a grupo específico
path('ahorcado/<int:group_id>/', views.hangman_game, name='hangman_game_with_group'),
⚙️ Instalación y Configuración
Clonar el repositorio:

Bash
git clone https://github.com/tu-usuario/nombre-del-repo.git
Instalar dependencias:

Bash
pip install -r requirements.txt
Migraciones de base de datos:

Bash
python manage.py migrate
Ejecutar el servidor:

Bash
python manage.py runserver
📋 Requisitos del Modelo de Datos
Para que los juegos funcionen correctamente, el modelo UserProfile debe contar con:

profile_picture: ImageField (obligatorio para la mayoría de juegos).

full_name o username: String.

interests / quiz_results: Campos de texto o relaciones ManyToMany.