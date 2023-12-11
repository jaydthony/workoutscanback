from django.core.management.base import BaseCommand
from api.models import Location, Program
from datetime import datetime, time
class Command(BaseCommand):
    help = 'Create default programs for locations'

    def handle(self, *args, **options):
        # Loop through all locations
        for location in Location.objects.all():
            # Check if a program with the same name as the location exists
            existing_program = Program.objects.filter(name=location.name).first()

            

            if not existing_program:
                # Create a new program if it doesn't exist
                new_program = Program(user=location.company, name=location.name, default=True)
                new_program.save()
                self.stdout.write(self.style.SUCCESS(f'Created a new program for {location.name}'))
            else:
                # Link the existing program to the location
                location.program = existing_program
                existing_program.default = True
                
                current_date = datetime.now().date()
                existing_program.started_at = datetime.combine(current_date, time(0, 0))

                existing_program.save()


                location.save()
                self.stdout.write(self.style.SUCCESS(f'Linked existing program to {location.name}'))
