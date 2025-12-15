# create_initial_courses.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RepetitorPoMatem.settings')
django.setup()

from homepage.models import Course

def create_initial_courses():
    courses_data = [
        {
            'title': 'Подготовка к ЕГЭ',
            'description': 'Полный курс подготовки к ЕГЭ по математике профильного уровня',
            'price': 15000,
            'duration': '8 месяцев',
            'max_students': 15,
            'is_active': True
        },
        {
            'title': 'Подготовка к ОГЭ', 
            'description': 'Комплексная подготовка к ОГЭ для учеников 9 классов',
            'price': 12000,
            'duration': '6 месяцев',
            'max_students': 15,
            'is_active': True
        },
        {
            'title': 'Школьная программа',
            'description': 'Помощь в освоении школьной программы 5-11 классы',
            'price': 8000,
            'duration': '3 месяцев',
            'max_students': 15,
            'is_active': True
        }
    ]
    
    created_count = 0
    for course_data in courses_data:
        course, created = Course.objects.get_or_create(
            title=course_data['title'],
            defaults=course_data
        )
        if created:
            created_count += 1
            print(f'Создан курс: {course.title}')
    
    print(f'Всего создано курсов: {created_count}')

if __name__ == '__main__':
    create_initial_courses()