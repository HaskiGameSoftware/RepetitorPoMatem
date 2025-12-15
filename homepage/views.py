from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
import os
import json
from .models import CourseOrder, UserProfile, UserCourse  # Добавить UserCourse
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Review, CourseOrder, UserCourse
from django.utils import timezone
from django.db import models
from .models import Course
from django.db import models
from django.utils import timezone
from .models import Course, CourseOrder, UserProfile, UserCourse, Review
from .models import Cart, CartItem


# Услуги для главной страницы
SERVICES = [
    {
        'title': 'Подготовка к ЕГЭ',
        'description': 'Полный курс подготовки к ЕГЭ по математике профильного и базового уровня с разбором всех заданий. Индивидуальный подход к каждому ученику, регулярные пробные тестирования, работа над сложными заданиями второй части.'
    },
    {
        'title': 'Подготовка к ОГЭ', 
        'description': 'Системная подготовка к ОГЭ для учеников 9 классов с проработкой всех типов задач. Ликвидация пробелов в знаниях, развитие вычислительных навыков, формирование уверенности на экзамене.'
    },
    {
        'title': 'Школьная программа',
        'description': 'Помощь в освоении школьной программы для учащихся 5-11 классов. Объяснение сложных тем, помощь с домашними заданиями, подготовка к контрольным работам и зачетам.'
    }
]

def index(request):
    # Получаем активные курсы для главной страницы
    courses_from_db = Course.objects.filter(is_active=True)[:3]  # Первые 3 активных курса
    
    # Преобразуем в нужный формат
    courses_list = []
    for course in courses_from_db:
        courses_list.append({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'price': course.price,
            'duration': course.duration,
            'max_students': course.max_students
        })
    # Получаем последние 3 одобренных отзыва из БД
    reviews_db = Review.objects.filter(is_approved=True).select_related('user', 'course').order_by('-timestamp')[:3]
    
    # Преобразуем в формат для шаблона
    reviews_list = []
    for review in reviews_db:
        reviews_list.append({
            'id': review.id,
            'student_name': review.student_name,
            'course_id': review.course.id if review.course else None,
            'text': review.text,
            'ratings': {
                'explanation': review.rating_explanation,
                'approach': review.rating_approach,
                'preparation': review.rating_preparation,
                'support': review.rating_support,
                'overall': review.rating_overall
            },
            'timestamp': review.timestamp.strftime('%Y-%m-%d')
        })
    
    # Вычисляем средние оценки
    all_reviews_db = Review.objects.filter(is_approved=True)
    avg_ratings = calculate_average_ratings_db(all_reviews_db)
    
    context = {
        'title': 'Репетитор по математике - Главная',
        'promo_text': 'Профессиональная подготовка к ЕГЭ и ОГЭ',
        'services': SERVICES,
        'reviews': reviews_list,
        'avg_ratings': avg_ratings,
        'total_reviews': all_reviews_db.count(),
        'courses': courses_list  # Передаем курсы из БД
    }
    
    return render(request, 'index.html', context)

def calculate_average_ratings_db(reviews_queryset):
    """Вычисляет средние оценки из QuerySet отзывов"""
    if not reviews_queryset.exists():
        return {
            'explanation': 0,
            'approach': 0,
            'preparation': 0,
            'support': 0,
            'overall': 0
        }
    
    from django.db.models import Avg
    aggregates = reviews_queryset.aggregate(
        avg_explanation=Avg('rating_explanation'),
        avg_approach=Avg('rating_approach'),
        avg_preparation=Avg('rating_preparation'),
        avg_support=Avg('rating_support'),
        avg_overall=Avg('rating_overall')
    )
    
    return {
        'explanation': round(aggregates['avg_explanation'] or 0, 1),
        'approach': round(aggregates['avg_approach'] or 0, 1),
        'preparation': round(aggregates['avg_preparation'] or 0, 1),
        'support': round(aggregates['avg_support'] or 0, 1),
        'overall': round(aggregates['avg_overall'] or 0, 1)
    }

def register(request):
    if request.method == 'POST':
        # Получаем данные из формы
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        # Проверяем, что все поля заполнены
        if not email or not password1 or not password2:
            messages.error(request, 'Пожалуйста, заполните все поля.')
            return redirect('homepage:register')
        
        # Проверяем, что пароли совпадают
        if password1 != password2:
            messages.error(request, 'Пароли не совпадают.')
            return redirect('homepage:register')
        
        # Проверяем, существует ли пользователь с таким email
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует.')
            return redirect('homepage:register')
        
        # Создаем имя пользователя из email (до символа @)
        username = email.split('@')[0]
        
        # Убедимся, что username уникален
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        try:
            # Создаем пользователя
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            # Автоматически логиним пользователя после регистрации
            login(request, user)
            
            # Создаем профиль
            UserProfile.objects.create(user=user)
            
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('homepage:personal_cabinet')
            
        except Exception as e:
            messages.error(request, f'Произошла ошибка при регистрации: {str(e)}')
            return redirect('homepage:register')
    
    return render(request, 'registration/register.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        # Находим пользователя по email
        try:
            user = User.objects.get(email=email)
            # Аутентифицируем с именем пользователя
            authenticated_user = authenticate(request, username=user.username, password=password)
            
            if authenticated_user is not None:
                login(request, authenticated_user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                return redirect('homepage:personal_cabinet')
            else:
                messages.error(request, 'Неверный пароль.')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден.')
    
    return render(request, 'registration/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('homepage:index')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Обновляем базовую информацию пользователя
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Обновляем профиль
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.phone = request.POST.get('phone', '')
        profile.birth_date = request.POST.get('birth_date', '')
        profile.save()
        
        messages.success(request, 'Профиль успешно обновлен!')
        return redirect('homepage:personal_cabinet')
    
    return render(request, 'registration/edit_profile.html')

@login_required
def personal_cabinet(request):
    # Получаем профиль пользователя
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    # Получаем курсы пользователя из UserCourse
    user_courses_objects = UserCourse.objects.filter(user=request.user).select_related('course_order')
    
    # Получаем все активные курсы из БД для контекста
    all_courses = Course.objects.filter(is_active=True)
    
    context = {
        'active_courses': user_courses_objects.filter(status='active'),
        'completed_courses': user_courses_objects.filter(status='completed'),
        'cancelled_courses': user_courses_objects.filter(status='cancelled'),
        'user_reviews': Review.objects.filter(user=request.user),
        'courses': all_courses,  # Передаем QuerySet курсов из БД
        'profile': profile,
        'total_courses_count': user_courses_objects.count()
    }
    
    return render(request, 'personal_cabinet.html', context)

def buy_course(request, course_id):
    print(f"=== DEBUG: buy_course called, course_id: {course_id} ===")
    print(f"=== DEBUG: Request method: {request.method} ===")
    
    if request.method == 'POST':
        print("=== DEBUG: This is a POST request ===")
        print(f"=== DEBUG: POST data: {dict(request.POST)} ===")
        
        try:
            # Получаем курс из БД
            try:
                course = Course.objects.get(id=course_id, is_active=True)
                print(f"=== DEBUG: Course found in DB: {course.title} ===")
            except Course.DoesNotExist:
                print("=== DEBUG: Course not found in DB or not active ===")
                messages.error(request, 'Курс не найден или временно недоступен.')
                return redirect('homepage:courses')
            
            # Получаем информацию о курсе
            course_info = {
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'price': course.price,
                'duration': course.duration,
                'max_students': course.max_students,
                'students_count': course.students_count,
                'available_slots': course.available_slots,
                'is_full': course.is_full
            }
            
            print(f"=== DEBUG: Course info: {course_info} ===")
            
            # Проверяем, есть ли свободные места
            if course_info['is_full']:
                print("=== DEBUG: Course is full ===")
                messages.error(request, f'Извините, на курс "{course_info["title"]}" все места заняты.')
                return redirect('homepage:courses')
            
            # Получаем данные из формы
            student_name = request.POST.get('student_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            
            print(f"=== DEBUG: Form data - name: '{student_name}', email: '{email}', phone: '{phone}' ===")
            
            # Валидация данных
            if not student_name or not email:
                print("=== DEBUG: Validation failed - missing required fields ===")
                messages.error(request, 'Пожалуйста, заполните все обязательные поля.')
                return redirect('homepage:courses')
            
            # Проверяем email
            if '@' not in email or '.' not in email:
                messages.error(request, 'Пожалуйста, введите корректный email адрес.')
                return redirect('homepage:courses')
            
            # Проверяем, не записан ли уже этот email на курс
            existing_order = CourseOrder.objects.filter(
                course_title=course.title,
                email=email
            ).first()
            
            if existing_order:
                print(f"=== DEBUG: Email {email} already registered for this course ===")
                messages.warning(request, 'Вы уже записаны на этот курс.')
                return redirect('homepage:personal_cabinet')
            
            print("=== DEBUG: Creating CourseOrder object ===")
            
            # Сохраняем заказ в БД
            order = CourseOrder(
                course=course,  # Связываем с объектом Course
                course_title=course.title,
                student_name=student_name,
                email=email,
                phone=phone,
                price=course.price
            )
            
            print(f"=== DEBUG: Before save - order: {order} ===")
            order.save()
            print(f"=== DEBUG: After save - order id: {order.id} ===")
            
            # Если пользователь авторизован, создаем запись в UserCourse
            if request.user.is_authenticated:
                user_course, created = UserCourse.objects.get_or_create(
                    user=request.user,
                    course_order=order,
                    defaults={
                        'course_id': course.id,
                        'course_title': course.title,
                        'status': 'active'
                    }
                )
                if created:
                    print(f"=== DEBUG: UserCourse created: {user_course} ===")
                else:
                    print(f"=== DEBUG: UserCourse already exists ===")
            
            # Выводим данные в консоль
            print("=" * 50)
            print("НОВЫЙ ЗАКАЗ КУРСА (из БД)")
            print(f"Курс ID: {course.id}")
            print(f"Курс: {course.title}")
            print(f"Цена: {course.price} руб.")
            print(f"Ученик: {student_name}")
            print(f"Email: {email}")
            print(f"Телефон: {phone}")
            print(f"Мест занято: {course.students_count + 1}/{course.max_students}")
            print(f"ID заказа в БД: {order.id}")
            print("=" * 50)
            
            # Обновляем сессию пользователя (если нужно)
            user_courses = request.session.get('user_courses', [])
            if course.id not in user_courses:
                user_courses.append(course.id)
                request.session['user_courses'] = user_courses
                print(f"=== DEBUG: Added course {course.id} to user_courses session ===")
            
            # Обновляем счетчик студентов
            updated_count = course.students_count + 1
            available = course.max_students - updated_count
            
            messages.success(request, 
                f'Вы успешно записались на курс "{course.title}"! '
                f'Осталось свободных мест: {available}'
            )
            
            return redirect('homepage:personal_cabinet')
            
        except Exception as e:
            print(f"=== DEBUG: EXCEPTION: {e} ===")
            import traceback
            traceback.print_exc()
            messages.error(request, 
                'Произошла ошибка при оформлении заказа. '
                'Пожалуйста, попробуйте еще раз или свяжитесь с нами.'
            )
            return redirect('homepage:courses')
    else:
        print("=== DEBUG: Not a POST request ===")
        messages.error(request, 'Некорректный запрос.')
    
    return redirect('homepage:courses')

@login_required
def leave_review(request):
    """Оставить отзыв (только для авторизованных пользователей)"""
    
    # Проверяем, авторизован ли пользователь
    if not request.user.is_authenticated:
        messages.error(request, 'Для оставления отзыва необходимо войти в систему.')
        return redirect('homepage:login')
    
    # Проверяем, есть ли у пользователя купленные курсы
    user_courses = UserCourse.objects.filter(user=request.user, status='active')
    
    if not user_courses.exists():
        messages.error(request, 'Для оставления отзыва необходимо приобрести хотя бы один курс.')
        return redirect('homepage:personal_cabinet')
    
    if request.method == 'POST':
        print(f"=== DEBUG: leave_review POST request ===")
        print(f"=== DEBUG: POST data: {dict(request.POST)} ===")
        
        try:
            # Получаем данные из формы
            student_name = request.POST.get('student_name', '').strip()
            course_id = request.POST.get('course_id', '').strip()
            text = request.POST.get('text', '').strip()
            
            print(f"=== DEBUG: Form data - student_name: '{student_name}', course_id: '{course_id}', text: '{text}' ===")
            
            # Проверяем обязательные поля
            if not student_name or not course_id or not text:
                print("=== DEBUG: Validation failed - missing required fields ===")
                messages.error(request, 'Пожалуйста, заполните все обязательные поля.')
                return redirect('homepage:leave_review')
            
            # Получаем курс из БД
            try:
                course = Course.objects.get(id=course_id, is_active=True)
                print(f"=== DEBUG: Course found: {course.title} ===")
            except Course.DoesNotExist:
                print("=== DEBUG: Course not found ===")
                messages.error(request, 'Выбранный курс не найден или неактивен.')
                return redirect('homepage:leave_review')
            
            # Проверяем, что имя содержит только буквы и пробелы
            if not all(c.isalpha() or c.isspace() for c in student_name):
                messages.error(request, 'Имя может содержать только буквы и пробелы.')
                return redirect('homepage:leave_review')
            
            # Проверяем длину текста отзыва
            if len(text) < 10:
                messages.error(request, 'Текст отзыва должен содержать не менее 10 символов.')
                return redirect('homepage:leave_review')
            
            # Проверяем, принадлежит ли курс пользователю
            # Ищем заказ курса для этого пользователя
            try:
                order = CourseOrder.objects.get(
                    course=course,
                    email=request.user.email
                )
                print(f"=== DEBUG: Course order found: {order.id} ===")
            except CourseOrder.DoesNotExist:
                # Проверяем через UserCourse
                user_course_exists = UserCourse.objects.filter(
                    user=request.user,
                    course_order__course_title=course.title
                ).exists()
                
                if not user_course_exists:
                    print("=== DEBUG: User doesn't own this course ===")
                    messages.error(request, 'Вы не приобретали этот курс.')
                    return redirect('homepage:leave_review')
                else:
                    # Находим любой заказ для этого курса пользователя
                    order = CourseOrder.objects.filter(
                        course_title=course.title,
                        email=request.user.email
                    ).first()
            
            # Проверяем, не оставлял ли пользователь уже отзыв на этот курс
            existing_review = Review.objects.filter(
                user=request.user,
                course=course
            ).first()
            
            if existing_review:
                print(f"=== DEBUG: User already left review for this course ===")
                messages.warning(request, 'Вы уже оставляли отзыв на этот курс.')
                return redirect('homepage:personal_cabinet')
            
            # Получаем оценки
            ratings = {
                'explanation': int(request.POST.get('rating_explanation', 0)),
                'approach': int(request.POST.get('rating_approach', 0)),
                'preparation': int(request.POST.get('rating_preparation', 0)),
                'support': int(request.POST.get('rating_support', 0)),
                'overall': int(request.POST.get('rating_overall', 0))
            }
            
            print(f"=== DEBUG: Ratings: {ratings} ===")
            
            # Проверяем, что все оценки проставлены (1-5)
            for key, value in ratings.items():
                if value < 1 or value > 5:
                    print(f"=== DEBUG: Invalid rating for {key}: {value} ===")
                    messages.error(request, 'Пожалуйста, оцените все характеристики от 1 до 5 звезд.')
                    return redirect('homepage:leave_review')
            
            # Создаем отзыв
            review = Review(
                user=request.user,
                course=course,  # Связываем с объектом Course
                student_name=student_name,
                text=text,
                rating_explanation=ratings['explanation'],
                rating_approach=ratings['approach'],
                rating_preparation=ratings['preparation'],
                rating_support=ratings['support'],
                rating_overall=ratings['overall']
            )
            
            # Автоматически одобряем отзывы для тестирования
            # В реальной системе здесь была бы модерация
            review.is_approved = True
            
            print(f"=== DEBUG: Before save - review: {review} ===")
            review.save()
            print(f"=== DEBUG: After save - review id: {review.id} ===")
            
            # Выводим данные в консоль
            print("=" * 50)
            print("НОВЫЙ ОТЗЫВ (из БД)")
            print(f"Пользователь: {request.user.username}")
            print(f"Курс: {course.title}")
            print(f"Имя ученика: {student_name}")
            print(f"Текст отзыва: {text[:100]}...")
            print(f"Оценки: {ratings}")
            print(f"ID отзыва: {review.id}")
            print("=" * 50)
            
            # Обновляем средние оценки курса
            course_reviews = Review.objects.filter(course=course, is_approved=True)
            if course_reviews.exists():
                from django.db.models import Avg
                avg_ratings = course_reviews.aggregate(
                    avg_explanation=Avg('rating_explanation'),
                    avg_approach=Avg('rating_approach'),
                    avg_preparation=Avg('rating_preparation'),
                    avg_support=Avg('rating_support'),
                    avg_overall=Avg('rating_overall')
                )
                
                print(f"=== DEBUG: Updated average ratings for course {course.id}: {avg_ratings} ===")
            
            messages.success(request, 
                'Спасибо за ваш отзыв! '
                'Он будет опубликован после модерации.'
            )
            
            # Перенаправляем на страницу всех отзывов или на главную
            return redirect('homepage:all_reviews')
            
        except ValueError as e:
            print(f"=== DEBUG: ValueError: {e} ===")
            messages.error(request, 'Ошибка в данных оценок. Пожалуйста, оцените все характеристики.')
            return redirect('homepage:leave_review')
        except Exception as e:
            print(f"=== DEBUG: EXCEPTION: {e} ===")
            import traceback
            traceback.print_exc()
            messages.error(request, 
                f'Произошла ошибка при сохранении отзыва: {str(e)}. '
                'Пожалуйста, попробуйте еще раз.'
            )
            return redirect('homepage:leave_review')
    
    # GET запрос - показываем форму
    
    # Получаем активные курсы пользователя
    # GET запрос - показываем форму
    # Получаем активные курсы пользователя
    user_courses_objects = UserCourse.objects.filter(
        user=request.user, 
        status='active'
    ).select_related('course_order')

    purchased_courses = []
    for user_course in user_courses_objects:
        # Ищем курс в БД по названию
        try:
            course = Course.objects.get(title=user_course.course_title, is_active=True)

            # Проверяем, не оставлял ли пользователь уже отзыв на этот курс
            has_review = Review.objects.filter(
                user=request.user,
                course=course
            ).exists()

            if not has_review:
                purchased_courses.append({
                    'id': course.id,
                    'title': course.title,
                    'description': course.description,
                    'course_order': user_course.course_order
                })
        except Course.DoesNotExist:
            print(f"=== DEBUG: Course '{user_course.course_title}' not found in DB ===")
            continue

    # Если у пользователя нет курсов без отзывов
    if not purchased_courses:
        messages.info(request, 
            'Вы уже оставили отзывы на все ваши курсы или у вас нет активных курсов.'
        )
        return redirect('homepage:personal_cabinet')

    # Получаем все активные курсы для контекста
    all_active_courses = Course.objects.filter(is_active=True)

    context = {
        'purchased_courses': purchased_courses,
        'courses': all_active_courses,  # QuerySet курсов
        'user': request.user
    }
    
    print(f"=== DEBUG: Context - purchased_courses: {len(purchased_courses)} ===")
    
    return render(request, 'leave_review.html', context)

def courses(request):
    """Показать все активные курсы"""
    # Получаем все активные курсы из БД
    courses_from_db = Course.objects.filter(is_active=True)
    
    # Преобразуем в нужный формат для шаблона
    courses_with_info = []
    for course in courses_from_db:
        courses_with_info.append({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'price': course.price,
            'duration': course.duration,
            'max_students': course.max_students,
            'students_count': course.students_count,
            'available_slots': course.available_slots,
            'is_full': course.is_full
        })
    
    context = {
        'courses': courses_with_info
    }
    return render(request, 'courses.html', context)

def all_reviews(request):
    """Показать все одобренные отзывы"""
    
    # Получаем одобренные отзывы из БД
    reviews_db = Review.objects.filter(is_approved=True).select_related('course', 'user').order_by('-timestamp')
    
    # Получаем активные курсы из БД
    courses_from_db = Course.objects.filter(is_active=True)
    
    # Преобразуем отзывы в формат для шаблона
    reviews_list = []
    for review in reviews_db:
        reviews_list.append({
            'id': review.id,
            'student_name': review.student_name,
            'course': review.course,  # Объект Course из БД
            'text': review.text,
            'ratings': {
                'explanation': review.rating_explanation,
                'approach': review.rating_approach,
                'preparation': review.rating_preparation,
                'support': review.rating_support,
                'overall': review.rating_overall
            },
            'timestamp': review.timestamp.strftime('%Y-%m-%d'),
            'username': review.user.username
        })
    
    # Вычисляем средние оценки
    if reviews_db.exists():
        from django.db.models import Avg
        aggregates = reviews_db.aggregate(
            avg_explanation=Avg('rating_explanation'),
            avg_approach=Avg('rating_approach'),
            avg_preparation=Avg('rating_preparation'),
            avg_support=Avg('rating_support'),
            avg_overall=Avg('rating_overall')
        )
        
        avg_ratings = {
            'explanation': round(aggregates['avg_explanation'] or 0, 1),
            'approach': round(aggregates['avg_approach'] or 0, 1),
            'preparation': round(aggregates['avg_preparation'] or 0, 1),
            'support': round(aggregates['avg_support'] or 0, 1),
            'overall': round(aggregates['avg_overall'] or 0, 1)
        }
    else:
        avg_ratings = {
            'explanation': 0,
            'approach': 0,
            'preparation': 0,
            'support': 0,
            'overall': 0
        }
    
    context = {
        'reviews': reviews_list,
        'avg_ratings': avg_ratings,
        'total_reviews': reviews_db.count(),
        'courses': courses_from_db,  # QuerySet курсов из БД
        'reviews_from_db': reviews_db  # Для совместимости
    }
    
    return render(request, 'all_reviews.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Обновляем сессию, чтобы пользователь не вышел
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('homepage:personal_cabinet')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'registration/change_password.html', {'form': form})

def get_course_info(course_id):
    """Получить информацию о курсе и количестве записавшихся"""
    try:
        course = Course.objects.get(id=course_id, is_active=True)
        return {
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'price': course.price,
            'duration': course.duration,
            'max_students': course.max_students,
            'students_count': course.students_count,
            'available_slots': course.available_slots,
            'is_full': course.is_full
        }
    except Course.DoesNotExist:
        return None


def password_reset(request):
    """Восстановление пароля с записью в текстовый файл"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Пожалуйста, введите email.')
            return render(request, 'registration/password_reset.html')
        
        try:
            # Ищем пользователя по email
            user = User.objects.get(email=email)
            
            # Генерируем новый случайный пароль
            new_password = get_random_string(12)
            
            # Устанавливаем новый пароль пользователю
            user.set_password(new_password)
            user.save()
            
            # Путь к файлу для записи паролей
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'password_resets.txt')
            
            # Записываем информацию в файл
            with open(file_path, 'a', encoding='utf-8') as f:
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"Время: {timestamp}\n")
                f.write(f"Email: {email}\n")
                f.write(f"Новый пароль: {new_password}\n")
                f.write(f"Имя пользователя: {user.username}\n")
                f.write("-" * 50 + "\n\n")
            
            # Сообщаем пользователю
            messages.success(request, f'Новый пароль был сгенерирован и записан в файл. Проверьте файл password_resets.txt в корне проекта.')
            messages.info(request, f'Ваш новый пароль для входа: {new_password}')
            
            # Логируем в консоль для отладки
            print("\n" + "="*60)
            print("ВОССТАНОВЛЕНИЕ ПАРОЛЯ")
            print(f"Email: {email}")
            print(f"Новый пароль: {new_password}")
            print(f"Пароль записан в файл: {file_path}")
            print("="*60 + "\n")
            
        except User.DoesNotExist:
            # Если пользователь не найден, все равно записываем попытку
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'password_resets.txt')
            
            with open(file_path, 'a', encoding='utf-8') as f:
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"Время: {timestamp}\n")
                f.write(f"Email: {email} - пользователь не найден\n")
                f.write("-" * 50 + "\n\n")
            
            # Для безопасности показываем то же сообщение
            messages.success(request, 'Если указанный email зарегистрирован в системе, новый пароль был сгенерирован и записан в файл.')
            
            print("\n" + "="*60)
            print("ПОПЫТКА ВОССТАНОВЛЕНИЯ ПАРОЛЯ - ПОЛЬЗОВАТЕЛЬ НЕ НАЙДЕН")
            print(f"Email: {email}")
            print(f"Записано в файл: {file_path}")
            print("="*60 + "\n")
        
        # Перенаправляем на страницу входа
        return redirect('homepage:login')
    
    return render(request, 'registration/password_reset.html')


def get_or_create_cart(request):
    """Получить или создать корзину для пользователя"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            is_active=True
        )
    else:
        # Для анонимных пользователей используем сессию
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, is_active=True)
            except Cart.DoesNotExist:
                cart = None
        else:
            cart = None
        
        if not cart:
            # Создаем временного пользователя для анонимной корзины
            temp_user, created = User.objects.get_or_create(
                username=f'anonymous_{request.session.session_key}',
                defaults={'email': '', 'password': 'anonymous'}
            )
            cart = Cart.objects.create(user=temp_user, is_active=True)
            request.session['cart_id'] = cart.id
            request.session['anonymous_cart'] = True
    
    return cart

def add_to_cart(request, course_id):
    """Добавить курс в корзину"""
    try:
        course = Course.objects.get(id=course_id, is_active=True)
    except Course.DoesNotExist:
        messages.error(request, 'Курс не найден.')
        return redirect('homepage:courses')
    
    cart = get_or_create_cart(request)
    
    # Проверяем, не добавлен ли уже курс в корзину
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        course=course,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'Курс "{course.title}" добавлен в корзину.')
    
    # Возвращаемся на предыдущую страницу или на страницу курсов
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('homepage:courses')

def remove_from_cart(request, item_id):
    """Удалить товар из корзины"""
    try:
        cart_item = CartItem.objects.get(id=item_id)
        
        # Проверяем, что товар принадлежит корзине пользователя
        if request.user.is_authenticated:
            if cart_item.cart.user != request.user:
                messages.error(request, 'У вас нет прав на удаление этого товара.')
                return redirect('homepage:cart')
        else:
            cart_id = request.session.get('cart_id')
            if not cart_id or cart_item.cart.id != cart_id:
                messages.error(request, 'У вас нет прав на удаление этого товара.')
                return redirect('homepage:cart')
        
        course_title = cart_item.course.title
        cart_item.delete()
        
        # Если корзина пуста, удаляем ее
        if cart_item.cart.items.count() == 0:
            cart_item.cart.delete()
            if not request.user.is_authenticated:
                del request.session['cart_id']
        
        messages.success(request, f'Курс "{course_title}" удален из корзины.')
        
    except CartItem.DoesNotExist:
        messages.error(request, 'Товар не найден в корзине.')
    
    return redirect('homepage:cart')

def clear_cart(request):
    """Очистить корзину"""
    cart = get_or_create_cart(request)
    
    if cart:
        items_count = cart.items.count()
        cart.items.all().delete()
        cart.delete()
        
        if not request.user.is_authenticated:
            if 'cart_id' in request.session:
                del request.session['cart_id']
            if 'anonymous_cart' in request.session:
                del request.session['anonymous_cart']
        
        messages.success(request, f'Корзина очищена. Удалено {items_count} товаров.')
    
    return redirect('homepage:cart')

def cart_view(request):
    """Просмотр корзины"""
    cart = get_or_create_cart(request)
    
    context = {
        'cart': cart,
        'cart_items': cart.items.all() if cart else [],
        'total_price': cart.total_price if cart else 0,
        'items_count': cart.items_count if cart else 0
    }
    
    return render(request, 'cart.html', context)

def checkout(request):
    """Оформление заказа из корзины"""
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        
        if not cart or cart.items.count() == 0:
            messages.error(request, 'Ваша корзина пуста.')
            return redirect('homepage:cart')
        
        try:
            # Получаем данные из формы
            student_name = request.POST.get('student_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            
            # Валидация данных
            if not student_name or not email:
                messages.error(request, 'Пожалуйста, заполните все обязательные поля.')
                return redirect('homepage:cart')
            
            # Для каждого курса в корзине создаем заказ
            for cart_item in cart.items.all():
                course = cart_item.course
                
                # Проверяем, есть ли свободные места
                if course.is_full:
                    messages.warning(request, 
                        f'Курс "{course.title}" заполнен. Он был удален из корзины.'
                    )
                    cart_item.delete()
                    continue
                
                # Создаем заказ
                order = CourseOrder(
                    course=course,
                    course_title=course.title,
                    student_name=student_name,
                    email=email,
                    phone=phone,
                    price=course.price
                )
                order.save()
                
                # Связываем с пользователем, если он авторизован
                if request.user.is_authenticated:
                    UserCourse.objects.get_or_create(
                        user=request.user,
                        course_order=order,
                        defaults={
                            'course_id': course.id,
                            'course_title': course.title,
                            'status': 'active'
                        }
                    )
                
                print("=" * 50)
                print("ЗАКАЗ ИЗ КОРЗИНЫ")
                print(f"Курс: {course.title}")
                print(f"Цена: {course.price} руб.")
                print(f"Ученик: {student_name}")
                print(f"Email: {email}")
                print(f"Телефон: {phone}")
                print("=" * 50)
            
            # Очищаем корзину после оформления заказа
            cart_items_count = cart.items.count()
            cart.items.all().delete()
            cart.delete()
            
            if not request.user.is_authenticated:
                if 'cart_id' in request.session:
                    del request.session['cart_id']
                if 'anonymous_cart' in request.session:
                    del request.session['anonymous_cart']
            
            messages.success(request, 
                f'Заказ успешно оформлен! Вы приобрели {cart_items_count} курсов. '
                f'Детали заказа отправлены на email {email}.'
            )
            
            return redirect('homepage:personal_cabinet' if request.user.is_authenticated else 'homepage:courses')
            
        except Exception as e:
            print(f"Ошибка при оформлении заказа: {e}")
            messages.error(request, 
                'Произошла ошибка при оформлении заказа. '
                'Пожалуйста, попробуйте еще раз или свяжитесь с нами.'
            )
            return redirect('homepage:cart')
    
    # GET запрос - показываем форму оформления заказа
    cart = get_or_create_cart(request)
    
    if not cart or cart.items.count() == 0:
        messages.error(request, 'Ваша корзина пуста.')
        return redirect('homepage:courses')
    
    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'total_price': cart.total_price,
        'items_count': cart.items_count
    }
    
    return render(request, 'checkout.html', context)