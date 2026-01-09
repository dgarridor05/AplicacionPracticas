from django.core.management.base import BaseCommand
from quizzes.models import Questionnaire, Question, Option

class Command(BaseCommand):
    help = 'Carga el cuestionario VARK con sus preguntas y opciones'

    def handle(self, *args, **kwargs):
        questionnaire, created = Questionnaire.objects.get_or_create(
            title='VARK',
            defaults={'description': 'Cuestionario sobre estilos de aprendizaje'}
        )

        if not created:
            questionnaire.question_set.all().delete()

        preguntas = [
            {
                "texto": "Prefiero aprender de un nuevo juego viendo una demostración.",
                "opciones": [
                    ("V", "Ver a alguien jugar el juego."),
                    ("A", "Escuchar las reglas."),
                    ("R", "Leer las instrucciones."),
                    ("K", "Jugarlo yo mismo.")
                ]
            },
            {
                "texto": "Cuando recibo instrucciones nuevas de un aparato técnico, prefiero:",
                "opciones": [
                    ("V", "Diagramas, esquemas, gráficos o cuadros."),
                    ("A", "Alguien que me explique."),
                    ("R", "Leer las instrucciones."),
                    ("K", "Probarlo y trabajar con los controles.")
                ]
            },
            {
                "texto": "Elijo vacaciones basándome en:",
                "opciones": [
                    ("V", "Lo que he visto en folletos y fotos."),
                    ("A", "Lo que me han dicho."),
                    ("R", "La información escrita."),
                    ("K", "Lo que he experimentado allí antes.")
                ]
            },
            {
                "texto": "En una clase me resulta más fácil aprender de:",
                "opciones": [
                    ("V", "Gráficos, esquemas, diagramas."),
                    ("A", "Explicaciones orales."),
                    ("R", "Lectura de apuntes."),
                    ("K", "Actividades prácticas.")
                ]
            },
            {
                "texto": "Cuando cocino algo nuevo:",
                "opciones": [
                    ("V", "Sigo las imágenes o videos."),
                    ("A", "Escucho instrucciones."),
                    ("R", "Leo la receta."),
                    ("K", "Lo hago experimentando.")
                ]
            },
            {
                "texto": "Cuando estudio, prefiero:",
                "opciones": [
                    ("V", "Usar colores y diagramas."),
                    ("A", "Leer en voz alta."),
                    ("R", "Tomar apuntes y leerlos."),
                    ("K", "Construir modelos o hacer actividades.")
                ]
            },
            {
                "texto": "Si tuviera que armar un mueble:",
                "opciones": [
                    ("V", "Seguiría ilustraciones."),
                    ("A", "Llamaría a alguien para que me explique."),
                    ("R", "Leería las instrucciones paso a paso."),
                    ("K", "Lo armaría y vería cómo encaja.")
                ]
            },
            {
                "texto": "Cuando intento recordar algo:",
                "opciones": [
                    ("V", "Visualizo cómo se veía."),
                    ("A", "Recuerdo lo que se dijo."),
                    ("R", "Me repito notas mentales."),
                    ("K", "Recuerdo cómo me sentí o qué hice.")
                ]
            },
            {
                "texto": "Me ayudan más las personas que:",
                "opciones": [
                    ("V", "Muestran cómo hacerlo."),
                    ("A", "Lo explican claramente."),
                    ("R", "Me dan información escrita."),
                    ("K", "Me permiten intentarlo por mí mismo.")
                ]
            },
            {
                "texto": "Me resulta más fácil aprender cuando:",
                "opciones": [
                    ("V", "Veo una película o un gráfico."),
                    ("A", "Alguien me habla al respecto."),
                    ("R", "Leo al respecto."),
                    ("K", "Lo experimento directamente.")
                ]
            },
            {
                "texto": "En un examen, prefiero preguntas:",
                "opciones": [
                    ("V", "Con imágenes o diagramas."),
                    ("A", "Que pueda responder en voz alta."),
                    ("R", "De desarrollo o escritura."),
                    ("K", "De opción múltiple con ejemplos.")
                ]
            },
            {
                "texto": "Cuando leo una historia, prefiero:",
                "opciones": [
                    ("V", "Imaginar las escenas."),
                    ("A", "Escuchar la narración."),
                    ("R", "Leerla cuidadosamente."),
                    ("K", "Relacionarla con experiencias propias.")
                ]
            },
            {
                "texto": "Me acuerdo mejor de las personas por:",
                "opciones": [
                    ("V", "Su apariencia."),
                    ("A", "Su voz."),
                    ("R", "Su nombre escrito."),
                    ("K", "Cómo me saludaron o interactuaron.")
                ]
            },
            {
                "texto": "Si tengo que aprender a usar un programa nuevo:",
                "opciones": [
                    ("V", "Vería un tutorial."),
                    ("A", "Escucharía una explicación."),
                    ("R", "Leería la guía de usuario."),
                    ("K", "Lo exploraría directamente.")
                ]
            },
            {
                "texto": "Para relajarme, prefiero:",
                "opciones": [
                    ("V", "Ver paisajes o arte."),
                    ("A", "Escuchar música."),
                    ("R", "Leer."),
                    ("K", "Moverme, bailar o hacer ejercicio.")
                ]
            },
            {
                "texto": "Cuando trabajo en grupo, me gusta:",
                "opciones": [
                    ("V", "Usar pizarras, dibujos o esquemas."),
                    ("A", "Hablar y discutir ideas."),
                    ("R", "Tomar notas y leerlas juntos."),
                    ("K", "Hacer actividades o simulaciones.")
                ]
            },
        ]

        for pregunta in preguntas:
            question = Question.objects.create(
                questionnaire=questionnaire,
                text=pregunta["texto"]
            )
            for category, texto_opcion in pregunta["opciones"]:
                Option.objects.create(
                    question=question,
                    text=texto_opcion,
                    category=category,
                    value=1
                )

        self.stdout.write(self.style.SUCCESS('Cuestionario VARK cargado con éxito.'))