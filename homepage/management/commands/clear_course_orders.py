from django.core.management.base import BaseCommand
from homepage.models import CourseOrder

class Command(BaseCommand):
    help = 'Удалить все записи на курсы для тестирования'
    
    def handle(self, *args, **kwargs):
        count = CourseOrder.objects.count()
        CourseOrder.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Удалено {count} записей на курсы'))