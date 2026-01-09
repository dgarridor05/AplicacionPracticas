import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "relaciona.settings")
django.setup()

from quizzes.models import Questionnaire, Question, Option

Questionnaire.objects.filter(title="VARK").delete()

vark = Questionnaire.objects.create(title="VARK", description="Test de estilos de aprendizaje VARK")

q = Question.objects.create(questionnaire=vark, text="Me gustaría que el profesor usara:")
Option.objects.create(question=q, text="diagramas y gráficos", category="V")
Option.objects.create(question=q, text="discusiones, charlas", category="A")
Option.objects.create(question=q, text="libros y apuntes", category="R")
Option.objects.create(question=q, text="actividades prácticas", category="K")

q = Question.objects.create(questionnaire=vark, text="Cuando trabajo en equipo, me gusta:")
Option.objects.create(question=q, text="hacer un esquema", category="V")
Option.objects.create(question=q, text="hablar con todos", category="A")
Option.objects.create(question=q, text="escribir todo en un documento", category="R")
Option.objects.create(question=q, text="realizar algo juntos", category="K")

q = Question.objects.create(questionnaire=vark, text="Cuando aprendo algo nuevo, prefiero:")
Option.objects.create(question=q, text="ver imágenes o mapas", category="V")
Option.objects.create(question=q, text="escuchar a alguien explicarlo", category="A")
Option.objects.create(question=q, text="leer sobre ello", category="R")
Option.objects.create(question=q, text="probarlo yo mismo", category="K")

q = Question.objects.create(questionnaire=vark, text="En una presentación me ayudan más:")
Option.objects.create(question=q, text="diagramas y fotos", category="V")
Option.objects.create(question=q, text="la explicación oral", category="A")
Option.objects.create(question=q, text="el folleto con texto", category="R")
Option.objects.create(question=q, text="los ejemplos prácticos", category="K")

q = Question.objects.create(questionnaire=vark, text="Me gusta que los profesores:")
Option.objects.create(question=q, text="usen dibujos", category="V")
Option.objects.create(question=q, text="expliquen en voz alta", category="A")
Option.objects.create(question=q, text="den apuntes", category="R")
Option.objects.create(question=q, text="hagan actividades", category="K")

q = Question.objects.create(questionnaire=vark, text="Si tengo que recordar algo, prefiero:")
Option.objects.create(question=q, text="visualizarlo", category="V")
Option.objects.create(question=q, text="repetírmelo en voz alta", category="A")
Option.objects.create(question=q, text="escribirlo muchas veces", category="R")
Option.objects.create(question=q, text="hacer algo relacionado", category="K")

q = Question.objects.create(questionnaire=vark, text="Cuando me dan instrucciones nuevas:")
Option.objects.create(question=q, text="me ayudan los esquemas", category="V")
Option.objects.create(question=q, text="prefiero que me lo digan", category="A")
Option.objects.create(question=q, text="quiero las instrucciones escritas", category="R")
Option.objects.create(question=q, text="pruebo a hacerlo directamente", category="K")

q = Question.objects.create(questionnaire=vark, text="Para tomar apuntes, prefiero:")
Option.objects.create(question=q, text="dibujar símbolos y flechas", category="V")
Option.objects.create(question=q, text="escuchar y anotar palabras clave", category="A")
Option.objects.create(question=q, text="copiar exactamente lo que dicen", category="R")
Option.objects.create(question=q, text="anotar solo lo que entiendo haciendo", category="K")

q = Question.objects.create(questionnaire=vark, text="Para revisar antes de un examen:")
Option.objects.create(question=q, text="uso mapas mentales", category="V")
Option.objects.create(question=q, text="explico el tema a alguien", category="A")
Option.objects.create(question=q, text="releo mis apuntes", category="R")
Option.objects.create(question=q, text="repaso con ejercicios", category="K")

q = Question.objects.create(questionnaire=vark, text="Si tengo que armar un mueble:")
Option.objects.create(question=q, text="me fijo en los diagramas", category="V")
Option.objects.create(question=q, text="escucho instrucciones", category="A")
Option.objects.create(question=q, text="leo el manual", category="R")
Option.objects.create(question=q, text="me pongo manos a la obra", category="K")

q = Question.objects.create(questionnaire=vark, text="Para entender una película o historia:")
Option.objects.create(question=q, text="presto atención a las imágenes", category="V")
Option.objects.create(question=q, text="escucho los diálogos", category="A")
Option.objects.create(question=q, text="leo los subtítulos", category="R")
Option.objects.create(question=q, text="me concentro en lo que hacen", category="K")

q = Question.objects.create(questionnaire=vark, text="Prefiero aprender con:")
Option.objects.create(question=q, text="esquemas y gráficos", category="V")
Option.objects.create(question=q, text="debates y conversaciones", category="A")
Option.objects.create(question=q, text="lectura y escritura", category="R")
Option.objects.create(question=q, text="proyectos y práctica", category="K")

q = Question.objects.create(questionnaire=vark, text="En el aula me ayuda más:")
Option.objects.create(question=q, text="dibujos y colores", category="V")
Option.objects.create(question=q, text="la voz del profesor", category="A")
Option.objects.create(question=q, text="los textos escritos", category="R")
Option.objects.create(question=q, text="las actividades", category="K")

q = Question.objects.create(questionnaire=vark, text="Cuando elijo ropa:")
Option.objects.create(question=q, text="me guío por el color y estilo", category="V")
Option.objects.create(question=q, text="pido opiniones", category="A")
Option.objects.create(question=q, text="leo las etiquetas", category="R")
Option.objects.create(question=q, text="me la pruebo", category="K")

q = Question.objects.create(questionnaire=vark, text="Si necesito aprender a usar una app nueva:")
Option.objects.create(question=q, text="veo un tutorial en video", category="V")
Option.objects.create(question=q, text="le pido a alguien que me lo explique", category="A")
Option.objects.create(question=q, text="leo las instrucciones", category="R")
Option.objects.create(question=q, text="exploro la app por mí mismo", category="K")

q = Question.objects.create(questionnaire=vark, text="Cuando explico algo a alguien:")
Option.objects.create(question=q, text="uso dibujos o ejemplos visuales", category="V")
Option.objects.create(question=q, text="lo digo en voz alta", category="A")
Option.objects.create(question=q, text="escribo los pasos", category="R")
Option.objects.create(question=q, text="le muestro cómo se hace", category="K")

print("Cuestionario VARK cargado correctamente.")
