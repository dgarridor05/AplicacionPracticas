from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Carga ambos tests: Chapman y VARK para producción'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando carga de tests para producción...'))
        
        try:
            # Cargar Chapman desde JSON
            self.stdout.write(self.style.WARNING('Cargando test de Chapman...'))
            call_command('load_chapman_from_json')
            
            # Cargar VARK
            self.stdout.write(self.style.WARNING('Cargando test de VARK...'))
            call_command('load_vark')
            
            self.stdout.write(
                self.style.SUCCESS('✅ Ambos tests cargados exitosamente para producción.')
            )
            self.stdout.write(
                self.style.SUCCESS('Los estudiantes ya pueden realizar los tests de Chapman y VARK.')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al cargar tests: {str(e)}')
            )
