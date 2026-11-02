from django.core.management.base import BaseCommand

from fitness.models import Muscle


MUSCLES = {
    'chest': 'chest',
    'front_delt': 'shoulders',
    'lateral_delt': 'shoulders',
    'rear_delt': 'shoulders',
    'triceps': 'arms',
    'biceps': 'arms',
    'lats': 'back',
    'upper_back': 'back',
    'traps': 'back',
    'quads': 'legs',
    'hamstrings': 'legs',
    'glutes': 'legs',
    'calves': 'legs',
    'abs': 'core',
    'lower_back': 'back',
}


class Command(BaseCommand):
    help = 'Seed the basic muscle list.'

    def handle(self, *args, **options):
        created_count = 0
        for name, muscle_group in MUSCLES.items():
            _, created = Muscle.objects.get_or_create(
                name=name,
                defaults={'muscle_group': muscle_group},
            )
            created_count += int(created)

        self.stdout.write(self.style.SUCCESS(f'Created {created_count} muscles.'))